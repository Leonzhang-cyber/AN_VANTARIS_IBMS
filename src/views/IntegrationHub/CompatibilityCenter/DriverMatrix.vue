<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, Upload, Download, Filter, Cpu,
  Link, Check, Close, QuestionFilled,
  Tools, Box, Ticket
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing driver database...',
  'Loading driver compatibility matrix...',
  'Checking driver versions...',
  'Analyzing compatibility...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedProtocol = ref('all')
const selectedStatus = ref('all')
const uploadVisible = ref(false)
const detailsVisible = ref(false)
const compareVisible = ref(false)
const chartRef = ref(null)

let driverChart: echarts.ECharts | null = null

// Protocols
const protocols = [
  { value: 'all', label: 'All Protocols' },
  { value: 'bacnet', label: 'BACnet' },
  { value: 'modbus', label: 'Modbus' },
  { value: 'mqtt', label: 'MQTT' },
  { value: 'opcua', label: 'OPC-UA' },
  { value: 'snmp', label: 'SNMP' },
  { value: 'knx', label: 'KNX' }
]

// Driver matrix data
const driverEntries = ref([
  {
    id: 'DRV001', driverName: 'BACnet IP Driver', protocol: 'bacnet', vendor: 'Siemens',
    currentVersion: '4.2.1', recommendedVersion: '4.2.1', latestVersion: '4.3.0',
    status: 'up_to_date', releaseDate: '2024-01-10', compatibility: 'full',
    devicesSupported: ['PXC4', 'PXC5', 'BACnet Router'], osSupport: ['Windows', 'Linux'],
    notes: 'Latest version tested and verified', devicesCount: 24, size: '15.2 MB'
  },
  {
    id: 'DRV002', driverName: 'BACnet MSTP Driver', protocol: 'bacnet', vendor: 'Schneider',
    currentVersion: '3.8.0', recommendedVersion: '4.0.0', latestVersion: '4.1.0',
    status: 'update_available', releaseDate: '2023-12-15', compatibility: 'full',
    devicesSupported: ['M171', 'M172', 'MCU'], osSupport: ['Windows'],
    notes: 'Security improvements and bug fixes', devicesCount: 18, size: '12.8 MB'
  },
  {
    id: 'DRV003', driverName: 'Modbus TCP Driver', protocol: 'modbus', vendor: 'Schneider',
    currentVersion: '2.1.0', recommendedVersion: '2.2.0', latestVersion: '2.2.0',
    status: 'update_available', releaseDate: '2024-01-05', compatibility: 'full',
    devicesSupported: ['PM8000', 'EGX100', 'M340'], osSupport: ['Windows', 'Linux', 'macOS'],
    notes: 'Improved Modbus TCP performance', devicesCount: 32, size: '8.5 MB'
  },
  {
    id: 'DRV004', driverName: 'Modbus RTU Driver', protocol: 'modbus', vendor: 'ABB',
    currentVersion: '3.0.0', recommendedVersion: '3.1.0', latestVersion: '3.2.0',
    status: 'update_available', releaseDate: '2024-01-20', compatibility: 'partial',
    devicesSupported: ['AC500', 'AC800'], osSupport: ['Windows'],
    notes: 'Requires configuration backup before update', devicesCount: 15, size: '6.3 MB'
  },
  {
    id: 'DRV005', driverName: 'MQTT Client Driver', protocol: 'mqtt', vendor: 'Honeywell',
    currentVersion: '5.1.2', recommendedVersion: '5.1.2', latestVersion: '5.2.0',
    status: 'up_to_date', releaseDate: '2023-12-01', compatibility: 'full',
    devicesSupported: ['W7750', 'W7751', 'Spyder'], osSupport: ['Windows', 'Linux', 'macOS'],
    notes: 'Stable version recommended', devicesCount: 45, size: '4.2 MB'
  },
  {
    id: 'DRV006', driverName: 'MQTT Bridge Driver', protocol: 'mqtt', vendor: 'Honeywell',
    currentVersion: '4.5.0', recommendedVersion: '4.6.0', latestVersion: '4.6.0',
    status: 'update_available', releaseDate: '2024-01-18', compatibility: 'full',
    devicesSupported: ['CIB', 'WEBs'], osSupport: ['Windows', 'Linux'],
    notes: 'Energy savings improvements', devicesCount: 28, size: '7.1 MB'
  },
  {
    id: 'DRV007', driverName: 'OPC-UA Client Driver', protocol: 'opcua', vendor: 'Siemens',
    currentVersion: '2.0.5', recommendedVersion: '2.1.0', latestVersion: '2.2.0',
    status: 'update_available', releaseDate: '2024-01-25', compatibility: 'full',
    devicesSupported: ['S7-1200', 'S7-1500'], osSupport: ['Windows', 'Linux'],
    notes: 'New security features added', devicesCount: 12, size: '22.5 MB'
  },
  {
    id: 'DRV008', driverName: 'OPC-UA Server Driver', protocol: 'opcua', vendor: 'ABB',
    currentVersion: '1.5.0', recommendedVersion: '1.5.0', latestVersion: '1.6.0',
    status: 'up_to_date', releaseDate: '2023-12-10', compatibility: 'full',
    devicesSupported: ['AC500', 'System 800xA'], osSupport: ['Windows'],
    notes: 'Stable version', devicesCount: 8, size: '18.3 MB'
  },
  {
    id: 'DRV009', driverName: 'SNMP Manager Driver', protocol: 'snmp', vendor: 'Johnson',
    currentVersion: '3.0.0', recommendedVersion: '3.0.0', latestVersion: '3.1.0',
    status: 'up_to_date', releaseDate: '2024-01-08', compatibility: 'full',
    devicesSupported: ['FX80', 'FX60'], osSupport: ['Windows', 'Linux'],
    notes: 'Recommended for production', devicesCount: 22, size: '9.8 MB'
  },
  {
    id: 'DRV010', driverName: 'SNMP Agent Driver', protocol: 'snmp', vendor: 'Schneider',
    currentVersion: '2.0.0', recommendedVersion: '2.1.0', latestVersion: '2.1.0',
    status: 'update_available', releaseDate: '2024-01-22', compatibility: 'partial',
    devicesSupported: ['M580', 'M340'], osSupport: ['Windows'],
    notes: 'Test before production deployment', devicesCount: 10, size: '5.6 MB'
  },
  {
    id: 'DRV011', driverName: 'KNX IP Driver', protocol: 'knx', vendor: 'Siemens',
    currentVersion: '1.8.0', recommendedVersion: '1.9.0', latestVersion: '2.0.0',
    status: 'update_available', releaseDate: '2024-01-15', compatibility: 'full',
    devicesSupported: ['GAMMA', 'KNX Router'], osSupport: ['Windows', 'Linux'],
    notes: 'Critical performance improvements', devicesCount: 16, size: '11.4 MB'
  },
  {
    id: 'DRV012', driverName: 'KNX TP Driver', protocol: 'knx', vendor: 'ABB',
    currentVersion: '2.0.0', recommendedVersion: '2.0.0', latestVersion: '2.1.0',
    status: 'up_to_date', releaseDate: '2024-01-12', compatibility: 'full',
    devicesSupported: ['i-bus', 'KNX Controller'], osSupport: ['Windows'],
    notes: 'Stable version with full support', devicesCount: 14, size: '7.8 MB'
  }
])

// Driver statistics
const driverStats = reactive({
  total: 0,
  upToDate: 0,
  updateAvailable: 0,
  critical: 0,
  deprecated: 0,
  byProtocol: {} as Record<string, number>,
  avgCompatibility: 0
})

// Selected drivers for comparison
const compareDrivers = ref<any[]>([])

// Driver upload form
const uploadForm = reactive({
  driverName: '',
  protocol: '',
  vendor: '',
  version: '',
  releaseNotes: '',
  file: null
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: driverEntries.value.length
})

// Filtered driver entries
const filteredEntries = computed(() => {
  let filtered = driverEntries.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.driverName.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.vendor.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.protocol.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedProtocol.value !== 'all') {
    filtered = filtered.filter(d => d.protocol === selectedProtocol.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(d => d.status === selectedStatus.value)
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

  driverChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const protocolStats = protocols.filter(p => p.value !== 'all').map(protocol => {
    const entries = driverEntries.value.filter(d => d.protocol === protocol.value)
    const upToDate = entries.filter(e => e.status === 'up_to_date').length
    const updateAvailable = entries.filter(e => e.status === 'update_available').length
    return { protocol: protocol.label, upToDate, updateAvailable }
  })

  driverChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Up to Date', 'Update Available'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: protocolStats.map(p => p.protocol) },
    yAxis: { type: 'value', name: 'Number of Drivers' },
    series: [
      { name: 'Up to Date', type: 'bar', data: protocolStats.map(p => p.upToDate), itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Update Available', type: 'bar', data: protocolStats.map(p => p.updateAvailable), itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  driverStats.total = driverEntries.value.length
  driverStats.upToDate = driverEntries.value.filter(d => d.status === 'up_to_date').length
  driverStats.updateAvailable = driverEntries.value.filter(d => d.status === 'update_available').length

  protocols.forEach(protocol => {
    if (protocol.value !== 'all') {
      const count = driverEntries.value.filter(d => d.protocol === protocol.value).length
      driverStats.byProtocol[protocol.value] = count
    }
  })

  const compatibilitySum = driverEntries.value.reduce((sum, d) => {
    return sum + (d.compatibility === 'full' ? 100 : d.compatibility === 'partial' ? 70 : 40)
  }, 0)
  driverStats.avgCompatibility = Math.round(compatibilitySum / driverEntries.value.length)
}

const handleResize = () => {
  driverChart?.resize()
}

// ==================== Driver Functions ====================
const checkUpdates = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  driverEntries.value.forEach(entry => {
    const shouldUpdate = Math.random() > 0.7
    if (shouldUpdate && entry.status === 'up_to_date') {
      entry.status = 'update_available'
    }
  })

  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success('Driver updates checked successfully')
}

const updateDriver = async (entry: any) => {
  await ElMessageBox.confirm(
      `Update driver ${entry.driverName} from ${entry.currentVersion} to ${entry.recommendedVersion}?`,
      'Confirm Update',
      {
        confirmButtonText: 'Update',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 3000))

  entry.currentVersion = entry.recommendedVersion
  entry.status = entry.recommendedVersion === entry.latestVersion ? 'up_to_date' : 'update_available'
  entry.lastUpdated = new Date().toLocaleString()

  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success(`${entry.driverName} driver updated successfully`)
}

const bulkUpdate = async () => {
  const driversToUpdate = driverEntries.value.filter(d => d.status === 'update_available')
  if (driversToUpdate.length === 0) {
    ElMessage.warning('No driver updates available')
    return
  }

  await ElMessageBox.confirm(
      `Update ${driversToUpdate.length} drivers?`,
      'Confirm Bulk Update',
      {
        confirmButtonText: 'Update All',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 5000))

  driversToUpdate.forEach(entry => {
    entry.currentVersion = entry.recommendedVersion
    entry.status = entry.recommendedVersion === entry.latestVersion ? 'up_to_date' : 'update_available'
  })

  updateStats()
  updateChart()
  loading.value = false
  ElMessage.success(`Updated ${driversToUpdate.length} drivers successfully`)
}

const viewDetails = (entry: any) => {
  selectedDriver.value = entry
  detailsVisible.value = true
}

const compareDriversFn = () => {
  if (compareDrivers.value.length < 2) {
    ElMessage.warning('Please select at least 2 drivers to compare')
    return
  }
  compareVisible.value = true
}

const toggleCompare = (entry: any) => {
  const index = compareDrivers.value.findIndex(d => d.id === entry.id)
  if (index === -1) {
    if (compareDrivers.value.length >= 4) {
      ElMessage.warning('Maximum 4 drivers can be compared')
      return
    }
    compareDrivers.value.push(entry)
  } else {
    compareDrivers.value.splice(index, 1)
  }
}

const exportMatrix = () => {
  const data = driverEntries.value.map(d => ({
    ID: d.id,
    DriverName: d.driverName,
    Protocol: d.protocol,
    Vendor: d.vendor,
    CurrentVersion: d.currentVersion,
    RecommendedVersion: d.recommendedVersion,
    LatestVersion: d.latestVersion,
    Status: d.status,
    ReleaseDate: d.releaseDate,
    Compatibility: d.compatibility,
    DevicesSupported: d.devicesSupported.join(', '),
    OS: d.osSupport.join(', '),
    DevicesCount: d.devicesCount,
    Size: d.size
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `driver_matrix_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Driver matrix exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
}

const uploadDriver = () => {
  uploadVisible.value = true
}

const saveUpload = async () => {
  if (!uploadForm.driverName || !uploadForm.protocol || !uploadForm.vendor || !uploadForm.version) {
    ElMessage.warning('Please fill in all required fields')
    return
  }

  const newEntry = {
    id: `DRV${String(driverEntries.value.length + 1).padStart(3, '0')}`,
    driverName: uploadForm.driverName,
    protocol: uploadForm.protocol,
    vendor: uploadForm.vendor,
    currentVersion: uploadForm.version,
    recommendedVersion: uploadForm.version,
    latestVersion: uploadForm.version,
    status: 'up_to_date',
    releaseDate: new Date().toISOString().slice(0, 10),
    compatibility: 'pending',
    devicesSupported: [],
    osSupport: ['Windows'],
    notes: uploadForm.releaseNotes || 'New driver added',
    devicesCount: 0,
    size: '0 MB'
  }

  driverEntries.value.push(newEntry)
  updateStats()
  updateChart()
  uploadVisible.value = false
  uploadForm.driverName = ''
  uploadForm.protocol = ''
  uploadForm.vendor = ''
  uploadForm.version = ''
  uploadForm.releaseNotes = ''
  ElMessage.success('Driver entry added successfully')
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

const selectedDriver = ref<any>(null)
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
          <span class="loading-title">Loading Driver Matrix</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Compatibility Center - Driver Matrix</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="driver-matrix-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Driver Matrix</h2>
        <el-tag type="warning" effect="dark">Compatibility Center</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">Protocol Drivers | Version Compatibility</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedProtocol" placeholder="Protocol" style="width: 100%" @change="updateChart">
            <el-option v-for="p in protocols" :key="p.value" :label="p.label" :value="p.value" />
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
          <el-input v-model="searchKeyword" placeholder="Search by driver, vendor, or protocol..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="checkUpdates" :loading="loading">
              <el-icon><Refresh /></el-icon> Check Updates
            </el-button>
            <el-button @click="bulkUpdate">
              <el-icon><Upload /></el-icon> Bulk Update
            </el-button>
            <el-button @click="uploadDriver">
              <el-icon><Document /></el-icon> Add Driver
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
          <el-button size="small" @click="compareDriversFn" :disabled="compareDrivers.length < 2">
            <el-icon><Link /></el-icon> Compare ({{ compareDrivers.length }})
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button size="small" @click="compareDrivers = []">
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
            <el-icon><Tools /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ driverStats.total }}</div>
            <div class="stat-label">Total Drivers</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon up-to-date-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ driverStats.upToDate }}</div>
            <div class="stat-label">Up to Date</div>
            <el-progress :percentage="(driverStats.upToDate / driverStats.total) * 100" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon update-icon">
            <el-icon><Upload /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ driverStats.updateAvailable }}</div>
            <div class="stat-label">Updates Available</div>
            <div class="stat-sub-value">Ready to update</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon compatibility-icon">
            <el-icon><Link /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ driverStats.avgCompatibility }}%</div>
            <div class="stat-label">Avg Compatibility</div>
            <el-progress :percentage="driverStats.avgCompatibility" :color="driverStats.avgCompatibility > 80 ? '#67C23A' : '#E6A23C'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Driver Chart -->
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <span>Driver Status by Protocol</span>
          <el-button text type="primary" @click="updateChart">Refresh Chart</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart" style="height: 320px"></div>
    </el-card>

    <!-- Driver Matrix Table -->
    <el-card shadow="never" class="matrix-card">
      <template #header>
        <div class="table-header">
          <span>Driver Compatibility Matrix</span>
          <div class="table-actions">
            <el-checkbox
                :model-value="compareDrivers.length === filteredEntries.length && filteredEntries.length > 0"
                :indeterminate="compareDrivers.length > 0 && compareDrivers.length < filteredEntries.length"
                @change="(val) => compareDrivers = val ? [...filteredEntries] : []"
            >
              Select All
            </el-checkbox>
          </div>
        </div>
      </template>

      <el-table :data="filteredEntries" stripe style="width: 100%">
        <el-table-column type="selection" width="55" :selectable="() => true" @selection-change="(val) => compareDrivers = val" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="driverName" label="Driver Name" min-width="180" />
        <el-table-column prop="protocol" label="Protocol" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.protocol.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="vendor" label="Vendor" width="120" />
        <el-table-column label="Current" width="100" align="center">
          <template #default="{ row }">
            <span class="version-text">{{ row.currentVersion }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Recommended" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.recommendedVersion !== row.currentVersion" class="recommended-version">
              {{ row.recommendedVersion }}
            </span>
            <span v-else class="current-version">{{ row.recommendedVersion }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Latest" width="90" align="center">
          <template #default="{ row }">
            {{ row.latestVersion }}
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
                @click="updateDriver(row)"
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

    <!-- Driver Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Driver Details - ${selectedDriver?.driverName}`" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Driver ID">{{ selectedDriver?.id }}</el-descriptions-item>
        <el-descriptions-item label="Driver Name">{{ selectedDriver?.driverName }}</el-descriptions-item>
        <el-descriptions-item label="Protocol">{{ selectedDriver?.protocol?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Vendor">{{ selectedDriver?.vendor }}</el-descriptions-item>
        <el-descriptions-item label="Current Version">{{ selectedDriver?.currentVersion }}</el-descriptions-item>
        <el-descriptions-item label="Recommended Version">{{ selectedDriver?.recommendedVersion }}</el-descriptions-item>
        <el-descriptions-item label="Latest Version">{{ selectedDriver?.latestVersion }}</el-descriptions-item>
        <el-descriptions-item label="Release Date">{{ selectedDriver?.releaseDate }}</el-descriptions-item>
        <el-descriptions-item label="File Size">{{ selectedDriver?.size }}</el-descriptions-item>
        <el-descriptions-item label="Devices Count">{{ selectedDriver?.devicesCount }}</el-descriptions-item>
        <el-descriptions-item label="Compatibility">
          <el-tag :type="getCompatibilityType(selectedDriver?.compatibility)" size="small">
            {{ getCompatibilityText(selectedDriver?.compatibility) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedDriver?.status)" size="small">
            {{ getStatusText(selectedDriver?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Supported Devices" :span="2">
          <div class="supported-devices">
            <el-tag v-for="device in selectedDriver?.devicesSupported" :key="device" size="small" style="margin: 2px">
              {{ device }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="OS Support" :span="2">
          <div class="os-support">
            <el-tag v-for="os in selectedDriver?.osSupport" :key="os" size="small" style="margin: 2px">
              {{ os }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Notes" :span="2">{{ selectedDriver?.notes }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button v-if="selectedDriver?.status === 'update_available'" type="primary" @click="updateDriver(selectedDriver)">
          Update Driver
        </el-button>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Compare Dialog -->
    <el-dialog v-model="compareVisible" title="Driver Comparison" width="950px">
      <el-table :data="compareDrivers" border stripe>
        <el-table-column prop="driverName" label="Driver Name" width="180" />
        <el-table-column prop="protocol" label="Protocol" width="100" />
        <el-table-column prop="vendor" label="Vendor" width="120" />
        <el-table-column label="Current" width="90" align="center">
          <template #default="{ row }">
            {{ row.currentVersion }}
          </template>
        </el-table-column>
        <el-table-column label="Recommended" width="100" align="center">
          <template #default="{ row }">
            {{ row.recommendedVersion }}
          </template>
        </el-table-column>
        <el-table-column label="Latest" width="90" align="center">
          <template #default="{ row }">
            {{ row.latestVersion }}
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110" align="center">
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
        <el-table-column prop="devicesCount" label="Devices" width="70" align="center" />
      </el-table>
      <template #footer>
        <el-button @click="compareVisible = false">Close</el-button>
        <el-button type="primary" @click="bulkUpdate">Update Selected</el-button>
      </template>
    </el-dialog>

    <!-- Upload Driver Dialog -->
    <el-dialog v-model="uploadVisible" title="Add Driver Entry" width="500px">
      <el-form :model="uploadForm" label-width="110px">
        <el-form-item label="Driver Name" required>
          <el-input v-model="uploadForm.driverName" placeholder="e.g., BACnet IP Driver" />
        </el-form-item>
        <el-form-item label="Protocol" required>
          <el-select v-model="uploadForm.protocol" placeholder="Select protocol" style="width: 100%">
            <el-option v-for="p in protocols.slice(1)" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Vendor" required>
          <el-select v-model="uploadForm.vendor" placeholder="Select vendor" style="width: 100%">
            <el-option label="Siemens" value="Siemens" />
            <el-option label="Schneider" value="Schneider" />
            <el-option label="Honeywell" value="Honeywell" />
            <el-option label="Johnson" value="Johnson" />
            <el-option label="ABB" value="ABB" />
            <el-option label="Other" value="Other" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version" required>
          <el-input v-model="uploadForm.version" placeholder="e.g., 1.0.0" />
        </el-form-item>
        <el-form-item label="Release Notes">
          <el-input v-model="uploadForm.releaseNotes" type="textarea" rows="3" placeholder="Describe changes or features" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveUpload">Add Driver</el-button>
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
.driver-matrix-container {
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

.version-text {
  font-family: monospace;
  font-weight: 500;
}

.recommended-version {
  color: #e6a23c;
  font-weight: bold;
  font-family: monospace;
}

.current-version {
  color: #67c23a;
  font-family: monospace;
}

.supported-devices,
.os-support {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
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