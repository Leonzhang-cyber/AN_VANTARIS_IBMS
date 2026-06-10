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
        <div class="loading-tip">Integration Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="integration-monitoring-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Integration Monitoring</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Integration Monitoring</h1>
        <p class="description">Real-time monitoring of all protocol gateways, device connections, and data flows</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="primary" @click="refreshAll">
          <el-icon><Refresh /></el-icon>
          Refresh All
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
                <span class="trend-label">vs last hour</span>
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

    <!-- System Health Overview -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Integration Health Overview</span>
              <el-radio-group v-model="healthPeriod" size="small">
                <el-radio-button value="hour">Last Hour</el-radio-button>
                <el-radio-button value="day">Last 24 Hours</el-radio-button>
                <el-radio-button value="week">Last Week</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="healthChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>System Status</span>
            </div>
          </template>
          <div class="system-status">
            <div class="status-item">
              <div class="status-label">Overall Health</div>
              <div class="status-value good">98.5%</div>
              <el-progress :percentage="98.5" :stroke-width="8" color="#67c23a" />
            </div>
            <div class="status-item">
              <div class="status-label">API Gateway</div>
              <div class="status-value good">99.2%</div>
              <el-progress :percentage="99.2" :stroke-width="8" color="#67c23a" />
            </div>
            <div class="status-item">
              <div class="status-label">Message Queue</div>
              <div class="status-value warning">97.8%</div>
              <el-progress :percentage="97.8" :stroke-width="8" color="#e6a23c" />
            </div>
            <div class="status-item">
              <div class="status-label">Database</div>
              <div class="status-value good">99.9%</div>
              <el-progress :percentage="99.9" :stroke-width="8" color="#67c23a" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Protocol Gateway Status -->
    <el-card class="gateways-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Protocol Gateways Status</span>
          <div class="table-actions">
            <el-input
                v-model="gatewaySearch"
                placeholder="Search gateway"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-select v-model="protocolFilter" placeholder="Protocol" clearable style="width: 140px">
              <el-option label="MQTT" value="mqtt" />
              <el-option label="Modbus TCP" value="modbus_tcp" />
              <el-option label="BACnet" value="bacnet" />
              <el-option label="OPC-UA" value="opcua" />
              <el-option label="SNMP" value="snmp" />
              <el-option label="KNX" value="knx" />
            </el-select>
            <el-select v-model="gatewayStatusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Online" value="Online" />
              <el-option label="Offline" value="Offline" />
              <el-option label="Warning" value="Warning" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchGateways" circle />
          </div>
        </div>
      </template>

      <el-table :data="filteredGateways" stripe style="width: 100%" v-loading="gatewayLoading">
        <el-table-column prop="name" label="Gateway Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="protocol" label="Protocol" width="120">
          <template #default="{ row }">
            <el-tag :type="getProtocolTag(row.protocol)" size="small">{{ row.protocol }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="endpoint" label="Endpoint" min-width="220" show-overflow-tooltip />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : row.status === 'Warning' ? 'warning' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Online' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="uptime" label="Uptime" width="120" />
        <el-table-column prop="msgRate" label="Msg Rate" width="90" align="center" />
        <el-table-column prop="lastSeen" label="Last Seen" width="150" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewGatewayDetails(row)">Details</el-button>
            <el-button link type="info" size="small" @click="testGateway(row)">Test</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Device Drivers Status -->
    <el-card class="drivers-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Device Drivers Status</span>
          <div class="table-actions">
            <el-input
                v-model="driverSearch"
                placeholder="Search driver"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-select v-model="manufacturerFilter" placeholder="Manufacturer" clearable style="width: 140px">
              <el-option label="Siemens" value="Siemens" />
              <el-option label="Schneider" value="Schneider" />
              <el-option label="ABB" value="ABB" />
              <el-option label="Honeywell" value="Honeywell" />
              <el-option label="Johnson Controls" value="Johnson Controls" />
              <el-option label="Daikin" value="Daikin" />
              <el-option label="Carrier" value="Carrier" />
              <el-option label="Mitsubishi" value="Mitsubishi" />
              <el-option label="Vertiv" value="Vertiv" />
              <el-option label="Delta" value="Delta" />
              <el-option label="Huawei" value="Huawei" />
            </el-select>
            <el-select v-model="driverStatusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Online" value="Online" />
              <el-option label="Offline" value="Offline" />
              <el-option label="Warning" value="Warning" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchDrivers" circle />
          </div>
        </div>
      </template>

      <el-table :data="filteredDrivers" stripe style="width: 100%" v-loading="driverLoading">
        <el-table-column prop="name" label="Driver Name" min-width="160" show-overflow-tooltip />
        <el-table-column prop="manufacturer" label="Manufacturer" width="140">
          <template #default="{ row }">
            <el-tag :type="getManufacturerTag(row.manufacturer)" size="small">{{ row.manufacturer }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deviceType" label="Device Type" width="120" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : row.status === 'Warning' ? 'warning' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Online' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="deviceCount" label="Devices" width="80" align="center" />
        <el-table-column prop="pointCount" label="Points" width="80" align="center" />
        <el-table-column prop="lastPoll" label="Last Poll" width="150" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDriverDetails(row)">Details</el-button>
            <el-button link type="info" size="small" @click="testDriver(row)">Test</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Data Flow Monitoring -->
    <el-card class="dataflow-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Data Flow Monitoring</span>
          <div class="chart-controls">
            <el-radio-group v-model="flowPeriod" size="small">
              <el-radio-button value="realtime">Real-time</el-radio-button>
              <el-radio-button value="hourly">Hourly</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      <div ref="flowChartRef" class="flow-chart-container"></div>
      <div class="flow-stats">
        <div class="flow-stat-item">
          <span class="stat-label">Total Messages</span>
          <span class="stat-number">1,245,678</span>
        </div>
        <div class="flow-stat-item">
          <span class="stat-label">Avg Throughput</span>
          <span class="stat-number">1,234 msg/s</span>
        </div>
        <div class="flow-stat-item">
          <span class="stat-label">Peak Throughput</span>
          <span class="stat-number">2,567 msg/s</span>
        </div>
        <div class="flow-stat-item">
          <span class="stat-label">Error Rate</span>
          <span class="stat-number error">0.23%</span>
        </div>
      </div>
    </el-card>

    <!-- Recent Alerts -->
    <el-card class="alerts-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Recent Alerts & Events</span>
          <el-button size="small" @click="clearAlerts">Clear All</el-button>
        </div>
      </template>

      <el-table :data="recentAlerts" stripe style="width: 100%">
        <el-table-column prop="timestamp" label="Time" width="160" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'Critical' ? 'danger' : row.severity === 'Warning' ? 'warning' : 'info'" size="small">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="160" show-overflow-tooltip />
        <el-table-column prop="message" label="Message" min-width="300" show-overflow-tooltip />
        <el-table-column label="Action" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="acknowledgeAlert(row)">Acknowledge</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Gateway Details Dialog -->
    <el-dialog v-model="gatewayDetailVisible" :title="`Gateway Details - ${currentGateway?.name}`" width="700px" destroy-on-close>
      <div class="gateway-details" v-if="currentGateway">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Gateway Name">{{ currentGateway.name }}</el-descriptions-item>
          <el-descriptions-item label="Protocol">{{ currentGateway.protocol }}</el-descriptions-item>
          <el-descriptions-item label="Endpoint">{{ currentGateway.endpoint }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="currentGateway.status === 'Online' ? 'success' : 'danger'" size="small">{{ currentGateway.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Uptime">{{ currentGateway.uptime }}</el-descriptions-item>
          <el-descriptions-item label="Message Rate">{{ currentGateway.msgRate }} msg/s</el-descriptions-item>
          <el-descriptions-item label="Last Seen">{{ currentGateway.lastSeen }}</el-descriptions-item>
          <el-descriptions-item label="Connected Devices">{{ currentGateway.deviceCount || 0 }}</el-descriptions-item>
          <el-descriptions-item label="Data Points">{{ currentGateway.pointCount || 0 }}</el-descriptions-item>
          <el-descriptions-item label="CPU Usage" :span="2">
            <el-progress :percentage="currentGateway.cpuUsage || 45" :stroke-width="10" />
          </el-descriptions-item>
          <el-descriptions-item label="Memory Usage" :span="2">
            <el-progress :percentage="currentGateway.memoryUsage || 32" :stroke-width="10" />
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="gatewayDetailVisible = false">Close</el-button>
        <el-button type="primary" @click="testGateway(currentGateway)">Test Connection</el-button>
      </template>
    </el-dialog>

    <!-- Driver Details Dialog -->
    <el-dialog v-model="driverDetailVisible" :title="`Driver Details - ${currentDriver?.name}`" width="700px" destroy-on-close>
      <div class="driver-details" v-if="currentDriver">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Driver Name">{{ currentDriver.name }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ currentDriver.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Device Type">{{ currentDriver.deviceType }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="currentDriver.status === 'Online' ? 'success' : 'danger'" size="small">{{ currentDriver.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Version">{{ currentDriver.version || '2.1.0' }}</el-descriptions-item>
          <el-descriptions-item label="Devices">{{ currentDriver.deviceCount || 0 }}</el-descriptions-item>
          <el-descriptions-item label="Data Points">{{ currentDriver.pointCount || 0 }}</el-descriptions-item>
          <el-descriptions-item label="Last Poll">{{ currentDriver.lastPoll }}</el-descriptions-item>
          <el-descriptions-item label="Poll Interval">{{ currentDriver.pollInterval || '5s' }}</el-descriptions-item>
          <el-descriptions-item label="Success Rate" :span="2">
            <el-progress :percentage="currentDriver.successRate || 99.2" :stroke-width="10" color="#67c23a" />
          </el-descriptions-item>
          <el-descriptions-item label="Avg Latency" :span="2">{{ currentDriver.avgLatency || '45ms' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="driverDetailVisible = false">Close</el-button>
        <el-button type="primary" @click="testDriver(currentDriver)">Test Connection</el-button>
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
  Delete, Connection, Edit, Cpu, DataAnalysis, Monitor, Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing monitoring...', 'Loading integration status...', 'Almost ready...']

// ==================== Chart References ====================
const healthChartRef = ref<HTMLElement>()
const flowChartRef = ref<HTMLElement>()
let healthChart: echarts.ECharts | null = null
let flowChart: echarts.ECharts | null = null

// ==================== State ====================
const gatewayLoading = ref(false)
const driverLoading = ref(false)
const gatewayDetailVisible = ref(false)
const driverDetailVisible = ref(false)
const currentGateway = ref<any>(null)
const currentDriver = ref<any>(null)
const gatewaySearch = ref('')
const driverSearch = ref('')
const protocolFilter = ref('')
const manufacturerFilter = ref('')
const gatewayStatusFilter = ref('')
const driverStatusFilter = ref('')
const healthPeriod = ref('hour')
const flowPeriod = ref('realtime')
const testing = ref(false)

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Active Gateways', value: '18', trend: 2, icon: 'Connection', bgColor: '#409eff', key: 'gateways', subTitle: 'Total: 24' },
  { title: 'Connected Devices', value: '156', trend: 8, icon: 'Cpu', bgColor: '#67c23a', key: 'devices', subTitle: 'Online: 148' },
  { title: 'Data Points', value: '3,245', trend: 12, icon: 'DataAnalysis', bgColor: '#e6a23c', key: 'points', subTitle: 'Active: 3,120' },
  { title: 'Message Rate', value: '1.2K/s', trend: 5, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'rate', subTitle: 'Peak: 1.8K/s' }
])

const gateways = ref([
  { id: 1, name: 'Building A MQTT Gateway', protocol: 'mqtt', endpoint: 'tcp://mqtt.ibms.com:1883', status: 'Online', uptime: '14d 6h 23m', msgRate: 1234, lastSeen: '2024-01-20 10:30:00', deviceCount: 24, pointCount: 567, cpuUsage: 32, memoryUsage: 28 },
  { id: 2, name: 'Chiller Plant Modbus Gateway', protocol: 'modbus_tcp', endpoint: '192.168.1.100:502', status: 'Online', uptime: '7d 2h 15m', msgRate: 234, lastSeen: '2024-01-20 10:28:00', deviceCount: 8, pointCount: 156, cpuUsage: 18, memoryUsage: 22 },
  { id: 3, name: 'BACnet IP Gateway', protocol: 'bacnet', endpoint: '192.168.1.101:47808', status: 'Online', uptime: '21d 8h 45m', msgRate: 89, lastSeen: '2024-01-20 10:32:00', deviceCount: 12, pointCount: 234, cpuUsage: 15, memoryUsage: 20 },
  { id: 4, name: 'Factory OPC-UA Server', protocol: 'opcua', endpoint: 'opc.tcp://192.168.1.102:4840', status: 'Warning', uptime: '3d 12h 30m', msgRate: 567, lastSeen: '2024-01-20 10:25:00', deviceCount: 15, pointCount: 345, cpuUsage: 65, memoryUsage: 58 },
  { id: 5, name: 'Network SNMP Gateway', protocol: 'snmp', endpoint: '192.168.1.103:161', status: 'Online', uptime: '30d 0h 0m', msgRate: 78, lastSeen: '2024-01-20 10:29:00', deviceCount: 20, pointCount: 234, cpuUsage: 12, memoryUsage: 16 }
])

const drivers = ref([
  { id: 1, name: 'Siemens S7 Driver', manufacturer: 'Siemens', deviceType: 'PLC', status: 'Online', deviceCount: 8, pointCount: 256, lastPoll: '2024-01-20 10:30:00', version: '2.1.0', pollInterval: '1s', successRate: 99.5, avgLatency: '32ms' },
  { id: 2, name: 'Schneider Modbus Driver', manufacturer: 'Schneider', deviceType: 'PLC', status: 'Online', deviceCount: 5, pointCount: 128, lastPoll: '2024-01-20 10:28:00', version: '1.8.0', pollInterval: '2s', successRate: 99.8, avgLatency: '28ms' },
  { id: 3, name: 'ABB AC500 Driver', manufacturer: 'ABB', deviceType: 'PLC', status: 'Online', deviceCount: 3, pointCount: 89, lastPoll: '2024-01-20 10:32:00', version: '1.5.0', pollInterval: '1s', successRate: 99.2, avgLatency: '35ms' },
  { id: 4, name: 'Honeywell BACnet Driver', manufacturer: 'Honeywell', deviceType: 'Controller', status: 'Warning', deviceCount: 6, pointCount: 145, lastPoll: '2024-01-20 10:25:00', version: '2.0.0', pollInterval: '3s', successRate: 97.5, avgLatency: '52ms' },
  { id: 5, name: 'Johnson Controls Driver', manufacturer: 'Johnson Controls', deviceType: 'Controller', status: 'Online', deviceCount: 4, pointCount: 98, lastPoll: '2024-01-20 10:29:00', version: '1.2.0', pollInterval: '2s', successRate: 99.3, avgLatency: '38ms' },
  { id: 6, name: 'Daikin HVAC Driver', manufacturer: 'Daikin', deviceType: 'HVAC', status: 'Online', deviceCount: 12, pointCount: 234, lastPoll: '2024-01-20 10:31:00', version: '1.1.0', pollInterval: '5s', successRate: 98.8, avgLatency: '45ms' },
  { id: 7, name: 'Carrier Chiller Driver', manufacturer: 'Carrier', deviceType: 'Chiller', status: 'Online', deviceCount: 3, pointCount: 67, lastPoll: '2024-01-20 10:27:00', version: '1.0.0', pollInterval: '3s', successRate: 99.1, avgLatency: '41ms' },
  { id: 8, name: 'Mitsubishi PLC Driver', manufacturer: 'Mitsubishi', deviceType: 'PLC', status: 'Online', deviceCount: 2, pointCount: 56, lastPoll: '2024-01-20 10:30:00', version: '1.3.0', pollInterval: '1s', successRate: 99.7, avgLatency: '29ms' },
  { id: 9, name: 'Vertiv UPS Driver', manufacturer: 'Vertiv', deviceType: 'UPS', status: 'Online', deviceCount: 4, pointCount: 45, lastPoll: '2024-01-20 10:28:00', version: '1.0.0', pollInterval: '10s', successRate: 99.4, avgLatency: '48ms' },
  { id: 10, name: 'Delta VFD Driver', manufacturer: 'Delta', deviceType: 'VFD', status: 'Offline', deviceCount: 2, pointCount: 32, lastPoll: '2024-01-20 08:15:00', version: '1.0.0', pollInterval: '5s', successRate: 85.2, avgLatency: '120ms' }
])

const recentAlerts = ref([
  { id: 1, timestamp: '2024-01-20 10:30:00', severity: 'Warning', source: 'OPC-UA Gateway', message: 'High latency detected (245ms)' },
  { id: 2, timestamp: '2024-01-20 10:15:00', severity: 'Info', source: 'BACnet Gateway', message: 'Device discovery completed, found 12 new devices' },
  { id: 3, timestamp: '2024-01-20 09:45:00', severity: 'Critical', source: 'Delta VFD Driver', message: 'Connection lost to device Delta_VFD_01' },
  { id: 4, timestamp: '2024-01-20 09:30:00', severity: 'Warning', source: 'Honeywell BACnet Driver', message: 'Polling timeout on 3 points' },
  { id: 5, timestamp: '2024-01-20 09:00:00', severity: 'Info', source: 'System', message: 'Integration service restarted successfully' }
])

// ==================== Computed ====================
const filteredGateways = computed(() => {
  let filtered = [...gateways.value]
  if (gatewaySearch.value) filtered = filtered.filter(g => g.name.toLowerCase().includes(gatewaySearch.value.toLowerCase()))
  if (protocolFilter.value) filtered = filtered.filter(g => g.protocol === protocolFilter.value)
  if (gatewayStatusFilter.value) filtered = filtered.filter(g => g.status === gatewayStatusFilter.value)
  return filtered
})

const filteredDrivers = computed(() => {
  let filtered = [...drivers.value]
  if (driverSearch.value) filtered = filtered.filter(d => d.name.toLowerCase().includes(driverSearch.value.toLowerCase()))
  if (manufacturerFilter.value) filtered = filtered.filter(d => d.manufacturer === manufacturerFilter.value)
  if (driverStatusFilter.value) filtered = filtered.filter(d => d.status === driverStatusFilter.value)
  return filtered
})

// ==================== Helper Methods ====================
const getProtocolTag = (protocol: string) => {
  const map: Record<string, string> = {
    'mqtt': 'primary',
    'modbus_tcp': 'success',
    'bacnet': 'warning',
    'opcua': 'danger',
    'snmp': 'info',
    'knx': 'success'
  }
  return map[protocol] || 'info'
}

const getManufacturerTag = (manufacturer: string) => {
  const map: Record<string, string> = {
    'Siemens': 'primary',
    'Schneider': 'success',
    'ABB': 'warning',
    'Honeywell': 'danger',
    'Johnson Controls': 'info',
    'Daikin': 'success',
    'Carrier': 'primary',
    'Mitsubishi': 'warning',
    'Vertiv': 'info',
    'Delta': 'danger'
  }
  return map[manufacturer] || 'info'
}

// ==================== Chart Initializations ====================
const initHealthChart = () => {
  if (!healthChartRef.value) return
  if (healthChart) healthChart.dispose()

  healthChart = echarts.init(healthChartRef.value)

  const hourlyData = [98.2, 98.5, 98.8, 98.3, 97.9, 98.1, 98.4, 98.6, 98.9, 98.5, 98.2, 98.0]
  const dailyData = [98.2, 98.4, 98.6, 98.3, 97.8, 98.1, 98.5, 98.7, 98.9, 98.4]
  const weeklyData = [97.5, 98.2, 98.8, 98.4, 97.9, 98.3, 98.6]

  let data, xAxisData
  if (healthPeriod.value === 'hour') {
    data = hourlyData
    xAxisData = ['1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h']
  } else if (healthPeriod.value === 'day') {
    data = dailyData
    xAxisData = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10']
  } else {
    data = weeklyData
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7']
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 95, max: 100 },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbolSize: 8,
      symbol: 'circle'
    }]
  }

  healthChart.setOption(option)
  window.addEventListener('resize', () => healthChart?.resize())
}

const initFlowChart = () => {
  if (!flowChartRef.value) return
  if (flowChart) flowChart.dispose()

  flowChart = echarts.init(flowChartRef.value)

  const realtimeData = [1250, 1320, 1280, 1450, 1380, 1420, 1350, 1480, 1520, 1490, 1550, 1600]
  const hourlyData = [12500, 13200, 12800, 14500, 13800, 14200, 13500, 14800, 15200, 14900, 15500, 16000]

  const data = flowPeriod.value === 'realtime' ? realtimeData : hourlyData
  const xAxisData = flowPeriod.value === 'realtime'
      ? Array.from({ length: 12 }, (_, i) => `${i*5}s`)
      : ['1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Messages per second' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#67c23a' },
      areaStyle: { opacity: 0.1, color: '#67c23a' },
      symbolSize: 6
    }]
  }

  flowChart.setOption(option)
  window.addEventListener('resize', () => flowChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting integration report...')
}

const refreshAll = () => {
  fetchGateways()
  fetchDrivers()
  initHealthChart()
  initFlowChart()
  ElMessage.success('All data refreshed')
}

const fetchGateways = () => {
  gatewayLoading.value = true
  setTimeout(() => {
    gatewayLoading.value = false
    ElMessage.success('Gateways refreshed')
  }, 500)
}

const fetchDrivers = () => {
  driverLoading.value = true
  setTimeout(() => {
    driverLoading.value = false
    ElMessage.success('Drivers refreshed')
  }, 500)
}

const viewGatewayDetails = (gateway: any) => {
  currentGateway.value = gateway
  gatewayDetailVisible.value = true
}

const viewDriverDetails = (driver: any) => {
  currentDriver.value = driver
  driverDetailVisible.value = true
}

const testGateway = (gateway: any) => {
  ElMessage.info(`Testing connection to ${gateway.name}...`)
  setTimeout(() => {
    ElMessage.success(`${gateway.name} connection successful`)
  }, 1000)
}

const testDriver = (driver: any) => {
  ElMessage.info(`Testing driver ${driver.name}...`)
  setTimeout(() => {
    ElMessage.success(`${driver.name} is ${driver.status}`)
  }, 1000)
}

const acknowledgeAlert = (alert: any) => {
  ElMessage.success(`Alert acknowledged: ${alert.message}`)
}

const clearAlerts = () => {
  ElMessageBox.confirm('Clear all alerts?', 'Confirm', {
    confirmButtonText: 'Clear',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    recentAlerts.value = []
    ElMessage.success('Alerts cleared')
  }).catch(() => {})
}

// ==================== Mounted ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initHealthChart()
    initFlowChart()
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
      fetchGateways()
      fetchDrivers()
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

.integration-monitoring-page {
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

.chart-row { margin-bottom: 20px; }
.chart-card, .stats-card { margin-bottom: 20px; }
.chart-card .card-header, .stats-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.chart-container { width: 100%; height: 320px; }

.system-status { padding: 8px; }
.status-item { margin-bottom: 20px; }
.status-label { font-size: 13px; color: #606266; margin-bottom: 8px; }
.status-value { font-size: 20px; font-weight: 600; margin-bottom: 8px; }
.status-value.good { color: #67c23a; }
.status-value.warning { color: #e6a23c; }
.status-value.bad { color: #f56c6c; }

.gateways-card, .drivers-card, .dataflow-card, .alerts-card { margin-bottom: 20px; }
.gateways-card .card-header, .drivers-card .card-header, .dataflow-card .card-header, .alerts-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.gateways-card .table-actions, .drivers-card .table-actions { display: flex; gap: 12px; align-items: center; }

.flow-chart-container { width: 100%; height: 320px; }
.flow-stats { display: flex; justify-content: space-around; margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.flow-stat-item { text-align: center; }
.flow-stat-item .stat-label { font-size: 12px; color: #909399; display: block; margin-bottom: 4px; }
.flow-stat-item .stat-number { font-size: 18px; font-weight: 600; color: #303133; }
.flow-stat-item .stat-number.error { color: #f56c6c; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.gateway-details, .driver-details { :deep(.el-progress) { margin-top: 8px; } }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
</style>