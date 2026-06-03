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
        <div class="loading-tip">Fire Impairment Status</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="impairment-container">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Fire Impairment Status</h2>
        <p class="header-subtitle">NFPA 25 Compliance | Impairment Tracking & Management</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="handleNewImpairment">
          <el-icon><Plus /></el-icon>
          New Impairment
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- System Overview Cards -->
    <el-row :gutter="20" class="overview-row">
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon active">
            <el-icon :size="28"><WarningFilled /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Active Impairments</div>
            <div class="overview-value" :class="{ 'has-impairment': stats.active > 0 }">{{ stats.active }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon planned">
            <el-icon :size="28"><Calendar /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Planned</div>
            <div class="overview-value">{{ stats.planned }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon resolved">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Resolved (30 days)</div>
            <div class="overview-value">{{ stats.resolved }}</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <div class="overview-card">
          <div class="overview-icon overdue">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div class="overview-info">
            <div class="overview-label">Overdue</div>
            <div class="overview-value" :class="{ 'has-overdue': stats.overdue > 0 }">{{ stats.overdue }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Active Impairments Section -->
    <div v-if="activeImpairments.length > 0" class="active-section">
      <div class="section-title">
        <span class="active-title">
          <el-icon><WarningFilled /></el-icon>
          Active Impairments
        </span>
        <el-badge :value="activeImpairments.length" type="danger" />
      </div>
      <el-card shadow="hover" class="active-card">
        <el-table :data="activeImpairments" stripe border style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="system" label="System" min-width="150" />
          <el-table-column prop="type" label="Impairment Type" width="140">
            <template #default="{ row }">
              <el-tag :type="row.type === 'Emergency' ? 'danger' : 'warning'" size="small">
                {{ row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="Reason" min-width="200" />
          <el-table-column prop="startDate" label="Start Date" width="110" sortable />
          <el-table-column prop="expectedEndDate" label="Expected End" width="110" />
          <el-table-column prop="daysActive" label="Days Active" width="100" sortable />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag type="danger" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" fixed="right" width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewImpairment(row)">
                View
              </el-button>
              <el-button type="success" link size="small" @click="resolveImpairment(row)">
                Resolve
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Impairment Statistics -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Impairment by System</span>
            </div>
          </template>
          <div ref="systemChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Impairment Trend (Last 6 Months)</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Impairment History Table -->
    <el-card shadow="hover" class="history-card">
      <template #header>
        <div class="card-header">
          <span>Impairment History</span>
          <div class="filter-group">
            <el-select v-model="statusFilter" size="small" style="width: 120px" placeholder="Status" clearable>
              <el-option label="All" value="all" />
              <el-option label="Active" value="Active" />
              <el-option label="Resolved" value="Resolved" />
              <el-option label="Planned" value="Planned" />
            </el-select>
            <el-select v-model="systemFilter" size="small" style="width: 150px" placeholder="System" clearable>
              <el-option label="All Systems" value="all" />
              <el-option label="Sprinkler System" value="Sprinkler System" />
              <el-option label="Fire Pump" value="Fire Pump" />
              <el-option label="Alarm System" value="Alarm System" />
              <el-option label="Hydrant System" value="Hydrant System" />
            </el-select>
            <el-input v-model="searchText" placeholder="Search..." style="width: 180px" clearable>
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </div>
      </template>
      <el-table :data="paginatedImpairments" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="system" label="System" min-width="150" />
        <el-table-column prop="type" label="Type" width="110">
          <template #default="{ row }">
            <el-tag :type="row.type === 'Emergency' ? 'danger' : 'warning'" size="small">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="Reason" min-width="180" />
        <el-table-column prop="startDate" label="Start Date" width="100" sortable />
        <el-table-column prop="endDate" label="End Date" width="100" />
        <el-table-column prop="duration" label="Duration (days)" width="110" sortable />
        <el-table-column prop="status" label="Status" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'danger' : (row.status === 'Resolved' ? 'success' : 'info')" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resolvedBy" label="Resolved By" min-width="120" />
        <el-table-column label="Actions" fixed="right" width="100">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewImpairment(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredImpairments.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- New Impairment Dialog -->
    <el-dialog v-model="dialogVisible" title="New Fire Impairment" width="550px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="130px">
        <el-form-item label="System" prop="system">
          <el-select v-model="formData.system" placeholder="Select system" style="width: 100%">
            <el-option label="Sprinkler System" value="Sprinkler System" />
            <el-option label="Fire Pump" value="Fire Pump" />
            <el-option label="Alarm System" value="Alarm System" />
            <el-option label="Hydrant System" value="Hydrant System" />
            <el-option label="Standpipe System" value="Standpipe System" />
          </el-select>
        </el-form-item>
        <el-form-item label="Impairment Type" prop="type">
          <el-radio-group v-model="formData.type">
            <el-radio label="Planned">Planned (Maintenance)</el-radio>
            <el-radio label="Emergency">Emergency (Repair)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Reason" prop="reason">
          <el-input v-model="formData.reason" type="textarea" :rows="2" placeholder="Enter reason for impairment" />
        </el-form-item>
        <el-form-item label="Start Date" prop="startDate">
          <el-date-picker v-model="formData.startDate" type="date" placeholder="Select start date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Expected End Date" prop="expectedEndDate">
          <el-date-picker v-model="formData.expectedEndDate" type="date" placeholder="Select expected end date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Affected Area" prop="affectedArea">
          <el-input v-model="formData.affectedArea" placeholder="e.g., Building A, Floor 1-3" />
        </el-form-item>
        <el-form-item label="Precautionary Measures" prop="precautions">
          <el-input v-model="formData.precautions" type="textarea" :rows="2" placeholder="Fire watch, temporary systems, etc." />
        </el-form-item>
        <el-form-item label="Notified Parties" prop="notifiedParties">
          <el-input v-model="formData.notifiedParties" placeholder="List of notified persons/departments" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitImpairment">Submit Impairment</el-button>
      </template>
    </el-dialog>

    <!-- Impairment Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Impairment Details - #${selectedImpairment?.id}`" width="650px">
      <el-descriptions :column="2" border v-if="selectedImpairment">
        <el-descriptions-item label="Impairment ID">#{{ selectedImpairment.id }}</el-descriptions-item>
        <el-descriptions-item label="System">{{ selectedImpairment.system }}</el-descriptions-item>
        <el-descriptions-item label="Type">
          <el-tag :type="selectedImpairment.type === 'Emergency' ? 'danger' : 'warning'" size="small">
            {{ selectedImpairment.type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedImpairment.status === 'Active' ? 'danger' : 'success'" size="small">
            {{ selectedImpairment.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Reason" :span="2">{{ selectedImpairment.reason }}</el-descriptions-item>
        <el-descriptions-item label="Start Date">{{ selectedImpairment.startDate }}</el-descriptions-item>
        <el-descriptions-item label="End Date">{{ selectedImpairment.endDate || 'Not resolved' }}</el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedImpairment.duration || 'Active' }} days</el-descriptions-item>
        <el-descriptions-item label="Affected Area">{{ selectedImpairment.affectedArea || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Precautions">{{ selectedImpairment.precautions || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Notified Parties">{{ selectedImpairment.notifiedParties || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedImpairment.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ selectedImpairment.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="Resolved By" v-if="selectedImpairment.resolvedBy">{{ selectedImpairment.resolvedBy }}</el-descriptions-item>
        <el-descriptions-item label="Resolution Notes" v-if="selectedImpairment.resolutionNotes" :span="2">{{ selectedImpairment.resolutionNotes }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Resolve Impairment Dialog -->
    <el-dialog v-model="resolveDialogVisible" title="Resolve Impairment" width="450px">
      <el-form :model="resolveForm" label-width="120px">
        <el-form-item label="Impairment ID">
          <span>{{ resolveForm.id }}</span>
        </el-form-item>
        <el-form-item label="System">
          <span>{{ resolveForm.system }}</span>
        </el-form-item>
        <el-form-item label="Resolution Notes" required>
          <el-input v-model="resolveForm.resolutionNotes" type="textarea" :rows="3" placeholder="Enter resolution notes" />
        </el-form-item>
        <el-form-item label="System Restored">
          <el-switch v-model="resolveForm.systemRestored" active-text="Yes" inactive-text="No" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmResolve">Confirm Resolution</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Download,
  Refresh,
  WarningFilled,
  Calendar,
  CircleCheck,
  Timer,
  Plus,
  Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading impairment data...',
  'Checking active impairments...',
  'Almost ready...'
]

// ==================== Data State ====================
const statusFilter = ref('all')
const systemFilter = ref('all')
const searchText = ref('')

interface Impairment {
  id: number
  system: string
  type: 'Planned' | 'Emergency'
  reason: string
  startDate: string
  endDate: string | null
  expectedEndDate: string | null
  duration: number | null
  daysActive: number | null
  status: 'Active' | 'Resolved' | 'Planned'
  affectedArea: string
  precautions: string
  notifiedParties: string
  createdBy: string
  createdAt: string
  resolvedBy: string | null
  resolutionNotes: string | null
}

const impairments = ref<Impairment[]>([])
const activeImpairments = ref<Impairment[]>([])

const stats = computed(() => {
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

  const resolvedCount = impairments.value.filter(i => {
    if (i.status !== 'Resolved') return false
    if (!i.endDate) return false
    return new Date(i.endDate) >= thirtyDaysAgo
  }).length

  const overdueCount = impairments.value.filter(i => {
    if (i.status !== 'Active') return false
    if (!i.expectedEndDate) return false
    return new Date(i.expectedEndDate) < new Date()
  }).length

  return {
    active: impairments.value.filter(i => i.status === 'Active').length,
    planned: impairments.value.filter(i => i.status === 'Planned').length,
    resolved: resolvedCount,
    overdue: overdueCount
  }
})

const filteredImpairments = computed(() => {
  let filtered = impairments.value
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(i => i.status === statusFilter.value)
  }
  if (systemFilter.value !== 'all') {
    filtered = filtered.filter(i => i.system === systemFilter.value)
  }
  if (searchText.value) {
    filtered = filtered.filter(i =>
        i.system.toLowerCase().includes(searchText.value.toLowerCase()) ||
        i.reason.toLowerCase().includes(searchText.value.toLowerCase()) ||
        i.id.toString().includes(searchText.value)
    )
  }
  return filtered
})

const pagination = ref({ currentPage: 1, pageSize: 10 })
const paginatedImpairments = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  return filteredImpairments.value.slice(start, start + pagination.value.pageSize)
})

// Generate mock impairments
const generateImpairments = (): Impairment[] => {
  const mockImpairments: Impairment[] = [
    {
      id: 1001,
      system: 'Sprinkler System',
      type: 'Planned',
      reason: 'Annual inspection and testing',
      startDate: '2024-01-10',
      endDate: '2024-01-12',
      expectedEndDate: '2024-01-12',
      duration: 2,
      daysActive: null,
      status: 'Resolved',
      affectedArea: 'Building A, Floors 1-5',
      precautions: 'Fire watch personnel deployed, temporary water supply',
      notifiedParties: 'Facility Management, Safety Team, Tenants',
      createdBy: 'John Smith',
      createdAt: '2024-01-05 09:00:00',
      resolvedBy: 'John Smith',
      resolutionNotes: 'Inspection completed, system fully operational'
    },
    {
      id: 1002,
      system: 'Fire Pump',
      type: 'Emergency',
      reason: 'Pump controller failure',
      startDate: '2024-01-14',
      endDate: null,
      expectedEndDate: '2024-01-21',
      duration: null,
      daysActive: 5,
      status: 'Active',
      affectedArea: 'Entire Facility',
      precautions: 'Manual fire watch, temporary diesel pump on standby',
      notifiedParties: 'Fire Department, Insurance, Management',
      createdBy: 'Sarah Johnson',
      createdAt: '2024-01-14 08:30:00',
      resolvedBy: null,
      resolutionNotes: null
    },
    {
      id: 1003,
      system: 'Alarm System',
      type: 'Planned',
      reason: 'Control panel upgrade',
      startDate: '2024-01-20',
      endDate: null,
      expectedEndDate: '2024-01-22',
      duration: null,
      daysActive: 0,
      status: 'Planned',
      affectedArea: 'Building B',
      precautions: 'Temporary alarm monitoring, increased patrols',
      notifiedParties: 'Security Team, Monitoring Center',
      createdBy: 'Mike Chen',
      createdAt: '2024-01-15 14:00:00',
      resolvedBy: null,
      resolutionNotes: null
    },
    {
      id: 1004,
      system: 'Hydrant System',
      type: 'Emergency',
      reason: 'Water main break',
      startDate: '2024-01-08',
      endDate: '2024-01-09',
      expectedEndDate: '2024-01-09',
      duration: 1,
      daysActive: null,
      status: 'Resolved',
      affectedArea: 'South Side of Building',
      precautions: 'Fire watch, alternative water source arranged',
      notifiedParties: 'Facility Management, Local Fire Department',
      createdBy: 'David Wong',
      createdAt: '2024-01-08 07:00:00',
      resolvedBy: 'David Wong',
      resolutionNotes: 'Water main repaired, system restored'
    },
    {
      id: 1005,
      system: 'Sprinkler System',
      type: 'Emergency',
      reason: 'Frozen pipe burst',
      startDate: '2024-01-15',
      endDate: null,
      expectedEndDate: '2024-01-18',
      duration: null,
      daysActive: 4,
      status: 'Active',
      affectedArea: 'Warehouse Section C',
      precautions: 'Fire watch, area isolation, portable extinguishers',
      notifiedParties: 'Safety Team, Insurance, Management',
      createdBy: 'Lisa Anderson',
      createdAt: '2024-01-15 10:15:00',
      resolvedBy: null,
      resolutionNotes: null
    }
  ]

  return mockImpairments
}

// Update active impairments
const updateActiveImpairments = () => {
  activeImpairments.value = impairments.value.filter(i => i.status === 'Active')
}

// Calculate days active
const calculateDaysActive = () => {
  impairments.value.forEach(impairment => {
    if (impairment.status === 'Active' && impairment.startDate) {
      const start = new Date(impairment.startDate)
      const today = new Date()
      const diffTime = Math.abs(today.getTime() - start.getTime())
      impairment.daysActive = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    }
  })
}

// ==================== Chart Functions ====================
const systemChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

let systemChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (systemChartRef.value) {
      if (systemChart) systemChart.dispose()
      systemChart = echarts.init(systemChartRef.value)
      updateSystemChart()
    }

    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }
  })
}

const updateSystemChart = () => {
  const systems = ['Sprinkler System', 'Fire Pump', 'Alarm System', 'Hydrant System']
  const counts = systems.map(sys => impairments.value.filter(i => i.system === sys).length)

  systemChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: systems, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Number of Impairments' },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
          return colors[params.dataIndex % colors.length]
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const updateTrendChart = () => {
  const months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']
  const plannedData = [2, 1, 3, 2, 1, 2]
  const emergencyData = [0, 1, 1, 2, 1, 2]

  trendChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Planned', 'Emergency'] },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Number of Impairments' },
    series: [
      {
        name: 'Planned',
        type: 'line',
        data: plannedData,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        areaStyle: { opacity: 0.1 }
      },
      {
        name: 'Emergency',
        type: 'line',
        data: emergencyData,
        smooth: true,
        lineStyle: { color: '#F56C6C', width: 3 },
        areaStyle: { opacity: 0.1 }
      }
    ]
  })
}

// ==================== Dialog Actions ====================
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const resolveDialogVisible = ref(false)
const formRef = ref()
const selectedImpairment = ref<Impairment | null>(null)

const formData = ref({
  system: '',
  type: 'Planned',
  reason: '',
  startDate: '',
  expectedEndDate: '',
  affectedArea: '',
  precautions: '',
  notifiedParties: ''
})

const formRules = {
  system: [{ required: true, message: 'Please select system', trigger: 'change' }],
  reason: [{ required: true, message: 'Please enter reason', trigger: 'blur' }],
  startDate: [{ required: true, message: 'Please select start date', trigger: 'change' }],
  expectedEndDate: [{ required: true, message: 'Please select expected end date', trigger: 'change' }]
}

const resolveForm = ref({
  id: '',
  system: '',
  resolutionNotes: '',
  systemRestored: true
})

const handleNewImpairment = () => {
  formData.value = {
    system: '',
    type: 'Planned',
    reason: '',
    startDate: '',
    expectedEndDate: '',
    affectedArea: '',
    precautions: '',
    notifiedParties: ''
  }
  dialogVisible.value = true
}

const submitImpairment = async () => {
  try {
    await formRef.value?.validate()

    const newImpairment: Impairment = {
      id: 2000 + impairments.value.length + 1,
      system: formData.value.system,
      type: formData.value.type as 'Planned' | 'Emergency',
      reason: formData.value.reason,
      startDate: formData.value.startDate,
      endDate: null,
      expectedEndDate: formData.value.expectedEndDate,
      duration: null,
      daysActive: 0,
      status: 'Planned',
      affectedArea: formData.value.affectedArea,
      precautions: formData.value.precautions,
      notifiedParties: formData.value.notifiedParties,
      createdBy: 'Current User',
      createdAt: new Date().toLocaleString(),
      resolvedBy: null,
      resolutionNotes: null
    }

    impairments.value.unshift(newImpairment)
    updateActiveImpairments()
    updateSystemChart()
    updateTrendChart()
    dialogVisible.value = false
    ElMessage.success('Impairment created successfully')
  } catch (error) {
    ElMessage.error('Please fill all required fields')
  }
}

const viewImpairment = (impairment: Impairment) => {
  selectedImpairment.value = impairment
  detailDialogVisible.value = true
}

const resolveImpairment = (impairment: Impairment) => {
  resolveForm.value = {
    id: impairment.id.toString(),
    system: impairment.system,
    resolutionNotes: '',
    systemRestored: true
  }
  resolveDialogVisible.value = true
}

const confirmResolve = () => {
  if (!resolveForm.value.resolutionNotes) {
    ElMessage.warning('Please enter resolution notes')
    return
  }

  const impairment = impairments.value.find(i => i.id === parseInt(resolveForm.value.id))
  if (impairment) {
    impairment.status = 'Resolved'
    impairment.endDate = new Date().toISOString().split('T')[0]
    impairment.resolvedBy = 'Current User'
    impairment.resolutionNotes = resolveForm.value.resolutionNotes
    const start = new Date(impairment.startDate)
    const end = new Date(impairment.endDate)
    const diffTime = Math.abs(end.getTime() - start.getTime())
    impairment.duration = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    impairment.daysActive = null
  }

  updateActiveImpairments()
  updateSystemChart()
  updateTrendChart()
  resolveDialogVisible.value = false
  ElMessage.success('Impairment resolved successfully')
}

// ==================== Actions ====================
const refreshData = () => {
  impairments.value = generateImpairments()
  calculateDaysActive()
  updateActiveImpairments()
  updateSystemChart()
  updateTrendChart()
  ElMessage.success('Data refreshed')
}

const handleExport = () => {
  ElMessage.success('Report export started')
}

const handleSizeChange = () => { pagination.value.currentPage = 1 }
const handleCurrentChange = () => {}

// ==================== Lifecycle ====================
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
      impairments.value = generateImpairments()
      calculateDaysActive()
      updateActiveImpairments()
      initCharts()
    }, 400)
  }, 2000)
})

watch([systemChartRef, trendChartRef], () => {
  window.addEventListener('resize', () => {
    systemChart?.resize()
    trendChart?.resize()
  })
})

watch([statusFilter, systemFilter, searchText], () => {
  pagination.value.currentPage = 1
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Main Container */
.impairment-container {
  padding: 20px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  background: white;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
}

.header-subtitle {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Overview Cards */
.overview-row {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

.overview-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.overview-icon.active { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.overview-icon.planned { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.overview-icon.resolved { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.overview-icon.overdue { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }

.overview-info {
  flex: 1;
}

.overview-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.overview-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.overview-value.has-impairment { color: #F56C6C; }
.overview-value.has-overdue { color: #E6A23C; }

/* Section Title */
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.active-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #F56C6C;
  font-weight: 600;
  font-size: 16px;
}

/* Active Impairments */
.active-section {
  margin-bottom: 24px;
}

.active-card {
  border-radius: 16px;
}

/* Stats Row */
.stats-row {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 16px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

/* History Card */
.history-card {
  border-radius: 16px;
}

.filter-group {
  display: flex;
  gap: 12px;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>