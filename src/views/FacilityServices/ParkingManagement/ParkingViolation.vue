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
          <span class="loading-title">Parking Violation</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Parking Violation Detection & Enforcement</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="parking-violation-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Warning /></el-icon>
          Parking Violation
        </h1>
        <div class="page-subtitle">Monitor, track and manage parking violations across all zones</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openReportDialog">
          <el-icon><Document /></el-icon> Generate Report
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalViolations }}</div>
          <div class="stat-label">Total Violations</div>
          <div class="stat-trend up">↑ {{ stats.violationGrowth }}% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pendingViolations }}</div>
          <div class="stat-label">Pending</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.resolvedViolations }}</div>
          <div class="stat-label">Resolved</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.totalFines }}k</div>
          <div class="stat-label">Total Fines</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Most Common Violation</div>
        <div class="metric-value">{{ metrics.topViolation }}</div>
        <div class="metric-sub">{{ metrics.topViolationCount }} incidents</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Repeat Offenders</div>
        <div class="metric-value">{{ metrics.repeatOffenders }}</div>
        <div class="metric-trend negative">↑ {{ metrics.repeatGrowth }}% vs last month</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Most Affected Zone</div>
        <div class="metric-value">{{ metrics.topZone }}</div>
        <div class="metric-sub">{{ metrics.topZoneCount }} violations</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Peak Violation Time</div>
        <div class="metric-value">{{ metrics.peakTime }}</div>
        <div class="metric-sub">{{ metrics.peakHourCount }} violations</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Violations by Type</span>
          <span class="chart-subtitle">Distribution of violation types</span>
        </div>
        <div class="chart-container" ref="violationTypeChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Violations by Zone</span>
          <span class="chart-subtitle">Hotspot analysis</span>
        </div>
        <div class="chart-container" ref="zoneChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Violation Trend</span>
          <span class="chart-subtitle">Last 30 days</span>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Hourly Violation Pattern</span>
          <span class="chart-subtitle">Time distribution</span>
        </div>
        <div class="chart-container" ref="hourlyChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by plate or vehicle..."
            style="width: 200px"
            clearable
            :prefix-icon="Search"
        />
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
        <el-select v-model="violationTypeFilter" placeholder="Violation Type" clearable style="width: 150px">
          <el-option v-for="t in violationTypes" :key="t" :label="t" :value="t" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="Pending" value="pending" />
          <el-option label="Resolved" value="resolved" />
          <el-option label="Disputed" value="disputed" />
        </el-select>
        <el-select v-model="zoneFilter" placeholder="Zone" clearable style="width: 120px">
          <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Violations Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Violation Records</span>
        <el-button size="small" @click="viewAllViolations">View All →</el-button>
      </div>
      <el-table :data="paginatedViolations" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="vehicleNumber" label="Vehicle Number" min-width="140">
          <template #default="{ row }">
            <span class="vehicle-number">{{ row.vehicleNumber }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="violationType" label="Violation Type" width="150">
          <template #default="{ row }">
            <el-tag :type="getViolationTagType(row.violationType)" size="small">{{ row.violationType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="zone" label="Zone" width="100" />
        <el-table-column prop="spotNumber" label="Spot" width="80" />
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="fine" label="Fine ($)" width="100">
          <template #default="{ row }">
            ${{ row.fine }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="imageUrl" label="Evidence" width="80">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewEvidence(row)">View</el-button>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewViolationDetail(row)">Details</el-button>
            <el-button v-if="row.status === 'pending'" link type="success" size="small" @click="resolveViolation(row)">Resolve</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Violation Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Violation ${selectedViolation?.id}`" width="750px">
      <div v-if="selectedViolation" class="violation-detail">
        <div class="detail-image" v-if="selectedViolation.imageUrl">
          <div class="evidence-placeholder">
            <el-icon><Camera /></el-icon>
            <span>Evidence Image</span>
            <div class="evidence-info">
              <p>Captured at: {{ selectedViolation.time }}</p>
              <p>Camera: {{ selectedViolation.cameraId }}</p>
            </div>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Violation ID">{{ selectedViolation.id }}</el-descriptions-item>
          <el-descriptions-item label="Vehicle Number">
            <span class="vehicle-number large">{{ selectedViolation.vehicleNumber }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Violation Type">
            <el-tag :type="getViolationTagType(selectedViolation.violationType)" size="small">{{ selectedViolation.violationType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Zone">{{ selectedViolation.zone }}</el-descriptions-item>
          <el-descriptions-item label="Spot Number">{{ selectedViolation.spotNumber }}</el-descriptions-item>
          <el-descriptions-item label="Time">{{ selectedViolation.time }}</el-descriptions-item>
          <el-descriptions-item label="Fine Amount">${{ selectedViolation.fine }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedViolation.status)" size="small">{{ getStatusText(selectedViolation.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Officer">{{ selectedViolation.officer }}</el-descriptions-item>
          <el-descriptions-item label="Camera ID">{{ selectedViolation.cameraId }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedViolation.description }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section" v-if="selectedViolation.status !== 'resolved'">
          <div class="section-title">Actions</div>
          <div class="action-buttons">
            <el-button type="success" @click="resolveViolation(selectedViolation)">Issue Fine & Resolve</el-button>
            <el-button type="warning" @click="sendReminder(selectedViolation)">Send Reminder</el-button>
            <el-button type="danger" @click="escalateViolation(selectedViolation)">Escalate</el-button>
          </div>
        </div>

        <div class="detail-section" v-if="selectedViolation.remarks">
          <div class="section-title">Remarks</div>
          <el-input type="textarea" :rows="2" v-model="remarksText" placeholder="Add remarks..." />
          <el-button size="small" style="margin-top: 8px" @click="addRemark">Add Remark</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button v-if="selectedViolation?.status === 'pending'" type="primary" @click="resolveViolation(selectedViolation)">Resolve</el-button>
        <el-button type="warning" @click="printViolation(selectedViolation)">Print Notice</el-button>
      </template>
    </el-dialog>

    <!-- Evidence Dialog -->
    <el-dialog v-model="evidenceDialogVisible" title="Violation Evidence" width="600px">
      <div class="evidence-container">
        <div class="evidence-image">
          <el-icon><Camera /></el-icon>
          <span>Violation Evidence</span>
        </div>
        <div class="evidence-details">
          <p><strong>Vehicle:</strong> {{ evidenceVehicle }}</p>
          <p><strong>Violation:</strong> {{ evidenceViolation }}</p>
          <p><strong>Time:</strong> {{ evidenceTime }}</p>
          <p><strong>Location:</strong> {{ evidenceLocation }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="evidenceDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadEvidence">Download</el-button>
      </template>
    </el-dialog>

    <!-- Generate Report Dialog -->
    <el-dialog v-model="reportDialogVisible" title="Generate Violation Report" width="500px">
      <el-form :model="reportForm" label-width="120px">
        <el-form-item label="Report Period">
          <el-date-picker
              v-model="reportForm.period"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Include Zones">
          <el-select v-model="reportForm.zones" multiple placeholder="All zones" style="width: 100%">
            <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
          </el-select>
        </el-form-item>
        <el-form-item label="Include Statistics">
          <el-checkbox-group v-model="reportForm.statistics">
            <el-checkbox label="summary">Summary Statistics</el-checkbox>
            <el-checkbox label="trend">Trend Analysis</el-checkbox>
            <el-checkbox label="top">Top Violations</el-checkbox>
            <el-checkbox label="repeat">Repeat Offenders</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Format">
          <el-radio-group v-model="reportForm.format">
            <el-radio label="pdf">PDF Report</el-radio>
            <el-radio label="excel">Excel Export</el-radio>
            <el-radio label="csv">CSV Data</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="generateReport">Generate</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Warning, Clock, CircleCheck, Money, Document, Download, Refresh,
  Search, RefreshLeft, Camera
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading violation data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading violation data...',
  'Analyzing violation patterns...',
  'Loading camera evidence...',
  'Processing fines data...',
  'Almost ready...'
]

// ==================== Types ====================
interface ParkingViolation {
  id: string
  vehicleNumber: string
  violationType: string
  zone: string
  spotNumber: string
  time: string
  fine: number
  status: string
  imageUrl: string
  cameraId: string
  officer: string
  description: string
  remarks?: string[]
}

// ==================== Mock Data ====================
const violationTypes = [
  'No Parking Zone',
  'Expired Meter',
  'Blocking Driveway',
  'Double Parking',
  'EV Spot Violation',
  'Disabled Spot Violation',
  'Overtime Parking',
  'Wrong Way Parking'
]
const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']

const generateViolations = (): ParkingViolation[] => {
  const violations: ParkingViolation[] = []
  const vehicles = ['SGD1234A', 'SGA5678B', 'SGB9012C', 'SGC3456D', 'SGD7890E', 'SGE2345F', 'SGF6789G', 'SGG0123H']
  const officers = ['John Tan', 'Mike Chen', 'Ahmad Ibrahim', 'Lim Wei Ming', 'Sarah Koh']

  for (let i = 0; i < 85; i++) {
    const date = new Date()
    date.setDate(date.getDate() - Math.floor(Math.random() * 30))
    date.setHours(Math.floor(Math.random() * 24), Math.floor(Math.random() * 60))
    const timeStr = date.toISOString().replace('T', ' ').slice(0, 19)

    const violationType = violationTypes[Math.floor(Math.random() * violationTypes.length)]
    const fine = violationType === 'No Parking Zone' ? 80 :
        violationType === 'Blocking Driveway' ? 100 :
            violationType === 'EV Spot Violation' ? 150 :
                violationType === 'Disabled Spot Violation' ? 200 : 50

    const status = Math.random() < 0.4 ? 'pending' : (Math.random() < 0.6 ? 'resolved' : 'disputed')

    violations.push({
      id: `VIO-${String(i + 1).padStart(6, '0')}`,
      vehicleNumber: vehicles[Math.floor(Math.random() * vehicles.length)],
      violationType: violationType,
      zone: zones[Math.floor(Math.random() * zones.length)],
      spotNumber: `${String.fromCharCode(65 + Math.floor(Math.random() * 5))}${Math.floor(Math.random() * 20) + 1}`,
      time: timeStr,
      fine: fine,
      status: status,
      imageUrl: `evidence_${i + 1}.jpg`,
      cameraId: `CAM-${Math.floor(Math.random() * 8) + 1}`,
      officer: officers[Math.floor(Math.random() * officers.length)],
      description: `${violationType} violation detected at ${timeStr}`,
      remarks: status === 'disputed' ? ['Driver disputes violation'] : []
    })
  }

  return violations.sort((a, b) => b.time.localeCompare(a.time))
}

const violations = ref<ParkingViolation[]>(generateViolations())

// ==================== State ====================
const searchText = ref('')
const dateRange = ref<Date[] | null>(null)
const violationTypeFilter = ref('')
const statusFilter = ref('')
const zoneFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const evidenceDialogVisible = ref(false)
const reportDialogVisible = ref(false)
const selectedViolation = ref<ParkingViolation | null>(null)
const remarksText = ref('')
const evidenceVehicle = ref('')
const evidenceViolation = ref('')
const evidenceTime = ref('')
const evidenceLocation = ref('')

const reportForm = ref({
  period: null as string[] | null,
  zones: [] as string[],
  statistics: ['summary', 'trend', 'top'],
  format: 'pdf'
})

// Chart refs
let violationTypeChart: echarts.ECharts | null = null
let zoneChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let hourlyChart: echarts.ECharts | null = null

const violationTypeChartEl = ref<HTMLElement | null>(null)
const zoneChartEl = ref<HTMLElement | null>(null)
const trendChartEl = ref<HTMLElement | null>(null)
const hourlyChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalViolations = violations.value.length
  const pendingViolations = violations.value.filter(v => v.status === 'pending').length
  const resolvedViolations = violations.value.filter(v => v.status === 'resolved').length
  const totalFines = violations.value.reduce((sum, v) => sum + v.fine, 0) / 1000

  return {
    totalViolations,
    violationGrowth: 12.5,
    pendingViolations,
    resolvedViolations,
    totalFines: totalFines.toFixed(1)
  }
})

const metrics = computed(() => {
  // Count violation types
  const typeCount = new Map<string, number>()
  violations.value.forEach(v => {
    typeCount.set(v.violationType, (typeCount.get(v.violationType) || 0) + 1)
  })
  let topViolation = ''
  let topViolationCount = 0
  for (const [type, count] of typeCount) {
    if (count > topViolationCount) {
      topViolationCount = count
      topViolation = type
    }
  }

  // Count repeat offenders
  const vehicleCount = new Map<string, number>()
  violations.value.forEach(v => {
    vehicleCount.set(v.vehicleNumber, (vehicleCount.get(v.vehicleNumber) || 0) + 1)
  })
  const repeatOffenders = Array.from(vehicleCount.values()).filter(c => c > 1).length

  // Count by zone
  const zoneCount = new Map<string, number>()
  violations.value.forEach(v => {
    zoneCount.set(v.zone, (zoneCount.get(v.zone) || 0) + 1)
  })
  let topZone = ''
  let topZoneCount = 0
  for (const [zone, count] of zoneCount) {
    if (count > topZoneCount) {
      topZoneCount = count
      topZone = zone
    }
  }

  // Peak hour
  const hourCount = new Array(24).fill(0)
  violations.value.forEach(v => {
    const hour = parseInt(v.time.split(' ')[1]?.split(':')[0] || '0')
    if (!isNaN(hour)) hourCount[hour]++
  })
  let peakHour = 0
  let peakHourCount = 0
  for (let i = 0; i < 24; i++) {
    if (hourCount[i] > peakHourCount) {
      peakHourCount = hourCount[i]
      peakHour = i
    }
  }

  return {
    topViolation,
    topViolationCount,
    repeatOffenders,
    repeatGrowth: 15,
    topZone,
    topZoneCount,
    peakTime: `${peakHour}:00 - ${peakHour + 1}:00`,
    peakHourCount
  }
})

const filteredViolations = computed(() => {
  let filtered = [...violations.value]

  if (searchText.value) {
    const search = searchText.value.toUpperCase()
    filtered = filtered.filter(v =>
        v.vehicleNumber.toUpperCase().includes(search)
    )
  }

  if (violationTypeFilter.value) {
    filtered = filtered.filter(v => v.violationType === violationTypeFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(v => v.status === statusFilter.value)
  }

  if (zoneFilter.value) {
    filtered = filtered.filter(v => v.zone === zoneFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(v => {
      const violationDate = new Date(v.time)
      return violationDate >= start && violationDate <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredViolations.value.length)

const paginatedViolations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredViolations.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getViolationTagType = (type: string): string => {
  const map: Record<string, string> = {
    'No Parking Zone': 'danger',
    'Expired Meter': 'warning',
    'Blocking Driveway': 'danger',
    'Double Parking': 'warning',
    'EV Spot Violation': 'primary',
    'Disabled Spot Violation': 'primary',
    'Overtime Parking': 'info',
    'Wrong Way Parking': 'danger'
  }
  return map[type] || 'info'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { pending: 'Pending', resolved: 'Resolved', disputed: 'Disputed' }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { pending: 'warning', resolved: 'success', disputed: 'danger' }
  return map[status] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  dateRange.value = null
  violationTypeFilter.value = ''
  statusFilter.value = ''
  zoneFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const viewViolationDetail = (violation: ParkingViolation) => {
  selectedViolation.value = violation
  detailDialogVisible.value = true
}

const viewEvidence = (violation: ParkingViolation) => {
  evidenceVehicle.value = violation.vehicleNumber
  evidenceViolation.value = violation.violationType
  evidenceTime.value = violation.time
  evidenceLocation.value = `${violation.zone} - Spot ${violation.spotNumber}`
  evidenceDialogVisible.value = true
}

const resolveViolation = (violation: ParkingViolation | null) => {
  if (violation) {
    const index = violations.value.findIndex(v => v.id === violation.id)
    if (index !== -1) {
      violations.value[index].status = 'resolved'
      ElMessage.success(`Violation ${violation.id} resolved. Fine amount: $${violation.fine}`)
    }
  }
  detailDialogVisible.value = false
}

const sendReminder = (violation: ParkingViolation | null) => {
  if (violation) {
    ElMessage.success(`Reminder sent to vehicle ${violation.vehicleNumber}`)
  }
}

const escalateViolation = (violation: ParkingViolation | null) => {
  if (violation) {
    ElMessage.warning(`Violation ${violation.id} escalated to enforcement team`)
  }
}

const addRemark = () => {
  if (remarksText.value && selectedViolation.value) {
    ElMessage.success('Remark added')
    remarksText.value = ''
  }
}

const printViolation = (violation: ParkingViolation | null) => {
  if (violation) {
    ElMessage.success(`Printing violation notice for ${violation.vehicleNumber}`)
  }
}

const downloadEvidence = () => {
  ElMessage.success('Downloading evidence...')
  setTimeout(() => {
    ElMessage.success('Evidence downloaded')
  }, 1000)
}

const viewAllViolations = () => {
  ElMessage.info('Viewing all violations')
}

const openReportDialog = () => {
  reportDialogVisible.value = true
}

const generateReport = () => {
  ElMessage.success('Report generation started. You will be notified when ready.')
  reportDialogVisible.value = false
}

const exportData = () => {
  ElMessage.success('Exporting violation data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  violations.value = generateViolations()
  refreshCharts()
  ElMessage.success('Data refreshed')
}

// ==================== Chart Functions ====================
const initViolationTypeChart = () => {
  if (!violationTypeChartEl.value) return
  if (violationTypeChart) {
    violationTypeChart.dispose()
    violationTypeChart = null
  }

  const typeCount = new Map<string, number>()
  violations.value.forEach(v => {
    typeCount.set(v.violationType, (typeCount.get(v.violationType) || 0) + 1)
  })

  const data = Array.from(typeCount.entries()).map(([name, value]) => ({ name, value }))

  violationTypeChart = echarts.init(violationTypeChartEl.value)
  violationTypeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} violations ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name), type: 'scroll' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {d}%', fontSize: 11 },
      emphasis: { scale: true }
    }]
  })
}

const initZoneChart = () => {
  if (!zoneChartEl.value) return
  if (zoneChart) {
    zoneChart.dispose()
    zoneChart = null
  }

  const zoneCount = new Map<string, number>()
  violations.value.forEach(v => {
    zoneCount.set(v.zone, (zoneCount.get(v.zone) || 0) + 1)
  })

  const data = Array.from(zoneCount.entries()).map(([name, value]) => ({ name, value }))

  zoneChart = echarts.init(zoneChartEl.value)
  zoneChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: data.map(d => d.name) },
    yAxis: { type: 'value', name: 'Number of Violations' },
    series: [{
      type: 'bar',
      data: data.map(d => d.value),
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 15) return '#ef4444'
          if (value > 10) return '#f59e0b'
          return '#22c55e'
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }

  const days = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
  const trendData = days.map(() => Math.floor(2 + Math.random() * 8))

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: days, axisLabel: { rotate: 45, interval: 5 } },
    yAxis: { type: 'value', name: 'Violations per Day' },
    series: [{
      type: 'line',
      data: trendData,
      smooth: true,
      lineStyle: { color: '#ef4444', width: 3 },
      symbol: 'circle',
      symbolSize: 6,
      areaStyle: { opacity: 0.1, color: '#ef4444' },
      label: { show: true, position: 'top', interval: 5 }
    }]
  })
}

const initHourlyChart = () => {
  if (!hourlyChartEl.value) return
  if (hourlyChart) {
    hourlyChart.dispose()
    hourlyChart = null
  }

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const hourlyData = [2, 1, 0, 0, 1, 2, 5, 12, 18, 22, 25, 20, 15, 12, 10, 15, 20, 25, 22, 18, 12, 8, 5, 3]

  hourlyChart = echarts.init(hourlyChartEl.value)
  hourlyChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Violations' },
    series: [{
      type: 'bar',
      data: hourlyData,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 20) return '#ef4444'
          if (value > 12) return '#f59e0b'
          return '#22c55e'
        }
      },
      label: { show: true, position: 'top', interval: 3 }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initViolationTypeChart()
    initZoneChart()
    initTrendChart()
    initHourlyChart()
  })
}

// ==================== Watch ====================
watch([searchText, violationTypeFilter, statusFilter, zoneFilter, dateRange], () => {
  currentPage.value = 1
})

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
      nextTick(() => refreshCharts())
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', () => {
    const charts = [violationTypeChart, zoneChart, trendChart, hourlyChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  })
})

onUnmounted(() => {
  const charts = [violationTypeChart, zoneChart, trendChart, hourlyChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.parking-violation-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.up { color: #ef4444; }

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-title {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.metric-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
}

.metric-trend {
  font-size: 12px;
  margin: 8px 0 4px;
}

.metric-trend.positive { color: #22c55e; }
.metric-trend.negative { color: #ef4444; }

.metric-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* Charts Row */
.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 280px;
  width: 100%;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.vehicle-number {
  font-family: monospace;
  font-weight: 600;
  letter-spacing: 1px;
}

.vehicle-number.large {
  font-size: 18px;
}

/* Violation Detail */
.violation-detail {
  padding: 8px;
}

.detail-image {
  margin-bottom: 20px;
}

.evidence-placeholder {
  background: #1e293b;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  color: #64748b;
}

.evidence-placeholder .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.evidence-info {
  margin-top: 16px;
  text-align: left;
  color: #94a3b8;
}

.evidence-info p {
  margin: 4px 0;
}

.detail-section {
  margin-top: 20px;
}

.section-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Evidence Dialog */
.evidence-container {
  text-align: center;
}

.evidence-image {
  background: #1e293b;
  border-radius: 12px;
  padding: 40px;
  margin-bottom: 20px;
  color: #64748b;
}

.evidence-image .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.evidence-details {
  text-align: left;
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
}

.evidence-details p {
  margin: 8px 0;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .action-buttons {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .stats-grid, .metrics-row {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select,
  .filter-left .el-date-editor {
    width: 100% !important;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-dialog__body) {
  padding: 20px;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>