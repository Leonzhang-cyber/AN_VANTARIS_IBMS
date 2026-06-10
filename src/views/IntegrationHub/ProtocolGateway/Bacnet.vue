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
        <div class="loading-tip">BACnet Gateway</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="bacnet-gateway-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>BACnet</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>BACnet Gateway</h1>
        <p class="description">Manage BACnet network interfaces, device discovery, and point mapping</p>
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

    <!-- Gateway Status Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in gatewayStats" :key="stat.title">
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
        </el-card>
      </el-col>
    </el-row>

    <!-- Gateway Connection Status -->
    <el-card class="connection-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Gateway Connection Status</span>
          <el-button size="small" @click="refreshConnection">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="connection-status">
            <div class="status-indicator" :class="gatewayStatus"></div>
            <div class="status-text">Gateway: {{ gatewayStatus === 'online' ? 'Online' : 'Offline' }}</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="connection-info">
            <div class="info-label">Interface</div>
            <div class="info-value">eth0:47808</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="connection-info">
            <div class="info-label">BACnet Instance</div>
            <div class="info-value">1001</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="connection-info">
            <div class="info-label">Devices Discovered</div>
            <div class="info-value">{{ discoveredDevices.length }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Device Discovery Panel -->
    <el-card class="discovery-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Device Discovery</span>
          <div class="discovery-controls">
            <el-input
                v-model="discoveryRange"
                placeholder="IP Range (e.g., 192.168.1.0/24)"
                style="width: 200px"
                size="small"
            />
            <el-button type="primary" size="small" @click="startDiscovery" :loading="discovering">
              <el-icon><Search /></el-icon>
              Start Discovery
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="discoveredDevices" stripe style="width: 100%" v-loading="discovering">
        <el-table-column prop="deviceId" label="Device ID" width="120" />
        <el-table-column prop="name" label="Device Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="port" label="Port" width="80" />
        <el-table-column prop="vendor" label="Vendor" width="120" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="importDevice(row)">Import</el-button>
            <el-button link type="info" size="small" @click="testDevice(row)">Test</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Configured Devices Table -->
    <el-card class="devices-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Configured Devices ({{ filteredDevices.length }})</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or ID"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-button :icon="Refresh" @click="fetchDevices" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDevices" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="Device Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="deviceId" label="BACnet ID" width="120" />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="port" label="Port" width="80" />
        <el-table-column prop="pointCount" label="Points" width="80" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewPoints(row)">Points</el-button>
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

    <!-- Points Mapping Table -->
    <el-card class="points-card" shadow="hover" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>Points Mapping - {{ selectedDevice.name }}</span>
          <div class="points-actions">
            <el-button size="small" @click="refreshPoints">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
            <el-button size="small" type="primary" @click="syncPoints">
              <el-icon><Connection /></el-icon>
              Sync Points
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="devicePoints" stripe style="width: 100%" v-loading="pointsLoading">
        <el-table-column prop="objectId" label="Object ID" width="120" />
        <el-table-column prop="objectType" label="Object Type" width="140">
          <template #default="{ row }">
            <el-tag :type="getObjectTypeTag(row.objectType)" size="small">{{ row.objectType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Point Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="presentValue" label="Present Value" width="120" align="right" />
        <el-table-column prop="units" label="Units" width="100" />
        <el-table-column prop="description" label="Description" min-width="180" show-overflow-tooltip />
        <el-table-column label="Mapped To" width="150">
          <template #default="{ row }">
            <el-select v-model="row.mappedTo" placeholder="Select mapping" size="small" clearable>
              <el-option
                  v-for="tag in availableTags"
                  :key="tag"
                  :label="tag"
                  :value="tag"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="testPoint(row)">Test</el-button>
            <el-button link type="success" size="small" @click="savePointMapping(row)">Save</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="points-footer">
        <el-button type="primary" @click="saveAllMappings">Save All Mappings</el-button>
        <span class="points-info">Total Points: {{ devicePoints.length }} | Active: {{ activePoints }}</span>
      </div>
    </el-card>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="deviceDialogVisible" :title="dialogMode === 'add' ? 'Add BACnet Device' : 'Edit BACnet Device'" width="550px" destroy-on-close>
      <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="120px">
        <el-form-item label="Device Name" prop="name">
          <el-input v-model="deviceForm.name" placeholder="Enter device name" />
        </el-form-item>
        <el-form-item label="BACnet Device ID" prop="deviceId">
          <el-input-number v-model="deviceForm.deviceId" :min="0" :max="4194303" style="width: 100%" />
        </el-form-item>
        <el-form-item label="IP Address" prop="ipAddress">
          <el-input v-model="deviceForm.ipAddress" placeholder="192.168.1.100" />
        </el-form-item>
        <el-form-item label="Port" prop="port">
          <el-input-number v-model="deviceForm.port" :min="1" :max="65535" :step="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="deviceForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Auto Sync" prop="autoSync">
          <el-switch v-model="deviceForm.autoSync" />
          <span style="margin-left: 8px; color: #909399">Automatically sync points every hour</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deviceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testAndSave">Test & Save</el-button>
        <el-button type="success" @click="saveDevice">Save</el-button>
      </template>
    </el-dialog>

    <!-- Point Test Dialog -->
    <el-dialog v-model="testDialogVisible" title="Point Test" width="500px" destroy-on-close>
      <div class="point-test" v-if="testPointData">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Object ID">{{ testPointData.objectId }}</el-descriptions-item>
          <el-descriptions-item label="Object Type">{{ testPointData.objectType }}</el-descriptions-item>
          <el-descriptions-item label="Point Name">{{ testPointData.name }}</el-descriptions-item>
          <el-descriptions-item label="Current Value">{{ testPointData.presentValue }} {{ testPointData.units }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag type="success" size="small">Online</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Response Time">{{ testLatency }}ms</el-descriptions-item>
        </el-descriptions>
        <div class="test-controls">
          <el-button type="primary" @click="writeTestValue">Write Test Value</el-button>
          <el-input v-model="testWriteValue" placeholder="Test value" style="width: 150px; margin-left: 8px" />
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
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, Connection, Edit, Cpu
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing BACnet gateway...',
  'Discovering devices...',
  'Almost ready...'
]

// ==================== State ====================
const tableLoading = ref(false)
const pointsLoading = ref(false)
const discovering = ref(false)
const deviceDialogVisible = ref(false)
const testDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedDevice = ref<any>(null)
const testPointData = ref<any>(null)
const testLatency = ref(0)
const testWriteValue = ref('')
const searchKeyword = ref('')
const discoveryRange = ref('192.168.1.0/24')
const currentPage = ref(1)
const pageSize = ref(10)
const gatewayStatus = ref('online')
const deviceFormRef = ref()

const deviceForm = reactive({
  id: null,
  name: '',
  deviceId: 1001,
  ipAddress: '',
  port: 47808,
  description: '',
  autoSync: false
})

const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  deviceId: [{ required: true, message: 'Please enter BACnet device ID', trigger: 'blur' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }]
}

// ==================== Mock Data ====================
const gatewayStats = ref([
  { title: 'Active Devices', value: 24, trend: 8, icon: 'Cpu', bgColor: '#409eff', key: 'devices' },
  { title: 'Total Points', value: '2,456', trend: 12, icon: 'Connection', bgColor: '#67c23a', key: 'points' },
  { title: 'Messages/sec', value: '1,234', trend: 5, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'messages' },
  { title: 'Gateway Uptime', value: '99.95%', trend: 0, icon: 'Clock', bgColor: '#f56c6c', key: 'uptime' }
])

const discoveredDevices = ref([
  { id: 1, deviceId: 1001, name: 'AHU Controller', ipAddress: '192.168.1.100', port: 47808, vendor: 'Johnson Controls', status: 'Online' },
  { id: 2, deviceId: 1002, name: 'Chiller Plant Controller', ipAddress: '192.168.1.101', port: 47808, vendor: 'Trane', status: 'Online' },
  { id: 3, deviceId: 1003, name: 'Lighting Panel', ipAddress: '192.168.1.102', port: 47808, vendor: 'Schneider', status: 'Online' },
  { id: 4, deviceId: 1004, name: 'VAV Controller', ipAddress: '192.168.1.103', port: 47808, vendor: 'Siemens', status: 'Offline' }
])

const configuredDevices = ref([
  { id: 1, name: 'AHU-01 Controller', deviceId: 1001, ipAddress: '192.168.1.100', port: 47808, pointCount: 45, status: 'Online' },
  { id: 2, name: 'Chiller Plant', deviceId: 1002, ipAddress: '192.168.1.101', port: 47808, pointCount: 128, status: 'Online' },
  { id: 3, name: 'Lighting System', deviceId: 1003, ipAddress: '192.168.1.102', port: 47808, pointCount: 256, status: 'Online' },
  { id: 4, name: 'VAV-03 Controller', deviceId: 1005, ipAddress: '192.168.1.105', port: 47808, pointCount: 32, status: 'Online' }
])

const devicePointsData = ref([
  { objectId: 'AI-1', objectType: 'Analog Input', name: 'Supply Air Temperature', presentValue: 22.5, units: '°C', description: 'AHU supply air temperature', mappedTo: 'supply_temp' },
  { objectId: 'AI-2', objectType: 'Analog Input', name: 'Return Air Temperature', presentValue: 23.5, units: '°C', description: 'Return air temperature', mappedTo: 'return_temp' },
  { objectId: 'AO-1', objectType: 'Analog Output', name: 'Chilled Water Valve', presentValue: 45.0, units: '%', description: 'Chilled water valve position', mappedTo: 'valve_position' },
  { objectId: 'DI-1', objectType: 'Digital Input', name: 'Fan Status', presentValue: 1, units: '', description: 'Fan running status', mappedTo: 'fan_status' },
  { objectId: 'DO-1', objectType: 'Digital Output', name: 'Fan Start/Stop', presentValue: 1, units: '', description: 'Fan control', mappedTo: 'fan_control' },
  { objectId: 'AI-3', objectType: 'Analog Input', name: 'Static Pressure', presentValue: 1.25, units: 'in.wg', description: 'Duct static pressure', mappedTo: 'static_pressure' }
])

const availableTags = ref(['supply_temp', 'return_temp', 'valve_position', 'fan_status', 'fan_control', 'static_pressure', 'temp_setpoint', 'alarm_status'])

// ==================== Computed ====================
const filteredDevices = computed(() => {
  if (!searchKeyword.value) return configuredDevices.value
  return configuredDevices.value.filter(d =>
      d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      d.deviceId.toString().includes(searchKeyword.value)
  )
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

const devicePoints = computed(() => devicePointsData.value)
const activePoints = computed(() => devicePointsData.value.filter(p => p.mappedTo).length)

// ==================== Helper Methods ====================
const getObjectTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Analog Input': 'primary',
    'Analog Output': 'success',
    'Digital Input': 'warning',
    'Digital Output': 'danger',
    'Binary Input': 'info',
    'Binary Output': 'info'
  }
  return map[type] || 'info'
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting BACnet configuration...')
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const refreshConnection = () => {
  ElMessage.success('Gateway connection refreshed')
  gatewayStatus.value = 'online'
}

const startDiscovery = () => {
  discovering.value = true
  setTimeout(() => {
    discovering.value = false
    ElMessage.success(`Discovered ${discoveredDevices.value.length} devices`)
  }, 2000)
}

const importDevice = (device: any) => {
  deviceForm.name = device.name
  deviceForm.deviceId = device.deviceId
  deviceForm.ipAddress = device.ipAddress
  deviceForm.port = device.port
  deviceDialogVisible.value = true
  dialogMode.value = 'add'
  ElMessage.success(`Device ${device.name} imported`)
}

const testDevice = (device: any) => {
  ElMessage.info(`Testing connection to ${device.name}...`)
  setTimeout(() => {
    ElMessage.success(`Device ${device.name} is reachable`)
  }, 1000)
}

const fetchDevices = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Devices refreshed')
  }, 500)
}

const openAddDeviceDialog = () => {
  dialogMode.value = 'add'
  Object.assign(deviceForm, {
    id: null,
    name: '',
    deviceId: 1001,
    ipAddress: '',
    port: 47808,
    description: '',
    autoSync: false
  })
  deviceDialogVisible.value = true
}

const editDevice = (device: any) => {
  dialogMode.value = 'edit'
  Object.assign(deviceForm, device)
  deviceDialogVisible.value = true
}

const testConnection = (device: any) => {
  ElMessage.info(`Testing connection to ${device.name}...`)
  setTimeout(() => {
    ElMessage.success(`Device ${device.name} is online`)
  }, 1000)
}

const deleteDevice = (device: any) => {
  ElMessageBox.confirm(`Delete device "${device.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = configuredDevices.value.findIndex(d => d.id === device.id)
    if (index !== -1) {
      configuredDevices.value.splice(index, 1)
      ElMessage.success(`Deleted: ${device.name}`)
    }
  }).catch(() => {})
}

const viewPoints = (device: any) => {
  selectedDevice.value = device
  pointsLoading.value = true
  setTimeout(() => {
    pointsLoading.value = false
    ElMessage.success(`Loaded ${devicePoints.value.length} points for ${device.name}`)
  }, 500)
}

const refreshPoints = () => {
  pointsLoading.value = true
  setTimeout(() => {
    pointsLoading.value = false
    ElMessage.success('Points refreshed')
  }, 1000)
}

const syncPoints = () => {
  ElMessage.info('Synchronizing points from device...')
  setTimeout(() => {
    ElMessage.success('Points synchronized')
  }, 2000)
}

const testPoint = (point: any) => {
  testPointData.value = point
  testLatency.value = Math.floor(Math.random() * 50) + 10
  testWriteValue.value = point.presentValue.toString()
  testDialogVisible.value = true
}

const writeTestValue = () => {
  ElMessage.success(`Wrote value ${testWriteValue.value} to point ${testPointData.value.name}`)
}

const savePointMapping = (point: any) => {
  ElMessage.success(`Mapping saved for ${point.name} → ${point.mappedTo}`)
}

const saveAllMappings = () => {
  ElMessage.success('All point mappings saved')
}

const testAndSave = async () => {
  if (!deviceFormRef.value) return
  await deviceFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.info('Testing connection...')
      setTimeout(() => {
        ElMessage.success('Connection test passed')
        saveDevice()
      }, 1500)
    }
  })
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

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
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
      fetchDevices()
    }, 400)
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

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
.bacnet-gateway-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.connection-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .connection-status {
    display: flex;
    align-items: center;
    gap: 8px;

    .status-indicator {
      width: 12px;
      height: 12px;
      border-radius: 50%;

      &.online {
        background-color: #67c23a;
        box-shadow: 0 0 6px #67c23a;
      }

      &.offline {
        background-color: #f56c6c;
      }
    }
  }

  .connection-info {
    .info-label {
      font-size: 12px;
      color: #909399;
    }

    .info-value {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.discovery-card, .devices-card, .points-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .discovery-controls, .table-actions, .points-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }
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

.point-test {
  .test-controls {
    margin-top: 16px;
    display: flex;
    align-items: center;
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>