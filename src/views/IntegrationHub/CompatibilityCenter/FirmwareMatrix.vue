<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, Upload, Download, Filter, Cpu, Link, Check, Close, QuestionFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing firmware database...',
  'Loading device compatibility matrix...',
  'Checking firmware versions...',
  'Analyzing compatibility...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedVendor = ref('all')
const selectedStatus = ref('all')
const uploadVisible = ref(false)
const detailsVisible = ref(false)
const compareVisible = ref(false)
const chartRef = ref(null)

let firmwareChart: echarts.ECharts | null = null

// Vendors
const vendors = [
  { value: 'all', label: 'All Vendors' },
  { value: 'siemens', label: 'Siemens' },
  { value: 'schneider', label: 'Schneider Electric' },
  { value: 'honeywell', label: 'Honeywell' },
  { value: 'johnson', label: 'Johnson Controls' },
  { value: 'abb', label: 'ABB' },
  { value: 'hikvision', label: 'Hikvision' },
  { value: 'dahua', label: 'Dahua' }
]

// Firmware matrix data
const firmwareEntries = ref([
  {
    id: 'FM001', deviceType: 'BACnet Controller', vendor: 'siemens', model: 'PXC4.ED16',
    currentFirmware: '4.2.1', recommendedFirmware: '4.2.1', latestFirmware: '4.3.0',
    status: 'up_to_date', releaseDate: '2024-01-10', compatibility: 'full',
    notes: 'Latest version tested and verified', devicesCount: 12
  },
  {
    id: 'FM002', deviceType: 'BACnet Router', vendor: 'siemens', model: 'PXC4.R16',
    currentFirmware: '3.8.0', recommendedFirmware: '4.0.0', latestFirmware: '4.1.0',
    status: 'update_available', releaseDate: '2023-12-15', compatibility: 'full',
    notes: 'Security improvements and bug fixes', devicesCount: 5
  },
  {
    id: 'FM003', deviceType: 'Modbus Gateway', vendor: 'schneider', model: 'EGX100',
    currentFirmware: '2.1.0', recommendedFirmware: '2.2.0', latestFirmware: '2.2.0',
    status: 'update_available', releaseDate: '2024-01-05', compatibility: 'full',
    notes: 'Improved Modbus TCP performance', devicesCount: 8
  },
  {
    id: 'FM004', deviceType: 'Power Meter', vendor: 'schneider', model: 'PM8000',
    currentFirmware: '3.0.0', recommendedFirmware: '3.1.0', latestFirmware: '3.2.0',
    status: 'update_available', releaseDate: '2024-01-20', compatibility: 'partial',
    notes: 'Requires configuration backup before update', devicesCount: 15
  },
  {
    id: 'FM005', deviceType: 'AHU Controller', vendor: 'honeywell', model: 'W7750',
    currentFirmware: '5.1.2', recommendedFirmware: '5.1.2', latestFirmware: '5.2.0',
    status: 'up_to_date', releaseDate: '2023-12-01', compatibility: 'full',
    notes: 'Stable version recommended', devicesCount: 20
  },
  {
    id: 'FM006', deviceType: 'VAV Controller', vendor: 'honeywell', model: 'W7751',
    currentFirmware: '4.5.0', recommendedFirmware: '4.6.0', latestFirmware: '4.6.0',
    status: 'update_available', releaseDate: '2024-01-18', compatibility: 'full',
    notes: 'Energy savings improvements', devicesCount: 35
  },
  {
    id: 'FM007', deviceType: 'NVR', vendor: 'hikvision', model: 'DS-9632NI-I8',
    currentFirmware: '4.30.005', recommendedFirmware: '4.40.000', latestFirmware: '4.50.000',
    status: 'update_available', releaseDate: '2024-01-25', compatibility: 'full',
    notes: 'New AI features added', devicesCount: 3
  },
  {
    id: 'FM008', deviceType: 'IP Camera', vendor: 'hikvision', model: 'DS-2CD2345',
    currentFirmware: '5.5.0', recommendedFirmware: '5.5.0', latestFirmware: '5.6.0',
    status: 'up_to_date', releaseDate: '2023-12-10', compatibility: 'full',
    notes: 'Stable version', devicesCount: 45
  },
  {
    id: 'FM009', deviceType: 'IP Camera', vendor: 'dahua', model: 'IPC-HFW5442',
    currentFirmware: '2.800.0000', recommendedFirmware: '2.800.0000', latestFirmware: '2.810.0000',
    status: 'up_to_date', releaseDate: '2024-01-08', compatibility: 'full',
    notes: 'Recommended for production', devicesCount: 28
  },
  {
    id: 'FM010', deviceType: 'NVR', vendor: 'dahua', model: 'NVR5216-4KS2',
    currentFirmware: '4.000.0000', recommendedFirmware: '4.001.0000', latestFirmware: '4.002.0000',
    status: 'update_available', releaseDate: '2024-01-22', compatibility: 'partial',
    notes: 'Test before production deployment', devicesCount: 2
  },
  {
    id: 'FM011', deviceType: 'PLC Controller', vendor: 'abb', model: 'AC500',
    currentFirmware: '2.5.0', recommendedFirmware: '2.6.0', latestFirmware: '2.7.0',
    status: 'update_available', releaseDate: '2024-01-15', compatibility: 'full',
    notes: 'Critical security patch included', devicesCount: 7
  },
  {
    id: 'FM012', deviceType: 'DDC Controller', vendor: 'johnson', model: 'FX80',
    currentFirmware: '10.0.0', recommendedFirmware: '10.1.0', latestFirmware: '10.1.0',
    status: 'update_available', releaseDate: '2024-01-12', compatibility: 'full',
    notes: 'Improved BACnet performance', devicesCount: 10
  }
])

// Compatibility statistics
const compatibilityStats = reactive({
  total: 0,
  upToDate: 0,
  updateAvailable: 0,
  critical: 0,
  deprecated: 0,
  byVendor: {} as Record<string, number>,
  avgCompatibility: 0
})

// Selected devices for comparison
const compareDevices = ref<any[]>([])

// Firmware upload form
const uploadForm = reactive({
  vendor: '',
  deviceType: '',
  model: '',
  firmwareVersion: '',
  releaseNotes: '',
  file: null
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: firmwareEntries.value.length
})

// Filtered firmware entries
const filteredEntries = computed(() => {
  let filtered = firmwareEntries.value
  if (searchKeyword.value) {
    filtered = filtered.filter(f =>
        f.deviceType.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        f.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        f.model.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        f.vendor.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedVendor.value !== 'all') {
    filtered = filtered.filter(f => f.vendor === selectedVendor.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(f => f.status === selectedStatus.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
        initChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  firmwareChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const vendorStats = vendors.filter(v => v.value !== 'all').map(vendor => {
    const entries = firmwareEntries.value.filter(f => f.vendor === vendor.value)
    const upToDate = entries.filter(e => e.status === 'up_to_date').length
    const updateAvailable = entries.filter(e => e.status === 'update_available').length
    return { vendor: vendor.label, upToDate, updateAvailable }
  })

  firmwareChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Up to Date', 'Update Available'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: vendorStats.map(v => v.vendor) },
    yAxis: { type: 'value', name: 'Number of Device Types' },
    series: [
      { name: 'Up to Date', type: 'bar', data: vendorStats.map(v => v.upToDate), itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Update Available', type: 'bar', data: vendorStats.map(v => v.updateAvailable), itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  compatibilityStats.total = firmwareEntries.value.length
  compatibilityStats.upToDate = firmwareEntries.value.filter(f => f.status === 'up_to_date').length
  compatibilityStats.updateAvailable = firmwareEntries.value.filter(f => f.status === 'update_available').length
  compatibilityStats.critical = firmwareEntries.value.filter(f => f.status === 'critical').length
  compatibilityStats.deprecated = firmwareEntries.value.filter(f => f.status === 'deprecated').length

  vendors.forEach(vendor => {
    if (vendor.value !== 'all') {
      const count = firmwareEntries.value.filter(f => f.vendor === vendor.value).length
      compatibilityStats.byVendor[vendor.value] = count
    }
  })

  const compatibilitySum = firmwareEntries.value.reduce((sum, f) => {
    return sum + (f.compatibility === 'full' ? 100 : f.compatibility === 'partial' ? 70 : 40)
  }, 0)
  compatibilityStats.avgCompatibility = Math.round(compatibilitySum / firmwareEntries.value.length)
}

const handleResize = () => {
  firmwareChart?.resize()
}

// ==================== Firmware Functions ====================
const checkUpdates = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  // Simulate checking for updates
  firmwareEntries.value.forEach(entry => {
    const shouldUpdate = Math.random() > 0.7
    if (shouldUpdate && entry.status === 'up_to_date') {
      entry.status = 'update_available'
    }
  })

  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success('Firmware updates checked successfully')
}

const updateFirmware = async (entry: any) => {
  await ElMessageBox.confirm(
      `Update firmware for ${entry.deviceType} (${entry.model}) from ${entry.currentFirmware} to ${entry.recommendedFirmware}?`,
      'Confirm Update',
      {
        confirmButtonText: 'Update',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 3000))

  entry.currentFirmware = entry.recommendedFirmware
  entry.status = entry.recommendedFirmware === entry.latestFirmware ? 'up_to_date' : 'update_available'
  entry.lastUpdated = new Date().toLocaleString()

  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success(`${entry.deviceType} firmware updated successfully`)
}

const bulkUpdate = async () => {
  const devicesToUpdate = firmwareEntries.value.filter(f => f.status === 'update_available')
  if (devicesToUpdate.length === 0) {
    ElMessage.warning('No firmware updates available')
    return
  }

  await ElMessageBox.confirm(
      `Update firmware for ${devicesToUpdate.length} device types?`,
      'Confirm Bulk Update',
      {
        confirmButtonText: 'Update All',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 5000))

  devicesToUpdate.forEach(entry => {
    entry.currentFirmware = entry.recommendedFirmware
    entry.status = entry.recommendedFirmware === entry.latestFirmware ? 'up_to_date' : 'update_available'
  })

  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success(`Updated ${devicesToUpdate.length} device types successfully`)
}

const viewDetails = (entry: any) => {
  selectedEntry.value = entry
  detailsVisible.value = true
}

const compareFirmware = () => {
  if (compareDevices.value.length < 2) {
    ElMessage.warning('Please select at least 2 devices to compare')
    return
  }
  compareVisible.value = true
}

const toggleCompare = (entry: any) => {
  const index = compareDevices.value.findIndex(d => d.id === entry.id)
  if (index === -1) {
    if (compareDevices.value.length >= 4) {
      ElMessage.warning('Maximum 4 devices can be compared')
      return
    }
    compareDevices.value.push(entry)
  } else {
    compareDevices.value.splice(index, 1)
  }
}

const exportMatrix = () => {
  const data = firmwareEntries.value.map(f => ({
    ID: f.id,
    DeviceType: f.deviceType,
    Vendor: f.vendor,
    Model: f.model,
    CurrentFirmware: f.currentFirmware,
    RecommendedFirmware: f.recommendedFirmware,
    LatestFirmware: f.latestFirmware,
    Status: f.status,
    ReleaseDate: f.releaseDate,
    Compatibility: f.compatibility,
    DevicesCount: f.devicesCount
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `firmware_matrix_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Firmware matrix exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
}

const uploadFirmware = () => {
  uploadVisible.value = true
}

const saveUpload = async () => {
  if (!uploadForm.vendor || !uploadForm.deviceType || !uploadForm.model || !uploadForm.firmwareVersion) {
    ElMessage.warning('Please fill in all required fields')
    return
  }

  const newEntry = {
    id: `FM${String(firmwareEntries.value.length + 1).padStart(3, '0')}`,
    deviceType: uploadForm.deviceType,
    vendor: uploadForm.vendor,
    model: uploadForm.model,
    currentFirmware: uploadForm.firmwareVersion,
    recommendedFirmware: uploadForm.firmwareVersion,
    latestFirmware: uploadForm.firmwareVersion,
    status: 'up_to_date',
    releaseDate: new Date().toISOString().slice(0, 10),
    compatibility: 'pending',
    notes: uploadForm.releaseNotes || 'New firmware added',
    devicesCount: 0
  }

  firmwareEntries.value.push(newEntry)
  updateStats()
  updateChart()
  uploadVisible.value = false
  uploadForm.vendor = ''
  uploadForm.deviceType = ''
  uploadForm.model = ''
  uploadForm.firmwareVersion = ''
  uploadForm.releaseNotes = ''
  ElMessage.success('Firmware entry added successfully')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'up_to_date': return 'success'
    case 'update_available': return 'warning'
    case 'critical': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'up_to_date': return 'Up to Date'
    case 'update_available': return 'Update Available'
    case 'critical': return 'Critical'
    default: return 'Deprecated'
  }
}

const getCompatibilityType = (compatibility: string) => {
  switch (compatibility) {
    case 'full': return 'success'
    case 'partial': return 'warning'
    default: return 'danger'
  }
}

const getCompatibilityText = (compatibility: string) => {
  switch (compatibility) {
    case 'full': return 'Full'
    case 'partial': return 'Partial'
    default: return 'None'
  }
}

const selectedEntry = ref<any>(null)
</script>

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
          <span class="loading-title">Loading Firmware Matrix</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Compatibility Center - Firmware Matrix</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="firmware-matrix-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Firmware Matrix</h2>
        <el-tag type="warning" effect="dark">Compatibility Center</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">Version Compatibility | Update Management</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedVendor" placeholder="Vendor" style="width: 100%" @change="updateChart">
            <el-option v-for="v in vendors" :key="v.value" :label="v.label" :value="v.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 100%">
            <el-option label="All" value="all" />
            <el-option label="Up to Date" value="up_to_date" />
            <el-option label="Update Available" value="update_available" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search by device, model, or vendor..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="checkUpdates" :loading="loading">
              <el-icon><Refresh /></el-icon> Check Updates
            </el-button>
            <el-button @click="bulkUpdate">
              <el-icon><Upload /></el-icon> Bulk Update
            </el-button>
            <el-button @click="uploadFirmware">
              <el-icon><Document /></el-icon> Add Firmware
            </el-button>
          </div>
        </el-col>
      </el-row>

      <!-- Quick Actions -->
      <el-row :gutter="10" class="action-buttons" style="margin-top: 15px">
        <el-col :span="4">
          <el-button size="small" @click="exportMatrix">
            <el-icon><Download /></el-icon> Export Matrix
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button size="small" @click="compareFirmware" :disabled="compareDevices.length < 2">
            <el-icon><Link /></el-icon> Compare ({{ compareDevices.length }})
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button size="small" @click="compareDevices = []">
            <el-icon><Close /></el-icon> Clear Selection
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon total-icon">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ compatibilityStats.total }}</div>
            <div class="stat-label">Device Types</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon up-to-date-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ compatibilityStats.upToDate }}</div>
            <div class="stat-label">Up to Date</div>
            <el-progress :percentage="(compatibilityStats.upToDate / compatibilityStats.total) * 100" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon update-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ compatibilityStats.updateAvailable }}</div>
            <div class="stat-label">Updates Available</div>
            <div class="stat-sub-value">Ready to update</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon compatibility-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ compatibilityStats.avgCompatibility }}%</div>
            <div class="stat-label">Avg Compatibility</div>
            <el-progress :percentage="compatibilityStats.avgCompatibility" :color="compatibilityStats.avgCompatibility > 80 ? '#67C23A' : '#E6A23C'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Firmware Chart -->
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <span>Firmware Status by Vendor</span>
          <el-button text type="primary" @click="updateChart">Refresh Chart</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart" style="height: 320px"></div>
    </el-card>

    <!-- Firmware Matrix Table -->
    <el-card shadow="never" class="matrix-card">
      <template #header>
        <div class="table-header">
          <span>Firmware Compatibility Matrix</span>
          <div class="table-actions">
            <el-checkbox
                :model-value="compareDevices.length === filteredEntries.length && filteredEntries.length > 0"
                :indeterminate="compareDevices.length > 0 && compareDevices.length < filteredEntries.length"
                @change="(val) => compareDevices = val ? [...filteredEntries] : []"
            >
              Select All
            </el-checkbox>
          </div>
        </div>
      </template>

      <el-table :data="filteredEntries" stripe style="width: 100%">
        <el-table-column type="selection" width="55" :selectable="() => true" @selection-change="(val) => compareDevices = val" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="deviceType" label="Device Type" min-width="160" />
        <el-table-column prop="vendor" label="Vendor" width="130">
          <template #default="{ row }">
            <el-tag size="small">{{ row.vendor.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="Model" width="140" />
        <el-table-column label="Current FW" width="110" align="center">
          <template #default="{ row }">
            <span class="fw-version">{{ row.currentFirmware }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Recommended" width="110" align="center">
          <template #default="{ row }">
            <span v-if="row.recommendedFirmware !== row.currentFirmware" class="recommended-fw">
              {{ row.recommendedFirmware }}
            </span>
            <span v-else class="current-fw">{{ row.recommendedFirmware }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Latest" width="100" align="center">
          <template #default="{ row }">
            {{ row.latestFirmware }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Compatibility" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getCompatibilityType(row.compatibility)" size="small">
              {{ getCompatibilityText(row.compatibility) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="devicesCount" label="Devices" width="80" align="center" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button
                v-if="row.status === 'update_available'"
                link type="warning"
                size="small"
                @click="updateFirmware(row)"
            >
              Update
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Device Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Firmware Details - ${selectedEntry?.deviceType}`" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Device ID">{{ selectedEntry?.id }}</el-descriptions-item>
        <el-descriptions-item label="Device Type">{{ selectedEntry?.deviceType }}</el-descriptions-item>
        <el-descriptions-item label="Vendor">{{ selectedEntry?.vendor?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Model">{{ selectedEntry?.model }}</el-descriptions-item>
        <el-descriptions-item label="Current Firmware">{{ selectedEntry?.currentFirmware }}</el-descriptions-item>
        <el-descriptions-item label="Recommended Firmware">{{ selectedEntry?.recommendedFirmware }}</el-descriptions-item>
        <el-descriptions-item label="Latest Firmware">{{ selectedEntry?.latestFirmware }}</el-descriptions-item>
        <el-descriptions-item label="Release Date">{{ selectedEntry?.releaseDate }}</el-descriptions-item>
        <el-descriptions-item label="Compatibility">
          <el-tag :type="getCompatibilityType(selectedEntry?.compatibility)" size="small">
            {{ getCompatibilityText(selectedEntry?.compatibility) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Devices Count">{{ selectedEntry?.devicesCount }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedEntry?.status)" size="small">
            {{ getStatusText(selectedEntry?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Notes" :span="2">{{ selectedEntry?.notes }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button v-if="selectedEntry?.status === 'update_available'" type="primary" @click="updateFirmware(selectedEntry)">
          Update Firmware
        </el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Compare Dialog -->
    <el-dialog v-model="compareVisible" title="Firmware Comparison" width="900px">
      <el-table :data="compareDevices" border stripe>
        <el-table-column prop="deviceType" label="Device Type" width="160" />
        <el-table-column prop="vendor" label="Vendor" width="120" />
        <el-table-column prop="model" label="Model" width="140" />
        <el-table-column label="Current FW" width="100" align="center">
          <template #default="{ row }">
            {{ row.currentFirmware }}
          </template>
        </el-table-column>
        <el-table-column label="Recommended" width="100" align="center">
          <template #default="{ row }">
            {{ row.recommendedFirmware }}
          </template>
        </el-table-column>
        <el-table-column label="Latest" width="100" align="center">
          <template #default="{ row }">
            {{ row.latestFirmware }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Compatibility" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getCompatibilityType(row.compatibility)" size="small">
              {{ getCompatibilityText(row.compatibility) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="compareVisible = false">Close</el-button>
        <el-button type="primary" @click="bulkUpdate">Update Selected</el-button>
      </template>
    </el-dialog>

    <!-- Upload Firmware Dialog -->
    <el-dialog v-model="uploadVisible" title="Add Firmware Entry" width="500px">
      <el-form :model="uploadForm" label-width="120px">
        <el-form-item label="Vendor" required>
          <el-select v-model="uploadForm.vendor" placeholder="Select vendor" style="width: 100%">
            <el-option v-for="v in vendors.slice(1)" :key="v.value" :label="v.label" :value="v.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Device Type" required>
          <el-input v-model="uploadForm.deviceType" placeholder="e.g., BACnet Controller" />
        </el-form-item>
        <el-form-item label="Model" required>
          <el-input v-model="uploadForm.model" placeholder="e.g., PXC4.ED16" />
        </el-form-item>
        <el-form-item label="Firmware Version" required>
          <el-input v-model="uploadForm.firmwareVersion" placeholder="e.g., 4.2.1" />
        </el-form-item>
        <el-form-item label="Release Notes">
          <el-input v-model="uploadForm.releaseNotes" type="textarea" rows="3" placeholder="Describe changes or notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveUpload">Add Firmware</el-button>
      </template>
    </el-dialog>
  </div>
</template>

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

/* ==================== Main Content ==================== */
.firmware-matrix-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.control-card {
  margin-bottom: 20px;
}

.control-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.action-buttons {
  margin-top: 15px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.total-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.up-to-date-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.update-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.compatibility-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 12px;
  color: #67c23a;
  margin-top: 2px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.matrix-card {
  margin-top: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.chart {
  width: 100%;
}

.fw-version {
  font-family: monospace;
  font-weight: 500;
}

.recommended-fw {
  color: #e6a23c;
  font-weight: bold;
  font-family: monospace;
}

.current-fw {
  color: #67c23a;
  font-family: monospace;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 1200px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .control-buttons {
    justify-content: flex-start;
    margin-top: 10px;
  }

  .action-buttons .el-col {
    margin-bottom: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>