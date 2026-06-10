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
        <div class="loading-tip">SNMP Gateway Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="snmp-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>SNMP</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>SNMP Gateway Management</h1>
        <p class="description">Manage SNMP devices, OID queries, and network monitoring data collection</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export MIB
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

    <!-- SNMP Devices Table -->
    <el-card class="devices-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>SNMP Devices</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="versionFilter" placeholder="SNMP Version" clearable style="width: 140px">
              <el-option label="v1" value="v1" />
              <el-option label="v2c" value="v2c" />
              <el-option label="v3" value="v3" />
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
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="snmpVersion" label="SNMP Version" width="100">
          <template #default="{ row }">
            <el-tag :type="row.snmpVersion === 'v3' ? 'primary' : 'success'" size="small">{{ row.snmpVersion }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="community" label="Community" width="100" v-if="filteredDevices.some(d => d.snmpVersion !== 'v3')">
          <template #default="{ row }">
            <span class="community-value">{{ row.community || '***' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="oidCount" label="OIDs" width="80" align="center" />
        <el-table-column prop="pollInterval" label="Poll Interval" width="100" align="center">
          <template #default="{ row }">
            {{ row.pollInterval }}s
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : row.status === 'Warning' ? 'warning' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Online' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastPoll" label="Last Poll" width="150" />
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewOIDs(row)">OIDs ({{ row.oidCount }})</el-button>
            <el-button link type="success" size="small" @click="walkDevice(row)">Walk</el-button>
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

    <!-- OID Browser Section -->
    <el-card class="oid-card" shadow="hover" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>OID Browser - {{ selectedDevice.name }}</span>
          <div class="oid-actions">
            <el-input
                v-model="oidSearch"
                placeholder="Search OID or description"
                prefix-icon="Search"
                clearable
                size="small"
                style="width: 200px"
            />
            <el-button size="small" type="primary" @click="addOID">
              <el-icon><Plus /></el-icon> Add OID
            </el-button>
            <el-button size="small" @click="refreshOIDs">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredOIDs" stripe size="small" v-loading="oidsLoading">
        <el-table-column prop="oid" label="OID" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="oid-code">{{ row.oid }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="100" />
        <el-table-column prop="currentValue" label="Current Value" width="150">
          <template #default="{ row }">
            <span class="oid-value">{{ row.currentValue || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="pollInterval" label="Interval" width="80" align="center" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="getOID(row)">Get</el-button>
            <el-button link type="success" size="small" @click="editOID(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteOID(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="oid-footer" v-if="selectedDevice">
        <el-button type="primary" @click="bulkPoll">Poll Selected</el-button>
        <span class="oid-info">Total OIDs: {{ oidList.length }} | Polling: {{ pollingActive ? 'Active' : 'Stopped' }}</span>
      </div>
    </el-card>

    <!-- MIB Tree Section -->
    <el-card class="mib-card" shadow="hover" v-if="showMibTree">
      <template #header>
        <div class="card-header">
          <span>MIB Tree - {{ selectedDevice?.name }}</span>
          <div class="mib-actions">
            <el-input
                v-model="mibSearch"
                placeholder="Search nodes"
                prefix-icon="Search"
                clearable
                size="small"
                style="width: 200px"
            />
            <el-button size="small" @click="showMibTree = false">Close</el-button>
          </div>
        </div>
      </template>

      <div class="mib-tree-container">
        <el-tree
            ref="mibTreeRef"
            :data="mibTreeData"
            :props="treeProps"
            node-key="oid"
            highlight-current
            @node-click="handleMibNodeClick"
        >
          <template #default="{ node, data }">
            <span class="mib-node">
              <el-icon><component :is="data.nodeClass === 'table' ? 'Grid' : 'DataAnalysis'" /></el-icon>
              <span>{{ node.label }}</span>
              <code class="mib-oid">{{ data.oid }}</code>
            </span>
          </template>
        </el-tree>
      </div>
    </el-card>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="deviceDialogVisible" :title="dialogMode === 'add' ? 'Add SNMP Device' : 'Edit SNMP Device'" width="600px" destroy-on-close class="device-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Basic Settings" name="basic">
          <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="120px">
            <el-form-item label="Device Name" prop="name">
              <el-input v-model="deviceForm.name" placeholder="Enter device name" />
            </el-form-item>
            <el-form-item label="IP Address" prop="ipAddress">
              <el-input v-model="deviceForm.ipAddress" placeholder="192.168.1.100" />
            </el-form-item>
            <el-form-item label="Port" prop="port">
              <el-input-number v-model="deviceForm.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
            <el-form-item label="SNMP Version" prop="snmpVersion">
              <el-radio-group v-model="deviceForm.snmpVersion">
                <el-radio value="v1">v1</el-radio>
                <el-radio value="v2c">v2c</el-radio>
                <el-radio value="v3">v3</el-radio>
              </el-radio-group>
            </el-form-item>

            <template v-if="deviceForm.snmpVersion !== 'v3'">
              <el-form-item label="Community" prop="community">
                <el-input v-model="deviceForm.community" placeholder="public" />
              </el-form-item>
            </template>

            <template v-if="deviceForm.snmpVersion === 'v3'">
              <el-form-item label="Security Name" prop="securityName">
                <el-input v-model="deviceForm.securityName" placeholder="Username" />
              </el-form-item>
              <el-form-item label="Authentication Protocol" prop="authProtocol">
                <el-select v-model="deviceForm.authProtocol" style="width: 100%">
                  <el-option label="MD5" value="MD5" />
                  <el-option label="SHA" value="SHA" />
                  <el-option label="SHA224" value="SHA224" />
                  <el-option label="SHA256" value="SHA256" />
                </el-select>
              </el-form-item>
              <el-form-item label="Authentication Password" prop="authPassword">
                <el-input v-model="deviceForm.authPassword" type="password" placeholder="Auth password" />
              </el-form-item>
              <el-form-item label="Privacy Protocol" prop="privProtocol">
                <el-select v-model="deviceForm.privProtocol" style="width: 100%">
                  <el-option label="DES" value="DES" />
                  <el-option label="AES" value="AES" />
                  <el-option label="AES192" value="AES192" />
                  <el-option label="AES256" value="AES256" />
                </el-select>
              </el-form-item>
              <el-form-item label="Privacy Password" prop="privPassword">
                <el-input v-model="deviceForm.privPassword" type="password" placeholder="Privacy password" />
              </el-form-item>
            </template>

            <el-form-item label="Poll Interval (seconds)" prop="pollInterval">
              <el-input-number v-model="deviceForm.pollInterval" :min="10" :max="3600" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Timeout (ms)" prop="timeout">
              <el-input-number v-model="deviceForm.timeout" :min="100" :max="30000" :step="100" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Retries" prop="retries">
              <el-input-number v-model="deviceForm.retries" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Description" prop="description">
              <el-input v-model="deviceForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="150px">
            <el-form-item label="Engine ID">
              <el-input v-model="deviceForm.engineId" placeholder="Optional engine ID" />
            </el-form-item>
            <el-form-item label="Context Name">
              <el-input v-model="deviceForm.contextName" placeholder="Optional context name" />
            </el-form-item>
            <el-form-item label="Auto Discover">
              <el-switch v-model="deviceForm.autoDiscover" />
              <span style="margin-left: 8px; color: #909399">Automatically discover OIDs</span>
            </el-form-item>
            <el-form-item label="Enable Trap Receiver">
              <el-switch v-model="deviceForm.enableTrap" />
            </el-form-item>
            <el-form-item label="Trap Port" v-if="deviceForm.enableTrap">
              <el-input-number v-model="deviceForm.trapPort" :min="1" :max="65535" style="width: 100%" />
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

    <!-- Add/Edit OID Dialog -->
    <el-dialog v-model="oidDialogVisible" :title="dialogMode === 'add' ? 'Add OID' : 'Edit OID'" width="550px" destroy-on-close>
      <el-form :model="oidForm" :rules="oidRules" ref="oidFormRef" label-width="120px">
        <el-form-item label="OID" prop="oid">
          <el-input v-model="oidForm.oid" placeholder=".1.3.6.1.2.1.1.1.0" />
        </el-form-item>
        <el-form-item label="Name" prop="name">
          <el-input v-model="oidForm.name" placeholder="sysDescr" />
        </el-form-item>
        <el-form-item label="Type" prop="type">
          <el-select v-model="oidForm.type" style="width: 100%">
            <el-option label="Integer" value="Integer" />
            <el-option label="String" value="String" />
            <el-option label="Octet String" value="OctetString" />
            <el-option label="OID" value="OID" />
            <el-option label="IpAddress" value="IpAddress" />
            <el-option label="Counter32" value="Counter32" />
            <el-option label="Counter64" value="Counter64" />
            <el-option label="Gauge32" value="Gauge32" />
            <el-option label="TimeTicks" value="TimeTicks" />
          </el-select>
        </el-form-item>
        <el-form-item label="Unit" prop="unit">
          <el-input v-model="oidForm.unit" placeholder="°C, %, ms, etc." />
        </el-form-item>
        <el-form-item label="Poll Interval (s)" prop="pollInterval">
          <el-input-number v-model="oidForm.pollInterval" :min="5" :max="3600" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="oidForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="oidDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testOID">Test OID</el-button>
        <el-button type="success" @click="saveOID">Save</el-button>
      </template>
    </el-dialog>

    <!-- SNMP Walk Dialog -->
    <el-dialog v-model="walkDialogVisible" title="SNMP Walk Results" width="800px" destroy-on-close>
      <div class="walk-results" v-loading="walkLoading">
        <el-table :data="walkResults" stripe size="small" max-height="400">
          <el-table-column prop="oid" label="OID" min-width="250" show-overflow-tooltip>
            <template #default="{ row }">
              <code class="walk-oid">{{ row.oid }}</code>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="Value" min-width="200" show-overflow-tooltip />
          <el-table-column prop="type" label="Type" width="100" />
          <el-table-column label="Action" width="80">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="addWalkOID(row)">Add</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="walkResults.length === 0 && !walkLoading" class="walk-empty">
          <el-empty description="No results" :image-size="80" />
        </div>
      </div>
      <template #footer>
        <el-button @click="walkDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportWalkResults">Export</el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Device Reachable' : 'Device Unreachable'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Device:</strong> {{ testResult.details.device }}</p>
          <p><strong>System Description:</strong> {{ testResult.details.sysDescr }}</p>
          <p><strong>Up Time:</strong> {{ testResult.details.upTime }}</p>
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
  Delete, Connection, Edit, Grid, DataAnalysis
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing SNMP gateway...', 'Loading devices...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const oidsLoading = ref(false)
const walkLoading = ref(false)
const testing = ref(false)
const pollingActive = ref(false)
const deviceDialogVisible = ref(false)
const oidDialogVisible = ref(false)
const testDialogVisible = ref(false)
const walkDialogVisible = ref(false)
const showMibTree = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedDevice = ref<any>(null)
const searchKeyword = ref('')
const oidSearch = ref('')
const mibSearch = ref('')
const versionFilter = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)

const deviceFormRef = ref()
const oidFormRef = ref()
const mibTreeRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })
const walkResults = ref<any[]>([])

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'SNMP Devices', value: '18', trend: 4, icon: 'Connection', bgColor: '#409eff', key: 'devices', subTitle: 'Online: 15' },
  { title: 'Monitored OIDs', value: '245', trend: 12, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'oids', subTitle: 'Active: 238' },
  { title: 'Poll Rate', value: '1,234/s', trend: 8, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'rate', subTitle: 'Peak: 1,567' },
  { title: 'Traps Received', value: '89', trend: -5, icon: 'Message', bgColor: '#f56c6c', key: 'traps', subTitle: 'Last 24h' }
])

const devices = ref([
  { id: 1, name: 'Core Router', ipAddress: '192.168.1.1', snmpVersion: 'v2c', community: 'public', oidCount: 24, pollInterval: 60, status: 'Online', lastPoll: '2024-01-20 10:30:00' },
  { id: 2, name: 'Switch-01', ipAddress: '192.168.1.2', snmpVersion: 'v2c', community: 'public', oidCount: 18, pollInterval: 60, status: 'Online', lastPoll: '2024-01-20 10:30:00' },
  { id: 3, name: 'UPS-01', ipAddress: '192.168.1.10', snmpVersion: 'v1', community: 'private', oidCount: 32, pollInterval: 30, status: 'Online', lastPoll: '2024-01-20 10:29:00' },
  { id: 4, name: 'HVAC Controller', ipAddress: '192.168.1.20', snmpVersion: 'v3', oidCount: 45, pollInterval: 120, status: 'Warning', lastPoll: '2024-01-20 10:28:00' },
  { id: 5, name: 'Security Gateway', ipAddress: '192.168.1.5', snmpVersion: 'v2c', community: 'public', oidCount: 12, pollInterval: 60, status: 'Offline', lastPoll: '2024-01-20 08:15:00' }
])

const oidsMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, oid: '.1.3.6.1.2.1.1.1.0', name: 'sysDescr', type: 'String', currentValue: 'Cisco IOS', unit: '', pollInterval: 300, description: 'System description' },
    { id: 2, oid: '.1.3.6.1.2.1.1.3.0', name: 'sysUpTime', type: 'TimeTicks', currentValue: '124 days', unit: '', pollInterval: 60, description: 'System uptime' },
    { id: 3, oid: '.1.3.6.1.2.1.2.2.1.10.1', name: 'ifInOctets', type: 'Counter32', currentValue: '1,234,567', unit: 'bytes', pollInterval: 30, description: 'Inbound traffic' }
  ],
  2: [
    { id: 4, oid: '.1.3.6.1.2.1.1.1.0', name: 'sysDescr', type: 'String', currentValue: 'Switch OS', unit: '', pollInterval: 300, description: 'System description' }
  ],
  3: [
    { id: 5, oid: '.1.3.6.1.2.1.33.1.1.1.0', name: 'upsBatteryStatus', type: 'Integer', currentValue: '2', unit: '', pollInterval: 30, description: 'Battery status (2=normal)' },
    { id: 6, oid: '.1.3.6.1.2.1.33.1.2.1.0', name: 'upsEstimatedChargeRemaining', type: 'Integer', currentValue: '85', unit: '%', pollInterval: 60, description: 'Battery charge remaining' }
  ]
})

// MIB Tree mock data
const mibTreeData = ref([
  {
    oid: '.1.3.6.1.2.1',
    name: 'mib-2',
    nodeClass: 'table',
    children: [
      { oid: '.1.3.6.1.2.1.1', name: 'system', nodeClass: 'group', children: [
          { oid: '.1.3.6.1.2.1.1.1', name: 'sysDescr', nodeClass: 'object' },
          { oid: '.1.3.6.1.2.1.1.3', name: 'sysUpTime', nodeClass: 'object' }
        ]},
      { oid: '.1.3.6.1.2.1.2', name: 'interfaces', nodeClass: 'group', children: [
          { oid: '.1.3.6.1.2.1.2.2', name: 'ifTable', nodeClass: 'table' }
        ]},
      { oid: '.1.3.6.1.2.1.33', name: 'UPS-MIB', nodeClass: 'group', children: [
          { oid: '.1.3.6.1.2.1.33.1', name: 'upsBattery', nodeClass: 'group' }
        ]}
    ]
  }
])

const treeProps = { children: 'children', label: 'name' }

// Forms
const deviceForm = reactive({
  id: null, name: '', ipAddress: '', port: 161, snmpVersion: 'v2c',
  community: 'public', securityName: '', authProtocol: 'SHA', authPassword: '',
  privProtocol: 'AES', privPassword: '', pollInterval: 60, timeout: 2000, retries: 3,
  description: '', engineId: '', contextName: '', autoDiscover: false, enableTrap: false, trapPort: 162
})

const oidForm = reactive({
  id: null, oid: '', name: '', type: 'String', unit: '', pollInterval: 60, description: ''
})

// Rules
const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }]
}

const oidRules = {
  oid: [{ required: true, message: 'Please enter OID', trigger: 'blur' }],
  name: [{ required: true, message: 'Please enter name', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredDevices = computed(() => {
  let filtered = [...devices.value]
  if (searchKeyword.value) filtered = filtered.filter(d => d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || d.ipAddress.includes(searchKeyword.value))
  if (versionFilter.value) filtered = filtered.filter(d => d.snmpVersion === versionFilter.value)
  if (statusFilter.value) filtered = filtered.filter(d => d.status === statusFilter.value)
  return filtered
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

const oidList = computed(() => oidsMap.value[selectedDevice.value?.id] || [])
const filteredOIDs = computed(() => {
  if (!oidSearch.value) return oidList.value
  return oidList.value.filter(o => o.oid.includes(oidSearch.value) || o.name.toLowerCase().includes(oidSearch.value.toLowerCase()))
})

// ==================== Helper Methods ====================
const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting SNMP configuration...')
const fetchDevices = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Devices refreshed') }, 500) }

const openAddDeviceDialog = () => {
  dialogMode.value = 'add'
  Object.assign(deviceForm, {
    id: null, name: '', ipAddress: '', port: 161, snmpVersion: 'v2c', community: 'public',
    securityName: '', authProtocol: 'SHA', authPassword: '', privProtocol: 'AES', privPassword: '',
    pollInterval: 60, timeout: 2000, retries: 3, description: '', engineId: '', contextName: '',
    autoDiscover: false, enableTrap: false, trapPort: 162
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
    testResult.message = 'Device is reachable via SNMP'
    testResult.details = {
      device: deviceForm.ipAddress,
      sysDescr: 'SNMP Device Simulator v1.0',
      upTime: '14 days, 6 hours, 32 minutes',
      responseTime: 45
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
  ElMessageBox.confirm(`Delete device "${device.name}"? This will also remove all OIDs.`, 'Confirm Delete', {
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

const viewOIDs = (device: any) => {
  selectedDevice.value = device
  refreshOIDs()
}

const walkDevice = (device: any) => {
  selectedDevice.value = device
  walkLoading.value = true
  walkDialogVisible.value = true
  setTimeout(() => {
    walkResults.value = [
      { oid: '.1.3.6.1.2.1.1.1.0', value: 'SNMP Device Simulator v1.0', type: 'String' },
      { oid: '.1.3.6.1.2.1.1.3.0', value: '14 days, 6 hours', type: 'TimeTicks' },
      { oid: '.1.3.6.1.2.1.1.5.0', value: 'Device-001', type: 'String' }
    ]
    walkLoading.value = false
  }, 1500)
}

const refreshOIDs = () => {
  oidsLoading.value = true
  setTimeout(() => { oidsLoading.value = false; ElMessage.success('OIDs refreshed') }, 500)
}

const addOID = () => {
  dialogMode.value = 'add'
  Object.assign(oidForm, { id: null, oid: '', name: '', type: 'String', unit: '', pollInterval: 60, description: '' })
  oidDialogVisible.value = true
}

const editOID = (oid: any) => {
  dialogMode.value = 'edit'
  Object.assign(oidForm, oid)
  oidDialogVisible.value = true
}

const testOID = () => {
  ElMessage.info(`Testing OID ${oidForm.oid}...`)
  setTimeout(() => { ElMessage.success(`Value: Test value returned`) }, 800)
}

const saveOID = async () => {
  if (!oidFormRef.value) return
  await oidFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'OID added successfully' : 'OID updated successfully')
      oidDialogVisible.value = false
      refreshOIDs()
    }
  })
}

const deleteOID = (oid: any) => {
  ElMessageBox.confirm(`Delete OID "${oid.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const oids = oidsMap.value[selectedDevice.value.id]
    const index = oids.findIndex(o => o.id === oid.id)
    if (index !== -1) { oids.splice(index, 1); ElMessage.success(`Deleted: ${oid.name}`) }
  }).catch(() => {})
}

const getOID = (oid: any) => {
  ElMessage.info(`Getting value for ${oid.name}...`)
  setTimeout(() => { ElMessage.success(`${oid.name}: ${Math.random() * 100}`) }, 500)
}

const bulkPoll = () => {
  ElMessage.info('Polling all OIDs...')
  setTimeout(() => { ElMessage.success('Poll completed') }, 2000)
}

const addWalkOID = (row: any) => {
  ElMessage.success(`Added OID: ${row.oid}`)
  walkDialogVisible.value = false
}

const exportWalkResults = () => {
  ElMessage.success('Exporting walk results...')
}

const handleMibNodeClick = (data: any) => {
  if (data.nodeClass === 'object') {
    oidForm.oid = data.oid
    oidForm.name = data.name
    oidDialogVisible.value = true
  }
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

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
.snmp-page {
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

.devices-card, .oid-card, .mib-card { margin-bottom: 20px; }
.devices-card .card-header, .oid-card .card-header, .mib-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.devices-card .table-actions, .oid-card .oid-actions, .mib-card .mib-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.oid-code, .walk-oid { font-family: monospace; font-size: 12px; background: #f5f7fa; padding: 2px 4px; border-radius: 4px; }
.oid-value { font-weight: 500; color: #409eff; }
.community-value { font-family: monospace; }

.oid-footer { margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }

.mib-tree-container { height: 400px; overflow-y: auto; border: 1px solid #ebeef5; border-radius: 8px; padding: 8px; }
.mib-node { display: flex; align-items: center; gap: 8px; }
.mib-oid { font-family: monospace; font-size: 11px; color: #909399; margin-left: auto; }

.walk-results { min-height: 300px; }
.walk-empty { padding: 40px; text-align: center; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.device-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>