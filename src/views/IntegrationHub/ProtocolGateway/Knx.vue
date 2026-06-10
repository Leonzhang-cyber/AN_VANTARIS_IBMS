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
        <div class="loading-tip">KNX Gateway Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="knx-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>KNX</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>KNX Gateway Management</h1>
        <p class="description">Manage KNX network connections, group addresses, devices, and building automation</p>
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

    <!-- KNX Gateways Table -->
    <el-card class="gateways-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>KNX Gateways</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="typeFilter" placeholder="Connection Type" clearable style="width: 140px">
              <el-option label="Tunneling" value="tunneling" />
              <el-option label="Routing" value="routing" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Connected" value="Connected" />
              <el-option label="Disconnected" value="Disconnected" />
              <el-option label="Error" value="Error" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchGateways" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedGateways" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Gateway Name" min-width="160" show-overflow-tooltip />
        <el-table-column prop="connectionType" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="row.connectionType === 'tunneling' ? 'primary' : 'success'" size="small">
              {{ row.connectionType === 'tunneling' ? 'Tunneling' : 'Routing' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="port" label="Port" width="80" />
        <el-table-column prop="individualAddress" label="Individual Address" width="120" />
        <el-table-column prop="groupAddressCount" label="Group Addresses" width="120" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Connected' ? 'success' : row.status === 'Error' ? 'danger' : 'info'" size="small">
              <span class="status-dot" :class="row.status === 'Connected' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastSeen" label="Last Seen" width="150" />
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewGroupAddresses(row)">Group Addresses ({{ row.groupAddressCount }})</el-button>
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

    <!-- Group Addresses Section -->
    <el-card class="group-addresses-card" shadow="hover" v-if="selectedGateway">
      <template #header>
        <div class="card-header">
          <span>Group Addresses - {{ selectedGateway.name }}</span>
          <div class="group-actions">
            <el-input
                v-model="groupSearch"
                placeholder="Search address or name"
                prefix-icon="Search"
                clearable
                size="small"
                style="width: 200px"
            />
            <el-button size="small" type="primary" @click="openAddGroupAddressDialog">
              <el-icon><Plus /></el-icon> Add Group Address
            </el-button>
            <el-button size="small" @click="refreshGroupAddresses">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredGroupAddresses" stripe size="small" v-loading="groupsLoading">
        <el-table-column prop="mainGroup" label="Main Group" width="100" />
        <el-table-column prop="middleGroup" label="Middle Group" width="100" />
        <el-table-column prop="subGroup" label="Sub Group" width="100" />
        <el-table-column prop="groupAddress" label="Group Address" width="120">
          <template #default="{ row }">
            <code class="group-address">{{ row.groupAddress }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="dataType" label="Data Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="currentValue" label="Current Value" width="150">
          <template #default="{ row }">
            <span class="group-value">{{ row.currentValue || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="Unit" width="70" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="readGroupValue(row)">Read</el-button>
            <el-button link type="success" size="small" @click="writeGroupValue(row)">Write</el-button>
            <el-button link type="danger" size="small" @click="deleteGroupAddress(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="group-footer" v-if="selectedGateway">
        <el-button type="primary" @click="syncGroupAddresses">Sync All</el-button>
        <span class="group-info">Total: {{ groupAddresses.length }} | Active: {{ activeGroups }}</span>
      </div>
    </el-card>

    <!-- Bus Monitor Section -->
    <el-card class="monitor-card" shadow="hover" v-if="showMonitor">
      <template #header>
        <div class="card-header">
          <span>KNX Bus Monitor - {{ selectedGateway?.name }}</span>
          <div class="monitor-actions">
            <el-button size="small" @click="clearMonitor">Clear</el-button>
            <el-button size="small" type="danger" @click="showMonitor = false">Close</el-button>
          </div>
        </div>
      </template>

      <div class="monitor-container">
        <div class="monitor-filter">
          <el-input
              v-model="monitorFilter"
              placeholder="Filter telegrams..."
              prefix-icon="Search"
              clearable
              size="small"
              style="width: 250px"
          />
          <el-checkbox v-model="monitorShowRead">Show Read</el-checkbox>
          <el-checkbox v-model="monitorShowWrite">Show Write</el-checkbox>
          <el-checkbox v-model="monitorShowResponse">Show Response</el-checkbox>
        </div>
        <div class="monitor-messages" ref="monitorRef">
          <div
              v-for="(msg, idx) in filteredTelegrams"
              :key="idx"
              class="monitor-message"
              :class="msg.type"
          >
            <div class="message-time">{{ msg.time }}</div>
            <div class="message-source">{{ msg.source }}</div>
            <div class="message-dest">{{ msg.destination }}</div>
            <div class="message-data">{{ msg.data }}</div>
            <div class="message-value" v-if="msg.value">{{ msg.value }}</div>
          </div>
          <div v-if="filteredTelegrams.length === 0" class="monitor-empty">
            <el-empty description="No telegrams received" :image-size="60" />
          </div>
        </div>
      </div>
    </el-card>

    <!-- Add/Edit KNX Gateway Dialog -->
    <el-dialog v-model="gatewayDialogVisible" :title="dialogMode === 'add' ? 'Add KNX Gateway' : 'Edit KNX Gateway'" width="600px" destroy-on-close class="gateway-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Connection Settings" name="basic">
          <el-form :model="gatewayForm" :rules="gatewayRules" ref="gatewayFormRef" label-width="130px">
            <el-form-item label="Gateway Name" prop="name">
              <el-input v-model="gatewayForm.name" placeholder="Enter gateway name" />
            </el-form-item>
            <el-form-item label="Connection Type" prop="connectionType">
              <el-radio-group v-model="gatewayForm.connectionType">
                <el-radio value="tunneling">Tunneling (IP)</el-radio>
                <el-radio value="routing">Routing (Multicast)</el-radio>
              </el-radio-group>
            </el-form-item>

            <template v-if="gatewayForm.connectionType === 'tunneling'">
              <el-form-item label="KNX Gateway IP" prop="ipAddress">
                <el-input v-model="gatewayForm.ipAddress" placeholder="192.168.1.100" />
              </el-form-item>
              <el-form-item label="Port" prop="port">
                <el-input-number v-model="gatewayForm.port" :min="1" :max="65535" style="width: 100%" />
              </el-form-item>
            </template>

            <template v-else>
              <el-form-item label="Multicast IP" prop="multicastIp">
                <el-input v-model="gatewayForm.multicastIp" placeholder="224.0.23.12" />
              </el-form-item>
              <el-form-item label="Network Interface" prop="networkInterface">
                <el-input v-model="gatewayForm.networkInterface" placeholder="eth0" />
              </el-form-item>
            </template>

            <el-form-item label="Individual Address" prop="individualAddress">
              <el-input v-model="gatewayForm.individualAddress" placeholder="15.15.250" />
            </el-form-item>
            <el-form-item label="Description" prop="description">
              <el-input v-model="gatewayForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="150px">
            <el-form-item label="Connection Timeout (ms)">
              <el-input-number v-model="gatewayForm.timeout" :min="100" :max="30000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Auto Reconnect">
              <el-switch v-model="gatewayForm.autoReconnect" />
            </el-form-item>
            <el-form-item label="Enable Bus Monitor">
              <el-switch v-model="gatewayForm.enableMonitor" />
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

    <!-- Add/Edit Group Address Dialog -->
    <el-dialog v-model="groupDialogVisible" :title="dialogMode === 'add' ? 'Add Group Address' : 'Edit Group Address'" width="550px" destroy-on-close>
      <el-form :model="groupForm" :rules="groupRules" ref="groupFormRef" label-width="120px">
        <el-form-item label="Main Group" prop="mainGroup">
          <el-input-number v-model="groupForm.mainGroup" :min="0" :max="31" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Middle Group" prop="middleGroup">
          <el-input-number v-model="groupForm.middleGroup" :min="0" :max="7" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Sub Group" prop="subGroup">
          <el-input-number v-model="groupForm.subGroup" :min="0" :max="255" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Group Address">
          <span class="group-address-preview">{{ groupAddressPreview }}</span>
        </el-form-item>
        <el-form-item label="Name" prop="name">
          <el-input v-model="groupForm.name" placeholder="e.g., Living Room Temperature" />
        </el-form-item>
        <el-form-item label="Data Type" prop="dataType">
          <el-select v-model="groupForm.dataType" style="width: 100%">
            <el-option label="1-bit Switch" value="switch" />
            <el-option label="1-bit Dimming" value="dimming" />
            <el-option label="1-byte Unsigned" value="uint8" />
            <el-option label="2-byte Signed" value="int16" />
            <el-option label="2-byte Float" value="float16" />
            <el-option label="4-byte Float" value="float32" />
            <el-option label="Temperature" value="temperature" />
            <el-option label="Percentage" value="percentage" />
            <el-option label="String" value="string" />
            <el-option label="DateTime" value="datetime" />
          </el-select>
        </el-form-item>
        <el-form-item label="Unit" prop="unit">
          <el-input v-model="groupForm.unit" placeholder="°C, %, lux, etc." />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="groupForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="groupDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testGroupAddress">Test Read</el-button>
        <el-button type="success" @click="saveGroupAddress">Save</el-button>
      </template>
    </el-dialog>

    <!-- Write Value Dialog -->
    <el-dialog v-model="writeDialogVisible" title="Write Value" width="450px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="Group Address">
          <code class="write-address">{{ writeGroup?.groupAddress }}</code>
        </el-form-item>
        <el-form-item label="Current Value">
          <span class="write-current">{{ writeGroup?.currentValue }} {{ writeGroup?.unit }}</span>
        </el-form-item>
        <el-form-item label="Data Type">
          <el-tag :type="getDataTypeTag(writeGroup?.dataType)" size="small">{{ writeGroup?.dataType }}</el-tag>
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
            :title="testResult.success ? 'Gateway Connected' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Gateway:</strong> {{ testResult.details.gateway }}</p>
          <p><strong>Firmware Version:</strong> {{ testResult.details.firmware }}</p>
          <p><strong>Individual Address:</strong> {{ testResult.details.individualAddress }}</p>
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
  Delete, Connection, Edit, Grid, DataAnalysis, Message
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing KNX gateway...', 'Loading group addresses...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const groupsLoading = ref(false)
const testing = ref(false)
const gatewayDialogVisible = ref(false)
const groupDialogVisible = ref(false)
const testDialogVisible = ref(false)
const writeDialogVisible = ref(false)
const showMonitor = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedGateway = ref<any>(null)
const writeGroup = ref<any>(null)
const searchKeyword = ref('')
const groupSearch = ref('')
const monitorFilter = ref('')
const monitorShowRead = ref(true)
const monitorShowWrite = ref(true)
const monitorShowResponse = ref(true)
const typeFilter = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const writeValue = ref('')
const monitorRef = ref<HTMLElement>()

const gatewayFormRef = ref()
const groupFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// Mock telegrams data
const telegrams = ref<any[]>([])

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'KNX Gateways', value: '4', trend: 0, icon: 'Connection', bgColor: '#409eff', key: 'gateways', subTitle: 'Connected: 3' },
  { title: 'Group Addresses', value: '156', trend: 12, icon: 'Grid', bgColor: '#67c23a', key: 'groups', subTitle: 'Active: 148' },
  { title: 'Telegrams/s', value: '45', trend: 8, icon: 'Message', bgColor: '#e6a23c', key: 'telegrams', subTitle: 'Peak: 67' },
  { title: 'Devices', value: '48', trend: 5, icon: 'DataAnalysis', bgColor: '#f56c6c', key: 'devices', subTitle: 'Online: 45' }
])

const gateways = ref([
  { id: 1, name: 'Main KNX Gateway', connectionType: 'tunneling', ipAddress: '192.168.1.100', port: 3671, individualAddress: '15.15.250', groupAddressCount: 56, status: 'Connected', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'Lighting Gateway', connectionType: 'routing', ipAddress: '224.0.23.12', port: 0, individualAddress: '15.15.251', groupAddressCount: 48, status: 'Connected', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'HVAC Gateway', connectionType: 'tunneling', ipAddress: '192.168.1.101', port: 3671, individualAddress: '15.15.252', groupAddressCount: 32, status: 'Connected', lastSeen: '2024-01-20 10:32:00' },
  { id: 4, name: 'Shading Gateway', connectionType: 'routing', ipAddress: '224.0.23.12', port: 0, individualAddress: '15.15.253', groupAddressCount: 20, status: 'Disconnected', lastSeen: '2024-01-20 08:15:00' }
])

const groupAddressesMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, mainGroup: 0, middleGroup: 0, subGroup: 1, groupAddress: '0/0/1', name: 'Living Room Light', dataType: 'switch', currentValue: 0, unit: '', description: 'Main living room lighting' },
    { id: 2, mainGroup: 0, middleGroup: 0, subGroup: 2, groupAddress: '0/0/2', name: 'Living Room Temperature', dataType: 'temperature', currentValue: 22.5, unit: '°C', description: 'Living room temperature sensor' },
    { id: 3, mainGroup: 1, middleGroup: 1, subGroup: 1, groupAddress: '1/1/1', name: 'Kitchen Light', dataType: 'switch', currentValue: 1, unit: '', description: 'Kitchen lighting' },
    { id: 4, mainGroup: 1, middleGroup: 1, subGroup: 2, groupAddress: '1/1/2', name: 'Kitchen Temperature', dataType: 'temperature', currentValue: 23.0, unit: '°C', description: 'Kitchen temperature sensor' }
  ],
  2: [
    { id: 5, mainGroup: 2, middleGroup: 0, subGroup: 1, groupAddress: '2/0/1', name: 'Floor 1 Hall Light', dataType: 'switch', currentValue: 0, unit: '', description: 'Hallway lighting' }
  ],
  3: [
    { id: 6, mainGroup: 3, middleGroup: 0, subGroup: 1, groupAddress: '3/0/1', name: 'AHU Setpoint', dataType: 'temperature', currentValue: 21.0, unit: '°C', description: 'Air handling unit setpoint' }
  ]
})

// ==================== Computed ====================
const filteredGateways = computed(() => {
  let filtered = [...gateways.value]
  if (searchKeyword.value) filtered = filtered.filter(g => g.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || g.ipAddress?.includes(searchKeyword.value))
  if (typeFilter.value) filtered = filtered.filter(g => g.connectionType === typeFilter.value)
  if (statusFilter.value) filtered = filtered.filter(g => g.status === statusFilter.value)
  return filtered
})

const paginatedGateways = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredGateways.value.slice(start, end)
})

const groupAddresses = computed(() => groupAddressesMap.value[selectedGateway.value?.id] || [])
const filteredGroupAddresses = computed(() => {
  if (!groupSearch.value) return groupAddresses.value
  return groupAddresses.value.filter(g =>
      g.groupAddress.includes(groupSearch.value) ||
      g.name.toLowerCase().includes(groupSearch.value.toLowerCase())
  )
})

const activeGroups = computed(() => groupAddresses.value.filter(g => g.currentValue !== null).length)
const groupAddressPreview = computed(() => `${groupForm.mainGroup}/${groupForm.middleGroup}/${groupForm.subGroup}`)

const filteredTelegrams = computed(() => {
  let filtered = [...telegrams.value]
  if (monitorFilter.value) filtered = filtered.filter(t =>
      t.source.includes(monitorFilter.value) ||
      t.destination.includes(monitorFilter.value) ||
      t.data.includes(monitorFilter.value)
  )
  if (!monitorShowRead.value) filtered = filtered.filter(t => t.type !== 'read')
  if (!monitorShowWrite.value) filtered = filtered.filter(t => t.type !== 'write')
  if (!monitorShowResponse.value) filtered = filtered.filter(t => t.type !== 'response')
  return filtered
})

// ==================== Helper Methods ====================
const getDataTypeTag = (dataType: string) => {
  const map: Record<string, string> = {
    'switch': 'warning',
    'dimming': 'warning',
    'temperature': 'danger',
    'percentage': 'primary',
    'string': 'info',
    'datetime': 'success'
  }
  return map[dataType] || 'info'
}

const scrollMonitorToBottom = () => {
  nextTick(() => {
    if (monitorRef.value) {
      monitorRef.value.scrollTop = monitorRef.value.scrollHeight
    }
  })
}

// Simulate a telegram
const addTelegram = (telegram: any) => {
  telegrams.value.push(telegram)
  if (telegrams.value.length > 200) telegrams.value.shift()
  scrollMonitorToBottom()
}

// ==================== Gateway Methods ====================
const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting KNX configuration...')
const fetchGateways = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Gateways refreshed') }, 500) }

const openAddGatewayDialog = () => {
  dialogMode.value = 'add'
  Object.assign(gatewayForm, {
    id: null, name: '', connectionType: 'tunneling', ipAddress: '', port: 3671,
    multicastIp: '224.0.23.12', networkInterface: 'eth0', individualAddress: '15.15.250',
    description: '', timeout: 3000, autoReconnect: true, enableMonitor: false, enableLogging: true
  })
  gatewayDialogVisible.value = true
}

const editGateway = (gateway: any) => {
  dialogMode.value = 'edit'
  Object.assign(gatewayForm, gateway)
  gatewayDialogVisible.value = true
}

const testGatewayConnection = () => {
  testing.value = true
  setTimeout(() => {
    testing.value = false
    testResult.success = true
    testResult.message = 'Successfully connected to KNX gateway'
    testResult.details = {
      gateway: gatewayForm.ipAddress || gatewayForm.multicastIp,
      firmware: 'KNX IP Router v2.0',
      individualAddress: gatewayForm.individualAddress,
      responseTime: 28
    }
    testDialogVisible.value = true
  }, 1500)
}

const saveGateway = async () => {
  if (!gatewayFormRef.value) return
  await gatewayFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Gateway added successfully' : 'Gateway updated successfully')
      gatewayDialogVisible.value = false
    }
  })
}

const deleteGateway = (gateway: any) => {
  ElMessageBox.confirm(`Delete gateway "${gateway.name}"? This will also remove all group addresses.`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const index = gateways.value.findIndex(g => g.id === gateway.id)
    if (index !== -1) { gateways.value.splice(index, 1); if (selectedGateway.value?.id === gateway.id) selectedGateway.value = null; ElMessage.success(`Deleted: ${gateway.name}`) }
  }).catch(() => {})
}

const testConnection = (gateway: any) => {
  ElMessage.info(`Testing connection to ${gateway.name}...`)
  setTimeout(() => { ElMessage.success(`${gateway.name} is ${gateway.status}`) }, 1000)
}

const viewGroupAddresses = (gateway: any) => {
  selectedGateway.value = gateway
  refreshGroupAddresses()
}

const refreshGroupAddresses = () => {
  groupsLoading.value = true
  setTimeout(() => { groupsLoading.value = false; ElMessage.success('Group addresses refreshed') }, 500)
}

// ==================== Group Address Methods ====================
const openAddGroupAddressDialog = () => {
  dialogMode.value = 'add'
  Object.assign(groupForm, { id: null, mainGroup: 0, middleGroup: 0, subGroup: 1, name: '', dataType: 'switch', unit: '', description: '' })
  groupDialogVisible.value = true
}

const editGroupAddress = (group: any) => {
  dialogMode.value = 'edit'
  Object.assign(groupForm, group)
  groupDialogVisible.value = true
}

const testGroupAddress = () => {
  ElMessage.info(`Reading group address ${groupAddressPreview}...`)
  setTimeout(() => { ElMessage.success('Read successful') }, 500)
}

const saveGroupAddress = async () => {
  if (!groupFormRef.value) return
  await groupFormRef.value.validate((valid: boolean) => {
    if (valid) {
      const newGroup = {
        id: Date.now(),
        mainGroup: groupForm.mainGroup,
        middleGroup: groupForm.middleGroup,
        subGroup: groupForm.subGroup,
        groupAddress: groupAddressPreview,
        name: groupForm.name,
        dataType: groupForm.dataType,
        currentValue: null,
        unit: groupForm.unit,
        description: groupForm.description
      }
      if (!groupAddressesMap.value[selectedGateway.value.id]) {
        groupAddressesMap.value[selectedGateway.value.id] = []
      }
      if (dialogMode.value === 'add') {
        groupAddressesMap.value[selectedGateway.value.id].push(newGroup)
        ElMessage.success('Group address added successfully')
      } else {
        const index = groupAddressesMap.value[selectedGateway.value.id].findIndex(g => g.id === groupForm.id)
        if (index !== -1) { groupAddressesMap.value[selectedGateway.value.id][index] = { ...groupForm, groupAddress: groupAddressPreview }; ElMessage.success('Group address updated successfully') }
      }
      groupDialogVisible.value = false
      refreshGroupAddresses()
    }
  })
}

const deleteGroupAddress = (group: any) => {
  ElMessageBox.confirm(`Delete group address "${group.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const groups = groupAddressesMap.value[selectedGateway.value.id]
    const index = groups.findIndex(g => g.id === group.id)
    if (index !== -1) { groups.splice(index, 1); ElMessage.success(`Deleted: ${group.name}`) }
  }).catch(() => {})
}

const readGroupValue = (group: any) => {
  ElMessage.info(`Reading ${group.name}...`)
  setTimeout(() => {
    const newValue = group.dataType === 'temperature' ? (Math.random() * 30 + 10).toFixed(1) : Math.random() > 0.5 ? 1 : 0
    group.currentValue = newValue
    ElMessage.success(`${group.name}: ${newValue} ${group.unit}`)
    addTelegram({
      time: new Date().toLocaleTimeString(),
      source: 'Gateway',
      destination: group.groupAddress,
      data: 'GroupValue Read',
      value: `${newValue} ${group.unit}`,
      type: 'read'
    })
  }, 300)
}

const writeGroupValue = (group: any) => {
  writeGroup.value = group
  writeValue.value = group.currentValue?.toString() || ''
  writeDialogVisible.value = true
}

const submitWrite = () => {
  if (writeGroup.value) {
    writeGroup.value.currentValue = writeValue.value
    ElMessage.success(`Wrote ${writeValue.value} to ${writeGroup.value.name}`)
    writeDialogVisible.value = false
    addTelegram({
      time: new Date().toLocaleTimeString(),
      source: 'Gateway',
      destination: writeGroup.value.groupAddress,
      data: 'GroupValue Write',
      value: `${writeValue.value} ${writeGroup.value.unit}`,
      type: 'write'
    })
  }
}

const syncGroupAddresses = () => {
  ElMessage.info('Synchronizing group addresses...')
  setTimeout(() => { ElMessage.success('Sync completed'); refreshGroupAddresses() }, 2000)
}

const clearMonitor = () => {
  telegrams.value = []
  ElMessage.success('Monitor cleared')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Group Form ====================
const groupForm = reactive({
  id: null, mainGroup: 0, middleGroup: 0, subGroup: 1, name: '', dataType: 'switch', unit: '', description: ''
})

const groupRules = {
  name: [{ required: true, message: 'Please enter group address name', trigger: 'blur' }]
}

// Gateway Form
const gatewayForm = reactive({
  id: null, name: '', connectionType: 'tunneling', ipAddress: '', port: 3671,
  multicastIp: '224.0.23.12', networkInterface: 'eth0', individualAddress: '15.15.250',
  description: '', timeout: 3000, autoReconnect: true, enableMonitor: false, enableLogging: true
})

const gatewayRules = {
  name: [{ required: true, message: 'Please enter gateway name', trigger: 'blur' }]
}

// ==================== Mounted ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => { if (messageIndex < loadingMessages.length - 1) messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }, 400)
  const progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(messageInterval); clearInterval(progressInterval); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; fetchGateways() }, 400)
  }, 2000)

  // Simulate periodic telegrams
  setInterval(() => {
    if (showMonitor && selectedGateway.value) {
      const types = ['read', 'write', 'response']
      const groups = groupAddresses.value
      if (groups.length > 0) {
        const randomGroup = groups[Math.floor(Math.random() * groups.length)]
        addTelegram({
          time: new Date().toLocaleTimeString(),
          source: `1.1.${Math.floor(Math.random() * 100)}`,
          destination: randomGroup.groupAddress,
          data: 'GroupValue Write',
          value: randomGroup.dataType === 'temperature' ? `${(Math.random() * 30 + 10).toFixed(1)}°C` : Math.random() > 0.5 ? 'ON' : 'OFF',
          type: types[Math.floor(Math.random() * types.length)]
        })
      }
    }
  }, 5000)
})
</script>

<style scoped lang="scss">
/* Loading screen styles (same as previous) */
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
.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}
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

/* Main page styles */
.knx-page {
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

.gateways-card, .group-addresses-card, .monitor-card { margin-bottom: 20px; }
.gateways-card .card-header, .group-addresses-card .card-header, .monitor-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.gateways-card .table-actions, .group-addresses-card .group-actions, .monitor-card .monitor-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.group-address { font-family: monospace; font-size: 13px; background: #f5f7fa; padding: 2px 6px; border-radius: 4px; }
.group-value { font-weight: 500; color: #409eff; }
.group-address-preview { font-family: monospace; font-size: 14px; font-weight: 600; color: #409eff; }

.group-footer { margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }

.monitor-container {
  .monitor-filter {
    display: flex;
    gap: 16px;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
  }
  .monitor-messages {
    height: 300px;
    overflow-y: auto;
    background: #1e1e1e;
    border-radius: 8px;
    padding: 8px;
    font-family: monospace;
    font-size: 12px;
  }
  .monitor-message {
    margin-bottom: 6px;
    padding: 6px 8px;
    border-radius: 4px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    &.read { background: #2d2d2d; border-left: 3px solid #409eff; }
    &.write { background: #2d2d2d; border-left: 3px solid #e6a23c; }
    &.response { background: #2d2d2d; border-left: 3px solid #67c23a; }
    .message-time { color: #909399; font-size: 11px; }
    .message-source { color: #e6a23c; }
    .message-dest { color: #409eff; }
    .message-data { color: #d4d4d4; }
    .message-value { color: #67c23a; font-weight: 500; }
  }
  .monitor-empty { padding: 40px; text-align: center; }
}

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.gateway-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.write-address, .write-current { font-family: monospace; font-size: 13px; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>