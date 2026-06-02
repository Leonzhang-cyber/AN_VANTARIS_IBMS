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
        <div class="loading-tip">MODBUS POINT MODULE</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="modbus-point-container">
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
        <el-form-item label="Device ID">
          <el-input v-model="filterForm.deviceId" placeholder="Input Device ID" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="Slave ID">
          <el-input v-model="filterForm.slaveId" placeholder="Input Slave ID" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="Function Code">
          <el-select v-model="filterForm.functionCode" placeholder="Select Function" clearable style="width: 140px">
            <el-option label="01 - Coil Status" value="01" />
            <el-option label="02 - Input Status" value="02" />
            <el-option label="03 - Holding Register" value="03" />
            <el-option label="04 - Input Register" value="04" />
          </el-select>
        </el-form-item>
        <el-form-item label="Point Type">
          <el-select v-model="filterForm.pointType" placeholder="Select Type" clearable style="width: 140px">
            <el-option label="Coil (DO)" value="coil" />
            <el-option label="Discrete Input (DI)" value="discrete" />
            <el-option label="Holding Register (AO)" value="holding" />
            <el-option label="Input Register (AI)" value="input" />
          </el-select>
        </el-form-item>
        <el-form-item label="Point Name">
          <el-input v-model="filterForm.pointName" placeholder="Search point name" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetFilter">Reset</el-button>
          <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
          <el-button type="success" :icon="Plus" @click="openAddPointDialog">Add Point</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span>Modbus Real-Time Value Trend</span>
            <el-select v-model="trendPointId" placeholder="Select Point" size="small" style="width: 200px" @change="updateTrendChart">
              <el-option v-for="point in analogPoints" :key="point.id" :label="point.pointName" :value="point.id" />
            </el-select>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-box"></div>
      </el-card>

      <el-card class="stats-chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">Point Type Distribution</div>
        </template>
        <div ref="pieChartRef" class="pie-chart-box"></div>
      </el-card>
    </div>

    <!-- Modbus点列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Modbus Points List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="450" v-loading="tableLoading">
        <el-table-column label="Point ID" prop="pointId" width="100" />
        <el-table-column label="Device ID" prop="deviceId" width="100" />
        <el-table-column label="Slave ID" prop="slaveId" width="80" />
        <el-table-column label="Address" prop="address" width="80" />
        <el-table-column label="Function" prop="functionCode" width="100">
          <template #default="scope">
            <el-tag size="small">{{ getFunctionLabel(scope.row.functionCode) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Point Name" prop="pointName" min-width="180" show-overflow-tooltip />
        <el-table-column label="Type" prop="pointType" width="100">
          <template #default="scope">
            <el-tag :type="getPointTypeTag(scope.row.pointType)" size="small">{{ scope.row.pointType.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Data Type" prop="dataType" width="100" />
        <el-table-column label="Current Value" prop="value" width="120">
          <template #default="scope">
            <div class="value-cell">
              <span :class="getValColor(scope.row)">{{ scope.row.value }}</span>
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
        <el-table-column label="Last Read" prop="lastRead" width="160" />
        <el-table-column label="Operation" width="140" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="writeValue(scope.row)">Write</el-button>
            <el-button text type="danger" size="small" @click="pollNow(scope.row)">Poll</el-button>
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

    <!-- 写入值对话框 -->
    <el-dialog v-model="writeDialogVisible" title="Write Value" width="400px">
      <el-form :model="writeForm" label-width="100px">
        <el-form-item label="Point Name">
          <span>{{ selectedPoint?.pointName }}</span>
        </el-form-item>
        <el-form-item label="Current Value">
          <span>{{ selectedPoint?.value }} {{ selectedPoint?.unit }}</span>
        </el-form-item>
        <el-form-item label="New Value" required>
          <el-input-number
              v-if="selectedPoint?.dataType !== 'boolean'"
              v-model="writeForm.value"
              :step="selectedPoint?.dataType === 'float' ? 0.1 : 1"
              style="width: 100%"
          />
          <el-switch v-else v-model="writeForm.value" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="writeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmWrite" :loading="writing">Write</el-button>
      </template>
    </el-dialog>

    <!-- 添加点对话框 -->
    <el-dialog v-model="addDialogVisible" title="Add Modbus Point" width="550px">
      <el-form :model="addForm" :rules="addFormRules" ref="addFormRef" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Device ID" prop="deviceId">
              <el-input v-model="addForm.deviceId" placeholder="e.g., PLC-01" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Slave ID" prop="slaveId">
              <el-input-number v-model="addForm.slaveId" :min="1" :max="247" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Address" prop="address">
              <el-input-number v-model="addForm.address" :min="0" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Function Code" prop="functionCode">
              <el-select v-model="addForm.functionCode" placeholder="Select" style="width: 100%">
                <el-option label="01 - Read Coil" value="01" />
                <el-option label="02 - Read Discrete Input" value="02" />
                <el-option label="03 - Read Holding Register" value="03" />
                <el-option label="04 - Read Input Register" value="04" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Point Name" prop="pointName">
          <el-input v-model="addForm.pointName" placeholder="e.g., Temperature Sensor" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Data Type" prop="dataType">
              <el-select v-model="addForm.dataType" style="width: 100%">
                <el-option label="Boolean" value="boolean" />
                <el-option label="16-bit Integer" value="int16" />
                <el-option label="32-bit Integer" value="int32" />
                <el-option label="32-bit Float" value="float" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Unit" prop="unit">
              <el-input v-model="addForm.unit" placeholder="e.g., °C, kPa, %" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Scale Factor" prop="scale">
          <el-input-number v-model="addForm.scale" :step="0.1" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAdd" :loading="adding">Add Point</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { FormInstance, FormRules } from 'element-plus'
import { Connection, CircleCheckFilled, WarningFilled, DataLine, Refresh, Plus } from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading Modbus modules...',
  'Connecting to devices...',
  'Initializing real-time stream...',
  'Almost ready...'
]

// ========== Chart References ==========
const trendChartRef = ref<HTMLDivElement | null>(null)
const pieChartRef = ref<HTMLDivElement | null>(null)
let trendInstance: echarts.ECharts | null = null
let pieInstance: echarts.ECharts | null = null
let realtimeTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const writing = ref(false)
const adding = ref(false)
const trendPointId = ref('')
const addFormRef = ref<FormInstance>()

// ========== Filter Form ==========
const filterForm = reactive({
  deviceId: '',
  slaveId: '',
  functionCode: '',
  pointType: '',
  pointName: ''
})

// ========== Pagination ==========
const pageInfo = reactive({
  pageNum: 1,
  pageSize: 15,
  total: 0
})

// ========== Dialog State ==========
const writeDialogVisible = ref(false)
const addDialogVisible = ref(false)
const selectedPoint = ref<any>(null)
const writeForm = ref({ value: 0 })

const addForm = reactive({
  deviceId: '',
  slaveId: 1,
  address: 0,
  functionCode: '03',
  pointName: '',
  dataType: 'int16',
  unit: '',
  scale: 1.0
})

const addFormRules: FormRules = {
  deviceId: [{ required: true, message: 'Please enter device ID', trigger: 'blur' }],
  pointName: [{ required: true, message: 'Please enter point name', trigger: 'blur' }]
}

// ========== Table Data ==========
const allTableData = ref<any[]>([])

// 统计数据
const totalPoints = computed(() => allTableData.value.length)
const onlinePoints = computed(() => allTableData.value.filter(item => item.status === 'online').length)
const alarmPoints = computed(() => allTableData.value.filter(item => item.status === 'alarm').length)
const onlinePercent = computed(() => totalPoints.value ? Math.round(onlinePoints.value / totalPoints.value * 100) : 0)
const avgValue = computed(() => {
  const analogPoints = allTableData.value.filter(item => (item.pointType === 'holding' || item.pointType === 'input') && typeof item.value === 'number')
  if (analogPoints.length === 0) return 0
  const sum = analogPoints.reduce((s, item) => s + item.value, 0)
  return sum / analogPoints.length
})

// 模拟量点列表（用于趋势图）
const analogPoints = computed(() =>
    allTableData.value.filter(p => (p.pointType === 'holding' || p.pointType === 'input') && p.dataType !== 'boolean')
)

// 分页数据
const paginatedTableData = computed(() => {
  let filtered = [...allTableData.value]

  if (filterForm.deviceId) {
    filtered = filtered.filter(item => item.deviceId?.toLowerCase().includes(filterForm.deviceId.toLowerCase()))
  }
  if (filterForm.slaveId) {
    filtered = filtered.filter(item => String(item.slaveId).includes(filterForm.slaveId))
  }
  if (filterForm.functionCode) {
    filtered = filtered.filter(item => item.functionCode === filterForm.functionCode)
  }
  if (filterForm.pointType) {
    filtered = filtered.filter(item => item.pointType === filterForm.pointType)
  }
  if (filterForm.pointName) {
    filtered = filtered.filter(item => item.pointName?.toLowerCase().includes(filterForm.pointName.toLowerCase()))
  }

  pageInfo.total = filtered.length
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return filtered.slice(start, start + pageInfo.pageSize)
})

// ========== 生成模拟数据 ==========
const generateModbusPoints = () => {
  const devices = ['PLC-01', 'PLC-02', 'RTU-01', 'RTU-02', 'Gateway-01']
  const points = []

  const pointTemplates = [
    { type: 'holding', name: 'Temperature Sensor', unit: '°C', min: 18, max: 35, func: '03', dataType: 'float' },
    { type: 'holding', name: 'Pressure Transmitter', unit: 'kPa', min: 80, max: 120, func: '03', dataType: 'float' },
    { type: 'holding', name: 'Flow Meter', unit: 'm³/h', min: 0, max: 500, func: '03', dataType: 'int32' },
    { type: 'holding', name: 'Valve Position', unit: '%', min: 0, max: 100, func: '03', dataType: 'int16' },
    { type: 'input', name: 'Power Meter', unit: 'kW', min: 0, max: 150, func: '04', dataType: 'float' },
    { type: 'input', name: 'Frequency', unit: 'Hz', min: 45, max: 55, func: '04', dataType: 'float' },
    { type: 'input', name: 'Energy Counter', unit: 'kWh', min: 1000, max: 50000, func: '04', dataType: 'int32' },
    { type: 'coil', name: 'Motor Start', unit: '', min: 0, max: 1, func: '01', dataType: 'boolean' },
    { type: 'coil', name: 'Valve Open', unit: '', min: 0, max: 1, func: '01', dataType: 'boolean' },
    { type: 'discrete', name: 'Limit Switch', unit: '', min: 0, max: 1, func: '02', dataType: 'boolean' }
  ]

  let id = 1
  for (const device of devices) {
    const slaveId = Math.floor(Math.random() * 100) + 1
    const pointCount = Math.floor(Math.random() * 12) + 8

    for (let i = 0; i < pointCount; i++) {
      const template = pointTemplates[Math.floor(Math.random() * pointTemplates.length)]
      const address = Math.floor(Math.random() * 100)
      const isOnline = Math.random() > 0.1
      const isAlarm = !isOnline || (Math.random() > 0.85)
      const status = isAlarm ? 'alarm' : (isOnline ? 'online' : 'offline')

      let value
      if (template.dataType === 'boolean') {
        value = Math.random() > 0.5 ? 1 : 0
      } else if (template.dataType === 'int16') {
        value = Math.floor(template.min + Math.random() * (template.max - template.min))
      } else {
        value = Number((template.min + Math.random() * (template.max - template.min)).toFixed(1))
      }

      points.push({
        id: id++,
        pointId: `MB_${String(id).padStart(4, '0')}`,
        deviceId: device,
        slaveId: slaveId,
        address: address,
        functionCode: template.func,
        pointName: `${device} ${template.name}`,
        pointType: template.type,
        dataType: template.dataType,
        value: value,
        unit: template.unit,
        status: status,
        lastRead: new Date().toLocaleString(),
        scale: 1.0
      })
    }
  }

  allTableData.value = points
  if (analogPoints.value.length > 0) {
    trendPointId.value = analogPoints.value[0].id
  }
}

// 更新点值
const updatePointValues = () => {
  for (const point of allTableData.value) {
    if (point.status === 'online') {
      if (point.dataType === 'boolean') {
        point.value = Math.random() > 0.7 ? 1 : 0
      } else if (point.dataType === 'int16') {
        const change = (Math.random() - 0.5) * 2
        point.value = Math.max(0, Math.min(100, Math.floor(point.value + change)))
      } else {
        const change = (Math.random() - 0.5) * 1.5
        let newVal = point.value + change
        if (point.pointName.includes('Temperature')) {
          newVal = Math.max(18, Math.min(35, newVal))
        } else if (point.pointName.includes('Pressure')) {
          newVal = Math.max(80, Math.min(120, newVal))
        } else if (point.pointName.includes('Power')) {
          newVal = Math.max(0, Math.min(150, newVal))
        } else {
          newVal = Math.max(0, newVal)
        }
        point.value = Number(newVal.toFixed(1))
      }
      point.lastRead = new Date().toLocaleString()
      point.status = Math.random() > 0.95 ? 'alarm' : 'online'
    }
  }
}

// ========== Chart Data ==========
const trendHistory = ref<{ timestamps: string[]; values: number[] }>({
  timestamps: [],
  values: []
})

// 生成趋势历史数据
const generateTrendHistory = () => {
  const timestamps = []
  const values = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)
    values.push(Number((20 + Math.random() * 15).toFixed(1)))
  }

  trendHistory.value = { timestamps, values }
}

// 获取当前选中点的历史数据
const getPointHistory = () => {
  const point = analogPoints.value.find(p => p.id === trendPointId.value)
  if (!point) return

  const timestamps = []
  const values = []
  const now = new Date()
  const baseValue = typeof point.value === 'number' ? point.value : 50
  const range = point.pointName.includes('Temperature') ? 8 :
      point.pointName.includes('Pressure') ? 15 :
          point.pointName.includes('Power') ? 30 : 20

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)
    const variation = (Math.sin(i * 0.3) * (range / 2)) + (Math.random() - 0.5) * 2
    values.push(Number((baseValue + variation).toFixed(1)))
  }

  trendHistory.value = { timestamps, values }
}

// 添加新数据点到趋势图
const appendTrendData = () => {
  const point = analogPoints.value.find(p => p.id === trendPointId.value)
  if (!point) return

  const now = new Date()
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:00`
  const newValue = typeof point.value === 'number' ? point.value : 50

  trendHistory.value.timestamps.push(timeStr)
  trendHistory.value.values.push(newValue)

  if (trendHistory.value.timestamps.length > 48) {
    trendHistory.value.timestamps.shift()
    trendHistory.value.values.shift()
  }

  updateTrendChart()
}

// 初始化趋势图
const initTrendChart = async () => {
  await nextTick()
  if (!trendChartRef.value) {
    setTimeout(() => initTrendChart(), 100)
    return
  }

  if (trendInstance) {
    trendInstance.dispose()
    trendInstance = null
  }

  getPointHistory()

  trendInstance = echarts.init(trendChartRef.value)
  updateTrendChart()
  window.addEventListener('resize', handleChartResize)
}

const updateTrendChart = () => {
  if (!trendInstance || !trendHistory.value.timestamps.length) return

  const point = analogPoints.value.find(p => p.id === trendPointId.value)
  const unit = point?.unit || ''

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        return `${params[0].axisValue}<br/>Value: ${params[0].value} ${unit}`
      }
    },
    grid: { left: '8%', right: '5%', top: '12%', bottom: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: trendHistory.value.timestamps,
      axisLabel: { rotate: 45, interval: 4, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      name: `Value (${unit})`,
      nameTextStyle: { fontSize: 12 }
    },
    series: [{
      name: point?.pointName || 'Value',
      type: 'line',
      data: trendHistory.value.values,
      smooth: true,
      lineStyle: { color: '#409eff', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle',
      symbolSize: 5,
      itemStyle: { color: '#409eff' }
    }]
  }
  trendInstance.setOption(option, true)
}

// 初始化饼图
const initPieChart = async () => {
  await nextTick()
  if (!pieChartRef.value) {
    setTimeout(() => initPieChart(), 100)
    return
  }

  if (pieInstance) {
    pieInstance.dispose()
    pieInstance = null
  }

  pieInstance = echarts.init(pieChartRef.value)

  const coilCount = allTableData.value.filter(p => p.pointType === 'coil').length
  const discreteCount = allTableData.value.filter(p => p.pointType === 'discrete').length
  const holdingCount = allTableData.value.filter(p => p.pointType === 'holding').length
  const inputCount = allTableData.value.filter(p => p.pointType === 'input').length

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['Coil (DO)', 'Discrete Input (DI)', 'Holding Register (AO)', 'Input Register (AI)'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'Coil (DO)', value: coilCount, itemStyle: { color: '#f56c6c' } },
        { name: 'Discrete Input (DI)', value: discreteCount, itemStyle: { color: '#e6a23c' } },
        { name: 'Holding Register (AO)', value: holdingCount, itemStyle: { color: '#409eff' } },
        { name: 'Input Register (AI)', value: inputCount, itemStyle: { color: '#67c23a' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}', position: 'outside' }
    }]
  }
  pieInstance.setOption(option)
}

const updatePieChart = () => {
  if (!pieInstance) return

  const coilCount = allTableData.value.filter(p => p.pointType === 'coil').length
  const discreteCount = allTableData.value.filter(p => p.pointType === 'discrete').length
  const holdingCount = allTableData.value.filter(p => p.pointType === 'holding').length
  const inputCount = allTableData.value.filter(p => p.pointType === 'input').length

  pieInstance.setOption({
    series: [{
      data: [
        { name: 'Coil (DO)', value: coilCount },
        { name: 'Discrete Input (DI)', value: discreteCount },
        { name: 'Holding Register (AO)', value: holdingCount },
        { name: 'Input Register (AI)', value: inputCount }
      ]
    }]
  })
}

const handleChartResize = () => {
  if (trendInstance) trendInstance.resize()
  if (pieInstance) pieInstance.resize()
}

// ========== Helper Functions ==========
const getFunctionLabel = (func: string) => {
  const labels: Record<string, string> = {
    '01': 'Read Coil',
    '02': 'Read Input',
    '03': 'Read Holding',
    '04': 'Read Input'
  }
  return labels[func] || func
}

const getPointTypeTag = (type: string) => {
  const map: Record<string, string> = { coil: 'danger', discrete: 'warning', holding: 'primary', input: 'success' }
  return map[type] || 'info'
}

const getValColor = (row: any) => {
  if (row.status === 'alarm') return 'text-danger'
  if (row.pointType === 'holding' || row.pointType === 'input') {
    const val = row.value
    if (row.pointName.includes('Temperature')) {
      if (val > 30 || val < 18) return 'text-danger'
      if (val > 28 || val < 20) return 'text-warning'
    }
    if (row.pointName.includes('Pressure')) {
      if (val > 115 || val < 85) return 'text-danger'
      if (val > 110 || val < 90) return 'text-warning'
    }
  }
  return ''
}

// ========== Actions ==========
const handleSearch = () => { pageInfo.pageNum = 1 }
const resetFilter = () => {
  filterForm.deviceId = ''
  filterForm.slaveId = ''
  filterForm.functionCode = ''
  filterForm.pointType = ''
  filterForm.pointName = ''
  pageInfo.pageNum = 1
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  generateModbusPoints()
  updatePieChart()
  if (analogPoints.value.length > 0 && !trendPointId.value) {
    trendPointId.value = analogPoints.value[0].id
    getPointHistory()
    updateTrendChart()
  }
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pageInfo.pageNum = 1 }
const handlePageChange = () => {}

const viewDetail = (row: any) => {
  ElMessage.info(`Viewing details for point: ${row.pointId}`)
}

const writeValue = (row: any) => {
  selectedPoint.value = row
  writeForm.value.value = row.value
  writeDialogVisible.value = true
}

const confirmWrite = async () => {
  writing.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  if (selectedPoint.value) {
    selectedPoint.value.value = writeForm.value.value
    selectedPoint.value.lastRead = new Date().toLocaleString()
    ElMessage.success(`Value written to ${selectedPoint.value.pointName}`)
  }
  writeDialogVisible.value = false
  writing.value = false
}

const pollNow = (row: any) => {
  ElMessage.info(`Polling ${row.pointName}...`)
  setTimeout(() => {
    if (row.dataType === 'boolean') {
      row.value = Math.random() > 0.5 ? 1 : 0
    } else {
      const change = (Math.random() - 0.5) * 2
      row.value = Number((row.value + change).toFixed(1))
    }
    row.lastRead = new Date().toLocaleString()
    ElMessage.success(`Polled ${row.pointName}: ${row.value} ${row.unit}`)
  }, 500)
}

const openAddPointDialog = () => {
  addForm.deviceId = ''
  addForm.slaveId = 1
  addForm.address = 0
  addForm.functionCode = '03'
  addForm.pointName = ''
  addForm.dataType = 'int16'
  addForm.unit = ''
  addForm.scale = 1.0
  addDialogVisible.value = true
}

const confirmAdd = async () => {
  if (!addFormRef.value) return
  await addFormRef.value.validate(async (valid) => {
    if (valid) {
      adding.value = true
      await new Promise(resolve => setTimeout(resolve, 800))

      const newPoint = {
        id: allTableData.value.length + 1,
        pointId: `MB_${String(allTableData.value.length + 1).padStart(4, '0')}`,
        deviceId: addForm.deviceId,
        slaveId: addForm.slaveId,
        address: addForm.address,
        functionCode: addForm.functionCode,
        pointName: addForm.pointName,
        pointType: addForm.functionCode === '01' ? 'coil' : addForm.functionCode === '02' ? 'discrete' : addForm.functionCode === '03' ? 'holding' : 'input',
        dataType: addForm.dataType,
        value: addForm.dataType === 'boolean' ? 0 : 0,
        unit: addForm.unit,
        status: 'online',
        lastRead: new Date().toLocaleString(),
        scale: addForm.scale
      }

      allTableData.value.unshift(newPoint)
      updatePieChart()
      addDialogVisible.value = false
      adding.value = false
      ElMessage.success('Point added successfully')
    }
  })
}

// 实时更新
const startRealtimeUpdates = () => {
  realtimeTimer = window.setInterval(() => {
    updatePointValues()
    appendTrendData()
    // 随机更新几个点的值
    const updateCount = Math.floor(Math.random() * 5) + 2
    for (let i = 0; i < updateCount; i++) {
      const idx = Math.floor(Math.random() * allTableData.value.length)
      const point = allTableData.value[idx]
      if (point && point.status === 'online') {
        if (point.dataType === 'boolean') {
          point.value = Math.random() > 0.7 ? 1 : 0
        } else {
          const change = (Math.random() - 0.5) * 2
          point.value = Number((point.value + change).toFixed(1))
        }
        point.lastRead = new Date().toLocaleString()
      }
    }
  }, 3000)
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
      generateModbusPoints()
      isLoaded.value = true
      await nextTick()

      setTimeout(async () => {
        await initTrendChart()
        await initPieChart()
        startRealtimeUpdates()
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (realtimeTimer) clearInterval(realtimeTimer)
  if (trendInstance) trendInstance.dispose()
  if (pieInstance) pieInstance.dispose()
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

/* Page Content */
.modbus-point-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

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

.stat-info { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }
.stat-percent { font-size: 20px; font-weight: 600; color: #67c23a; }

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

.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card, .stats-chart-card {
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

.chart-box, .pie-chart-box {
  width: 100%;
  height: 320px;
}

.status-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.alarm { background: #f56c6c; box-shadow: 0 0 4px #f56c6c; animation: pulseRed 1s infinite; }

@keyframes pulseRed {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
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

@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .modbus-point-container {
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
  .chart-box, .pie-chart-box {
    height: 250px;
  }
}
</style>