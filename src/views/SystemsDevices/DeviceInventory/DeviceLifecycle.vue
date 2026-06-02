<template>
  <!-- ==================== Loading Screen ==================== -->
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
        <div class="loading-tip">Device Lifecycle Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="device-lifecycle-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Device Inventory
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Lifecycle</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="openLifecycleDialog">
          Add Lifecycle Record
        </el-button>
      </div>
    </div>

    <!-- 生命周期统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Monitor /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalDevices }}</span>
          <span class="stat-label">Total Devices</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><SuccessFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.activeDevices }}</span>
          <span class="stat-label">Active</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.warningDevices }}</span>
          <span class="stat-label">End of Life Warning</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><CircleCloseFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.retiredDevices }}</span>
          <span class="stat-label">Retired</span>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-bar">
      <el-input
          v-model="searchKeyword"
          placeholder="Search by device name, model, or serial"
          clearable
          :prefix-icon="Search"
          style="width: 280px"
          @clear="loadLifecycleData"
          @keyup.enter="loadLifecycleData"
      />
      <el-select v-model="filterStatus" placeholder="Lifecycle Status" clearable style="width: 160px" @change="loadLifecycleData">
        <el-option label="All Status" value="" />
        <el-option label="Active" value="active" />
        <el-option label="Maintenance" value="maintenance" />
        <el-option label="End of Life" value="eol" />
        <el-option label="Retired" value="retired" />
      </el-select>
      <el-date-picker
          v-model="filterDateRange"
          type="daterange"
          range-separator="-"
          start-placeholder="Purchase Start"
          end-placeholder="Purchase End"
          style="width: 280px"
          @change="loadLifecycleData"
      />
      <el-button type="primary" :icon="Refresh" @click="resetFilters">Reset</el-button>
      <el-button :icon="Download" @click="exportData">Export</el-button>
    </div>

    <!-- 设备生命周期表格 -->
    <div class="lifecycle-table-container">
      <el-table :data="lifecycleData" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column label="Device" min-width="200">
          <template #default="{ row }">
            <div class="device-cell">
              <el-avatar :src="row.imageUrl" :size="36" shape="square" fit="cover">
                <template #error><el-icon><Cpu /></el-icon></template>
              </el-avatar>
              <div class="device-info">
                <span class="device-name">{{ row.name }}</span>
                <span class="device-model">{{ row.model }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="serialNumber" label="Serial Number" width="160" />
        <el-table-column label="Lifecycle Status" width="140">
          <template #default="{ row }">
            <el-tag :type="getLifecycleTagType(row.lifecycleStatus)" size="small">
              {{ getLifecycleLabel(row.lifecycleStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="purchaseDate" label="Purchase Date" width="120">
          <template #default="{ row }">{{ formatDate(row.purchaseDate) }}</template>
        </el-table-column>
        <el-table-column prop="installationDate" label="Installation Date" width="120">
          <template #default="{ row }">{{ formatDate(row.installationDate) }}</template>
        </el-table-column>
        <el-table-column prop="warrantyEnd" label="Warranty End" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-warning': isWarrantyExpiring(row.warrantyEnd), 'text-danger': isExpired(row.warrantyEnd) }">
              {{ formatDate(row.warrantyEnd) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Expected Life" width="120">
          <template #default="{ row }">{{ row.expectedLife }} years</template>
        </el-table-column>
        <el-table-column label="Remaining Life" width="120">
          <template #default="{ row }">
            <el-progress :percentage="getRemainingLifePercent(row)" :stroke-width="8" :show-text="false" :color="getLifeProgressColor(row)" style="width: 80px" />
            <span :class="getRemainingLifeClass(row)">{{ getRemainingLife(row) }} years</span>
          </template>
        </el-table-column>
        <el-table-column label="Health Score" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.healthScore" :stroke-width="8" :color="getHealthColor(row.healthScore)" />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click="viewTimeline(row)">Timeline</el-button>
            <el-button size="small" text type="primary" @click="editLifecycle(row)">Edit</el-button>
            <el-dropdown trigger="click">
              <el-button size="small" text><el-icon><MoreFilled /></el-icon></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="updateStatus(row, 'maintenance')">Set Maintenance</el-dropdown-item>
                  <el-dropdown-item @click="updateStatus(row, 'eol')">Mark End of Life</el-dropdown-item>
                  <el-dropdown-item divided @click="retireDevice(row)">Retire Device</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="loadLifecycleData"
            @current-change="loadLifecycleData"
        />
      </div>
    </div>

    <!-- 生命周期时间线对话框 -->
    <el-dialog v-model="timelineDialogVisible" :title="`Lifecycle Timeline - ${selectedDevice?.name}`" width="700px">
      <div class="timeline-container">
        <el-timeline>
          <el-timeline-item
              v-for="event in deviceTimeline"
              :key="event.id"
              :timestamp="formatDateTime(event.date)"
              :type="event.type"
              placement="top"
          >
            <div class="timeline-event">
              <h4>{{ event.title }}</h4>
              <p>{{ event.description }}</p>
              <div class="event-meta">
                <span class="event-user">By: {{ event.user }}</span>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>

    <!-- 编辑生命周期对话框 -->
    <el-dialog v-model="lifecycleDialogVisible" :title="editingLifecycle ? 'Edit Lifecycle Record' : 'Add Lifecycle Record'" width="550px">
      <el-form :model="lifecycleForm" :rules="lifecycleRules" ref="lifecycleFormRef" label-width="130px">
        <el-form-item label="Device" prop="deviceId" required>
          <el-select v-model="lifecycleForm.deviceId" placeholder="Select device" filterable style="width: 100%">
            <el-option
                v-for="device in deviceOptions"
                :key="device.id"
                :label="`${device.name} (${device.model})`"
                :value="device.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Lifecycle Status" prop="lifecycleStatus">
          <el-select v-model="lifecycleForm.lifecycleStatus" placeholder="Select status" style="width: 100%">
            <el-option label="Active" value="active" />
            <el-option label="Maintenance" value="maintenance" />
            <el-option label="End of Life" value="eol" />
            <el-option label="Retired" value="retired" />
          </el-select>
        </el-form-item>
        <el-form-item label="Purchase Date" prop="purchaseDate">
          <el-date-picker v-model="lifecycleForm.purchaseDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Installation Date" prop="installationDate">
          <el-date-picker v-model="lifecycleForm.installationDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Warranty End Date" prop="warrantyEnd">
          <el-date-picker v-model="lifecycleForm.warrantyEnd" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Expected Life (years)" prop="expectedLife">
          <el-input-number v-model="lifecycleForm.expectedLife" :min="1" :max="30" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Purchase Cost ($)" prop="purchaseCost">
          <el-input-number v-model="lifecycleForm.purchaseCost" :min="0" :step="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Supplier" prop="supplier">
          <el-input v-model="lifecycleForm.supplier" placeholder="Supplier name" />
        </el-form-item>
        <el-form-item label="Notes" prop="notes">
          <el-input v-model="lifecycleForm.notes" type="textarea" :rows="3" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="lifecycleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveLifecycleRecord" :loading="saving">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus, Search, Refresh, Download, MoreFilled, Monitor,
  SuccessFilled, WarningFilled, CircleCloseFilled, Cpu
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading lifecycle data...')
const router = useRouter()
const loadingMessages = ['Initializing...', 'Loading device data...', 'Loading lifecycle records...', 'Almost ready...']

// ==================== State ====================
const searchKeyword = ref('')
const filterStatus = ref('')
const filterDateRange = ref<[Date, Date] | null>(null)
const tableLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalRecords = ref(0)
const timelineDialogVisible = ref(false)
const lifecycleDialogVisible = ref(false)
const editingLifecycle = ref<any>(null)
const saving = ref(false)
const lifecycleFormRef = ref<FormInstance>()
const selectedDevice = ref<any>(null)
const deviceTimeline = ref<any[]>([])

// ==================== Data ====================
interface LifecycleRecord {
  id: string
  deviceId: string
  name: string
  model: string
  serialNumber: string
  imageUrl: string
  lifecycleStatus: 'active' | 'maintenance' | 'eol' | 'retired'
  purchaseDate: string
  installationDate: string
  warrantyEnd: string
  expectedLife: number
  remainingLife: number
  healthScore: number
  purchaseCost: number
  supplier: string
  notes: string
}

const lifecycleData = ref<LifecycleRecord[]>([])
const deviceOptions = ref<any[]>([])

// 统计数据
const stats = computed(() => {
  return {
    totalDevices: lifecycleData.value.length,
    activeDevices: lifecycleData.value.filter(d => d.lifecycleStatus === 'active').length,
    warningDevices: lifecycleData.value.filter(d => d.lifecycleStatus === 'eol' || d.healthScore < 60).length,
    retiredDevices: lifecycleData.value.filter(d => d.lifecycleStatus === 'retired').length
  }
})

// 表单数据
const lifecycleForm = ref({
  deviceId: '',
  lifecycleStatus: 'active',
  purchaseDate: new Date(),
  installationDate: new Date(),
  warrantyEnd: new Date(Date.now() + 365 * 24 * 3600000),
  expectedLife: 10,
  purchaseCost: 0,
  supplier: '',
  notes: ''
})

const lifecycleRules: FormRules = {
  deviceId: [{ required: true, message: 'Please select a device', trigger: 'change' }],
  lifecycleStatus: [{ required: true, message: 'Please select lifecycle status', trigger: 'change' }]
}

// ==================== Helper Functions ====================
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const getLifecycleLabel = (status: string) => {
  const labels: Record<string, string> = {
    active: 'Active', maintenance: 'Maintenance', eol: 'End of Life', retired: 'Retired'
  }
  return labels[status] || status
}

const getLifecycleTagType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success', maintenance: 'warning', eol: 'danger', retired: 'info'
  }
  return types[status] || 'info'
}

const isExpired = (dateStr: string) => {
  return new Date(dateStr) < new Date()
}

const isWarrantyExpiring = (dateStr: string) => {
  const daysLeft = (new Date(dateStr).getTime() - new Date().getTime()) / (1000 * 3600 * 24)
  return daysLeft <= 90 && daysLeft > 0
}

const getRemainingLife = (record: LifecycleRecord) => {
  const installDate = new Date(record.installationDate)
  const yearsSinceInstall = (new Date().getTime() - installDate.getTime()) / (1000 * 3600 * 24 * 365)
  const remaining = Math.max(0, record.expectedLife - yearsSinceInstall)
  return Math.round(remaining * 10) / 10
}

const getRemainingLifePercent = (record: LifecycleRecord) => {
  const remaining = getRemainingLife(record)
  return Math.min(100, (remaining / record.expectedLife) * 100)
}

const getRemainingLifeClass = (record: LifecycleRecord) => {
  const remaining = getRemainingLife(record)
  if (remaining <= 1) return 'text-danger'
  if (remaining <= 3) return 'text-warning'
  return ''
}

const getHealthColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getLifeProgressColor = (record: LifecycleRecord) => {
  const percent = getRemainingLifePercent(record)
  if (percent >= 70) return '#67c23a'
  if (percent >= 30) return '#e6a23c'
  return '#f56c6c'
}

// ==================== Load Data ====================
const loadLifecycleData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))

  // Mock data
  const mockData: LifecycleRecord[] = [
    {
      id: '1', deviceId: 'dev-ahu-b2-01', name: 'AHU-B2-01 Air Handler', model: 'Carrier 39G',
      serialNumber: 'CA-2024-B201', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',
      lifecycleStatus: 'active', purchaseDate: '2023-12-15', installationDate: '2024-01-10',
      warrantyEnd: '2026-12-15', expectedLife: 15, remainingLife: 13.5, healthScore: 94,
      purchaseCost: 25000, supplier: 'Carrier Corp', notes: 'Main HVAC unit for B2'
    },
    {
      id: '2', deviceId: 'dev-fcu-b2-01', name: 'FCU-B2-01 Fan Coil', model: 'Daikin FXMQ',
      serialNumber: 'DK-2024-B201', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',
      lifecycleStatus: 'active', purchaseDate: '2024-01-20', installationDate: '2024-02-15',
      warrantyEnd: '2027-01-20', expectedLife: 12, remainingLife: 10.8, healthScore: 91,
      purchaseCost: 3500, supplier: 'Daikin', notes: 'Fan coil unit for B2 offices'
    },
    {
      id: '3', deviceId: 'dev-chiller-b2-01', name: 'CH-B2-01 Chiller', model: 'Carrier AquaEdge',
      serialNumber: 'CA-2024-B202', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',
      lifecycleStatus: 'maintenance', purchaseDate: '2023-10-05', installationDate: '2023-11-20',
      warrantyEnd: '2025-10-05', expectedLife: 20, remainingLife: 17.8, healthScore: 72,
      purchaseCost: 85000, supplier: 'Carrier Corp', notes: 'Central chiller for B2'
    },
    {
      id: '4', deviceId: 'dev-exhaust-b2-02', name: 'EF-B2-02 Exhaust Fan', model: 'Greenheck CUBE',
      serialNumber: 'GH-2024-B202', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',
      lifecycleStatus: 'eol', purchaseDate: '2018-03-10', installationDate: '2018-04-01',
      warrantyEnd: '2021-03-10', expectedLife: 8, remainingLife: 0.2, healthScore: 45,
      purchaseCost: 2800, supplier: 'Greenheck', notes: 'Near end of life, replacement recommended'
    },
    {
      id: '5', deviceId: 'dev-ahu-2f-01', name: 'AHU-2F-01 Air Handler', model: 'Trane IntelliPak',
      serialNumber: 'TR-2024-2F01', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',
      lifecycleStatus: 'eol', purchaseDate: '2016-06-15', installationDate: '2016-07-20',
      warrantyEnd: '2019-06-15', expectedLife: 10, remainingLife: 0, healthScore: 38,
      purchaseCost: 32000, supplier: 'Trane', notes: 'End of life, requires replacement'
    },
    {
      id: '6', deviceId: 'dev-light-b2-01', name: 'LIGHT-B2-01 Controller', model: 'Philips Dynalite',
      serialNumber: 'PH-2024-B201', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',
      lifecycleStatus: 'active', purchaseDate: '2024-01-10', installationDate: '2024-01-20',
      warrantyEnd: '2027-01-10', expectedLife: 10, remainingLife: 8.9, healthScore: 96,
      purchaseCost: 1200, supplier: 'Philips', notes: 'Lighting control system'
    },
    {
      id: '7', deviceId: 'dev-pump-b2-02', name: 'PUMP-B2-02 Booster', model: 'Grundfos CR',
      serialNumber: 'GF-2024-B202', imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',
      lifecycleStatus: 'retired', purchaseDate: '2015-11-20', installationDate: '2015-12-05',
      warrantyEnd: '2018-11-20', expectedLife: 8, remainingLife: 0, healthScore: 25,
      purchaseCost: 4500, supplier: 'Grundfos', notes: 'Retired and replaced'
    }
  ]

  // Apply filters
  let filtered = [...mockData]
  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(d => d.name.toLowerCase().includes(kw) || d.model.toLowerCase().includes(kw) || d.serialNumber.toLowerCase().includes(kw))
  }
  if (filterStatus.value) {
    filtered = filtered.filter(d => d.lifecycleStatus === filterStatus.value)
  }
  if (filterDateRange.value && filterDateRange.value.length === 2) {
    const [start, end] = filterDateRange.value
    filtered = filtered.filter(d => {
      const purchaseDate = new Date(d.purchaseDate)
      return purchaseDate >= start && purchaseDate <= end
    })
  }

  totalRecords.value = filtered.length
  const start = (currentPage.value - 1) * pageSize.value
  lifecycleData.value = filtered.slice(start, start + pageSize.value)

  // Update device options
  deviceOptions.value = lifecycleData.value.map(d => ({ id: d.deviceId, name: d.name, model: d.model }))

  tableLoading.value = false
}

const resetFilters = () => {
  searchKeyword.value = ''
  filterStatus.value = ''
  filterDateRange.value = null
  currentPage.value = 1
  loadLifecycleData()
}

const exportData = () => {
  ElMessage.success('Exporting lifecycle data to CSV')
}

// ==================== Lifecycle Actions ====================
const viewTimeline = async (record: LifecycleRecord) => {
  selectedDevice.value = record
  await new Promise(resolve => setTimeout(resolve, 300))

  // Mock timeline data
  deviceTimeline.value = [
    { id: '1', date: record.purchaseDate, type: 'primary', title: 'Device Purchased', description: `Purchased from ${record.supplier} for $${record.purchaseCost.toLocaleString()}`, user: 'Procurement Team' },
    { id: '2', date: record.installationDate, type: 'success', title: 'Device Installed', description: `Installed at ${record.name} location`, user: 'Installation Team' },
    { id: '3', date: new Date(record.installationDate).toISOString().split('T')[0], type: 'info', title: 'Warranty Start', description: `Warranty period started, expires on ${formatDate(record.warrantyEnd)}`, user: 'System' },
    { id: '4', date: new Date(Date.now() - 180 * 24 * 3600000).toISOString().split('T')[0], type: 'warning', title: 'Maintenance Performed', description: 'Quarterly inspection and filter replacement', user: 'Maintenance Team' },
    { id: '5', date: new Date().toISOString().split('T')[0], type: 'info', title: 'Health Check', description: `Current health score: ${record.healthScore}%`, user: 'System' }
  ]

  timelineDialogVisible.value = true
}

const editLifecycle = (record: LifecycleRecord) => {
  editingLifecycle.value = record
  lifecycleForm.value = {
    deviceId: record.deviceId,
    lifecycleStatus: record.lifecycleStatus,
    purchaseDate: new Date(record.purchaseDate),
    installationDate: new Date(record.installationDate),
    warrantyEnd: new Date(record.warrantyEnd),
    expectedLife: record.expectedLife,
    purchaseCost: record.purchaseCost,
    supplier: record.supplier,
    notes: record.notes
  }
  lifecycleDialogVisible.value = true
}

const openLifecycleDialog = () => {
  editingLifecycle.value = null
  lifecycleForm.value = {
    deviceId: '',
    lifecycleStatus: 'active',
    purchaseDate: new Date(),
    installationDate: new Date(),
    warrantyEnd: new Date(Date.now() + 365 * 24 * 3600000),
    expectedLife: 10,
    purchaseCost: 0,
    supplier: '',
    notes: ''
  }
  lifecycleDialogVisible.value = true
}

const saveLifecycleRecord = async () => {
  if (!lifecycleFormRef.value) return
  await lifecycleFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      await new Promise(resolve => setTimeout(resolve, 1000))

      if (editingLifecycle.value) {
        ElMessage.success('Lifecycle record updated successfully')
      } else {
        ElMessage.success('Lifecycle record added successfully')
      }

      lifecycleDialogVisible.value = false
      saving.value = false
      loadLifecycleData()
    }
  })
}

const updateStatus = async (record: LifecycleRecord, newStatus: string) => {
  const statusLabels: Record<string, string> = {
    maintenance: 'Maintenance Mode',
    eol: 'End of Life'
  }

  await ElMessageBox.confirm(
      `Are you sure you want to set "${record.name}" to ${statusLabels[newStatus]}?`,
      'Confirm Status Change',
      { confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', type: 'warning' }
  )

  await new Promise(resolve => setTimeout(resolve, 500))
  ElMessage.success(`Device status updated to ${statusLabels[newStatus]}`)
  loadLifecycleData()
}

const retireDevice = async (record: LifecycleRecord) => {
  await ElMessageBox.confirm(
      `Are you sure you want to retire "${record.name}"? This action cannot be undone.`,
      'Confirm Retirement',
      { confirmButtonText: 'Retire', cancelButtonText: 'Cancel', type: 'warning' }
  )

  await new Promise(resolve => setTimeout(resolve, 500))
  ElMessage.success(`Device "${record.name}" has been retired`)
  loadLifecycleData()
}

// ==================== Lifecycle ====================
onMounted(() => {
  let msgIdx = 0
  const msgInt = setInterval(() => {
    if (msgIdx < loadingMessages.length - 1) {
      msgIdx++
      loadingMessage.value = loadingMessages[msgIdx]
    }
  }, 400)

  const progInt = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(msgInt)
    clearInterval(progInt)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      loadLifecycleData()
    }, 400)
  }, 2000)
})
</script>

<style scoped>
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
.loading-overlay { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: fadeInUp 0.6s ease-out; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.device-lifecycle-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat-icon .el-icon { font-size: 36px; color: #3b82f6; }
.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }

.filter-bar { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; background: white; padding: 16px 20px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }

.lifecycle-table-container { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.device-cell { display: flex; align-items: center; gap: 12px; }
.device-info { display: flex; flex-direction: column; }
.device-name { font-weight: 600; color: #1e293b; }
.device-model { font-size: 11px; color: #64748b; }

.text-warning { color: #e6a23c; }
.text-danger { color: #f56c6c; }

.pagination-wrapper { display: flex; justify-content: flex-end; padding: 16px 20px; border-top: 1px solid #e4e7ed; }

.timeline-container { max-height: 500px; overflow-y: auto; padding: 8px; }
.timeline-event h4 { margin: 0 0 8px 0; font-size: 14px; font-weight: 600; }
.timeline-event p { margin: 0 0 8px 0; font-size: 13px; color: #64748b; }
.event-meta { font-size: 11px; color: #94a3b8; }

@media (max-width: 1024px) { .stats-cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .stats-cards { grid-template-columns: 1fr; } .filter-bar { flex-direction: column; } .filter-bar .el-input, .filter-bar .el-select, .filter-bar .el-date-editor { width: 100% !important; } }
</style>