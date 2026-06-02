<template>
  <!-- Global Pre Loading Screen -->
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
        <div class="loading-tip">SNMP POINT MODULE</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="snmp-point-container">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalOids }}</span>
          <span class="stat-label">Total OIDs</span>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ activeOids }}</span>
          <span class="stat-label">Active</span>
        </div>
        <div class="stat-percent">{{ activePercent }}%</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ errorOids }}</span>
          <span class="stat-label">Error</span>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ avgResponseTime.toFixed(0) }}ms</span>
          <span class="stat-label">Avg Response</span>
        </div>
      </div>
    </div>

    <!-- 设备连接状态 -->
    <el-card class="device-card" shadow="hover">
      <div class="device-header">
        <span class="device-title">SNMP Devices</span>
        <el-button type="primary" size="small" :icon="Plus" @click="openAddDeviceDialog">Add Device</el-button>
      </div>
      <div class="device-list">
        <div v-for="device in snmpDevices" :key="device.id" class="device-item" :class="{ active: selectedDeviceId === device.id }" @click="selectDevice(device.id)">
          <div class="device-info">
            <div class="device-status">
              <span class="status-dot" :class="device.status"></span>
              <span class="device-name">{{ device.name }}</span>
            </div>
            <div class="device-address">{{ device.host }}:{{ device.port }}</div>
          </div>
          <div class="device-version">
            <el-tag size="small">SNMPv{{ device.version }}</el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 筛选卡片 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="OID">
          <el-input v-model="filterForm.oid" placeholder="e.g., 1.3.6.1.2.1.1" clearable style="width: 220px" />
        </el-form-item>
        <el-form-item label="MIB Module">
          <el-select v-model="filterForm.mibModule" placeholder="MIB Module" clearable style="width: 150px">
            <el-option label="RFC1213-MIB" value="RFC1213-MIB" />
            <el-option label="IF-MIB" value="IF-MIB" />
            <el-option label="IP-MIB" value="IP-MIB" />
            <el-option label="TCP-MIB" value="TCP-MIB" />
            <el-option label="UDP-MIB" value="UDP-MIB" />
            <el-option label="SNMPv2-MIB" value="SNMPv2-MIB" />
          </el-select>
        </el-form-item>
        <el-form-item label="Object Type">
          <el-select v-model="filterForm.objectType" placeholder="Type" clearable style="width: 120px">
            <el-option label="Scalar" value="scalar" />
            <el-option label="Table" value="table" />
          </el-select>
        </el-form-item>
        <el-form-item label="Value Type">
          <el-select v-model="filterForm.valueType" placeholder="Value Type" clearable style="width: 120px">
            <el-option label="Integer" value="integer" />
            <el-option label="String" value="string" />
            <el-option label="Counter" value="counter" />
            <el-option label="Gauge" value="gauge" />
            <el-option label="IpAddress" value="ipaddress" />
            <el-option label="OID" value="oid" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetFilter">Reset</el-button>
          <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
          <el-button type="success" :icon="Plus" @click="openAddOidDialog">Add OID</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span>SNMP Value Trend</span>
            <el-select v-model="trendOidId" placeholder="Select OID" size="small" style="width: 250px" filterable @change="updateTrendChart">
              <el-option v-for="oid in numericOids" :key="oid.id" :label="oid.objectName" :value="oid.id" />
            </el-select>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-box"></div>
      </el-card>

      <el-card class="stats-chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">OID Type Distribution</div>
        </template>
        <div ref="pieChartRef" class="pie-chart-box"></div>
      </el-card>
    </div>

    <!-- SNMP OID 列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">SNMP OID Monitoring List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="400" v-loading="tableLoading">
        <el-table-column label="OID" prop="oid" min-width="250" show-overflow-tooltip />
        <el-table-column label="Object Name" prop="objectName" min-width="180" show-overflow-tooltip />
        <el-table-column label="MIB Module" prop="mibModule" width="140" />
        <el-table-column label="Type" prop="valueType" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.valueType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Current Value" prop="currentValue" width="150">
          <template #default="scope">
            <span :class="getValueClass(scope.row)">{{ formatValue(scope.row.currentValue) }}</span>
            <span class="unit">{{ scope.row.unit || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" prop="status" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'good' ? 'success' : scope.row.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Response Time" prop="responseTime" width="110">
          <template #default="scope">
            <span :class="{ 'text-warning': scope.row.responseTime > 100 }">{{ scope.row.responseTime }}ms</span>
          </template>
        </el-table-column>
        <el-table-column label="Last Poll" prop="lastPoll" width="160" />
        <el-table-column label="Operation" width="140" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="pollNow(scope.row)">Poll</el-button>
            <el-button text type="danger" size="small" @click="walkOid(scope.row)">Walk</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
            v-model:current-page="pageInfo.pageNum"
            v-model:page-size="pageInfo.pageSize"
            :page-sizes="[15, 30, 50, 100]"
            :total="pageInfo.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 添加设备对话框 -->
    <el-dialog v-model="addDeviceDialogVisible" title="Add SNMP Device" width="500px">
      <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="100px">
        <el-form-item label="Device Name" prop="name">
          <el-input v-model="deviceForm.name" placeholder="e.g., Core Switch-01" />
        </el-form-item>
        <el-form-item label="Host/IP" prop="host">
          <el-input v-model="deviceForm.host" placeholder="192.168.1.1" />
        </el-form-item>
        <el-form-item label="Port" prop="port">
          <el-input-number v-model="deviceForm.port" :min="1" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="SNMP Version" prop="version">
          <el-select v-model="deviceForm.version" style="width: 100%">
            <el-option label="v1" value="1" />
            <el-option label="v2c" value="2c" />
            <el-option label="v3" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Community" prop="community">
          <el-input v-model="deviceForm.community" placeholder="public" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDeviceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAddDevice" :loading="addingDevice">Add Device</el-button>
      </template>
    </el-dialog>

    <!-- 添加OID对话框 -->
    <el-dialog v-model="addOidDialogVisible" title="Add SNMP OID" width="550px">
      <el-form :model="oidForm" :rules="oidRules" ref="oidFormRef" label-width="110px">
        <el-form-item label="Device" prop="deviceId">
          <el-select v-model="oidForm.deviceId" style="width: 100%">
            <el-option v-for="device in snmpDevices" :key="device.id" :label="device.name" :value="device.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="OID" prop="oid">
          <el-input v-model="oidForm.oid" placeholder="1.3.6.1.2.1.1.1.0" />
        </el-form-item>
        <el-form-item label="Object Name" prop="objectName">
          <el-input v-model="oidForm.objectName" placeholder="sysDescr" />
        </el-form-item>
        <el-form-item label="MIB Module" prop="mibModule">
          <el-select v-model="oidForm.mibModule" style="width: 100%">
            <el-option label="RFC1213-MIB" value="RFC1213-MIB" />
            <el-option label="IF-MIB" value="IF-MIB" />
            <el-option label="IP-MIB" value="IP-MIB" />
            <el-option label="TCP-MIB" value="TCP-MIB" />
            <el-option label="UDP-MIB" value="UDP-MIB" />
            <el-option label="CUSTOM-MIB" value="CUSTOM-MIB" />
          </el-select>
        </el-form-item>
        <el-form-item label="Value Type" prop="valueType">
          <el-select v-model="oidForm.valueType" style="width: 100%">
            <el-option label="Integer" value="integer" />
            <el-option label="String" value="string" />
            <el-option label="Counter" value="counter" />
            <el-option label="Gauge" value="gauge" />
            <el-option label="IpAddress" value="ipaddress" />
          </el-select>
        </el-form-item>
        <el-form-item label="Unit">
          <el-input v-model="oidForm.unit" placeholder="e.g., packets, bytes, %" />
        </el-form-item>
        <el-form-item label="Poll Interval (s)">
          <el-input-number v-model="oidForm.pollInterval" :min="5" :max="3600" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addOidDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAddOid" :loading="addingOid">Add OID</el-button>
      </template>
    </el-dialog>

    <!-- OID Walk 结果对话框 -->
    <el-dialog v-model="walkDialogVisible" :title="`SNMP Walk - ${selectedOid?.objectName || selectedOid?.oid}`" width="700px">
      <el-table :data="walkResults" stripe border max-height="400">
        <el-table-column label="OID" prop="oid" min-width="300" show-overflow-tooltip />
        <el-table-column label="Value" prop="value" min-width="200" />
        <el-table-column label="Type" prop="type" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="walkDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportWalkResults">Export</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import type { FormInstance, FormRules } from 'element-plus'
import { Connection, CircleCheckFilled, WarningFilled, DataLine, Refresh, Plus } from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading SNMP modules...',
  'Initializing MIB database...',
  'Discovering OIDs...',
  'Almost ready...'
]

// ========== Chart References ==========
const trendChartRef = ref<HTMLDivElement | null>(null)
const pieChartRef = ref<HTMLDivElement | null>(null)
let trendInstance: echarts.ECharts | null = null
let pieInstance: echarts.ECharts | null = null
let pollTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const addingDevice = ref(false)
const addingOid = ref(false)
const trendOidId = ref('')
const selectedDeviceId = ref('')
const deviceFormRef = ref<FormInstance>()
const oidFormRef = ref<FormInstance>()

// ========== Filter Form ==========
const filterForm = reactive({
  oid: '',
  mibModule: '',
  objectType: '',
  valueType: ''
})

// ========== Pagination ==========
const pageInfo = reactive({
  pageNum: 1,
  pageSize: 15,
  total: 0
})

// ========== Dialog State ==========
const addDeviceDialogVisible = ref(false)
const addOidDialogVisible = ref(false)
const walkDialogVisible = ref(false)
const selectedOid = ref<any>(null)
const walkResults = ref<any[]>([])

// ========== Form Data ==========
const deviceForm = reactive({
  name: '',
  host: '',
  port: 161,
  version: '2c',
  community: 'public'
})

const deviceRules: FormRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  host: [{ required: true, message: 'Please enter host/IP', trigger: 'blur' }]
}

const oidForm = reactive({
  deviceId: '',
  oid: '',
  objectName: '',
  mibModule: 'RFC1213-MIB',
  valueType: 'string',
  unit: '',
  pollInterval: 60
})

const oidRules: FormRules = {
  deviceId: [{ required: true, message: 'Please select device', trigger: 'change' }],
  oid: [{ required: true, message: 'Please enter OID', trigger: 'blur' }],
  objectName: [{ required: true, message: 'Please enter object name', trigger: 'blur' }]
}

// ========== SNMP Devices ==========
const snmpDevices = ref([
  { id: '1', name: 'Core Switch-01', host: '192.168.1.1', port: 161, version: '2c', community: 'public', status: 'online' },
  { id: '2', name: 'Building Router', host: '192.168.1.254', port: 161, version: '2c', community: 'public', status: 'online' },
  { id: '3', name: 'UPS Power Monitor', host: '192.168.1.100', port: 161, version: '1', community: 'public', status: 'offline' }
])

// ========== SNMP OID Data ==========
const allOids = ref<any[]>([])

// 统计数据
const totalOids = computed(() => allOids.value.length)
const activeOids = computed(() => allOids.value.filter(item => item.status === 'good').length)
const errorOids = computed(() => allOids.value.filter(item => item.status === 'error').length)
const activePercent = computed(() => totalOids.value ? Math.round(activeOids.value / totalOids.value * 100) : 0)
const avgResponseTime = computed(() => {
  const goodOids = allOids.value.filter(o => o.status === 'good')
  if (goodOids.length === 0) return 0
  const sum = goodOids.reduce((s, o) => s + (o.responseTime || 0), 0)
  return sum / goodOids.length
})

// 数值型OID（用于趋势图）
const numericOids = computed(() =>
    allOids.value.filter(o => (o.valueType === 'integer' || o.valueType === 'counter' || o.valueType === 'gauge') && o.status === 'good')
)

// 分页数据
const paginatedTableData = computed(() => {
  let filtered = [...allOids.value]

  if (filterForm.oid) {
    filtered = filtered.filter(item => item.oid?.includes(filterForm.oid))
  }
  if (filterForm.mibModule) {
    filtered = filtered.filter(item => item.mibModule === filterForm.mibModule)
  }
  if (filterForm.objectType) {
    filtered = filtered.filter(item => item.objectType === filterForm.objectType)
  }
  if (filterForm.valueType) {
    filtered = filtered.filter(item => item.valueType === filterForm.valueType)
  }
  if (selectedDeviceId.value) {
    filtered = filtered.filter(item => item.deviceId === selectedDeviceId.value)
  }

  pageInfo.total = filtered.length
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return filtered.slice(start, start + pageInfo.pageSize)
})

// ========== 生成模拟数据 ==========
const generateOidData = () => {
  const baseOids = [
    { oid: '1.3.6.1.2.1.1.1.0', objectName: 'sysDescr', mibModule: 'RFC1213-MIB', valueType: 'string', unit: '', objectType: 'scalar', baseValue: 'Cisco IOS Software' },
    { oid: '1.3.6.1.2.1.1.3.0', objectName: 'sysUpTime', mibModule: 'RFC1213-MIB', valueType: 'counter', unit: 'ms', objectType: 'scalar', baseValue: 1234567890, isNumeric: true },
    { oid: '1.3.6.1.2.1.2.2.1.10.1', objectName: 'ifInOctets', mibModule: 'IF-MIB', valueType: 'counter', unit: 'bytes', objectType: 'table', baseValue: 1234567890, isNumeric: true },
    { oid: '1.3.6.1.2.1.2.2.1.16.1', objectName: 'ifOutOctets', mibModule: 'IF-MIB', valueType: 'counter', unit: 'bytes', objectType: 'table', baseValue: 987654321, isNumeric: true },
    { oid: '1.3.6.1.2.1.4.20.0', objectName: 'ipRoutingDiscards', mibModule: 'IP-MIB', valueType: 'counter', unit: 'packets', objectType: 'scalar', baseValue: 125, isNumeric: true },
    { oid: '1.3.6.1.2.1.6.13.0', objectName: 'tcpAttemptFails', mibModule: 'TCP-MIB', valueType: 'counter', unit: 'count', objectType: 'scalar', baseValue: 45, isNumeric: true },
    { oid: '1.3.6.1.2.1.7.1.0', objectName: 'udpInDatagrams', mibModule: 'UDP-MIB', valueType: 'counter', unit: 'datagrams', objectType: 'scalar', baseValue: 67890, isNumeric: true },
    { oid: '1.3.6.1.2.1.25.1.1.0', objectName: 'hrSystemUptime', mibModule: 'HOST-RESOURCES-MIB', valueType: 'counter', unit: 'ms', objectType: 'scalar', baseValue: 87654321, isNumeric: true },
    { oid: '1.3.6.1.2.1.25.3.3.1.2.1', objectName: 'hrProcessorLoad', mibModule: 'HOST-RESOURCES-MIB', valueType: 'gauge', unit: '%', objectType: 'table', baseValue: 15, isNumeric: true },
    { oid: '1.3.6.1.2.1.25.2.3.1.5.1', objectName: 'hrStorageUsed', mibModule: 'HOST-RESOURCES-MIB', valueType: 'gauge', unit: 'KB', objectType: 'table', baseValue: 512000, isNumeric: true },
    { oid: '1.3.6.1.2.1.25.2.3.1.6.1', objectName: 'hrStorageAllocationUnits', mibModule: 'HOST-RESOURCES-MIB', valueType: 'integer', unit: 'bytes', objectType: 'table', baseValue: 4096, isNumeric: true }
  ]

  const devices = snmpDevices.value
  const oids = []
  let id = 1

  for (const device of devices) {
    for (const base of baseOids) {
      const isGood = Math.random() > 0.15
      const responseTime = Math.floor(15 + Math.random() * 50)
      let currentValue = base.baseValue

      if (base.isNumeric && typeof base.baseValue === 'number') {
        const variation = (Math.random() - 0.5) * (base.baseValue * 0.05)
        currentValue = Math.max(0, Math.floor(base.baseValue + variation))
      }

      oids.push({
        id: id++,
        deviceId: device.id,
        deviceName: device.name,
        oid: base.oid,
        objectName: base.objectName,
        mibModule: base.mibModule,
        valueType: base.valueType,
        unit: base.unit,
        objectType: base.objectType,
        currentValue: currentValue,
        status: isGood ? 'good' : (Math.random() > 0.5 ? 'warning' : 'error'),
        responseTime: responseTime,
        lastPoll: new Date().toLocaleString(),
        pollInterval: 60
      })
    }
  }

  allOids.value = oids
  if (numericOids.value.length > 0) {
    trendOidId.value = numericOids.value[0].id.toString()
  }
}

// 更新OID值
const updateOidValues = () => {
  for (const oid of allOids.value) {
    if (oid.status === 'good' && (oid.valueType === 'counter' || oid.valueType === 'gauge' || oid.valueType === 'integer')) {
      const change = (Math.random() - 0.5) * (typeof oid.currentValue === 'number' ? oid.currentValue * 0.02 : 5)
      let newVal = (oid.currentValue as number) + change
      if (oid.objectName === 'hrProcessorLoad') {
        newVal = Math.max(0, Math.min(100, newVal))
      } else if (oid.objectName === 'hrStorageUsed') {
        newVal = Math.max(0, newVal)
      }
      oid.currentValue = Math.max(0, Math.floor(newVal))
      oid.responseTime = Math.floor(15 + Math.random() * 50)
      oid.lastPoll = new Date().toLocaleString()

      // 随机状态变化
      if (Math.random() > 0.98) {
        oid.status = oid.status === 'good' ? (Math.random() > 0.5 ? 'warning' : 'error') : 'good'
      }
    }
  }
}

// ========== 趋势图数据 ==========
const trendHistory = ref<{ timestamps: string[]; values: number[] }>({
  timestamps: [],
  values: []
})

// 获取OID历史数据
const getOidHistory = () => {
  const oid = numericOids.value.find(o => o.id.toString() === trendOidId.value)
  if (!oid) return

  const timestamps = []
  const values = []
  const now = new Date()
  const baseValue = typeof oid.currentValue === 'number' ? oid.currentValue : 100

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)
    const variation = Math.sin(i * 0.3) * (baseValue * 0.1) + (Math.random() - 0.5) * (baseValue * 0.05)
    values.push(Math.max(0, Math.floor(baseValue + variation)))
  }

  trendHistory.value = { timestamps, values }
}

// 添加新数据点
const appendTrendData = () => {
  const oid = numericOids.value.find(o => o.id.toString() === trendOidId.value)
  if (!oid) return

  const now = new Date()
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:00`
  const newValue = typeof oid.currentValue === 'number' ? oid.currentValue : 0

  trendHistory.value.timestamps.push(timeStr)
  trendHistory.value.values.push(newValue)

  if (trendHistory.value.timestamps.length > 48) {
    trendHistory.value.timestamps.shift()
    trendHistory.value.values.shift()
  }

  updateTrendChart()
}

// 初始化趋势图
const initTrendChart = async () => {
  await nextTick()
  if (!trendChartRef.value) {
    setTimeout(() => initTrendChart(), 100)
    return
  }

  if (trendInstance) trendInstance.dispose()

  getOidHistory()
  trendInstance = echarts.init(trendChartRef.value)
  updateTrendChart()
  window.addEventListener('resize', handleChartResize)
}

const updateTrendChart = () => {
  if (!trendInstance || !trendHistory.value.timestamps.length) return

  const oid = numericOids.value.find(o => o.id.toString() === trendOidId.value)
  const unit = oid?.unit || ''

  const option = {
    tooltip: { trigger: 'axis', formatter: (params: any) => `${params[0].axisValue}<br/>Value: ${params[0].value} ${unit}` },
    grid: { left: '8%', right: '5%', top: '12%', bottom: '8%', containLabel: true },
    xAxis: { type: 'category', data: trendHistory.value.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: `Value (${unit})`, nameTextStyle: { fontSize: 12 } },
    series: [{
      name: oid?.objectName || 'Value',
      type: 'line',
      data: trendHistory.value.values,
      smooth: true,
      lineStyle: { color: '#409eff', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle',
      symbolSize: 5
    }]
  }
  trendInstance.setOption(option, true)
}

// 初始化饼图
const initPieChart = async () => {
  await nextTick()
  if (!pieChartRef.value) {
    setTimeout(() => initPieChart(), 100)
    return
  }

  if (pieInstance) pieInstance.dispose()
  pieInstance = echarts.init(pieChartRef.value)

  const scalarCount = allOids.value.filter(o => o.objectType === 'scalar').length
  const tableCount = allOids.value.filter(o => o.objectType === 'table').length

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['Scalar OIDs', 'Table OIDs'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'Scalar OIDs', value: scalarCount, itemStyle: { color: '#409eff' } },
        { name: 'Table OIDs', value: tableCount, itemStyle: { color: '#67c23a' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}', position: 'outside' }
    }]
  }
  pieInstance.setOption(option)
}

const updatePieChart = () => {
  if (!pieInstance) return
  const scalarCount = allOids.value.filter(o => o.objectType === 'scalar').length
  const tableCount = allOids.value.filter(o => o.objectType === 'table').length
  pieInstance.setOption({ series: [{ data: [{ name: 'Scalar OIDs', value: scalarCount }, { name: 'Table OIDs', value: tableCount }] }] })
}

const handleChartResize = () => {
  if (trendInstance) trendInstance.resize()
  if (pieInstance) pieInstance.resize()
}

// ========== Helper Functions ==========
const formatValue = (value: any) => {
  if (typeof value === 'number') return value.toLocaleString()
  return value
}

const getValueClass = (row: any) => {
  if (row.status === 'error') return 'text-danger'
  if (row.status === 'warning') return 'text-warning'
  if (row.objectName === 'hrProcessorLoad' && row.currentValue > 80) return 'text-warning'
  if (row.objectName === 'hrProcessorLoad' && row.currentValue > 95) return 'text-danger'
  return ''
}

const selectDevice = (deviceId: string) => {
  selectedDeviceId.value = deviceId
  pageInfo.pageNum = 1
}

// ========== Actions ==========
const handleSearch = () => { pageInfo.pageNum = 1 }
const resetFilter = () => {
  filterForm.oid = ''
  filterForm.mibModule = ''
  filterForm.objectType = ''
  filterForm.valueType = ''
  selectedDeviceId.value = ''
  pageInfo.pageNum = 1
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  generateOidData()
  updatePieChart()
  if (numericOids.value.length > 0 && !trendOidId.value) {
    trendOidId.value = numericOids.value[0].id.toString()
    getOidHistory()
    updateTrendChart()
  }
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pageInfo.pageNum = 1 }
const handlePageChange = () => {}

const viewDetail = (row: any) => {
  ElMessage.info(`Viewing details for OID: ${row.oid}`)
}

const pollNow = (row: any) => {
  ElMessage.info(`Polling ${row.objectName}...`)
  setTimeout(() => {
    if (row.valueType === 'counter' || row.valueType === 'gauge' || row.valueType === 'integer') {
      const change = (Math.random() - 0.5) * (typeof row.currentValue === 'number' ? row.currentValue * 0.02 : 5)
      row.currentValue = Math.max(0, Math.floor((row.currentValue as number) + change))
    }
    row.responseTime = Math.floor(15 + Math.random() * 50)
    row.lastPoll = new Date().toLocaleString()
    ElMessage.success(`Polled ${row.objectName}: ${row.currentValue} ${row.unit}`)
  }, 500)
}

const walkOid = (row: any) => {
  selectedOid.value = row
  // 模拟walk结果
  walkResults.value = [
    { oid: row.oid, value: row.currentValue, type: row.valueType },
    { oid: `${row.oid}.1`, value: 'Sub-value-1', type: 'string' },
    { oid: `${row.oid}.2`, value: 'Sub-value-2', type: 'string' },
    { oid: `${row.oid}.3`, value: Math.floor(Math.random() * 1000), type: 'integer' }
  ]
  walkDialogVisible.value = true
}

const exportWalkResults = () => {
  ElMessage.success('Exporting walk results...')
}

const openAddDeviceDialog = () => {
  deviceForm.name = ''
  deviceForm.host = ''
  deviceForm.port = 161
  deviceForm.version = '2c'
  deviceForm.community = 'public'
  addDeviceDialogVisible.value = true
}

const confirmAddDevice = async () => {
  if (!deviceFormRef.value) return
  await deviceFormRef.value.validate(async (valid) => {
    if (valid) {
      addingDevice.value = true
      await new Promise(resolve => setTimeout(resolve, 800))

      const newDevice = {
        id: (snmpDevices.value.length + 1).toString(),
        name: deviceForm.name,
        host: deviceForm.host,
        port: deviceForm.port,
        version: deviceForm.version,
        community: deviceForm.community,
        status: 'online'
      }
      snmpDevices.value.push(newDevice)
      addDeviceDialogVisible.value = false
      addingDevice.value = false
      ElMessage.success(`Device ${deviceForm.name} added`)
    }
  })
}

const openAddOidDialog = () => {
  oidForm.deviceId = snmpDevices.value[0]?.id || ''
  oidForm.oid = ''
  oidForm.objectName = ''
  oidForm.mibModule = 'RFC1213-MIB'
  oidForm.valueType = 'string'
  oidForm.unit = ''
  oidForm.pollInterval = 60
  addOidDialogVisible.value = true
}

const confirmAddOid = async () => {
  if (!oidFormRef.value) return
  await oidFormRef.value.validate(async (valid) => {
    if (valid) {
      addingOid.value = true
      await new Promise(resolve => setTimeout(resolve, 800))

      const device = snmpDevices.value.find(d => d.id === oidForm.deviceId)
      const newOid = {
        id: allOids.value.length + 1,
        deviceId: oidForm.deviceId,
        deviceName: device?.name || '',
        oid: oidForm.oid,
        objectName: oidForm.objectName,
        mibModule: oidForm.mibModule,
        valueType: oidForm.valueType,
        unit: oidForm.unit,
        objectType: 'scalar',
        currentValue: oidForm.valueType === 'string' ? '-' : 0,
        status: 'good',
        responseTime: 0,
        lastPoll: new Date().toLocaleString(),
        pollInterval: oidForm.pollInterval
      }
      allOids.value.unshift(newOid)
      updatePieChart()
      addOidDialogVisible.value = false
      addingOid.value = false
      ElMessage.success(`OID ${oidForm.oid} added`)
    }
  })
}

// 定时轮询
const startPolling = () => {
  pollTimer = window.setInterval(() => {
    updateOidValues()
    appendTrendData()
  }, 5000)
}

// ========== Lifecycle ==========
onMounted(async () => {
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

  setTimeout(async () => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(async () => {
      generateOidData()
      isLoaded.value = true
      await nextTick()

      setTimeout(async () => {
        await initTrendChart()
        await initPieChart()
        startPolling()
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (trendInstance) trendInstance.dispose()
  if (pieInstance) pieInstance.dispose()
  window.removeEventListener('resize', handleChartResize)
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

/* Page Content */
.snmp-point-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon .el-icon {
  font-size: 32px;
  color: #3b82f6;
}

.stat-card.success .stat-icon .el-icon { color: #67c23a; }
.stat-card.warning .stat-icon .el-icon { color: #e6a23c; }
.stat-card.info .stat-icon .el-icon { color: #409eff; }

.stat-info { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }
.stat-percent { font-size: 20px; font-weight: 600; color: #67c23a; }

.device-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.device-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.device-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.device-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.device-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
  min-width: 200px;
}

.device-item:hover {
  background: #ecf5ff;
  border-color: #409eff;
}

.device-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}

.device-info {
  flex: 1;
}

.device-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.device-name {
  font-weight: 500;
  font-size: 14px;
  color: #1e293b;
}

.device-address {
  font-size: 11px;
  color: #64748b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #67c23a;
  box-shadow: 0 0 4px #67c23a;
}

.status-dot.offline {
  background: #f56c6c;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-card :deep(.el-card__body) {
  padding: 20px;
}

.filter-card :deep(.el-form) {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px;
}

.filter-card :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-card :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  padding-bottom: 4px;
}

.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card, .stats-chart-card {
  flex: 1;
  border-radius: 12px;
}

.card-header-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-box, .pie-chart-box {
  width: 100%;
  height: 320px;
}

.text-warning { color: #e6a23c; font-weight: 500; }
.text-danger { color: #f56c6c; font-weight: 500; }

.unit {
  font-size: 11px;
  color: #94a3b8;
  margin-left: 2px;
}

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .snmp-point-container {
    padding: 12px;
  }
  .stats-cards {
    grid-template-columns: 1fr;
  }
  .device-list {
    flex-direction: column;
  }
  .device-item {
    width: 100%;
  }
  .filter-card :deep(.el-form) {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-card :deep(.el-form-item) {
    width: 100%;
  }
  .filter-card :deep(.el-input),
  .filter-card :deep(.el-select) {
    width: 100% !important;
  }
  .chart-box, .pie-chart-box {
    height: 250px;
  }
}
</style>