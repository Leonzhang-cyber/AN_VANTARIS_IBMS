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
        <div class="loading-tip">Battery Alarms Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="battery-alarms-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <div class="title-icon battery-icon">
            <el-icon><Lightning /></el-icon>
          </div>
          Battery Alarms
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalBatteries }} Battery Strings
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

    <!-- Battery Health Overview Cards -->
    <div class="health-overview">
      <div class="health-card overall">
        <div class="health-card-inner">
          <div class="health-icon">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="health-stats">
            <div class="health-label">Overall Battery Health</div>
            <div class="health-value">{{ overallHealth }}<span class="unit">%</span></div>
            <div class="health-trend" :class="healthTrend > 0 ? 'up' : 'down'">
              {{ healthTrend > 0 ? '+' : '' }}{{ healthTrend }}% vs last month
            </div>
          </div>
          <div class="health-gauge">
            <el-progress type="circle" :percentage="overallHealth" :color="getHealthColor(overallHealth)" :width="80" :stroke-width="8">
              <template #default>{{ overallHealth }}%</template>
            </el-progress>
          </div>
        </div>
      </div>

      <div class="health-card aging">
        <div class="health-card-inner">
          <div class="health-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="health-stats">
            <div class="health-label">Batteries > 3 Years</div>
            <div class="health-value">{{ agingCount }}<span class="unit">units</span></div>
            <div class="health-sub">Replace recommended</div>
          </div>
          <div class="health-badge">⚠️</div>
        </div>
      </div>

      <div class="health-card capacity">
        <div class="health-card-inner">
          <div class="health-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="health-stats">
            <div class="health-label">Avg Capacity Degradation</div>
            <div class="health-value">{{ avgDegradation }}<span class="unit">%</span></div>
            <div class="health-sub">per year</div>
          </div>
          <div class="health-badge">📉</div>
        </div>
      </div>

      <div class="health-card remaining">
        <div class="health-card-inner">
          <div class="health-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="health-stats">
            <div class="health-label">Avg Remaining Life</div>
            <div class="health-value">{{ avgRemainingLife }}<span class="unit">years</span></div>
            <div class="health-sub">Based on current degradation</div>
          </div>
          <div class="health-badge">🔋</div>
        </div>
      </div>
    </div>

    <!-- Battery String Cards - 高辨识度卡片网格 -->
    <div class="section-title">
      <span class="title-text">🔋 Battery Strings Status</span>
      <span class="title-badge">{{ filteredBatteries.length }} Active Strings</span>
    </div>

    <div class="battery-grid">
      <div v-for="battery in filteredBatteries" :key="battery.id" class="battery-card" :class="battery.status">
        <div class="battery-card-header">
          <div class="battery-name">
            <span class="battery-icon">🔋</span>
            {{ battery.name }}
          </div>
          <div class="battery-status-badge" :class="battery.status">
            <span class="status-dot"></span>
            {{ battery.statusText }}
          </div>
        </div>

        <div class="battery-health-section">
          <div class="health-ring">
            <el-progress type="circle" :percentage="battery.health" :color="getHealthColor(battery.health)" :width="70" :stroke-width="6">
              <template #default>
                <span class="ring-value">{{ battery.health }}%</span>
              </template>
            </el-progress>
            <span class="ring-label">SOH</span>
          </div>
          <div class="health-details">
            <div class="detail-item">
              <span class="detail-label">Voltage</span>
              <span class="detail-value" :class="{ critical: battery.voltage < 200 }">{{ battery.voltage }}V</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Current</span>
              <span class="detail-value">{{ battery.current }}A</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Temperature</span>
              <span class="detail-value" :class="{ warning: battery.temp > 35 }">{{ battery.temp }}°C</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Internal Resistance</span>
              <span class="detail-value" :class="{ warning: battery.resistance > 8 }">{{ battery.resistance }}mΩ</span>
            </div>
          </div>
        </div>

        <div class="battery-metrics">
          <div class="metric-bar">
            <div class="metric-bar-label">Capacity</div>
            <div class="metric-bar-track">
              <div class="metric-bar-fill" :style="{ width: battery.capacity + '%', background: getCapacityColor(battery.capacity) }"></div>
            </div>
            <div class="metric-bar-value">{{ battery.capacity }}%</div>
          </div>
          <div class="metric-bar">
            <div class="metric-bar-label">Charge Level</div>
            <div class="metric-bar-track">
              <div class="metric-bar-fill" :style="{ width: battery.soc + '%', background: getSocColor(battery.soc) }"></div>
            </div>
            <div class="metric-bar-value">{{ battery.soc }}%</div>
          </div>
          <div class="metric-bar">
            <div class="metric-bar-label">Cycle Life</div>
            <div class="metric-bar-track">
              <div class="metric-bar-fill" :style="{ width: battery.cyclePercent + '%', background: getCycleColor(battery.cyclePercent) }"></div>
            </div>
            <div class="metric-bar-value">{{ battery.cycles }} / {{ battery.cycleLimit }}</div>
          </div>
        </div>

        <div class="battery-footer">
          <div class="footer-info">
            <span>📅 Installed: {{ battery.installDate }}</span>
            <span>⚠️ {{ battery.alarmCount }} active alarms</span>
          </div>
          <el-button type="primary" link size="small" @click="viewBatteryDetails(battery)">
            Details →
          </el-button>
        </div>
      </div>
    </div>

    <!-- Active Alarms Section -->
    <div class="section-title">
      <span class="title-text">🚨 Active Battery Alarms</span>
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
            <span>🔋 {{ alarm.batteryName }}</span>
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
        <el-empty description="No active battery alarms" :image-size="80" />
      </div>
    </div>

    <!-- Degradation Trend Chart -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          Battery Capacity Degradation Trend
        </div>
        <el-radio-group v-model="trendPeriod" size="small">
          <el-radio-button label="month">Monthly</el-radio-button>
          <el-radio-button label="quarter">Quarterly</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="degradationChartRef" class="chart-container"></div>
    </div>

    <!-- Battery Details Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Battery Details - ${selectedBattery?.name}`" width="650px">
      <el-descriptions :column="2" border v-if="selectedBattery">
        <el-descriptions-item label="Battery String">{{ selectedBattery.name }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTagType(selectedBattery.status)">{{ selectedBattery.statusText }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Health (SOH)">{{ selectedBattery.health }}%</el-descriptions-item>
        <el-descriptions-item label="Capacity">{{ selectedBattery.capacity }}%</el-descriptions-item>
        <el-descriptions-item label="State of Charge">{{ selectedBattery.soc }}%</el-descriptions-item>
        <el-descriptions-item label="Voltage">{{ selectedBattery.voltage }}V</el-descriptions-item>
        <el-descriptions-item label="Current">{{ selectedBattery.current }}A</el-descriptions-item>
        <el-descriptions-item label="Temperature">{{ selectedBattery.temp }}°C</el-descriptions-item>
        <el-descriptions-item label="Internal Resistance">{{ selectedBattery.resistance }}mΩ</el-descriptions-item>
        <el-descriptions-item label="Cycle Count">{{ selectedBattery.cycles }} / {{ selectedBattery.cycleLimit }}</el-descriptions-item>
        <el-descriptions-item label="Installation Date">{{ selectedBattery.installDate }}</el-descriptions-item>
        <el-descriptions-item label="Expected Lifetime">{{ selectedBattery.expectedLife }} years</el-descriptions-item>
        <el-descriptions-item label="Remaining Life">{{ selectedBattery.remainingLife }} years</el-descriptions-item>
        <el-descriptions-item label="Last Test Date">{{ selectedBattery.lastTestDate }}</el-descriptions-item>
        <el-descriptions-item label="Next Test Due">{{ selectedBattery.nextTestDue }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch  } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Lightning, Grid, Refresh, Download, DataLine, Timer, TrendCharts, Clock } from '@element-plus/icons-vue'
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
  'Loading battery data...',
  'Analyzing health metrics...',
  'Checking alarm status...',
  'Almost ready...'
]

// ==================== Data State ====================
const trendPeriod = ref('month')
const detailDialogVisible = ref(false)
const selectedBattery = ref<any>(null)

// Battery Data
interface Battery {
  id: number
  name: string
  status: 'critical' | 'warning' | 'normal'
  statusText: string
  health: number
  capacity: number
  soc: number
  voltage: number
  current: number
  temp: number
  resistance: number
  cycles: number
  cycleLimit: number
  cyclePercent: number
  installDate: string
  expectedLife: number
  remainingLife: number
  lastTestDate: string
  nextTestDue: string
  alarmCount: number
}

const batteries = ref<Battery[]>([
  { id: 1, name: 'UPS-01 Battery String A', status: 'critical', statusText: 'Critical', health: 45, capacity: 42, soc: 38, voltage: 198, current: 125, temp: 42, resistance: 12.5, cycles: 1850, cycleLimit: 2000, cyclePercent: 92.5, installDate: '2019-06-15', expectedLife: 5, remainingLife: 0.5, lastTestDate: '2024-05-20', nextTestDue: '2024-06-20', alarmCount: 3 },
  { id: 2, name: 'UPS-01 Battery String B', status: 'critical', statusText: 'Critical', health: 48, capacity: 45, soc: 42, voltage: 202, current: 118, temp: 40, resistance: 11.2, cycles: 1820, cycleLimit: 2000, cyclePercent: 91, installDate: '2019-06-15', expectedLife: 5, remainingLife: 0.7, lastTestDate: '2024-05-20', nextTestDue: '2024-06-20', alarmCount: 2 },
  { id: 3, name: 'UPS-02 Battery String', status: 'warning', statusText: 'Warning', health: 68, capacity: 65, soc: 72, voltage: 415, current: 85, temp: 36, resistance: 7.8, cycles: 1250, cycleLimit: 2000, cyclePercent: 62.5, installDate: '2021-03-10', expectedLife: 5, remainingLife: 2.2, lastTestDate: '2024-05-15', nextTestDue: '2024-08-15', alarmCount: 1 },
  { id: 4, name: 'UPS-03 Battery String', status: 'normal', statusText: 'Normal', health: 92, capacity: 88, soc: 95, voltage: 422, current: 62, temp: 28, resistance: 4.2, cycles: 420, cycleLimit: 2000, cyclePercent: 21, installDate: '2023-01-20', expectedLife: 5, remainingLife: 4.2, lastTestDate: '2024-06-01', nextTestDue: '2024-09-01', alarmCount: 0 },
  { id: 5, name: 'UPS-04 Battery String A', status: 'warning', statusText: 'Warning', health: 72, capacity: 68, soc: 65, voltage: 408, current: 78, temp: 34, resistance: 6.5, cycles: 980, cycleLimit: 2000, cyclePercent: 49, installDate: '2021-11-05', expectedLife: 5, remainingLife: 2.8, lastTestDate: '2024-05-25', nextTestDue: '2024-08-25', alarmCount: 1 },
  { id: 6, name: 'UPS-04 Battery String B', status: 'normal', statusText: 'Normal', health: 85, capacity: 82, soc: 88, voltage: 418, current: 58, temp: 30, resistance: 5.1, cycles: 680, cycleLimit: 2000, cyclePercent: 34, installDate: '2022-05-18', expectedLife: 5, remainingLife: 3.3, lastTestDate: '2024-05-25', nextTestDue: '2024-08-25', alarmCount: 0 },
  { id: 7, name: 'UPS-05 Battery String', status: 'critical', statusText: 'Critical', health: 38, capacity: 35, soc: 28, voltage: 195, current: 142, temp: 45, resistance: 14.8, cycles: 1980, cycleLimit: 2000, cyclePercent: 99, installDate: '2019-03-12', expectedLife: 5, remainingLife: 0.2, lastTestDate: '2024-05-10', nextTestDue: '2024-06-10', alarmCount: 4 }
])

const totalBatteries = computed(() => batteries.value.length)
const criticalCount = computed(() => batteries.value.filter(b => b.status === 'critical').length)
const warningCount = computed(() => batteries.value.filter(b => b.status === 'warning').length)
const overallHealth = computed(() => Math.round(batteries.value.reduce((sum, b) => sum + b.health, 0) / batteries.value.length))
const healthTrend = ref(-8)
const agingCount = computed(() => batteries.value.filter(b => b.remainingLife < 1).length)
const avgDegradation = ref(12)
const avgRemainingLife = computed(() => (batteries.value.reduce((sum, b) => sum + b.remainingLife, 0) / batteries.value.length).toFixed(1))

const filteredBatteries = computed(() => batteries.value)

// Active Alarms
interface BatteryAlarm {
  id: number
  batteryName: string
  title: string
  description: string
  severity: string
  value: string
  time: string
}

const activeAlarms = ref<BatteryAlarm[]>([
  { id: 1, batteryName: 'UPS-01 Battery String A', title: 'Battery Health Critical', description: 'Battery health dropped below 50%', severity: 'critical', value: 'SOH: 45%', time: '15 min ago' },
  { id: 2, batteryName: 'UPS-01 Battery String B', title: 'Battery Health Critical', description: 'Battery health below threshold', severity: 'critical', value: 'SOH: 48%', time: '15 min ago' },
  { id: 3, batteryName: 'UPS-02 Battery String', title: 'High Internal Resistance', description: 'Internal resistance exceeded 7mΩ', severity: 'major', value: 'Resistance: 7.8mΩ', time: '32 min ago' },
  { id: 4, batteryName: 'UPS-05 Battery String', title: 'End of Life Approaching', description: 'Battery cycle count near limit', severity: 'critical', value: 'Cycles: 1980/2000', time: '1 hour ago' },
  { id: 5, batteryName: 'UPS-04 Battery String A', title: 'Capacity Degradation', description: 'Capacity below 70%', severity: 'warning', value: 'Capacity: 68%', time: '2 hours ago' }
])

const activeAlarmsCount = computed(() => activeAlarms.value.length)

// Degradation data
const monthlyDegradationData = ref<number[]>([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
const quarterlyDegradationData = ref<number[]>([5, 8, 11, 14, 17, 20])
const monthLabels = ref<string[]>(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
const quarterLabels = ref<string[]>(['2022 Q1', '2022 Q2', '2022 Q3', '2022 Q4', '2023 Q1', '2023 Q2'])

// ==================== Helper Functions ====================
const getHealthColor = (health: number) => {
  if (health >= 80) return '#67c23a'
  if (health >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getCapacityColor = (capacity: number) => {
  if (capacity >= 80) return '#67c23a'
  if (capacity >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getSocColor = (soc: number) => {
  if (soc >= 80) return '#67c23a'
  if (soc >= 50) return '#e6a23c'
  return '#f56c6c'
}

const getCycleColor = (cyclePercent: number) => {
  if (cyclePercent < 50) return '#67c23a'
  if (cyclePercent < 80) return '#e6a23c'
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

const viewBatteryDetails = (battery: Battery) => {
  selectedBattery.value = battery
  detailDialogVisible.value = true
}

const acknowledgeAlarm = (alarm: BatteryAlarm) => {
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

const escalateAlarm = (alarm: BatteryAlarm) => {
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
const degradationChartRef = ref<HTMLElement>()
let degradationChart: echarts.ECharts | null = null

const initChart = () => {
  nextTick(() => {
    if (!degradationChartRef.value) {
      setTimeout(initChart, 200)
      return
    }

    if (degradationChart) degradationChart.dispose()
    degradationChart = echarts.init(degradationChartRef.value)
    updateDegradationChart()

    window.addEventListener('resize', () => degradationChart?.resize())
  })
}

const updateDegradationChart = () => {
  if (!degradationChart) return

  const isMonthly = trendPeriod.value === 'month'
  const data = isMonthly ? monthlyDegradationData.value : quarterlyDegradationData.value
  const labels = isMonthly ? monthLabels.value : quarterLabels.value

  degradationChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { rotate: 45, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: { type: 'value', name: 'Capacity Degradation (%)', axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
    series: [{
      type: 'line', data: data, smooth: true,
      lineStyle: { color: '#f56c6c', width: 3 },
      areaStyle: { opacity: 0.1, color: '#f56c6c' },
      symbol: 'circle', symbolSize: 6, itemStyle: { color: '#f56c6c' }
    }]
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
  updateDegradationChart()
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
.battery-alarms-dashboard {
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

.battery-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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

/* Health Overview Cards */
.health-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.health-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
}

.health-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.health-card.overall {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.health-card.aging {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.health-card.capacity {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.health-card.remaining {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.health-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.health-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.health-stats {
  flex: 1;
  margin-left: 16px;
}

.health-label {
  font-size: 13px;
  opacity: 0.85;
  margin-bottom: 4px;
}

.health-value {
  font-size: 28px;
  font-weight: 700;
}

.health-value .unit {
  font-size: 12px;
  font-weight: normal;
  margin-left: 4px;
}

.health-trend {
  font-size: 11px;
  margin-top: 4px;
}

.health-trend.up { color: #67c23a; }
.health-trend.down { color: #f56c6c; }

.health-sub {
  font-size: 11px;
  opacity: 0.75;
  margin-top: 4px;
}

.health-badge {
  font-size: 32px;
}

.health-gauge {
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

/* Battery Grid */
.battery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.battery-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  border-top: 4px solid #67c23a;
}

.battery-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.15);
}

.battery-card.critical { border-top-color: #f56c6c; }
.battery-card.warning { border-top-color: #e6a23c; }
.battery-card.normal { border-top-color: #67c23a; }

.battery-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
}

.battery-name {
  font-weight: 600;
  font-size: 16px;
  color: #1f2f3d;
  display: flex;
  align-items: center;
  gap: 8px;
}

.battery-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.battery-status-badge.critical {
  background: #fef0f0;
  color: #f56c6c;
}

.battery-status-badge.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.battery-status-badge.normal {
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

.battery-health-section {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.health-ring {
  text-align: center;
  flex-shrink: 0;
}

.ring-value {
  font-size: 16px;
  font-weight: 700;
}

.ring-label {
  display: block;
  font-size: 10px;
  color: #909399;
  margin-top: 4px;
}

.health-details {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.detail-label {
  font-size: 11px;
  color: #909399;
}

.detail-value {
  font-size: 14px;
  font-weight: 600;
  color: #1f2f3d;
}

.detail-value.critical { color: #f56c6c; }
.detail-value.warning { color: #e6a23c; }

.battery-metrics {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.metric-bar {
  margin-bottom: 12px;
}

.metric-bar:last-child {
  margin-bottom: 0;
}

.metric-bar-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-bar-track {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.metric-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.metric-bar-value {
  font-size: 11px;
  font-weight: 500;
  text-align: right;
  color: #606266;
}

.battery-footer {
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
  height: 320px;
  padding: 16px;
}

/* Responsive */
@media (max-width: 1200px) {
  .health-overview {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .battery-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .battery-alarms-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .health-overview {
    grid-template-columns: 1fr;
  }
  .battery-health-section {
    flex-direction: column;
    text-align: center;
  }
  .alarm-card {
    flex-direction: column;
    text-align: center;
  }
  .alarm-meta {
    flex-wrap: wrap;
    justify-content: center;
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