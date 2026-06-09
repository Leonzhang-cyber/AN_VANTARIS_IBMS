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
        <div class="loading-tip">Fault Decisions Register</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="fault-decisions-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Decision Register</el-breadcrumb-item>
            <el-breadcrumb-item>Fault Decisions</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Fault Decisions</h1>
        <p class="description">Manage and track all fault-related decisions, root cause analyses, and resolution actions</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateDecision">
          <el-icon><Plus /></el-icon>
          New Fault Decision
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by title or description"
              prefix-icon="Search"
              clearable
              style="width: 260px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 140px">
            <el-option label="Critical" value="Critical" />
            <el-option label="Major" value="Major" />
            <el-option label="Minor" value="Minor" />
            <el-option label="Warning" value="Warning" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 140px">
            <el-option label="Open" value="Open" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Resolved" value="Resolved" />
            <el-option label="Closed" value="Closed" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 280px"
          />
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Fault Decisions List</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchDecisions" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDecisions" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="Decision Title" min-width="220" show-overflow-tooltip />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="affectedAsset" label="Affected Asset" width="160" show-overflow-tooltip />
        <el-table-column prop="rootCause" label="Root Cause" min-width="200" show-overflow-tooltip />
        <el-table-column prop="resolution" label="Resolution" min-width="200" show-overflow-tooltip />
        <el-table-column prop="decisionMaker" label="Decision Maker" width="130" />
        <el-table-column prop="decisionDate" label="Decision Date" width="120" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">View</el-button>
            <el-button link type="success" size="small" @click="editDecision(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteDecision(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredDecisions.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- View/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'New Fault Decision' : (dialogMode === 'edit' ? 'Edit Fault Decision' : 'Fault Decision Details')" width="700px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Decision Title" prop="title">
              <el-input v-model="formData.title" placeholder="Enter decision title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Severity" prop="severity">
              <el-select v-model="formData.severity" placeholder="Select severity" style="width: 100%">
                <el-option label="Critical" value="Critical" />
                <el-option label="Major" value="Major" />
                <el-option label="Minor" value="Minor" />
                <el-option label="Warning" value="Warning" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
                <el-option label="Open" value="Open" />
                <el-option label="In Progress" value="In Progress" />
                <el-option label="Resolved" value="Resolved" />
                <el-option label="Closed" value="Closed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Affected Asset" prop="affectedAsset">
              <el-input v-model="formData.affectedAsset" placeholder="Enter affected asset" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Decision Maker" prop="decisionMaker">
              <el-input v-model="formData.decisionMaker" placeholder="Enter decision maker name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Decision Date" prop="decisionDate">
              <el-date-picker v-model="formData.decisionDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Estimated Cost" prop="estimatedCost">
              <el-input-number v-model="formData.estimatedCost" :min="0" :step="1000" style="width: 100%" />
              <span style="margin-left: 8px; color: #909399">USD</span>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Root Cause" prop="rootCause">
              <el-input v-model="formData.rootCause" type="textarea" :rows="2" placeholder="Enter root cause analysis" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Resolution" prop="resolution">
              <el-input v-model="formData.resolution" type="textarea" :rows="2" placeholder="Enter resolution actions" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter additional description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button v-if="dialogMode !== 'view'" type="primary" @click="submitForm">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete decision "{{ deleteTarget?.title }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading fault decisions...',
  'Fetching register data...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface FaultDecision {
  id: number
  title: string
  severity: string
  status: string
  affectedAsset: string
  rootCause: string
  resolution: string
  decisionMaker: string
  decisionDate: string
  estimatedCost: number
  description: string
}

interface StatCard {
  title: string
  value: number
  trend: number
  icon: string
  bgColor: string
  key: string
}

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Fault Decisions', value: 142, trend: 8, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Open / In Progress', value: 38, trend: -5, icon: 'Clock', bgColor: '#e6a23c', key: 'open' },
  { title: 'Resolved / Closed', value: 104, trend: 12, icon: 'Checked', bgColor: '#67c23a', key: 'resolved' },
  { title: 'Avg Resolution Time', value: '4.2', trend: -10, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'avgTime' }
])

const faultDecisions = ref<FaultDecision[]>([
  {
    id: 1,
    title: 'AHU-03 Compressor Failure Resolution',
    severity: 'Critical',
    status: 'Resolved',
    affectedAsset: 'AHU-03',
    rootCause: 'Compressor bearing wear due to insufficient lubrication',
    resolution: 'Replaced compressor, implemented automated lubrication schedule',
    decisionMaker: 'John Smith',
    decisionDate: '2024-01-10',
    estimatedCost: 12500,
    description: 'Compressor failed during peak cooling season, causing temperature rise in server room'
  },
  {
    id: 2,
    title: 'UPS Module Redundancy Decision',
    severity: 'Major',
    status: 'In Progress',
    affectedAsset: 'UPS-01',
    rootCause: 'UPS module failed to transfer during power test',
    resolution: 'Procuring replacement module, scheduled for Q1 maintenance window',
    decisionMaker: 'Sarah Chen',
    decisionDate: '2024-01-12',
    estimatedCost: 8750,
    description: 'UPS module showed signs of capacitor degradation'
  },
  {
    id: 3,
    title: 'Cooling Tower Fan Motor Replacement',
    severity: 'Major',
    status: 'Resolved',
    affectedAsset: 'CT-02',
    rootCause: 'Motor bearing seized due to water ingress',
    resolution: 'Replaced motor, added protective cover',
    decisionMaker: 'Mike Johnson',
    decisionDate: '2024-01-08',
    estimatedCost: 5200,
    description: 'Fan motor failure caused reduced cooling capacity'
  },
  {
    id: 4,
    title: 'Chiller Efficiency Degradation',
    severity: 'Critical',
    status: 'Closed',
    affectedAsset: 'Chiller-01',
    rootCause: 'Refrigerant leak in evaporator coil',
    resolution: 'Repaired leak, recharged refrigerant, implemented leak detection system',
    decisionMaker: 'David Wang',
    decisionDate: '2023-12-28',
    estimatedCost: 23400,
    description: 'Chiller efficiency dropped by 25% over 3 months'
  },
  {
    id: 5,
    title: 'BMS Communication Interruption',
    severity: 'Warning',
    status: 'Resolved',
    affectedAsset: 'BMS Gateway',
    rootCause: 'Network switch failure',
    resolution: 'Replaced faulty switch, added redundant path',
    decisionMaker: 'Lisa Zhang',
    decisionDate: '2024-01-05',
    estimatedCost: 1850,
    description: 'BMS lost communication with 15 devices for 2 hours'
  },
  {
    id: 6,
    title: 'Fire Panel False Alarm Investigation',
    severity: 'Major',
    status: 'Open',
    affectedAsset: 'Fire Panel-01',
    rootCause: 'Under investigation - suspected dust accumulation',
    resolution: 'Awaiting root cause confirmation',
    decisionMaker: 'Robert Liu',
    decisionDate: '2024-01-14',
    estimatedCost: 0,
    description: 'Multiple false alarms triggered after maintenance work'
  },
  {
    id: 7,
    title: 'VFD Programming Error Correction',
    severity: 'Minor',
    status: 'Closed',
    affectedAsset: 'VFD-Pump-04',
    rootCause: 'Incorrect parameter configuration',
    resolution: 'Reprogrammed VFD, updated documentation',
    decisionMaker: 'Emily Zhao',
    decisionDate: '2024-01-03',
    estimatedCost: 450,
    description: 'Pump running at incorrect speed due to programming error'
  },
  {
    id: 8,
    title: 'Data Center Rack Temperature Hotspot',
    severity: 'Critical',
    status: 'In Progress',
    affectedAsset: 'Rack-A12',
    rootCause: 'Blocked airflow due to cable management',
    resolution: 'Redesigning cable layout, installing blanking panels',
    decisionMaker: 'Tom Harris',
    decisionDate: '2024-01-13',
    estimatedCost: 3200,
    description: 'Temperature reached 32°C in server inlet area'
  },
  {
    id: 9,
    title: 'Access Control Reader Malfunction',
    severity: 'Minor',
    status: 'Resolved',
    affectedAsset: 'Door-108 Reader',
    rootCause: 'Firmware corruption',
    resolution: 'Re-flashed firmware, scheduled regular updates',
    decisionMaker: 'Anna Kim',
    decisionDate: '2024-01-09',
    estimatedCost: 200,
    description: 'Card reader intermittently failing to authenticate'
  },
  {
    id: 10,
    title: 'Generator Load Bank Test Failure',
    severity: 'Major',
    status: 'Open',
    affectedAsset: 'Generator-01',
    rootCause: 'Fuel system contamination',
    resolution: 'Awaiting fuel polishing service',
    decisionMaker: 'James Wu',
    decisionDate: '2024-01-11',
    estimatedCost: 6800,
    description: 'Generator failed to reach full load during monthly test'
  }
])

// ==================== Reactive Variables ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('view')
const deleteTarget = ref<FaultDecision | null>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  keyword: '',
  severity: '',
  status: '',
  dateRange: null as [Date, Date] | null
})

const formData = reactive<FaultDecision>({
  id: 0,
  title: '',
  severity: 'Minor',
  status: 'Open',
  affectedAsset: '',
  rootCause: '',
  resolution: '',
  decisionMaker: '',
  decisionDate: new Date().toISOString().split('T')[0],
  estimatedCost: 0,
  description: ''
})

const formRules = {
  title: [{ required: true, message: 'Please enter decision title', trigger: 'blur' }],
  severity: [{ required: true, message: 'Please select severity', trigger: 'change' }],
  status: [{ required: true, message: 'Please select status', trigger: 'change' }],
  affectedAsset: [{ required: true, message: 'Please enter affected asset', trigger: 'blur' }],
  decisionMaker: [{ required: true, message: 'Please enter decision maker', trigger: 'blur' }],
  rootCause: [{ required: true, message: 'Please enter root cause', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredDecisions = computed(() => {
  let filtered = [...faultDecisions.value]

  if (filters.keyword) {
    filtered = filtered.filter(d =>
        d.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.description.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.rootCause.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.severity) {
    filtered = filtered.filter(d => d.severity === filters.severity)
  }

  if (filters.status) {
    filtered = filtered.filter(d => d.status === filters.status)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(d => {
      const date = new Date(d.decisionDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedDecisions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDecisions.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getSeverityTag = (severity: string): string => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'Major': 'warning',
    'Minor': 'info',
    'Warning': 'success'
  }
  return map[severity] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Open': 'danger',
    'In Progress': 'warning',
    'Resolved': 'success',
    'Closed': 'info'
  }
  return map[status] || 'info'
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.severity = ''
  filters.status = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredDecisions.value.length} fault decisions...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchDecisions = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleCreateDecision = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    id: Date.now(),
    title: '',
    severity: 'Minor',
    status: 'Open',
    affectedAsset: '',
    rootCause: '',
    resolution: '',
    decisionMaker: '',
    decisionDate: new Date().toISOString().split('T')[0],
    estimatedCost: 0,
    description: ''
  })
  dialogVisible.value = true
}

const viewDetail = (row: FaultDecision) => {
  dialogMode.value = 'view'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const editDecision = (row: FaultDecision) => {
  dialogMode.value = 'edit'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const deleteDecision = (row: FaultDecision) => {
  deleteTarget.value = row
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = faultDecisions.value.findIndex(d => d.id === deleteTarget.value!.id)
    if (index !== -1) {
      faultDecisions.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'create') {
        faultDecisions.value.unshift({ ...formData, id: Date.now() })
        ElMessage.success('Fault decision created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = faultDecisions.value.findIndex(d => d.id === formData.id)
        if (index !== -1) {
          faultDecisions.value[index] = { ...formData }
          ElMessage.success('Fault decision updated successfully')
        }
      }
      dialogVisible.value = false
      currentPage.value = 1
    }
  })
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
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
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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
  font-size: 28px;
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

/* ==================== Main Page Styles ==================== */
.fault-decisions-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  padding-top: 20px;
  max-height: 60vh;
  overflow-y: auto;
}
</style>