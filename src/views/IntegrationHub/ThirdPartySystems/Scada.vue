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
        <div class="loading-tip">SCADA Integration</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="scada-integration-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Third-Party Systems</el-breadcrumb-item>
            <el-breadcrumb-item>SCADA</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>SCADA Integration</h1>
        <p class="description">Integrate with Wonderware, Ignition, WinCC, and other SCADA systems for real-time monitoring</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Data
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
                <span class="trend-label">vs last week</span>
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

    <!-- SCADA Platform Cards -->
    <el-row :gutter="20" class="scada-cards-row">
      <el-col :xs="24" :sm="12" :lg="8" v-for="scada in scadaPlatforms" :key="scada.name">
        <el-card class="scada-card" shadow="hover" @click="selectSCADAPlatform(scada)">
          <div class="scada-card-content">
            <div class="scada-icon" :style="{ background: scada.color }">
              <el-icon :size="32"><component :is="scada.icon" /></el-icon>
            </div>
            <div class="scada-info">
              <div class="scada-name">{{ scada.name }}</div>
              <div class="scada-status">
                <el-tag :type="scada.status === 'Connected' ? 'success' : 'danger'" size="small">
                  {{ scada.status }}
                </el-tag>
              </div>
              <div class="scada-version">{{ scada.version }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Real-time Dashboard -->
    <el-row :gutter="20" class="dashboard-row">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Real-time Data Stream</span>
              <div class="chart-controls">
                <el-radio-group v-model="realtimePeriod" size="small">
                  <el-radio-button value="realtime">Real-time</el-radio-button>
                  <el-radio-button value="minute">1 Min Avg</el-radio-button>
                  <el-radio-button value="hour">1 Hour Avg</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </template>
          <div ref="realtimeChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="alerts-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Active Alerts</span>
              <el-badge :value="activeAlerts.length" class="badge" />
            </div>
          </template>
          <div class="alerts-list">
            <div v-for="alert in activeAlerts" :key="alert.id" class="alert-item" :class="alert.severity.toLowerCase()">
              <div class="alert-icon">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.title }}</div>
                <div class="alert-description">{{ alert.description }}</div>
                <div class="alert-time">{{ alert.time }}</div>
              </div>
              <div class="alert-action">
                <el-button link type="primary" size="small" @click="acknowledgeAlert(alert)">Acknowledge</el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- SCADA Connections Table -->
    <el-card class="connections-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>SCADA Connections</span>
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
        <el-table-column prop="host" label="Host/IP" width="150" />
        <el-table-column prop="tags" label="Tags" width="80" align="center" />
        <el-table-column prop="dataPoints" label="Data Points" width="100" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Connected' ? 'success' : row.status === 'Error' ? 'danger' : 'info'" size="small">
              <span class="status-dot" :class="row.status === 'Connected' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastUpdate" label="Last Update" width="150" />
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewTags(row)">Tags</el-button>
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

    <!-- Tags & Data Points Section -->
    <el-card class="tags-card" shadow="hover" v-if="selectedConnection">
      <template #header>
        <div class="card-header">
          <span>SCADA Tags - {{ selectedConnection.name }}</span>
          <div class="tags-actions">
            <el-button size="small" type="primary" @click="openAddTagDialog">
              <el-icon><Plus /></el-icon> Add Tag
            </el-button>
            <el-button size="small" @click="refreshTags">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="scadaTags" stripe size="small" v-loading="tagsLoading">
        <el-table-column prop="tagName" label="Tag Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
        <el-table-column prop="dataType" label="Data Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="currentValue" label="Current Value" width="120" align="right">
          <template #default="{ row }">
            <span class="tag-value">{{ row.currentValue }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Good' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewTagHistory(row)">History</el-button>
            <el-button link type="danger" size="small" @click="deleteTag(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Data Points Table -->
    <el-card class="datapoints-card" shadow="hover" v-if="showDataPoints">
      <template #header>
        <div class="card-header">
          <span>Data Points - {{ selectedConnection?.name }}</span>
          <div class="datapoints-actions">
            <el-button size="small" @click="showDataPoints = false">Close</el-button>
          </div>
        </div>
      </template>

      <el-table :data="dataPoints" stripe size="small" v-loading="dataPointsLoading">
        <el-table-column prop="tagName" label="Tag Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="value" label="Value" width="120" align="right" />
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="quality" label="Quality" width="100">
          <template #default="{ row }">
            <el-tag :type="row.quality === 'Good' ? 'success' : 'danger'" size="small">{{ row.quality }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
      </el-table>
    </el-card>

    <!-- Add Connection Dialog -->
    <el-dialog v-model="connectionDialogVisible" title="Add SCADA Connection" width="600px" destroy-on-close>
      <el-form :model="connectionForm" :rules="connectionRules" ref="connectionFormRef" label-width="130px">
        <el-form-item label="Connection Name" prop="name">
          <el-input v-model="connectionForm.name" placeholder="Enter connection name" />
        </el-form-item>
        <el-form-item label="SCADA Platform" prop="platform">
          <el-select v-model="connectionForm.platform" style="width: 100%">
            <el-option label="Wonderware" value="Wonderware" />
            <el-option label="Ignition" value="Ignition" />
            <el-option label="WinCC" value="WinCC" />
            <el-option label="Citect" value="Citect" />
            <el-option label="iFIX" value="iFIX" />
            <el-option label="FactoryTalk" value="FactoryTalk" />
          </el-select>
        </el-form-item>
        <el-form-item label="Host/IP" prop="host">
          <el-input v-model="connectionForm.host" placeholder="192.168.1.100" />
        </el-form-item>
        <el-form-item label="Port" prop="port">
          <el-input-number v-model="connectionForm.port" :min="1" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Protocol" prop="protocol">
          <el-select v-model="connectionForm.protocol" style="width: 100%">
            <el-option label="OPC DA" value="OPC DA" />
            <el-option label="OPC UA" value="OPC UA" />
            <el-option label="Modbus TCP" value="Modbus TCP" />
            <el-option label="DNP3" value="DNP3" />
            <el-option label="IEC 60870-5-104" value="IEC104" />
          </el-select>
        </el-form-item>
        <el-form-item label="Username" prop="username">
          <el-input v-model="connectionForm.username" placeholder="Optional" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="connectionForm.password" type="password" placeholder="Optional" />
        </el-form-item>
        <el-form-item label="Poll Interval (ms)" prop="pollInterval">
          <el-input-number v-model="connectionForm.pollInterval" :min="100" :max="60000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="connectionForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="connectionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testSCADAConnection">Test Connection</el-button>
        <el-button type="success" @click="saveConnection">Save Connection</el-button>
      </template>
    </el-dialog>

    <!-- Add Tag Dialog -->
    <el-dialog v-model="tagDialogVisible" title="Add SCADA Tag" width="550px" destroy-on-close>
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="120px">
        <el-form-item label="Tag Name" prop="tagName">
          <el-input v-model="tagForm.tagName" placeholder="e.g., Tank1_Level" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="tagForm.description" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Data Type" prop="dataType">
          <el-select v-model="tagForm.dataType" style="width: 100%">
            <el-option label="Boolean" value="Boolean" />
            <el-option label="Integer" value="Integer" />
            <el-option label="Float" value="Float" />
            <el-option label="String" value="String" />
          </el-select>
        </el-form-item>
        <el-form-item label="Unit" prop="unit">
          <el-input v-model="tagForm.unit" placeholder="°C, kW, %, psi" />
        </el-form-item>
        <el-form-item label="Scale Factor" prop="scaleFactor">
          <el-input-number v-model="tagForm.scaleFactor" :step="0.1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Offset" prop="offset">
          <el-input-number v-model="tagForm.offset" :step="0.1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTag">Save Tag</el-button>
      </template>
    </el-dialog>

    <!-- Tag History Dialog -->
    <el-dialog v-model="historyDialogVisible" title="Tag History" width="800px" destroy-on-close>
      <div class="history-container">
        <div ref="historyChartRef" class="history-chart-container"></div>
        <el-table :data="tagHistory" size="small" border max-height="300">
          <el-table-column prop="timestamp" label="Timestamp" width="160" />
          <el-table-column prop="value" label="Value" width="120" align="right" />
          <el-table-column prop="quality" label="Quality" width="100" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="historyDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportHistory">Export Data</el-button>
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
          <p><strong>Tags Available:</strong> {{ testResult.details.tagCount }}</p>
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
  Delete, Connection, Edit, DataAnalysis, Monitor, WarningFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing SCADA integration...', 'Connecting to data sources...', 'Almost ready...']

// ==================== Chart References ====================
const realtimeChartRef = ref<HTMLElement>()
const historyChartRef = ref<HTMLElement>()
let realtimeChart: echarts.ECharts | null = null
let historyChart: echarts.ECharts | null = null

// ==================== State ====================
const connectionsLoading = ref(false)
const tagsLoading = ref(false)
const dataPointsLoading = ref(false)
const connectionDialogVisible = ref(false)
const tagDialogVisible = ref(false)
const testDialogVisible = ref(false)
const historyDialogVisible = ref(false)
const showDataPoints = ref(false)
const selectedConnection = ref<any>(null)
const connectionSearch = ref('')
const connectionStatusFilter = ref('')
const realtimePeriod = ref('realtime')
const connectionsPage = ref(1)
const connectionsPageSize = ref(10)

const connectionFormRef = ref()
const tagFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// Mock data
const statsCards = ref([
  { title: 'SCADA Connections', value: '6', trend: 2, icon: 'Connection', bgColor: '#409eff', key: 'connections', subTitle: 'Active: 5' },
  { title: 'Data Points', value: '3,456', trend: 12, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'points', subTitle: 'Per second' },
  { title: 'Active Alarms', value: '8', trend: -3, icon: 'WarningFilled', bgColor: '#e6a23c', key: 'alarms', subTitle: 'Unacknowledged: 3' },
  { title: 'Data Rate', value: '1.2K/s', trend: 8, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'rate', subTitle: 'Peak: 1.8K/s' }
])

const scadaPlatforms = ref([
  { name: 'Wonderware', icon: 'Monitor', color: '#409eff', status: 'Connected', version: '2023' },
  { name: 'Ignition', icon: 'DataAnalysis', color: '#67c23a', status: 'Connected', version: '8.1' },
  { name: 'WinCC', icon: 'Connection', color: '#e6a23c', status: 'Connected', version: '7.5' }
])

const scadaConnections = ref([
  { id: 1, name: 'Factory SCADA - Main', platform: 'Wonderware', host: '192.168.1.100', port: 8080, tags: 124, dataPoints: 12500, status: 'Connected', lastUpdate: '2024-01-20 10:30:00' },
  { id: 2, name: 'Power Plant SCADA', platform: 'Ignition', host: '192.168.1.101', port: 8088, tags: 89, dataPoints: 8900, status: 'Connected', lastUpdate: '2024-01-20 10:28:00' },
  { id: 3, name: 'Water Treatment', platform: 'WinCC', host: '192.168.1.102', port: 80, tags: 56, dataPoints: 5600, status: 'Error', lastUpdate: '2024-01-20 10:25:00' },
  { id: 4, name: 'HVAC SCADA', platform: 'Citect', host: '192.168.1.103', port: 80, tags: 234, dataPoints: 23400, status: 'Connected', lastUpdate: '2024-01-20 10:32:00' }
])

const scadaTags = ref([
  { id: 1, tagName: 'Tank1_Temperature', description: 'Reactor tank temperature', dataType: 'Float', unit: '°C', currentValue: 75.5, status: 'Good' },
  { id: 2, tagName: 'Pump1_Speed', description: 'Main circulation pump speed', dataType: 'Float', unit: 'rpm', currentValue: 1450, status: 'Good' },
  { id: 3, tagName: 'Valve1_Position', description: 'Inlet valve position', dataType: 'Integer', unit: '%', currentValue: 65, status: 'Good' },
  { id: 4, tagName: 'Level1', description: 'Tank level', dataType: 'Float', unit: 'm', currentValue: 2.3, status: 'Warning' }
])

const dataPoints = ref([
  { tagName: 'Tank1_Temperature', value: 75.5, unit: '°C', quality: 'Good', timestamp: '2024-01-20 10:30:00' },
  { tagName: 'Pump1_Speed', value: 1450, unit: 'rpm', quality: 'Good', timestamp: '2024-01-20 10:30:00' },
  { tagName: 'Valve1_Position', value: 65, unit: '%', quality: 'Good', timestamp: '2024-01-20 10:30:00' }
])

const activeAlerts = ref([
  { id: 1, severity: 'Critical', title: 'High Temperature Alarm', description: 'Reactor temperature exceeded 80°C', time: '2024-01-20 10:25:00' },
  { id: 2, severity: 'Warning', title: 'Low Pressure', description: 'Line pressure below threshold', time: '2024-01-20 10:15:00' },
  { id: 3, severity: 'Info', title: 'Maintenance Due', description: 'Pump maintenance overdue', time: '2024-01-20 09:00:00' }
])

const tagHistory = ref([
  { timestamp: '2024-01-20 10:00:00', value: 74.2, quality: 'Good' },
  { timestamp: '2024-01-20 10:05:00', value: 74.8, quality: 'Good' },
  { timestamp: '2024-01-20 10:10:00', value: 75.1, quality: 'Good' },
  { timestamp: '2024-01-20 10:15:00', value: 75.5, quality: 'Good' },
  { timestamp: '2024-01-20 10:20:00', value: 75.8, quality: 'Good' }
])

// ==================== Computed ====================
const filteredConnections = computed(() => {
  let filtered = [...scadaConnections.value]
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
    'Wonderware': 'primary',
    'Ignition': 'success',
    'WinCC': 'warning',
    'Citect': 'info',
    'iFIX': 'danger',
    'FactoryTalk': 'success'
  }
  return map[platform] || 'info'
}

const getDataTypeTag = (dataType: string) => {
  const map: Record<string, string> = {
    'Boolean': 'warning',
    'Integer': 'primary',
    'Float': 'success',
    'String': 'info'
  }
  return map[dataType] || 'info'
}

const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting SCADA data...')
}

const selectSCADAPlatform = (scada: any) => {
  ElMessage.info(`Selected ${scada.name} - ${scada.status}`)
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

const testSCADAConnection = () => {
  ElMessage.info('Testing SCADA connection...')
  setTimeout(() => {
    testResult.success = true
    testResult.message = 'Successfully connected to SCADA server'
    testResult.details = {
      platform: connectionForm.platform,
      version: '2023.1',
      responseTime: 156,
      tagCount: 1250
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
    const index = scadaConnections.value.findIndex(c => c.id === connection.id)
    if (index !== -1) {
      scadaConnections.value.splice(index, 1)
      ElMessage.success(`Deleted: ${connection.name}`)
    }
  }).catch(() => {})
}

const viewTags = (connection: any) => {
  selectedConnection.value = connection
  refreshTags()
}

const viewDataPoints = (connection: any) => {
  selectedConnection.value = connection
  showDataPoints.value = true
  dataPointsLoading.value = true
  setTimeout(() => {
    dataPointsLoading.value = false
  }, 500)
}

const refreshTags = () => {
  tagsLoading.value = true
  setTimeout(() => {
    tagsLoading.value = false
    ElMessage.success('Tags refreshed')
  }, 500)
}

const openAddTagDialog = () => {
  tagDialogVisible.value = true
}

const saveTag = async () => {
  if (!tagFormRef.value) return
  await tagFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Tag added successfully')
      tagDialogVisible.value = false
      tagFormRef.value?.resetFields()
      refreshTags()
    }
  })
}

const deleteTag = (tag: any) => {
  ElMessageBox.confirm(`Delete tag "${tag.tagName}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = scadaTags.value.findIndex(t => t.id === tag.id)
    if (index !== -1) {
      scadaTags.value.splice(index, 1)
      ElMessage.success(`Deleted: ${tag.tagName}`)
    }
  }).catch(() => {})
}

const viewTagHistory = (tag: any) => {
  historyDialogVisible.value = true
  nextTick(() => {
    if (historyChartRef.value) {
      if (historyChart) historyChart.dispose()
      historyChart = echarts.init(historyChartRef.value)
      historyChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['10:00', '10:05', '10:10', '10:15', '10:20', '10:25', '10:30'] },
        yAxis: { type: 'value', name: tag.unit || 'Value' },
        series: [{ type: 'line', data: [74.2, 74.8, 75.1, 75.5, 75.8, 76.2, 75.5], smooth: true, lineStyle: { width: 2, color: '#409eff' }, areaStyle: { opacity: 0.1 } }]
      })
    }
  })
}

const acknowledgeAlert = (alert: any) => {
  ElMessage.success(`Alert acknowledged: ${alert.title}`)
  const index = activeAlerts.value.findIndex(a => a.id === alert.id)
  if (index !== -1) {
    activeAlerts.value.splice(index, 1)
  }
}

const exportHistory = () => {
  ElMessage.success('Exporting tag history...')
}

// ==================== Chart Initializations ====================
const initRealtimeChart = () => {
  if (!realtimeChartRef.value) return
  if (realtimeChart) realtimeChart.dispose()

  realtimeChart = echarts.init(realtimeChartRef.value)

  const realtimeData = [75.2, 75.5, 74.8, 75.1, 75.6, 75.3, 75.0, 74.9, 75.4, 75.7, 75.2, 74.8]
  const minuteData = [75.0, 75.2, 75.4, 75.3, 75.5, 75.6, 75.4, 75.2, 75.1, 75.3, 75.5, 75.6]
  const hourData = [74.5, 75.0, 75.2, 75.5, 75.3, 75.0, 74.8, 75.1, 75.4, 75.6, 75.5, 75.2]

  let data, xAxisData
  if (realtimePeriod.value === 'realtime') {
    data = realtimeData
    xAxisData = Array.from({ length: 12 }, (_, i) => `${i*5}s`)
  } else if (realtimePeriod.value === 'minute') {
    data = minuteData
    xAxisData = Array.from({ length: 12 }, (_, i) => `${i*5}min`)
  } else {
    data = hourData
    xAxisData = ['1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h']
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#f56c6c' },
      areaStyle: { opacity: 0.1, color: '#f56c6c' },
      symbolSize: 6
    }]
  }

  realtimeChart.setOption(option)
  window.addEventListener('resize', () => realtimeChart?.resize())
}

// ==================== Forms ====================
const connectionForm = reactive({
  name: '',
  platform: '',
  host: '',
  port: 80,
  protocol: 'OPC UA',
  username: '',
  password: '',
  pollInterval: 1000,
  description: ''
})

const tagForm = reactive({
  tagName: '',
  description: '',
  dataType: 'Float',
  unit: '',
  scaleFactor: 1,
  offset: 0
})

const connectionRules = {
  name: [{ required: true, message: 'Please enter connection name', trigger: 'blur' }],
  platform: [{ required: true, message: 'Please select platform', trigger: 'change' }],
  host: [{ required: true, message: 'Please enter host', trigger: 'blur' }],
  port: [{ required: true, message: 'Please enter port', trigger: 'blur' }]
}

const tagRules = {
  tagName: [{ required: true, message: 'Please enter tag name', trigger: 'blur' }]
}

// ==================== Mounted ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initRealtimeChart()
  }, 100)

  // Simulate real-time data updates
  setInterval(() => {
    if (realtimeChart && realtimePeriod.value === 'realtime') {
      const newData = 75 + (Math.random() - 0.5) * 2
      const currentData = (realtimeChart.getOption() as any).series[0].data
      const newSeriesData = [...currentData.slice(1), newData]
      realtimeChart.setOption({ series: [{ data: newSeriesData }] })
    }
  }, 3000)
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

.scada-integration-page {
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

.scada-cards-row { margin-bottom: 20px; }
.scada-card { cursor: pointer; transition: all 0.3s; }
.scada-card:hover { transform: translateY(-4px); }
.scada-card .scada-card-content { display: flex; gap: 16px; align-items: center; }
.scada-card .scada-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.scada-card .scada-info { flex: 1; }
.scada-card .scada-name { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.scada-card .scada-version { font-size: 12px; color: #909399; margin-top: 4px; }

.dashboard-row { margin-bottom: 20px; }
.chart-card .card-header, .alerts-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.chart-container { width: 100%; height: 320px; }

.alerts-list { max-height: 320px; overflow-y: auto; }
.alert-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px; border-bottom: 1px solid #ebeef5; transition: background 0.2s; }
.alert-item:hover { background: #f5f7fa; }
.alert-item.critical .alert-icon .el-icon { color: #f56c6c; }
.alert-item.warning .alert-icon .el-icon { color: #e6a23c; }
.alert-item.info .alert-icon .el-icon { color: #409eff; }
.alert-item .alert-content { flex: 1; }
.alert-item .alert-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; }
.alert-item .alert-description { font-size: 12px; color: #606266; margin-bottom: 4px; }
.alert-item .alert-time { font-size: 11px; color: #909399; }

.connections-card, .tags-card, .datapoints-card { margin-bottom: 20px; }
.connections-card .card-header, .tags-card .card-header, .datapoints-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.connections-card .connections-actions, .tags-card .tags-actions, .datapoints-card .datapoints-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.tag-value { font-weight: 500; color: #409eff; }

.history-container .history-chart-container { width: 100%; height: 300px; margin-bottom: 16px; }

.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
</style>