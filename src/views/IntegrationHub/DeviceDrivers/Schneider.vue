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
        <div class="loading-tip">Schneider Device Drivers</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="schneider-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Device Drivers</el-breadcrumb-item>
            <el-breadcrumb-item>Schneider</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Schneider Device Drivers</h1>
        <p class="description">Manage Schneider Electric PLC connections, data points, and industrial automation</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Config
        </el-button>
        <el-button type="primary" @click="openAddDeviceDialog">
          <el-icon><Plus /></el-icon>
          Add Device
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

    <!-- Schneider Devices Table -->
    <el-card class="devices-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Schneider PLC Devices</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="modelFilter" placeholder="Model" clearable style="width: 150px">
              <el-option label="M340" value="M340" />
              <el-option label="M580" value="M580" />
              <el-option label="M221" value="M221" />
              <el-option label="M241" value="M241" />
              <el-option label="M251" value="M251" />
              <el-option label="Quantum" value="Quantum" />
              <el-option label="Premium" value="Premium" />
            </el-select>
            <el-select v-model="protocolFilter" placeholder="Protocol" clearable style="width: 130px">
              <el-option label="Modbus TCP" value="Modbus TCP" />
              <el-option label="Modbus RTU" value="Modbus RTU" />
              <el-option label="Ethernet/IP" value="Ethernet/IP" />
              <el-option label="Profibus" value="Profibus" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Online" value="Online" />
              <el-option label="Offline" value="Offline" />
              <el-option label="Warning" value="Warning" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchDevices" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDevices" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Device Name" min-width="160" show-overflow-tooltip />
        <el-table-column prop="model" label="Model" width="100" />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="protocol" label="Protocol" width="110">
          <template #default="{ row }">
            <el-tag :type="getProtocolTag(row.protocol)" size="small">{{ row.protocol }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dataPointCount" label="Data Points" width="110" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : row.status === 'Warning' ? 'warning' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Online' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastSeen" label="Last Seen" width="150" />
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDataPoints(row)">Data Points ({{ row.dataPointCount }})</el-button>
            <el-button link type="success" size="small" @click="editDevice(row)">Edit</el-button>
            <el-button link type="info" size="small" @click="testConnection(row)">Test</el-button>
            <el-button link type="danger" size="small" @click="deleteDevice(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredDevices.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Data Points Section -->
    <el-card class="datapoints-card" shadow="hover" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>Data Points - {{ selectedDevice.name }}</span>
          <div class="dp-actions">
            <el-button size="small" type="primary" @click="openAddDataPointDialog">
              <el-icon><Plus /></el-icon> Add Data Point
            </el-button>
            <el-button size="small" @click="refreshDataPoints">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button size="small" type="success" @click="readAllDataPoints">
              <el-icon><Connection /></el-icon> Read All
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="dataPoints" stripe size="small" v-loading="dpLoading">
        <el-table-column prop="address" label="Address" width="140" />
        <el-table-column prop="name" label="Point Name" min-width="160" show-overflow-tooltip />
        <el-table-column prop="dataType" label="Data Type" width="110">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="currentValue" label="Current Value" width="150">
          <template #default="{ row }">
            <span class="dp-value">{{ formatValue(row.currentValue, row.dataType) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="150" show-overflow-tooltip />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="readDataPoint(row)">Read</el-button>
            <el-button v-if="isWritable(row.dataType)" link type="success" size="small" @click="openWriteDialog(row)">Write</el-button>
            <el-button link type="danger" size="small" @click="deleteDataPoint(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="dp-footer" v-if="selectedDevice">
        <el-button type="primary" @click="syncAllDataPoints">Sync All Points</el-button>
        <span class="dp-info">Total Points: {{ dataPoints.length }} | Active: {{ activeDataPointsCount }}</span>
      </div>
    </el-card>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="deviceDialogVisible" :title="dialogMode === 'add' ? 'Add Schneider Device' : 'Edit Schneider Device'" width="650px" destroy-on-close class="device-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Connection Settings" name="basic">
          <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="140px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Device Name" prop="name">
                  <el-input v-model="deviceForm.name" placeholder="Enter device name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Model" prop="model">
                  <el-select v-model="deviceForm.model" style="width: 100%">
                    <el-option label="Modicon M340" value="M340" />
                    <el-option label="Modicon M580" value="M580" />
                    <el-option label="Modicon M221" value="M221" />
                    <el-option label="Modicon M241" value="M241" />
                    <el-option label="Modicon M251" value="M251" />
                    <el-option label="Quantum" value="Quantum" />
                    <el-option label="Premium" value="Premium" />
                    <el-option label="Twido" value="Twido" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="IP Address" prop="ipAddress">
                  <el-input v-model="deviceForm.ipAddress" placeholder="192.168.1.100" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Port" prop="port">
                  <el-input-number v-model="deviceForm.port" :min="1" :max="65535" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Protocol" prop="protocol">
                  <el-select v-model="deviceForm.protocol" style="width: 100%">
                    <el-option label="Modbus TCP" value="Modbus TCP" />
                    <el-option label="Modbus RTU" value="Modbus RTU" />
                    <el-option label="Ethernet/IP" value="Ethernet/IP" />
                    <el-option label="Profibus DP" value="Profibus DP" />
                    <el-option label="CANopen" value="CANopen" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Unit ID" prop="unitId">
                  <el-input-number v-model="deviceForm.unitId" :min="0" :max="255" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="Description" prop="description">
              <el-input v-model="deviceForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="150px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Connection Timeout (ms)">
                  <el-input-number v-model="deviceForm.timeout" :min="100" :max="30000" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Retry Count">
                  <el-input-number v-model="deviceForm.retryCount" :min="0" :max="10" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Auto Reconnect">
                  <el-switch v-model="deviceForm.autoReconnect" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Polling Enabled">
                  <el-switch v-model="deviceForm.pollingEnabled" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Polling Interval (ms)">
                  <el-input-number v-model="deviceForm.pollingInterval" :min="100" :max="60000" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Enable Logging">
                  <el-switch v-model="deviceForm.enableLogging" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="deviceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testDeviceConnection" :loading="testing">
          Test Connection
        </el-button>
        <el-button type="success" @click="saveDevice">
          Save Device
        </el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Data Point Dialog -->
    <el-dialog v-model="dataPointDialogVisible" :title="dialogMode === 'add' ? 'Add Data Point' : 'Edit Data Point'" width="600px" destroy-on-close>
      <el-form :model="dataPointForm" :rules="dataPointRules" ref="dataPointFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Address" prop="address">
              <el-input v-model="dataPointForm.address" placeholder="e.g., 40001, %MW0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Point Name" prop="name">
              <el-input v-model="dataPointForm.name" placeholder="Enter point name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Data Type" prop="dataType">
              <el-select v-model="dataPointForm.dataType" style="width: 100%">
                <el-option label="Bool" value="Bool" />
                <el-option label="Byte" value="Byte" />
                <el-option label="Word" value="Word" />
                <el-option label="DWord" value="DWord" />
                <el-option label="Int" value="Int" />
                <el-option label="DInt" value="DInt" />
                <el-option label="Real" value="Real" />
                <el-option label="String" value="String" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Unit" prop="unit">
              <el-input v-model="dataPointForm.unit" placeholder="°C, bar, %, etc." />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Scale Factor" prop="scaleFactor">
              <el-input-number v-model="dataPointForm.scaleFactor" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Offset" prop="offset">
              <el-input-number v-model="dataPointForm.offset" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="dataPointForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dataPointDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveDataPoint">Save</el-button>
      </template>
    </el-dialog>

    <!-- Write Value Dialog -->
    <el-dialog v-model="writeDialogVisible" title="Write Value" width="450px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="Point Name">
          <span class="write-point">{{ writeTarget?.name }}</span>
        </el-form-item>
        <el-form-item label="Address">
          <span class="write-address">{{ writeTarget?.address }}</span>
        </el-form-item>
        <el-form-item label="Current Value">
          <span class="write-current">{{ writeTarget?.currentValue }} {{ writeTarget?.unit || '' }}</span>
        </el-form-item>
        <el-form-item label="Data Type">
          <el-tag :type="getDataTypeTag(writeTarget?.dataType)" size="small">{{ writeTarget?.dataType }}</el-tag>
        </el-form-item>
        <el-form-item label="New Value">
          <el-input v-model="writeValue" placeholder="Enter new value" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="writeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitWrite">Write</el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Device Connected' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Device:</strong> {{ testResult.details.device }}</p>
          <p><strong>Model:</strong> {{ testResult.details.model }}</p>
          <p><strong>Firmware:</strong> {{ testResult.details.firmware }}</p>
          <p><strong>Response Time:</strong> {{ testResult.details.responseTime }}ms</p>
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
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download,
  Delete, Connection, Edit, Cpu, DataAnalysis
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing Schneider drivers...', 'Loading devices...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const dpLoading = ref(false)
const testing = ref(false)
const deviceDialogVisible = ref(false)
const dataPointDialogVisible = ref(false)
const testDialogVisible = ref(false)
const writeDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedDevice = ref<any>(null)
const writeTarget = ref<any>(null)
const searchKeyword = ref('')
const modelFilter = ref('')
const protocolFilter = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const writeValue = ref('')

const deviceFormRef = ref()
const dataPointFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Schneider Devices', value: '12', trend: 3, icon: 'Cpu', bgColor: '#409eff', key: 'devices', subTitle: 'Online: 10' },
  { title: 'Data Points', value: '345', trend: 8, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'points', subTitle: 'Active: 328' },
  { title: 'Read Rate', value: '1.2K/s', trend: 5, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'rate', subTitle: 'Peak: 1.8K/s' },
  { title: 'Alarms', value: '8', trend: -2, icon: 'Warning', bgColor: '#f56c6c', key: 'alarms', subTitle: 'Active: 3' }
])

const devices = ref([
  { id: 1, name: 'PLC_Production_Line', model: 'M580', ipAddress: '192.168.1.100', port: 502, protocol: 'Modbus TCP', unitId: 1, dataPointCount: 86, status: 'Online', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'PLC_Packaging', model: 'M241', ipAddress: '192.168.1.101', port: 502, protocol: 'Modbus TCP', unitId: 1, dataPointCount: 45, status: 'Online', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'PLC_HVAC', model: 'M340', ipAddress: '192.168.1.102', port: 502, protocol: 'Modbus TCP', unitId: 2, dataPointCount: 67, status: 'Online', lastSeen: '2024-01-20 10:32:00' },
  { id: 4, name: 'PLC_Energy_Monitor', model: 'M221', ipAddress: '192.168.1.103', port: 502, protocol: 'Modbus TCP', unitId: 1, dataPointCount: 32, status: 'Warning', lastSeen: '2024-01-20 10:25:00' },
  { id: 5, name: 'PLC_Assembly_Line', model: 'Quantum', ipAddress: '192.168.1.104', port: 502, protocol: 'Ethernet/IP', unitId: 1, dataPointCount: 115, status: 'Online', lastSeen: '2024-01-20 10:29:00' }
])

const dataPointsMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, address: '40001', name: 'Temperature', dataType: 'Real', unit: '°C', currentValue: 22.5, scaleFactor: 1, offset: 0, description: 'Process temperature' },
    { id: 2, address: '40003', name: 'Pressure', dataType: 'Real', unit: 'bar', currentValue: 5.2, scaleFactor: 1, offset: 0, description: 'Line pressure' },
    { id: 3, address: '40005', name: 'Speed', dataType: 'Int', unit: 'rpm', currentValue: 1450, scaleFactor: 1, offset: 0, description: 'Motor speed' },
    { id: 4, address: '10001', name: 'MotorStatus', dataType: 'Bool', unit: '', currentValue: true, scaleFactor: 1, offset: 0, description: 'Motor running' }
  ],
  2: [
    { id: 5, address: '40001', name: 'PackagingCount', dataType: 'DInt', unit: 'pcs', currentValue: 12450, scaleFactor: 1, offset: 0, description: 'Daily production' }
  ]
})

// ==================== Computed ====================
const filteredDevices = computed(() => {
  let filtered = [...devices.value]
  if (searchKeyword.value) filtered = filtered.filter(d => d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || d.ipAddress.includes(searchKeyword.value))
  if (modelFilter.value) filtered = filtered.filter(d => d.model === modelFilter.value)
  if (protocolFilter.value) filtered = filtered.filter(d => d.protocol === protocolFilter.value)
  if (statusFilter.value) filtered = filtered.filter(d => d.status === statusFilter.value)
  return filtered
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

const dataPoints = computed(() => dataPointsMap.value[selectedDevice.value?.id] || [])
const activeDataPointsCount = computed(() => dataPoints.value.length)

// ==================== Helper Methods ====================
const getProtocolTag = (protocol: string) => {
  const map: Record<string, string> = {
    'Modbus TCP': 'primary',
    'Modbus RTU': 'success',
    'Ethernet/IP': 'warning',
    'Profibus DP': 'danger',
    'CANopen': 'info'
  }
  return map[protocol] || 'info'
}

const getDataTypeTag = (dataType: string) => {
  const map: Record<string, string> = {
    'Bool': 'warning',
    'Int': 'primary',
    'DInt': 'primary',
    'Real': 'success',
    'String': 'info'
  }
  return map[dataType] || 'info'
}

const formatValue = (value: any, dataType: string) => {
  if (dataType === 'Bool') return value ? 'TRUE' : 'FALSE'
  if (dataType === 'Real') return typeof value === 'number' ? value.toFixed(2) : value
  return value
}

const isWritable = (dataType: string) => {
  return dataType !== 'String'
}

const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting Schneider configuration...')
const fetchDevices = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Devices refreshed') }, 500) }

const openAddDeviceDialog = () => {
  dialogMode.value = 'add'
  Object.assign(deviceForm, {
    id: null, name: '', model: 'M340', ipAddress: '', port: 502, protocol: 'Modbus TCP',
    unitId: 1, description: '', timeout: 5000, retryCount: 3, autoReconnect: true,
    pollingEnabled: true, pollingInterval: 1000, enableLogging: true
  })
  deviceDialogVisible.value = true
}

const editDevice = (device: any) => {
  dialogMode.value = 'edit'
  Object.assign(deviceForm, device)
  deviceDialogVisible.value = true
}

const testDeviceConnection = () => {
  testing.value = true
  setTimeout(() => {
    testing.value = false
    testResult.success = true
    testResult.message = 'Successfully connected to Schneider PLC'
    testResult.details = {
      device: deviceForm.ipAddress,
      model: deviceForm.model,
      firmware: 'V2.5',
      responseTime: 32
    }
    testDialogVisible.value = true
  }, 1500)
}

const saveDevice = async () => {
  if (!deviceFormRef.value) return
  await deviceFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Device added successfully' : 'Device updated successfully')
      deviceDialogVisible.value = false
    }
  })
}

const deleteDevice = (device: any) => {
  ElMessageBox.confirm(`Delete device "${device.name}"? This will also remove all data points.`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const index = devices.value.findIndex(d => d.id === device.id)
    if (index !== -1) { devices.value.splice(index, 1); if (selectedDevice.value?.id === device.id) selectedDevice.value = null; ElMessage.success(`Deleted: ${device.name}`) }
  }).catch(() => {})
}

const testConnection = (device: any) => {
  ElMessage.info(`Testing connection to ${device.name}...`)
  setTimeout(() => { ElMessage.success(`${device.name} is ${device.status}`) }, 1000)
}

const viewDataPoints = (device: any) => {
  selectedDevice.value = device
  refreshDataPoints()
}

const refreshDataPoints = () => {
  dpLoading.value = true
  setTimeout(() => { dpLoading.value = false; ElMessage.success('Data points refreshed') }, 500)
}

// ==================== Data Point Methods ====================
const openAddDataPointDialog = () => {
  dialogMode.value = 'add'
  Object.assign(dataPointForm, {
    id: null, address: '', name: '', dataType: 'Real', unit: '',
    scaleFactor: 1, offset: 0, description: ''
  })
  dataPointDialogVisible.value = true
}

const editDataPoint = (point: any) => {
  dialogMode.value = 'edit'
  Object.assign(dataPointForm, point)
  dataPointDialogVisible.value = true
}

const saveDataPoint = async () => {
  if (!dataPointFormRef.value) return
  await dataPointFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Data point added successfully' : 'Data point updated successfully')
      dataPointDialogVisible.value = false
      refreshDataPoints()
    }
  })
}

const deleteDataPoint = (point: any) => {
  ElMessageBox.confirm(`Delete data point "${point.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const points = dataPointsMap.value[selectedDevice.value.id]
    const index = points.findIndex(p => p.id === point.id)
    if (index !== -1) { points.splice(index, 1); ElMessage.success(`Deleted: ${point.name}`) }
  }).catch(() => {})
}

const readDataPoint = (point: any) => {
  ElMessage.info(`Reading ${point.name}...`)
  setTimeout(() => {
    const newValue = point.dataType === 'Real' ? (Math.random() * 100).toFixed(2) : Math.floor(Math.random() * 1000)
    point.currentValue = newValue
    ElMessage.success(`${point.name}: ${formatValue(newValue, point.dataType)} ${point.unit}`)
  }, 300)
}

const openWriteDialog = (point: any) => {
  writeTarget.value = point
  writeValue.value = point.currentValue?.toString() || ''
  writeDialogVisible.value = true
}

const submitWrite = () => {
  if (writeTarget.value) {
    writeTarget.value.currentValue = writeValue.value
    ElMessage.success(`Wrote ${writeValue.value} to ${writeTarget.value.name}`)
    writeDialogVisible.value = false
  }
}

const readAllDataPoints = () => {
  ElMessage.info('Reading all data points...')
  setTimeout(() => {
    dataPoints.value.forEach(point => {
      point.currentValue = point.dataType === 'Real' ? (Math.random() * 100).toFixed(2) : Math.floor(Math.random() * 1000)
    })
    ElMessage.success('All data points updated')
    refreshDataPoints()
  }, 1000)
}

const syncAllDataPoints = () => {
  ElMessage.info('Synchronizing all data points...')
  setTimeout(() => { ElMessage.success('Sync completed'); refreshDataPoints() }, 2000)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Forms ====================
const deviceForm = reactive({
  id: null, name: '', model: 'M340', ipAddress: '', port: 502, protocol: 'Modbus TCP',
  unitId: 1, description: '', timeout: 5000, retryCount: 3, autoReconnect: true,
  pollingEnabled: true, pollingInterval: 1000, enableLogging: true
})

const dataPointForm = reactive({
  id: null, address: '', name: '', dataType: 'Real', unit: '',
  scaleFactor: 1, offset: 0, description: ''
})

const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }]
}

const dataPointRules = {
  address: [{ required: true, message: 'Please enter address', trigger: 'blur' }],
  name: [{ required: true, message: 'Please enter point name', trigger: 'blur' }]
}

// ==================== Mounted ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => { if (messageIndex < loadingMessages.length - 1) messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }, 400)
  const progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(messageInterval); clearInterval(progressInterval); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; fetchDevices() }, 400)
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

.schneider-page {
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

.devices-card, .datapoints-card { margin-bottom: 20px; }
.devices-card .card-header, .datapoints-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.devices-card .table-actions, .datapoints-card .dp-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.dp-footer { margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }

.dp-value { font-weight: 500; color: #409eff; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.device-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.write-point, .write-address, .write-current { font-family: monospace; font-size: 13px; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>