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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Cooling Alarms Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cooling-alarms-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <div class="title-icon cooling-icon">
            <el-icon><CircleClose /></el-icon>
          </div>
          Cooling Alarms
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalUnits }} Cooling Units
          </div>
          <div class="stat-badge critical">
            <span class="pulse-dot"></span>
            {{ criticalCount }} Critical
          </div>
          <div class="stat-badge warning">
            {{ warningCount }} Warning
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
      </div>
    </div>

    <!-- Temperature Overview Cards -->
    <div class="temp-overview">
      <div class="temp-card overall">
        <div class="temp-card-inner">
          <div class="temp-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="temp-stats">
            <div class="temp-label">Average Inlet Temp</div>
            <div class="temp-value">{{ avgInletTemp }}<span class="unit">°C</span></div>
            <div class="temp-status" :class="avgInletTemp > 25 ? 'warning' : 'normal'">
              {{ avgInletTemp > 25 ? '⚠️ Above ASHRAE' : '✅ Within Range' }}
            </div>
          </div>
          <div class="temp-gauge">
            <el-progress type="circle" :percentage="inletTempPercent" :color="getTempColor(avgInletTemp)" :width="70" :stroke-width="6">
              <template #default>{{ avgInletTemp }}°C</template>
            </el-progress>
          </div>
        </div>
      </div>

      <div class="temp-card hotspot">
        <div class="temp-card-inner">
          <div class="temp-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="temp-stats">
            <div class="temp-label">Hottest Zone</div>
            <div class="temp-value">{{ hottestZoneTemp }}<span class="unit">°C</span></div>
            <div class="temp-location">{{ hottestZoneName }}</div>
          </div>
          <div class="temp-badge">🔥</div>
        </div>
      </div>

      <div class="temp-card delta">
        <div class="temp-card-inner">
          <div class="temp-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="temp-stats">
            <div class="temp-label">Avg ΔT (Return - Supply)</div>
            <div class="temp-value">{{ avgDeltaT }}<span class="unit">°C</span></div>
            <div class="temp-status" :class="avgDeltaT < 8 ? 'warning' : 'normal'">
              {{ avgDeltaT < 8 ? '⚠️ Low Delta T' : '✅ Optimal' }}
            </div>
          </div>
          <div class="temp-badge">🌡️</div>
        </div>
      </div>

      <div class="temp-card humidity">
        <div class="temp-card-inner">
          <div class="temp-icon">
            <el-icon><Histogram /></el-icon>
          </div>
          <div class="temp-stats">
            <div class="temp-label">Average Humidity</div>
            <div class="temp-value">{{ avgHumidity }}<span class="unit">%</span></div>
            <div class="temp-status" :class="avgHumidity > 60 ? 'warning' : 'normal'">
              {{ avgHumidity > 60 ? '⚠️ High Humidity' : '✅ Normal' }}
            </div>
          </div>
          <div class="temp-badge">💧</div>
        </div>
      </div>
    </div>

    <!-- CRAC/CRAH Units Cards -->
    <div class="section-title">
      <span class="title-text">❄️ Cooling Units Status</span>
      <span class="title-badge">{{ filteredUnits.length }} Active Units</span>
    </div>

    <div class="cooling-grid">
      <div v-for="unit in filteredUnits" :key="unit.id" class="cooling-card" :class="unit.status">
        <div class="cooling-card-header">
          <div class="unit-name">
            <span class="unit-icon">❄️</span>
            {{ unit.name }}
          </div>
          <div class="unit-status-badge" :class="unit.status">
            <span class="status-dot"></span>
            {{ unit.statusText }}
          </div>
        </div>

        <div class="cooling-temp-section">
          <div class="temp-readings">
            <div class="temp-reading supply">
              <div class="reading-label">Supply Air</div>
              <div class="reading-value" :class="{ warning: unit.supplyTemp > 18 }">{{ unit.supplyTemp }}°C</div>
              <div class="reading-target">Target: 16-18°C</div>
            </div>
            <div class="temp-reading return">
              <div class="reading-label">Return Air</div>
              <div class="reading-value" :class="{ warning: unit.returnTemp > 28 }">{{ unit.returnTemp }}°C</div>
              <div class="reading-target">Target: 24-26°C</div>
            </div>
            <div class="temp-reading delta">
              <div class="reading-label">ΔT</div>
              <div class="reading-value" :class="{ warning: (unit.returnTemp - unit.supplyTemp) < 8 }">{{ unit.returnTemp - unit.supplyTemp }}°C</div>
              <div class="reading-target">Target: 8-12°C</div>
            </div>
          </div>
        </div>

        <div class="cooling-metrics">
          <div class="metric-row">
            <div class="metric-item">
              <span class="metric-label">Cooling Capacity</span>
              <div class="metric-bar">
                <div class="metric-bar-track">
                  <div class="metric-bar-fill" :style="{ width: unit.capacity + '%', background: getCapacityColor(unit.capacity) }"></div>
                </div>
                <span class="metric-value">{{ unit.capacity }}%</span>
              </div>
            </div>
            <div class="metric-item">
              <span class="metric-label">Fan Speed</span>
              <div class="metric-bar">
                <div class="metric-bar-track">
                  <div class="metric-bar-fill" :style="{ width: unit.fanSpeed + '%', background: getFanSpeedColor(unit.fanSpeed) }"></div>
                </div>
                <span class="metric-value">{{ unit.fanSpeed }}%</span>
              </div>
            </div>
          </div>
          <div class="metric-row">
            <div class="metric-item">
              <span class="metric-label">Water/Glycol Supply</span>
              <div class="metric-bar">
                <div class="metric-bar-track">
                  <div class="metric-bar-fill" :style="{ width: unit.waterSupplyTempPercent, background: '#60a5fa' }"></div>
                </div>
                <span class="metric-value">{{ unit.waterSupplyTemp }}°C</span>
              </div>
            </div>
            <div class="metric-item">
              <span class="metric-label">Water/Glycol Return</span>
              <div class="metric-bar">
                <div class="metric-bar-track">
                  <div class="metric-bar-fill" :style="{ width: unit.waterReturnTempPercent, background: '#f97316' }"></div>
                </div>
                <span class="metric-value">{{ unit.waterReturnTemp }}°C</span>
              </div>
            </div>
          </div>
        </div>

        <div class="cooling-footer">
          <div class="footer-info">
            <span>⚡ Power: {{ unit.power }} kW</span>
            <span>💧 Flow: {{ unit.waterFlow }} m³/h</span>
            <span>⚠️ {{ unit.alarmCount }} alarms</span>
          </div>
          <el-button type="primary" link size="small" @click="viewUnitDetails(unit)">
            Details →
          </el-button>
        </div>
      </div>
    </div>

    <!-- Active Cooling Alarms -->
    <div class="section-title">
      <span class="title-text">🚨 Active Cooling Alarms</span>
      <span class="title-badge critical">{{ activeAlarmsCount }} Active</span>
    </div>

    <div class="alarms-container">
      <div v-for="alarm in activeAlarms" :key="alarm.id" class="alarm-card" :class="alarm.severity">
        <div class="alarm-icon">
          <span v-if="alarm.severity === 'critical'">🔴</span>
          <span v-else-if="alarm.severity === 'major'">🟠</span>
          <span v-else>🟡</span>
        </div>
        <div class="alarm-content">
          <div class="alarm-title">{{ alarm.title }}</div>
          <div class="alarm-description">{{ alarm.description }}</div>
          <div class="alarm-meta">
            <span>❄️ {{ alarm.unitName }}</span>
            <span>⏱️ {{ alarm.time }}</span>
            <span>📊 {{ alarm.value }}</span>
          </div>
        </div>
        <div class="alarm-actions">
          <el-button size="small" type="primary" plain @click="acknowledgeAlarm(alarm)">
            Acknowledge
          </el-button>
          <el-button size="small" type="danger" plain @click="escalateAlarm(alarm)">
            Escalate
          </el-button>
        </div>
      </div>
      <div v-if="activeAlarms.length === 0" class="empty-alarms">
        <el-empty description="No active cooling alarms" :image-size="80" />
      </div>
    </div>

    <!-- Temperature Trend Chart -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          Temperature & Humidity Trend (Last 24 Hours)
        </div>
        <el-radio-group v-model="trendPeriod" size="small">
          <el-radio-button label="hour">Hourly</el-radio-button>
          <el-radio-button label="day">Daily</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="trendChartRef" class="chart-container"></div>
    </div>

    <!-- Unit Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Cooling Unit Details - ${selectedUnit?.name}`" width="650px">
      <el-descriptions :column="2" border v-if="selectedUnit">
        <el-descriptions-item label="Unit Name">{{ selectedUnit.name }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTagType(selectedUnit.status)">{{ selectedUnit.statusText }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Supply Air Temp">{{ selectedUnit.supplyTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Return Air Temp">{{ selectedUnit.returnTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Delta T">{{ selectedUnit.returnTemp - selectedUnit.supplyTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Cooling Capacity">{{ selectedUnit.capacity }}%</el-descriptions-item>
        <el-descriptions-item label="Fan Speed">{{ selectedUnit.fanSpeed }}%</el-descriptions-item>
        <el-descriptions-item label="Water Supply Temp">{{ selectedUnit.waterSupplyTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Water Return Temp">{{ selectedUnit.waterReturnTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Water Flow">{{ selectedUnit.waterFlow }} m³/h</el-descriptions-item>
        <el-descriptions-item label="Power Consumption">{{ selectedUnit.power }} kW</el-descriptions-item>
        <el-descriptions-item label="Installation Date">{{ selectedUnit.installDate }}</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">{{ selectedUnit.lastMaintenance }}</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance Due">{{ selectedUnit.nextMaintenance }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
// import { Snowflake, Grid, Refresh, Download, Thermometer, Fire, Connection, WaterRate, TrendCharts } from '@element-plus/icons-vue'
import {
  Grid,
  Refresh,
  Download,
  Connection,
  TrendCharts,
  Warning,
  Histogram,
  CircleClose,
  Clock
} from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading cooling units...',
  'Analyzing temperature data...',
  'Checking alarm status...',
  'Almost ready...'
]

// ==================== Data State ====================
const trendPeriod = ref('hour')
const detailDialogVisible = ref(false)
const selectedUnit = ref<any>(null)

// Cooling Unit Data
interface CoolingUnit {
  id: number
  name: string
  status: 'critical' | 'warning' | 'normal'
  statusText: string
  supplyTemp: number
  returnTemp: number
  capacity: number
  fanSpeed: number
  waterSupplyTemp: number
  waterReturnTemp: number
  waterSupplyTempPercent: number
  waterReturnTempPercent: number
  waterFlow: number
  power: number
  installDate: string
  lastMaintenance: string
  nextMaintenance: string
  alarmCount: number
}

const coolingUnits = ref<CoolingUnit[]>([
  { id: 1, name: 'CRAC-01 (Row A)', status: 'critical', statusText: 'Critical', supplyTemp: 22.5, returnTemp: 31.2, capacity: 95, fanSpeed: 92, waterSupplyTemp: 12.5, waterReturnTemp: 18.2, waterSupplyTempPercent: 62, waterReturnTempPercent: 45, waterFlow: 85, power: 42.5, installDate: '2021-03-15', lastMaintenance: '2024-05-10', nextMaintenance: '2024-08-10', alarmCount: 3 },
  { id: 2, name: 'CRAC-02 (Row A)', status: 'warning', statusText: 'Warning', supplyTemp: 19.8, returnTemp: 27.5, capacity: 78, fanSpeed: 75, waterSupplyTemp: 10.2, waterReturnTemp: 15.8, waterSupplyTempPercent: 51, waterReturnTempPercent: 39, waterFlow: 72, power: 35.2, installDate: '2021-03-15', lastMaintenance: '2024-05-10', nextMaintenance: '2024-08-10', alarmCount: 1 },
  { id: 3, name: 'CRAC-03 (Row B)', status: 'normal', statusText: 'Normal', supplyTemp: 17.2, returnTemp: 25.5, capacity: 62, fanSpeed: 58, waterSupplyTemp: 9.5, waterReturnTemp: 14.2, waterSupplyTempPercent: 47, waterReturnTempPercent: 35, waterFlow: 65, power: 28.5, installDate: '2022-01-20', lastMaintenance: '2024-04-15', nextMaintenance: '2024-07-15', alarmCount: 0 },
  { id: 4, name: 'CRAH-01 (Hot Aisle)', status: 'critical', statusText: 'Critical', supplyTemp: 23.5, returnTemp: 32.5, capacity: 98, fanSpeed: 96, waterSupplyTemp: 13.8, waterReturnTemp: 20.5, waterSupplyTempPercent: 69, waterReturnTempPercent: 51, waterFlow: 92, power: 48.2, installDate: '2020-11-10', lastMaintenance: '2024-05-20', nextMaintenance: '2024-08-20', alarmCount: 4 },
  { id: 5, name: 'CRAH-02 (Cold Aisle)', status: 'normal', statusText: 'Normal', supplyTemp: 16.5, returnTemp: 24.8, capacity: 55, fanSpeed: 52, waterSupplyTemp: 8.5, waterReturnTemp: 12.5, waterSupplyTempPercent: 42, waterReturnTempPercent: 31, waterFlow: 58, power: 24.8, installDate: '2022-06-05', lastMaintenance: '2024-05-25', nextMaintenance: '2024-08-25', alarmCount: 0 },
  { id: 6, name: 'InRow Cooling-01', status: 'warning', statusText: 'Warning', supplyTemp: 20.5, returnTemp: 28.5, capacity: 82, fanSpeed: 80, waterSupplyTemp: 11.2, waterReturnTemp: 16.5, waterSupplyTempPercent: 56, waterReturnTempPercent: 41, waterFlow: 78, power: 38.5, installDate: '2022-09-18', lastMaintenance: '2024-05-05', nextMaintenance: '2024-08-05', alarmCount: 2 },
  { id: 7, name: 'InRow Cooling-02', status: 'normal', statusText: 'Normal', supplyTemp: 17.8, returnTemp: 26.2, capacity: 68, fanSpeed: 65, waterSupplyTemp: 9.8, waterReturnTemp: 13.8, waterSupplyTempPercent: 49, waterReturnTempPercent: 34, waterFlow: 68, power: 30.2, installDate: '2022-09-18', lastMaintenance: '2024-05-05', nextMaintenance: '2024-08-05', alarmCount: 0 }
])

const totalUnits = computed(() => coolingUnits.value.length)
const criticalCount = computed(() => coolingUnits.value.filter(u => u.status === 'critical').length)
const warningCount = computed(() => coolingUnits.value.filter(u => u.status === 'warning').length)
const avgInletTemp = computed(() => (coolingUnits.value.reduce((sum, u) => sum + u.supplyTemp, 0) / coolingUnits.value.length).toFixed(1))
const inletTempPercent = computed(() => Math.min(100, (parseFloat(avgInletTemp.value) / 30) * 100))
const avgDeltaT = computed(() => {
  const sum = coolingUnits.value.reduce((sum, u) => sum + (u.returnTemp - u.supplyTemp), 0)
  return (sum / coolingUnits.value.length).toFixed(1)
})
const avgHumidity = ref(52)
const hottestZoneTemp = ref(34.2)
const hottestZoneName = ref('Hot Aisle - Row A Top')

const filteredUnits = computed(() => coolingUnits.value)

// Active Alarms
interface CoolingAlarm {
  id: number
  unitName: string
  title: string
  description: string
  severity: string
  value: string
  time: string
}

const activeAlarms = ref<CoolingAlarm[]>([
  { id: 1, unitName: 'CRAC-01 (Row A)', title: 'High Return Air Temperature', description: 'Return temperature exceeded 30°C threshold', severity: 'critical', value: 'Return: 31.2°C', time: '8 min ago' },
  { id: 2, unitName: 'CRAH-01 (Hot Aisle)', title: 'Cooling Capacity Critical', description: 'Cooling capacity near 100%', severity: 'critical', value: 'Capacity: 98%', time: '15 min ago' },
  { id: 3, unitName: 'CRAC-02 (Row A)', title: 'High Fan Speed', description: 'Fan running at high speed', severity: 'major', value: 'Fan Speed: 75%', time: '22 min ago' },
  { id: 4, unitName: 'InRow Cooling-01', title: 'Water Flow Low', description: 'Water flow below optimal level', severity: 'warning', value: 'Flow: 78 m³/h', time: '35 min ago' },
  { id: 5, unitName: 'CRAH-01 (Hot Aisle)', title: 'High Water Return Temp', description: 'Water return temperature elevated', severity: 'warning', value: 'Return: 20.5°C', time: '45 min ago' }
])

const activeAlarmsCount = computed(() => activeAlarms.value.length)

// Trend data
const hourlyTempData = ref<number[]>([22.5, 22.8, 23.1, 23.4, 23.8, 24.2, 25.0, 25.5, 26.0, 26.2, 25.8, 25.2, 24.5, 24.0, 23.8, 23.5, 23.2, 23.0, 22.8, 22.5, 22.2, 22.0, 21.8, 21.5])
const hourlyHumidityData = ref<number[]>([48, 49, 50, 51, 52, 53, 54, 55, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 43, 42, 41])
const dailyTempData = ref<number[]>([23.2, 23.5, 23.8, 24.1, 24.5, 24.8, 24.2])
const dailyHumidityData = ref<number[]>([50, 51, 52, 53, 52, 51, 50])
const hourLabels = ref<string[]>(Array.from({ length: 24 }, (_, i) => `${i}:00`))
const dayLabels = ref<string[]>(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

// ==================== Helper Functions ====================
const getTempColor = (temp: number) => {
  if (temp <= 22) return '#67c23a'
  if (temp <= 25) return '#e6a23c'
  return '#f56c6c'
}

const getCapacityColor = (capacity: number) => {
  if (capacity <= 70) return '#67c23a'
  if (capacity <= 85) return '#e6a23c'
  return '#f56c6c'
}

const getFanSpeedColor = (speed: number) => {
  if (speed <= 60) return '#67c23a'
  if (speed <= 80) return '#e6a23c'
  return '#f56c6c'
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    normal: 'success'
  }
  return map[status] || 'info'
}

const viewUnitDetails = (unit: CoolingUnit) => {
  selectedUnit.value = unit
  detailDialogVisible.value = true
}

const acknowledgeAlarm = (alarm: CoolingAlarm) => {
  ElMessageBox.confirm(`Acknowledge alarm "${alarm.title}"?`, 'Confirm', {
    confirmButtonText: 'Acknowledge',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = activeAlarms.value.findIndex(a => a.id === alarm.id)
    if (index > -1) {
      activeAlarms.value.splice(index, 1)
      ElMessage.success(`Alarm "${alarm.title}" acknowledged`)
    }
  }).catch(() => {})
}

const escalateAlarm = (alarm: CoolingAlarm) => {
  ElMessageBox.confirm(`Escalate alarm "${alarm.title}" to management?`, 'Confirm', {
    confirmButtonText: 'Escalate',
    cancelButtonText: 'Cancel',
    type: 'error'
  }).then(() => {
    ElMessage.success(`Alarm "${alarm.title}" escalated`)
  }).catch(() => {})
}

const exportReport = () => {
  ElMessage.success('Exporting report...')
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null

const initChart = () => {
  nextTick(() => {
    if (!trendChartRef.value) {
      setTimeout(initChart, 200)
      return
    }

    if (trendChart) trendChart.dispose()
    trendChart = echarts.init(trendChartRef.value)
    updateTrendChart()

    window.addEventListener('resize', () => trendChart?.resize())
  })
}

const updateTrendChart = () => {
  if (!trendChart) return

  const isHourly = trendPeriod.value === 'hour'
  const tempData = isHourly ? hourlyTempData.value : dailyTempData.value
  const humidityData = isHourly ? hourlyHumidityData.value : dailyHumidityData.value
  const labels = isHourly ? hourLabels.value : dayLabels.value

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperature (°C)', 'Humidity (%)'], textStyle: { color: '#606266' } },
    grid: { left: '8%', right: '8%', top: '15%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: isHourly ? 45 : 0, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: [
      { type: 'value', name: 'Temperature (°C)', min: 18, max: 30, axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
      { type: 'value', name: 'Humidity (%)', min: 30, max: 70, axisLabel: { color: '#606266' }, splitLine: { show: false } }
    ],
    series: [
      { name: 'Temperature (°C)', type: 'line', data: tempData, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, symbol: 'circle', symbolSize: 4, yAxisIndex: 0 },
      { name: 'Humidity (%)', type: 'line', data: humidityData, smooth: true, lineStyle: { color: '#60a5fa', width: 2 }, symbol: 'diamond', symbolSize: 4, yAxisIndex: 1 }
    ]
  })
}

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
      nextTick(() => {
        setTimeout(() => {
          initChart()
        }, 100)
      })
    }, 500)
  }, 2500)
}

watch(trendPeriod, () => {
  updateTrendChart()
})

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
})
</script>

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

/* ==================== Main Dashboard Styles ==================== */
.cooling-alarms-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f5 100%);
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
  margin: 0;
}

.title-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cooling-icon {
  background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
  color: white;
}

.header-stats {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
}

.stat-badge.critical {
  background: #fef0f0;
  color: #f56c6c;
}

.stat-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #f56c6c;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Temperature Overview Cards */
.temp-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.temp-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
}

.temp-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.temp-card.overall {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.temp-card.hotspot {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.temp-card.delta {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.temp-card.humidity {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.temp-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.temp-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.temp-stats {
  flex: 1;
  margin-left: 16px;
}

.temp-label {
  font-size: 13px;
  opacity: 0.85;
  margin-bottom: 4px;
}

.temp-value {
  font-size: 28px;
  font-weight: 700;
}

.temp-value .unit {
  font-size: 12px;
  font-weight: normal;
  margin-left: 4px;
}

.temp-status {
  font-size: 11px;
  margin-top: 4px;
}

.temp-status.warning { color: #fbbf24; }
.temp-status.normal { color: #67c23a; }

.temp-location {
  font-size: 11px;
  opacity: 0.75;
  margin-top: 4px;
}

.temp-badge {
  font-size: 32px;
}

.temp-gauge {
  margin-left: 16px;
}

/* Section Title */
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.title-text {
  font-size: 18px;
  font-weight: 600;
  color: #1f2f3d;
}

.title-badge {
  background: #e4e7ed;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  color: #606266;
}

.title-badge.critical {
  background: #fef0f0;
  color: #f56c6c;
}

/* Cooling Grid */
.cooling-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.cooling-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  border-top: 4px solid #67c23a;
}

.cooling-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
}

.cooling-card.critical { border-top-color: #f56c6c; }
.cooling-card.warning { border-top-color: #e6a23c; }
.cooling-card.normal { border-top-color: #67c23a; }

.cooling-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
}

.unit-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
  display: flex;
  align-items: center;
  gap: 8px;
}

.unit-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.unit-status-badge.critical {
  background: #fef0f0;
  color: #f56c6c;
}

.unit-status-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.unit-status-badge.normal {
  background: #f0f9eb;
  color: #67c23a;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot.critical { background: #f56c6c; }
.status-dot.warning { background: #e6a23c; }
.status-dot.normal { background: #67c23a; }

.cooling-temp-section {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.temp-readings {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.temp-reading {
  flex: 1;
}

.reading-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.reading-value {
  font-size: 20px;
  font-weight: 700;
  color: #1f2f3d;
}

.reading-value.warning { color: #f56c6c; }

.reading-target {
  font-size: 10px;
  color: #c0c4cc;
  margin-top: 2px;
}

.cooling-metrics {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.metric-row {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
}

.metric-row:last-child {
  margin-bottom: 0;
}

.metric-item {
  flex: 1;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
  display: block;
}

.metric-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-bar-track {
  flex: 1;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.metric-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.metric-value {
  font-size: 12px;
  font-weight: 600;
  color: #1f2f3d;
  min-width: 45px;
  text-align: right;
}

.cooling-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fafafa;
  font-size: 11px;
  color: #909399;
}

.footer-info {
  display: flex;
  gap: 16px;
}

/* Alarms Container */
.alarms-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.alarm-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
}

.alarm-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.alarm-card.critical { border-left: 4px solid #f56c6c; }
.alarm-card.major { border-left: 4px solid #e6a23c; }
.alarm-card.warning { border-left: 4px solid #fbbf24; }

.alarm-icon {
  font-size: 24px;
}

.alarm-content {
  flex: 1;
}

.alarm-title {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.alarm-description {
  font-size: 12px;
  color: #606266;
  margin-bottom: 6px;
}

.alarm-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #909399;
}

.alarm-actions {
  display: flex;
  gap: 8px;
}

.empty-alarms {
  padding: 40px;
  text-align: center;
  background: white;
  border-radius: 12px;
}

/* Card */
.card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.chart-container {
  width: 100%;
  height: 350px;
  padding: 16px;
}

/* Responsive */
@media (max-width: 1200px) {
  .temp-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .cooling-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .cooling-alarms-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .temp-overview {
    grid-template-columns: 1fr;
  }
  .temp-readings {
    flex-direction: column;
    gap: 12px;
  }
  .metric-row {
    flex-direction: column;
    gap: 12px;
  }
  .alarm-card {
    flex-direction: column;
    text-align: center;
  }
  .alarm-meta {
    flex-wrap: wrap;
    justify-content: center;
  }
  .footer-info {
    flex-wrap: wrap;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-progress-circle) {
  --el-progress-circle-width: 70px;
}

:deep(.el-progress__text) {
  font-size: 14px !important;
  font-weight: 600;
}
</style>