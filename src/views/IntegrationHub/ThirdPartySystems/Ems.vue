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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">EMS Integration</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ems-integration-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Third-Party Systems</el-breadcrumb-item>
            <el-breadcrumb-item>EMS</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>EMS Integration</h1>
        <p class="description">Integrate with Energy Management Systems for consumption monitoring, carbon tracking, and efficiency analysis</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="primary" @click="openAddConnectionDialog">
          <el-icon><Plus /></el-icon>
          Add Connection
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <span>{{ stat.subTitle }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- EMS Platform Cards -->
    <el-row :gutter="20" class="ems-cards-row">
      <el-col :xs="24" :sm="12" :lg="8" v-for="ems in emsPlatforms" :key="ems.name">
        <el-card class="ems-card" shadow="hover" @click="selectEMSPlatform(ems)">
          <div class="ems-card-content">
            <div class="ems-icon" :style="{ background: ems.color }">
              <el-icon :size="32"><component :is="ems.icon" /></el-icon>
            </div>
            <div class="ems-info">
              <div class="ems-name">{{ ems.name }}</div>
              <div class="ems-status">
                <el-tag :type="ems.status === 'Connected' ? 'success' : 'danger'" size="small">
                  {{ ems.status }}
                </el-tag>
              </div>
              <div class="ems-version">{{ ems.version }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Energy Dashboard -->
    <el-row :gutter="20" class="dashboard-row">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Energy Consumption Trend</span>
              <div class="chart-controls">
                <el-radio-group v-model="trendPeriod" size="small">
                  <el-radio-button value="daily">Daily</el-radio-button>
                  <el-radio-button value="weekly">Weekly</el-radio-button>
                  <el-radio-button value="monthly">Monthly</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </template>
          <div ref="consumptionChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Energy Summary</span>
            </div>
          </template>
          <div class="energy-summary">
            <div class="summary-item">
              <div class="summary-label">Total Consumption</div>
              <div class="summary-value">1,245,678 kWh</div>
              <div class="summary-trend up">+8.5% vs last month</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">Peak Demand</div>
              <div class="summary-value">1,850 kW</div>
              <div class="summary-trend up">+5.2% vs last month</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">Avg Power Factor</div>
              <div class="summary-value">0.95</div>
              <div class="summary-trend up">+0.02</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">CO₂ Emissions</div>
              <div class="summary-value">425 tCO₂e</div>
              <div class="summary-trend down">-12% vs last month</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Carbon Emissions Gauge -->
    <el-row :gutter="20" class="carbon-row">
      <el-col :xs="24" :lg="8">
        <el-card class="gauge-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Carbon Reduction Target</span>
            </div>
          </template>
          <div ref="carbonGaugeRef" class="gauge-container"></div>
          <div class="target-info">
            <span>Target: 30% reduction by 2025</span>
            <span>Current: 18% reduction</span>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="16">
        <el-card class="pie-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Consumption by Category</span>
            </div>
          </template>
          <div ref="pieChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- EMS Connections Table -->
    <el-card class="connections-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>EMS Connections</span>
          <div class="connections-actions">
            <el-input
                v-model="connectionSearch"
                placeholder="Search connections"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-select v-model="connectionStatusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Connected" value="Connected" />
              <el-option label="Disconnected" value="Disconnected" />
              <el-option label="Error" value="Error" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchConnections" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedConnections" stripe style="width: 100%" v-loading="connectionsLoading">
        <el-table-column prop="name" label="Connection Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="platform" label="Platform" width="140">
          <template #default="{ row }">
            <el-tag :type="getPlatformTag(row.platform)" size="small">{{ row.platform }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="endpoint" label="Endpoint" min-width="200" show-overflow-tooltip />
        <el-table-column prop="meterCount" label="Meters" width="90" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Connected' ? 'success' : row.status === 'Error' ? 'danger' : 'info'" size="small">
              <span class="status-dot" :class="row.status === 'Connected' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastSync" label="Last Sync" width="150" />
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewMeters(row)">Meters</el-button>
            <el-button link type="success" size="small" @click="viewDataPoints(row)">Data Points</el-button>
            <el-button link type="info" size="small" @click="testConnection(row)">Test</el-button>
            <el-button link type="danger" size="small" @click="deleteConnection(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="connectionsPage"
            v-model:page-size="connectionsPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="filteredConnections.length"
            @size-change="connectionsPage = 1"
        />
      </div>
    </el-card>

    <!-- Meters Table -->
    <el-card class="meters-card" shadow="hover" v-if="selectedConnection">
      <template #header>
        <div class="card-header">
          <span>Energy Meters - {{ selectedConnection.name }}</span>
          <div class="meters-actions">
            <el-button size="small" type="primary" @click="openAddMeterDialog">
              <el-icon><Plus /></el-icon> Add Meter
            </el-button>
            <el-button size="small" @click="refreshMeters">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="energyMeters" stripe size="small" v-loading="metersLoading">
        <el-table-column prop="meterId" label="Meter ID" width="140" />
        <el-table-column prop="name" label="Meter Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getMeterTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="Location" width="150" />
        <el-table-column prop="currentReading" label="Current Reading" width="140" align="right">
          <template #default="{ row }">
            {{ row.currentReading.toLocaleString() }} kWh
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewMeterData(row)">Data</el-button>
            <el-button link type="danger" size="small" @click="deleteMeter(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Data Points Table -->
    <el-card class="datapoints-card" shadow="hover" v-if="showDataPoints">
      <template #header>
        <div class="card-header">
          <span>Energy Data Points - {{ selectedConnection?.name }}</span>
          <div class="datapoints-actions">
            <el-button size="small" @click="showDataPoints = false">Close</el-button>
          </div>
        </div>
      </template>

      <el-table :data="energyDataPoints" stripe size="small" v-loading="dataPointsLoading">
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="meterName" label="Meter" width="180" show-overflow-tooltip />
        <el-table-column prop="consumption" label="Consumption (kWh)" width="150" align="right" />
        <el-table-column prop="cost" label="Cost (USD)" width="120" align="right" />
        <el-table-column prop="co2" label="CO₂ (kg)" width="100" align="right" />
        <el-table-column prop="quality" label="Quality" width="100">
          <template #default="{ row }">
            <el-tag :type="row.quality === 'Good' ? 'success' : 'warning'" size="small">{{ row.quality }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="dataPointsPage"
            v-model:page-size="dataPointsPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="energyDataPoints.length"
            @size-change="dataPointsPage = 1"
        />
      </div>
    </el-card>

    <!-- Add Connection Dialog -->
    <el-dialog v-model="connectionDialogVisible" title="Add EMS Connection" width="600px" destroy-on-close>
      <el-form :model="connectionForm" :rules="connectionRules" ref="connectionFormRef" label-width="130px">
        <el-form-item label="Connection Name" prop="name">
          <el-input v-model="connectionForm.name" placeholder="Enter connection name" />
        </el-form-item>
        <el-form-item label="EMS Platform" prop="platform">
          <el-select v-model="connectionForm.platform" style="width: 100%">
            <el-option label="Schneider Electric EMS" value="Schneider EMS" />
            <el-option label="Siemens EMS" value="Siemens EMS" />
            <el-option label="Honeywell EMS" value="Honeywell EMS" />
            <el-option label="Johnson Controls EMS" value="Johnson Controls EMS" />
            <el-option label="ABB EMS" value="ABB EMS" />
          </el-select>
        </el-form-item>
        <el-form-item label="API Endpoint" prop="endpoint">
          <el-input v-model="connectionForm.endpoint" placeholder="https://ems.example.com/api/v1" />
        </el-form-item>
        <el-form-item label="API Key" prop="apiKey">
          <el-input v-model="connectionForm.apiKey" placeholder="Enter API key" />
        </el-form-item>
        <el-form-item label="API Secret" prop="apiSecret">
          <el-input v-model="connectionForm.apiSecret" type="password" placeholder="Enter API secret" />
        </el-form-item>
        <el-form-item label="Poll Interval (s)" prop="pollInterval">
          <el-input-number v-model="connectionForm.pollInterval" :min="30" :max="3600" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="connectionForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="connectionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testEMSConnection">Test Connection</el-button>
        <el-button type="success" @click="saveConnection">Save Connection</el-button>
      </template>
    </el-dialog>

    <!-- Add Meter Dialog -->
    <el-dialog v-model="meterDialogVisible" title="Add Energy Meter" width="550px" destroy-on-close>
      <el-form :model="meterForm" :rules="meterRules" ref="meterFormRef" label-width="120px">
        <el-form-item label="Meter ID" prop="meterId">
          <el-input v-model="meterForm.meterId" placeholder="Enter meter ID" />
        </el-form-item>
        <el-form-item label="Meter Name" prop="name">
          <el-input v-model="meterForm.name" placeholder="Enter meter name" />
        </el-form-item>
        <el-form-item label="Meter Type" prop="type">
          <el-select v-model="meterForm.type" style="width: 100%">
            <el-option label="Electricity" value="Electricity" />
            <el-option label="Water" value="Water" />
            <el-option label="Gas" value="Gas" />
            <el-option label="Steam" value="Steam" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location" prop="location">
          <el-input v-model="meterForm.location" placeholder="Building, floor, room" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="meterForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="meterDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveMeter">Save Meter</el-button>
      </template>
    </el-dialog>

    <!-- Meter Data Dialog -->
    <el-dialog v-model="meterDataDialogVisible" title="Meter Data" width="700px" destroy-on-close>
      <div class="meter-data-container">
        <div ref="meterChartRef" class="meter-chart-container"></div>
        <el-table :data="meterHistory" size="small" border max-height="300">
          <el-table-column prop="date" label="Date" width="120" />
          <el-table-column prop="consumption" label="Consumption (kWh)" width="150" align="right" />
          <el-table-column prop="cost" label="Cost (USD)" width="120" align="right" />
          <el-table-column prop="co2" label="CO₂ (kg)" width="100" align="right" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="meterDataDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportMeterData">Export Data</el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Connection Successful' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Platform:</strong> {{ testResult.details.platform }}</p>
          <p><strong>Version:</strong> {{ testResult.details.version }}</p>
          <p><strong>Response Time:</strong> {{ testResult.details.responseTime }}ms</p>
          <p><strong>Meters Found:</strong> {{ testResult.details.meterCount }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, Connection, Edit, DataAnalysis, Monitor, Share,
  Location, Grid
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing EMS integration...', 'Loading energy data...', 'Almost ready...']

// ==================== Chart References ====================
const consumptionChartRef = ref<HTMLElement>()
const carbonGaugeRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
const meterChartRef = ref<HTMLElement>()
let consumptionChart: echarts.ECharts | null = null
let carbonGauge: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null
let meterChart: echarts.ECharts | null = null

// ==================== State ====================
const connectionsLoading = ref(false)
const metersLoading = ref(false)
const dataPointsLoading = ref(false)
const connectionDialogVisible = ref(false)
const meterDialogVisible = ref(false)
const meterDataDialogVisible = ref(false)
const testDialogVisible = ref(false)
const showDataPoints = ref(false)
const selectedConnection = ref<any>(null)
const selectedMeter = ref<any>(null)
const connectionSearch = ref('')
const connectionStatusFilter = ref('')
const trendPeriod = ref('daily')
const connectionsPage = ref(1)
const connectionsPageSize = ref(10)
const dataPointsPage = ref(1)
const dataPointsPageSize = ref(15)

const connectionFormRef = ref()
const meterFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// Mock data
const statsCards = ref([
  { title: 'EMS Connections', value: '5', trend: 2, icon: 'Connection', bgColor: '#409eff', key: 'connections', subTitle: 'Active: 4' },
  { title: 'Energy Meters', value: '28', trend: 4, icon: 'Grid', bgColor: '#67c23a', key: 'meters', subTitle: 'Online: 26' },
  { title: 'Total Consumption', value: '1.24M kWh', trend: 8, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'consumption', subTitle: 'Last 30 days' },
  { title: 'CO₂ Reduction', value: '12.5%', trend: 3, icon: 'Checked', bgColor: '#f56c6c', key: 'reduction', subTitle: 'Year over year' }
])

const emsPlatforms = ref([
  { name: 'Schneider EMS', icon: 'DataAnalysis', color: '#409eff', status: 'Connected', version: '2023.2' },
  { name: 'Siemens EMS', icon: 'Monitor', color: '#67c23a', status: 'Connected', version: '8.0' },
  { name: 'Honeywell EMS', icon: 'Share', color: '#e6a23c', status: 'Connected', version: '3.1' }
])

const emsConnections = ref([
  { id: 1, name: 'Main Building EMS', platform: 'Schneider EMS', endpoint: 'https://ems.schneider.com/api', meterCount: 12, status: 'Connected', lastSync: '2024-01-20 10:30:00' },
  { id: 2, name: 'Factory EMS', platform: 'Siemens EMS', endpoint: 'https://ems.siemens.com/api', meterCount: 8, status: 'Connected', lastSync: '2024-01-20 10:28:00' },
  { id: 3, name: 'Data Center EMS', platform: 'Honeywell EMS', endpoint: 'https://ems.honeywell.com/api', meterCount: 6, status: 'Error', lastSync: '2024-01-20 10:25:00' },
  { id: 4, name: 'Office Building EMS', platform: 'ABB EMS', endpoint: 'https://ems.abb.com/api', meterCount: 4, status: 'Connected', lastSync: '2024-01-20 10:32:00' }
])

const energyMeters = ref([
  { id: 1, meterId: 'MTR-001', name: 'Main Utility Meter', type: 'Electricity', location: 'Building A - Basement', currentReading: 1245000, status: 'Online' },
  { id: 2, meterId: 'MTR-002', name: 'HVAC Sub-meter', type: 'Electricity', location: 'Building A - Floor 2', currentReading: 345000, status: 'Online' },
  { id: 3, meterId: 'MTR-003', name: 'Lighting Sub-meter', type: 'Electricity', location: 'Building A - Floor 1', currentReading: 156000, status: 'Online' },
  { id: 4, meterId: 'MTR-004', name: 'Water Main', type: 'Water', location: 'Building A - Basement', currentReading: 89000, status: 'Online' }
])

const energyDataPoints = ref([
  { timestamp: '2024-01-20 10:00:00', meterName: 'Main Utility Meter', consumption: 12500, cost: 1250, co2: 5250, quality: 'Good' },
  { timestamp: '2024-01-20 09:00:00', meterName: 'Main Utility Meter', consumption: 12300, cost: 1230, co2: 5166, quality: 'Good' },
  { timestamp: '2024-01-20 08:00:00', meterName: 'Main Utility Meter', consumption: 12800, cost: 1280, co2: 5376, quality: 'Good' }
])

const meterHistory = ref([
  { date: '2024-01-15', consumption: 12500, cost: 1250, co2: 5250 },
  { date: '2024-01-16', consumption: 12300, cost: 1230, co2: 5166 },
  { date: '2024-01-17', consumption: 12800, cost: 1280, co2: 5376 },
  { date: '2024-01-18', consumption: 12600, cost: 1260, co2: 5292 }
])

// ==================== Computed ====================
const filteredConnections = computed(() => {
  let filtered = [...emsConnections.value]
  if (connectionSearch.value) filtered = filtered.filter(c => c.name.toLowerCase().includes(connectionSearch.value.toLowerCase()))
  if (connectionStatusFilter.value) filtered = filtered.filter(c => c.status === connectionStatusFilter.value)
  return filtered
})

const paginatedConnections = computed(() => {
  const start = (connectionsPage.value - 1) * connectionsPageSize.value
  const end = start + connectionsPageSize.value
  return filteredConnections.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getPlatformTag = (platform: string) => {
  const map: Record<string, string> = {
    'Schneider EMS': 'primary',
    'Siemens EMS': 'success',
    'Honeywell EMS': 'warning',
    'Johnson Controls EMS': 'info',
    'ABB EMS': 'danger'
  }
  return map[platform] || 'info'
}

const getMeterTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Electricity': 'primary',
    'Water': 'info',
    'Gas': 'warning',
    'Steam': 'danger'
  }
  return map[type] || 'info'
}

const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting EMS data...')
}

const selectEMSPlatform = (ems: any) => {
  ElMessage.info(`Selected ${ems.name} - ${ems.status}`)
}

const fetchConnections = () => {
  connectionsLoading.value = true
  setTimeout(() => {
    connectionsLoading.value = false
    ElMessage.success('Connections refreshed')
  }, 500)
}

const openAddConnectionDialog = () => {
  connectionDialogVisible.value = true
}

const testEMSConnection = () => {
  ElMessage.info('Testing EMS connection...')
  setTimeout(() => {
    testResult.success = true
    testResult.message = 'Successfully connected to EMS system'
    testResult.details = {
      platform: connectionForm.platform,
      version: '2023.1',
      responseTime: 345,
      meterCount: 24
    }
    testDialogVisible.value = true
  }, 1500)
}

const saveConnection = async () => {
  if (!connectionFormRef.value) return
  await connectionFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Connection saved successfully')
      connectionDialogVisible.value = false
      connectionFormRef.value?.resetFields()
    }
  })
}

const testConnection = (connection: any) => {
  ElMessage.info(`Testing connection to ${connection.name}...`)
  setTimeout(() => {
    ElMessage.success(`${connection.name} is ${connection.status}`)
  }, 1000)
}

const deleteConnection = (connection: any) => {
  ElMessageBox.confirm(`Delete connection "${connection.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = emsConnections.value.findIndex(c => c.id === connection.id)
    if (index !== -1) {
      emsConnections.value.splice(index, 1)
      ElMessage.success(`Deleted: ${connection.name}`)
    }
  }).catch(() => {})
}

const viewMeters = (connection: any) => {
  selectedConnection.value = connection
  refreshMeters()
}

const viewDataPoints = (connection: any) => {
  selectedConnection.value = connection
  showDataPoints.value = true
  dataPointsLoading.value = true
  setTimeout(() => {
    dataPointsLoading.value = false
  }, 500)
}

const refreshMeters = () => {
  metersLoading.value = true
  setTimeout(() => {
    metersLoading.value = false
    ElMessage.success('Meters refreshed')
  }, 500)
}

const openAddMeterDialog = () => {
  meterDialogVisible.value = true
}

const saveMeter = async () => {
  if (!meterFormRef.value) return
  await meterFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Meter added successfully')
      meterDialogVisible.value = false
      meterFormRef.value?.resetFields()
      refreshMeters()
    }
  })
}

const deleteMeter = (meter: any) => {
  ElMessageBox.confirm(`Delete meter "${meter.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = energyMeters.value.findIndex(m => m.id === meter.id)
    if (index !== -1) {
      energyMeters.value.splice(index, 1)
      ElMessage.success(`Deleted: ${meter.name}`)
    }
  }).catch(() => {})
}

const viewMeterData = (meter: any) => {
  selectedMeter.value = meter
  meterDataDialogVisible.value = true
  nextTick(() => {
    if (meterChartRef.value) {
      if (meterChart) meterChart.dispose()
      meterChart = echarts.init(meterChartRef.value)
      meterChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
        yAxis: { type: 'value', name: 'kWh' },
        series: [{ type: 'line', data: [12500, 12300, 12800, 12600, 12400, 11200, 10800], smooth: true, lineStyle: { width: 2, color: '#409eff' }, areaStyle: { opacity: 0.1 } }]
      })
    }
  })
}

const exportMeterData = () => {
  ElMessage.success('Exporting meter data...')
}

// ==================== Chart Initializations ====================
const initConsumptionChart = () => {
  if (!consumptionChartRef.value) return
  if (consumptionChart) consumptionChart.dispose()

  consumptionChart = echarts.init(consumptionChartRef.value)

  const dailyData = [12500, 12300, 12800, 12600, 12400, 12200, 12100, 12300, 12500, 12700, 12600, 12400, 12200, 12100, 12300, 12500, 12400, 12600, 12800, 12700, 12500, 12300, 12200, 12100, 12300, 12400, 12600, 12500, 12400, 12300]
  const weeklyData = [87500, 86400, 86800, 87200, 88000, 87500, 87000, 86500]
  const monthlyData = [124500, 123800, 125200, 124900, 126100, 125500, 124700, 125800]

  let data, xAxisData
  if (trendPeriod.value === 'daily') {
    data = dailyData
    xAxisData = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
  } else if (trendPeriod.value === 'weekly') {
    data = weeklyData
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8']
  } else {
    data = monthlyData
    xAxisData = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData, axisLabel: { rotate: trendPeriod.value === 'daily' ? 45 : 0 } },
    yAxis: { type: 'value', name: 'kWh' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbolSize: 6
    }]
  }

  consumptionChart.setOption(option)
  window.addEventListener('resize', () => consumptionChart?.resize())
}

const initCarbonGauge = () => {
  if (!carbonGaugeRef.value) return
  if (carbonGauge) carbonGauge.dispose()

  carbonGauge = echarts.init(carbonGaugeRef.value)

  const option: echarts.EChartsOption = {
    series: [{
      type: 'gauge',
      center: ['50%', '50%'],
      radius: '70%',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 5,
      progress: { show: true, width: 18, itemStyle: { color: '#67c23a' } },
      axisLine: { lineStyle: { width: 18, color: [[0.18, '#67c23a'], [1, '#e6e9f0']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { show: true, offsetCenter: [0, 20], valueAnimation: true, fontSize: 24, fontWeight: 'bold', color: '#303133' },
      title: { show: true, offsetCenter: [0, -20], fontSize: 14, color: '#909399' },
      data: [{ value: 18, name: 'Reduction %' }]
    }]
  }

  carbonGauge.setOption(option)
  window.addEventListener('resize', () => carbonGauge?.resize())
}

const initPieChart = () => {
  if (!pieChartRef.value) return
  if (pieChart) pieChart.dispose()

  pieChart = echarts.init(pieChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} kWh)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 425000, name: 'HVAC', itemStyle: { color: '#f56c6c' } },
        { value: 245000, name: 'Lighting', itemStyle: { color: '#e6a23c' } },
        { value: 185000, name: 'IT Equipment', itemStyle: { color: '#409eff' } },
        { value: 125000, name: 'Pumps & Fans', itemStyle: { color: '#67c23a' } },
        { value: 85000, name: 'Other', itemStyle: { color: '#909399' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  pieChart.setOption(option)
  window.addEventListener('resize', () => pieChart?.resize())
}

// ==================== Forms ====================
const connectionForm = reactive({
  name: '',
  platform: '',
  endpoint: '',
  apiKey: '',
  apiSecret: '',
  pollInterval: 60,
  description: ''
})

const meterForm = reactive({
  meterId: '',
  name: '',
  type: '',
  location: '',
  description: ''
})

const connectionRules = {
  name: [{ required: true, message: 'Please enter connection name', trigger: 'blur' }],
  platform: [{ required: true, message: 'Please select platform', trigger: 'change' }],
  endpoint: [{ required: true, message: 'Please enter API endpoint', trigger: 'blur' }],
  apiKey: [{ required: true, message: 'Please enter API key', trigger: 'blur' }],
  apiSecret: [{ required: true, message: 'Please enter API secret', trigger: 'blur' }]
}

const meterRules = {
  meterId: [{ required: true, message: 'Please enter meter ID', trigger: 'blur' }],
  name: [{ required: true, message: 'Please enter meter name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select meter type', trigger: 'change' }]
}

// ==================== Mounted ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initConsumptionChart()
    initCarbonGauge()
    initPieChart()
  }, 100)
}

onMounted(() => {
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

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      initCharts()
      fetchConnections()
    }, 400)
  }, 2000)
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
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%,80%,100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
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
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
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
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.ems-integration-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-header .breadcrumb { margin-bottom: 8px; }
.page-header h1 { font-size: 28px; font-weight: 600; color: #303133; margin: 0 0 8px 0; }
.page-header .description { color: #909399; font-size: 14px; margin: 0; }
.page-header .header-actions { display: flex; gap: 12px; }

.stats-row { margin-bottom: 20px; }
.stat-card { cursor: pointer; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-4px); }
.stat-card .stat-content { display: flex; justify-content: space-between; align-items: center; }
.stat-card .stat-info { flex: 1; }
.stat-card .stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-card .stat-value { font-size: 28px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.stat-card .stat-trend { font-size: 12px; display: flex; align-items: center; gap: 4px; }
.stat-card .stat-trend.up { color: #67c23a; }
.stat-card .stat-trend.down { color: #f56c6c; }
.stat-card .stat-trend .trend-label { color: #909399; margin-left: 4px; }
.stat-card .stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-card .stat-footer { margin-top: 12px; padding-top: 8px; border-top: 1px solid #ebeef5; font-size: 12px; color: #909399; }

.ems-cards-row { margin-bottom: 20px; }
.ems-card { cursor: pointer; transition: all 0.3s; }
.ems-card:hover { transform: translateY(-4px); }
.ems-card .ems-card-content { display: flex; gap: 16px; align-items: center; }
.ems-card .ems-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.ems-card .ems-info { flex: 1; }
.ems-card .ems-name { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.ems-card .ems-version { font-size: 12px; color: #909399; margin-top: 4px; }

.dashboard-row, .carbon-row { margin-bottom: 20px; }
.chart-card .card-header, .stats-card .card-header, .gauge-card .card-header, .pie-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.chart-container { width: 100%; height: 320px; }
.gauge-container { width: 100%; height: 250px; }
.pie-chart-container { width: 100%; height: 300px; }

.energy-summary { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.summary-item { background: #f5f7fa; border-radius: 8px; padding: 16px; text-align: center; }
.summary-label { font-size: 12px; color: #909399; margin-bottom: 8px; }
.summary-value { font-size: 20px; font-weight: 600; color: #303133; margin-bottom: 4px; }
.summary-trend { font-size: 11px; }
.summary-trend.up { color: #67c23a; }
.summary-trend.down { color: #f56c6c; }

.target-info { text-align: center; margin-top: 12px; font-size: 12px; color: #909399; display: flex; justify-content: center; gap: 24px; }

.connections-card, .meters-card, .datapoints-card { margin-bottom: 20px; }
.connections-card .card-header, .meters-card .card-header, .datapoints-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.connections-card .connections-actions, .meters-card .meters-actions, .datapoints-card .datapoints-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.meter-data-container .meter-chart-container { width: 100%; height: 300px; margin-bottom: 16px; }

.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
</style>