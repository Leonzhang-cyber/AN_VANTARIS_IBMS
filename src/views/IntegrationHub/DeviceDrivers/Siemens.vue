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
        <div class="loading-tip">Siemens Device Drivers</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="siemens-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Device Drivers</el-breadcrumb-item>
            <el-breadcrumb-item>Siemens</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Siemens Device Drivers</h1>
        <p class="description">Manage Siemens PLC connections, data blocks, tags, and industrial automation data</p>
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

    <!-- Siemens Devices Table -->
    <el-card class="devices-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Siemens PLC Devices</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="modelFilter" placeholder="Model" clearable style="width: 140px">
              <el-option label="S7-1200" value="S7-1200" />
              <el-option label="S7-1500" value="S7-1500" />
              <el-option label="S7-300" value="S7-300" />
              <el-option label="S7-400" value="S7-400" />
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
        <el-table-column prop="name" label="Device Name" min-width="150" show-overflow-tooltip />
        <el-table-column prop="model" label="Model" width="100" />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="rack" label="Rack" width="60" align="center" />
        <el-table-column prop="slot" label="Slot" width="60" align="center" />
        <el-table-column prop="dbCount" label="DB Blocks" width="90" align="center" />
        <el-table-column prop="tagCount" label="Tags" width="80" align="center" />
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
            <el-button link type="primary" size="small" @click="viewDataBlocks(row)">DB Blocks ({{ row.dbCount }})</el-button>
            <el-button link type="success" size="small" @click="viewTags(row)">Tags</el-button>
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

    <!-- Data Blocks Section -->
    <el-card class="datablocks-card" shadow="hover" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>Data Blocks - {{ selectedDevice.name }}</span>
          <div class="db-actions">
            <el-button size="small" type="primary" @click="openAddDBDialog">
              <el-icon><Plus /></el-icon> Add DB Block
            </el-button>
            <el-button size="small" @click="refreshDataBlocks">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="dataBlocks" stripe size="small" v-loading="dbLoading">
        <el-table-column prop="number" label="DB Number" width="100" />
        <el-table-column prop="name" label="Block Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
        <el-table-column prop="tagCount" label="Tags" width="80" align="center" />
        <el-table-column prop="size" label="Size (bytes)" width="100" align="center" />
        <el-table-column label="Actions" width="180">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDBTags(row)">View Tags</el-button>
            <el-button link type="success" size="small" @click="editDB(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteDB(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Tags Section -->
    <el-card class="tags-card" shadow="hover" v-if="selectedDB">
      <template #header>
        <div class="card-header">
          <span>Tags - {{ selectedDB.name }} (DB{{ selectedDB.number }})</span>
          <div class="tag-actions">
            <el-button size="small" type="primary" @click="openAddTagDialog">
              <el-icon><Plus /></el-icon> Add Tag
            </el-button>
            <el-button size="small" @click="refreshTags">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button size="small" type="success" @click="readAllTags">
              <el-icon><Connection /></el-icon> Read All
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="tags" stripe size="small" v-loading="tagsLoading">
        <el-table-column prop="name" label="Tag Name" min-width="150" show-overflow-tooltip />
        <el-table-column prop="offset" label="Offset" width="80" align="center" />
        <el-table-column prop="dataType" label="Data Type" width="110">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="arraySize" label="Array Size" width="90" align="center" />
        <el-table-column prop="currentValue" label="Current Value" width="150">
          <template #default="{ row }">
            <span class="tag-value">{{ formatValue(row.currentValue, row.dataType) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="description" label="Description" min-width="150" show-overflow-tooltip />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="readTag(row)">Read</el-button>
            <el-button v-if="isWritable(row.dataType)" link type="success" size="small" @click="openWriteDialog(row)">Write</el-button>
            <el-button link type="danger" size="small" @click="deleteTag(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="tags-footer" v-if="selectedDB">
        <el-button type="primary" @click="syncAllTags">Sync All Tags</el-button>
        <span class="tags-info">Total Tags: {{ tags.length }} | Active: {{ activeTagsCount }}</span>
      </div>
    </el-card>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="deviceDialogVisible" :title="dialogMode === 'add' ? 'Add Siemens Device' : 'Edit Siemens Device'" width="600px" destroy-on-close class="device-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Connection Settings" name="basic">
          <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="130px">
            <el-form-item label="Device Name" prop="name">
              <el-input v-model="deviceForm.name" placeholder="Enter device name" />
            </el-form-item>
            <el-form-item label="Model" prop="model">
              <el-select v-model="deviceForm.model" style="width: 100%">
                <el-option label="S7-1200" value="S7-1200" />
                <el-option label="S7-1500" value="S7-1500" />
                <el-option label="S7-300" value="S7-300" />
                <el-option label="S7-400" value="S7-400" />
                <el-option label="S7-200" value="S7-200" />
                <el-option label="LOGO!" value="LOGO" />
              </el-select>
            </el-form-item>
            <el-form-item label="IP Address" prop="ipAddress">
              <el-input v-model="deviceForm.ipAddress" placeholder="192.168.1.100" />
            </el-form-item>
            <el-form-item label="Rack" prop="rack">
              <el-input-number v-model="deviceForm.rack" :min="0" :max="7" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Slot" prop="slot">
              <el-input-number v-model="deviceForm.slot" :min="0" :max="7" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Connection Type" prop="connectionType">
              <el-radio-group v-model="deviceForm.connectionType">
                <el-radio value="iso">ISO over TCP</el-radio>
                <el-radio value="iso_on_tcp">ISO on TCP</el-radio>
                <el-radio value="profibus">Profibus</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Local TSAP" prop="localTsap">
              <el-input v-model="deviceForm.localTsap" placeholder="0100" />
            </el-form-item>
            <el-form-item label="Remote TSAP" prop="remoteTsap">
              <el-input v-model="deviceForm.remoteTsap" placeholder="0100" />
            </el-form-item>
            <el-form-item label="Description" prop="description">
              <el-input v-model="deviceForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="150px">
            <el-form-item label="Connection Timeout (ms)">
              <el-input-number v-model="deviceForm.timeout" :min="100" :max="30000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Auto Reconnect">
              <el-switch v-model="deviceForm.autoReconnect" />
            </el-form-item>
            <el-form-item label="Max Retry Count">
              <el-input-number v-model="deviceForm.maxRetries" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Polling Enabled">
              <el-switch v-model="deviceForm.pollingEnabled" />
            </el-form-item>
            <el-form-item label="Polling Interval (ms)">
              <el-input-number v-model="deviceForm.pollingInterval" :min="100" :max="60000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Enable Logging">
              <el-switch v-model="deviceForm.enableLogging" />
            </el-form-item>
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

    <!-- Add/Edit Data Block Dialog -->
    <el-dialog v-model="dbDialogVisible" :title="dialogMode === 'add' ? 'Add Data Block' : 'Edit Data Block'" width="500px" destroy-on-close>
      <el-form :model="dbForm" :rules="dbRules" ref="dbFormRef" label-width="110px">
        <el-form-item label="DB Number" prop="number">
          <el-input-number v-model="dbForm.number" :min="1" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Block Name" prop="name">
          <el-input v-model="dbForm.name" placeholder="Enter block name" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="dbForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dbDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveDB">Save</el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Tag Dialog -->
    <el-dialog v-model="tagDialogVisible" :title="dialogMode === 'add' ? 'Add Tag' : 'Edit Tag'" width="600px" destroy-on-close>
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="120px">
        <el-form-item label="Tag Name" prop="name">
          <el-input v-model="tagForm.name" placeholder="Enter tag name" />
        </el-form-item>
        <el-form-item label="Data Type" prop="dataType">
          <el-select v-model="tagForm.dataType" style="width: 100%">
            <el-option label="Bool" value="Bool" />
            <el-option label="Byte" value="Byte" />
            <el-option label="Word" value="Word" />
            <el-option label="DWord" value="DWord" />
            <el-option label="Int" value="Int" />
            <el-option label="DInt" value="DInt" />
            <el-option label="Real" value="Real" />
            <el-option label="String" value="String" />
            <el-option label="DateTime" value="DateTime" />
            <el-option label="Array" value="Array" />
          </el-select>
        </el-form-item>
        <el-form-item label="Offset" prop="offset">
          <el-input-number v-model="tagForm.offset" :min="0" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Bit Offset" v-if="tagForm.dataType === 'Bool'" prop="bitOffset">
          <el-input-number v-model="tagForm.bitOffset" :min="0" :max="7" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Array Size" v-if="tagForm.dataType === 'Array'" prop="arraySize">
          <el-input-number v-model="tagForm.arraySize" :min="1" :max="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Unit" prop="unit">
          <el-input v-model="tagForm.unit" placeholder="°C, bar, %, etc." />
        </el-form-item>
        <el-form-item label="Scale Factor" prop="scaleFactor">
          <el-input-number v-model="tagForm.scaleFactor" :step="0.1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="tagForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTag">Save</el-button>
      </template>
    </el-dialog>

    <!-- Write Value Dialog -->
    <el-dialog v-model="writeDialogVisible" title="Write Value" width="450px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="Tag Name">
          <span class="write-tag">{{ writeTarget?.name }}</span>
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
            :title="testResult.success ? 'PLC Connected' : 'Connection Failed'"
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
  Delete, Connection, Edit, Cpu, DataAnalysis, Monitor
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing Siemens drivers...', 'Loading devices...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const dbLoading = ref(false)
const tagsLoading = ref(false)
const testing = ref(false)
const deviceDialogVisible = ref(false)
const dbDialogVisible = ref(false)
const tagDialogVisible = ref(false)
const testDialogVisible = ref(false)
const writeDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedDevice = ref<any>(null)
const selectedDB = ref<any>(null)
const writeTarget = ref<any>(null)  // 重命名避免与函数冲突
const searchKeyword = ref('')
const modelFilter = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const writeValue = ref('')

const deviceFormRef = ref()
const dbFormRef = ref()
const tagFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Siemens Devices', value: '8', trend: 2, icon: 'Cpu', bgColor: '#409eff', key: 'devices', subTitle: 'Online: 7' },
  { title: 'Data Blocks', value: '32', trend: 4, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'dbs', subTitle: 'Active: 30' },
  { title: 'Tags', value: '456', trend: 12, icon: 'Document', bgColor: '#e6a23c', key: 'tags', subTitle: 'Monitored: 432' },
  { title: 'Data Points', value: '2.4K/s', trend: 8, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'rate', subTitle: 'Peak: 3.2K/s' }
])

const devices = ref([
  { id: 1, name: 'PLC_Production_Line1', model: 'S7-1500', ipAddress: '192.168.1.100', rack: 0, slot: 1, dbCount: 8, tagCount: 124, status: 'Online', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'PLC_Packaging', model: 'S7-1200', ipAddress: '192.168.1.101', rack: 0, slot: 1, dbCount: 5, tagCount: 56, status: 'Online', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'PLC_HVAC', model: 'S7-300', ipAddress: '192.168.1.102', rack: 0, slot: 2, dbCount: 6, tagCount: 89, status: 'Online', lastSeen: '2024-01-20 10:32:00' },
  { id: 4, name: 'PLC_Energy_Monitoring', model: 'S7-1200', ipAddress: '192.168.1.103', rack: 0, slot: 1, dbCount: 4, tagCount: 45, status: 'Warning', lastSeen: '2024-01-20 10:25:00' }
])

const dataBlocksMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, number: 100, name: 'ProcessData', description: 'Main process data block', tagCount: 24, size: 256 },
    { id: 2, number: 101, name: 'AlarmData', description: 'Alarm and event data', tagCount: 12, size: 128 }
  ],
  2: [
    { id: 3, number: 200, name: 'PackagingParams', description: 'Packaging parameters', tagCount: 16, size: 192 }
  ]
})

const tagsMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, name: 'Temperature', offset: 0, dataType: 'Real', arraySize: 0, currentValue: 22.5, unit: '°C', description: 'Process temperature' },
    { id: 2, name: 'Pressure', offset: 4, dataType: 'Real', arraySize: 0, currentValue: 101.3, unit: 'kPa', description: 'Process pressure' },
    { id: 3, name: 'MotorStatus', offset: 8, dataType: 'Bool', bitOffset: 0, arraySize: 0, currentValue: true, unit: '', description: 'Motor running status' },
    { id: 4, name: 'ProductionCount', offset: 10, dataType: 'DInt', arraySize: 0, currentValue: 12450, unit: 'pcs', description: 'Daily production count' }
  ],
  2: [
    { id: 5, name: 'AlarmCode', offset: 0, dataType: 'Word', arraySize: 0, currentValue: 0, unit: '', description: 'Active alarm code' }
  ]
})

// ==================== Computed ====================
const filteredDevices = computed(() => {
  let filtered = [...devices.value]
  if (searchKeyword.value) filtered = filtered.filter(d => d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || d.ipAddress.includes(searchKeyword.value))
  if (modelFilter.value) filtered = filtered.filter(d => d.model === modelFilter.value)
  if (statusFilter.value) filtered = filtered.filter(d => d.status === statusFilter.value)
  return filtered
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

const dataBlocks = computed(() => dataBlocksMap.value[selectedDevice.value?.id] || [])
const tags = computed(() => tagsMap.value[selectedDB.value?.id] || [])
const activeTagsCount = computed(() => tags.value.length)

// ==================== Helper Methods ====================
const getDataTypeTag = (dataType: string) => {
  const map: Record<string, string> = {
    'Bool': 'warning',
    'Int': 'primary',
    'DInt': 'primary',
    'Real': 'success',
    'String': 'info',
    'Array': 'danger'
  }
  return map[dataType] || 'info'
}

const formatValue = (value: any, dataType: string) => {
  if (dataType === 'Bool') return value ? 'TRUE' : 'FALSE'
  if (dataType === 'Real') return typeof value === 'number' ? value.toFixed(2) : value
  return value
}

const isWritable = (dataType: string) => {
  return dataType !== 'Array' && dataType !== 'String'
}

const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting Siemens configuration...')
const fetchDevices = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Devices refreshed') }, 500) }

const openAddDeviceDialog = () => {
  dialogMode.value = 'add'
  Object.assign(deviceForm, {
    id: null, name: '', model: 'S7-1200', ipAddress: '', rack: 0, slot: 1,
    connectionType: 'iso_on_tcp', localTsap: '0100', remoteTsap: '0100',
    description: '', timeout: 5000, autoReconnect: true, maxRetries: 3,
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
    testResult.message = 'Successfully connected to Siemens PLC'
    testResult.details = {
      device: deviceForm.ipAddress,
      model: deviceForm.model,
      firmware: 'V2.9',
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
  ElMessageBox.confirm(`Delete device "${device.name}"? This will also remove all data blocks and tags.`, 'Confirm Delete', {
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

const viewDataBlocks = (device: any) => {
  selectedDevice.value = device
  selectedDB.value = null
  refreshDataBlocks()
}

const viewTags = (device: any) => {
  selectedDevice.value = device
  ElMessage.info(`Viewing tags for ${device.name}`)
}

const refreshDataBlocks = () => {
  dbLoading.value = true
  setTimeout(() => { dbLoading.value = false; ElMessage.success('Data blocks refreshed') }, 500)
}

// ==================== Data Block Methods ====================
const openAddDBDialog = () => {
  dialogMode.value = 'add'
  Object.assign(dbForm, { id: null, number: 1, name: '', description: '' })
  dbDialogVisible.value = true
}

const editDB = (db: any) => {
  dialogMode.value = 'edit'
  Object.assign(dbForm, db)
  dbDialogVisible.value = true
}

const saveDB = async () => {
  if (!dbFormRef.value) return
  await dbFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Data block added successfully' : 'Data block updated successfully')
      dbDialogVisible.value = false
      refreshDataBlocks()
    }
  })
}

const deleteDB = (db: any) => {
  ElMessageBox.confirm(`Delete data block "${db.name}"? This will also remove all tags.`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const dbs = dataBlocksMap.value[selectedDevice.value.id]
    const index = dbs.findIndex(d => d.id === db.id)
    if (index !== -1) { dbs.splice(index, 1); if (selectedDB.value?.id === db.id) selectedDB.value = null; ElMessage.success(`Deleted: ${db.name}`) }
  }).catch(() => {})
}

const viewDBTags = (db: any) => {
  selectedDB.value = db
  refreshTags()
}

// ==================== Tag Methods ====================
const openAddTagDialog = () => {
  dialogMode.value = 'add'
  Object.assign(tagForm, {
    id: null, name: '', dataType: 'Real', offset: 0, bitOffset: 0, arraySize: 0,
    unit: '', scaleFactor: 1, description: ''
  })
  tagDialogVisible.value = true
}

const editTag = (tag: any) => {
  dialogMode.value = 'edit'
  Object.assign(tagForm, tag)
  tagDialogVisible.value = true
}

const saveTag = async () => {
  if (!tagFormRef.value) return  await tagFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Tag added successfully' : 'Tag updated successfully')
      tagDialogVisible.value = false
      refreshTags()
    }
  })
}

const deleteTag = (tag: any) => {
  ElMessageBox.confirm(`Delete tag "${tag.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const tagsList = tagsMap.value[selectedDB.value.id]
    const index = tagsList.findIndex(t => t.id === tag.id)
    if (index !== -1) { tagsList.splice(index, 1); ElMessage.success(`Deleted: ${tag.name}`) }
  }).catch(() => {})
}

const readTag = (tag: any) => {
  ElMessage.info(`Reading ${tag.name}...`)
  setTimeout(() => {
    const newValue = tag.dataType === 'Real' ? (Math.random() * 100).toFixed(2) : Math.floor(Math.random() * 1000)
    tag.currentValue = newValue
    ElMessage.success(`${tag.name}: ${formatValue(newValue, tag.dataType)} ${tag.unit}`)
  }, 300)
}

const openWriteDialog = (tag: any) => {
  writeTarget.value = tag
  writeValue.value = tag.currentValue?.toString() || ''
  writeDialogVisible.value = true
}

const submitWrite = () => {
  if (writeTarget.value) {
    writeTarget.value.currentValue = writeValue.value
    ElMessage.success(`Wrote ${writeValue.value} to ${writeTarget.value.name}`)
    writeDialogVisible.value = false
  }
}

const readAllTags = () => {
  ElMessage.info('Reading all tags...')
  setTimeout(() => {
    tags.value.forEach(tag => {
      tag.currentValue = tag.dataType === 'Real' ? (Math.random() * 100).toFixed(2) : Math.floor(Math.random() * 1000)
    })
    ElMessage.success('All tags updated')
    refreshTags()
  }, 1000)
}

const syncAllTags = () => {
  ElMessage.info('Synchronizing all tags...')
  setTimeout(() => { ElMessage.success('Sync completed'); refreshTags() }, 2000)
}

const refreshTags = () => {
  tagsLoading.value = true
  setTimeout(() => { tagsLoading.value = false; ElMessage.success('Tags refreshed') }, 500)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Forms ====================
const deviceForm = reactive({
  id: null, name: '', model: 'S7-1200', ipAddress: '', rack: 0, slot: 1,
  connectionType: 'iso_on_tcp', localTsap: '0100', remoteTsap: '0100',
  description: '', timeout: 5000, autoReconnect: true, maxRetries: 3,
  pollingEnabled: true, pollingInterval: 1000, enableLogging: true
})

const dbForm = reactive({ id: null, number: 1, name: '', description: '' })
const tagForm = reactive({
  id: null, name: '', dataType: 'Real', offset: 0, bitOffset: 0, arraySize: 0,
  unit: '', scaleFactor: 1, description: ''
})

const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }]
}

const dbRules = {
  number: [{ required: true, message: 'Please enter DB number', trigger: 'blur' }],
  name: [{ required: true, message: 'Please enter block name', trigger: 'blur' }]
}

const tagRules = {
  name: [{ required: true, message: 'Please enter tag name', trigger: 'blur' }],
  offset: [{ required: true, message: 'Please enter offset', trigger: 'blur' }]
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

.siemens-page {
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

.devices-card, .datablocks-card, .tags-card { margin-bottom: 20px; }
.devices-card .card-header, .datablocks-card .card-header, .tags-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.devices-card .table-actions, .datablocks-card .db-actions, .tags-card .tag-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
.tags-footer { margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }

.tag-value { font-weight: 500; color: #409eff; }
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.device-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.write-tag, .write-current { font-family: monospace; font-size: 13px; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>