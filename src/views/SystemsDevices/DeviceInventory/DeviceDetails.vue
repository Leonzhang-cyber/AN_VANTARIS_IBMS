<template>
  <!-- ==================== Loading Screen ==================== -->
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
        <div class="loading-tip">Device Details</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="device-details-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Device Inventory
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Details</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="ArrowLeft" @click="goBack">Back</el-button>
        <el-button type="primary" :icon="Switch" @click="controlDevice">Control</el-button>
        <el-button :icon="Tools" @click="createWorkOrder">Work Order</el-button>
        <el-button :icon="Download" @click="exportData">Export</el-button>
      </div>
    </div>

    <!-- Device Selector -->
    <div class="device-selector-card">
      <div class="selector-label">
        <el-icon><List /></el-icon>
        <span>Select Device</span>
      </div>
      <div class="selector-controls">
        <el-select
            v-model="selectedDeviceId"
            placeholder="Search or select device"
            filterable
            clearable
            style="width: 320px"
            @change="onDeviceChange"
        >
          <el-option
              v-for="device in deviceList"
              :key="device.id"
              :label="`${device.name} (${device.model})`"
              :value="device.id"
          >
            <div class="device-option">
              <span class="status-dot" :class="`status-${device.status}`"></span>
              <span>{{ device.name }}</span>
              <span class="option-model">{{ device.model }}</span>
            </div>
          </el-option>
        </el-select>
        <el-input
            v-model="deviceIdInput"
            placeholder="Enter device serial number"
            style="width: 240px"
            @keyup.enter="loadDeviceBySerial"
        >
          <template #append>
            <el-button :icon="Search" @click="loadDeviceBySerial" />
          </template>
        </el-input>
      </div>
      <div class="device-stats-mini">
        <div class="mini-stat">
          <span class="mini-label">Total Devices:</span>
          <span class="mini-value">{{ deviceList.length }}</span>
        </div>
        <div class="mini-stat">
          <span class="mini-label">Online:</span>
          <span class="mini-value online">{{ onlineCount }}</span>
        </div>
      </div>
    </div>

    <!-- Device Details Content -->
    <div v-if="currentDevice" class="details-content">
      <!-- Top Section: Device Overview -->
      <div class="overview-section">
        <div class="device-overview-card">
          <div class="device-image-area">
            <el-image
                :src="currentDevice.imageUrl"
                fit="contain"
                class="device-image"
                :preview-src-list="[currentDevice.imageUrl]"
            >
              <template #error>
                <div class="image-fallback">
                  <el-icon :size="48"><Cpu /></el-icon>
                  <span>No Image</span>
                </div>
              </template>
            </el-image>
            <div class="device-status-badge" :class="currentDevice.status">
              {{ currentDevice.status.toUpperCase() }}
            </div>
          </div>
          <div class="device-info-area">
            <div class="device-title">
              <h1>{{ currentDevice.name }}</h1>
              <el-tag :type="getStatusType(currentDevice.status)" size="large" effect="dark">
                {{ currentDevice.status.toUpperCase() }}
              </el-tag>
            </div>
            <div class="device-meta">
              <div class="meta-item"><el-icon><OfficeBuilding /></el-icon><span>{{ currentDevice.model }}</span></div>
              <div class="meta-item"><el-icon><House /></el-icon><span>{{ currentDevice.manufacturer }}</span></div>
              <div class="meta-item"><el-icon><Document /></el-icon><span>SN: {{ currentDevice.serialNumber }}</span></div>
              <div class="meta-item"><el-icon><Grid /></el-icon><span>{{ currentDevice.area }} ({{ currentDevice.floor }})</span></div>
            </div>
            <div class="device-specs">
              <div class="spec-item"><span class="spec-label">System Type:</span><el-tag :type="getSystemTagType(currentDevice.systemType)" size="small">{{ getSystemLabel(currentDevice.systemType) }}</el-tag></div>
              <div class="spec-item"><span class="spec-label">Installation:</span><span>{{ formatDate(currentDevice.installationDate) }}</span></div>
              <div class="spec-item"><span class="spec-label">Last Maintenance:</span><span>{{ formatDate(currentDevice.lastMaintenance) }}</span></div>
              <div class="spec-item"><span class="spec-label">Next Maintenance:</span><span :class="isMaintenanceOverdue ? 'text-danger' : ''">{{ formatDate(currentDevice.nextMaintenance) }}</span><el-tag v-if="isMaintenanceOverdue" type="danger" size="small">Overdue</el-tag></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-cards">
        <div class="stat-card" v-for="stat in deviceStats" :key="stat.key">
          <div class="stat-icon"><el-icon><component :is="stat.icon" /></el-icon></div>
          <div class="stat-info"><span class="stat-value">{{ stat.value }}</span><span class="stat-label">{{ stat.label }}</span></div>
          <div class="stat-trend" :class="stat.trendClass">{{ stat.trendIcon }}</div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="details-grid">
        <!-- Left Column: Real-time Metrics -->
        <div class="metrics-section">
          <div class="section-card">
            <div class="card-header"><h3><el-icon><DataLine /></el-icon> Real-time Metrics</h3><span class="update-time">Updated: {{ lastUpdateTime }}</span></div>
            <div class="metrics-list">
              <div class="metric-row" v-for="metric in allMetrics" :key="metric.key">
                <div class="metric-label"><el-icon><component :is="metric.icon" /></el-icon><span>{{ metric.label }}</span></div>
                <div class="metric-value-area">
                  <span class="metric-value" :class="{ 'text-warning': metric.warning }">{{ metric.value }}<span class="metric-unit">{{ metric.unit }}</span></span>
                  <div class="metric-progress"><div class="progress-fill" :style="{ width: metric.percentage + '%' }" :class="{ 'fill-warning': metric.warning }"></div></div>
                </div>
              </div>
            </div>
          </div>

          <!-- System Specific Metrics -->
          <div class="section-card" v-if="currentDevice.systemType === 'hvac'">
            <div class="card-header"><h3><el-icon><ColdDrink /></el-icon> HVAC Metrics</h3></div>
            <div class="metrics-grid-2col">
              <div class="metric-card-mini"><span class="metric-label-mini">Pressure</span><span class="metric-value-mini">{{ currentDevice.metrics.pressure || '-' }} kPa</span></div>
              <div class="metric-card-mini"><span class="metric-label-mini">Flow Rate</span><span class="metric-value-mini">{{ currentDevice.metrics.flowRate || '-' }} m³/h</span></div>
              <div class="metric-card-mini"><span class="metric-label-mini">Noise Level</span><span class="metric-value-mini">{{ currentDevice.metrics.noiseLevel || '-' }} dB</span></div>
              <div class="metric-card-mini"><span class="metric-label-mini">Energy</span><span class="metric-value-mini">{{ (currentDevice.metrics.energy || 0).toLocaleString() }} kWh</span></div>
            </div>
          </div>
        </div>

        <!-- Right Column: Charts -->
        <div class="charts-section">
          <div class="section-card">
            <div class="card-header">
              <h3><el-icon><TrendCharts /></el-icon> Trend Analysis - Last 24 Hours</h3>
              <div class="chart-date-info">{{ getCurrentDateRange() }}</div>
            </div>
            <div ref="trendChartRef" class="trend-chart"></div>
          </div>
          <div class="section-card">
            <div class="card-header">
              <h3><el-icon><DataBoard /></el-icon> Energy Consumption</h3>
              <el-radio-group v-model="energyPeriod" size="small" @change="refreshEnergyChart">
                <el-radio-button label="week">Week</el-radio-button>
                <el-radio-button label="month">Month</el-radio-button>
                <el-radio-button label="year">Year</el-radio-button>
              </el-radio-group>
            </div>
            <div ref="energyChartRef" class="energy-chart"></div>
          </div>
        </div>
      </div>

      <!-- Device Logs Section -->
      <div class="section-card full-width">
        <div class="card-header">
          <h3><el-icon><Document /></el-icon> Device Event Logs</h3>
          <div class="log-filters">
            <el-select v-model="logFilter.severity" placeholder="Severity" clearable size="small" style="width: 120px" @change="filterLogs">
              <el-option label="All" value="" /><el-option label="Info" value="info" /><el-option label="Warning" value="warning" /><el-option label="Error" value="error" /><el-option label="Critical" value="critical" />
            </el-select>
            <el-date-picker v-model="logFilter.dateRange" type="daterange" range-separator="-" start-placeholder="Start" end-placeholder="End" size="small" style="width: 260px" @change="filterLogs" />
            <el-button size="small" :icon="RefreshRight" @click="resetLogFilters">Reset</el-button>
            <el-button size="small" type="primary" :icon="Download" @click="exportLogs">Export Logs</el-button>
          </div>
        </div>
        <div class="logs-container">
          <el-table :data="paginatedLogs" stripe style="width: 100%" max-height="400">
            <el-table-column prop="timestamp" label="Timestamp" width="180"><template #default="{ row }">{{ formatDateTime(row.timestamp) }}</template></el-table-column>
            <el-table-column prop="severity" label="Severity" width="100"><template #default="{ row }"><el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity.toUpperCase() }}</el-tag></template></el-table-column>
            <el-table-column prop="eventType" label="Event Type" width="140"><template #default="{ row }"><el-tag :type="getEventTypeTag(row.eventType)" size="small" effect="plain">{{ row.eventType }}</el-tag></template></el-table-column>
            <el-table-column prop="message" label="Message" min-width="300" show-overflow-tooltip />
            <el-table-column prop="source" label="Source" width="120" />
            <el-table-column label="Details" width="80" fixed="right"><template #default="{ row }"><el-button size="small" text @click="viewLogDetail(row)">View</el-button></template></el-table-column>
          </el-table>
          <div class="pagination-wrapper"><el-pagination v-model:current-page="logPage" :page-size="logPageSize" :total="filteredLogs.length" layout="total, prev, pager, next" small @current-change="handleLogPageChange" /></div>
        </div>
      </div>

      <!-- Maintenance Timeline -->
      <div class="section-card full-width">
        <div class="card-header"><h3><el-icon><Clock /></el-icon> Maintenance History</h3><el-button size="small" :icon="Plus" @click="addMaintenanceRecord">Add Record</el-button></div>
        <div class="timeline-container">
          <el-timeline><el-timeline-item v-for="record in maintenanceHistory" :key="record.id" :timestamp="formatDate(record.date)" :type="record.type" placement="top"><div class="timeline-content"><h4>{{ record.title }}</h4><p>{{ record.description }}</p><div class="timeline-footer"><span class="technician">Technician: {{ record.technician }}</span><el-tag :type="record.status === 'completed' ? 'success' : 'warning'" size="small">{{ record.status }}</el-tag></div></div></el-timeline-item></el-timeline>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state"><el-empty description="No device selected"><el-button type="primary" @click="selectFirstDevice">Select a device from the list</el-button></el-empty></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Cpu, OfficeBuilding, House, Document, Grid, ArrowLeft, Switch,
  Tools, Download, List, Search, RefreshRight, Plus, Clock, DataLine,
  ColdDrink, TrendCharts, DataBoard, Odometer, Sunny, MagicStick
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading device data...')
const router = useRouter()
const loadingMessages = ['Initializing...', 'Loading device list...', 'Loading device details...', 'Loading charts...', 'Ready!']

// ==================== Device Data Interfaces ====================
interface DeviceMetrics { temperature: number; humidity: number; power: number; energy: number; uptime: number; efficiency: number; pressure?: number; flowRate?: number; co2Level?: number; noiseLevel?: number; vibration?: number }
interface Device { id: string; name: string; type: 'device'; status: 'online' | 'offline' | 'warning' | 'error'; model: string; manufacturer: string; serialNumber: string; systemType: string; area: string; floor: string; imageUrl: string; metrics: DeviceMetrics; lastMaintenance: string; nextMaintenance: string; installationDate: string }
interface DeviceLog { id: string; timestamp: string; severity: 'info' | 'warning' | 'error' | 'critical'; eventType: string; message: string; source: string; details?: any }
interface MaintenanceRecord { id: string; date: string; title: string; description: string; technician: string; status: 'completed' | 'pending'; type: 'primary' | 'success' | 'warning' | 'danger' | 'info' }

// ==================== Current Date Helpers ====================
const getCurrentDateRange = () => {
  const now = new Date()
  const endDate = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  const startDate = new Date(now.getTime() - 24 * 3600000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  return `${startDate} - ${endDate}`
}

// ==================== Device List ====================
const deviceList = ref<Device[]>([])
const selectedDeviceId = ref('')
const deviceIdInput = ref('')
const currentDevice = ref<Device | null>(null)

// Generate Device List with realistic data
const generateDeviceList = (): Device[] => {
  const now = new Date()
  const lastYear = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate())

  const baseDevices = [
    { id: 'dev-ahu-b2-01', name: 'AHU-B2-01 Air Handler', model: 'Carrier 39G', manufacturer: 'Carrier', serial: 'CA-2024-B201', systemType: 'hvac', area: 'Basement B2', floor: 'B2', status: 'online', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', temp: 23.0, humidity: 50, power: 18.5, energy: 15200, efficiency: 94, pressure: 280, flowRate: 15000, noise: 62, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 45).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() + 45).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-fcu-b2-01', name: 'FCU-B2-01 Fan Coil', model: 'Daikin FXMQ', manufacturer: 'Daikin', serial: 'DK-2024-B201', systemType: 'hvac', area: 'Basement B2', floor: 'B2', status: 'online', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp', temp: 22.5, humidity: 48, power: 6.8, energy: 5400, efficiency: 91, pressure: 160, flowRate: 1800, noise: 38, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() + 60).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-chiller-b2-01', name: 'CH-B2-01 Chiller', model: 'Carrier AquaEdge', manufacturer: 'Carrier', serial: 'CA-2024-B202', systemType: 'hvac', area: 'Basement B2', floor: 'B2', status: 'online', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg', temp: 28.0, humidity: 65, power: 85.0, energy: 68000, efficiency: 92, pressure: 420, flowRate: 45000, noise: 72, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 60).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() + 30).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-exhaust-b2-02', name: 'EF-B2-02 Exhaust Fan', model: 'Greenheck CUBE', manufacturer: 'Greenheck', serial: 'GH-2024-B202', systemType: 'hvac', area: 'Basement B2', floor: 'B2', status: 'warning', img: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp', temp: 29.5, humidity: 58, power: 8.2, energy: 6560, efficiency: 86, pressure: 195, flowRate: 8500, noise: 68, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 75).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() + 15).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-ahu-2f-01', name: 'AHU-2F-01 Air Handler', model: 'Trane IntelliPak', manufacturer: 'Trane', serial: 'TR-2024-2F01', systemType: 'hvac', area: 'Office 2F', floor: '2F', status: 'error', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', temp: 31.2, humidity: 72, power: 22.5, energy: 18500, efficiency: 72, pressure: 195, flowRate: 9800, noise: 78, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 5).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-light-b2-01', name: 'LIGHT-B2-01 Controller', model: 'Philips Dynalite', manufacturer: 'Philips', serial: 'PH-2024-B201', systemType: 'lighting', area: 'Basement B2', floor: 'B2', status: 'online', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp', temp: 26.5, humidity: 42, power: 4.2, energy: 3200, efficiency: 96, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 15).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() + 75).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-access-1f-01', name: 'ACS-1F-01 Entrance', model: 'HID VertX', manufacturer: 'HID Global', serial: 'HD-2024-1F01', systemType: 'sas', area: 'Lobby 1F', floor: '1F', status: 'online', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg', temp: 35.0, humidity: 40, power: 0.5, energy: 400, efficiency: 99, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 10).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() + 80).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-smoke-1f-01', name: 'SD-1F-01 Smoke Detector', model: 'Honeywell XLS', manufacturer: 'Honeywell', serial: 'HW-2024-1F01', systemType: 'fas', area: 'Lobby 1F', floor: '1F', status: 'online', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg', temp: 22.0, humidity: 55, power: 0.3, energy: 240, efficiency: 99, co2Level: 440, noise: 13, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 60).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() + 30).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-pump-b2-02', name: 'PUMP-B2-02 Booster', model: 'Grundfos CR', manufacturer: 'Grundfos', serial: 'GF-2024-B202', systemType: 'plumbing', area: 'Basement B2', floor: 'B2', status: 'warning', img: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png', temp: 38.0, humidity: 72, power: 9.5, energy: 7600, efficiency: 76, pressure: 320, flowRate: 42, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 30).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 10).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] },
    { id: 'dev-camera-2f-01', name: 'CAM-2F-01 Camera', model: 'Hikvision DS-2CD', manufacturer: 'Hikvision', serial: 'HK-2024-2F01', systemType: 'sas', area: 'Office 2F', floor: '2F', status: 'warning', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp', temp: 40.0, humidity: 35, power: 1.0, energy: 800, efficiency: 95, lastMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 25).toISOString().split('T')[0], nextMain: new Date(now.getFullYear(), now.getMonth(), now.getDate() + 65).toISOString().split('T')[0], install: lastYear.toISOString().split('T')[0] }
  ]
  return baseDevices.map(d => ({ id: d.id, name: d.name, type: 'device', status: d.status as any, model: d.model, manufacturer: d.manufacturer, serialNumber: d.serial, systemType: d.systemType, area: d.area, floor: d.floor, imageUrl: d.img, metrics: { temperature: d.temp, humidity: d.humidity, power: d.power, energy: d.energy, uptime: Math.floor(Math.random() * 8760), efficiency: d.efficiency, pressure: (d as any).pressure, flowRate: (d as any).flowRate, noiseLevel: (d as any).noise, co2Level: (d as any).co2Level }, lastMaintenance: d.lastMain, nextMaintenance: d.nextMain, installationDate: d.install }))
}

// Generate Device Logs with realistic timestamps
const generateDeviceLogs = (deviceId: string): DeviceLog[] => {
  const now = new Date()
  const baseLogs = [
    { id: '1', timestamp: new Date(now.getTime() - 2 * 3600000).toISOString(), severity: 'info', eventType: 'STARTUP', message: 'Device started successfully', source: 'SYSTEM' },
    { id: '2', timestamp: new Date(now.getTime() - 5 * 3600000).toISOString(), severity: 'info', eventType: 'CONFIG', message: 'Configuration updated: setpoint changed to 22.5°C', source: 'USER' },
    { id: '3', timestamp: new Date(now.getTime() - 24 * 3600000).toISOString(), severity: 'warning', eventType: 'THRESHOLD', message: 'Temperature exceeded warning threshold (28.5°C)', source: 'SENSOR' },
    { id: '4', timestamp: new Date(now.getTime() - 48 * 3600000).toISOString(), severity: 'info', eventType: 'MAINTENANCE', message: 'Scheduled maintenance reminder generated', source: 'SCHEDULER' },
    { id: '5', timestamp: new Date(now.getTime() - 72 * 3600000).toISOString(), severity: 'critical', eventType: 'ALARM', message: 'Critical alarm: High vibration detected', source: 'MONITOR' },
    { id: '6', timestamp: new Date(now.getTime() - 73 * 3600000).toISOString(), severity: 'info', eventType: 'COMMAND', message: 'Emergency shutdown command received', source: 'OPERATOR' },
    { id: '7', timestamp: new Date(now.getTime() - 5 * 24 * 3600000).toISOString(), severity: 'error', eventType: 'COMM_FAIL', message: 'Communication timeout with gateway', source: 'NETWORK' },
    { id: '8', timestamp: new Date(now.getTime() - 5 * 24 * 3600000 + 5 * 3600000).toISOString(), severity: 'info', eventType: 'RECOVERY', message: 'Communication restored', source: 'NETWORK' },
    { id: '9', timestamp: new Date(now.getTime() - 7 * 24 * 3600000).toISOString(), severity: 'info', eventType: 'DATA_SYNC', message: 'Telemetry data synchronized', source: 'DATA_SERVICE' },
    { id: '10', timestamp: new Date(now.getTime() - 10 * 24 * 3600000).toISOString(), severity: 'warning', eventType: 'PERFORMANCE', message: 'Efficiency dropped below 85%', source: 'ANALYTICS' }
  ]
  return baseLogs.map(log => ({ ...log, id: `${deviceId}-${log.id}` }))
}

// Generate Maintenance History with realistic dates
const generateMaintenanceHistory = (deviceId: string): MaintenanceRecord[] => {
  const now = new Date()
  const baseRecords = [
    { id: '1', date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 45).toISOString().split('T')[0], title: 'Routine Inspection', description: 'Quarterly inspection completed. All parameters normal. Filters cleaned.', technician: 'John Smith', status: 'completed', type: 'success' },
    { id: '2', date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 90).toISOString().split('T')[0], title: 'Filter Replacement', description: 'Replaced primary and secondary air filters. Pressure drop within spec.', technician: 'Sarah Johnson', status: 'completed', type: 'primary' },
    { id: '3', date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 180).toISOString().split('T')[0], title: 'Sensor Calibration', description: 'Calibrated all sensors. Accuracy within ±0.5°C.', technician: 'Mike Chen', status: 'completed', type: 'info' },
    { id: '4', date: new Date(now.getFullYear(), now.getMonth(), now.getDate() - 270).toISOString().split('T')[0], title: 'Emergency Repair', description: 'Replaced worn bearings on fan motor.', technician: 'Emergency Team', status: 'completed', type: 'danger' }
  ]
  return baseRecords.map(r => ({ ...r, id: `${deviceId}-${r.id}` }))
}

// ==================== State ====================
const deviceLogs = ref<DeviceLog[]>([])
const maintenanceHistory = ref<MaintenanceRecord[]>([])
const logFilter = ref({ severity: '', dateRange: null as any })
const logPage = ref(1)
const logPageSize = ref(10)
const lastUpdateTime = ref('')
const energyPeriod = ref<'week' | 'month' | 'year'>('week')
let trendChart: echarts.ECharts | null = null
let energyChart: echarts.ECharts | null = null
const trendChartRef = ref<HTMLElement>()
const energyChartRef = ref<HTMLElement>()
let updateTimer: number
let chartInitRetryTimer: number

// ==================== Computed ====================
const onlineCount = computed(() => deviceList.value.filter(d => d.status === 'online').length)
const isMaintenanceOverdue = computed(() => currentDevice.value ? new Date(currentDevice.value.nextMaintenance) < new Date() : false)
const filteredLogs = computed(() => {
  let logs = [...deviceLogs.value]
  if (logFilter.value.severity) logs = logs.filter(l => l.severity === logFilter.value.severity)
  if (logFilter.value.dateRange && logFilter.value.dateRange.length === 2) {
    const [start, end] = logFilter.value.dateRange
    logs = logs.filter(l => { const ts = new Date(l.timestamp); return ts >= start && ts <= end })
  }
  return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
})
const paginatedLogs = computed(() => {
  const start = (logPage.value - 1) * logPageSize.value
  return filteredLogs.value.slice(start, start + logPageSize.value)
})
const deviceStats = computed(() => currentDevice.value ? [
  { key: 'temp', label: 'Temperature', value: `${currentDevice.value.metrics.temperature}°C`, icon: ColdDrink, trendClass: currentDevice.value.metrics.temperature > 28 ? 'trend-up' : 'trend-down', trendIcon: currentDevice.value.metrics.temperature > 28 ? '↑' : '↓' },
  { key: 'humidity', label: 'Humidity', value: `${currentDevice.value.metrics.humidity}%`, icon: Sunny, trendClass: currentDevice.value.metrics.humidity > 65 ? 'trend-up' : 'trend-down', trendIcon: currentDevice.value.metrics.humidity > 65 ? '↑' : '↓' },
  { key: 'power', label: 'Power', value: `${currentDevice.value.metrics.power} kW`, icon: Odometer, trendClass: currentDevice.value.metrics.power > 20 ? 'trend-up' : 'trend-down', trendIcon: currentDevice.value.metrics.power > 20 ? '↑' : '↓' },
  { key: 'efficiency', label: 'Efficiency', value: `${currentDevice.value.metrics.efficiency}%`, icon: MagicStick, trendClass: currentDevice.value.metrics.efficiency < 80 ? 'trend-down' : 'trend-up', trendIcon: currentDevice.value.metrics.efficiency < 80 ? '↓' : '↑' }
] : [])
const allMetrics = computed(() => {
  if (!currentDevice.value) return []
  const m = currentDevice.value.metrics
  return [
    { key: 'temperature', label: 'Temperature', value: m.temperature, unit: '°C', icon: ColdDrink, warning: m.temperature > 28, max: 50, percentage: (m.temperature / 50) * 100 },
    { key: 'humidity', label: 'Humidity', value: m.humidity, unit: '%', icon: Sunny, warning: m.humidity > 65, max: 100, percentage: m.humidity },
    { key: 'power', label: 'Power', value: m.power, unit: 'kW', icon: Odometer, warning: m.power > 20, max: 200, percentage: (m.power / 200) * 100 },
    { key: 'efficiency', label: 'Efficiency', value: m.efficiency, unit: '%', icon: MagicStick, warning: m.efficiency < 80, max: 100, percentage: m.efficiency }
  ]
})

// ==================== Helper Functions ====================
const getStatusType = (status: string) => ({ online: 'success', offline: 'info', warning: 'warning', error: 'danger' }[status] || 'info')
const getSystemLabel = (type: string) => ({ hvac: 'HVAC', lighting: 'Lighting', sas: 'Security', fas: 'Fire Alarm', plumbing: 'Plumbing' }[type] || type)
const getSystemTagType = (type: string) => ({ hvac: 'primary', lighting: 'success', sas: 'danger', fas: 'warning', plumbing: 'info' }[type] || '')
const getSeverityType = (severity: string) => ({ critical: 'danger', error: 'danger', warning: 'warning', info: 'info' }[severity] || 'info')
const getEventTypeTag = (type: string) => ({ ALARM: 'danger', ERROR: 'danger', WARNING: 'warning', INFO: 'info', CONFIG: 'primary', STARTUP: 'success', MAINTENANCE: 'info', COMMAND: 'primary', RECOVERY: 'success', DATA_SYNC: 'info', PERFORMANCE: 'warning', THRESHOLD: 'warning', COMM_FAIL: 'danger' }[type] || 'info')
const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
const formatDateTime = (dateStr: string) => new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' })
const goBack = () => router.push('/systems-devices/device-inventory')
const selectFirstDevice = () => { if (deviceList.value.length) selectedDeviceId.value = deviceList.value[0].id; onDeviceChange() }

// ==================== Load Device ====================
const loadDevice = (deviceId: string) => {
  const device = deviceList.value.find(d => d.id === deviceId)
  if (device) {
    currentDevice.value = device
    deviceLogs.value = generateDeviceLogs(deviceId)
    maintenanceHistory.value = generateMaintenanceHistory(deviceId)
    logPage.value = 1
    logFilter.value = { severity: '', dateRange: null }
    // 延迟一下确保 DOM 更新后再渲染图表
    nextTick(() => {
      setTimeout(() => {
        initAllCharts()
      }, 100)
    })
  } else {
    currentDevice.value = null
    ElMessage.warning('Device not found')
  }
}

const initAllCharts = () => {
  initTrendChart()
  initEnergyChart()
}

const onDeviceChange = () => { if (selectedDeviceId.value) loadDevice(selectedDeviceId.value) }
const loadDeviceBySerial = () => {
  const device = deviceList.value.find(d => d.serialNumber === deviceIdInput.value)
  if (device) { selectedDeviceId.value = device.id; loadDevice(device.id); deviceIdInput.value = '' }
  else ElMessage.warning(`No device found with serial number: ${deviceIdInput.value}`)
}

// ==================== Chart Functions with Real Current Date ====================
// Generate 24-hour time labels based on current time (last 24 hours)
const getLast24HourLabels = (): string[] => {
  const now = new Date()
  const labels: string[] = []
  for (let i = 23; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 3600000)
    labels.push(`${String(d.getHours()).padStart(2, '0')}:00`)
  }
  return labels
}

// Generate realistic trend data
const generateTrendData = () => {
  if (!currentDevice.value) return { xAxis: [], temperature: [], power: [], efficiency: [] }

  const xAxis = getLast24HourLabels()
  const baseTemp = currentDevice.value.metrics.temperature
  const basePower = currentDevice.value.metrics.power
  const baseEff = currentDevice.value.metrics.efficiency

  return {
    xAxis,
    temperature: xAxis.map((_, i) => {
      const hour = i
      const hourEffect = Math.sin(hour * 0.26) * 2.5
      const businessEffect = (hour >= 8 && hour <= 20) ? 1.5 : -1
      const random = (Math.random() - 0.5) * 1.5
      return +(baseTemp + hourEffect + businessEffect + random).toFixed(1)
    }),
    power: xAxis.map((_, i) => {
      const hour = i
      const businessEffect = (hour >= 8 && hour <= 18) ? basePower * 0.3 : 0
      const random = (Math.random() - 0.5) * basePower * 0.1
      return +(basePower + businessEffect + random).toFixed(1)
    }),
    efficiency: xAxis.map((_, i) => {
      const hour = i
      const baseVal = baseEff + (hour >= 8 && hour <= 18 ? -2 : 2)
      const random = (Math.random() - 0.5) * 3
      return Math.min(100, Math.max(65, +(baseVal + random).toFixed(1)))
    })
  }
}

// Generate energy consumption data based on current date
const generateEnergyData = () => {
  if (!currentDevice.value) return { xAxis: [], data: [] }

  const now = new Date()
  const baseEnergy = currentDevice.value.metrics.energy

  let labels: string[]
  let multiplier: number

  switch (energyPeriod.value) {
    case 'week':
      labels = []
      for (let i = 6; i >= 0; i--) {
        const d = new Date(now.getTime() - i * 24 * 3600000)
        labels.push(d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }))
      }
      multiplier = baseEnergy / 30
      break
    case 'month':
      labels = []
      for (let i = 29; i >= 0; i--) {
        const d = new Date(now.getTime() - i * 24 * 3600000)
        labels.push(`${d.getMonth() + 1}/${d.getDate()}`)
      }
      multiplier = baseEnergy / 30
      break
    default:
      labels = []
      for (let i = 11; i >= 0; i--) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
        labels.push(d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }))
      }
      multiplier = baseEnergy / 12
  }

  return {
    xAxis: labels,
    data: labels.map((_, i) => {
      const weekdayEffect = energyPeriod.value === 'week' ? (i === 5 || i === 6 ? 0.6 : 1) : 1
      const random = 0.7 + Math.random() * 0.8
      return +(multiplier * weekdayEffect * random).toFixed(0)
    })
  }
}

const initTrendChart = () => {
  if (!trendChartRef.value || !currentDevice.value) {
    // 如果 DOM 还没准备好，延迟重试
    if (chartInitRetryTimer) clearTimeout(chartInitRetryTimer)
    chartInitRetryTimer = setTimeout(() => initTrendChart(), 200)
    return
  }
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = generateTrendData()

  trendChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Temperature (°C)', 'Power (kW)', 'Efficiency (%)'], bottom: 0, left: 'center', itemWidth: 25, itemHeight: 10 },
    grid: { top: 30, right: 20, bottom: 40, left: 50, containLabel: true },
    xAxis: { type: 'category', data: data.xAxis, axisLabel: { rotate: 45, interval: 3, fontSize: 10 } },
    yAxis: [
      { type: 'value', name: 'Temperature (°C) / Power (kW)', nameTextStyle: { fontSize: 11 }, axisLabel: { fontSize: 10 } },
      { type: 'value', name: 'Efficiency (%)', nameTextStyle: { fontSize: 11 }, min: 0, max: 100, axisLabel: { fontSize: 10 } }
    ],
    series: [
      { name: 'Temperature (°C)', type: 'line', data: data.temperature, smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, symbol: 'circle', symbolSize: 4, areaStyle: { opacity: 0.1, color: '#f56c6c' } },
      { name: 'Power (kW)', type: 'line', data: data.power, smooth: true, lineStyle: { color: '#e6a23c', width: 2 }, symbol: 'diamond', symbolSize: 4, areaStyle: { opacity: 0.1, color: '#e6a23c' } },
      { name: 'Efficiency (%)', type: 'line', yAxisIndex: 1, data: data.efficiency, smooth: true, lineStyle: { color: '#67c23a', width: 2 }, symbol: 'triangle', symbolSize: 4, areaStyle: { opacity: 0.1, color: '#67c23a' } }
    ]
  })
}

const initEnergyChart = () => {
  if (!energyChartRef.value || !currentDevice.value) {
    if (chartInitRetryTimer) clearTimeout(chartInitRetryTimer)
    chartInitRetryTimer = setTimeout(() => initEnergyChart(), 200)
    return
  }
  if (energyChart) energyChart.dispose()

  energyChart = echarts.init(energyChartRef.value)
  const data = generateEnergyData()

  energyChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Energy: {c} kWh' },
    grid: { top: 30, right: 20, bottom: 40, left: 55, containLabel: true },
    xAxis: { type: 'category', data: data.xAxis, axisLabel: { rotate: 45, interval: energyPeriod.value === 'week' ? 0 : Math.floor(data.xAxis.length / 6), fontSize: 10 } },
    yAxis: { type: 'value', name: 'Energy Consumption (kWh)', nameTextStyle: { fontSize: 11 }, axisLabel: { fontSize: 10 } },
    series: [{
      name: 'Energy Consumption', type: 'bar', data: data.data, barWidth: energyPeriod.value === 'week' ? '60%' : '50%',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#409eff' }, { offset: 1, color: '#67c23a' }] } }
    }]
  })
}

const refreshEnergyChart = () => {
  if (energyChart && currentDevice.value) {
    const data = generateEnergyData()
    energyChart.setOption({ xAxis: { data: data.xAxis }, series: [{ data: data.data }] })
  }
}

const updateTrendChartData = () => {
  if (trendChart && currentDevice.value) {
    const newData = generateTrendData()
    trendChart.setOption({
      series: [
        { data: newData.temperature },
        { data: newData.power },
        { data: newData.efficiency }
      ]
    })
  }
}

// ==================== Actions ====================
const controlDevice = () => ElMessage.info(`Opening control panel for ${currentDevice.value?.name}`)
const createWorkOrder = () => ElMessage.info(`Creating work order for ${currentDevice.value?.name}`)
const exportData = () => ElMessage.success(`Exporting data for ${currentDevice.value?.name}`)
const exportLogs = () => ElMessage.success('Exporting device logs to CSV')
const addMaintenanceRecord = () => ElMessage.info('Opening add maintenance record form')
const viewLogDetail = (log: DeviceLog) => ElMessage.info(`Viewing details for log: ${log.message}`)
const filterLogs = () => { logPage.value = 1 }
const resetLogFilters = () => { logFilter.value = { severity: '', dateRange: null }; filterLogs() }
const handleLogPageChange = () => {}

// ==================== Real-time Updates ====================
const startRealtimeUpdates = () => {
  updateTimer = window.setInterval(() => {
    lastUpdateTime.value = new Date().toLocaleTimeString()
    if (currentDevice.value) {
      const m = currentDevice.value.metrics
      m.temperature += (Math.random() - 0.5) * 0.2
      m.power += (Math.random() - 0.5) * 0.3
      m.temperature = Math.round(m.temperature * 10) / 10
      m.power = Math.round(m.power * 10) / 10
      updateTrendChartData()
    }
  }, 5000)
}

// ==================== Resize Handler ====================
const handleResize = () => {
  if (trendChart) trendChart.resize()
  if (energyChart) energyChart.resize()
}

// ==================== Lifecycle ====================
onMounted(() => {
  deviceList.value = generateDeviceList()

  // 设置 loading 进度
  let msgIdx = 0
  const msgInt = setInterval(() => {
    if (msgIdx < loadingMessages.length - 1) {
      msgIdx++
      loadingMessage.value = loadingMessages[msgIdx]
    }
  }, 400)

  const progInt = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(msgInt)
    clearInterval(progInt)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      // 页面加载完成后，选择第一个设备并渲染图表
      if (deviceList.value.length) {
        selectedDeviceId.value = deviceList.value[0].id
        loadDevice(selectedDeviceId.value)
      }
      startRealtimeUpdates()
    }, 400)
  }, 2000)

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  clearInterval(updateTimer)
  if (chartInitRetryTimer) clearTimeout(chartInitRetryTimer)
  window.removeEventListener('resize', handleResize)
  if (trendChart) trendChart.dispose()
  if (energyChart) energyChart.dispose()
})

watch(energyPeriod, () => { refreshEnergyChart() })
</script>

<style scoped>
.loading-container { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-overlay { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: fadeInUp 0.6s ease-out; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
.device-details-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.header-right { display: flex; gap: 12px; }
.device-selector-card { background: white; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.selector-label { display: flex; align-items: center; gap: 8px; font-weight: 600; color: #1e293b; }
.selector-controls { display: flex; gap: 12px; flex-wrap: wrap; }
.device-stats-mini { display: flex; gap: 16px; }
.mini-stat { display: flex; gap: 4px; font-size: 13px; }
.mini-label { color: #64748b; }
.mini-value { font-weight: 600; color: #1e293b; }
.mini-value.online { color: #10b981; }
.device-option { display: flex; align-items: center; gap: 8px; }
.option-model { font-size: 12px; color: #94a3b8; margin-left: auto; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.status-online { background: #10b981; }
.status-dot.status-warning { background: #f59e0b; }
.status-dot.status-error { background: #ef4444; }
.status-dot.status-offline { background: #6b7280; }
.overview-section { margin-bottom: 24px; }
.device-overview-card { background: white; border-radius: 16px; display: flex; gap: 24px; padding: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.device-image-area { flex-shrink: 0; width: 200px; height: 200px; background: #f8fafc; border-radius: 12px; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; }
.device-image { width: 100%; height: 100%; object-fit: contain; }
.device-status-badge { position: absolute; top: 8px; right: 8px; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.device-status-badge.online { background: #10b981; color: white; }
.device-status-badge.warning { background: #f59e0b; color: white; }
.device-status-badge.error { background: #ef4444; color: white; }
.device-status-badge.offline { background: #6b7280; color: white; }
.image-fallback { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; color: #94a3b8; }
.device-info-area { flex: 1; }
.device-title { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.device-title h1 { font-size: 24px; font-weight: 700; color: #1e293b; margin: 0; }
.device-meta { display: flex; flex-wrap: wrap; gap: 24px; margin-bottom: 20px; }
.meta-item { display: flex; align-items: center; gap: 6px; color: #64748b; font-size: 14px; }
.meta-item .el-icon { color: #3b82f6; }
.device-specs { display: flex; flex-wrap: wrap; gap: 24px; background: #f8fafc; padding: 16px; border-radius: 12px; }
.spec-item { display: flex; gap: 8px; font-size: 13px; }
.spec-label { color: #64748b; }
.text-danger { color: #ef4444; font-weight: 500; }
.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat-icon .el-icon { font-size: 32px; color: #3b82f6; }
.stat-info { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }
.stat-trend { font-size: 20px; font-weight: 600; }
.stat-trend.trend-up { color: #ef4444; }
.stat-trend.trend-down { color: #10b981; }
.details-grid { display: grid; grid-template-columns: 1fr 1.5fr; gap: 24px; margin-bottom: 24px; }
.section-card { background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); margin-bottom: 24px; }
.section-card.full-width { grid-column: span 2; margin-bottom: 0; }
.card-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid #e4e7ed; flex-wrap: wrap; gap: 12px; }
.card-header h3 { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; color: #1e293b; margin: 0; }
.card-header .el-icon { color: #3b82f6; }
.chart-date-info { font-size: 11px; color: #94a3b8; }
.log-filters { display: flex; gap: 8px; flex-wrap: wrap; }
.update-time { font-size: 11px; color: #94a3b8; }
.metrics-list { padding: 20px; }
.metric-row { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f1f5f9; }
.metric-row:last-child { border-bottom: none; }
.metric-label { display: flex; align-items: center; gap: 10px; font-size: 14px; color: #475569; }
.metric-value-area { flex: 1; max-width: 200px; }
.metric-value { font-size: 18px; font-weight: 600; color: #1e293b; }
.metric-unit { font-size: 12px; color: #64748b; font-weight: normal; }
.text-warning { color: #f59e0b; }
.metric-progress { margin-top: 6px; height: 4px; background: #e2e8f0; border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6); border-radius: 2px; transition: width 0.3s ease; }
.progress-fill.fill-warning { background: linear-gradient(90deg, #f59e0b, #ef4444); }
.metrics-grid-2col { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; padding: 20px; }
.metric-card-mini { background: #f8fafc; border-radius: 12px; padding: 16px; text-align: center; }
.metric-label-mini { display: block; font-size: 12px; color: #64748b; margin-bottom: 8px; }
.metric-value-mini { font-size: 20px; font-weight: 700; color: #1e293b; }
.trend-chart, .energy-chart { width: 100%; height: 300px; min-height: 280px; }
.logs-container { padding: 16px; }
.pagination-wrapper { display: flex; justify-content: flex-end; padding: 16px; border-top: 1px solid #e4e7ed; }
.timeline-container { padding: 20px; max-height: 400px; overflow-y: auto; }
.timeline-content h4 { margin: 0 0 8px 0; font-size: 14px; font-weight: 600; color: #1e293b; }
.timeline-content p { margin: 0 0 8px 0; font-size: 13px; color: #64748b; }
.timeline-footer { display: flex; justify-content: space-between; align-items: center; }
.technician { font-size: 11px; color: #94a3b8; }
.empty-state { display: flex; justify-content: center; align-items: center; height: 50vh; }
@media (max-width: 1200px) { .details-grid { grid-template-columns: 1fr; } .section-card.full-width { grid-column: span 1; } .stats-cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .device-overview-card { flex-direction: column; align-items: center; text-align: center; } .device-title { justify-content: center; } .device-meta { justify-content: center; } .device-specs { justify-content: center; } .stats-cards { grid-template-columns: 1fr; } .metrics-grid-2col { grid-template-columns: 1fr; } .trend-chart, .energy-chart { height: 240px; } .device-selector-card { flex-direction: column; align-items: stretch; } .selector-controls { flex-direction: column; } .selector-controls .el-select, .selector-controls .el-input { width: 100% !important; } .card-header { flex-direction: column; align-items: flex-start; } .log-filters { width: 100%; } }
</style>