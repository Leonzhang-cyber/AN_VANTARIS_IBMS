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
        <div class="loading-tip">Device Inventory</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="device-inventory">
    <!-- Header -->
    <div class="inventory-header">
      <div class="header-title">
        <el-icon><Cpu /></el-icon>
        <span>Device Inventory</span>
        <el-tag type="primary" size="small">{{ totalDevices }} Total</el-tag>
      </div>
      <div class="header-actions">
        <el-button type="primary" :icon="Plus" @click="openAddDeviceDialog">
          Add Device
        </el-button>
        <el-button :icon="Download" @click="exportDevices">
          Export
        </el-button>
        <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <div class="stat-card online">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.online }}</span>
          <span class="stat-label">Online</span>
        </div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.warning }}</span>
          <span class="stat-label">Warning</span>
        </div>
      </div>
      <div class="stat-card error">
        <div class="stat-icon"><el-icon><CircleCloseFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.error }}</span>
          <span class="stat-label">Error</span>
        </div>
      </div>
      <div class="stat-card offline">
        <div class="stat-icon"><el-icon><RemoveFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.offline }}</span>
          <span class="stat-label">Offline</span>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchKeyword"
            placeholder="Search by device name, model, or serial"
            clearable
            :prefix-icon="Search"
            style="width: 280px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
        />
        <el-select
            v-model="filterSystem"
            placeholder="System Type"
            clearable
            style="width: 160px"
            @change="handleFilter"
        >
          <el-option label="All Systems" value="" />
          <el-option label="HVAC" value="hvac" />
          <el-option label="Lighting" value="lighting" />
          <el-option label="Security" value="sas" />
          <el-option label="Fire Alarm" value="fas" />
          <el-option label="Plumbing" value="plumbing" />
        </el-select>
        <el-select
            v-model="filterStatus"
            placeholder="Status"
            clearable
            style="width: 140px"
            @change="handleFilter"
        >
          <el-option label="All Status" value="" />
          <el-option label="Online" value="online" />
          <el-option label="Warning" value="warning" />
          <el-option label="Error" value="error" />
          <el-option label="Offline" value="offline" />
        </el-select>
        <el-select
            v-model="filterArea"
            placeholder="Area"
            clearable
            style="width: 160px"
            @change="handleFilter"
        >
          <el-option label="All Areas" value="" />
          <el-option v-for="area in areas" :key="area" :label="area" :value="area" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button :icon="RefreshRight" @click="resetFilters">
          Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Device Table -->
    <div class="device-table-container">
      <el-table
          :data="paginatedDevices"
          stripe
          border
          style="width: 100%"
          @row-click="handleRowClick"
          v-loading="tableLoading"
          :row-class-name="tableRowClassName"
      >
        <el-table-column type="index" label="#" width="50" fixed="left" />
        <el-table-column label="Device" width="260" fixed="left">
          <template #default="{ row }">
            <div class="device-cell">
              <el-avatar :src="row.imageUrl" :size="40" shape="square" fit="cover">
                <template #error>
                  <el-icon :size="24"><Cpu /></el-icon>
                </template>
              </el-avatar>
              <div class="device-info">
                <span class="device-name">{{ row.name }}</span>
                <span class="device-model">{{ row.model }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="serialNumber" label="Serial Number" width="160" />
        <el-table-column prop="manufacturer" label="Manufacturer" width="140" />
        <el-table-column label="System" width="120">
          <template #default="{ row }">
            <el-tag :type="getSystemTagType(row.systemType)" size="small">
              {{ getSystemLabel(row.systemType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="110">
          <template #default="{ row }">
            <div class="status-cell">
              <span class="status-dot" :class="`status-${row.status}`"></span>
              <span :class="`status-text status-${row.status}`">
                {{ row.status.toUpperCase() }}
              </span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Temperature" width="110">
          <template #default="{ row }">
            <span :class="row.metrics.temperature > 28 ? 'text-warning' : ''">
              {{ row.metrics.temperature }}°C
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Power" width="110">
          <template #default="{ row }">
            <span :class="row.metrics.power > 20 ? 'text-warning' : ''">
              {{ row.metrics.power }} kW
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Efficiency" width="110">
          <template #default="{ row }">
            <el-progress
                :percentage="row.metrics.efficiency"
                :stroke-width="6"
                :show-text="false"
                :color="getEfficiencyColor(row.metrics.efficiency)"
                style="width: 80px"
            />
            <span :class="row.metrics.efficiency < 80 ? 'text-danger' : ''" style="margin-left: 8px">
              {{ row.metrics.efficiency }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Last Maintenance" width="140">
          <template #default="{ row }">
            {{ formatDate(row.lastMaintenance) }}
          </template>
        </el-table-column>
        <el-table-column label="Next Maintenance" width="140">
          <template #default="{ row }">
            <span :class="isMaintenanceOverdue(row.nextMaintenance) ? 'text-danger' : ''">
              {{ formatDate(row.nextMaintenance) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" :icon="View" @click.stop="viewDeviceDetail(row)">
              View
            </el-button>
            <el-button size="small" :icon="Switch" type="primary" @click.stop="controlDevice(row)">
              Control
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredDevices.length"
            layout="total, sizes, prev, pager, next, jumper"
            background
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Device Detail Drawer -->
    <el-drawer
        v-model="detailDrawerVisible"
        :title="selectedDevice?.name || 'Device Details'"
        size="50%"
        direction="rtl"
    >
      <div v-if="selectedDevice" class="device-detail">
        <!-- Device Image -->
        <div class="detail-image">
          <el-image
              :src="selectedDevice.imageUrl"
              fit="contain"
              :preview-src-list="[selectedDevice.imageUrl]"
          >
            <template #error>
              <div class="image-fallback">
                <el-icon :size="60"><Cpu /></el-icon>
                <span>No Image</span>
              </div>
            </template>
          </el-image>
        </div>

        <!-- Basic Info -->
        <div class="detail-section">
          <h3>Basic Information</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Device Name">{{ selectedDevice.name }}</el-descriptions-item>
            <el-descriptions-item label="Model">{{ selectedDevice.model }}</el-descriptions-item>
            <el-descriptions-item label="Manufacturer">{{ selectedDevice.manufacturer }}</el-descriptions-item>
            <el-descriptions-item label="Serial Number">{{ selectedDevice.serialNumber }}</el-descriptions-item>
            <el-descriptions-item label="System Type">
              <el-tag :type="getSystemTagType(selectedDevice.systemType)" size="small">
                {{ getSystemLabel(selectedDevice.systemType) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Status">
              <div class="status-cell">
                <span class="status-dot" :class="`status-${selectedDevice.status}`"></span>
                <span>{{ selectedDevice.status.toUpperCase() }}</span>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="Installation Date">{{ formatDate(selectedDevice.installationDate) }}</el-descriptions-item>
            <el-descriptions-item label="Last Maintenance">{{ formatDate(selectedDevice.lastMaintenance) }}</el-descriptions-item>
            <el-descriptions-item label="Next Maintenance" :span="2">
              <span :class="isMaintenanceOverdue(selectedDevice.nextMaintenance) ? 'text-danger' : ''">
                {{ formatDate(selectedDevice.nextMaintenance) }}
              </span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Metrics -->
        <div class="detail-section">
          <h3>Real-time Metrics</h3>
          <div class="metrics-grid">
            <div class="metric-card" v-for="metric in detailMetrics" :key="metric.key">
              <div class="metric-icon">
                <el-icon :size="24"><component :is="metric.icon" /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-value">
                  {{ metric.value }}
                  <span class="metric-unit">{{ metric.unit }}</span>
                </span>
                <span class="metric-label">{{ metric.label }}</span>
              </div>
              <div class="metric-bar">
                <div
                    class="metric-fill"
                    :style="{ width: metric.percentage + '%' }"
                    :class="{ 'fill-warning': metric.warning }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Trend Chart -->
        <div class="detail-section">
          <h3>Trend Analysis - Last 24 Hours</h3>
          <div ref="detailChartRef" class="detail-chart"></div>
        </div>

        <!-- Actions -->
        <div class="detail-actions">
          <el-button type="primary" :icon="Switch" @click="controlDevice(selectedDevice)">
            Control Device
          </el-button>
          <el-button :icon="Tools" @click="createWorkOrder(selectedDevice)">
            Create Work Order
          </el-button>
          <el-button :icon="Download" @click="exportDeviceData(selectedDevice)">
            Export Data
          </el-button>
        </div>
      </div>
    </el-drawer>

    <!-- Add Device Dialog -->
    <el-dialog
        v-model="addDialogVisible"
        title="Add New Device"
        width="600px"
        :close-on-click-modal="false"
    >
      <el-form :model="newDeviceForm" :rules="deviceFormRules" ref="deviceFormRef" label-width="120px">
        <el-form-item label="Device Name" prop="name">
          <el-input v-model="newDeviceForm.name" placeholder="Enter device name" />
        </el-form-item>
        <el-form-item label="Model" prop="model">
          <el-input v-model="newDeviceForm.model" placeholder="Enter device model" />
        </el-form-item>
        <el-form-item label="Manufacturer" prop="manufacturer">
          <el-input v-model="newDeviceForm.manufacturer" placeholder="Enter manufacturer" />
        </el-form-item>
        <el-form-item label="Serial Number" prop="serialNumber">
          <el-input v-model="newDeviceForm.serialNumber" placeholder="Enter serial number" />
        </el-form-item>
        <el-form-item label="System Type" prop="systemType">
          <el-select v-model="newDeviceForm.systemType" placeholder="Select system type" style="width: 100%">
            <el-option label="HVAC" value="hvac" />
            <el-option label="Lighting" value="lighting" />
            <el-option label="Security" value="sas" />
            <el-option label="Fire Alarm" value="fas" />
            <el-option label="Plumbing" value="plumbing" />
          </el-select>
        </el-form-item>
        <el-form-item label="Area" prop="area">
          <el-select v-model="newDeviceForm.area" placeholder="Select area" style="width: 100%">
            <el-option v-for="area in areas" :key="area" :label="area" :value="area" />
          </el-select>
        </el-form-item>
        <el-form-item label="Installation Date" prop="installationDate">
          <el-date-picker v-model="newDeviceForm.installationDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Image URL" prop="imageUrl">
          <el-input v-model="newDeviceForm.imageUrl" placeholder="Enter image URL" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitAddDevice" :loading="addingDevice">
          Add Device
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Cpu,
  Plus,
  Download,
  Refresh,
  CircleCheckFilled,
  WarningFilled,
  CircleCloseFilled,
  RemoveFilled,
  Search,
  RefreshRight,
  View,
  Switch,
  Tools,
  ColdDrink,
  Sunny,
  Odometer,
  TrendCharts,
  MagicStick,
  Lock,
  Bell,
  House,
  Grid
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading device inventory...',
  'Fetching device details...',
  'Initializing table...',
  'Almost ready...'
]

// ==================== Device Data ====================
interface DeviceMetrics {
  temperature: number
  humidity: number
  power: number
  energy: number
  uptime: number
  efficiency: number
  pressure?: number
  flowRate?: number
  co2Level?: number
  noiseLevel?: number
}

interface Device {
  id: string
  name: string
  type: 'device'
  status: 'online' | 'offline' | 'warning' | 'error'
  model: string
  manufacturer: string
  serialNumber: string
  systemType: string
  area: string
  floor: string
  imageUrl: string
  metrics: DeviceMetrics
  lastMaintenance: string
  nextMaintenance: string
  installationDate: string
}

// Mock Device Data
const devices = ref<Device[]>([
  {
    id: 'dev-ahu-b2-01',
    name: 'AHU-B2-01 Air Handler',
    type: 'device',
    status: 'online',
    model: 'Carrier 39G',
    manufacturer: 'Carrier',
    serialNumber: 'CA-2024-B201',
    systemType: 'hvac',
    area: 'Basement B2',
    floor: 'B2',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',
    metrics: { temperature: 23.0, humidity: 50, power: 18.5, energy: 15200, uptime: 8760, efficiency: 94, pressure: 280, flowRate: 15000, noiseLevel: 62 },
    lastMaintenance: '2026-04-15',
    nextMaintenance: '2026-07-15',
    installationDate: '2024-01-10'
  },
  {
    id: 'dev-fcu-b2-01',
    name: 'FCU-B2-01 Fan Coil',
    type: 'device',
    status: 'online',
    model: 'Daikin FXMQ',
    manufacturer: 'Daikin',
    serialNumber: 'DK-2024-B201',
    systemType: 'hvac',
    area: 'Basement B2',
    floor: 'B2',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',
    metrics: { temperature: 22.5, humidity: 48, power: 6.8, energy: 5400, uptime: 8760, efficiency: 91, pressure: 160, flowRate: 1800, noiseLevel: 38 },
    lastMaintenance: '2026-05-01',
    nextMaintenance: '2026-08-01',
    installationDate: '2024-02-15'
  },
  {
    id: 'dev-chiller-b2-01',
    name: 'CH-B2-01 Chiller',
    type: 'device',
    status: 'online',
    model: 'Carrier AquaEdge',
    manufacturer: 'Carrier',
    serialNumber: 'CA-2024-B202',
    systemType: 'hvac',
    area: 'Basement B2',
    floor: 'B2',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',
    metrics: { temperature: 28.0, humidity: 65, power: 85.0, energy: 68000, uptime: 8760, efficiency: 92, pressure: 420, flowRate: 45000, noiseLevel: 72 },
    lastMaintenance: '2026-04-10',
    nextMaintenance: '2026-07-10',
    installationDate: '2024-01-05'
  },
  {
    id: 'dev-exhaust-b2-02',
    name: 'EF-B2-02 Exhaust Fan',
    type: 'device',
    status: 'warning',
    model: 'Greenheck CUBE',
    manufacturer: 'Greenheck',
    serialNumber: 'GH-2024-B202',
    systemType: 'hvac',
    area: 'Basement B2',
    floor: 'B2',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp',
    metrics: { temperature: 29.5, humidity: 58, power: 8.2, energy: 6560, uptime: 8760, efficiency: 86, pressure: 195, flowRate: 8500, noiseLevel: 68 },
    lastMaintenance: '2026-03-15',
    nextMaintenance: '2026-06-15',
    installationDate: '2024-01-25'
  },
  {
    id: 'dev-ahu-2f-01',
    name: 'AHU-2F-01 Air Handler',
    type: 'device',
    status: 'error',
    model: 'Trane IntelliPak',
    manufacturer: 'Trane',
    serialNumber: 'TR-2024-2F01',
    systemType: 'hvac',
    area: 'Office 2F',
    floor: '2F',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp',
    metrics: { temperature: 31.2, humidity: 72, power: 22.5, energy: 18500, uptime: 8760, efficiency: 72, pressure: 195, flowRate: 9800, noiseLevel: 78, vibration: 4.2 },
    lastMaintenance: '2024-02-28',
    nextMaintenance: '2026-04-28',
    installationDate: '2023-08-10'
  },
  {
    id: 'dev-light-b2-01',
    name: 'LIGHT-B2-01 Main Controller',
    type: 'device',
    status: 'online',
    model: 'Philips Dynalite',
    manufacturer: 'Philips',
    serialNumber: 'PH-2024-B201',
    systemType: 'lighting',
    area: 'Basement B2',
    floor: 'B2',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp',
    metrics: { temperature: 26.5, humidity: 42, power: 4.2, energy: 3200, uptime: 8760, efficiency: 96 },
    lastMaintenance: '2026-05-15',
    nextMaintenance: '2026-08-15',
    installationDate: '2024-01-20'
  },
  {
    id: 'dev-access-1f-01',
    name: 'ACS-1F-01 Main Entrance',
    type: 'device',
    status: 'online',
    model: 'HID VertX',
    manufacturer: 'HID Global',
    serialNumber: 'HD-2024-1F01',
    systemType: 'sas',
    area: 'Lobby 1F',
    floor: '1F',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg',
    metrics: { temperature: 35.0, humidity: 40, power: 0.5, energy: 400, uptime: 8760, efficiency: 99 },
    lastMaintenance: '2026-06-01',
    nextMaintenance: '2026-09-01',
    installationDate: '2024-01-05'
  },
  {
    id: 'dev-smoke-1f-01',
    name: 'SD-1F-01 Smoke Detector',
    type: 'device',
    status: 'online',
    model: 'Honeywell XLS',
    manufacturer: 'Honeywell',
    serialNumber: 'HW-2024-1F01',
    systemType: 'fas',
    area: 'Lobby 1F',
    floor: '1F',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg',
    metrics: { temperature: 22.0, humidity: 55, power: 0.3, energy: 240, uptime: 8760, efficiency: 99, co2Level: 440, noiseLevel: 13 },
    lastMaintenance: '2026-04-10',
    nextMaintenance: '2026-07-10',
    installationDate: '2024-01-01'
  },
  {
    id: 'dev-pump-b2-02',
    name: 'PUMP-B2-02 Booster Pump',
    type: 'device',
    status: 'warning',
    model: 'Grundfos CR',
    manufacturer: 'Grundfos',
    serialNumber: 'GF-2024-B202',
    systemType: 'plumbing',
    area: 'Basement B2',
    floor: 'B2',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png',
    metrics: { temperature: 38.0, humidity: 72, power: 9.5, energy: 7600, uptime: 8760, efficiency: 76, pressure: 320, flowRate: 42, vibration: 3.8 },
    lastMaintenance: '2024-02-28',
    nextMaintenance: '2026-04-28',
    installationDate: '2023-11-20'
  },
  {
    id: 'dev-camera-2f-01',
    name: 'CAM-2F-01 Bullet Camera',
    type: 'device',
    status: 'warning',
    model: 'Hikvision DS-2CD',
    manufacturer: 'Hikvision',
    serialNumber: 'HK-2024-2F01',
    systemType: 'sas',
    area: 'Office 2F',
    floor: '2F',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314234432.webp',
    metrics: { temperature: 40.0, humidity: 35, power: 1.0, energy: 800, uptime: 8760, efficiency: 95 },
    lastMaintenance: '2026-05-22',
    nextMaintenance: '2026-08-22',
    installationDate: '2024-02-08'
  },
  {
    id: 'dev-fcu-1f-01',
    name: 'FCU-1F-01 Fan Coil Unit',
    type: 'device',
    status: 'warning',
    model: 'Daikin FXMQ',
    manufacturer: 'Daikin',
    serialNumber: 'DK-2024-1F01',
    systemType: 'hvac',
    area: 'Lobby 1F',
    floor: '1F',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp',
    metrics: { temperature: 25.8, humidity: 58, power: 8.2, energy: 6540, uptime: 8760, efficiency: 87, pressure: 180, flowRate: 2200, noiseLevel: 42 },
    lastMaintenance: '2024-03-10',
    nextMaintenance: '2026-05-10',
    installationDate: '2023-06-20'
  },
  {
    id: 'dev-chiller-roof-01',
    name: 'CH-RF-01 Chiller',
    type: 'device',
    status: 'online',
    model: 'Carrier AquaEdge',
    manufacturer: 'Carrier',
    serialNumber: 'CA-2024-RF01',
    systemType: 'hvac',
    area: 'Roof Mechanical',
    floor: 'RF',
    imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg',
    metrics: { temperature: 35.0, humidity: 75, power: 150.0, energy: 120000, uptime: 8760, efficiency: 88, pressure: 450, flowRate: 80000, noiseLevel: 85 },
    lastMaintenance: '2026-04-01',
    nextMaintenance: '2026-07-01',
    installationDate: '2024-01-01'
  }
])

// ==================== Filter State ====================
const searchKeyword = ref('')
const filterSystem = ref('')
const filterStatus = ref('')
const filterArea = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// ==================== Computed ====================
const areas = computed(() => {
  const areaSet = new Set<string>()
  devices.value.forEach(d => areaSet.add(d.area))
  return Array.from(areaSet).sort()
})

const totalDevices = computed(() => devices.value.length)

const stats = computed(() => {
  return {
    online: devices.value.filter(d => d.status === 'online').length,
    warning: devices.value.filter(d => d.status === 'warning').length,
    error: devices.value.filter(d => d.status === 'error').length,
    offline: devices.value.filter(d => d.status === 'offline').length
  }
})

const filteredDevices = computed(() => {
  let result = [...devices.value]

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(d =>
        d.name.toLowerCase().includes(keyword) ||
        d.model.toLowerCase().includes(keyword) ||
        d.serialNumber.toLowerCase().includes(keyword)
    )
  }

  if (filterSystem.value) {
    result = result.filter(d => d.systemType === filterSystem.value)
  }

  if (filterStatus.value) {
    result = result.filter(d => d.status === filterStatus.value)
  }

  if (filterArea.value) {
    result = result.filter(d => d.area === filterArea.value)
  }

  return result
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getSystemLabel = (systemType: string) => {
  const labels: Record<string, string> = {
    hvac: 'HVAC',
    lighting: 'Lighting',
    sas: 'Security',
    fas: 'Fire Alarm',
    plumbing: 'Plumbing'
  }
  return labels[systemType] || systemType
}

const getSystemTagType = (systemType: string) => {
  const types: Record<string, string> = {
    hvac: 'primary',
    lighting: 'success',
    sas: 'danger',
    fas: 'warning',
    plumbing: 'info'
  }
  return types[systemType] || ''
}

const getEfficiencyColor = (efficiency: number) => {
  if (efficiency >= 90) return '#67c23a'
  if (efficiency >= 70) return '#e6a23c'
  return '#f56c6c'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const isMaintenanceOverdue = (dateStr: string) => {
  return new Date(dateStr) < new Date()
}

const tableRowClassName = ({ row }: { row: Device }) => {
  return `row-${row.status}`
}

// ==================== Filter Methods ====================
const handleSearch = () => {
  currentPage.value = 1
  tableLoading.value = true
  setTimeout(() => { tableLoading.value = false }, 300)
}

const handleFilter = () => {
  currentPage.value = 1
  tableLoading.value = true
  setTimeout(() => { tableLoading.value = false }, 300)
}

const resetFilters = () => {
  searchKeyword.value = ''
  filterSystem.value = ''
  filterStatus.value = ''
  filterArea.value = ''
  currentPage.value = 1
  handleFilter()
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed successfully')
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handlePageChange = () => {
  // Page changed
}

// ==================== Device Actions ====================
const selectedDevice = ref<Device | null>(null)
const detailDrawerVisible = ref(false)
let detailChart: echarts.ECharts | null = null
const detailChartRef = ref<HTMLElement>()

const generateTrendData = (device: Device) => {
  const now = new Date()
  const hours: string[] = []
  for (let i = 23; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 3600000)
    hours.push(`${String(d.getHours()).padStart(2, '0')}:00`)
  }
  const baseTemp = device.metrics.temperature || 24
  const basePower = device.metrics.power || 10

  return {
    xAxis: hours,
    temperature: hours.map((_, i) => {
      const hourEffect = Math.sin(i * 0.5) * 3
      const random = (Math.random() - 0.5) * 2
      return +(baseTemp + hourEffect + random).toFixed(1)
    }),
    power: hours.map((_, i) => {
      const hour = i
      const businessEffect = (hour >= 8 && hour <= 18) ? 5 : 0
      const random = (Math.random() - 0.5) * 3
      return +(basePower + businessEffect + random).toFixed(1)
    })
  }
}

const initDetailChart = () => {
  if (!detailChartRef.value || !selectedDevice.value) return

  if (detailChart) {
    detailChart.dispose()
  }

  detailChart = echarts.init(detailChartRef.value)
  const trendData = generateTrendData(selectedDevice.value)

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(13, 25, 48, 0.95)',
      borderColor: 'rgba(64, 158, 255, 0.3)',
      textStyle: { color: '#e5eaf3', fontSize: 12 }
    },
    legend: {
      data: ['Temperature (°C)', 'Power (kW)'],
      textStyle: { color: '#8899aa' }
    },
    grid: {
      top: 30,
      right: 20,
      bottom: 25,
      left: 50
    },
    xAxis: {
      type: 'category',
      data: trendData.xAxis,
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.15)' } },
      axisLabel: { color: '#8899aa', fontSize: 10, interval: 3 }
    },
    yAxis: {
      type: 'value',
      name: 'Value',
      nameTextStyle: { color: '#8899aa' },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } },
      axisLabel: { color: '#8899aa' }
    },
    series: [
      {
        name: 'Temperature (°C)',
        type: 'line',
        data: trendData.temperature,
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        lineStyle: { width: 2, color: '#f56c6c' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.02)' }
          ])
        }
      },
      {
        name: 'Power (kW)',
        type: 'line',
        data: trendData.power,
        smooth: true,
        symbol: 'diamond',
        symbolSize: 4,
        lineStyle: { width: 2, color: '#e6a23c' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(230, 162, 60, 0.2)' },
            { offset: 1, color: 'rgba(230, 162, 60, 0.02)' }
          ])
        }
      }
    ]
  }

  detailChart.setOption(option)
}

const viewDeviceDetail = (device: Device) => {
  selectedDevice.value = device
  detailDrawerVisible.value = true
  nextTick(() => {
    initDetailChart()
  })
}

const handleRowClick = (row: Device) => {
  viewDeviceDetail(row)
}

const controlDevice = (device: Device) => {
  ElMessage.info(`Opening control panel for ${device.name}`)
}

const createWorkOrder = (device: Device) => {
  ElMessage.info(`Creating work order for ${device.name}`)
}

const exportDeviceData = (device: Device) => {
  ElMessage.success(`Exporting data for ${device.name} to CSV`)
}

const exportDevices = () => {
  ElMessage.success('Exporting device list to CSV')
}

// ==================== Add Device ====================
const addDialogVisible = ref(false)
const addingDevice = ref(false)
const deviceFormRef = ref()

const newDeviceForm = ref({
  name: '',
  model: '',
  manufacturer: '',
  serialNumber: '',
  systemType: '',
  area: '',
  installationDate: '',
  imageUrl: ''
})

const deviceFormRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  model: [{ required: true, message: 'Please enter device model', trigger: 'blur' }],
  manufacturer: [{ required: true, message: 'Please enter manufacturer', trigger: 'blur' }],
  systemType: [{ required: true, message: 'Please select system type', trigger: 'change' }],
  area: [{ required: true, message: 'Please select area', trigger: 'change' }]
}

const openAddDeviceDialog = () => {
  newDeviceForm.value = {
    name: '',
    model: '',
    manufacturer: '',
    serialNumber: '',
    systemType: '',
    area: '',
    installationDate: '',
    imageUrl: ''
  }
  addDialogVisible.value = true
}

const submitAddDevice = async () => {
  if (!deviceFormRef.value) return

  await deviceFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      addingDevice.value = true
      await new Promise(resolve => setTimeout(resolve, 1000))

      const newId = `dev-${Date.now()}`
      const newDevice: Device = {
        id: newId,
        name: newDeviceForm.value.name,
        type: 'device',
        status: 'online',
        model: newDeviceForm.value.model,
        manufacturer: newDeviceForm.value.manufacturer,
        serialNumber: newDeviceForm.value.serialNumber || `SN-${Date.now()}`,
        systemType: newDeviceForm.value.systemType,
        area: newDeviceForm.value.area,
        floor: newDeviceForm.value.area.substring(0, 2),
        imageUrl: newDeviceForm.value.imageUrl || 'https://aegisnx.com/wp-content/uploads/2026/05/1779084477643.png',
        metrics: { temperature: 24, humidity: 50, power: 5, energy: 4000, uptime: 0, efficiency: 95 },
        lastMaintenance: new Date().toISOString().split('T')[0],
        nextMaintenance: new Date(Date.now() + 90 * 24 * 3600000).toISOString().split('T')[0],
        installationDate: newDeviceForm.value.installationDate || new Date().toISOString().split('T')[0]
      }

      devices.value.unshift(newDevice)
      addingDevice.value = false
      addDialogVisible.value = false
      ElMessage.success('Device added successfully')
    }
  })
}

// ==================== Detail Metrics ====================
const detailMetrics = computed(() => {
  const device = selectedDevice.value
  if (!device) return []
  const m = device.metrics
  return [
    { key: 'temperature', label: 'Temperature', value: m.temperature, unit: '°C', icon: ColdDrink, warning: m.temperature > 28, max: 50, percentage: (m.temperature / 50) * 100 },
    { key: 'humidity', label: 'Humidity', value: m.humidity, unit: '%', icon: Sunny, warning: m.humidity > 65, max: 100, percentage: m.humidity },
    { key: 'power', label: 'Power', value: m.power, unit: 'kW', icon: Odometer, warning: m.power > 20, max: 200, percentage: (m.power / 200) * 100 },
    { key: 'efficiency', label: 'Efficiency', value: m.efficiency, unit: '%', icon: MagicStick, warning: m.efficiency < 80, max: 100, percentage: m.efficiency }
  ]
})

// ==================== Resize Handler ====================
const handleResize = () => {
  if (detailChart) {
    detailChart.resize()
  }
}

// ==================== Lifecycle ====================
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
    }, 400)
  }, 2000)

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (detailChart) {
    detailChart.dispose()
    detailChart = null
  }
  window.removeEventListener('resize', handleResize)
})

watch(detailDrawerVisible, (visible) => {
  if (!visible && detailChart) {
    detailChart.dispose()
    detailChart = null
  }
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

/* ==================== Main Content ==================== */
.device-inventory {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

/* Header */
.inventory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.header-title .el-icon {
  font-size: 24px;
  color: #3b82f6;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Statistics Cards */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.online .stat-icon { color: #10b981; }
.stat-card.warning .stat-icon { color: #f59e0b; }
.stat-card.error .stat-icon { color: #ef4444; }
.stat-card.offline .stat-icon { color: #6b7280; }

.stat-icon .el-icon {
  font-size: 32px;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  gap: 12px;
}

/* Device Table */
.device-table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.device-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.device-info {
  display: flex;
  flex-direction: column;
}

.device-name {
  font-weight: 600;
  color: #1e293b;
}

.device-model {
  font-size: 11px;
  color: #64748b;
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

.status-dot.status-online { background: #10b981; box-shadow: 0 0 6px rgba(16, 185, 129, 0.5); }
.status-dot.status-warning { background: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.5); }
.status-dot.status-error { background: #ef4444; box-shadow: 0 0 6px rgba(239, 68, 68, 0.5); animation: pulseRed 1s infinite; }
.status-dot.status-offline { background: #6b7280; }

@keyframes pulseRed {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.status-text.status-online { color: #10b981; }
.status-text.status-warning { color: #f59e0b; }
.status-text.status-error { color: #ef4444; }

.text-warning { color: #f59e0b; font-weight: 500; }
.text-danger { color: #ef4444; font-weight: 500; }

/* Table Row Classes */
:deep(.el-table .row-online) { background-color: rgba(16, 185, 129, 0.02); }
:deep(.el-table .row-warning) { background-color: rgba(245, 158, 11, 0.04); }
:deep(.el-table .row-error) { background-color: rgba(239, 68, 68, 0.04); }

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
}

/* Device Detail Drawer */
.device-detail {
  padding: 0 4px;
}

.detail-image {
  text-align: center;
  margin-bottom: 24px;
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
}

.detail-image .el-image {
  max-height: 200px;
  width: auto;
}

.image-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: #94a3b8;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e2e8f0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.metric-card {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
}

.metric-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #e0f2fe, #dbeafe);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  color: #3b82f6;
}

.metric-info {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
}

.metric-unit {
  font-size: 12px;
  color: #64748b;
}

.metric-label {
  font-size: 12px;
  color: #64748b;
  display: block;
  margin-bottom: 8px;
}

.metric-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.metric-fill.fill-warning {
  background: linear-gradient(90deg, #f59e0b, #ef4444);
}

.detail-chart {
  width: 100%;
  height: 280px;
}

.detail-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .filter-bar {
    flex-direction: column;
    gap: 12px;
  }

  .filter-left {
    width: 100%;
    flex-wrap: wrap;
  }

  .filter-right {
    width: 100%;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .inventory-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .device-table-container {
    overflow-x: auto;
  }

  .detail-chart {
    height: 220px;
  }
}
</style>