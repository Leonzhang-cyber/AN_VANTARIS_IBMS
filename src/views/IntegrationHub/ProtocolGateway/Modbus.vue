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
        <div class="loading-tip">Modbus Gateway Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="modbus-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>Modbus</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Modbus Gateway Management</h1>
        <p class="description">Manage Modbus TCP/RTU gateways, slave devices, and register point mappings</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Config
        </el-button>
        <el-button type="primary" @click="openAddGatewayDialog">
          <el-icon><Plus /></el-icon>
          Add Gateway
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

    <!-- Protocol Type Tabs -->
    <el-card class="tabs-card" shadow="hover">
      <el-tabs v-model="activeProtocol" @tab-click="handleProtocolChange">
        <el-tab-pane name="all">
          <template #label>
            <span><el-icon><Grid /></el-icon> All Gateways ({{ totalGateways }})</span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="modbus_tcp">
          <template #label>
            <span><el-icon><Connection /></el-icon> Modbus TCP ({{ tcpCount }})</span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="modbus_rtu">
          <template #label>
            <span><el-icon><Cpu /></el-icon> Modbus RTU ({{ rtuCount }})</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Gateways Table -->
    <el-card class="gateways-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Modbus Gateways</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Online" value="Online" />
              <el-option label="Offline" value="Offline" />
              <el-option label="Warning" value="Warning" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchGateways" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedGateways" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Gateway Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="protocol" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="row.protocol === 'modbus_tcp' ? 'primary' : 'success'" size="small">
              {{ row.protocol === 'modbus_tcp' ? 'TCP' : 'RTU' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="endpoint" label="Endpoint" min-width="200" show-overflow-tooltip />
        <el-table-column prop="deviceCount" label="Devices" width="80" align="center" />
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
        <el-table-column label="Actions" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDevices(row)">Devices</el-button>
            <el-button link type="success" size="small" @click="editGateway(row)">Edit</el-button>
            <el-button link type="info" size="small" @click="testConnection(row)">Test</el-button>
            <el-button link type="danger" size="small" @click="deleteGateway(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredGateways.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Devices Section -->
    <el-card class="devices-card" shadow="hover" v-if="selectedGateway">
      <template #header>
        <div class="card-header">
          <span>Modbus Devices - {{ selectedGateway.name }}</span>
          <div class="device-actions">
            <el-button size="small" type="primary" @click="openAddDeviceDialog">
              <el-icon><Plus /></el-icon> Add Device
            </el-button>
            <el-button size="small" @click="refreshDevices">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="gatewayDevices" stripe style="width: 100%" v-loading="devicesLoading">
        <el-table-column prop="slaveId" label="Slave ID" width="100" />
        <el-table-column prop="name" label="Device Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
        <el-table-column prop="pointCount" label="Points" width="100" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewPoints(row)">Points</el-button>
            <el-button link type="success" size="small" @click="editDevice(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteDevice(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Points Section -->
    <el-card class="points-card" shadow="hover" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>Register Map - {{ selectedDevice.name }}</span>
          <div class="point-actions">
            <el-button size="small" type="primary" @click="openAddPointDialog">
              <el-icon><Plus /></el-icon> Add Register
            </el-button>
            <el-button size="small" @click="refreshPoints">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button size="small" @click="pollPoints">
              <el-icon><Connection /></el-icon> Poll Now
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="devicePoints" stripe style="width: 100%" v-loading="pointsLoading">
        <el-table-column prop="address" label="Address" width="100" />
        <el-table-column prop="registerType" label="Type" width="130">
          <template #default="{ row }">
            <el-tag :type="getRegisterTypeTag(row.registerType)" size="small">{{ row.registerType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Register Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="dataType" label="Data Type" width="110" />
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="currentValue" label="Current Value" width="120" align="right">
          <template #default="{ row }">
            <span :class="row.currentValue !== null ? 'value-active' : 'value-inactive'">
              {{ row.currentValue !== null ? row.currentValue : '—' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="testPoint(row)">Test</el-button>
            <el-button link type="success" size="small" @click="editPoint(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deletePoint(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="points-footer">
        <el-button type="primary" @click="syncAllPoints">Sync All Registers</el-button>
        <span class="points-info">Total: {{ devicePoints.length }} | Active: {{ activePointsCount }}</span>
      </div>
    </el-card>

    <!-- Add/Edit Gateway Dialog -->
    <el-dialog v-model="gatewayDialogVisible" :title="dialogMode === 'add' ? 'Add Modbus Gateway' : 'Edit Modbus Gateway'" width="650px" destroy-on-close class="gateway-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Basic Configuration" name="basic">
          <el-form :model="gatewayForm" :rules="gatewayRules" ref="gatewayFormRef" label-width="110px">
            <el-form-item label="Gateway Name" prop="name">
              <el-input v-model="gatewayForm.name" placeholder="Enter gateway name" />
            </el-form-item>
            <el-form-item label="Protocol Type" prop="protocol">
              <el-radio-group v-model="gatewayForm.protocol">
                <el-radio value="modbus_tcp">Modbus TCP</el-radio>
                <el-radio value="modbus_rtu">Modbus RTU (Serial)</el-radio>
              </el-radio-group>
            </el-form-item>

            <template v-if="gatewayForm.protocol === 'modbus_tcp'">
              <el-form-item label="Host/IP" prop="host">
                <el-input v-model="gatewayForm.host" placeholder="192.168.1.100" />
              </el-form-item>
              <el-form-item label="Port" prop="port">
                <el-input-number v-model="gatewayForm.port" :min="1" :max="65535" style="width: 100%" />
              </el-form-item>
            </template>

            <template v-else>
              <el-form-item label="Serial Port" prop="serialPort">
                <el-input v-model="gatewayForm.serialPort" placeholder="/dev/ttyUSB0 or COM3" />
              </el-form-item>
              <el-row :gutter="16">
                <el-col :span="12">
                  <el-form-item label="Baud Rate" prop="baudRate">
                    <el-select v-model="gatewayForm.baudRate" style="width: 100%">
                      <el-option label="9600" value="9600" />
                      <el-option label="19200" value="19200" />
                      <el-option label="38400" value="38400" />
                      <el-option label="115200" value="115200" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Parity" prop="parity">
                    <el-select v-model="gatewayForm.parity" style="width: 100%">
                      <el-option label="None" value="none" />
                      <el-option label="Even" value="even" />
                      <el-option label="Odd" value="odd" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Data Bits" prop="dataBits">
                    <el-select v-model="gatewayForm.dataBits" style="width: 100%">
                      <el-option label="8" value="8" />
                      <el-option label="7" value="7" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Stop Bits" prop="stopBits">
                    <el-select v-model="gatewayForm.stopBits" style="width: 100%">
                      <el-option label="1" value="1" />
                      <el-option label="2" value="2" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </template>

            <el-form-item label="Timeout (ms)" prop="timeout">
              <el-input-number v-model="gatewayForm.timeout" :min="100" :max="30000" :step="100" style="width: 100%" />
            </el-form-item>

            <el-form-item label="Description" prop="description">
              <el-input v-model="gatewayForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="130px">
            <el-form-item label="Connection Pool Size">
              <el-input-number v-model="gatewayForm.poolSize" :min="1" :max="50" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Auto Reconnect">
              <el-switch v-model="gatewayForm.autoReconnect" />
            </el-form-item>
            <el-form-item label="Max Retry Attempts">
              <el-input-number v-model="gatewayForm.maxRetries" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Enable Logging">
              <el-switch v-model="gatewayForm.enableLogging" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="gatewayDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testGatewayConnection" :loading="testing">
          Test Connection
        </el-button>
        <el-button type="success" @click="saveGateway">
          Save Gateway
        </el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="deviceDialogVisible" :title="dialogMode === 'add' ? 'Add Modbus Device' : 'Edit Modbus Device'" width="500px" destroy-on-close>
      <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="100px">
        <el-form-item label="Slave ID" prop="slaveId">
          <el-input-number v-model="deviceForm.slaveId" :min="1" :max="247" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Device Name" prop="name">
          <el-input v-model="deviceForm.name" placeholder="Enter device name" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="deviceForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deviceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveDevice">Save</el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Register Dialog -->
    <el-dialog v-model="pointDialogVisible" :title="dialogMode === 'add' ? 'Add Register' : 'Edit Register'" width="580px" destroy-on-close>
      <el-form :model="pointForm" :rules="pointRules" ref="pointFormRef" label-width="120px">
        <el-form-item label="Register Type" prop="registerType">
          <el-select v-model="pointForm.registerType" style="width: 100%">
            <el-option label="Coil (0x) - Read/Write" value="Coil" />
            <el-option label="Discrete Input (1x) - Read Only" value="Discrete Input" />
            <el-option label="Input Register (3x) - Read Only" value="Input Register" />
            <el-option label="Holding Register (4x) - Read/Write" value="Holding Register" />
          </el-select>
        </el-form-item>
        <el-form-item label="Address" prop="address">
          <el-input-number v-model="pointForm.address" :min="0" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Register Name" prop="name">
          <el-input v-model="pointForm.name" placeholder="e.g., Temperature" />
        </el-form-item>
        <el-form-item label="Data Type" prop="dataType">
          <el-select v-model="pointForm.dataType" style="width: 100%">
            <el-option label="16-bit Integer (int16)" value="int16" />
            <el-option label="32-bit Integer (int32)" value="int32" />
            <el-option label="32-bit Float" value="float32" />
            <el-option label="Boolean" value="bool" />
            <el-option label="String" value="string" />
          </el-select>
        </el-form-item>
        <el-form-item label="Byte Order" prop="byteOrder">
          <el-select v-model="pointForm.byteOrder" style="width: 100%">
            <el-option label="Big Endian (ABCD)" value="big" />
            <el-option label="Little Endian (DCBA)" value="little" />
            <el-option label="Big Endian Swap (BADC)" value="big_swap" />
            <el-option label="Little Endian Swap (CDAB)" value="little_swap" />
          </el-select>
        </el-form-item>
        <el-form-item label="Scale Factor" prop="scale">
          <el-input-number v-model="pointForm.scale" :step="0.1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Unit" prop="unit">
          <el-input v-model="pointForm.unit" placeholder="°C, kW, %, etc." />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="pointForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pointDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePoint">Save</el-button>
      </template>
    </el-dialog>

    <!-- Test Register Dialog -->
    <el-dialog v-model="testDialogVisible" title="Register Test" width="500px" destroy-on-close>
      <div v-if="testPointData" class="test-dialog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Register">{{ testPointData.registerType }} {{ testPointData.address }}</el-descriptions-item>
          <el-descriptions-item label="Name">{{ testPointData.name }}</el-descriptions-item>
          <el-descriptions-item label="Current Value">
            <span class="test-value">{{ testPointData.currentValue }}</span>
            <span class="test-unit">{{ testPointData.unit }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Raw Value">{{ testRawValue }}</el-descriptions-item>
          <el-descriptions-item label="Response Time">{{ testLatency }}ms</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag type="success" size="small">Success</el-tag>
          </el-descriptions-item>
        </el-descriptions>
        <div class="test-controls" v-if="testPointData.registerType === 'Coil' || testPointData.registerType === 'Holding Register'">
          <el-divider />
          <h4>Write Test Value</h4>
          <div class="write-controls">
            <el-input-number v-model="writeValue" :step="testPointData.dataType === 'bool' ? 1 : 0.1" />
            <el-button type="primary" @click="writeTestValue">Write</el-button>
          </div>
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
  Delete, Connection, Edit, Cpu, Grid
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing Modbus gateway...', 'Loading configurations...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const devicesLoading = ref(false)
const pointsLoading = ref(false)
const testing = ref(false)
const gatewayDialogVisible = ref(false)
const deviceDialogVisible = ref(false)
const pointDialogVisible = ref(false)
const testDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedGateway = ref<any>(null)
const selectedDevice = ref<any>(null)
const testPointData = ref<any>(null)
const searchKeyword = ref('')
const statusFilter = ref('')
const activeProtocol = ref('all')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const testRawValue = ref(0)
const testLatency = ref(0)
const writeValue = ref(0)

const gatewayFormRef = ref()
const deviceFormRef = ref()
const pointFormRef = ref()

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Gateways', value: '12', trend: 8, icon: 'Cpu', bgColor: '#409eff', key: 'gateways', subTitle: 'Active: 10' },
  { title: 'Modbus Devices', value: '48', trend: 12, icon: 'Connection', bgColor: '#67c23a', key: 'devices', subTitle: 'Online: 45' },
  { title: 'Active Registers', value: '1,245', trend: 15, icon: 'Document', bgColor: '#e6a23c', key: 'registers', subTitle: 'Updated: 1,210' },
  { title: 'Poll Rate', value: '98.5%', trend: 2, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'rate', subTitle: 'Avg: 45ms' }
])

const gateways = ref([
  { id: 1, name: 'Building A Modbus Gateway', protocol: 'modbus_tcp', endpoint: '192.168.1.100:502', deviceCount: 8, pointCount: 156, status: 'Online', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'Chiller Plant Gateway', protocol: 'modbus_tcp', endpoint: '192.168.1.101:502', deviceCount: 5, pointCount: 98, status: 'Online', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'Serial RTU Gateway', protocol: 'modbus_rtu', endpoint: '/dev/ttyUSB0:9600', deviceCount: 4, pointCount: 64, status: 'Online', lastSeen: '2024-01-20 10:27:00' },
  { id: 4, name: 'AHU Network Gateway', protocol: 'modbus_tcp', endpoint: '192.168.1.102:502', deviceCount: 6, pointCount: 112, status: 'Offline', lastSeen: '2024-01-20 09:15:00' },
  { id: 5, name: 'Lighting Control Gateway', protocol: 'modbus_tcp', endpoint: '192.168.1.103:502', deviceCount: 3, pointCount: 45, status: 'Online', lastSeen: '2024-01-20 10:29:00' },
  { id: 6, name: 'Power Monitoring RTU', protocol: 'modbus_rtu', endpoint: '/dev/ttyUSB1:19200', deviceCount: 2, pointCount: 32, status: 'Warning', lastSeen: '2024-01-20 10:26:00' }
])

const devicesMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, slaveId: 1, name: 'AHU-01 Controller', description: 'Main air handling unit controller', pointCount: 24, status: 'Online' },
    { id: 2, slaveId: 2, name: 'VAV-101', description: 'VAV box controller floor 1', pointCount: 12, status: 'Online' },
    { id: 3, slaveId: 3, name: 'VAV-102', description: 'VAV box controller floor 1', pointCount: 12, status: 'Online' },
    { id: 4, slaveId: 4, name: 'VAV-201', description: 'VAV box controller floor 2', pointCount: 12, status: 'Online' },
    { id: 5, slaveId: 5, name: 'VAV-202', description: 'VAV box controller floor 2', pointCount: 12, status: 'Offline' }
  ],
  2: [
    { id: 6, slaveId: 10, name: 'Chiller-01', description: 'Main chiller unit', pointCount: 32, status: 'Online' },
    { id: 7, slaveId: 11, name: 'Chiller-02', description: 'Secondary chiller unit', pointCount: 28, status: 'Online' },
    { id: 8, slaveId: 12, name: 'Cooling Tower', description: 'Cooling tower controller', pointCount: 24, status: 'Online' }
  ],
  3: [
    { id: 9, slaveId: 1, name: 'RTU-01', description: 'Roof top unit', pointCount: 16, status: 'Online' },
    { id: 10, slaveId: 2, name: 'FCU-101', description: 'Fan coil unit', pointCount: 8, status: 'Online' }
  ]
})

const pointsMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, address: 40001, registerType: 'Holding Register', name: 'Supply Air Temperature', dataType: 'float32', byteOrder: 'big', scale: 0.1, unit: '°C', currentValue: 22.5, status: 'Active' },
    { id: 2, address: 40003, registerType: 'Holding Register', name: 'Return Air Temperature', dataType: 'float32', byteOrder: 'big', scale: 0.1, unit: '°C', currentValue: 23.2, status: 'Active' },
    { id: 3, address: 40005, registerType: 'Holding Register', name: 'Fan Speed Setpoint', dataType: 'int16', byteOrder: 'big', scale: 1, unit: '%', currentValue: 65, status: 'Active' },
    { id: 4, address: 10001, registerType: 'Coil', name: 'Fan Run Command', dataType: 'bool', byteOrder: 'big', scale: 1, unit: '', currentValue: 1, status: 'Active' },
    { id: 5, address: 30001, registerType: 'Input Register', name: 'Static Pressure', dataType: 'int16', byteOrder: 'big', scale: 0.01, unit: 'in.wg', currentValue: 1.25, status: 'Active' }
  ],
  6: [
    { id: 6, address: 40001, registerType: 'Holding Register', name: 'Power Consumption', dataType: 'float32', byteOrder: 'big', scale: 1, unit: 'kW', currentValue: 45.2, status: 'Active' },
    { id: 7, address: 40003, registerType: 'Holding Register', name: 'Voltage', dataType: 'float32', byteOrder: 'big', scale: 1, unit: 'V', currentValue: 480, status: 'Active' }
  ]
})

// Forms
const gatewayForm = reactive({
  id: null, name: '', protocol: 'modbus_tcp', host: '', port: 502,
  serialPort: '', baudRate: 9600, parity: 'none', dataBits: 8, stopBits: 1,
  timeout: 3000, description: '',
  poolSize: 10, autoReconnect: true, maxRetries: 3, enableLogging: true
})

const deviceForm = reactive({ id: null, slaveId: 1, name: '', description: '' })
const pointForm = reactive({
  id: null, registerType: 'Holding Register', address: 40001, name: '',
  dataType: 'float32', byteOrder: 'big', scale: 1, unit: '', description: ''
})

// Rules
const gatewayRules = { name: [{ required: true, message: 'Please enter gateway name', trigger: 'blur' }] }
const deviceRules = { name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }] }
const pointRules = { name: [{ required: true, message: 'Please enter register name', trigger: 'blur' }] }

// ==================== Computed ====================
const totalGateways = computed(() => gateways.value.length)
const tcpCount = computed(() => gateways.value.filter(g => g.protocol === 'modbus_tcp').length)
const rtuCount = computed(() => gateways.value.filter(g => g.protocol === 'modbus_rtu').length)

const filteredGateways = computed(() => {
  let filtered = [...gateways.value]
  if (activeProtocol.value !== 'all') filtered = filtered.filter(g => g.protocol === activeProtocol.value)
  if (searchKeyword.value) filtered = filtered.filter(g => g.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || g.endpoint.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  if (statusFilter.value) filtered = filtered.filter(g => g.status === statusFilter.value)
  return filtered
})

const paginatedGateways = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredGateways.value.slice(start, end)
})

const gatewayDevices = computed(() => devicesMap.value[selectedGateway.value?.id] || [])
const devicePoints = computed(() => pointsMap.value[selectedDevice.value?.id] || [])
const activePointsCount = computed(() => devicePoints.value.filter(p => p.status === 'Active').length)

// ==================== Helper Methods ====================
const getRegisterTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Coil': 'warning',
    'Discrete Input': 'info',
    'Input Register': 'primary',
    'Holding Register': 'success'
  }
  return map[type] || 'info'
}

// ==================== Gateway Methods ====================
const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting Modbus configuration...')
const handleProtocolChange = () => { currentPage.value = 1 }
const fetchGateways = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Gateways refreshed') }, 500) }

const openAddGatewayDialog = () => {
  dialogMode.value = 'add'
  Object.assign(gatewayForm, { id: null, name: '', protocol: 'modbus_tcp', host: '', port: 502, serialPort: '', baudRate: 9600, parity: 'none', dataBits: 8, stopBits: 1, timeout: 3000, description: '', poolSize: 10, autoReconnect: true, maxRetries: 3, enableLogging: true })
  gatewayDialogVisible.value = true
}

const editGateway = (gateway: any) => { dialogMode.value = 'edit'; Object.assign(gatewayForm, gateway); gatewayDialogVisible.value = true }
const testGatewayConnection = () => { testing.value = true; setTimeout(() => { testing.value = false; ElMessage.success('Connection test successful') }, 1500) }
const saveGateway = async () => { if (!gatewayFormRef.value) return; await gatewayFormRef.value.validate((valid: boolean) => { if (valid) { ElMessage.success(dialogMode.value === 'add' ? 'Gateway added successfully' : 'Gateway updated successfully'); gatewayDialogVisible.value = false } }) }
const deleteGateway = (gateway: any) => {
  ElMessageBox.confirm(`Delete gateway "${gateway.name}"? This will also delete all associated devices and registers.`, 'Confirm Delete', { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }).then(() => {
    const index = gateways.value.findIndex(g => g.id === gateway.id)
    if (index !== -1) { gateways.value.splice(index, 1); if (selectedGateway.value?.id === gateway.id) { selectedGateway.value = null; selectedDevice.value = null } ElMessage.success(`Deleted: ${gateway.name}`) }
  }).catch(() => {})
}

const viewDevices = (gateway: any) => { selectedGateway.value = gateway; selectedDevice.value = null; refreshDevices() }
const testConnection = (gateway: any) => { ElMessage.info(`Testing connection to ${gateway.name}...`); setTimeout(() => { ElMessage.success(`Gateway ${gateway.name} is ${gateway.status}`) }, 1000) }
const refreshDevices = () => { devicesLoading.value = true; setTimeout(() => { devicesLoading.value = false; ElMessage.success('Devices refreshed') }, 500) }

// ==================== Device Methods ====================
const openAddDeviceDialog = () => { dialogMode.value = 'add'; Object.assign(deviceForm, { id: null, slaveId: 1, name: '', description: '' }); deviceDialogVisible.value = true }
const editDevice = (device: any) => { dialogMode.value = 'edit'; Object.assign(deviceForm, device); deviceDialogVisible.value = true }
const saveDevice = async () => { if (!deviceFormRef.value) return; await deviceFormRef.value.validate((valid: boolean) => { if (valid) { ElMessage.success(dialogMode.value === 'add' ? 'Device added successfully' : 'Device updated successfully'); deviceDialogVisible.value = false; refreshDevices() } }) }
const deleteDevice = (device: any) => {
  ElMessageBox.confirm(`Delete device "${device.name}"? This will also delete all associated registers.`, 'Confirm Delete', { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }).then(() => {
    const devices = devicesMap.value[selectedGateway.value?.id] || []
    const index = devices.findIndex(d => d.id === device.id)
    if (index !== -1) { devices.splice(index, 1); if (selectedDevice.value?.id === device.id) selectedDevice.value = null; ElMessage.success(`Deleted: ${device.name}`) }
  }).catch(() => {})
}
const viewPoints = (device: any) => { selectedDevice.value = device; refreshPoints() }

// ==================== Point Methods ====================
const openAddPointDialog = () => { dialogMode.value = 'add'; Object.assign(pointForm, { id: null, registerType: 'Holding Register', address: 40001, name: '', dataType: 'float32', byteOrder: 'big', scale: 1, unit: '', description: '' }); pointDialogVisible.value = true }
const editPoint = (point: any) => { dialogMode.value = 'edit'; Object.assign(pointForm, point); pointDialogVisible.value = true }
const testPoint = (point: any) => { testPointData.value = point; testRawValue.value = Math.floor(Math.random() * 10000); testLatency.value = Math.floor(Math.random() * 50) + 10; writeValue.value = point.currentValue; testDialogVisible.value = true }
const writeTestValue = () => { ElMessage.success(`Wrote value ${writeValue.value} to register ${testPointData.value.name}`); testDialogVisible.value = false }
const savePoint = async () => { if (!pointFormRef.value) return; await pointFormRef.value.validate((valid: boolean) => { if (valid) { ElMessage.success(dialogMode.value === 'add' ? 'Register added successfully' : 'Register updated successfully'); pointDialogVisible.value = false; refreshPoints() } }) }
const deletePoint = (point: any) => {
  ElMessageBox.confirm(`Delete register "${point.name}"?`, 'Confirm Delete', { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }).then(() => {
    const points = pointsMap.value[selectedDevice.value?.id] || []
    const index = points.findIndex(p => p.id === point.id)
    if (index !== -1) { points.splice(index, 1); ElMessage.success(`Deleted: ${point.name}`) }
  }).catch(() => {})
}
const refreshPoints = () => { pointsLoading.value = true; setTimeout(() => { pointsLoading.value = false; ElMessage.success('Registers refreshed') }, 500) }
const pollPoints = () => { ElMessage.info('Polling all registers...'); setTimeout(() => { ElMessage.success('Polling completed'); refreshPoints() }, 2000) }
const syncAllPoints = () => { ElMessage.info('Synchronizing all register values...'); setTimeout(() => { ElMessage.success('Sync completed'); refreshPoints() }, 2000) }

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Mounted ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => { if (messageIndex < loadingMessages.length - 1) messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }, 400)
  const progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(messageInterval); clearInterval(progressInterval); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; fetchGateways() }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.modbus-page {
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

.page-header .breadcrumb {
  margin-bottom: 8px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.page-header .description {
  color: #909399;
  font-size: 14px;
  margin: 0;
}

.page-header .header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-card .stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card .stat-info {
  flex: 1;
}

.stat-card .stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-card .stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.stat-card .stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-card .stat-trend.up { color: #67c23a; }
.stat-card .stat-trend.down { color: #f56c6c; }
.stat-card .stat-trend .trend-label { color: #909399; margin-left: 4px; }

.stat-card .stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-card .stat-footer {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
  color: #909399;
}

.tabs-card {
  margin-bottom: 20px;
}

.gateways-card, .devices-card, .points-card {
  margin-bottom: 20px;
}

.gateways-card .card-header, .devices-card .card-header, .points-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.gateways-card .table-actions, .devices-card .device-actions, .points-card .point-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.points-footer {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.value-active {
  color: #67c23a;
  font-weight: 500;
}

.value-inactive {
  color: #c0c4cc;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.status-dot.online {
  background-color: #67c23a;
  box-shadow: 0 0 4px #67c23a;
}

.status-dot.offline {
  background-color: #909399;
}

.test-dialog .test-value {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}

.test-dialog .test-unit {
  font-size: 14px;
  color: #909399;
  margin-left: 4px;
}

.test-dialog .write-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 8px;
}

.gateway-dialog :deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}
</style>