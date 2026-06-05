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
          <span class="loading-title">Visitor Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Smart Visitor Registration & Access Control</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="visitor-management-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <div class="title-icon">
            <el-icon><User /></el-icon>
          </div>
          Visitor Management
        </h1>
        <div class="page-subtitle">Manage visitor registrations, check-ins, and access control</div>
      </div>
      <div class="header-actions">
        <el-button class="primary-btn" @click="openRegisterDialog">
          <el-icon><Plus /></el-icon>
          <span>Register Visitor</span>
        </el-button>
        <el-button class="secondary-btn" @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.todayVisitors }}</div>
          <div class="stat-label">Today's Visitors</div>
          <div class="stat-trend up">↑ {{ stats.todayGrowth }}% vs yesterday</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.checkedIn }}</div>
          <div class="stat-label">Checked In</div>
          <div class="stat-trend">{{ stats.checkInRate }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.expectedVisitors }}</div>
          <div class="stat-label">Expected</div>
          <div class="stat-trend">Next 24 hours</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgStayDuration }}<span class="stat-unit">min</span></div>
          <div class="stat-label">Avg Stay Duration</div>
          <div class="stat-trend down">↓ 8% vs last month</div>
        </div>
      </div>
    </div>

    <!-- Today's Visitors Overview -->
    <div class="today-visitors">
      <div class="section-header">
        <div class="section-title-wrapper">
          <span class="section-icon">📅</span>
          <h2 class="section-title">Today's Visitor Overview</h2>
        </div>
        <div class="section-actions">
          <el-button class="outline-btn" @click="exportTodayData">
            <el-icon><Download /></el-icon> Export
          </el-button>
        </div>
      </div>
      <div class="visitors-stats-row">
        <div class="visitor-stat-item">
          <div class="visitor-stat-value">{{ stats.checkedIn }}</div>
          <div class="visitor-stat-label">Checked In</div>
          <div class="visitor-stat-progress">
            <div class="progress-fill" :style="{ width: (stats.checkedIn / stats.todayVisitors * 100) + '%' }"></div>
          </div>
        </div>
        <div class="visitor-stat-item">
          <div class="visitor-stat-value">{{ stats.pendingCheckIn }}</div>
          <div class="visitor-stat-label">Pending Check-in</div>
        </div>
        <div class="visitor-stat-item">
          <div class="visitor-stat-value">{{ stats.completedVisits }}</div>
          <div class="visitor-stat-label">Completed</div>
        </div>
        <div class="visitor-stat-item">
          <div class="visitor-stat-value">{{ stats.noShow }}</div>
          <div class="visitor-stat-label">No-Show</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <div class="quick-action-card" @click="quickCheckIn">
        <div class="action-icon">📱</div>
        <div class="action-text">Quick Check-in</div>
        <div class="action-sub">Scan QR code</div>
      </div>
      <div class="quick-action-card" @click="openPreRegister">
        <div class="action-icon">📝</div>
        <div class="action-text">Pre-register</div>
        <div class="action-sub">For VIP guests</div>
      </div>
      <div class="quick-action-card" @click="openBulkRegister">
        <div class="action-icon">👥</div>
        <div class="action-text">Bulk Register</div>
        <div class="action-sub">Import CSV file</div>
      </div>
      <div class="quick-action-card" @click="generateReport">
        <div class="action-icon">📊</div>
        <div class="action-text">Generate Report</div>
        <div class="action-sub">Visitor analytics</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Visitor Traffic Trend</span>
          <span class="chart-subtitle">Last 7 days</span>
        </div>
        <div class="chart-container" ref="trafficChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Visitors by Purpose</span>
          <span class="chart-subtitle">Visit reason distribution</span>
        </div>
        <div class="chart-container" ref="purposeChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <div class="search-wrapper">
          <el-icon class="search-icon"><Search /></el-icon>
          <el-input
              v-model="searchText"
              placeholder="Search by name, company, or phone..."
              class="search-input"
              clearable
          />
        </div>
        <el-select v-model="statusFilter" placeholder="Status" clearable class="filter-select">
          <el-option label="All" value="" />
          <el-option label="Expected" value="expected" />
          <el-option label="Checked In" value="checked-in" />
          <el-option label="Completed" value="completed" />
          <el-option label="No-Show" value="no-show" />
        </el-select>
        <el-select v-model="hostFilter" placeholder="Host" clearable class="filter-select" filterable>
          <el-option v-for="h in hosts" :key="h" :label="h" :value="h" />
        </el-select>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="→"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            class="date-picker"
            :shortcuts="dateShortcuts"
        />
      </div>
      <div class="filter-right">
        <el-button class="reset-btn" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Visitors Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Visitor Records</span>
        <el-button size="small" class="view-all-btn" @click="viewAllVisitors">View All →</el-button>
      </div>
      <el-table :data="paginatedVisitors" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewVisitorDetail" class="visitor-table">
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="name" label="Visitor Name" min-width="150">
          <template #default="{ row }">
            <div class="visitor-name-cell">
              <div class="visitor-avatar">{{ row.name.charAt(0) }}</div>
              <div>
                <div class="visitor-name">{{ row.name }}</div>
                <div class="visitor-company">{{ row.company }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="Phone" width="130" />
        <el-table-column prop="host" label="Host" width="130" />
        <el-table-column prop="purpose" label="Purpose" width="130">
          <template #default="{ row }">
            <el-tag :type="getPurposeTagType(row.purpose)" size="small">{{ row.purpose }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="checkInTime" label="Check-in Time" width="160" />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="viewVisitorDetail(row)">
              <el-icon><View /></el-icon>
            </el-button>
            <el-button v-if="row.status === 'expected'" link type="success" size="small" @click.stop="checkInVisitor(row)">
              <el-icon><CircleCheck /></el-icon>
            </el-button>
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

    <!-- Register Visitor Dialog -->
    <el-dialog v-model="registerDialogVisible" title="Register Visitor" width="550px" class="register-dialog">
      <div class="dialog-header-icon">👤</div>
      <el-form :model="visitorForm" :rules="formRules" ref="formRef" label-width="110px" class="visitor-form">
        <el-form-item label="Full Name" prop="name">
          <el-input v-model="visitorForm.name" placeholder="Enter visitor name" />
        </el-form-item>
        <el-form-item label="Company" prop="company">
          <el-input v-model="visitorForm.company" placeholder="Enter company name" />
        </el-form-item>
        <el-form-item label="Phone Number" prop="phone">
          <el-input v-model="visitorForm.phone" placeholder="Enter phone number" />
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="visitorForm.email" placeholder="Enter email address" />
        </el-form-item>
        <el-form-item label="Host" prop="host">
          <el-select v-model="visitorForm.host" placeholder="Select host" filterable style="width: 100%">
            <el-option v-for="h in hosts" :key="h" :label="h" :value="h" />
          </el-select>
        </el-form-item>
        <el-form-item label="Purpose" prop="purpose">
          <el-select v-model="visitorForm.purpose" placeholder="Select purpose" style="width: 100%">
            <el-option label="Business Meeting" value="Business Meeting" />
            <el-option label="Interview" value="Interview" />
            <el-option label="Delivery" value="Delivery" />
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Tour" value="Tour" />
            <el-option label="Other" value="Other" />
          </el-select>
        </el-form-item>
        <el-form-item label="Visit Date" prop="visitDate">
          <el-date-picker v-model="visitorForm.visitDate" type="date" placeholder="Select date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Expected Time">
          <el-time-picker v-model="visitorForm.expectedTime" placeholder="Select time" format="HH:mm" value-format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Vehicle Plate" prop="vehiclePlate">
          <el-input v-model="visitorForm.vehiclePlate" placeholder="Optional" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="visitorForm.notes" type="textarea" :rows="2" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="registerDialogVisible = false">Cancel</el-button>
          <el-button class="submit-btn" @click="submitRegistration">
            <el-icon><Plus /></el-icon> Register Visitor
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Visitor Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedVisitor?.name" width="600px" class="detail-dialog">
      <div v-if="selectedVisitor" class="visitor-detail">
        <div class="detail-header">
          <div class="detail-avatar">{{ selectedVisitor.name.charAt(0) }}</div>
          <div class="detail-info">
            <h3>{{ selectedVisitor.name }}</h3>
            <p>{{ selectedVisitor.company }}</p>
          </div>
          <el-tag :type="getStatusTagType(selectedVisitor.status)" size="large">{{ getStatusText(selectedVisitor.status) }}</el-tag>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Phone">{{ selectedVisitor.phone }}</el-descriptions-item>
          <el-descriptions-item label="Email">{{ selectedVisitor.email }}</el-descriptions-item>
          <el-descriptions-item label="Host">{{ selectedVisitor.host }}</el-descriptions-item>
          <el-descriptions-item label="Purpose">
            <el-tag :type="getPurposeTagType(selectedVisitor.purpose)" size="small">{{ selectedVisitor.purpose }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Check-in Time">{{ selectedVisitor.checkInTime || 'Not checked in' }}</el-descriptions-item>
          <el-descriptions-item label="Check-out Time">{{ selectedVisitor.checkOutTime || 'Not checked out' }}</el-descriptions-item>
          <el-descriptions-item label="Vehicle Plate">{{ selectedVisitor.vehiclePlate || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Badge Number">{{ selectedVisitor.badgeNumber || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Notes" :span="2">{{ selectedVisitor.notes || 'No notes' }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions" v-if="selectedVisitor.status === 'expected'">
          <el-button type="success" @click="checkInVisitor(selectedVisitor)">Check In Now</el-button>
        </div>
        <div class="detail-actions" v-if="selectedVisitor.status === 'checked-in'">
          <el-button type="warning" @click="checkOutVisitor(selectedVisitor)">Check Out</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="printBadge(selectedVisitor)">Print Badge</el-button>
        <el-button type="warning" @click="sendNotification(selectedVisitor)">Send Reminder</el-button>
      </template>
    </el-dialog>

    <!-- Quick Check-in Dialog -->
    <el-dialog v-model="quickCheckinDialogVisible" title="Quick Check-in" width="450px" class="quick-checkin-dialog">
      <div class="quick-checkin-content">
        <div class="qr-placeholder">
          <el-icon><Camera /></el-icon>
          <span>Scan QR Code</span>
        </div>
        <p class="or-text">or</p>
        <el-input
            v-model="quickCheckinCode"
            placeholder="Enter registration code or phone number"
            class="quick-input"
        />
      </div>
      <template #footer>
        <el-button @click="quickCheckinDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="processQuickCheckin">Find Visitor</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  User, Plus, Refresh, CircleCheck, Clock, Timer, Download,
  Search, RefreshLeft, View, Camera
} from '@element-plus/icons-vue'

// ==================== Helper Functions ====================
const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    expected: 'Expected', 'checked-in': 'Checked In', completed: 'Completed', 'no-show': 'No-Show'
  }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = {
    expected: 'info', 'checked-in': 'success', completed: '', 'no-show': 'danger'
  }
  return map[status] || 'info'
}

const getPurposeTagType = (purpose: string): string => {
  const map: Record<string, string> = {
    'Business Meeting': 'primary',
    'Interview': 'success',
    'Delivery': 'warning',
    'Maintenance': 'info',
    'Tour': '',
    'Other': ''
  }
  return map[purpose] || 'info'
}

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading visitor data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading visitor data...',
  'Fetching check-in records...',
  'Loading host information...',
  'Almost ready...'
]

// ==================== Types ====================
interface Visitor {
  id: string
  name: string
  company: string
  phone: string
  email: string
  host: string
  purpose: string
  visitDate: string
  expectedTime: string
  checkInTime: string | null
  checkOutTime: string | null
  status: string
  vehiclePlate: string
  badgeNumber: string
  notes: string
}

// ==================== Mock Data ====================
const hosts = ['John Tan', 'Mike Chen', 'Ahmad Ibrahim', 'Lim Wei Ming', 'Sarah Koh', 'David Lee', 'Priya Sharma']

const generateVisitors = (): Visitor[] => {
  const visitors: Visitor[] = []
  const names = ['Tan Ah Kow', 'Lim Bee Hua', 'Wong Wei Ming', 'Goh Siew Lee', 'Ong Kian Teck', 'Yap Cheng Huat', 'Chua Soon Keat']
  const companies = ['Tech Solutions Pte Ltd', 'Global Trading', 'ABC Corporation', 'SME Services', 'Data Center Asia', 'Cloud Innovations']
  const purposes = ['Business Meeting', 'Interview', 'Delivery', 'Maintenance', 'Tour', 'Other']

  const today = new Date().toISOString().slice(0, 10)

  for (let i = 0; i < 45; i++) {
    const date = new Date()
    date.setDate(date.getDate() - Math.floor(Math.random() * 7))
    const dateStr = date.toISOString().slice(0, 10)
    const isToday = dateStr === today

    let status = 'expected'
    let checkInTime = null
    let checkOutTime = null

    if (isToday) {
      const random = Math.random()
      if (random < 0.5) {
        status = 'expected'
      } else if (random < 0.8) {
        status = 'checked-in'
        checkInTime = `${Math.floor(Math.random() * 10 + 8)}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`
      } else {
        status = 'completed'
        checkInTime = `${Math.floor(Math.random() * 10 + 8)}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`
        checkOutTime = `${Math.floor(parseInt(checkInTime.split(':')[0]) + 1)}:${checkInTime.split(':')[1]}`
      }
    } else if (date < new Date()) {
      status = Math.random() > 0.7 ? 'no-show' : 'completed'
    }

    visitors.push({
      id: `VIS-${String(i + 1).padStart(6, '0')}`,
      name: names[Math.floor(Math.random() * names.length)] + ' ' + (Math.floor(Math.random() * 100) + 1),
      company: companies[Math.floor(Math.random() * companies.length)],
      phone: `+65 9${Math.floor(Math.random() * 9000 + 1000)} ${Math.floor(Math.random() * 9000 + 1000)}`,
      email: `visitor${i + 1}@example.com`,
      host: hosts[Math.floor(Math.random() * hosts.length)],
      purpose: purposes[Math.floor(Math.random() * purposes.length)],
      visitDate: dateStr,
      expectedTime: `${Math.floor(Math.random() * 10 + 9)}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`,
      checkInTime: checkInTime,
      checkOutTime: checkOutTime,
      status: status,
      vehiclePlate: Math.random() > 0.7 ? `SGD${Math.floor(Math.random() * 9000 + 1000)}` : '',
      badgeNumber: status !== 'expected' ? `B${Math.floor(Math.random() * 9000 + 1000)}` : '',
      notes: ''
    })
  }

  return visitors.sort((a, b) => b.visitDate.localeCompare(a.visitDate))
}

const visitors = ref<Visitor[]>(generateVisitors())

// ==================== State ====================
const searchText = ref('')
const statusFilter = ref('')
const hostFilter = ref('')
const dateRange = ref<Date[] | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const registerDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const quickCheckinDialogVisible = ref(false)
const selectedVisitor = ref<Visitor | null>(null)
const quickCheckinCode = ref('')
const formRef = ref()

// Chart refs
let trafficChart: echarts.ECharts | null = null
let purposeChart: echarts.ECharts | null = null

const trafficChartEl = ref<HTMLElement | null>(null)
const purposeChartEl = ref<HTMLElement | null>(null)

const visitorForm = ref({
  name: '',
  company: '',
  phone: '',
  email: '',
  host: '',
  purpose: '',
  visitDate: new Date().toISOString().slice(0, 10),
  expectedTime: '10:00',
  vehiclePlate: '',
  notes: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter visitor name', trigger: 'blur' }],
  company: [{ required: true, message: 'Please enter company name', trigger: 'blur' }],
  phone: [{ required: true, message: 'Please enter phone number', trigger: 'blur' }],
  host: [{ required: true, message: 'Please select host', trigger: 'change' }],
  purpose: [{ required: true, message: 'Please select purpose', trigger: 'change' }]
}

const dateShortcuts = [
  { text: 'Today', value: () => {
      const today = new Date()
      return [today, today]
    }},
  { text: 'Last 7 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'This Month', value: () => {
      const start = new Date()
      start.setDate(1)
      const end = new Date()
      return [start, end]
    }}
]

// ==================== Computed ====================
const stats = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  const todayVisitors = visitors.value.filter(v => v.visitDate === today).length
  const checkedIn = visitors.value.filter(v => v.status === 'checked-in').length
  const expectedVisitors = visitors.value.filter(v => v.status === 'expected' && v.visitDate === today).length
  const completedVisits = visitors.value.filter(v => v.status === 'completed').length
  const noShow = visitors.value.filter(v => v.status === 'no-show').length
  const pendingCheckIn = expectedVisitors
  const checkInRate = todayVisitors > 0 ? Math.round((checkedIn / todayVisitors) * 100) : 0
  const avgStayDuration = 48

  return {
    todayVisitors,
    todayGrowth: 12,
    checkedIn,
    checkInRate,
    expectedVisitors,
    avgStayDuration,
    pendingCheckIn,
    completedVisits,
    noShow
  }
})

const filteredVisitors = computed(() => {
  let filtered = [...visitors.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(v =>
        v.name.toLowerCase().includes(search) ||
        v.company.toLowerCase().includes(search) ||
        v.phone.includes(search)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(v => v.status === statusFilter.value)
  }

  if (hostFilter.value) {
    filtered = filtered.filter(v => v.host === hostFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(v => {
      const visitDate = new Date(v.visitDate)
      return visitDate >= start && visitDate <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredVisitors.value.length)

const paginatedVisitors = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredVisitors.value.slice(start, end)
})

// ==================== Chart Functions ====================
const initTrafficChart = () => {
  if (!trafficChartEl.value) return
  if (trafficChart) {
    trafficChart.dispose()
    trafficChart = null
  }

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const visitorsData = [45, 52, 48, 58, 65, 32, 28]

  trafficChart = echarts.init(trafficChartEl.value)
  trafficChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 40, left: 60, right: 30, bottom: 30 },
    xAxis: { type: 'category', data: days, axisLabel: { fontSize: 12 } },
    yAxis: { type: 'value', name: 'Number of Visitors' },
    series: [{
      type: 'bar',
      data: visitorsData,
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 50) return '#ef4444'
          if (value > 40) return '#f59e0b'
          return '#22c55e'
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initPurposeChart = () => {
  if (!purposeChartEl.value) return
  if (purposeChart) {
    purposeChart.dispose()
    purposeChart = null
  }

  const purposeCount = new Map<string, number>()
  visitors.value.forEach(v => {
    purposeCount.set(v.purpose, (purposeCount.get(v.purpose) || 0) + 1)
  })

  const data = Array.from(purposeCount.entries()).map(([name, value]) => ({ name, value }))

  purposeChart = echarts.init(purposeChartEl.value)
  purposeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} visitors ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initTrafficChart()
    initPurposeChart()
  })
}

// ==================== Actions ====================
const resetFilters = () => {
  searchText.value = ''
  statusFilter.value = ''
  hostFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const viewVisitorDetail = (visitor: Visitor) => {
  selectedVisitor.value = visitor
  detailDialogVisible.value = true
}

const checkInVisitor = (visitor: Visitor) => {
  const index = visitors.value.findIndex(v => v.id === visitor.id)
  if (index !== -1) {
    const now = new Date()
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    visitors.value[index] = {
      ...visitors.value[index],
      status: 'checked-in',
      checkInTime: timeStr,
      badgeNumber: `B${Math.floor(Math.random() * 9000 + 1000)}`
    }
    ElMessage.success(`${visitor.name} checked in successfully`)
    detailDialogVisible.value = false
  }
}

const checkOutVisitor = (visitor: Visitor) => {
  const index = visitors.value.findIndex(v => v.id === visitor.id)
  if (index !== -1) {
    const now = new Date()
    const timeStr = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`
    visitors.value[index] = {
      ...visitors.value[index],
      status: 'completed',
      checkOutTime: timeStr
    }
    ElMessage.success(`${visitor.name} checked out successfully`)
    detailDialogVisible.value = false
  }
}

const printBadge = (visitor: Visitor | null) => {
  if (visitor) {
    ElMessage.success(`Printing badge for ${visitor.name}`)
  }
}

const sendNotification = (visitor: Visitor | null) => {
  if (visitor) {
    ElMessage.success(`Reminder sent to ${visitor.name}`)
  }
}

const openRegisterDialog = () => {
  visitorForm.value = {
    name: '',
    company: '',
    phone: '',
    email: '',
    host: '',
    purpose: '',
    visitDate: new Date().toISOString().slice(0, 10),
    expectedTime: '10:00',
    vehiclePlate: '',
    notes: ''
  }
  registerDialogVisible.value = true
}

const submitRegistration = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      const newVisitor: Visitor = {
        id: `VIS-${String(visitors.value.length + 1).padStart(6, '0')}`,
        name: visitorForm.value.name,
        company: visitorForm.value.company,
        phone: visitorForm.value.phone,
        email: visitorForm.value.email,
        host: visitorForm.value.host,
        purpose: visitorForm.value.purpose,
        visitDate: visitorForm.value.visitDate,
        expectedTime: visitorForm.value.expectedTime,
        checkInTime: null,
        checkOutTime: null,
        status: 'expected',
        vehiclePlate: visitorForm.value.vehiclePlate,
        badgeNumber: '',
        notes: visitorForm.value.notes
      }
      visitors.value.unshift(newVisitor)
      ElMessage.success('Visitor registered successfully')
      registerDialogVisible.value = false
    }
  })
}

const quickCheckIn = () => {
  quickCheckinCode.value = ''
  quickCheckinDialogVisible.value = true
}

const processQuickCheckin = () => {
  if (!quickCheckinCode.value) {
    ElMessage.warning('Please enter registration code or phone number')
    return
  }
  const visitor = visitors.value.find(v => v.phone.includes(quickCheckinCode.value) || v.id === quickCheckinCode.value)
  if (visitor && visitor.status === 'expected') {
    checkInVisitor(visitor)
    quickCheckinDialogVisible.value = false
  } else if (visitor && visitor.status !== 'expected') {
    ElMessage.warning('Visitor already checked in or completed')
  } else {
    ElMessage.warning('Visitor not found')
  }
}

const openPreRegister = () => {
  openRegisterDialog()
}

const openBulkRegister = () => {
  ElMessage.info('CSV import feature coming soon')
}

const generateReport = () => {
  ElMessage.success('Generating visitor report...')
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportTodayData = () => {
  ElMessage.success('Exporting today\'s visitor data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const viewAllVisitors = () => {
  ElMessage.info('Viewing all visitors')
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  visitors.value = generateVisitors()
  refreshCharts()
  ElMessage.success('Data refreshed')
}

// ==================== Watch ====================
watch([searchText, statusFilter, hostFilter, dateRange], () => {
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
    if (trafficChart && !trafficChart.isDisposed()) trafficChart.resize()
    if (purposeChart && !purposeChart.isDisposed()) purposeChart.resize()
  })
})

onUnmounted(() => {
  if (trafficChart && !trafficChart.isDisposed()) trafficChart.dispose()
  if (purposeChart && !purposeChart.isDisposed()) purposeChart.dispose()
})
</script>

<style scoped>
/* 样式与之前保持一致，使用相同的设计语言 */
.visitor-management-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f0fe 100%);
  padding: 28px;
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
  border-radius: 10px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
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
  padding: 48px;
  border-radius: 40px;
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
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.title-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin-left: 62px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.primary-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.primary-btn:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.secondary-btn {
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 10px 20px;
  border-radius: 12px;
  transition: all 0.3s;
}

.secondary-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateY(-2px);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.stat-card {
  background: white;
  border-radius: 24px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.stat-icon.blue { background: linear-gradient(135deg, #eef2ff, #dbeafe); color: #3b82f6; }
.stat-icon.green { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #22c55e; }
.stat-icon.orange { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #f59e0b; }
.stat-icon.purple { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); color: #8b5cf6; }

.stat-info {
  flex: 1;
}

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
  margin-top: 6px;
}

.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }

/* Today's Visitors */
.today-visitors {
  background: white;
  border-radius: 24px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  font-size: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.outline-btn {
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 40px;
  padding: 6px 16px;
}

.visitors-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.visitor-stat-item {
  text-align: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 20px;
}

.visitor-stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #1e293b;
}

.visitor-stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.visitor-stat-progress {
  margin-top: 12px;
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #22c55e, #16a34a);
  border-radius: 3px;
}

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.quick-action-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.quick-action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.action-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.action-text {
  font-weight: 600;
  color: #1e293b;
}

.action-sub {
  font-size: 11px;
  color: #94a3b8;
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
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.chart-header {
  margin-bottom: 16px;
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
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 14px;
  color: #94a3b8;
}

.search-input {
  width: 220px;
}
.search-input :deep(.el-input__wrapper) {
  padding-left: 36px;
  border-radius: 40px;
}

.filter-select {
  width: 150px;
}
.filter-select :deep(.el-input__wrapper) {
  border-radius: 40px;
}

.date-picker {
  width: 260px;
}
.date-picker :deep(.el-input__wrapper) {
  border-radius: 40px;
}

.reset-btn {
  color: #64748b;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 24px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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

.view-all-btn {
  background: transparent;
  border: none;
  color: #3b82f6;
}

.visitor-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.visitor-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
}

.visitor-name {
  font-weight: 500;
}

.visitor-company {
  font-size: 11px;
  color: #94a3b8;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Visitor Detail */
.visitor-detail {
  padding: 8px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 20px;
}

.detail-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 28px;
  font-weight: 600;
}

.detail-info h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
}

.detail-info p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.detail-actions {
  margin-top: 20px;
  text-align: center;
}

/* Dialogs */
.register-dialog :deep(.el-dialog__header),
.detail-dialog :deep(.el-dialog__header),
.quick-checkin-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #eef2f8;
  padding: 20px 24px;
}

.dialog-header-icon {
  text-align: center;
  font-size: 48px;
  margin-bottom: 16px;
}

.visitor-form {
  padding: 0 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 40px;
  padding: 8px 20px;
}

.submit-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  color: white;
  border-radius: 40px;
  padding: 8px 20px;
}

/* Quick Checkin */
.quick-checkin-content {
  text-align: center;
  padding: 20px;
}

.qr-placeholder {
  background: #f8fafc;
  border-radius: 20px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #64748b;
}

.qr-placeholder .el-icon {
  font-size: 64px;
}

.or-text {
  margin: 16px 0;
  color: #94a3b8;
}

.quick-input {
  margin-top: 8px;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .visitors-stats-row, .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .stats-grid, .visitors-stats-row, .quick-actions {
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
  .search-wrapper, .search-input, .filter-select, .date-picker {
    width: 100%;
  }
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 16px;
  overflow: hidden;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc;
  color: #1e293b;
  font-weight: 600;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
</style>