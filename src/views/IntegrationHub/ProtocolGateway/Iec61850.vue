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
        <div class="loading-tip">IEC 61850 Gateway Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="iec61850-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>IEC 61850</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>IEC 61850 Gateway Management</h1>
        <p class="description">Manage IEC 61850 IED connections, data models, GOOSE/SMV messages, and substation automation</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export SCL
        </el-button>
        <el-button type="primary" @click="openAddIEDDialog">
          <el-icon><Plus /></el-icon>
          Add IED
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

    <!-- IEC 61850 IEDs Table -->
    <el-card class="ieds-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>IEDs (Intelligent Electronic Devices)</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Connected" value="Connected" />
              <el-option label="Disconnected" value="Disconnected" />
              <el-option label="Warning" value="Warning" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchIEDs" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedIEDs" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="IED Name" min-width="140" show-overflow-tooltip />
        <el-table-column prop="iedName" label="IED Identifier" width="140" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="port" label="Port" width="80" />
        <el-table-column prop="manufacturer" label="Manufacturer" width="130" />
        <el-table-column prop="dataSetCount" label="Data Sets" width="90" align="center" />
        <el-table-column prop="reportCount" label="Reports" width="80" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Connected' ? 'success' : row.status === 'Warning' ? 'warning' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Connected' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastSeen" label="Last Seen" width="150" />
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDataModel(row)">Data Model</el-button>
            <el-button link type="success" size="small" @click="viewDataSets(row)">Data Sets</el-button>
            <el-button link type="info" size="small" @click="testConnection(row)">Test</el-button>
            <el-button link type="danger" size="small" @click="deleteIED(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredIEDs.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Data Model Browser Section -->
    <el-card class="datamodel-card" shadow="hover" v-if="selectedIED">
      <template #header>
        <div class="card-header">
          <span>Data Model - {{ selectedIED.name }} ({{ selectedIED.iedName }})</span>
          <div class="datamodel-actions">
            <el-input
                v-model="dataModelSearch"
                placeholder="Search data objects"
                prefix-icon="Search"
                clearable
                size="small"
                style="width: 200px"
            />
            <el-button size="small" @click="refreshDataModel">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button size="small" type="primary" @click="importSCL">
              <el-icon><Download /></el-icon> Import SCL
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <div class="datamodel-tree">
            <el-tree
                ref="dataModelTreeRef"
                :data="dataModelTree"
                :props="treeProps"
                node-key="reference"
                default-expand-all
                highlight-current
                @node-click="handleDataNodeClick"
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <el-icon :color="getNodeColor(data.type)">
                    <component :is="getNodeIcon(data.type)" />
                  </el-icon>
                  <span>{{ node.label }}</span>
                  <el-tag v-if="data.type" :type="getDataNodeTag(data.type)" size="small" class="node-tag">{{ data.type }}</el-tag>
                </span>
              </template>
            </el-tree>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="data-details" v-if="selectedDataNode">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="Reference">{{ selectedDataNode.reference }}</el-descriptions-item>
              <el-descriptions-item label="Name">{{ selectedDataNode.name }}</el-descriptions-item>
              <el-descriptions-item label="Type">
                <el-tag :type="getDataNodeTag(selectedDataNode.type)" size="small">{{ selectedDataNode.type }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="Data Type" v-if="selectedDataNode.dataType">{{ selectedDataNode.dataType }}</el-descriptions-item>
              <el-descriptions-item label="Value" v-if="selectedDataNode.value !== undefined">
                <span class="data-value">{{ selectedDataNode.value }} {{ selectedDataNode.unit || '' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="FC" v-if="selectedDataNode.fc">{{ selectedDataNode.fc }}</el-descriptions-item>
              <el-descriptions-item label="Description">{{ selectedDataNode.description || 'N/A' }}</el-descriptions-item>
            </el-descriptions>
            <div class="data-actions" v-if="selectedDataNode.type === 'DA'">
              <el-button type="primary" size="small" @click="readDataValue(selectedDataNode)">Read Value</el-button>
              <el-button v-if="selectedDataNode.writable" size="small" @click="writeDataValue(selectedDataNode)">Write Value</el-button>
              <el-button size="small" @click="subscribeData(selectedDataNode)">Subscribe</el-button>
            </div>
          </div>
          <div class="data-empty" v-else>
            <el-empty description="Select a data object from the tree" :image-size="80" />
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- GOOSE/SMV Monitoring Section -->
    <el-card class="messaging-card" shadow="hover" v-if="showMessaging">
      <template #header>
        <div class="card-header">
          <span>GOOSE / SMV Messages - {{ selectedIED?.name }}</span>
          <div class="messaging-actions">
            <el-radio-group v-model="messageType" size="small">
              <el-radio-button value="goose">GOOSE</el-radio-button>
              <el-radio-button value="smv">SMV</el-radio-button>
              <el-radio-button value="both">Both</el-radio-button>
            </el-radio-group>
            <el-button size="small" @click="clearMessages">Clear</el-button>
            <el-button size="small" @click="showMessaging = false">Close</el-button>
          </div>
        </div>
      </template>

      <div class="messages-container">
        <el-table :data="filteredMessages" stripe size="small" max-height="300">
          <el-table-column prop="time" label="Time" width="120" />
          <el-table-column prop="type" label="Type" width="80">
            <template #default="{ row }">
              <el-tag :type="row.type === 'GOOSE' ? 'warning' : 'primary'" size="small">{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="gocbRef" label="GoCB Reference" min-width="200" show-overflow-tooltip />
          <el-table-column prop="datSet" label="Data Set" min-width="180" show-overflow-tooltip />
          <el-table-column prop="stNum" label="StNum" width="70" align="center" />
          <el-table-column prop="sqNum" label="SqNum" width="70" align="center" />
          <el-table-column prop="value" label="Value" min-width="150" show-overflow-tooltip />
        </el-table>
        <div v-if="filteredMessages.length === 0" class="messages-empty">
          <el-empty description="No messages received" :image-size="60" />
        </div>
      </div>
    </el-card>

    <!-- Add/Edit IED Dialog -->
    <el-dialog v-model="iedDialogVisible" :title="dialogMode === 'add' ? 'Add IED' : 'Edit IED'" width="650px" destroy-on-close class="ied-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Connection Settings" name="basic">
          <el-form :model="iedForm" :rules="iedRules" ref="iedFormRef" label-width="140px">
            <el-form-item label="IED Name" prop="name">
              <el-input v-model="iedForm.name" placeholder="Enter IED name" />
            </el-form-item>
            <el-form-item label="IED Identifier" prop="iedName">
              <el-input v-model="iedForm.iedName" placeholder="e.g., PCS1234" />
            </el-form-item>
            <el-form-item label="IP Address" prop="ipAddress">
              <el-input v-model="iedForm.ipAddress" placeholder="192.168.1.100" />
            </el-form-item>
            <el-form-item label="Port" prop="port">
              <el-input-number v-model="iedForm.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Manufacturer" prop="manufacturer">
              <el-input v-model="iedForm.manufacturer" placeholder="Siemens, ABB, GE, etc." />
            </el-form-item>
            <el-form-item label="Model" prop="model">
              <el-input v-model="iedForm.model" placeholder="Device model" />
            </el-form-item>
            <el-form-item label="Firmware Version" prop="firmware">
              <el-input v-model="iedForm.firmware" placeholder="1.0" />
            </el-form-item>
            <el-form-item label="Description" prop="description">
              <el-input v-model="iedForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="GOOSE/SMV" name="messaging">
          <el-form label-width="140px">
            <el-form-item label="Enable GOOSE">
              <el-switch v-model="iedForm.enableGOOSE" />
            </el-form-item>
            <el-form-item label="GOOSE MAC Address" v-if="iedForm.enableGOOSE">
              <el-input v-model="iedForm.gooseMac" placeholder="01:0C:CD:01:00:01" />
            </el-form-item>
            <el-form-item label="GOOSE VLAN ID" v-if="iedForm.enableGOOSE">
              <el-input-number v-model="iedForm.gooseVlan" :min="0" :max="4095" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Enable SMV">
              <el-switch v-model="iedForm.enableSMV" />
            </el-form-item>
            <el-form-item label="SMV MAC Address" v-if="iedForm.enableSMV">
              <el-input v-model="iedForm.smvMac" placeholder="01:0C:CD:04:00:01" />
            </el-form-item>
            <el-form-item label="Sample Rate (Hz)" v-if="iedForm.enableSMV">
              <el-input-number v-model="iedForm.sampleRate" :min="50" :max="4800" style="width: 100%" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="150px">
            <el-form-item label="Connection Timeout (ms)">
              <el-input-number v-model="iedForm.timeout" :min="1000" :max="60000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Auto Reconnect">
              <el-switch v-model="iedForm.autoReconnect" />
            </el-form-item>
            <el-form-item label="Buffered Reporting">
              <el-switch v-model="iedForm.bufferedReporting" />
            </el-form-item>
            <el-form-item label="Enable Logging">
              <el-switch v-model="iedForm.enableLogging" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="iedDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testIEDConnection" :loading="testing">
          Test Connection
        </el-button>
        <el-button type="success" @click="saveIED">
          Save IED
        </el-button>
      </template>
    </el-dialog>

    <!-- Data Set Dialog -->
    <el-dialog v-model="dataSetDialogVisible" title="Data Sets" width="700px" destroy-on-close>
      <div class="data-sets" v-if="selectedIED">
        <el-table :data="dataSets" stripe size="small">
          <el-table-column prop="name" label="Data Set Name" min-width="200" show-overflow-tooltip />
          <el-table-column prop="reference" label="Reference" min-width="250" show-overflow-tooltip />
          <el-table-column prop="memberCount" label="Members" width="80" align="center" />
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewDataSetMembers(row)">View Members</el-button>
              <el-button link type="success" size="small" @click="subscribeDataSet(row)">Subscribe</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="dataSetDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Write Value Dialog -->
    <el-dialog v-model="writeDialogVisible" title="Write Value" width="450px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="Data Object">
          <code class="write-ref">{{ writeNode?.reference }}</code>
        </el-form-item>
        <el-form-item label="Current Value">
          <span class="write-current">{{ writeNode?.value }} {{ writeNode?.unit || '' }}</span>
        </el-form-item>
        <el-form-item label="Data Type">
          <el-tag size="small">{{ writeNode?.dataType }}</el-tag>
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
            :title="testResult.success ? 'IED Connected' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>IED:</strong> {{ testResult.details.iedName }}</p>
          <p><strong>Manufacturer:</strong> {{ testResult.details.manufacturer }}</p>
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
  Delete, Connection, Edit, Grid, DataAnalysis, Monitor, Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing IEC 61850 gateway...', 'Loading IEDs...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const testing = ref(false)
const iedDialogVisible = ref(false)
const dataSetDialogVisible = ref(false)
const testDialogVisible = ref(false)
const writeDialogVisible = ref(false)
const showMessaging = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedIED = ref<any>(null)
const selectedDataNode = ref<any>(null)
const writeNode = ref<any>(null)
const searchKeyword = ref('')
const dataModelSearch = ref('')
const statusFilter = ref('')
const messageType = ref('both')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const writeValue = ref('')

const iedFormRef = ref()
const dataModelTreeRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// Mock messages data
const gooseMessages = ref<any[]>([])
const smvMessages = ref<any[]>([])

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'IEDs', value: '6', trend: 2, icon: 'Connection', bgColor: '#409eff', key: 'ieds', subTitle: 'Connected: 5' },
  { title: 'Data Objects', value: '2,456', trend: 8, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'objects', subTitle: 'Active: 2,380' },
  { title: 'GOOSE/SMV', value: '24', trend: 4, icon: 'Message', bgColor: '#e6a23c', key: 'messages', subTitle: 'Active: 22' },
  { title: 'Reports', value: '48', trend: 6, icon: 'Document', bgColor: '#f56c6c', key: 'reports', subTitle: 'Buffered: 32' }
])

const ieds = ref([
  { id: 1, name: 'Bay Controller 1', iedName: 'BAY1', ipAddress: '192.168.1.100', port: 102, manufacturer: 'Siemens', dataSetCount: 8, reportCount: 12, status: 'Connected', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'Protection Relay P1', iedName: 'PROT1', ipAddress: '192.168.1.101', port: 102, manufacturer: 'ABB', dataSetCount: 6, reportCount: 8, status: 'Connected', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'RTU Gateway', iedName: 'RTU1', ipAddress: '192.168.1.102', port: 102, manufacturer: 'GE', dataSetCount: 12, reportCount: 16, status: 'Connected', lastSeen: '2024-01-20 10:32:00' },
  { id: 4, name: 'Breaker Controller', iedName: 'BRK1', ipAddress: '192.168.1.103', port: 102, manufacturer: 'Schneider', dataSetCount: 4, reportCount: 6, status: 'Warning', lastSeen: '2024-01-20 10:25:00' },
  { id: 5, name: 'Metering IED', iedName: 'MET1', ipAddress: '192.168.1.104', port: 102, manufacturer: 'Elster', dataSetCount: 10, reportCount: 5, status: 'Connected', lastSeen: '2024-01-20 10:29:00' }
])

// Data model tree mock data
const dataModelTree = ref([
  {
    reference: 'BAY1',
    name: 'BAY1',
    type: 'LD',
    children: [
      {
        reference: 'BAY1/LLN0',
        name: 'LLN0',
        type: 'LN',
        children: [
          { reference: 'BAY1/LLN0.Mod', name: 'Mod', type: 'DO', dataType: 'INC', value: 1, fc: 'ST', description: 'Mode' },
          { reference: 'BAY1/LLN0.Health', name: 'Health', type: 'DO', dataType: 'ENS', value: 'Ok', fc: 'ST', description: 'Health status' }
        ]
      },
      {
        reference: 'BAY1/XCBR1',
        name: 'XCBR1',
        type: 'LN',
        children: [
          { reference: 'BAY1/XCBR1.Pos', name: 'Pos', type: 'DO', dataType: 'DPC', value: 'ON', fc: 'ST', writable: true, description: 'Breaker position' },
          { reference: 'BAY1/XCBR1.BlkOpn', name: 'BlkOpn', type: 'DO', dataType: 'SPC', value: false, fc: 'CO', description: 'Block open' }
        ]
      }
    ]
  },
  {
    reference: 'PROT1',
    name: 'PROT1',
    type: 'LD',
    children: [
      {
        reference: 'PROT1/PTOC1',
        name: 'PTOC1',
        type: 'LN',
        children: [
          { reference: 'PROT1/PTOC1.Str', name: 'Str', type: 'DO', dataType: 'ACT', value: false, fc: 'ST', description: 'Start' },
          { reference: 'PROT1/PTOC1.Op', name: 'Op', type: 'DO', dataType: 'ACT', value: false, fc: 'ST', description: 'Operate' }
        ]
      }
    ]
  }
])

const dataSets = ref([
  { name: 'Measurements', reference: 'BAY1/LLN0.Measurements', memberCount: 12 },
  { name: 'Status Values', reference: 'BAY1/LLN0.Status', memberCount: 8 },
  { name: 'Protection Events', reference: 'PROT1/LLN0.Events', memberCount: 6 }
])

const treeProps = { children: 'children', label: 'name' }

// ==================== Computed ====================
const filteredIEDs = computed(() => {
  let filtered = [...ieds.value]
  if (searchKeyword.value) filtered = filtered.filter(i => i.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || i.ipAddress.includes(searchKeyword.value))
  if (statusFilter.value) filtered = filtered.filter(i => i.status === statusFilter.value)
  return filtered
})

const paginatedIEDs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredIEDs.value.slice(start, end)
})

const filteredMessages = computed(() => {
  let messages: any[] = []
  if (messageType.value === 'goose' || messageType.value === 'both') messages.push(...gooseMessages.value)
  if (messageType.value === 'smv' || messageType.value === 'both') messages.push(...smvMessages.value)
  return messages.sort((a, b) => b.time.localeCompare(a.time))
})

// ==================== Helper Methods ====================
const getNodeIcon = (type: string) => {
  const map: Record<string, string> = {
    'LD': 'Grid',
    'LN': 'Monitor',
    'DO': 'DataAnalysis',
    'DA': 'Document'
  }
  return map[type] || 'Document'
}

const getNodeColor = (type: string) => {
  const map: Record<string, string> = {
    'LD': '#409eff',
    'LN': '#67c23a',
    'DO': '#e6a23c',
    'DA': '#f56c6c'
  }
  return map[type] || '#909399'
}

const getDataNodeTag = (type: string) => {
  const map: Record<string, string> = {
    'LD': 'primary',
    'LN': 'success',
    'DO': 'warning',
    'DA': 'danger'
  }
  return map[type] || 'info'
}

const addGOOSEMessage = () => {
  const stNum = Math.floor(Math.random() * 100)
  gooseMessages.value.unshift({
    time: new Date().toLocaleTimeString(),
    type: 'GOOSE',
    gocbRef: 'BAY1/LLN0.gcb1',
    datSet: 'BAY1/LLN0.Measurements',
    stNum: stNum,
    sqNum: Math.floor(Math.random() * 100),
    value: `Position: ${Math.random() > 0.5 ? 'ON' : 'OFF'}, Current: ${(Math.random() * 1000).toFixed(1)}A`
  })
  if (gooseMessages.value.length > 50) gooseMessages.value.pop()
}

const addSMVMessage = () => {
  smvMessages.value.unshift({
    time: new Date().toLocaleTimeString(),
    type: 'SMV',
    gocbRef: 'MU1/LLN0.svcb1',
    datSet: 'MU1/LLN0.Samples',
    stNum: 0,
    sqNum: Math.floor(Math.random() * 100),
    value: `Ia: ${(Math.random() * 5000).toFixed(1)}A, Ib: ${(Math.random() * 5000).toFixed(1)}A, Ic: ${(Math.random() * 5000).toFixed(1)}A`
  })
  if (smvMessages.value.length > 50) smvMessages.value.pop()
}

// ==================== IED Methods ====================
const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting SCL configuration...')
const fetchIEDs = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('IEDs refreshed') }, 500) }

const openAddIEDDialog = () => {
  dialogMode.value = 'add'
  Object.assign(iedForm, {
    id: null, name: '', iedName: '', ipAddress: '', port: 102, manufacturer: '', model: '', firmware: '', description: '',
    enableGOOSE: false, gooseMac: '01:0C:CD:01:00:01', gooseVlan: 0,
    enableSMV: false, smvMac: '01:0C:CD:04:00:01', sampleRate: 4000,
    timeout: 5000, autoReconnect: true, bufferedReporting: false, enableLogging: true
  })
  iedDialogVisible.value = true
}

const editIED = (ied: any) => {
  dialogMode.value = 'edit'
  Object.assign(iedForm, ied)
  iedDialogVisible.value = true
}

const testIEDConnection = () => {
  testing.value = true
  setTimeout(() => {
    testing.value = false
    testResult.success = true
    testResult.message = 'Successfully connected to IED'
    testResult.details = {
      iedName: iedForm.iedName,
      manufacturer: iedForm.manufacturer || 'Siemens',
      firmware: iedForm.firmware || '2.1',
      responseTime: 35
    }
    testDialogVisible.value = true
  }, 1500)
}

const saveIED = async () => {
  if (!iedFormRef.value) return
  await iedFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'IED added successfully' : 'IED updated successfully')
      iedDialogVisible.value = false
    }
  })
}

const deleteIED = (ied: any) => {
  ElMessageBox.confirm(`Delete IED "${ied.name}"? This will also remove all data model configurations.`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const index = ieds.value.findIndex(i => i.id === ied.id)
    if (index !== -1) { ieds.value.splice(index, 1); if (selectedIED.value?.id === ied.id) selectedIED.value = null; ElMessage.success(`Deleted: ${ied.name}`) }
  }).catch(() => {})
}

const testConnection = (ied: any) => {
  ElMessage.info(`Testing connection to ${ied.name}...`)
  setTimeout(() => { ElMessage.success(`${ied.name} is ${ied.status}`) }, 1000)
}

const viewDataModel = (ied: any) => {
  selectedIED.value = ied
  selectedDataNode.value = null
  refreshDataModel()
}

const viewDataSets = (ied: any) => {
  selectedIED.value = ied
  dataSetDialogVisible.value = true
}

const refreshDataModel = () => {
  ElMessage.success('Data model refreshed')
}

const importSCL = () => {
  ElMessage.info('Import SCL file dialog would open here')
}

// ==================== Data Model Methods ====================
const handleDataNodeClick = (data: any) => {
  selectedDataNode.value = data
}

const readDataValue = (node: any) => {
  ElMessage.info(`Reading ${node.reference}...`)
  setTimeout(() => {
    const newValue = node.dataType === 'DPC' ? (Math.random() > 0.5 ? 'ON' : 'OFF') : Math.random() * 100
    node.value = newValue
    ElMessage.success(`${node.name}: ${newValue}`)
  }, 500)
}

const writeDataValue = (node: any) => {
  writeNode.value = node
  writeValue.value = node.value?.toString() || ''
  writeDialogVisible.value = true
}

const submitWrite = () => {
  if (writeNode.value) {
    writeNode.value.value = writeValue.value
    ElMessage.success(`Wrote ${writeValue.value} to ${writeNode.value.name}`)
    writeDialogVisible.value = false
  }
}

const subscribeData = (node: any) => {
  ElMessage.success(`Subscribed to ${node.reference}`)
}

const viewDataSetMembers = (dataSet: any) => {
  ElMessage.info(`Viewing members of ${dataSet.name}`)
}

const subscribeDataSet = (dataSet: any) => {
  ElMessage.success(`Subscribed to data set ${dataSet.name}`)
}

const clearMessages = () => {
  gooseMessages.value = []
  smvMessages.value = []
  ElMessage.success('Messages cleared')
}

// ==================== Forms ====================
const iedForm = reactive({
  id: null, name: '', iedName: '', ipAddress: '', port: 102, manufacturer: '', model: '', firmware: '', description: '',
  enableGOOSE: false, gooseMac: '01:0C:CD:01:00:01', gooseVlan: 0,
  enableSMV: false, smvMac: '01:0C:CD:04:00:01', sampleRate: 4000,
  timeout: 5000, autoReconnect: true, bufferedReporting: false, enableLogging: true
})

const iedRules = {
  name: [{ required: true, message: 'Please enter IED name', trigger: 'blur' }],
  iedName: [{ required: true, message: 'Please enter IED identifier', trigger: 'blur' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }]
}

// ==================== Mounted ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => { if (messageIndex < loadingMessages.length - 1) messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }, 400)
  const progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(messageInterval); clearInterval(progressInterval); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; fetchIEDs() }, 400)
  }, 2000)

  // Simulate periodic GOOSE and SMV messages
  setInterval(() => { addGOOSEMessage() }, 8000)
  setInterval(() => { addSMVMessage() }, 12000)
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
.iec61850-page {
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

.ieds-card, .datamodel-card, .messaging-card { margin-bottom: 20px; }
.ieds-card .card-header, .datamodel-card .card-header, .messaging-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.ieds-card .table-actions, .datamodel-card .datamodel-actions, .messaging-card .messaging-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.datamodel-tree {
  height: 450px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 8px;
}
.tree-node { display: flex; align-items: center; gap: 8px; }
.tree-node .node-tag { margin-left: auto; }

.data-details { padding: 16px; background: #f5f7fa; border-radius: 8px; min-height: 450px; }
.data-value { font-size: 18px; font-weight: 600; color: #409eff; }
.data-actions { margin-top: 16px; display: flex; gap: 8px; }
.data-empty { padding: 40px; text-align: center; }

.messages-container { min-height: 300px; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.ied-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.write-ref, .write-current { font-family: monospace; font-size: 13px; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>