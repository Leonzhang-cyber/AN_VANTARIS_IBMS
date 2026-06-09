<template>
  <div class="environmental-monitoring-container">
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
            <span class="loading-title">Loading Environmental Monitoring</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Environmental Monitoring System</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="environmental-monitoring-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Environmental Monitoring</h1>
          <p class="page-subtitle">Real-time monitoring of temperature, humidity, airflow and water leakage</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
          <el-button @click="configureAlerts">
            <el-icon><Bell /></el-icon>
            Configure Alerts
          </el-button>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="hasActiveAlert" class="alert-banner" :class="alertSeverity">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ activeAlertMessage }}</span>
        <el-button size="small" :type="alertSeverity === 'critical' ? 'danger' : 'warning'" @click="viewAlertDetails">
          View Details
        </el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon blue">
                <el-icon><Grid /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Average Temperature</span>
                <span class="card-value" :style="{ color: getTempColor(avgTemperature) }">{{ avgTemperature }}°C</span>
                <el-progress :percentage="(avgTemperature / 35) * 100" :stroke-width="6" :color="getTempColor(avgTemperature)" :show-text="false" />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon green">
                <el-icon><Sunny /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Average Humidity</span>
                <span class="card-value" :style="{ color: getHumidityColor(avgHumidity) }">{{ avgHumidity }}%</span>
                <el-progress :percentage="avgHumidity" :stroke-width="6" :color="getHumidityColor(avgHumidity)" :show-text="false" />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon orange">
                <el-icon><WindPower /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Average Airflow</span>
                <span class="card-value">{{ avgAirflow }} CFM</span>
                <el-progress :percentage="(avgAirflow / 2000) * 100" :stroke-width="6" color="#f59e0b" :show-text="false" />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon red">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Water Leak Status</span>
                <span class="card-value" :style="{ color: waterLeakDetected ? '#ef4444' : '#10b981' }">
                  {{ waterLeakDetected ? 'Leak Detected' : 'Normal' }}
                </span>
                <el-progress :percentage="waterLeakDetected ? 100 : 0" :stroke-width="6" :color="waterLeakDetected ? '#ef4444' : '#10b981'" :show-text="false" />
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Sensor Map / Data Hall Layout -->
      <div class="sensor-map-section">
        <el-card class="sensor-map-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Grid /></el-icon>
              <span>Data Hall Sensor Map</span>
            </div>
            <div class="header-controls">
              <el-radio-group v-model="sensorMapLayer" size="small">
                <el-radio-button label="temperature">Temperature</el-radio-button>
                <el-radio-button label="humidity">Humidity</el-radio-button>
                <el-radio-button label="airflow">Airflow</el-radio-button>
              </el-radio-group>
              <el-button size="small" @click="resetMapView">Reset View</el-button>
            </div>
          </div>
          <div class="sensor-map-container">
            <div class="data-hall-grid">
              <!-- Row Labels -->
              <div class="row-labels">
                <div class="corner"></div>
                <div v-for="pos in 12" :key="pos" class="position-label">Pos {{ pos }}</div>
              </div>
              <!-- Rows A-D -->
              <div v-for="row in ['A', 'B', 'C', 'D']" :key="row" class="sensor-row">
                <div class="row-label">{{ row }}</div>
                <div
                    v-for="pos in 12"
                    :key="pos"
                    class="sensor-cell"
                    :class="getSensorClass(row, pos)"
                    @click="showSensorDetail(row, pos)"
                >
                  <div class="sensor-value">{{ getSensorValue(row, pos) }}</div>
                  <div class="sensor-unit">{{ getSensorUnit() }}</div>
                  <div class="sensor-status" :class="getSensorStatus(row, pos)"></div>
                </div>
              </div>
            </div>
          </div>
          <div class="map-legend">
            <div v-if="sensorMapLayer === 'temperature'" class="legend-items">
              <span class="legend-title">Temperature Scale:</span>
              <span class="legend-color" style="background: #3b82f6"></span>
              <span>&lt;18°C</span>
              <span class="legend-color" style="background: #10b981"></span>
              <span>18-22°C</span>
              <span class="legend-color" style="background: #84cc16"></span>
              <span>22-24°C</span>
              <span class="legend-color" style="background: #f59e0b"></span>
              <span>24-26°C</span>
              <span class="legend-color" style="background: #ef4444"></span>
              <span>26-28°C</span>
              <span class="legend-color" style="background: #7c2d12"></span>
              <span>&gt;28°C</span>
            </div>
            <div v-else-if="sensorMapLayer === 'humidity'" class="legend-items">
              <span class="legend-title">Humidity Scale:</span>
              <span class="legend-color" style="background: #ef4444"></span>
              <span>&lt;40%</span>
              <span class="legend-color" style="background: #84cc16"></span>
              <span>40-50%</span>
              <span class="legend-color" style="background: #10b981"></span>
              <span>50-60%</span>
              <span class="legend-color" style="background: #f59e0b"></span>
              <span>60-70%</span>
              <span class="legend-color" style="background: #ef4444"></span>
              <span>&gt;70%</span>
            </div>
            <div v-else class="legend-items">
              <span class="legend-title">Airflow Scale:</span>
              <span class="legend-color" style="background: #ef4444"></span>
              <span>&lt;500 CFM</span>
              <span class="legend-color" style="background: #f59e0b"></span>
              <span>500-800 CFM</span>
              <span class="legend-color" style="background: #84cc16"></span>
              <span>800-1200 CFM</span>
              <span class="legend-color" style="background: #10b981"></span>
              <span>1200-1500 CFM</span>
              <span class="legend-color" style="background: #3b82f6"></span>
              <span>&gt;1500 CFM</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Sensor Data Charts -->
      <div class="charts-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="chart-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><TrendCharts /></el-icon>
                  <span>Temperature & Humidity Trends</span>
                </div>
                <el-select v-model="trendZone" size="small" placeholder="Select Zone" style="width: 120px">
                  <el-option label="Zone A" value="A" />
                  <el-option label="Zone B" value="B" />
                  <el-option label="Zone C" value="C" />
                  <el-option label="Zone D" value="D" />
                  <el-option label="Average" value="avg" />
                </el-select>
              </div>
              <div class="chart-container">
                <canvas id="tempHumidityChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="chart-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataLine /></el-icon>
                  <span>Airflow Distribution</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="airflowChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Sensor List -->
      <div class="sensors-section">
        <div class="section-header">
          <h3>Sensor Network Status</h3>
          <div class="header-controls">
            <el-input v-model="sensorSearch" placeholder="Search sensor..." prefix-icon="Search" style="width: 200px" clearable />
            <el-select v-model="sensorStatusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Normal" value="normal" />
              <el-option label="Warning" value="warning" />
              <el-option label="Critical" value="critical" />
              <el-option label="Offline" value="offline" />
            </el-select>
          </div>
        </div>
        <el-table :data="filteredSensors" stripe class="sensors-table">
          <el-table-column prop="id" label="Sensor ID"  />
          <el-table-column prop="location" label="Location"  />
          <el-table-column prop="temperature" label="Temperature" >
            <template #default="{ row }">
              <span :style="{ color: getTempColor(row.temperature) }">{{ row.temperature }}°C</span>
            </template>
          </el-table-column>
          <el-table-column prop="humidity" label="Humidity" >
            <template #default="{ row }">
              <span :style="{ color: getHumidityColor(row.humidity) }">{{ row.humidity }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="airflow" label="Airflow" >
            <template #default="{ row }">
              <span :style="{ color: getAirflowColor(row.airflow) }">{{ row.airflow }} CFM</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" >
            <template #default="{ row }">
              <el-tag :type="getSensorTagType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastUpdate" label="Last Update"  />
          <el-table-column label="Actions" >
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewSensorHistory(row)">History</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Water Leak Detection -->
      <div class="water-leak-section">
        <el-card class="water-leak-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Bell /></el-icon>
              <span>Water Leak Detection System</span>
              <el-tag v-if="waterLeakDetected" type="danger" size="small">Leak Detected!</el-tag>
              <el-tag v-else type="success" size="small">All Clear</el-tag>
            </div>
            <el-button size="small" @click="testLeakSensors">Test Sensors</el-button>
          </div>
          <div class="leak-map">
            <div class="leak-zones">
              <div
                  v-for="zone in leakZones"
                  :key="zone.id"
                  class="leak-zone"
                  :class="{ alert: zone.leakDetected, warning: zone.warning }"
                  @click="viewLeakZone(zone)"
              >
                <div class="zone-name">{{ zone.name }}</div>
                <div class="zone-status">
                  <el-icon v-if="zone.leakDetected"><WarningFilled /></el-icon>
                  <el-icon v-else-if="zone.warning"><Warning /></el-icon>
                  <el-icon v-else><CircleCheck /></el-icon>
                </div>
                <div class="zone-detail">{{ zone.leakDetected ? 'Leak Detected' : zone.warning ? 'Moisture Warning' : 'Normal' }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Environmental Alerts -->
      <div class="alerts-section">
        <div class="section-header">
          <h3>Recent Environmental Alerts</h3>
          <el-button type="primary" link @click="viewAllAlerts">View All →</el-button>
        </div>
        <el-table :data="recentAlerts" stripe class="alerts-table">
          <el-table-column prop="severity" label="Severity" >
            <template #default="{ row }">
              <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'warning' ? 'warning' : 'info'" size="small">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="Alert Message" />
          <el-table-column prop="location" label="Location"  />
          <el-table-column prop="timestamp" label="Time" width="180" />
          <el-table-column label="Action" >
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="acknowledgeAlert(row)">Acknowledge</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="runDiagnostics">
          <el-icon><Cpu /></el-icon>
          Run System Diagnostics
        </el-button>
        <el-button size="large" @click="generateEnvironmentalReport">
          <el-icon><Document /></el-icon>
          Generate Environmental Report
        </el-button>
        <el-button size="large" @click="scheduleMaintenance">
          <el-icon><Tools /></el-icon>
          Schedule Maintenance
        </el-button>
      </div>
    </div>

    <!-- Sensor Detail Dialog -->
    <el-dialog v-model="sensorDetailVisible" :title="`Sensor ${selectedSensor?.id} Details`" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Location">{{ selectedSensor?.location }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getSensorTagType(selectedSensor?.status)" size="small">{{ selectedSensor?.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Temperature">{{ selectedSensor?.temperature }}°C</el-descriptions-item>
        <el-descriptions-item label="Humidity">{{ selectedSensor?.humidity }}%</el-descriptions-item>
        <el-descriptions-item label="Airflow">{{ selectedSensor?.airflow }} CFM</el-descriptions-item>
        <el-descriptions-item label="Last Update">{{ selectedSensor?.lastUpdate }}</el-descriptions-item>
        <el-descriptions-item label="Battery Level">{{ selectedSensor?.battery || 85 }}%</el-descriptions-item>
        <el-descriptions-item label="Signal Strength">{{ selectedSensor?.signal || 92 }}%</el-descriptions-item>
      </el-descriptions>
      <div class="sensor-history-chart">
        <h4>24-Hour History</h4>
        <canvas id="sensorHistoryChart" style="height: 200px"></canvas>
      </div>
      <template #footer>
        <el-button @click="sensorDetailVisible = false">Close</el-button>
        <el-button type="primary" @click="calibrateSensor">Calibrate</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Sunny, WindPower, Grid, TrendCharts, DataLine,
  Refresh, Download, Bell, WarningFilled, Warning, CircleCheck,
  Cpu, Document, Tools, Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading environmental data...')

// ==================== Reactive Data ====================
const sensorMapLayer = ref('temperature')
const trendZone = ref('avg')
const sensorSearch = ref('')
const sensorStatusFilter = ref('')
const sensorDetailVisible = ref(false)
const selectedSensor = ref<any>(null)

// Alert state
const hasActiveAlert = ref(true)
const alertSeverity = ref('warning')
const activeAlertMessage = ref('Temperature threshold exceeded in Zone B (27.5°C)')

// Environmental metrics
const avgTemperature = ref(23.8)
const avgHumidity = ref(52)
const avgAirflow = ref(1250)
const waterLeakDetected = ref(false)

// Sensor data for map (4 rows x 12 columns)
const sensorData = ref([
  // Row A
  { row: 'A', pos: 1, temp: 22.5, humidity: 48, airflow: 1350, status: 'normal' },
  { row: 'A', pos: 2, temp: 23.2, humidity: 50, airflow: 1280, status: 'normal' },
  { row: 'A', pos: 3, temp: 24.5, humidity: 52, airflow: 1180, status: 'normal' },
  { row: 'A', pos: 4, temp: 25.8, humidity: 55, airflow: 1050, status: 'warning' },
  { row: 'A', pos: 5, temp: 26.5, humidity: 58, airflow: 980, status: 'warning' },
  { row: 'A', pos: 6, temp: 24.2, humidity: 51, airflow: 1220, status: 'normal' },
  { row: 'A', pos: 7, temp: 23.5, humidity: 49, airflow: 1320, status: 'normal' },
  { row: 'A', pos: 8, temp: 22.8, humidity: 47, airflow: 1380, status: 'normal' },
  { row: 'A', pos: 9, temp: 23.0, humidity: 48, airflow: 1350, status: 'normal' },
  { row: 'A', pos: 10, temp: 23.8, humidity: 50, airflow: 1300, status: 'normal' },
  { row: 'A', pos: 11, temp: 24.5, humidity: 52, airflow: 1250, status: 'normal' },
  { row: 'A', pos: 12, temp: 25.2, humidity: 54, airflow: 1150, status: 'warning' },
  // Row B
  { row: 'B', pos: 1, temp: 23.0, humidity: 49, airflow: 1300, status: 'normal' },
  { row: 'B', pos: 2, temp: 24.5, humidity: 52, airflow: 1200, status: 'normal' },
  { row: 'B', pos: 3, temp: 27.5, humidity: 62, airflow: 850, status: 'critical' },
  { row: 'B', pos: 4, temp: 28.0, humidity: 65, airflow: 800, status: 'critical' },
  { row: 'B', pos: 5, temp: 26.5, humidity: 58, airflow: 950, status: 'warning' },
  { row: 'B', pos: 6, temp: 24.8, humidity: 53, airflow: 1180, status: 'normal' },
  { row: 'B', pos: 7, temp: 23.5, humidity: 49, airflow: 1280, status: 'normal' },
  { row: 'B', pos: 8, temp: 22.8, humidity: 47, airflow: 1350, status: 'normal' },
  { row: 'B', pos: 9, temp: 23.2, humidity: 48, airflow: 1320, status: 'normal' },
  { row: 'B', pos: 10, temp: 24.0, humidity: 50, airflow: 1280, status: 'normal' },
  { row: 'B', pos: 11, temp: 24.8, humidity: 52, airflow: 1220, status: 'normal' },
  { row: 'B', pos: 12, temp: 25.5, humidity: 55, airflow: 1120, status: 'warning' }
])

// Complete sensor list
const sensors = ref([
  { id: 'S-101', location: 'Row A-01', temperature: 22.5, humidity: 48, airflow: 1350, status: 'normal', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-102', location: 'Row A-02', temperature: 23.2, humidity: 50, airflow: 1280, status: 'normal', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-103', location: 'Row A-03', temperature: 24.5, humidity: 52, airflow: 1180, status: 'normal', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-104', location: 'Row A-04', temperature: 25.8, humidity: 55, airflow: 1050, status: 'warning', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-105', location: 'Row A-05', temperature: 26.5, humidity: 58, airflow: 980, status: 'warning', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-201', location: 'Row B-01', temperature: 23.0, humidity: 49, airflow: 1300, status: 'normal', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-202', location: 'Row B-02', temperature: 24.5, humidity: 52, airflow: 1200, status: 'normal', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-203', location: 'Row B-03', temperature: 27.5, humidity: 62, airflow: 850, status: 'critical', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-204', location: 'Row B-04', temperature: 28.0, humidity: 65, airflow: 800, status: 'critical', lastUpdate: '2024-01-15 14:23:15' },
  { id: 'S-205', location: 'Row B-05', temperature: 26.5, humidity: 58, airflow: 950, status: 'warning', lastUpdate: '2024-01-15 14:23:15' }
])

// Leak zones
const leakZones = ref([
  { id: 1, name: 'Zone A - CRAC 1', leakDetected: false, warning: false },
  { id: 2, name: 'Zone B - CRAC 2', leakDetected: false, warning: true },
  { id: 3, name: 'Zone C - CRAC 3', leakDetected: false, warning: false },
  { id: 4, name: 'Zone D - CRAC 4', leakDetected: false, warning: false },
  { id: 5, name: 'Underfloor - North', leakDetected: false, warning: false },
  { id: 6, name: 'Underfloor - South', leakDetected: false, warning: false }
])

// Recent alerts
const recentAlerts = ref([
  { severity: 'warning', message: 'Temperature threshold exceeded in Zone B', location: 'Row B-03', timestamp: '2024-01-15 14:23:15' },
  { severity: 'critical', message: 'High temperature alert - critical threshold reached', location: 'Row B-04', timestamp: '2024-01-15 14:20:30' },
  { severity: 'info', message: 'Humidity sensor recalibrated', location: 'Row A-01', timestamp: '2024-01-15 13:45:00' },
  { severity: 'warning', message: 'Airflow below optimal level', location: 'Row B-02', timestamp: '2024-01-15 13:30:22' }
])

// Computed
const filteredSensors = computed(() => {
  let result = sensors.value

  if (sensorSearch.value) {
    result = result.filter(s =>
        s.id.toLowerCase().includes(sensorSearch.value.toLowerCase()) ||
        s.location.toLowerCase().includes(sensorSearch.value.toLowerCase())
    )
  }

  if (sensorStatusFilter.value) {
    result = result.filter(s => s.status === sensorStatusFilter.value)
  }

  return result
})

// Helper functions
const getTempColor = (temp: number) => {
  if (temp < 18) return '#3b82f6'
  if (temp < 22) return '#10b981'
  if (temp < 24) return '#84cc16'
  if (temp < 26) return '#f59e0b'
  if (temp < 28) return '#ef4444'
  return '#7c2d12'
}

const getHumidityColor = (humidity: number) => {
  if (humidity < 40) return '#ef4444'
  if (humidity < 50) return '#84cc16'
  if (humidity < 60) return '#10b981'
  if (humidity < 70) return '#f59e0b'
  return '#ef4444'
}

const getAirflowColor = (airflow: number) => {
  if (airflow < 500) return '#ef4444'
  if (airflow < 800) return '#f59e0b'
  if (airflow < 1200) return '#84cc16'
  if (airflow < 1500) return '#10b981'
  return '#3b82f6'
}

const getSensorTagType = (status: string) => {
  if (status === 'critical') return 'danger'
  if (status === 'warning') return 'warning'
  return 'success'
}

const getSensorValue = (row: string, pos: number) => {
  const sensor = sensorData.value.find(s => s.row === row && s.pos === pos)
  if (!sensor) return '--'
  if (sensorMapLayer.value === 'temperature') return sensor.temp.toFixed(1)
  if (sensorMapLayer.value === 'humidity') return sensor.humidity
  return sensor.airflow
}

const getSensorUnit = () => {
  if (sensorMapLayer.value === 'temperature') return '°C'
  if (sensorMapLayer.value === 'humidity') return '%'
  return 'CFM'
}

const getSensorStatus = (row: string, pos: number) => {
  const sensor = sensorData.value.find(s => s.row === row && s.pos === pos)
  return sensor?.status || 'normal'
}

const getSensorClass = (row: string, pos: number) => {
  const sensor = sensorData.value.find(s => s.row === row && s.pos === pos)
  if (!sensor) return ''
  if (sensorMapLayer.value === 'temperature') {
    if (sensor.temp < 22) return 'temp-good'
    if (sensor.temp < 24) return 'temp-optimal'
    if (sensor.temp < 26) return 'temp-warning'
    if (sensor.temp < 28) return 'temp-critical'
    return 'temp-danger'
  } else if (sensorMapLayer.value === 'humidity') {
    if (sensor.humidity < 40) return 'humidity-low'
    if (sensor.humidity < 60) return 'humidity-good'
    return 'humidity-high'
  } else {
    if (sensor.airflow < 800) return 'airflow-low'
    if (sensor.airflow < 1200) return 'airflow-medium'
    return 'airflow-good'
  }
}

// Chart instances
let tempHumidityChart: echarts.ECharts | null = null
let airflowChart: echarts.ECharts | null = null
let sensorHistoryChart: echarts.ECharts | null = null

// Chart initialization
const initTempHumidityChart = () => {
  const canvas = document.getElementById('tempHumidityChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 350

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (tempHumidityChart) tempHumidityChart.dispose()
  tempHumidityChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const hours = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']

  tempHumidityChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperature (°C)', 'Humidity (%)'], bottom: 0, left: 'center' },
    grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: hours, axisLabel: { fontSize: 11 } },
    yAxis: [
      { type: 'value', name: 'Temperature (°C)', min: 18, max: 32, axisLabel: { fontSize: 11 } },
      { type: 'value', name: 'Humidity (%)', min: 30, max: 80, axisLabel: { fontSize: 11 } }
    ],
    series: [
      { name: 'Temperature (°C)', type: 'line', data: [23.2, 23.0, 22.8, 22.5, 23.2, 24.0, 24.8, 25.5, 25.2, 24.5, 23.8, 23.5], smooth: true, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Humidity (%)', type: 'line', yAxisIndex: 1, data: [52, 51, 50, 49, 51, 53, 55, 58, 56, 54, 53, 52], smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle', symbolSize: 6 }
    ]
  })
}

const initAirflowChart = () => {
  const canvas = document.getElementById('airflowChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 350

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (airflowChart) airflowChart.dispose()
  airflowChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const rows = ['Row A', 'Row B', 'Row C', 'Row D']
  const rowAirflow = [1250, 950, 1180, 1320]

  airflowChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: rows, axisLabel: { fontSize: 12 } },
    yAxis: { type: 'value', name: 'Airflow (CFM)', axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar', data: rowAirflow,
      itemStyle: { borderRadius: [8, 8, 0, 0], color: (params: any) => getAirflowColor(params.data) },
      label: { show: true, position: 'top', formatter: '{c} CFM' }
    }]
  })
}

const showSensorDetail = (row: string, pos: number) => {
  const sensor = sensorData.value.find(s => s.row === row && s.pos === pos)
  if (sensor) {
    selectedSensor.value = {
      id: `S-${row}${pos.toString().padStart(2, '0')}`,
      location: `${row}${pos.toString().padStart(2, '0')}`,
      temperature: sensor.temp,
      humidity: sensor.humidity,
      airflow: sensor.airflow,
      status: sensor.status,
      lastUpdate: new Date().toLocaleString()
    }
    sensorDetailVisible.value = true
    setTimeout(() => initSensorHistoryChart(), 100)
  }
}

const initSensorHistoryChart = () => {
  const canvas = document.getElementById('sensorHistoryChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 200

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (sensorHistoryChart) sensorHistoryChart.dispose()
  sensorHistoryChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const hours = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
  const temps = [23.5, 23.2, 24.0, 25.5, 26.0, 25.2]

  sensorHistoryChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: hours },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [{
      type: 'line', data: temps, smooth: true, lineStyle: { color: '#ef4444', width: 2 },
      areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 6,
      markLine: { data: [{ yAxis: 26, name: 'Warning', lineStyle: { color: '#f59e0b', type: 'dashed' } }] }
    }]
  })
}

// Actions
const refreshData = () => {
  ElMessage.success('Data refreshed')
}

const exportReport = () => {
  ElMessage.success('Report export started')
}

const configureAlerts = () => {
  ElMessage.info('Alert configuration interface will open')
}

const viewAlertDetails = () => {
  ElMessage.info('Viewing alert details')
}

const resetMapView = () => {
  ElMessage.success('Map view reset')
}

const testLeakSensors = () => {
  ElMessage.info('Testing leak detection sensors...')
}

const viewLeakZone = (zone: any) => {
  ElMessage.info(`Viewing details for ${zone.name}`)
}

const viewAllAlerts = () => {
  ElMessage.info('Viewing all alerts')
}

const acknowledgeAlert = (alert: any) => {
  ElMessage.success(`Alert acknowledged: ${alert.message}`)
}

const viewSensorHistory = (sensor: any) => {
  selectedSensor.value = sensor
  sensorDetailVisible.value = true
  setTimeout(() => initSensorHistoryChart(), 100)
}

const calibrateSensor = () => {
  ElMessage.success('Sensor calibration initiated')
  sensorDetailVisible.value = false
}

const runDiagnostics = () => {
  ElMessage.success('System diagnostics started')
}

const generateEnvironmentalReport = () => {
  ElMessage.success('Environmental report generation started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Maintenance scheduling interface will open')
}

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (tempHumidityChart) tempHumidityChart.resize()
    if (airflowChart) airflowChart.resize()
    if (sensorHistoryChart) sensorHistoryChart.resize()
  }, 200)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initTempHumidityChart()
          initAirflowChart()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  if (tempHumidityChart) tempHumidityChart.dispose()
  if (airflowChart) airflowChart.dispose()
  if (sensorHistoryChart) sensorHistoryChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.environmental-monitoring-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
}

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
  font-size: 24px;
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
  width: 320px;
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
.environmental-monitoring-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Alert Banner */
.alert-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.alert-banner.critical {
  background: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #dc2626;
}

.alert-banner.warning {
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
  color: #d97706;
}

.alert-banner .el-icon {
  font-size: 20px;
}

.alert-banner span {
  flex: 1;
  font-weight: 500;
}

/* Overview Cards */
.overview-section {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.card-icon.blue { background: #eff6ff; color: #3b82f6; }
.card-icon.green { background: #ecfdf5; color: #10b981; }
.card-icon.orange { background: #fffbeb; color: #f59e0b; }
.card-icon.red { background: #fef2f2; color: #ef4444; }

.card-info {
  flex: 1;
}

.card-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.card-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

/* Sensor Map Section */
.sensor-map-section {
  margin-bottom: 24px;
}

.sensor-map-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.card-title .el-icon {
  font-size: 18px;
  color: #3b82f6;
}

.header-controls {
  display: flex;
  gap: 12px;
}

.sensor-map-container {
  overflow-x: auto;
}

.data-hall-grid {
  min-width: 800px;
}

.row-labels,
.sensor-row {
  display: flex;
  margin-bottom: 4px;
}

.corner {
  width: 60px;
}

.position-label {
  width: 80px;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: #64748b;
  padding: 8px;
}

.row-label {
  width: 60px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sensor-cell {
  width: 80px;
  height: 70px;
  margin: 2px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  color: white;
}

.sensor-cell:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.sensor-cell.temp-good { background: #3b82f6; }
.sensor-cell.temp-optimal { background: #10b981; }
.sensor-cell.temp-warning { background: #f59e0b; }
.sensor-cell.temp-critical { background: #ef4444; }
.sensor-cell.temp-danger { background: #7c2d12; }
.sensor-cell.humidity-low { background: #ef4444; }
.sensor-cell.humidity-good { background: #10b981; }
.sensor-cell.humidity-high { background: #f59e0b; }
.sensor-cell.airflow-low { background: #ef4444; }
.sensor-cell.airflow-medium { background: #f59e0b; }
.sensor-cell.airflow-good { background: #10b981; }

.sensor-value {
  font-size: 16px;
  font-weight: 700;
}

.sensor-unit {
  font-size: 10px;
  opacity: 0.9;
}

.sensor-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 4px;
}

.sensor-status.normal { background: #10b981; box-shadow: 0 0 4px #10b981; }
.sensor-status.warning { background: #f59e0b; box-shadow: 0 0 4px #f59e0b; }
.sensor-status.critical { background: #ef4444; box-shadow: 0 0 4px #ef4444; }

.map-legend {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.legend-items {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.legend-title {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 4px;
}

/* Charts Section */
.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-container {
  width: 100%;
  min-height: 350px;
  position: relative;
}

/* Sensors Section */
.sensors-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.sensors-table {
  border-radius: 16px;
  overflow: hidden;
}

/* Water Leak Section */
.water-leak-section {
  margin-bottom: 24px;
}

.water-leak-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.leak-map {
  margin-top: 16px;
}

.leak-zones {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.leak-zone {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 4px solid #10b981;
}

.leak-zone:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.leak-zone.alert {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.leak-zone.warning {
  border-left-color: #f59e0b;
  background: #fffbeb;
}

.zone-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.zone-status {
  font-size: 24px;
  margin-bottom: 4px;
}

.zone-detail {
  font-size: 11px;
  color: #64748b;
}

/* Alerts Section */
.alerts-section {
  margin-bottom: 24px;
}

.alerts-table {
  border-radius: 16px;
  overflow: hidden;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 20px;
}

/* Sensor History Chart */
.sensor-history-chart {
  margin-top: 20px;
}

.sensor-history-chart h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px 0;
}

/* Responsive */
@media (max-width: 1200px) {
  .environmental-monitoring-main { padding: 16px; }
  .sensor-cell { width: 60px; height: 60px; }
  .position-label { width: 60px; }
  .sensor-value { font-size: 14px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .sensor-cell { width: 50px; height: 55px; }
  .position-label { width: 50px; font-size: 9px; }
  .sensor-value { font-size: 12px; }
  .leak-zones { grid-template-columns: 1fr; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>