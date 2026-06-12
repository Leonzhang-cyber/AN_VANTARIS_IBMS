<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, Upload, Download, Filter, Cpu,
  Link, Check, Close, QuestionFilled,
  Share, Expand, Fold
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing protocol database...',
  'Loading protocol compatibility matrix...',
  'Analyzing protocol versions...',
  'Checking interoperability...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedProtocolType = ref('all')
const selectedCompatibility = ref('all')
const detailsVisible = ref(false)
const compareVisible = ref(false)
const chartRef = ref(null)
const heatmapRef = ref(null)

let protocolChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null

// Protocol types
const protocolTypes = [
  { value: 'all', label: 'All Protocols' },
  { value: 'building', label: 'Building Automation' },
  { value: 'industrial', label: 'Industrial' },
  { value: 'iot', label: 'IoT' },
  { value: 'it', label: 'IT/Network' }
]

// Protocol matrix data
const protocols = ref([
  {
    id: 'PROT001', name: 'BACnet', type: 'building', version: 'BACnet/IP', status: 'stable',
    compatibility: 'full', releaseDate: '2024-01-15', devicesSupported: 245,
    interoperability: ['Modbus', 'OPC-UA', 'MQTT'], standards: ['ASHRAE 135', 'ISO 16484-5'],
    vendors: ['Siemens', 'Schneider', 'Honeywell', 'Johnson'], adoption: 92
  },
  {
    id: 'PROT002', name: 'BACnet MS/TP', type: 'building', version: 'MS/TP', status: 'stable',
    compatibility: 'full', releaseDate: '2024-01-10', devicesSupported: 189,
    interoperability: ['BACnet/IP', 'Modbus'], standards: ['ASHRAE 135'],
    vendors: ['Siemens', 'Schneider', 'Honeywell'], adoption: 85
  },
  {
    id: 'PROT003', name: 'Modbus TCP', type: 'industrial', version: 'TCP/IP', status: 'stable',
    compatibility: 'full', releaseDate: '2024-01-20', devicesSupported: 312,
    interoperability: ['Modbus RTU', 'BACnet', 'OPC-UA'], standards: ['IEC 61158'],
    vendors: ['Schneider', 'ABB', 'Siemens'], adoption: 94
  },
  {
    id: 'PROT004', name: 'Modbus RTU', type: 'industrial', version: 'RTU/ASCII', status: 'stable',
    compatibility: 'full', releaseDate: '2024-01-05', devicesSupported: 278,
    interoperability: ['Modbus TCP', 'BACnet'], standards: ['IEC 61158'],
    vendors: ['Schneider', 'ABB', 'Siemens'], adoption: 88
  },
  {
    id: 'PROT005', name: 'MQTT', type: 'iot', version: '5.0', status: 'stable',
    compatibility: 'full', releaseDate: '2024-01-25', devicesSupported: 456,
    interoperability: ['Sparkplug', 'OPC-UA', 'HTTP'], standards: ['OASIS'],
    vendors: ['HiveMQ', 'EMQX', 'Mosquitto'], adoption: 89
  },
  {
    id: 'PROT006', name: 'OPC-UA', type: 'industrial', version: '1.05', status: 'stable',
    compatibility: 'full', releaseDate: '2024-01-18', devicesSupported: 234,
    interoperability: ['Modbus', 'BACnet', 'MQTT'], standards: ['IEC 62541'],
    vendors: ['Siemens', 'ABB', 'Rockwell'], adoption: 87
  },
  {
    id: 'PROT007', name: 'SNMP', type: 'it', version: 'v3', status: 'stable',
    compatibility: 'partial', releaseDate: '2024-01-12', devicesSupported: 567,
    interoperability: ['HTTP', 'NetConf'], standards: ['IETF RFC 3411-3418'],
    vendors: ['Cisco', 'Juniper', 'HP'], adoption: 91
  },
  {
    id: 'PROT008', name: 'KNX', type: 'building', version: 'TP/IP', status: 'stable',
    compatibility: 'full', releaseDate: '2024-01-08', devicesSupported: 167,
    interoperability: ['BACnet', 'Modbus'], standards: ['ISO/IEC 14543', 'EN 50090'],
    vendors: ['Siemens', 'ABB', 'Schneider'], adoption: 76
  },
  {
    id: 'PROT009', name: 'LonWorks', type: 'building', version: 'FT-10', status: 'legacy',
    compatibility: 'partial', releaseDate: '2023-12-01', devicesSupported: 89,
    interoperability: ['BACnet'], standards: ['ANSI/CEA-709'],
    vendors: ['Echelon', 'Loytec'], adoption: 45
  },
  {
    id: 'PROT010', name: 'CoAP', type: 'iot', version: 'RFC 7252', status: 'emerging',
    compatibility: 'partial', releaseDate: '2024-01-28', devicesSupported: 78,
    interoperability: ['MQTT', 'HTTP'], standards: ['IETF RFC 7252'],
    vendors: ['Eclipse', 'Californium'], adoption: 34
  },
  {
    id: 'PROT011', name: 'AMQP', type: 'iot', version: '1.0', status: 'stable',
    compatibility: 'full', releaseDate: '2024-01-22', devicesSupported: 123,
    interoperability: ['MQTT', 'HTTP'], standards: ['OASIS'],
    vendors: ['Apache', 'Microsoft', 'Red Hat'], adoption: 56
  },
  {
    id: 'PROT012', name: 'DDS', type: 'iot', version: '1.4', status: 'stable',
    compatibility: 'partial', releaseDate: '2024-01-14', devicesSupported: 92,
    interoperability: ['OPC-UA'], standards: ['OMG DDS'],
    vendors: ['RTI', 'ADLINK', 'eProsima'], adoption: 48
  }
])

// Compatibility matrix data for heatmap
const compatibilityMatrix = ref([
  { protocol: 'BACnet', compatible: ['BACnet', 'Modbus', 'OPC-UA', 'KNX'], incompatible: ['SNMP', 'CoAP'] },
  { protocol: 'Modbus', compatible: ['Modbus', 'BACnet', 'OPC-UA', 'MQTT'], incompatible: ['SNMP', 'CoAP'] },
  { protocol: 'MQTT', compatible: ['MQTT', 'OPC-UA', 'HTTP', 'CoAP'], incompatible: ['BACnet', 'Modbus RTU'] },
  { protocol: 'OPC-UA', compatible: ['OPC-UA', 'BACnet', 'Modbus', 'MQTT'], incompatible: ['SNMP', 'LonWorks'] },
  { protocol: 'SNMP', compatible: ['SNMP', 'HTTP'], incompatible: ['BACnet', 'Modbus', 'MQTT'] },
  { protocol: 'KNX', compatible: ['KNX', 'BACnet', 'Modbus'], incompatible: ['MQTT', 'SNMP'] }
])

// Protocol statistics
const protocolStats = reactive({
  total: 0,
  stable: 0,
  emerging: 0,
  legacy: 0,
  byType: {} as Record<string, number>,
  avgAdoption: 0,
  totalDevices: 0
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: protocols.value.length
})

// Filtered protocols
const filteredProtocols = computed(() => {
  let filtered = protocols.value
  if (searchKeyword.value) {
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.version.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.vendors.some(v => v.toLowerCase().includes(searchKeyword.value.toLowerCase()))
    )
  }
  if (selectedProtocolType.value !== 'all') {
    filtered = filtered.filter(p => p.type === selectedProtocolType.value)
  }
  if (selectedCompatibility.value !== 'all') {
    filtered = filtered.filter(p => p.compatibility === selectedCompatibility.value)
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
        initHeatmap()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  protocolChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const typeStats = protocolTypes.filter(t => t.value !== 'all').map(type => {
    const entries = protocols.value.filter(p => p.type === type.value)
    return {
      type: type.label,
      count: entries.length,
      adoption: Math.round(entries.reduce((sum, p) => sum + p.adoption, 0) / (entries.length || 1))
    }
  })

  protocolChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Number of Protocols', 'Adoption Rate (%)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: typeStats.map(t => t.type) },
    yAxis: [
      { type: 'value', name: 'Number of Protocols' },
      { type: 'value', name: 'Adoption Rate (%)', min: 0, max: 100 }
    ],
    series: [
      { name: 'Number of Protocols', type: 'bar', data: typeStats.map(t => t.count), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Adoption Rate (%)', type: 'line', data: typeStats.map(t => t.adoption), smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const initHeatmap = () => {
  if (!heatmapRef.value) return

  const protocolsList = [...new Set(compatibilityMatrix.value.flatMap(m => [m.protocol, ...m.compatible, ...m.incompatible]))]
  const matrix: number[][] = []

  protocolsList.forEach(p1 => {
    const row: number[] = []
    protocolsList.forEach(p2 => {
      if (p1 === p2) {
        row.push(2) // Same protocol
      } else {
        const protocol = compatibilityMatrix.value.find(m => m.protocol === p1)
        if (protocol?.compatible.includes(p2)) {
          row.push(1) // Compatible
        } else if (protocol?.incompatible.includes(p2)) {
          row.push(0) // Incompatible
        } else {
          row.push(0.5) // Unknown/Partial
        }
      }
    })
    matrix.push(row)
  })

  heatmapChart = echarts.init(heatmapRef.value)
  heatmapChart.setOption({
    tooltip: {
      position: 'top',
      formatter: (params: any) => {
        const p1 = protocolsList[params.data[1]]
        const p2 = protocolsList[params.data[0]]
        const value = params.data[2]
        let status = ''
        if (value === 2) status = 'Same Protocol'
        else if (value === 1) status = 'Fully Compatible'
        else if (value === 0) status = 'Incompatible'
        else status = 'Partial Compatibility'
        return `${p1} ↔ ${p2}<br/>${status}`
      }
    },
    xAxis: { type: 'category', data: protocolsList, position: 'top', axisLabel: { rotate: 45, interval: 0 } },
    yAxis: { type: 'category', data: protocolsList, axisLabel: { rotate: 0 } },
    visualMap: {
      min: 0,
      max: 2,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: {
        color: ['#F56C6C', '#E6A23C', '#67C23A']
      },
      formatter: (value: number) => {
        if (value === 2) return 'Same'
        if (value === 1) return 'Compatible'
        if (value === 0) return 'Incompatible'
        return 'Partial'
      }
    },
    series: [{
      type: 'heatmap',
      data: matrix.flatMap((row, i) => row.map((value, j) => [j, i, value])),
      label: { show: false },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } }
    }]
  })
}

const updateStats = () => {
  protocolStats.total = protocols.value.length
  protocolStats.stable = protocols.value.filter(p => p.status === 'stable').length
  protocolStats.emerging = protocols.value.filter(p => p.status === 'emerging').length
  protocolStats.legacy = protocols.value.filter(p => p.status === 'legacy').length

  protocolTypes.forEach(type => {
    if (type.value !== 'all') {
      const count = protocols.value.filter(p => p.type === type.value).length
      protocolStats.byType[type.value] = count
    }
  })

  const totalAdoption = protocols.value.reduce((sum, p) => sum + p.adoption, 0)
  protocolStats.avgAdoption = Math.round(totalAdoption / protocols.value.length)
  protocolStats.totalDevices = protocols.value.reduce((sum, p) => sum + p.devicesSupported, 0)
}

const handleResize = () => {
  protocolChart?.resize()
  heatmapChart?.resize()
}

// ==================== Protocol Functions ====================
const refreshMatrix = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  updateStats()
  updateChart()
  initHeatmap()
  loading.value = false
  ElMessage.success('Protocol matrix refreshed successfully')
}

const viewDetails = (protocol: any) => {
  selectedProtocol.value = protocol
  detailsVisible.value = true
}

const exportMatrix = () => {
  const data = protocols.value.map(p => ({
    ID: p.id,
    Protocol: p.name,
    Type: p.type,
    Version: p.version,
    Status: p.status,
    Compatibility: p.compatibility,
    DevicesSupported: p.devicesSupported,
    AdoptionRate: `${p.adoption}%`,
    Vendors: p.vendors.join(', '),
    Standards: p.standards.join(', ')
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `protocol_matrix_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Protocol matrix exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
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
    case 'stable': return 'success'
    case 'emerging': return 'warning'
    case 'legacy': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'stable': return 'Stable'
    case 'emerging': return 'Emerging'
    case 'legacy': return 'Legacy'
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
    default: return 'Limited'
  }
}

const selectedProtocol = ref<any>(null)
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
          <span class="loading-title">Loading Protocol Matrix</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Compatibility Center - Protocol Matrix</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="protocol-matrix-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Protocol Matrix</h2>
        <el-tag type="warning" effect="dark">Compatibility Center</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">Protocol Compatibility | Interoperability</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedProtocolType" placeholder="Protocol Type" style="width: 100%" @change="updateChart">
            <el-option v-for="t in protocolTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedCompatibility" placeholder="Compatibility" clearable style="width: 100%">
            <el-option label="All" value="all" />
            <el-option label="Full" value="full" />
            <el-option label="Partial" value="partial" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search by protocol, version, or vendor..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="refreshMatrix" :loading="loading">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button @click="exportMatrix">
              <el-icon><Download /></el-icon> Export
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
            <el-icon><Share /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ protocolStats.total }}</div>
            <div class="stat-label">Total Protocols</div>
            <div class="stat-sub-value">{{ protocolStats.stable }} Stable | {{ protocolStats.emerging }} Emerging</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon devices-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ (protocolStats.totalDevices / 1000).toFixed(0) }}K+</div>
            <div class="stat-label">Total Devices</div>
            <el-progress :percentage="protocolStats.avgAdoption" :color="'#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon adoption-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ protocolStats.avgAdoption }}%</div>
            <div class="stat-label">Avg Adoption Rate</div>
            <div class="stat-sub-value">Industry-wide</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon compatibility-icon">
            <el-icon><Link /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">87%</div>
            <div class="stat-label">Interoperability</div>
            <el-progress :percentage="87" :color="'#409EFF'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Protocol Chart -->
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <span>Protocol Distribution & Adoption</span>
          <el-button text type="primary" @click="updateChart">Refresh Chart</el-button>
        </div>
      </template>
      <div ref="chartRef" class="chart" style="height: 320px"></div>
    </el-card>

    <!-- Compatibility Heatmap -->
    <el-card shadow="never" class="heatmap-card">
      <template #header>
        <div class="card-header">
          <span>Protocol Compatibility Matrix</span>
          <el-button text type="primary" @click="initHeatmap">Refresh Heatmap</el-button>
        </div>
      </template>
      <div ref="heatmapRef" class="heatmap" style="height: 500px"></div>
      <div class="heatmap-legend">
        <div class="legend-item"><span class="legend-color" style="background: #67C23A"></span> Compatible</div>
        <div class="legend-item"><span class="legend-color" style="background: #E6A23C"></span> Partial</div>
        <div class="legend-item"><span class="legend-color" style="background: #F56C6C"></span> Incompatible</div>
      </div>
    </el-card>

    <!-- Protocol Matrix Table -->
    <el-card shadow="never" class="matrix-card">
      <template #header>
        <div class="table-header">
          <span>Protocol Specifications</span>
          <div class="table-actions">
            <el-tag type="info" size="small">Click on protocol for details</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredProtocols" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="Protocol" min-width="120" />
        <el-table-column prop="type" label="Type" width="130">
          <template #default="{ row }">
            <el-tag size="small" :type="row.type === 'building' ? 'primary' : row.type === 'industrial' ? 'success' : row.type === 'iot' ? 'warning' : 'info'">
              {{ row.type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="Version" width="100" />
        <el-table-column label="Status" width="100" align="center">
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
        <el-table-column prop="devicesSupported" label="Devices" width="90" align="center" />
        <el-table-column label="Adoption" width="100" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.adoption" :stroke-width="6" :show-text="false" />
            <span style="font-size: 12px">{{ row.adoption }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Vendors" min-width="150">
          <template #default="{ row }">
            <div class="vendor-list">
              <el-tag v-for="vendor in row.vendors.slice(0, 2)" :key="vendor" size="small" style="margin: 2px">
                {{ vendor }}
              </el-tag>
              <span v-if="row.vendors.length > 2" class="more-vendors">+{{ row.vendors.length - 2 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
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

    <!-- Protocol Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Protocol Details - ${selectedProtocol?.name}`" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Protocol ID">{{ selectedProtocol?.id }}</el-descriptions-item>
        <el-descriptions-item label="Protocol Name">{{ selectedProtocol?.name }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedProtocol?.type?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedProtocol?.version }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedProtocol?.status)" size="small">
            {{ getStatusText(selectedProtocol?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Compatibility">
          <el-tag :type="getCompatibilityType(selectedProtocol?.compatibility)" size="small">
            {{ getCompatibilityText(selectedProtocol?.compatibility) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Release Date">{{ selectedProtocol?.releaseDate }}</el-descriptions-item>
        <el-descriptions-item label="Devices Supported">{{ selectedProtocol?.devicesSupported }}</el-descriptions-item>
        <el-descriptions-item label="Adoption Rate">{{ selectedProtocol?.adoption }}%</el-descriptions-item>
        <el-descriptions-item label="Standards" :span="2">
          <div class="standards-list">
            <el-tag v-for="std in selectedProtocol?.standards" :key="std" size="small" style="margin: 2px">
              {{ std }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Interoperability" :span="2">
          <div class="interop-list">
            <el-tag v-for="interop in selectedProtocol?.interoperability" :key="interop" type="success" size="small" style="margin: 2px">
              {{ interop }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Vendors" :span="2">
          <div class="vendor-list-full">
            <el-tag v-for="vendor in selectedProtocol?.vendors" :key="vendor" size="small" style="margin: 2px">
              {{ vendor }}
            </el-tag>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
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
.protocol-matrix-container {
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

.devices-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.adoption-icon {
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

.chart-card,
.heatmap-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.heatmap-legend {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
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

.heatmap {
  width: 100%;
}

.vendor-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.more-vendors {
  font-size: 12px;
  color: #909399;
  margin-left: 4px;
}

.standards-list,
.interop-list,
.vendor-list-full {
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

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .heatmap-legend {
    flex-wrap: wrap;
    gap: 15px;
  }
}
</style>