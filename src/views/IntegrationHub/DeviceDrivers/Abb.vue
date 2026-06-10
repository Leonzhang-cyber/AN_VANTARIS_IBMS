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
        <div class="loading-tip">ABB Device Drivers</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="abb-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Device Drivers</el-breadcrumb-item>
            <el-breadcrumb-item>ABB</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>ABB Device Drivers</h1>
        <p class="description">Manage ABB PLCs, drives, and industrial automation devices</p>
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

    <!-- ABB Devices Table -->
    <el-card class="devices-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>ABB Devices</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="typeFilter" placeholder="Device Type" clearable style="width: 140px">
              <el-option label="PLC" value="PLC" />
              <el-option label="Drive" value="Drive" />
              <el-option label="Controller" value="Controller" />
              <el-option label="Robot" value="Robot" />
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
        <el-table-column prop="deviceType" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getDeviceTypeTag(row.deviceType)" size="small">{{ row.deviceType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="Model" width="120" />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="protocol" label="Protocol" width="100" />
        <el-table-column prop="parameterCount" label="Parameters" width="100" align="center" />
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
            <el-button link type="primary" size="small" @click="viewParameters(row)">Parameters ({{ row.parameterCount }})</el-button>
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

    <!-- Parameters Section -->
    <el-card class="parameters-card" shadow="hover" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>Device Parameters - {{ selectedDevice.name }}</span>
          <div class="param-actions">
            <el-button size="small" type="primary" @click="openAddParameterDialog">
              <el-icon><Plus /></el-icon> Add Parameter
            </el-button>
            <el-button size="small" @click="refreshParameters">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button size="small" type="success" @click="readAllParameters">
              <el-icon><Connection /></el-icon> Read All
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="parameters" stripe size="small" v-loading="paramLoading">
        <el-table-column prop="index" label="Index" width="100" />
        <el-table-column prop="subIndex" label="SubIndex" width="80" align="center" />
        <el-table-column prop="name" label="Parameter Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="dataType" label="Data Type" width="110">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="currentValue" label="Current Value" width="150">
          <template #default="{ row }">
            <span class="param-value">{{ formatValue(row.currentValue, row.dataType) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="150" show-overflow-tooltip />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="readParameter(row)">Read</el-button>
            <el-button v-if="isWritable(row.dataType)" link type="success" size="small" @click="openWriteDialog(row)">Write</el-button>
            <el-button link type="danger" size="small" @click="deleteParameter(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="param-footer" v-if="selectedDevice">
        <el-button type="primary" @click="syncAllParameters">Sync All Parameters</el-button>
        <span class="param-info">Total Parameters: {{ parameters.length }} | Active: {{ activeParametersCount }}</span>
      </div>
    </el-card>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="deviceDialogVisible" :title="dialogMode === 'add' ? 'Add ABB Device' : 'Edit ABB Device'" width="650px" destroy-on-close class="device-dialog">
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
                <el-form-item label="Device Type" prop="deviceType">
                  <el-select v-model="deviceForm.deviceType" style="width: 100%">
                    <el-option label="PLC" value="PLC" />
                    <el-option label="Drive" value="Drive" />
                    <el-option label="Controller" value="Controller" />
                    <el-option label="Robot" value="Robot" />
                    <el-option label="IO Module" value="IO Module" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Model" prop="model">
                  <el-select v-model="deviceForm.model" style="width: 100%">
                    <el-option label="AC500" value="AC500" />
                    <el-option label="AC500-eCo" value="AC500-eCo" />
                    <el-option label="AC500-S" value="AC500-S" />
                    <el-option label="AC800M" value="AC800M" />
                    <el-option label="ACS880" value="ACS880" />
                    <el-option label="ACS580" value="ACS580" />
                    <el-option label="ACS380" value="ACS380" />
                    <el-option label="IRB 1200" value="IRB 1200" />
                    <el-option label="IRB 6700" value="IRB 6700" />
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
                    <el-option label="PROFINET" value="PROFINET" />
                    <el-option label="EtherNet/IP" value="EtherNet/IP" />
                    <el-option label="OPC UA" value="OPC UA" />
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

    <!-- Add/Edit Parameter Dialog -->
    <el-dialog v-model="parameterDialogVisible" :title="dialogMode === 'add' ? 'Add Parameter' : 'Edit Parameter'" width="600px" destroy-on-close>
      <el-form :model="parameterForm" :rules="parameterRules" ref="parameterFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Index" prop="index">
              <el-input-number v-model="parameterForm.index" :min="0" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SubIndex" prop="subIndex">
              <el-input-number v-model="parameterForm.subIndex" :min="0" :max="255" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Parameter Name" prop="name">
              <el-input v-model="parameterForm.name" placeholder="Enter parameter name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Data Type" prop="dataType">
              <el-select v-model="parameterForm.dataType" style="width: 100%">
                <el-option label="BOOL" value="BOOL" />
                <el-option label="INT8" value="INT8" />
                <el-option label="UINT8" value="UINT8" />
                <el-option label="INT16" value="INT16" />
                <el-option label="UINT16" value="UINT16" />
                <el-option label="INT32" value="INT32" />
                <el-option label="UINT32" value="UINT32" />
                <el-option label="REAL32" value="REAL32" />
                <el-option label="REAL64" value="REAL64" />
                <el-option label="STRING" value="STRING" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Unit" prop="unit">
              <el-input v-model="parameterForm.unit" placeholder="°C, rpm, kW, Hz, %" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Scale Factor" prop="scaleFactor">
              <el-input-number v-model="parameterForm.scaleFactor" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Min Value" prop="minValue">
              <el-input-number v-model="parameterForm.minValue" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Max Value" prop="maxValue">
              <el-input-number v-model="parameterForm.maxValue" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="parameterForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="parameterDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveParameter">Save</el-button>
      </template>
    </el-dialog>

    <!-- Write Value Dialog -->
    <el-dialog v-model="writeDialogVisible" title="Write Value" width="450px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="Parameter">
          <span class="write-param">{{ writeTarget?.name }}</span>
        </el-form-item>
        <el-form-item label="Index">
          <span class="write-index">{{ writeTarget?.index }}:{{ writeTarget?.subIndex }}</span>
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
const loadingMessages = ['Preparing...', 'Initializing ABB drivers...', 'Loading devices...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const paramLoading = ref(false)
const testing = ref(false)
const deviceDialogVisible = ref(false)
const parameterDialogVisible = ref(false)
const testDialogVisible = ref(false)
const writeDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedDevice = ref<any>(null)
const writeTarget = ref<any>(null)
const searchKeyword = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const writeValue = ref('')

const deviceFormRef = ref()
const parameterFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'ABB Devices', value: '8', trend: 2, icon: 'Cpu', bgColor: '#409eff', key: 'devices', subTitle: 'Online: 7' },
  { title: 'Parameters', value: '186', trend: 12, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'params', subTitle: 'Active: 178' },
  { title: 'Scan Rate', value: '856/s', trend: 5, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'rate', subTitle: 'Peak: 1.2K/s' },
  { title: 'Drive Status', value: 'OK', trend: 0, icon: 'Checked', bgColor: '#f56c6c', key: 'status', subTitle: 'All drives normal' }
])

const devices = ref([
  { id: 1, name: 'Main_PLC_AC500', deviceType: 'PLC', model: 'AC500', ipAddress: '192.168.1.100', port: 502, protocol: 'Modbus TCP', unitId: 1, parameterCount: 56, status: 'Online', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'Conveyor_Drive_ACS880', deviceType: 'Drive', model: 'ACS880', ipAddress: '192.168.1.101', port: 502, protocol: 'Modbus TCP', unitId: 2, parameterCount: 32, status: 'Online', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'Robot_IRB1200', deviceType: 'Robot', model: 'IRB 1200', ipAddress: '192.168.1.102', port: 502, protocol: 'PROFINET', unitId: 1, parameterCount: 48, status: 'Online', lastSeen: '2024-01-20 10:32:00' },
  { id: 4, name: 'Pump_Drive_ACS580', deviceType: 'Drive', model: 'ACS580', ipAddress: '192.168.1.103', port: 502, protocol: 'Modbus TCP', unitId: 3, parameterCount: 24, status: 'Warning', lastSeen: '2024-01-20 10:25:00' },
  { id: 5, name: 'Safety_Controller_AC500S', deviceType: 'Controller', model: 'AC500-S', ipAddress: '192.168.1.104', port: 502, protocol: 'PROFINET', unitId: 1, parameterCount: 26, status: 'Online', lastSeen: '2024-01-20 10:29:00' }
])

const parametersMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, index: 2001, subIndex: 1, name: 'Speed', dataType: 'REAL32', unit: 'rpm', currentValue: 1450, scaleFactor: 1, minValue: 0, maxValue: 3000, description: 'Motor speed' },
    { id: 2, index: 2002, subIndex: 1, name: 'Current', dataType: 'REAL32', unit: 'A', currentValue: 12.5, scaleFactor: 1, minValue: 0, maxValue: 100, description: 'Motor current' },
    { id: 3, index: 2003, subIndex: 1, name: 'Voltage', dataType: 'REAL32', unit: 'V', currentValue: 380, scaleFactor: 1, minValue: 0, maxValue: 500, description: 'Input voltage' },
    { id: 4, index: 3001, subIndex: 1, name: 'Temperature', dataType: 'REAL32', unit: '°C', currentValue: 45.2, scaleFactor: 1, minValue: -10, maxValue: 100, description: 'Device temperature' }
  ],
  2: [
    { id: 5, index: 101, subIndex: 1, name: 'Frequency Reference', dataType: 'REAL32', unit: 'Hz', currentValue: 50.0, scaleFactor: 1, minValue: 0, maxValue: 120, description: 'Drive frequency setpoint' },
    { id: 6, index: 102, subIndex: 1, name: 'Actual Frequency', dataType: 'REAL32', unit: 'Hz', currentValue: 49.8, scaleFactor: 1, minValue: 0, maxValue: 120, description: 'Actual output frequency' }
  ]
})

// ==================== Computed ====================
const filteredDevices = computed(() => {
  let filtered = [...devices.value]
  if (searchKeyword.value) filtered = filtered.filter(d => d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || d.ipAddress.includes(searchKeyword.value))
  if (typeFilter.value) filtered = filtered.filter(d => d.deviceType === typeFilter.value)
  if (statusFilter.value) filtered = filtered.filter(d => d.status === statusFilter.value)
  return filtered
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

const parameters = computed(() => parametersMap.value[selectedDevice.value?.id] || [])
const activeParametersCount = computed(() => parameters.value.length)

// ==================== Helper Methods ====================
const getDeviceTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'PLC': 'primary',
    'Drive': 'success',
    'Controller': 'warning',
    'Robot': 'danger',
    'IO Module': 'info'
  }
  return map[type] || 'info'
}

const getDataTypeTag = (dataType: string) => {
  const map: Record<string, string> = {
    'BOOL': 'warning',
    'INT16': 'primary',
    'INT32': 'primary',
    'REAL32': 'success',
    'REAL64': 'success',
    'STRING': 'info'
  }
  return map[dataType] || 'info'
}

const formatValue = (value: any, dataType: string) => {
  if (dataType === 'BOOL') return value ? 'TRUE' : 'FALSE'
  if (dataType === 'REAL32' || dataType === 'REAL64') return typeof value === 'number' ? value.toFixed(2) : value
  return value
}

const isWritable = (dataType: string) => {
  return dataType !== 'STRING'
}

const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting ABB configuration...')
const fetchDevices = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Devices refreshed') }, 500) }

const openAddDeviceDialog = () => {
  dialogMode.value = 'add'
  Object.assign(deviceForm, {
    id: null, name: '', deviceType: 'PLC', model: 'AC500', ipAddress: '', port: 502,
    protocol: 'Modbus TCP', unitId: 1, description: '', timeout: 5000, retryCount: 3,
    autoReconnect: true, pollingEnabled: true, pollingInterval: 1000, enableLogging: true
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
    testResult.message = 'Successfully connected to ABB device'
    testResult.details = {
      device: deviceForm.ipAddress,
      model: deviceForm.model,
      firmware: 'V2.1',
      responseTime: 28
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
  ElMessageBox.confirm(`Delete device "${device.name}"? This will also remove all parameters.`, 'Confirm Delete', {
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

const viewParameters = (device: any) => {
  selectedDevice.value = device
  refreshParameters()
}

const refreshParameters = () => {
  paramLoading.value = true
  setTimeout(() => { paramLoading.value = false; ElMessage.success('Parameters refreshed') }, 500)
}

// ==================== Parameter Methods ====================
const openAddParameterDialog = () => {
  dialogMode.value = 'add'
  Object.assign(parameterForm, {
    id: null, index: 2001, subIndex: 1, name: '', dataType: 'REAL32', unit: '',
    scaleFactor: 1, minValue: 0, maxValue: 100, description: ''
  })
  parameterDialogVisible.value = true
}

const editParameter = (param: any) => {
  dialogMode.value = 'edit'
  Object.assign(parameterForm, param)
  parameterDialogVisible.value = true
}

const saveParameter = async () => {
  if (!parameterFormRef.value) return
  await parameterFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Parameter added successfully' : 'Parameter updated successfully')
      parameterDialogVisible.value = false
      refreshParameters()
    }
  })
}

const deleteParameter = (param: any) => {
  ElMessageBox.confirm(`Delete parameter "${param.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const params = parametersMap.value[selectedDevice.value.id]
    const index = params.findIndex(p => p.id === param.id)
    if (index !== -1) { params.splice(index, 1); ElMessage.success(`Deleted: ${param.name}`) }
  }).catch(() => {})
}

const readParameter = (param: any) => {
  ElMessage.info(`Reading ${param.name}...`)
  setTimeout(() => {
    const newValue = param.dataType === 'REAL32' ? (Math.random() * 100).toFixed(2) : Math.floor(Math.random() * 1000)
    param.currentValue = newValue
    ElMessage.success(`${param.name}: ${formatValue(newValue, param.dataType)} ${param.unit}`)
  }, 300)
}

const openWriteDialog = (param: any) => {
  writeTarget.value = param
  writeValue.value = param.currentValue?.toString() || ''
  writeDialogVisible.value = true
}

const submitWrite = () => {
  if (writeTarget.value) {
    writeTarget.value.currentValue = writeValue.value
    ElMessage.success(`Wrote ${writeValue.value} to ${writeTarget.value.name}`)
    writeDialogVisible.value = false
  }
}

const readAllParameters = () => {
  ElMessage.info('Reading all parameters...')
  setTimeout(() => {
    parameters.value.forEach(param => {
      param.currentValue = param.dataType === 'REAL32' ? (Math.random() * 100).toFixed(2) : Math.floor(Math.random() * 1000)
    })
    ElMessage.success('All parameters updated')
    refreshParameters()
  }, 1000)
}

const syncAllParameters = () => {
  ElMessage.info('Synchronizing all parameters...')
  setTimeout(() => { ElMessage.success('Sync completed'); refreshParameters() }, 2000)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Forms ====================
const deviceForm = reactive({
  id: null, name: '', deviceType: 'PLC', model: 'AC500', ipAddress: '', port: 502,
  protocol: 'Modbus TCP', unitId: 1, description: '', timeout: 5000, retryCount: 3,
  autoReconnect: true, pollingEnabled: true, pollingInterval: 1000, enableLogging: true
})

const parameterForm = reactive({
  id: null, index: 2001, subIndex: 1, name: '', dataType: 'REAL32', unit: '',
  scaleFactor: 1, minValue: 0, maxValue: 100, description: ''
})

const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }]
}

const parameterRules = {
  name: [{ required: true, message: 'Please enter parameter name', trigger: 'blur' }]
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

.abb-page {
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

.devices-card, .parameters-card { margin-bottom: 20px; }
.devices-card .card-header, .parameters-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.devices-card .table-actions, .parameters-card .param-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.param-footer { margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }

.param-value { font-weight: 500; color: #409eff; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.device-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.write-param, .write-index, .write-current { font-family: monospace; font-size: 13px; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>