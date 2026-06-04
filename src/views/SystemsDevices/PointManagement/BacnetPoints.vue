<template>
  <!-- Global Pre Loading Screen -->
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
        <div class="loading-tip">BACNET POINT MODULE</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content After Loading Finish -->
  <div v-else class="bacnet-point-container">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalPoints }}</span>
          <span class="stat-label">Total Points</span>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ onlinePoints }}</span>
          <span class="stat-label">Online</span>
        </div>
        <div class="stat-percent">{{ onlinePercent }}%</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ alarmPoints }}</span>
          <span class="stat-label">Alarm</span>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ avgValue.toFixed(1) }}</span>
          <span class="stat-label">Avg Value</span>
        </div>
      </div>
    </div>

    <!-- 筛选卡片 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="Device Code">
          <el-input v-model="filterForm.deviceCode" placeholder="Input Device Code" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="Point Type">
          <el-select v-model="filterForm.pointType" placeholder="Select Point Type" clearable style="width: 160px">
            <el-option v-for="item in pointTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Point Name">
          <el-input v-model="filterForm.pointName" placeholder="Search point name" clearable style="width: 200px" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="filterForm.status" placeholder="Select Status" clearable style="width: 120px">
            <el-option label="All" value="" />
            <el-option label="Online" value="online" />
            <el-option label="Offline" value="offline" />
            <el-option label="Alarm" value="alarm" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetFilter">Reset</el-button>
          <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表和拓扑区域 -->
    <div class="split-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span>BACNET Point Real-Time Trend</span>
            <el-radio-group v-model="trendMetric" size="small" @change="updateTrendChart">
              <el-radio-button label="temperature">Temperature</el-radio-button>
              <el-radio-button label="humidity">Humidity</el-radio-button>
              <el-radio-button label="pressure">Pressure</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-box"></div>
        <div class="chart-legend">
          <span><span class="legend-dot temp"></span> Temperature (°C)</span>
          <span><span class="legend-dot humidity"></span> Humidity (%)</span>
          <span><span class="legend-dot pressure"></span> Pressure (kPa)</span>
        </div>
      </el-card>

      <el-card class="flow-card" shadow="hover">
        <template #header>
          <div class="card-header-title">BACNET Device Topology</div>
        </template>
        <div class="topology-container">
          <VueFlow
              :nodes="flowNodes"
              :edges="flowEdges"
              :default-viewport="{ zoom: 0.8, x: 50, y: 20 }"
              :min-zoom="0.5"
              :max-zoom="1.5"
              fit-view-on-init
              class="flow-wrap"
          >
            <template #node-custom="props">
              <div :class="['flow-node', props.data.status]">
                <div class="node-icon">
                  <el-icon><component :is="getDeviceIcon(props.data.type)" /></el-icon>
                </div>
                <div class="node-title">{{ props.data.label }}</div>
                <div class="node-desc">{{ props.data.ip }}</div>
                <div class="node-status">
                  <span class="status-dot" :class="props.data.status"></span>
                  <span>{{ props.data.status }}</span>
                </div>
              </div>
            </template>
          </VueFlow>
        </div>
      </el-card>
    </div>

    <!-- 点列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">BACNET Points List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="480" v-loading="tableLoading">
        <el-table-column label="Point ID" prop="pointId" width="110" />
        <el-table-column label="Device ID" prop="deviceId" width="120" />
        <el-table-column label="BACnet Address" prop="bacAddr" width="150" />
        <el-table-column label="Point Name" prop="pointName" min-width="180" show-overflow-tooltip />
        <el-table-column label="Point Type" prop="pointType" width="100">
          <template #default="scope">
            <el-tag :type="getPointTypeTag(scope.row.pointType)" size="small">{{ scope.row.pointType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Current Value" prop="realValue" width="120">
          <template #default="scope">
            <div class="value-cell">
              <span :class="getValColor(scope.row)">{{ scope.row.realValue }}</span>
              <span class="unit">{{ scope.row.unit }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Status" prop="status" width="100">
          <template #default="scope">
            <div class="status-cell">
              <span class="status-dot" :class="scope.row.status"></span>
              <span>{{ scope.row.status.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Quality" prop="quality" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.quality === 'good' ? 'success' : 'danger'" size="small">{{ scope.row.quality }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Update Time" prop="updateTime" width="160" />
        <el-table-column label="Operation" width="140" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="manualSet(scope.row)">Set</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
            v-model:current-page="pageInfo.pageNum"
            v-model:page-size="pageInfo.pageSize"
            :page-sizes="[15, 30, 50, 100]"
            :total="pageInfo.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'

import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import { Connection, CircleCheckFilled, WarningFilled, DataLine, Refresh, Cpu, Monitor, House, Setting } from '@element-plus/icons-vue'

// ========== Global Page Preloading Logic ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading BACnet modules...',
  'Connecting to devices...',
  'Initializing real-time stream...',
  'Almost ready...'
]

// ========== Chart References ==========
const trendChartRef = ref<HTMLDivElement | null>(null)
let trendInstance: echarts.ECharts | null = null
let realtimeTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const trendMetric = ref('temperature')

// ========== Filter Form ==========
const filterForm = reactive({
  deviceCode: '',
  pointType: '',
  pointName: '',
  status: ''
})

const pointTypeOptions = [
  { label: 'AI - Analog Input', value: 'AI' },
  { label: 'AO - Analog Output', value: 'AO' },
  { label: 'DI - Digital Input', value: 'DI' },
  { label: 'DO - Digital Output', value: 'DO' }
]

// ========== Pagination ==========
const pageInfo = reactive({
  pageNum: 1,
  pageSize: 15,
  total: 0
})

// ========== Table Data ==========
const allTableData = ref<any[]>([])

// 统计数据
const totalPoints = computed(() => allTableData.value.length)
const onlinePoints = computed(() => allTableData.value.filter(item => item.status === 'online').length)
const alarmPoints = computed(() => allTableData.value.filter(item => item.status === 'alarm' || item.quality === 'bad').length)
const onlinePercent = computed(() => totalPoints.value ? Math.round(onlinePoints.value / totalPoints.value * 100) : 0)
const avgValue = computed(() => {
  const analogPoints = allTableData.value.filter(item => item.pointType === 'AI' && typeof item.realValue === 'number')
  if (analogPoints.length === 0) return 0
  const sum = analogPoints.reduce((s, item) => s + item.realValue, 0)
  return sum / analogPoints.length
})

// 分页数据
const paginatedTableData = computed(() => {
  let filtered = [...allTableData.value]

  if (filterForm.deviceCode) {
    filtered = filtered.filter(item => item.deviceId?.toLowerCase().includes(filterForm.deviceCode.toLowerCase()))
  }
  if (filterForm.pointType) {
    filtered = filtered.filter(item => item.pointType === filterForm.pointType)
  }
  if (filterForm.pointName) {
    filtered = filtered.filter(item => item.pointName?.toLowerCase().includes(filterForm.pointName.toLowerCase()))
  }
  if (filterForm.status) {
    filtered = filtered.filter(item => item.status === filterForm.status)
  }

  pageInfo.total = filtered.length
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return filtered.slice(start, start + pageInfo.pageSize)
})

// ========== VueFlow Topology ==========
const getDeviceIcon = (type: string) => {
  const icons: Record<string, any> = {
    gateway: Setting,
    controller: Monitor,
    sensor: Cpu,
    actuator: House
  }
  return icons[type] || Cpu
}

const flowNodes = ref([
  { id: 'gateway', type: 'custom', position: { x: 300, y: 20 }, data: { label: 'BACnet Gateway', ip: '192.168.1.10', status: 'online', type: 'gateway' } },
  { id: 'controller1', type: 'custom', position: { x: 100, y: 150 }, data: { label: 'B-BC Controller', ip: '192.168.1.11', status: 'online', type: 'controller' } },
  { id: 'controller2', type: 'custom', position: { x: 300, y: 150 }, data: { label: 'B-ASC Controller', ip: '192.168.1.12', status: 'online', type: 'controller' } },
  { id: 'controller3', type: 'custom', position: { x: 500, y: 150 }, data: { label: 'B-AAC Controller', ip: '192.168.1.13', status: 'warning', type: 'controller' } },
  { id: 'sensor1', type: 'custom', position: { x: 30, y: 280 }, data: { label: 'Temperature Sensor', ip: '192.168.1.14', status: 'online', type: 'sensor' } },
  { id: 'sensor2', type: 'custom', position: { x: 170, y: 280 }, data: { label: 'Humidity Sensor', ip: '192.168.1.15', status: 'online', type: 'sensor' } },
  { id: 'actuator1', type: 'custom', position: { x: 310, y: 280 }, data: { label: 'VAV Actuator', ip: '192.168.1.16', status: 'online', type: 'actuator' } },
  { id: 'sensor3', type: 'custom', position: { x: 450, y: 280 }, data: { label: 'Pressure Sensor', ip: '192.168.1.17', status: 'offline', type: 'sensor' } },
  { id: 'actuator2', type: 'custom', position: { x: 570, y: 280 }, data: { label: 'Damper Actuator', ip: '192.168.1.18', status: 'warning', type: 'actuator' } }
])

const flowEdges = ref([
  { id: 'e-gw-c1', source: 'gateway', target: 'controller1', animated: true },
  { id: 'e-gw-c2', source: 'gateway', target: 'controller2', animated: true },
  { id: 'e-gw-c3', source: 'gateway', target: 'controller3', animated: true },
  { id: 'e-c1-s1', source: 'controller1', target: 'sensor1' },
  { id: 'e-c1-s2', source: 'controller1', target: 'sensor2' },
  { id: 'e-c2-a1', source: 'controller2', target: 'actuator1' },
  { id: 'e-c3-s3', source: 'controller3', target: 'sensor3' },
  { id: 'e-c3-a2', source: 'controller3', target: 'actuator2' }
])

// ========== Chart Data ==========
const trendData = ref({
  timestamps: [] as string[],
  temperature: [] as number[],
  humidity: [] as number[],
  pressure: [] as number[]
})

// 生成模拟趋势数据
const generateTrendData = () => {
  const now = new Date()
  const timestamps = []
  const temperature = []
  const humidity = []
  const pressure = []

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    const hour = time.getHours()
    const timeStr = `${String(time.getMonth() + 1).padStart(2, '0')}/${String(time.getDate()).padStart(2, '0')} ${String(hour).padStart(2, '0')}:00`
    timestamps.push(timeStr)

    // 模拟日间温度变化
    const baseTemp = 22
    const dayEffect = hour >= 8 && hour <= 18 ? 5 : 0
    const randomTemp = (Math.random() - 0.5) * 2
    temperature.push(Number((baseTemp + dayEffect + randomTemp).toFixed(1)))

    // 模拟湿度变化
    const baseHumidity = 55
    const humidityEffect = hour >= 10 && hour <= 16 ? -8 : 3
    const randomHumidity = (Math.random() - 0.5) * 5
    humidity.push(Math.min(85, Math.max(30, Number((baseHumidity + humidityEffect + randomHumidity).toFixed(0)))))

    // 模拟压力变化
    const basePressure = 101.3
    const randomPressure = (Math.random() - 0.5) * 2.5
    pressure.push(Number((basePressure + randomPressure).toFixed(1)))
  }

  trendData.value = { timestamps, temperature, humidity, pressure }
}

// 添加新数据点
const appendTrendData = () => {
  const now = new Date()
  const timeStr = `${String(now.getMonth() + 1).padStart(2, '0')}/${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:00`
  const hour = now.getHours()

  const baseTemp = 22
  const dayEffect = hour >= 8 && hour <= 18 ? 5 : 0
  const randomTemp = (Math.random() - 0.5) * 2
  const newTemp = Number((baseTemp + dayEffect + randomTemp).toFixed(1))

  const baseHumidity = 55
  const humidityEffect = hour >= 10 && hour <= 16 ? -8 : 3
  const randomHumidity = (Math.random() - 0.5) * 5
  const newHumidity = Math.min(85, Math.max(30, Number((baseHumidity + humidityEffect + randomHumidity).toFixed(0))))

  const basePressure = 101.3
  const randomPressure = (Math.random() - 0.5) * 2.5
  const newPressure = Number((basePressure + randomPressure).toFixed(1))

  trendData.value.timestamps.push(timeStr)
  trendData.value.temperature.push(newTemp)
  trendData.value.humidity.push(newHumidity)
  trendData.value.pressure.push(newPressure)

  if (trendData.value.timestamps.length > 48) {
    trendData.value.timestamps.shift()
    trendData.value.temperature.shift()
    trendData.value.humidity.shift()
    trendData.value.pressure.shift()
  }

  updateTrendChart()
}

// 初始化图表
const initChart = async () => {
  await nextTick()

  if (!trendChartRef.value) {
    console.warn('trendChartRef is not ready')
    // 延迟重试
    setTimeout(() => initChart(), 100)
    return
  }

  // 生成数据
  generateTrendData()

  // 确保 echarts 已加载
  if (!echarts) {
    console.warn('echarts not loaded')
    setTimeout(() => initChart(), 100)
    return
  }

  try {
    if (trendInstance) {
      trendInstance.dispose()
      trendInstance = null
    }

    trendInstance = echarts.init(trendChartRef.value)
    updateTrendChart()

    // 监听窗口大小变化
    window.addEventListener('resize', handleChartResize)
  } catch (error) {
    console.error('Chart initialization error:', error)
  }
}

const updateTrendChart = () => {
  if (!trendInstance || !trendData.value.timestamps.length) return

  let seriesData, yAxisName, lineColor, yAxisMin, yAxisMax

  switch (trendMetric.value) {
    case 'temperature':
      seriesData = trendData.value.temperature
      yAxisName = 'Temperature (°C)'
      lineColor = '#f56c6c'
      yAxisMin = 15
      yAxisMax = 35
      break
    case 'humidity':
      seriesData = trendData.value.humidity
      yAxisName = 'Humidity (%)'
      lineColor = '#409eff'
      yAxisMin = 30
      yAxisMax = 85
      break
    default:
      seriesData = trendData.value.pressure
      yAxisName = 'Pressure (kPa)'
      lineColor = '#67c23a'
      yAxisMin = 98
      yAxisMax = 105
  }

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const val = params[0].value
        const unit = trendMetric.value === 'temperature' ? '°C' : trendMetric.value === 'humidity' ? '%' : 'kPa'
        return `${params[0].axisValue}<br/>${params[0].seriesName}: ${val} ${unit}`
      }
    },
    grid: {
      left: '8%',
      right: '5%',
      top: '12%',
      bottom: '8%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: trendData.value.timestamps,
      axisLabel: { rotate: 45, interval: 4, fontSize: 10 },
      axisLine: { lineStyle: { color: '#94a3b8' } }
    },
    yAxis: {
      type: 'value',
      name: yAxisName,
      nameTextStyle: { fontSize: 12, fontWeight: 500 },
      min: yAxisMin,
      max: yAxisMax,
      splitLine: { lineStyle: { color: '#e2e8f0', type: 'dashed' } }
    },
    series: [{
      name: trendMetric.value === 'temperature' ? 'Temperature' : trendMetric.value === 'humidity' ? 'Humidity' : 'Pressure',
      type: 'line',
      data: seriesData,
      smooth: true,
      lineStyle: { color: lineColor, width: 2 },
      areaStyle: { opacity: 0.1, color: lineColor },
      symbol: 'circle',
      symbolSize: 5,
      itemStyle: { color: lineColor }
    }]
  }

  trendInstance.setOption(option, true)
}

const handleChartResize = () => {
  if (trendInstance) {
    trendInstance.resize()
  }
}

// ========== 生成模拟点数据 ==========
const pointNamesMap = {
  AI: [
    { name: 'Supply Air Temperature', unit: '°C', min: 18, max: 26 },
    { name: 'Return Air Temperature', unit: '°C', min: 20, max: 28 },
    { name: 'Room Temperature', unit: '°C', min: 21, max: 25 },
    { name: 'Outside Air Temperature', unit: '°C', min: -5, max: 40 },
    { name: 'Chilled Water Supply Temp', unit: '°C', min: 5, max: 12 },
    { name: 'Hot Water Supply Temp', unit: '°C', min: 35, max: 55 },
    { name: 'CO2 Level', unit: 'ppm', min: 350, max: 1200 },
    { name: 'Air Pressure', unit: 'Pa', min: 50, max: 500 }
  ],
  AO: [
    { name: 'Valve Position', unit: '%', min: 0, max: 100 },
    { name: 'Damper Position', unit: '%', min: 0, max: 100 },
    { name: 'Fan Speed', unit: '%', min: 0, max: 100 },
    { name: 'Temperature Setpoint', unit: '°C', min: 18, max: 26 },
    { name: 'Dimming Level', unit: '%', min: 0, max: 100 }
  ],
  DI: [
    { name: 'Fan Status', unit: '', min: 0, max: 1 },
    { name: 'Filter Status', unit: '', min: 0, max: 1 },
    { name: 'Alarm Status', unit: '', min: 0, max: 1 },
    { name: 'Run Status', unit: '', min: 0, max: 1 },
    { name: 'Occupancy Status', unit: '', min: 0, max: 1 }
  ],
  DO: [
    { name: 'Fan Command', unit: '', min: 0, max: 1 },
    { name: 'Valve Command', unit: '', min: 0, max: 1 },
    { name: 'Light Command', unit: '', min: 0, max: 1 },
    { name: 'Pump Command', unit: '', min: 0, max: 1 }
  ]
}

const generatePointData = () => {
  const devices = ['AHU-01', 'AHU-02', 'FCU-01', 'FCU-02', 'CH-01', 'VAV-01', 'VAV-02', 'RTU-01']
  const points = []

  for (let i = 0; i < 85; i++) {
    const pointType = ['AI', 'AO', 'DI', 'DO'][Math.floor(Math.random() * 4)] as keyof typeof pointNamesMap
    const nameConfig = pointNamesMap[pointType][Math.floor(Math.random() * pointNamesMap[pointType].length)]
    const deviceId = devices[Math.floor(Math.random() * devices.length)]
    const isOnline = Math.random() > 0.12
    const quality = isOnline && Math.random() > 0.08 ? 'good' : 'bad'
    const status = quality === 'bad' ? 'alarm' : (isOnline ? 'online' : 'offline')

    let realValue
    if (pointType === 'DI' || pointType === 'DO') {
      realValue = Math.random() > 0.6 ? 1 : 0
    } else {
      realValue = Number((nameConfig.min + Math.random() * (nameConfig.max - nameConfig.min)).toFixed(1))
    }

    points.push({
      id: i + 1,
      pointId: `${pointType}_${String(i + 1001)}`,
      deviceId: deviceId,
      bacAddr: `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 128)}`,
      pointName: nameConfig.name,
      pointType: pointType,
      realValue: realValue,
      unit: nameConfig.unit,
      status: status,
      quality: quality,
      updateTime: new Date().toLocaleString()
    })
  }

  allTableData.value = points
  pageInfo.total = points.length
  pageInfo.pageNum = 1
}

// 实时更新点数据
const startRealtimeUpdate = () => {
  realtimeTimer = window.setInterval(() => {
    // 更新趋势图
    appendTrendData()

    // 随机更新点值
    const updateCount = Math.floor(Math.random() * 5) + 3
    for (let i = 0; i < updateCount; i++) {
      const idx = Math.floor(Math.random() * allTableData.value.length)
      const point = allTableData.value[idx]
      if (point) {
        if (point.pointType === 'AI') {
          const config = pointNamesMap[point.pointType as keyof typeof pointNamesMap]?.find(p => p.name === point.pointName)
          if (config) {
            point.realValue = Number((config.min + Math.random() * (config.max - config.min)).toFixed(1))
          }
        } else if (point.pointType === 'AO') {
          point.realValue = Number((Math.random() * 100).toFixed(0))
        } else {
          point.realValue = Math.random() > 0.7 ? 1 : 0
        }

        point.status = Math.random() > 0.12 ? 'online' : (Math.random() > 0.5 ? 'offline' : 'alarm')
        point.quality = point.status === 'online' && Math.random() > 0.05 ? 'good' : 'bad'
        point.updateTime = new Date().toLocaleString()
      }
    }
  }, 4000)
}

// ========== Helper Functions ==========
const getPointTypeTag = (type: string) => {
  const map: Record<string, string> = { AI: 'primary', AO: 'success', DI: 'warning', DO: 'info' }
  return map[type] || ''
}

const getValColor = (row: any) => {
  if (row.status === 'alarm') return 'text-danger'
  if (row.pointType === 'AI') {
    const val = row.realValue
    if (val > 30 || val < 18) return 'text-danger'
    if (val > 28 || val < 20) return 'text-warning'
    return 'text-success'
  }
  return ''
}

const handleSearch = () => {
  pageInfo.pageNum = 1
}

const resetFilter = () => {
  filterForm.deviceCode = ''
  filterForm.pointType = ''
  filterForm.pointName = ''
  filterForm.status = ''
  pageInfo.pageNum = 1
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  generatePointData()
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => {
  pageInfo.pageNum = 1
}

const handlePageChange = () => {
  // Page changed
}

const viewDetail = (row: any) => {
  ElMessage.info(`Viewing details for point: ${row.pointId}`)
}

const manualSet = (row: any) => {
  ElMessage.info(`Setting value for point: ${row.pointName}`)
}

// ========== Lifecycle ==========
onMounted(async () => {
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

  setTimeout(async () => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(async () => {
      generatePointData()
      isLoaded.value = true
      await nextTick()

      // 确保 DOM 完全渲染后再初始化图表
      setTimeout(async () => {
        await initChart()
        startRealtimeUpdate()
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (realtimeTimer) clearInterval(realtimeTimer)
  if (trendInstance) {
    trendInstance.dispose()
    trendInstance = null
  }
  window.removeEventListener('resize', handleChartResize)
})
</script>

<style scoped lang="scss">
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

/* Page Content Style */
.bacnet-point-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

/* Stats Cards */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon .el-icon {
  font-size: 32px;
  color: #3b82f6;
}

.stat-card.success .stat-icon .el-icon { color: #67c23a; }
.stat-card.warning .stat-icon .el-icon { color: #e6a23c; }
.stat-card.info .stat-icon .el-icon { color: #409eff; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

.stat-percent {
  font-size: 20px;
  font-weight: 600;
  color: #67c23a;
}

/* Filter Card */
.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-card :deep(.el-card__body) {
  padding: 20px;
}

.filter-card :deep(.el-form) {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px;
}

.filter-card :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-card :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  padding-bottom: 4px;
}

/* Split Row */
.split-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card,
.flow-card {
  flex: 1;
  border-radius: 12px;
}

.card-header-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-box {
  width: 100%;
  height: 360px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
}

.legend-dot.temp { background: #f56c6c; }
.legend-dot.humidity { background: #409eff; }
.legend-dot.pressure { background: #67c23a; }

.topology-container {
  width: 100%;
  height: 400px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafbfc;
  overflow: hidden;
}

.flow-wrap {
  width: 100%;
  height: 100%;
  background: #fafbfc;
}

/* Flow Node Style */
.flow-node {
  padding: 8px 12px;
  border-radius: 10px;
  border: 2px solid;
  background: white;
  min-width: 130px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.flow-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.flow-node.online { border-color: #67c23a; background: linear-gradient(135deg, #f0f9eb, #e8f5e9); }
.flow-node.warning { border-color: #e6a23c; background: linear-gradient(135deg, #fdf6ec, #fef0e6); }
.flow-node.offline { border-color: #f56c6c; background: linear-gradient(135deg, #fef0f0, #fce4e4); opacity: 0.8; }

.node-icon .el-icon { font-size: 20px; margin-bottom: 4px; }
.node-title { font-weight: 700; font-size: 13px; color: #1e293b; }
.node-desc { font-size: 10px; color: #64748b; margin: 4px 0; }
.node-status { font-size: 10px; display: flex; align-items: center; justify-content: center; gap: 6px; }

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.warning { background: #e6a23c; box-shadow: 0 0 4px #e6a23c; }
.status-dot.offline { background: #f56c6c; box-shadow: 0 0 4px #f56c6c; }
.status-dot.alarm { background: #f56c6c; box-shadow: 0 0 4px #f56c6c; animation: pulseRed 1s infinite; }

@keyframes pulseRed {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.value-cell {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.value-cell .unit {
  font-size: 11px;
  color: #94a3b8;
}

.text-danger { color: #f56c6c; font-weight: 600; }
.text-warning { color: #e6a23c; font-weight: 600; }
.text-success { color: #67c23a; font-weight: 600; }

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

/* VueFlow 样式 */
:deep(.vue-flow__edge-path) {
  stroke: #409eff;
  stroke-width: 2;
}

:deep(.vue-flow__edge.animated .vue-flow__edge-path) {
  stroke-dasharray: 5;
  animation: dashdraw 0.5s linear infinite;
}

@keyframes dashdraw {
  from { stroke-dashoffset: 10; }
  to { stroke-dashoffset: 0; }
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .split-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .bacnet-point-container {
    padding: 12px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
  }

  .filter-card :deep(.el-form) {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-card :deep(.el-form-item) {
    width: 100%;
  }

  .filter-card :deep(.el-input),
  .filter-card :deep(.el-select) {
    width: 100% !important;
  }

  .chart-box {
    height: 280px;
  }

  .topology-container {
    height: 500px;
  }
}
</style>