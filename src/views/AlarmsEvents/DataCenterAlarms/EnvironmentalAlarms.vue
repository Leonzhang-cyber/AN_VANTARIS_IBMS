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
        <div class="loading-tip">Environmental Alarms Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="environmental-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <div class="title-icon env-icon">
            <el-icon><CircleClose /></el-icon>
          </div>
          Environmental Alarms
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalSensors }} Sensors
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

    <!-- Environmental Overview Cards -->
    <div class="env-overview">
      <div class="env-card temp">
        <div class="env-card-inner">
          <div class="env-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="env-stats">
            <div class="env-label">Average Temperature</div>
            <div class="env-value">{{ avgTemp }}<span class="unit">°C</span></div>
            <div class="env-status" :class="getTempStatusClass(avgTemp)">
              {{ getTempStatusText(avgTemp) }}
            </div>
          </div>
          <div class="env-gauge">
            <el-progress type="circle" :percentage="tempPercent" :color="getTempColor(avgTemp)" :width="70" :stroke-width="6">
              <template #default>{{ avgTemp }}°C</template>
            </el-progress>
          </div>
        </div>
      </div>

      <div class="env-card humidity">
        <div class="env-card-inner">
          <div class="env-icon">
            <el-icon><Histogram /></el-icon>
          </div>
          <div class="env-stats">
            <div class="env-label">Average Humidity</div>
            <div class="env-value">{{ avgHumidity }}<span class="unit">%</span></div>
            <div class="env-status" :class="getHumidityStatusClass(avgHumidity)">
              {{ getHumidityStatusText(avgHumidity) }}
            </div>
          </div>
          <div class="env-gauge">
            <el-progress type="circle" :percentage="avgHumidity" :color="getHumidityColor(avgHumidity)" :width="70" :stroke-width="6">
              <template #default>{{ avgHumidity }}%</template>
            </el-progress>
          </div>
        </div>
      </div>

      <div class="env-card pressure">
        <div class="env-card-inner">
          <div class="env-icon">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="env-stats">
            <div class="env-label">Air Pressure</div>
            <div class="env-value">{{ avgPressure }}<span class="unit">hPa</span></div>
            <div class="env-status normal">Stable</div>
          </div>
          <div class="env-badge">📊</div>
        </div>
      </div>

      <div class="env-card air">
        <div class="env-card-inner">
          <div class="env-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="env-stats">
            <div class="env-label">Air Quality</div>
            <div class="env-value">{{ airQuality }}<span class="unit">μg/m³</span></div>
            <div class="env-status" :class="getAirQualityClass(airQuality)">
              {{ getAirQualityStatus(airQuality) }}
            </div>
          </div>
          <div class="env-badge">🌬️</div>
        </div>
      </div>
    </div>

    <!-- Zone Status Cards -->
    <div class="section-title">
      <span class="title-text">📍 Zone Environmental Status</span>
      <span class="title-badge">{{ zones.length }} Zones</span>
    </div>

    <div class="zone-grid">
      <div v-for="zone in zones" :key="zone.id" class="zone-card" :class="zone.status">
        <div class="zone-header">
          <div class="zone-name">
            <span class="zone-icon">📍</span>
            {{ zone.name }}
          </div>
          <div class="zone-status-badge" :class="zone.status">
            <span class="status-dot"></span>
            {{ zone.statusText }}
          </div>
        </div>

        <div class="zone-metrics">
          <div class="zone-metric">
            <span class="metric-label">Temperature</span>
            <span class="metric-value" :class="getTempWarningClass(zone.temp)">{{ zone.temp }}°C</span>
            <div class="metric-bar">
              <div class="metric-bar-track">
                <div class="metric-bar-fill" :style="{ width: (zone.temp / 35) * 100 + '%', background: getTempColor(zone.temp) }"></div>
              </div>
            </div>
          </div>
          <div class="zone-metric">
            <span class="metric-label">Humidity</span>
            <span class="metric-value" :class="getHumidityWarningClass(zone.humidity)">{{ zone.humidity }}%</span>
            <div class="metric-bar">
              <div class="metric-bar-track">
                <div class="metric-bar-fill" :style="{ width: zone.humidity + '%', background: getHumidityColor(zone.humidity) }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="zone-footer">
          <div class="footer-info">
            <span>🌡️ {{ zone.sensorCount }} sensors</span>
            <span>⚠️ {{ zone.alarmCount }} alarms</span>
          </div>
          <el-button type="primary" link size="small" @click="viewZoneDetails(zone)">
            Details →
          </el-button>
        </div>
      </div>
    </div>

    <!-- Sensor Grid -->
    <div class="section-title">
      <span class="title-text">🔬 Environmental Sensors</span>
      <div class="filter-group">
        <el-select v-model="zoneFilter" size="small" placeholder="Filter by zone" style="width: 140px" clearable>
          <el-option label="All Zones" value="all" />
          <el-option v-for="zone in zones" :key="zone.id" :label="zone.name" :value="zone.name" />
        </el-select>
        <el-select v-model="sensorTypeFilter" size="small" placeholder="Sensor Type" style="width: 120px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Temperature" value="temp" />
          <el-option label="Humidity" value="humidity" />
          <el-option label="Air Quality" value="air" />
        </el-select>
      </div>
    </div>

    <div class="sensor-grid">
      <div v-for="sensor in filteredSensors" :key="sensor.id" class="sensor-card" :class="sensor.status">
        <div class="sensor-header">
          <div class="sensor-name">
            <span class="sensor-icon">📡</span>
            {{ sensor.name }}
          </div>
          <div class="sensor-type-tag" :class="sensor.type">
            {{ sensor.type === 'temp' ? 'Temperature' : (sensor.type === 'humidity' ? 'Humidity' : 'Air Quality') }}
          </div>
        </div>

        <div class="sensor-reading">
          <div class="reading-value" :class="sensor.status">
            {{ sensor.value }}<span class="unit">{{ sensor.unit }}</span>
          </div>
          <div class="reading-label">Current Reading</div>
        </div>

        <div class="sensor-threshold">
          <div class="threshold-bar">
            <div class="threshold-bar-track">
              <div class="threshold-bar-fill" :style="{ width: sensor.percent + '%', background: sensor.status === 'critical' ? '#f56c6c' : (sensor.status === 'warning' ? '#e6a23c' : '#67c23a') }"></div>
            </div>
            <div class="threshold-markers">
              <span class="marker low">Min: {{ sensor.minThreshold }}</span>
              <span class="marker high">Max: {{ sensor.maxThreshold }}</span>
            </div>
          </div>
        </div>

        <div class="sensor-footer">
          <div class="footer-info">
            <span>📍 {{ sensor.zone }}</span>
            <span>⏱️ {{ sensor.lastUpdate }}</span>
          </div>
          <el-button type="primary" link size="small" @click="viewSensorDetails(sensor)">
            Details →
          </el-button>
        </div>
      </div>
    </div>

    <!-- Active Environmental Alarms -->
    <div class="section-title">
      <span class="title-text">🚨 Active Environmental Alarms</span>
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
            <span>📍 {{ alarm.zone }}</span>
            <span>📡 {{ alarm.sensorName }}</span>
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
        <el-empty description="No active environmental alarms" :image-size="80" />
      </div>
    </div>

    <!-- Temperature Heatmap -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          Temperature Heatmap (Last 24 Hours)
        </div>
        <el-radio-group v-model="heatmapPeriod" size="small">
          <el-radio-button label="hour">Hourly</el-radio-button>
          <el-radio-button label="day">Daily</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="heatmapChartRef" class="heatmap-container"></div>
    </div>

    <!-- ASHRAE Compliance -->
    <div class="ashrae-card">
      <div class="ashrae-header">
        <div class="ashrae-title">
          <span class="title-icon">✅</span>
          ASHRAE Compliance Summary
        </div>
        <div class="ashrae-score">
          <el-progress type="circle" :percentage="ashraeCompliance" :color="getComplianceColor(ashraeCompliance)" :width="60" :stroke-width="6">
            <template #default>{{ ashraeCompliance }}%</template>
          </el-progress>
        </div>
      </div>
      <div class="ashrae-metrics">
        <div class="ashrae-item">
          <div class="ashrae-label">Temperature Range</div>
          <div class="ashrae-value">18-27°C</div>
          <div class="ashrae-status" :class="tempCompliance ? 'pass' : 'fail'">
            {{ tempCompliance ? '✅ Within Range' : '❌ Out of Range' }}
          </div>
        </div>
        <div class="ashrae-item">
          <div class="ashrae-label">Humidity Range</div>
          <div class="ashrae-value">40-60%</div>
          <div class="ashrae-status" :class="humidityCompliance ? 'pass' : 'fail'">
            {{ humidityCompliance ? '✅ Within Range' : '❌ Out of Range' }}
          </div>
        </div>
        <div class="ashrae-item">
          <div class="ashrae-label">Max Temperature Deviation</div>
          <div class="ashrae-value">+{{ maxTempDeviation }}°C</div>
          <div class="ashrae-status warning">⚠️ Action Required</div>
        </div>
        <div class="ashrae-item">
          <div class="ashrae-label">Compliant Sensors</div>
          <div class="ashrae-value">{{ compliantSensors }}/{{ totalSensors }}</div>
          <div class="ashrae-status pass">{{ compliantPercent }}%</div>
        </div>
      </div>
    </div>

    <!-- Zone Detail Dialog -->
    <el-dialog v-model="zoneDetailVisible" :title="`Zone Details - ${selectedZone?.name}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedZone">
        <el-descriptions-item label="Zone Name">{{ selectedZone.name }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTagType(selectedZone.status)">{{ selectedZone.statusText }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Temperature">{{ selectedZone.temp }}°C</el-descriptions-item>
        <el-descriptions-item label="Humidity">{{ selectedZone.humidity }}%</el-descriptions-item>
        <el-descriptions-item label="Sensor Count">{{ selectedZone.sensorCount }}</el-descriptions-item>
        <el-descriptions-item label="Active Alarms">{{ selectedZone.alarmCount }}</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedZone.lastUpdate }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Sensor Detail Dialog -->
    <el-dialog v-model="sensorDetailVisible" :title="`Sensor Details - ${selectedSensor?.name}`" width="550px">
      <el-descriptions :column="2" border v-if="selectedSensor">
        <el-descriptions-item label="Sensor Name">{{ selectedSensor.name }}</el-descriptions-item>
        <el-descriptions-item label="Type">
          <el-tag :type="selectedSensor.type === 'temp' ? 'danger' : (selectedSensor.type === 'humidity' ? 'primary' : 'success')" size="small">
            {{ selectedSensor.type === 'temp' ? 'Temperature' : (selectedSensor.type === 'humidity' ? 'Humidity' : 'Air Quality') }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Zone">{{ selectedSensor.zone }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedSensor.status === 'critical' ? 'danger' : (selectedSensor.status === 'warning' ? 'warning' : 'success')" size="small">
            {{ selectedSensor.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Current Reading">{{ selectedSensor.value }} {{ selectedSensor.unit }}</el-descriptions-item>
        <el-descriptions-item label="Min Threshold">{{ selectedSensor.minThreshold }}</el-descriptions-item>
        <el-descriptions-item label="Max Threshold">{{ selectedSensor.maxThreshold }}</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedSensor.lastUpdate }}</el-descriptions-item>
        <el-descriptions-item label="Battery Level">{{ selectedSensor.battery }}%</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, Refresh, Download, CircleClose, Clock, Histogram, Connection, TrendCharts } from '@element-plus/icons-vue'
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
  'Loading environmental data...',
  'Analyzing sensor readings...',
  'Checking alarm status...',
  'Almost ready...'
]

// ==================== Data State ====================
const zoneFilter = ref('all')
const sensorTypeFilter = ref('all')
const heatmapPeriod = ref('hour')
const zoneDetailVisible = ref(false)
const sensorDetailVisible = ref(false)
const selectedZone = ref<any>(null)
const selectedSensor = ref<any>(null)

// Environmental Stats
const avgTemp = ref(24.8)
const avgHumidity = ref(52)
const avgPressure = ref(1013.2)
const airQuality = ref(35)
const tempPercent = computed(() => Math.min(100, (avgTemp.value / 35) * 100))
const ashraeCompliance = ref(86)
const tempCompliance = computed(() => avgTemp.value >= 18 && avgTemp.value <= 27)
const humidityCompliance = computed(() => avgHumidity.value >= 40 && avgHumidity.value <= 60)
const maxTempDeviation = ref(3.2)
const totalSensors = ref(48)
const compliantSensors = ref(42)
const compliantPercent = computed(() => Math.round((compliantSensors.value / totalSensors.value) * 100))
const criticalCount = ref(3)
const warningCount = ref(5)

// Zones Data
interface Zone {
  id: number
  name: string
  status: string
  statusText: string
  temp: number
  humidity: number
  sensorCount: number
  alarmCount: number
  lastUpdate: string
}

const zones = ref<Zone[]>([
  { id: 1, name: 'Cold Aisle A', status: 'normal', statusText: 'Normal', temp: 22.5, humidity: 48, sensorCount: 8, alarmCount: 0, lastUpdate: '2 min ago' },
  { id: 2, name: 'Hot Aisle A', status: 'warning', statusText: 'Warning', temp: 28.5, humidity: 52, sensorCount: 8, alarmCount: 1, lastUpdate: '2 min ago' },
  { id: 3, name: 'Cold Aisle B', status: 'normal', statusText: 'Normal', temp: 23.2, humidity: 45, sensorCount: 8, alarmCount: 0, lastUpdate: '2 min ago' },
  { id: 4, name: 'Hot Aisle B', status: 'critical', statusText: 'Critical', temp: 31.5, humidity: 58, sensorCount: 8, alarmCount: 2, lastUpdate: '2 min ago' },
  { id: 5, name: 'Server Room A', status: 'warning', statusText: 'Warning', temp: 26.8, humidity: 62, sensorCount: 6, alarmCount: 1, lastUpdate: '2 min ago' },
  { id: 6, name: 'Network Room', status: 'normal', statusText: 'Normal', temp: 23.5, humidity: 44, sensorCount: 5, alarmCount: 0, lastUpdate: '2 min ago' }
])

// Sensors Data
interface EnvironmentalSensor {
  id: number
  name: string
  type: string
  zone: string
  status: string
  value: number
  unit: string
  percent: number
  minThreshold: number
  maxThreshold: number
  lastUpdate: string
  battery: number
}

const sensors = ref<EnvironmentalSensor[]>([
  { id: 1, name: 'Temp Sensor A01', type: 'temp', zone: 'Cold Aisle A', status: 'normal', value: 22.5, unit: '°C', percent: 64, minThreshold: 18, maxThreshold: 27, lastUpdate: '1 min ago', battery: 98 },
  { id: 2, name: 'Temp Sensor A02', type: 'temp', zone: 'Hot Aisle A', status: 'warning', value: 28.5, unit: '°C', percent: 81, minThreshold: 18, maxThreshold: 27, lastUpdate: '1 min ago', battery: 95 },
  { id: 3, name: 'Temp Sensor B01', type: 'temp', zone: 'Cold Aisle B', status: 'normal', value: 23.2, unit: '°C', percent: 66, minThreshold: 18, maxThreshold: 27, lastUpdate: '1 min ago', battery: 92 },
  { id: 4, name: 'Temp Sensor B02', type: 'temp', zone: 'Hot Aisle B', status: 'critical', value: 31.5, unit: '°C', percent: 90, minThreshold: 18, maxThreshold: 27, lastUpdate: '1 min ago', battery: 88 },
  { id: 5, name: 'Humidity Sensor A01', type: 'humidity', zone: 'Cold Aisle A', status: 'normal', value: 48, unit: '%', percent: 48, minThreshold: 40, maxThreshold: 60, lastUpdate: '1 min ago', battery: 96 },
  { id: 6, name: 'Humidity Sensor A02', type: 'humidity', zone: 'Hot Aisle A', status: 'normal', value: 52, unit: '%', percent: 52, minThreshold: 40, maxThreshold: 60, lastUpdate: '1 min ago', battery: 94 },
  { id: 7, name: 'Humidity Sensor B01', type: 'humidity', zone: 'Server Room A', status: 'warning', value: 62, unit: '%', percent: 62, minThreshold: 40, maxThreshold: 60, lastUpdate: '1 min ago', battery: 90 },
  { id: 8, name: 'Air Quality A01', type: 'air', zone: 'Server Room A', status: 'normal', value: 35, unit: 'μg/m³', percent: 35, minThreshold: 0, maxThreshold: 50, lastUpdate: '1 min ago', battery: 85 }
])

const filteredSensors = computed(() => {
  let filtered = sensors.value
  if (zoneFilter.value !== 'all') {
    filtered = filtered.filter(s => s.zone === zoneFilter.value)
  }
  if (sensorTypeFilter.value !== 'all') {
    filtered = filtered.filter(s => s.type === sensorTypeFilter.value)
  }
  return filtered
})

// Active Alarms
interface EnvAlarm {
  id: number
  title: string
  description: string
  severity: string
  zone: string
  sensorName: string
  value: string
  time: string
}

const activeAlarms = ref<EnvAlarm[]>([
  { id: 1, title: 'High Temperature Alert', description: 'Temperature exceeded 30°C in Hot Aisle B', severity: 'critical', zone: 'Hot Aisle B', sensorName: 'Temp Sensor B02', value: '31.5°C', time: '8 min ago' },
  { id: 2, title: 'High Humidity Warning', description: 'Humidity above 60% in Server Room A', severity: 'warning', zone: 'Server Room A', sensorName: 'Humidity Sensor B01', value: '62%', time: '15 min ago' },
  { id: 3, title: 'Elevated Temperature', description: 'Temperature above 27°C in Hot Aisle A', severity: 'warning', zone: 'Hot Aisle A', sensorName: 'Temp Sensor A02', value: '28.5°C', time: '22 min ago' },
  { id: 4, title: 'Temperature Critical', description: 'Temperature exceeds ASHRAE limits', severity: 'critical', zone: 'Hot Aisle B', sensorName: 'Temp Sensor B02', value: '31.5°C', time: '22 min ago' }
])

const activeAlarmsCount = computed(() => activeAlarms.value.length)

// Heatmap data
const hourlyHeatmapData = ref<number[][]>(Array.from({ length: 8 }, () => Array.from({ length: 24 }, () => Math.floor(20 + Math.random() * 15))))
const dailyHeatmapData = ref<number[][]>(Array.from({ length: 8 }, () => Array.from({ length: 7 }, () => Math.floor(20 + Math.random() * 15))))
const zoneLabels = ['Cold Aisle A', 'Hot Aisle A', 'Cold Aisle B', 'Hot Aisle B', 'Server Room A', 'Server Room B', 'Network Room', 'Storage Room']
const hourLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`)
const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

// ==================== Helper Functions ====================
const getTempStatusClass = (temp: number) => {
  if (temp < 18) return 'low'
  if (temp > 27) return 'high'
  return 'normal'
}

const getTempStatusText = (temp: number) => {
  if (temp < 18) return '⚠️ Below Range'
  if (temp > 27) return '⚠️ Above Range'
  return '✅ Within Range'
}

const getTempColor = (temp: number) => {
  if (temp < 18) return '#60a5fa'
  if (temp <= 27) return '#67c23a'
  if (temp <= 30) return '#e6a23c'
  return '#f56c6c'
}

const getTempWarningClass = (temp: number) => {
  if (temp > 27) return 'warning'
  if (temp < 18) return 'warning'
  return ''
}

const getHumidityStatusClass = (humidity: number) => {
  if (humidity < 40) return 'low'
  if (humidity > 60) return 'high'
  return 'normal'
}

const getHumidityStatusText = (humidity: number) => {
  if (humidity < 40) return '⚠️ Below Range'
  if (humidity > 60) return '⚠️ Above Range'
  return '✅ Within Range'
}

const getHumidityColor = (humidity: number) => {
  if (humidity < 40) return '#60a5fa'
  if (humidity <= 60) return '#67c23a'
  return '#e6a23c'
}

const getHumidityWarningClass = (humidity: number) => {
  if (humidity > 60) return 'warning'
  if (humidity < 40) return 'warning'
  return ''
}

const getAirQualityClass = (aqi: number) => {
  if (aqi <= 50) return 'good'
  if (aqi <= 100) return 'moderate'
  return 'poor'
}

const getAirQualityStatus = (aqi: number) => {
  if (aqi <= 50) return '✅ Good'
  if (aqi <= 100) return '⚠️ Moderate'
  return '❌ Poor'
}

const getComplianceColor = (score: number) => {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#e6a23c'
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

const viewZoneDetails = (zone: Zone) => {
  selectedZone.value = zone
  zoneDetailVisible.value = true
}

const viewSensorDetails = (sensor: EnvironmentalSensor) => {
  selectedSensor.value = sensor
  sensorDetailVisible.value = true
}

const acknowledgeAlarm = (alarm: EnvAlarm) => {
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

const escalateAlarm = (alarm: EnvAlarm) => {
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
const heatmapChartRef = ref<HTMLElement>()
let heatmapChart: echarts.ECharts | null = null

const initHeatmap = () => {
  nextTick(() => {
    if (!heatmapChartRef.value) {
      setTimeout(initHeatmap, 200)
      return
    }

    if (heatmapChart) heatmapChart.dispose()
    heatmapChart = echarts.init(heatmapChartRef.value)
    updateHeatmap()

    window.addEventListener('resize', () => heatmapChart?.resize())
  })
}

const updateHeatmap = () => {
  if (!heatmapChart) return

  const isHourly = heatmapPeriod.value === 'hour'
  const data = isHourly ? hourlyHeatmapData.value : dailyHeatmapData.value
  const xLabels = isHourly ? hourLabels : dayLabels
  const yLabels = zoneLabels

  const seriesData: [number, number, number][] = []
  for (let i = 0; i < yLabels.length; i++) {
    for (let j = 0; j < xLabels.length; j++) {
      seriesData.push([j, i, data[i]?.[j] || 0])
    }
  }

  heatmapChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: (params: any) => `${yLabels[params.value[1]]}<br/>${xLabels[params.value[0]]}<br/>Temperature: ${params.value[2]}°C` },
    grid: { left: '12%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: xLabels, axisLabel: { rotate: isHourly ? 45 : 0, color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: { type: 'category', data: yLabels, axisLabel: { color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    visualMap: { min: 18, max: 35, calculable: true, orient: 'vertical', left: 'left', inRange: { color: ['#60a5fa', '#67c23a', '#fbbf24', '#f97316', '#f56c6c'] }, textStyle: { color: '#606266' } },
    series: [{ type: 'heatmap', data: seriesData, label: { show: false }, emphasis: { scale: true } }]
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
          initHeatmap()
        }, 100)
      })
    }, 500)
  }, 2500)
}

watch(heatmapPeriod, () => {
  updateHeatmap()
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
.environmental-dashboard {
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

.env-icon {
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

/* Environmental Overview Cards */
.env-overview {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.env-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  cursor: pointer;
}

.env-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.env-card.temp {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.env-card.humidity {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.env-card.pressure {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.env-card.air {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.env-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.env-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.env-stats {
  flex: 1;
  margin-left: 16px;
}

.env-label {
  font-size: 13px;
  opacity: 0.85;
  margin-bottom: 4px;
}

.env-value {
  font-size: 28px;
  font-weight: 700;
}

.env-value .unit {
  font-size: 12px;
  font-weight: normal;
  margin-left: 4px;
}

.env-status {
  font-size: 11px;
  margin-top: 4px;
}

.env-status.low { color: #60a5fa; }
.env-status.high { color: #fbbf24; }
.env-status.normal { color: #67c23a; }
.env-status.good { color: #67c23a; }
.env-status.moderate { color: #e6a23c; }
.env-status.poor { color: #f56c6c; }

.env-badge {
  font-size: 32px;
}

.env-gauge {
  margin-left: 16px;
}

/* Section Title */
.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
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

.filter-group {
  display: flex;
  gap: 12px;
}

/* Zone Grid */
.zone-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.zone-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
  border-left: 4px solid #67c23a;
}

.zone-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.zone-card.critical { border-left-color: #f56c6c; }
.zone-card.warning { border-left-color: #e6a23c; }
.zone-card.normal { border-left-color: #67c23a; }

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
}

.zone-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  display: flex;
  align-items: center;
  gap: 6px;
}

.zone-status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
}

.zone-status-badge.critical { background: #fef0f0; color: #f56c6c; }
.zone-status-badge.warning { background: #fdf6ec; color: #e6a23c; }
.zone-status-badge.normal { background: #f0f9eb; color: #67c23a; }

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.zone-metrics {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.zone-metric {
  margin-bottom: 10px;
}

.zone-metric:last-child {
  margin-bottom: 0;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
  display: inline-block;
}

.metric-value.warning { color: #f56c6c; }

.metric-bar-track {
  height: 4px;
  background: #e4e7ed;
  border-radius: 2px;
  overflow: hidden;
}

.metric-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

.zone-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #fafafa;
  font-size: 10px;
  color: #909399;
}

.footer-info {
  display: flex;
  gap: 12px;
}

/* Sensor Grid */
.sensor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.sensor-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s;
  border-top: 3px solid #67c23a;
}

.sensor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.sensor-card.critical { border-top-color: #f56c6c; }
.sensor-card.warning { border-top-color: #e6a23c; }
.sensor-card.normal { border-top-color: #67c23a; }

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
}

.sensor-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  display: flex;
  align-items: center;
  gap: 6px;
}

.sensor-type-tag {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.sensor-type-tag.temp { background: #fef0f0; color: #f56c6c; }
.sensor-type-tag.humidity { background: #ecf5ff; color: #409eff; }
.sensor-type-tag.air { background: #f0f9eb; color: #67c23a; }

.sensor-reading {
  text-align: center;
  padding: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.reading-value {
  font-size: 36px;
  font-weight: 700;
  color: #1f2f3d;
}

.reading-value .unit {
  font-size: 14px;
  font-weight: normal;
  color: #909399;
}

.reading-value.critical { color: #f56c6c; }
.reading-value.warning { color: #e6a23c; }

.reading-label {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

.sensor-threshold {
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
}

.threshold-bar-track {
  height: 4px;
  background: #e4e7ed;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 6px;
}

.threshold-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

.threshold-markers {
  display: flex;
  justify-content: space-between;
  font-size: 9px;
  color: #c0c4cc;
}

.sensor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #fafafa;
  font-size: 10px;
  color: #909399;
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
  flex-wrap: wrap;
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
  margin-bottom: 24px;
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

.heatmap-container {
  width: 100%;
  height: 400px;
  padding: 16px;
}

/* ASHRAE Card */
.ashrae-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.ashrae-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.ashrae-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ashrae-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.ashrae-item {
  text-align: center;
}

.ashrae-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 6px;
}

.ashrae-value {
  font-size: 18px;
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.ashrae-status {
  font-size: 11px;
}

.ashrae-status.pass { color: #67c23a; }
.ashrae-status.fail { color: #f56c6c; }
.ashrae-status.warning { color: #e6a23c; }

/* Responsive */
@media (max-width: 1200px) {
  .env-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  .ashrae-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .environmental-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .env-overview {
    grid-template-columns: 1fr;
  }
  .zone-grid {
    grid-template-columns: 1fr;
  }
  .sensor-grid {
    grid-template-columns: 1fr;
  }
  .ashrae-metrics {
    grid-template-columns: 1fr;
  }
  .alarm-card {
    flex-direction: column;
    text-align: center;
  }
  .alarm-meta {
    justify-content: center;
  }
  .filter-group {
    flex-direction: column;
    width: 100%;
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