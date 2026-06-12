<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, VideoPlay,
  DataLine, Document, CircleCheck, CircleClose,
  Loading, Clock, TrendCharts, Monitor
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing protocol analyzer...',
  'Connecting to BACnet devices...',
  'Preparing Modbus scanner...',
  'Loading point database...',
  'Almost ready...'
]

// ==================== Component State ====================
const testing = ref(false)
const searchKeyword = ref('')
const selectedProtocol = ref('bacnet')
const selectedDevice = ref('')
const testResultsVisible = ref(false)
const batchTestVisible = ref(false)
const chartRef = ref(null)

let responseChart: echarts.ECharts | null = null

// Protocols
const protocols = [
  { value: 'bacnet', label: 'BACnet/IP' },
  { value: 'modbus', label: 'Modbus TCP' },
  { value: 'mqtt', label: 'MQTT' },
  { value: 'opcua', label: 'OPC-UA' },
  { value: 'snmp', label: 'SNMP' }
]

// Available devices
const devices = ref([
  { id: 'DEV001', name: 'Building A - BMS Controller', protocol: 'bacnet', ip: '192.168.1.100', port: 47808, status: 'online', points: 245 },
  { id: 'DEV002', name: 'Chiller Plant Controller', protocol: 'bacnet', ip: '192.168.1.101', port: 47808, status: 'online', points: 89 },
  { id: 'DEV003', name: 'AHU-1 Controller', protocol: 'bacnet', ip: '192.168.1.102', port: 47808, status: 'online', points: 56 },
  { id: 'DEV004', name: 'Power Meter - Main', protocol: 'modbus', ip: '192.168.2.100', port: 502, status: 'online', points: 32 },
  { id: 'DEV005', name: 'Lighting Panel - L1', protocol: 'modbus', ip: '192.168.2.101', port: 502, status: 'offline', points: 24 },
  { id: 'DEV006', name: 'Temperature Sensors Hub', protocol: 'mqtt', ip: '192.168.3.100', port: 1883, status: 'online', points: 128 },
  { id: 'DEV007', name: 'VFD Pump Controller', protocol: 'modbus', ip: '192.168.2.102', port: 502, status: 'online', points: 18 },
  { id: 'DEV008', name: 'OPC-UA Gateway', protocol: 'opcua', ip: '192.168.4.100', port: 4840, status: 'online', points: 345 }
])

// Points for testing
const testPoints = ref([
  { id: 'P001', name: 'Supply Air Temperature', device: 'AHU-1 Controller', address: 'AI:1', value: null, status: 'pending', responseTime: null, unit: '°C', expectedRange: { min: 18, max: 26 } },
  { id: 'P002', name: 'Return Air Temperature', device: 'AHU-1 Controller', address: 'AI:2', value: null, status: 'pending', responseTime: null, unit: '°C', expectedRange: { min: 20, max: 24 } },
  { id: 'P003', name: 'Supply Fan Speed', device: 'AHU-1 Controller', address: 'AO:1', value: null, status: 'pending', responseTime: null, unit: '%', expectedRange: { min: 0, max: 100 } },
  { id: 'P004', name: 'Chilled Water Valve', device: 'AHU-1 Controller', address: 'AO:2', value: null, status: 'pending', responseTime: null, unit: '%', expectedRange: { min: 0, max: 100 } },
  { id: 'P005', name: 'Room Temperature', device: 'Temperature Sensors Hub', address: 'sensors/temp/zone1', value: null, status: 'pending', responseTime: null, unit: '°C', expectedRange: { min: 19, max: 25 } },
  { id: 'P006', name: 'Room Humidity', device: 'Temperature Sensors Hub', address: 'sensors/humidity/zone1', value: null, status: 'pending', responseTime: null, unit: '%', expectedRange: { min: 40, max: 60 } },
  { id: 'P007', name: 'CO2 Level', device: 'Temperature Sensors Hub', address: 'sensors/co2/zone1', value: null, status: 'pending', responseTime: null, unit: 'ppm', expectedRange: { min: 350, max: 800 } },
  { id: 'P008', name: 'Power Consumption', device: 'Power Meter - Main', address: '40001', value: null, status: 'pending', responseTime: null, unit: 'kW', expectedRange: { min: 0, max: 500 } },
  { id: 'P009', name: 'Current (Phase A)', device: 'Power Meter - Main', address: '40003', value: null, status: 'pending', responseTime: null, unit: 'A', expectedRange: { min: 0, max: 200 } },
  { id: 'P010', name: 'Voltage (Line)', device: 'Power Meter - Main', address: '40005', value: null, status: 'pending', responseTime: null, unit: 'V', expectedRange: { min: 210, max: 240 } }
])

// Batch test configuration
const batchConfig = reactive({
  protocol: 'bacnet',
  deviceId: '',
  pointTypes: ['analog', 'binary', 'multistate'],
  timeout: 5000,
  retries: 2
})

// Test statistics
const testStats = reactive({
  total: 0,
  passed: 0,
  failed: 0,
  timeout: 0,
  avgResponseTime: 0,
  minResponseTime: 0,
  maxResponseTime: 0
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: testPoints.value.length
})

// Filtered points
const filteredPoints = computed(() => {
  let filtered = testPoints.value
  if (searchKeyword.value) {
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.device.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.address.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedDevice.value) {
    filtered = filtered.filter(p => p.device === selectedDevice.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Unique devices for filter
const uniqueDevices = computed(() => {
  return [...new Set(testPoints.value.map(p => p.device))]
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
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  responseChart = echarts.init(chartRef.value)
  responseChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: [] },
    yAxis: { type: 'value', name: 'Response Time (ms)' },
    series: [{ name: 'Response Time', type: 'bar', data: [], itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } }]
  })
}

const updateChart = (responseTimes: number[]) => {
  if (!responseChart) return
  responseChart.setOption({
    xAxis: { data: testPoints.value.filter(p => p.responseTime !== null).map(p => p.name.substring(0, 15)) },
    series: [{ data: responseTimes }]
  })
}

const handleResize = () => {
  responseChart?.resize()
}

// ==================== Test Functions ====================
const simulateRead = async (point: any): Promise<{ value: number; responseTime: number }> => {
  const startTime = performance.now()

  // Simulate network delay based on protocol
  let delay = 0
  switch (selectedProtocol.value) {
    case 'bacnet':
      delay = Math.random() * 100 + 20
      break
    case 'modbus':
      delay = Math.random() * 80 + 15
      break
    case 'mqtt':
      delay = Math.random() * 60 + 10
      break
    case 'opcua':
      delay = Math.random() * 150 + 50
      break
    case 'snmp':
      delay = Math.random() * 120 + 30
      break
    default:
      delay = Math.random() * 100 + 20
  }

  await new Promise(resolve => setTimeout(resolve, delay))

  // Generate realistic value based on point type
  let value = 0
  if (point.name.includes('Temperature')) {
    value = 20 + Math.random() * 8
  } else if (point.name.includes('Humidity')) {
    value = 40 + Math.random() * 30
  } else if (point.name.includes('CO2')) {
    value = 400 + Math.random() * 200
  } else if (point.name.includes('Power')) {
    value = Math.random() * 300
  } else if (point.name.includes('Current')) {
    value = Math.random() * 150
  } else if (point.name.includes('Voltage')) {
    value = 220 + (Math.random() - 0.5) * 20
  } else if (point.name.includes('Speed') || point.name.includes('Valve')) {
    value = Math.random() * 100
  } else {
    value = Math.random() * 100
  }

  const endTime = performance.now()
  return { value: parseFloat(value.toFixed(1)), responseTime: Math.round(endTime - startTime) }
}

const testSinglePoint = async (point: any) => {
  point.status = 'testing'

  try {
    const result = await simulateRead(point)
    point.value = result.value
    point.responseTime = result.responseTime
    point.status = 'passed'

    // Check if value is within expected range
    if (point.expectedRange) {
      const isInRange = result.value >= point.expectedRange.min && result.value <= point.expectedRange.max
      point.status = isInRange ? 'passed' : 'warning'
    }

    ElMessage.success(`Successfully read ${point.name}: ${result.value} ${point.unit} (${result.responseTime}ms)`)
  } catch (error) {
    point.status = 'failed'
    ElMessage.error(`Failed to read ${point.name}`)
  }
}

const testAllPoints = async () => {
  testing.value = true
  testStats.total = filteredPoints.value.length
  testStats.passed = 0
  testStats.failed = 0
  testStats.timeout = 0
  const responseTimes: number[] = []

  for (const point of filteredPoints.value) {
    point.status = 'testing'
    await new Promise(resolve => setTimeout(resolve, 100)) // Small delay between requests

    try {
      const result = await simulateRead(point)
      point.value = result.value
      point.responseTime = result.responseTime
      responseTimes.push(result.responseTime)

      let isInRange = true
      if (point.expectedRange) {
        isInRange = result.value >= point.expectedRange.min && result.value <= point.expectedRange.max
      }

      point.status = isInRange ? 'passed' : 'warning'

      if (point.status === 'passed') {
        testStats.passed++
      } else {
        testStats.failed++
      }
    } catch (error) {
      point.status = 'failed'
      testStats.failed++
    }
  }

  // Calculate response time statistics
  if (responseTimes.length > 0) {
    testStats.avgResponseTime = Math.round(responseTimes.reduce((a, b) => a + b, 0) / responseTimes.length)
    testStats.minResponseTime = Math.min(...responseTimes)
    testStats.maxResponseTime = Math.max(...responseTimes)
  }

  updateChart(responseTimes)
  testing.value = false
  ElMessage.success(`Test completed: ${testStats.passed} passed, ${testStats.failed} failed`)
}

const runBatchTest = () => {
  batchTestVisible.value = true
}

const executeBatchTest = async () => {
  batchTestVisible.value = false
  testing.value = true

  // Filter points by protocol and device
  let pointsToTest = testPoints.value
  if (batchConfig.deviceId) {
    pointsToTest = pointsToTest.filter(p => p.device === batchConfig.deviceId)
  }

  testStats.total = pointsToTest.length
  testStats.passed = 0
  testStats.failed = 0

  for (const point of pointsToTest) {
    point.status = 'testing'
    await new Promise(resolve => setTimeout(resolve, 50))

    try {
      const result = await simulateRead(point)
      point.value = result.value
      point.responseTime = result.responseTime
      point.status = 'passed'
      testStats.passed++
    } catch (error) {
      point.status = 'failed'
      testStats.failed++
    }
  }

  testing.value = false
  ElMessage.success(`Batch test completed: ${testStats.passed}/${testStats.total} passed`)
}

const viewTestResults = () => {
  testResultsVisible.value = true
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'passed': return CircleCheck
    case 'failed': return CircleClose
    case 'testing': return Loading
    case 'warning': return Warning
    default: return Clock
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'passed': return 'success'
    case 'failed': return 'danger'
    case 'testing': return 'warning'
    case 'warning': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'passed': return 'Passed'
    case 'failed': return 'Failed'
    case 'testing': return 'Testing...'
    case 'warning': return 'Warning'
    default: return 'Pending'
  }
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const exportResults = () => {
  const results = testPoints.value.map(p => ({
    PointID: p.id,
    PointName: p.name,
    Device: p.device,
    Address: p.address,
    Value: p.value,
    Unit: p.unit,
    Status: p.status,
    ResponseTime: p.responseTime
  }))

  const csv = convertToCSV(results)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `point_read_test_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Results exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
}
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
          <span class="loading-title">Loading Point Read Test</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Protocol Health Check - Point Read Test</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="point-read-test-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Point Read Test</h2>
        <el-tag type="warning" effect="dark">Protocol Health Check</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">BACnet | Modbus | MQTT | OPC-UA | SNMP</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedProtocol" placeholder="Select Protocol" style="width: 100%">
            <el-option v-for="p in protocols" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedDevice" placeholder="Filter by Device" clearable style="width: 100%">
            <el-option v-for="d in uniqueDevices" :key="d" :label="d" :value="d" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search points..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="testAllPoints" :loading="testing">
              <el-icon><VideoPlay /></el-icon> Test All
            </el-button>
            <el-button @click="runBatchTest">
              <el-icon><DataLine /></el-icon> Batch Test
            </el-button>
            <el-button @click="exportResults">
              <el-icon><Document /></el-icon> Export
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon total-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ testStats.total || filteredPoints.length }}</div>
            <div class="stat-label">Total Points</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon passed-icon">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ testStats.passed }}</div>
            <div class="stat-label">Passed</div>
            <el-progress :percentage="testStats.total ? (testStats.passed / testStats.total) * 100 : 0" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon failed-icon">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ testStats.failed }}</div>
            <div class="stat-label">Failed</div>
            <el-progress :percentage="testStats.total ? (testStats.failed / testStats.total) * 100 : 0" :color="'#F56C6C'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon response-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ testStats.avgResponseTime }}ms</div>
            <div class="stat-label">Avg Response</div>
            <div class="stat-sub-value">Min: {{ testStats.minResponseTime }}ms | Max: {{ testStats.maxResponseTime }}ms</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Response Time Chart -->
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <span>Response Time by Point</span>
          <el-button text type="primary" @click="viewTestResults">View Details</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart" style="height: 320px"></div>
    </el-card>

    <!-- Points Table -->
    <el-card shadow="never" class="points-card">
      <template #header>
        <div class="table-header">
          <span>Points to Test</span>
          <div class="table-actions">
            <el-button type="primary" size="small" @click="testAllPoints" :loading="testing">
              Test All Points
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredPoints" stripe style="width: 100%">
        <el-table-column prop="id" label="Point ID" width="80" />
        <el-table-column prop="name" label="Point Name" min-width="180" />
        <el-table-column prop="device" label="Device" width="180" />
        <el-table-column prop="address" label="Address" width="150" />
        <el-table-column label="Value" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.value !== null" :class="{ 'warning-value': row.status === 'warning' }">
              {{ row.value }} {{ row.unit }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Response Time" width="110" align="center">
          <template #default="{ row }">
            <span v-if="row.responseTime !== null" :class="{ 'slow-response': row.responseTime > 100 }">
              {{ row.responseTime }}ms
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              <el-icon style="margin-right: 4px"><component :is="getStatusIcon(row.status)" /></el-icon>
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Expected Range" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.expectedRange">
              {{ row.expectedRange.min }} - {{ row.expectedRange.max }} {{ row.unit }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="testSinglePoint(row)" :disabled="testing">
              Test
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

    <!-- Test Results Dialog -->
    <el-dialog v-model="testResultsVisible" title="Test Results Summary" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Total Points">{{ testStats.total || filteredPoints.length }}</el-descriptions-item>
        <el-descriptions-item label="Passed">{{ testStats.passed }}</el-descriptions-item>
        <el-descriptions-item label="Failed">{{ testStats.failed }}</el-descriptions-item>
        <el-descriptions-item label="Success Rate">{{ testStats.total ? ((testStats.passed / testStats.total) * 100).toFixed(1) : 0 }}%</el-descriptions-item>
        <el-descriptions-item label="Avg Response Time">{{ testStats.avgResponseTime }}ms</el-descriptions-item>
        <el-descriptions-item label="Min/Max Response">{{ testStats.minResponseTime }}ms / {{ testStats.maxResponseTime }}ms</el-descriptions-item>
      </el-descriptions>

      <el-divider>Failed Points</el-divider>
      <el-table :data="testPoints.filter(p => p.status === 'failed')" stripe max-height="250">
        <el-table-column prop="name" label="Point Name" />
        <el-table-column prop="device" label="Device" />
        <el-table-column prop="address" label="Address" />
        <el-table-column label="Status">
          <template #default>
            <el-tag type="danger" size="small">Failed</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <template #footer>
        <el-button type="primary" @click="testResultsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Batch Test Dialog -->
    <el-dialog v-model="batchTestVisible" title="Batch Test Configuration" width="500px">
      <el-form :model="batchConfig" label-width="120px">
        <el-form-item label="Protocol">
          <el-select v-model="batchConfig.protocol" style="width: 100%">
            <el-option v-for="p in protocols" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Device">
          <el-select v-model="batchConfig.deviceId" clearable placeholder="All Devices" style="width: 100%">
            <el-option v-for="d in devices.filter(d => d.protocol === batchConfig.protocol)" :key="d.id" :label="d.name" :value="d.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="Point Types">
          <el-checkbox-group v-model="batchConfig.pointTypes">
            <el-checkbox value="analog">Analog Points</el-checkbox>
            <el-checkbox value="binary">Binary Points</el-checkbox>
            <el-checkbox value="multistate">Multistate Points</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Timeout (ms)">
          <el-input-number v-model="batchConfig.timeout" :min="1000" :max="30000" :step="1000" />
        </el-form-item>
        <el-form-item label="Retries">
          <el-input-number v-model="batchConfig.retries" :min="0" :max="5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchTestVisible = false">Cancel</el-button>
        <el-button type="primary" @click="executeBatchTest">Start Batch Test</el-button>
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
.point-read-test-container {
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

.passed-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.failed-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.response-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
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

.points-card {
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

.warning-value {
  color: #e6a23c;
  font-weight: bold;
}

.slow-response {
  color: #f56c6c;
  font-weight: bold;
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

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>