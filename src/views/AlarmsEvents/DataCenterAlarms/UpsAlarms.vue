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
        <div class="loading-tip">UPS Alarms Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ups-alarms-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <el-icon><Lightning /></el-icon>
          UPS Alarms
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalUpsUnits }} UPS Units
          </div>
          <div class="stat-badge">
            <el-icon><Bell /></el-icon>
            {{ totalActiveAlarms }} Active Alarms
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

    <!-- Statistics Cards -->
    <div class="kpi-grid">
      <div class="kpi-card critical">
        <div class="kpi-icon">🔴</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ criticalAlarms }}</div>
          <div class="kpi-label">Critical Alarms</div>
          <div class="kpi-trend up">{{ criticalTrend }}% vs last week</div>
        </div>
      </div>
      <div class="kpi-card major">
        <div class="kpi-icon">🟠</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ majorAlarms }}</div>
          <div class="kpi-label">Major Alarms</div>
          <div class="kpi-trend down">{{ majorTrend }}% vs last week</div>
        </div>
      </div>
      <div class="kpi-card warning">
        <div class="kpi-icon">🟡</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ warningAlarms }}</div>
          <div class="kpi-label">Warning Alarms</div>
          <div class="kpi-trend up">{{ warningTrend }}% vs last week</div>
        </div>
      </div>
      <div class="kpi-card info">
        <div class="kpi-icon">🔵</div>
        <div class="kpi-info">
          <div class="kpi-value">{{ infoAlarms }}</div>
          <div class="kpi-label">Info Alarms</div>
          <div class="kpi-trend stable">{{ infoTrend }}% vs last week</div>
        </div>
      </div>
    </div>

    <!-- UPS Status Overview -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><Monitor /></el-icon>
          UPS Units Status
        </div>
        <el-radio-group v-model="upsFilter" size="small">
          <el-radio-button label="all">All Units</el-radio-button>
          <el-radio-button label="critical">Critical</el-radio-button>
          <el-radio-button label="warning">Warning</el-radio-button>
          <el-radio-button label="normal">Normal</el-radio-button>
        </el-radio-group>
      </div>
      <div class="ups-grid">
        <div v-for="ups in filteredUpsUnits" :key="ups.id" class="ups-card" :class="ups.status">
          <div class="ups-header">
            <span class="ups-name">{{ ups.name }}</span>
            <span class="ups-status" :class="ups.status">{{ ups.statusText }}</span>
          </div>
          <div class="ups-metrics">
            <div class="metric">
              <span class="label">Load:</span>
              <span class="value">{{ ups.load }}%</span>
              <el-progress :percentage="ups.load" :stroke-width="6" :show-text="false" />
            </div>
            <div class="metric">
              <span class="label">Battery:</span>
              <span class="value">{{ ups.battery }}%</span>
              <el-progress :percentage="ups.battery" :color="getBatteryColor(ups.battery)" :stroke-width="6" :show-text="false" />
            </div>
            <div class="metric">
              <span class="label">Runtime:</span>
              <span class="value">{{ ups.runtime }} min</span>
            </div>
            <div class="metric">
              <span class="label">Temp:</span>
              <span class="value" :class="{ high: ups.temp > 35 }">{{ ups.temp }}°C</span>
            </div>
          </div>
          <div class="ups-alarms-count">
            <el-badge :value="ups.alarmCount" :type="ups.alarmCount > 0 ? 'danger' : 'success'" />
          </div>
        </div>
      </div>
    </div>

    <!-- Alarm Trend Chart -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          UPS Alarm Trend (Last 7 Days)
        </div>
        <el-radio-group v-model="trendPeriod" size="small" @change="updateTrendChart">
          <el-radio-button label="day">Daily</el-radio-button>
          <el-radio-button label="week">Weekly</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="trendChartRef" class="chart-container"></div>
    </div>

    <!-- Top Alarm Types -->
    <div class="two-columns">
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><PieChart /></el-icon>
            Top Alarm Types
          </div>
        </div>
        <div ref="alarmTypeChartRef" class="chart-container-small"></div>
      </div>

      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><List /></el-icon>
            Alarm by UPS Unit
          </div>
        </div>
        <div ref="upsAlarmChartRef" class="chart-container-small"></div>
      </div>
    </div>

    <!-- Active Alarms Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><WarningFilled /></el-icon>
          Active UPS Alarms
        </div>
        <div class="table-controls">
          <el-input v-model="searchText" placeholder="Search alarms..." size="small" style="width: 200px" clearable>
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
          <el-select v-model="severityFilter" placeholder="Severity" size="small" style="width: 120px" clearable>
            <el-option label="All" value="all" />
            <el-option label="Critical" value="critical" />
            <el-option label="Major" value="major" />
            <el-option label="Warning" value="warning" />
            <el-option label="Info" value="info" />
          </el-select>
          <el-select v-model="upsUnitFilter" placeholder="UPS Unit" size="small" style="width: 140px" clearable>
            <el-option label="All Units" value="all" />
            <el-option v-for="ups in upsUnits" :key="ups.id" :label="ups.name" :value="ups.name" />
          </el-select>
        </div>
      </div>
      <el-table :data="paginatedAlarms" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="time" label="Time" width="160" sortable />
        <el-table-column prop="upsName" label="UPS Unit" width="140" />
        <el-table-column prop="title" label="Alarm Title" min-width="200" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="Alarm Type" width="130" />
        <el-table-column prop="value" label="Current Value" width="110" />
        <el-table-column prop="threshold" label="Threshold" width="100" />
        <el-table-column prop="duration" label="Duration" width="100" sortable />
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button type="success" link size="small" @click="acknowledgeAlarm(row)">
              Acknowledge
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="card-footer">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="filteredAlarms.length"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`UPS Alarm Details - ${selectedAlarm?.title}`" width="550px">
      <el-descriptions :column="2" border v-if="selectedAlarm">
        <el-descriptions-item label="Alarm ID">{{ selectedAlarm.id }}</el-descriptions-item>
        <el-descriptions-item label="UPS Unit">{{ selectedAlarm.upsName }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTag(selectedAlarm.severity)">{{ selectedAlarm.severity.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Alarm Type">{{ selectedAlarm.type }}</el-descriptions-item>
        <el-descriptions-item label="Title" :span="2">{{ selectedAlarm.title }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedAlarm.description }}</el-descriptions-item>
        <el-descriptions-item label="Current Value">{{ selectedAlarm.value }}</el-descriptions-item>
        <el-descriptions-item label="Threshold">{{ selectedAlarm.threshold }}</el-descriptions-item>
        <el-descriptions-item label="Occurred At">{{ selectedAlarm.time }}</el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedAlarm.duration }}</el-descriptions-item>
        <el-descriptions-item label="Recommended Action" :span="2">{{ selectedAlarm.recommendedAction || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Lightning, Grid, Bell, Refresh, Download, Monitor, TrendCharts, PieChart, List, WarningFilled, Search } from '@element-plus/icons-vue'
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
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading UPS units...',
  'Checking battery status...',
  'Analyzing alarms...',
  'Almost ready...'
]

// ==================== Data State ====================
const upsFilter = ref('all')
const searchText = ref('')
const severityFilter = ref('all')
const upsUnitFilter = ref('all')
const trendPeriod = ref('day')
const detailDialogVisible = ref(false)
const selectedAlarm = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 10 })

// UPS Units Data
interface UpsUnit {
  id: number
  name: string
  status: string
  statusText: string
  load: number
  battery: number
  runtime: number
  temp: number
  alarmCount: number
}

const upsUnits = ref<UpsUnit[]>([
  { id: 1, name: 'UPS-01 (Main)', status: 'critical', statusText: 'Critical', load: 92, battery: 45, runtime: 8, temp: 38, alarmCount: 3 },
  { id: 2, name: 'UPS-02 (Backup)', status: 'warning', statusText: 'Warning', load: 78, battery: 35, runtime: 12, temp: 34, alarmCount: 2 },
  { id: 3, name: 'UPS-03 (Data Center)', status: 'normal', statusText: 'Normal', load: 65, battery: 78, runtime: 25, temp: 28, alarmCount: 0 },
  { id: 4, name: 'UPS-04 (Server Room)', status: 'normal', statusText: 'Normal', load: 52, battery: 82, runtime: 32, temp: 26, alarmCount: 0 },
  { id: 5, name: 'UPS-05 (Storage)', status: 'warning', statusText: 'Warning', load: 72, battery: 48, runtime: 10, temp: 32, alarmCount: 1 },
  { id: 6, name: 'UPS-06 (Network)', status: 'normal', statusText: 'Normal', load: 48, battery: 88, runtime: 38, temp: 25, alarmCount: 0 }
])

const totalUpsUnits = computed(() => upsUnits.value.length)
const totalActiveAlarms = computed(() => upsUnits.value.reduce((sum, u) => sum + u.alarmCount, 0))

const filteredUpsUnits = computed(() => {
  if (upsFilter.value === 'all') return upsUnits.value
  return upsUnits.value.filter(u => u.status === upsFilter.value)
})

// Alarm Statistics
const criticalAlarms = ref(8)
const majorAlarms = ref(12)
const warningAlarms = ref(18)
const infoAlarms = ref(6)
const criticalTrend = ref(15)
const majorTrend = ref(-5)
const warningTrend = ref(8)
const infoTrend = ref(0)

// Alarm Data
interface UpsAlarm {
  id: number
  time: string
  upsName: string
  title: string
  description: string
  severity: string
  type: string
  value: string
  threshold: string
  duration: string
  recommendedAction: string
}

const alarms = ref<UpsAlarm[]>([
  { id: 1, time: '2024-06-03 08:23:15', upsName: 'UPS-01 (Main)', title: 'UPS Overload', description: 'UPS load exceeded 90% capacity', severity: 'critical', type: 'Overload', value: '92%', threshold: '90%', duration: '5 min', recommendedAction: 'Reduce load immediately or add additional UPS capacity' },
  { id: 2, time: '2024-06-03 09:45:22', upsName: 'UPS-01 (Main)', title: 'Battery Low', description: 'Battery capacity below 50%', severity: 'critical', type: 'Battery', value: '45%', threshold: '50%', duration: '15 min', recommendedAction: 'Schedule battery replacement' },
  { id: 3, time: '2024-06-03 10:30:10', upsName: 'UPS-02 (Backup)', title: 'High Temperature', description: 'Internal temperature exceeded threshold', severity: 'warning', type: 'Temperature', value: '34°C', threshold: '32°C', duration: '8 min', recommendedAction: 'Check cooling fans and airflow' },
  { id: 4, time: '2024-06-03 11:15:33', upsName: 'UPS-02 (Backup)', title: 'Battery Aging', description: 'Battery capacity degradation detected', severity: 'warning', type: 'Battery', value: '35%', threshold: '60%', duration: '2 days', recommendedAction: 'Perform battery capacity test' },
  { id: 5, time: '2024-06-03 12:00:00', upsName: 'UPS-05 (Storage)', title: 'Input Voltage Fluctuation', description: 'Input voltage out of range', severity: 'warning', type: 'Power Quality', value: '198V', threshold: '207-253V', duration: '3 min', recommendedAction: 'Check upstream power quality' },
  { id: 6, time: '2024-06-02 14:30:45', upsName: 'UPS-01 (Main)', title: 'Fan Failure', description: 'Cooling fan not responding', severity: 'critical', type: 'Hardware', value: '0 RPM', threshold: '> 2000 RPM', duration: '10 min', recommendedAction: 'Schedule immediate fan replacement' },
  { id: 7, time: '2024-06-02 16:20:30', upsName: 'UPS-02 (Backup)', title: 'Communication Lost', description: 'SNMP communication timeout', severity: 'major', type: 'Communication', value: 'Timeout', threshold: 'Online', duration: '5 min', recommendedAction: 'Check network connection and restart agent' }
])

const filteredAlarms = computed(() => {
  let filtered = alarms.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a => a.title.toLowerCase().includes(search) || a.description.toLowerCase().includes(search))
  }

  if (severityFilter.value !== 'all') {
    filtered = filtered.filter(a => a.severity === severityFilter.value)
  }

  if (upsUnitFilter.value !== 'all') {
    filtered = filtered.filter(a => a.upsName === upsUnitFilter.value)
  }

  return filtered
})

const paginatedAlarms = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filteredAlarms.value.slice(start, start + pagination.value.pageSize)
})

// Trend data
const dailyTrendData = ref<number[]>([5, 8, 12, 7, 10, 6, 4])
const weeklyTrendData = ref<number[]>([18, 22, 15, 20])
const dailyLabels = ref<string[]>(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
const weeklyLabels = ref<string[]>(['Week 1', 'Week 2', 'Week 3', 'Week 4'])

// Chart data
const alarmTypeData = ref([
  { name: 'Overload', value: 8, color: '#f56c6c' },
  { name: 'Battery', value: 12, color: '#e6a23c' },
  { name: 'Temperature', value: 6, color: '#fbbf24' },
  { name: 'Communication', value: 4, color: '#409eff' },
  { name: 'Power Quality', value: 3, color: '#909399' },
  { name: 'Hardware', value: 2, color: '#67c23a' }
])

const upsAlarmData = ref([
  { name: 'UPS-01', value: 8, color: '#f56c6c' },
  { name: 'UPS-02', value: 5, color: '#e6a23c' },
  { name: 'UPS-03', value: 0, color: '#67c23a' },
  { name: 'UPS-04', value: 0, color: '#67c23a' },
  { name: 'UPS-05', value: 1, color: '#fbbf24' },
  { name: 'UPS-06', value: 0, color: '#67c23a' }
])

// ==================== Chart Refs ====================
const trendChartRef = ref<HTMLElement>()
const alarmTypeChartRef = ref<HTMLElement>()
const upsAlarmChartRef = ref<HTMLElement>()

let trendChart: echarts.ECharts | null = null
let alarmTypeChart: echarts.ECharts | null = null
let upsAlarmChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    // Trend Chart
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      updateTrendChart()
    }

    // Alarm Type Pie Chart
    if (alarmTypeChartRef.value) {
      if (alarmTypeChart) alarmTypeChart.dispose()
      alarmTypeChart = echarts.init(alarmTypeChartRef.value)
      alarmTypeChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left', textStyle: { color: '#606266' } },
        series: [{
          type: 'pie', radius: '55%', center: ['50%', '50%'],
          data: alarmTypeData.value.map(item => ({ name: item.name, value: item.value, itemStyle: { color: item.color } })),
          label: { show: true, formatter: '{b}: {d}%', color: '#606266' }
        }]
      })
    }

    // UPS Alarm Bar Chart
    if (upsAlarmChartRef.value) {
      if (upsAlarmChart) upsAlarmChart.dispose()
      upsAlarmChart = echarts.init(upsAlarmChartRef.value)
      upsAlarmChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '10%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
        xAxis: { type: 'category', data: upsAlarmData.value.map(u => u.name), axisLabel: { rotate: 30, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
        yAxis: { type: 'value', name: 'Alarm Count', axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
        series: [{
          type: 'bar', data: upsAlarmData.value.map(u => u.value),
          itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => upsAlarmData.value[params.dataIndex].color },
          label: { show: true, position: 'top' }
        }]
      })
    }

    window.addEventListener('resize', handleResize)
  })
}

const updateTrendChart = () => {
  if (!trendChart) return

  let data: number[]
  let labels: string[]

  if (trendPeriod.value === 'day') {
    labels = dailyLabels.value
    data = dailyTrendData.value
  } else {
    labels = weeklyLabels.value
    data = weeklyTrendData.value
  }

  trendChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: { type: 'value', name: 'Alarm Count', axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
    series: [{
      type: 'line', data: data, smooth: true,
      lineStyle: { color: '#f56c6c', width: 3 },
      areaStyle: { opacity: 0.1, color: '#f56c6c' },
      symbol: 'circle', symbolSize: 6, itemStyle: { color: '#f56c6c' }
    }]
  })
}

const handleResize = () => {
  trendChart?.resize()
  alarmTypeChart?.resize()
  upsAlarmChart?.resize()
}

// ==================== Helper Functions ====================
const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    major: 'warning',
    warning: 'warning',
    info: 'info'
  }
  return map[severity] || 'info'
}

const getBatteryColor = (battery: number) => {
  if (battery >= 70) return '#67c23a'
  if (battery >= 30) return '#e6a23c'
  return '#f56c6c'
}

const acknowledgeAlarm = (alarm: UpsAlarm) => {
  ElMessageBox.confirm(`Acknowledge alarm "${alarm.title}"?`, 'Confirm', {
    confirmButtonText: 'Acknowledge',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = alarms.value.findIndex(a => a.id === alarm.id)
    if (index > -1) {
      alarms.value.splice(index, 1)
      // Update UPS alarm count
      const upsUnit = upsUnits.value.find(u => u.name === alarm.upsName)
      if (upsUnit) upsUnit.alarmCount--
      ElMessage.success(`Alarm "${alarm.title}" acknowledged`)
    }
  }).catch(() => {})
}

const viewDetails = (alarm: UpsAlarm) => {
  selectedAlarm.value = alarm
  detailDialogVisible.value = true
}

const exportReport = () => {
  ElMessage.success('Exporting report...')
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pagination.value.page = 1 }
const handlePageChange = () => {}

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
          initCharts()
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
.ups-alarms-dashboard {
  min-height: 100vh;
  background: #ffffff;
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0;
}

.dashboard-title .el-icon {
  color: #409eff;
}

.header-stats {
  display: flex;
  gap: 16px;
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

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-trend {
  font-size: 11px;
  margin-top: 4px;
  display: block;
}

.kpi-trend.up { color: #f56c6c; }
.kpi-trend.down { color: #67c23a; }
.kpi-trend.stable { color: #909399; }

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-wrap: wrap;
  gap: 12px;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.card-title .el-icon {
  color: #409eff;
}

/* UPS Grid */
.ups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  padding: 16px;
}

.ups-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 16px;
  border-left: 4px solid #67c23a;
  transition: all 0.2s;
  position: relative;
}

.ups-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.ups-card.critical { border-left-color: #f56c6c; background: rgba(245, 108, 108, 0.02); }
.ups-card.warning { border-left-color: #e6a23c; background: rgba(230, 162, 60, 0.02); }
.ups-card.normal { border-left-color: #67c23a; }

.ups-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.ups-name {
  font-weight: 600;
  font-size: 15px;
  color: #1f2f3d;
}

.ups-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
}

.ups-status.critical { background: #fef0f0; color: #f56c6c; }
.ups-status.warning { background: #fdf6ec; color: #e6a23c; }
.ups-status.normal { background: #f0f9eb; color: #67c23a; }

.ups-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 12px;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric .label {
  font-size: 11px;
  color: #909399;
}

.metric .value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.metric .value.high { color: #f56c6c; }

.ups-alarms-count {
  position: absolute;
  top: 12px;
  right: 12px;
}

/* Charts */
.chart-container {
  width: 100%;
  height: 320px;
  padding: 8px;
}

.chart-container-small {
  width: 100%;
  height: 280px;
  padding: 8px;
}

/* Two Columns */
.two-columns {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.two-columns .card {
  flex: 1;
  margin-bottom: 0;
}

/* Table */
.table-card {
  overflow-x: auto;
}

.table-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

/* Responsive */
@media (max-width: 1000px) {
  .two-columns {
    flex-direction: column;
  }
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .ups-alarms-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  .table-controls {
    flex-direction: column;
    width: 100%;
  }
  .table-controls .el-input,
  .table-controls .el-select {
    width: 100% !important;
  }
  .ups-grid {
    grid-template-columns: 1fr;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-table) {
  background: transparent;
  --el-table-header-bg-color: #fafafa;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-border-color: #e4e7ed;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  color: #1f2f3d;
}

:deep(.el-table td.el-table__cell) {
  color: #606266;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-button-bg-color: #f5f7fa;
  --el-pagination-hover-color: #409eff;
}

:deep(.el-dialog) {
  background: #ffffff;
  border-radius: 12px;
}

:deep(.el-dialog__title) {
  color: #1f2f3d;
}

:deep(.el-progress-bar__outer) {
  background-color: #e4e7ed;
}
</style>