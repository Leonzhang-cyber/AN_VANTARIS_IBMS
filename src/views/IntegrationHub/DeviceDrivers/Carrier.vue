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
        <div class="loading-tip">Daikin Device Drivers</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="daikin-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Device Drivers</el-breadcrumb-item>
            <el-breadcrumb-item>Daikin</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Daikin Device Drivers</h1>
        <p class="description">Manage Daikin HVAC systems, VRV/VRF units, air conditioners, and building climate control</p>
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

    <!-- Daikin Devices Table -->
    <el-card class="devices-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Daikin HVAC Devices</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="typeFilter" placeholder="Device Type" clearable style="width: 150px">
              <el-option label="VRV Outdoor Unit" value="VRV Outdoor" />
              <el-option label="VRV Indoor Unit" value="VRV Indoor" />
              <el-option label="SkyAir" value="SkyAir" />
              <el-option label="Split AC" value="Split AC" />
              <el-option label="Air Handling Unit" value="AHU" />
              <el-option label="Heat Pump" value="Heat Pump" />
              <el-option label="Chiller" value="Chiller" />
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
        <el-table-column prop="deviceType" label="Type" width="140">
          <template #default="{ row }">
            <el-tag :type="getDeviceTypeTag(row.deviceType)" size="small">{{ row.deviceType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="Model" width="120" />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="refrigerant" label="Refrigerant" width="100" />
        <el-table-column prop="pointCount" label="Points" width="80" align="center" />
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
            <el-button link type="primary" size="small" @click="viewPoints(row)">Points ({{ row.pointCount }})</el-button>
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

    <!-- Points Section -->
    <el-card class="points-card" shadow="hover" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>HVAC Points - {{ selectedDevice.name }}</span>
          <div class="point-actions">
            <el-button size="small" type="primary" @click="openAddPointDialog">
              <el-icon><Plus /></el-icon> Add Point
            </el-button>
            <el-button size="small" @click="refreshPoints">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button size="small" type="success" @click="readAllPoints">
              <el-icon><Connection /></el-icon> Read All
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="points" stripe size="small" v-loading="pointsLoading">
        <el-table-column prop="address" label="Address" width="120" />
        <el-table-column prop="name" label="Point Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="pointType" label="Point Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getPointTypeTag(row.pointType)" size="small">{{ row.pointType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dataType" label="Data Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="currentValue" label="Current Value" width="150">
          <template #default="{ row }">
            <span class="point-value">{{ formatValue(row.currentValue, row.dataType) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="range" label="Range" width="100" />
        <el-table-column prop="description" label="Description" min-width="150" show-overflow-tooltip />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="readPoint(row)">Read</el-button>
            <el-button v-if="isWritable(row.pointType)" link type="success" size="small" @click="openWriteDialog(row)">Write</el-button>
            <el-button link type="danger" size="small" @click="deletePoint(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="points-footer" v-if="selectedDevice">
        <el-button type="primary" @click="syncAllPoints">Sync All Points</el-button>
        <span class="points-info">Total Points: {{ points.length }} | Monitored: {{ activePointsCount }}</span>
      </div>
    </el-card>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="deviceDialogVisible" :title="dialogMode === 'add' ? 'Add Daikin Device' : 'Edit Daikin Device'" width="650px" destroy-on-close class="device-dialog">
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
                    <el-option label="VRV Outdoor Unit" value="VRV Outdoor" />
                    <el-option label="VRV Indoor Unit" value="VRV Indoor" />
                    <el-option label="SkyAir" value="SkyAir" />
                    <el-option label="Split AC" value="Split AC" />
                    <el-option label="Air Handling Unit" value="AHU" />
                    <el-option label="Heat Pump" value="Heat Pump" />
                    <el-option label="Chiller" value="Chiller" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Model" prop="model">
                  <el-select v-model="deviceForm.model" style="width: 100%">
                    <el-option label="VRV IV" value="VRV IV" />
                    <el-option label="VRV IV X" value="VRV IV X" />
                    <el-option label="VRV 5" value="VRV 5" />
                    <el-option label="SkyAir FTQ" value="SkyAir FTQ" />
                    <el-option label="SkyAir RZQ" value="SkyAir RZQ" />
                    <el-option label="Split FTX" value="Split FTX" />
                    <el-option label="Split CTX" value="Split CTX" />
                    <el-option label="AHU EWAQ" value="AHU EWAQ" />
                    <el-option label="Heat Pump RXS" value="Heat Pump RXS" />
                    <el-option label="Chiller EWYD" value="Chiller EWYD" />
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
                    <el-option label="BACnet IP" value="BACnet IP" />
                    <el-option label="Modbus TCP" value="Modbus TCP" />
                    <el-option label="Daikin DIII-NET" value="DIII-NET" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Refrigerant" prop="refrigerant">
                  <el-select v-model="deviceForm.refrigerant" style="width: 100%">
                    <el-option label="R410A" value="R410A" />
                    <el-option label="R32" value="R32" />
                    <el-option label="R134a" value="R134a" />
                    <el-option label="R407C" value="R407C" />
                  </el-select>
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

    <!-- Add/Edit Point Dialog -->
    <el-dialog v-model="pointDialogVisible" :title="dialogMode === 'add' ? 'Add HVAC Point' : 'Edit HVAC Point'" width="580px" destroy-on-close>
      <el-form :model="pointForm" :rules="pointRules" ref="pointFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Address" prop="address">
              <el-input v-model="pointForm.address" placeholder="e.g., AI-1, 40001" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Point Name" prop="name">
              <el-input v-model="pointForm.name" placeholder="Enter point name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Point Type" prop="pointType">
              <el-select v-model="pointForm.pointType" style="width: 100%">
                <el-option label="Temperature" value="Temperature" />
                <el-option label="Humidity" value="Humidity" />
                <el-option label="Pressure" value="Pressure" />
                <el-option label="Fan Speed" value="Fan Speed" />
                <el-option label="Valve Position" value="Valve Position" />
                <el-option label="Setpoint" value="Setpoint" />
                <el-option label="Status" value="Status" />
                <el-option label="Alarm" value="Alarm" />
                <el-option label="Energy" value="Energy" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Data Type" prop="dataType">
              <el-select v-model="pointForm.dataType" style="width: 100%">
                <el-option label="Float" value="Float" />
                <el-option label="Integer" value="Integer" />
                <el-option label="Boolean" value="Boolean" />
                <el-option label="String" value="String" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Unit" prop="unit">
              <el-input v-model="pointForm.unit" placeholder="°C, %, kPa, rpm" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Scale Factor" prop="scaleFactor">
              <el-input-number v-model="pointForm.scaleFactor" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Min Range" prop="minRange">
              <el-input-number v-model="pointForm.minRange" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Max Range" prop="maxRange">
              <el-input-number v-model="pointForm.maxRange" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="pointForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="pointDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePoint">Save</el-button>
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
        <el-form-item label="Point Type">
          <el-tag :type="getPointTypeTag(writeTarget?.pointType)" size="small">{{ writeTarget?.pointType }}</el-tag>
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
const loadingMessages = ['Preparing...', 'Initializing Daikin drivers...', 'Loading devices...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const pointsLoading = ref(false)
const testing = ref(false)
const deviceDialogVisible = ref(false)
const pointDialogVisible = ref(false)
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
const pointFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'HVAC Devices', value: '28', trend: 6, icon: 'Cpu', bgColor: '#409eff', key: 'devices', subTitle: 'Online: 26' },
  { title: 'Monitoring Points', value: '456', trend: 18, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'points', subTitle: 'Active: 438' },
  { title: 'Energy Savings', value: '12.5%', trend: -2, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'energy', subTitle: 'vs baseline' },
  { title: 'Alerts', value: '3', trend: -1, icon: 'Warning', bgColor: '#f56c6c', key: 'alerts', subTitle: 'Active: 1' }
])

const devices = ref([
  { id: 1, name: 'VRV_Outdoor_1', deviceType: 'VRV Outdoor', model: 'VRV IV', ipAddress: '192.168.1.100', port: 47808, protocol: 'BACnet IP', refrigerant: 'R410A', pointCount: 56, status: 'Online', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'VRV_Indoor_Zone_A', deviceType: 'VRV Indoor', model: 'VRV IV', ipAddress: '192.168.1.101', port: 47808, protocol: 'BACnet IP', refrigerant: 'R410A', pointCount: 24, status: 'Online', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'SkyAir_FTQ_Lobby', deviceType: 'SkyAir', model: 'SkyAir FTQ', ipAddress: '192.168.1.102', port: 47808, protocol: 'BACnet IP', refrigerant: 'R32', pointCount: 32, status: 'Online', lastSeen: '2024-01-20 10:32:00' },
  { id: 4, name: 'Split_AC_Office_1', deviceType: 'Split AC', model: 'Split FTX', ipAddress: '192.168.1.103', port: 502, protocol: 'Modbus TCP', refrigerant: 'R32', pointCount: 18, status: 'Warning', lastSeen: '2024-01-20 10:25:00' },
  { id: 5, name: 'AHU_Building_A', deviceType: 'AHU', model: 'AHU EWAQ', ipAddress: '192.168.1.104', port: 47808, protocol: 'BACnet IP', refrigerant: 'R134a', pointCount: 45, status: 'Online', lastSeen: '2024-01-20 10:29:00' },
  { id: 6, name: 'Heat_Pump_Pool', deviceType: 'Heat Pump', model: 'Heat Pump RXS', ipAddress: '192.168.1.105', port: 502, protocol: 'Modbus TCP', refrigerant: 'R410A', pointCount: 28, status: 'Online', lastSeen: '2024-01-20 10:31:00' }
])

const pointsMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, address: 'AI-1', name: 'Outdoor Temperature', pointType: 'Temperature', dataType: 'Float', unit: '°C', currentValue: 22.5, range: '-20-50', scaleFactor: 1, minRange: -20, maxRange: 50, description: 'Ambient outdoor temperature' },
    { id: 2, address: 'AI-2', name: 'Suction Pressure', pointType: 'Pressure', dataType: 'Float', unit: 'kPa', currentValue: 850, range: '0-2000', scaleFactor: 1, minRange: 0, maxRange: 2000, description: 'Compressor suction pressure' },
    { id: 3, address: 'AI-3', name: 'Discharge Pressure', pointType: 'Pressure', dataType: 'Float', unit: 'kPa', currentValue: 2650, range: '0-4000', scaleFactor: 1, minRange: 0, maxRange: 4000, description: 'Compressor discharge pressure' },
    { id: 4, address: 'AO-1', name: 'Compressor Speed', pointType: 'Setpoint', dataType: 'Float', unit: '%', currentValue: 65, range: '0-100', scaleFactor: 1, minRange: 0, maxRange: 100, description: 'Compressor speed setpoint' },
    { id: 5, address: 'BI-1', name: 'Compressor Status', pointType: 'Status', dataType: 'Boolean', unit: '', currentValue: true, range: '0/1', scaleFactor: 1, description: 'Compressor running status' }
  ],
  2: [
    { id: 6, address: 'AI-1', name: 'Room Temperature', pointType: 'Temperature', dataType: 'Float', unit: '°C', currentValue: 23.0, range: '10-30', scaleFactor: 1, minRange: 10, maxRange: 30, description: 'Zone temperature' },
    { id: 7, address: 'AI-2', name: 'Setpoint', pointType: 'Setpoint', dataType: 'Float', unit: '°C', currentValue: 22.0, range: '18-28', scaleFactor: 1, minRange: 18, maxRange: 28, description: 'Temperature setpoint' },
    { id: 8, address: 'BI-1', name: 'Fan Status', pointType: 'Status', dataType: 'Boolean', unit: '', currentValue: true, range: '0/1', scaleFactor: 1, description: 'Indoor fan status' }
  ],
  3: [
    { id: 9, address: 'AI-1', name: 'Supply Air Temp', pointType: 'Temperature', dataType: 'Float', unit: '°C', currentValue: 18.5, range: '10-25', scaleFactor: 1, minRange: 10, maxRange: 25, description: 'Supply air temperature' }
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

const points = computed(() => pointsMap.value[selectedDevice.value?.id] || [])
const activePointsCount = computed(() => points.value.length)

// ==================== Helper Methods ====================
const getDeviceTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'VRV Outdoor': 'primary',
    'VRV Indoor': 'success',
    'SkyAir': 'warning',
    'Split AC': 'info',
    'AHU': 'danger',
    'Heat Pump': 'success',
    'Chiller': 'primary'
  }
  return map[type] || 'info'
}

const getPointTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Temperature': 'danger',
    'Humidity': 'primary',
    'Pressure': 'warning',
    'Fan Speed': 'success',
    'Valve Position': 'info',
    'Setpoint': 'success',
    'Status': 'primary',
    'Alarm': 'danger',
    'Energy': 'success'
  }
  return map[type] || 'info'
}

const getDataTypeTag = (dataType: string) => {
  const map: Record<string, string> = {
    'Float': 'success',
    'Integer': 'primary',
    'Boolean': 'warning',
    'String': 'info'
  }
  return map[dataType] || 'info'
}

const formatValue = (value: any, dataType: string) => {
  if (dataType === 'Boolean') return value ? 'TRUE' : 'FALSE'
  if (dataType === 'Float') return typeof value === 'number' ? value.toFixed(2) : value
  return value
}

const isWritable = (pointType: string) => {
  return pointType === 'Setpoint' || pointType === 'Fan Speed' || pointType === 'Valve Position'
}

const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting Daikin configuration...')
const fetchDevices = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Devices refreshed') }, 500) }

const openAddDeviceDialog = () => {
  dialogMode.value = 'add'
  Object.assign(deviceForm, {
    id: null, name: '', deviceType: 'VRV Outdoor', model: 'VRV IV', ipAddress: '', port: 47808,
    protocol: 'BACnet IP', refrigerant: 'R410A', description: '', timeout: 5000, retryCount: 3,
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
    testResult.message = 'Successfully connected to Daikin device'
    testResult.details = {
      device: deviceForm.ipAddress,
      model: deviceForm.model,
      firmware: 'V2.5',
      responseTime: 38
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
  ElMessageBox.confirm(`Delete device "${device.name}"? This will also remove all points.`, 'Confirm Delete', {
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

const viewPoints = (device: any) => {
  selectedDevice.value = device
  refreshPoints()
}

const refreshPoints = () => {
  pointsLoading.value = true
  setTimeout(() => { pointsLoading.value = false; ElMessage.success('Points refreshed') }, 500)
}

// ==================== Point Methods ====================
const openAddPointDialog = () => {
  dialogMode.value = 'add'
  Object.assign(pointForm, {
    id: null, address: '', name: '', pointType: 'Temperature', dataType: 'Float', unit: '',
    scaleFactor: 1, minRange: 0, maxRange: 100, description: ''
  })
  pointDialogVisible.value = true
}

const editPoint = (point: any) => {
  dialogMode.value = 'edit'
  Object.assign(pointForm, point)
  pointDialogVisible.value = true
}

const savePoint = async () => {
  if (!pointFormRef.value) return
  await pointFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Point added successfully' : 'Point updated successfully')
      pointDialogVisible.value = false
      refreshPoints()
    }
  })
}

const deletePoint = (point: any) => {
  ElMessageBox.confirm(`Delete point "${point.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const pointsList = pointsMap.value[selectedDevice.value.id]
    const index = pointsList.findIndex(p => p.id === point.id)
    if (index !== -1) { pointsList.splice(index, 1); ElMessage.success(`Deleted: ${point.name}`) }
  }).catch(() => {})
}

const readPoint = (point: any) => {
  ElMessage.info(`Reading ${point.name}...`)
  setTimeout(() => {
    const newValue = point.dataType === 'Float' ? (Math.random() * 50 + 15).toFixed(2) :
        point.dataType === 'Boolean' ? Math.random() > 0.5 :
            Math.floor(Math.random() * 100)
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

const readAllPoints = () => {
  ElMessage.info('Reading all points...')
  setTimeout(() => {
    points.value.forEach(point => {
      point.currentValue = point.dataType === 'Float' ? (Math.random() * 50 + 15).toFixed(2) :
          point.dataType === 'Boolean' ? Math.random() > 0.5 :
              Math.floor(Math.random() * 100)
    })
    ElMessage.success('All points updated')
    refreshPoints()
  }, 1000)
}

const syncAllPoints = () => {
  ElMessage.info('Synchronizing all points...')
  setTimeout(() => { ElMessage.success('Sync completed'); refreshPoints() }, 2000)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Forms ====================
const deviceForm = reactive({
  id: null, name: '', deviceType: 'VRV Outdoor', model: 'VRV IV', ipAddress: '', port: 47808,
  protocol: 'BACnet IP', refrigerant: 'R410A', description: '', timeout: 5000, retryCount: 3,
  autoReconnect: true, pollingEnabled: true, pollingInterval: 1000, enableLogging: true
})

const pointForm = reactive({
  id: null, address: '', name: '', pointType: 'Temperature', dataType: 'Float', unit: '',
  scaleFactor: 1, minRange: 0, maxRange: 100, description: ''
})

const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }]
}

const pointRules = {
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

.daikin-page {
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

.devices-card, .points-card { margin-bottom: 20px; }
.devices-card .card-header, .points-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.devices-card .table-actions, .points-card .point-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.points-footer { margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }

.point-value { font-weight: 500; color: #409eff; }
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