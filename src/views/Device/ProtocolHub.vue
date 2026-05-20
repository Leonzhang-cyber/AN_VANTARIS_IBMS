<template>
  <div class="protocol-hub">
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
          <div class="loading-tip">IoT Digital Base · Protocol Hub</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <div class="page-header">
        <h1>Protocol Hub</h1>
        <p class="subtitle">IoT Digital Base · Multi-Protocol Gateway · Device Integration</p>
      </div>

      <!-- Statistics Cards -->
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-icon" style="background: #667eea"><el-icon><Connection /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.activeConnections }}</div><div class="stat-label">Active Connections</div></div></div>
        <div class="stat-card"><div class="stat-icon" style="background: #10b981"><el-icon><Cpu /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.connectedDevices }}</div><div class="stat-label">Connected Devices</div></div></div>
        <div class="stat-card"><div class="stat-icon" style="background: #f59e0b"><el-icon><Document /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.supportedProtocols }}</div><div class="stat-label">Protocols Supported</div></div></div>
        <div class="stat-card"><div class="stat-icon" style="background: #ef4444"><el-icon><Timer /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.avgLatency }}<span class="stat-unit">ms</span></div><div class="stat-label">Avg Latency</div></div></div>
        <div class="stat-card"><div class="stat-icon" style="background: #8b5cf6"><el-icon><DataLine /></el-icon></div><div class="stat-info"><div class="stat-value">{{ formatNumber(stats.todayMessages) }}</div><div class="stat-label">Messages Today</div></div></div>
        <div class="stat-card"><div class="stat-icon" style="background: #06b6d4"><el-icon><Share /></el-icon></div><div class="stat-info"><div class="stat-value">{{ formatNumber(stats.dataPoints) }}</div><div class="stat-label">Data Points</div></div></div>
      </div>

      <!-- Protocols Table -->
      <div class="section-card">
        <div class="section-header">
          <div class="section-title"><el-icon><Connection /></el-icon><span>Protocols</span><el-tag size="small" type="info">{{ protocols.length }}</el-tag></div>
          <el-button type="primary" size="small" @click="openAddProtocol"><el-icon><Plus /></el-icon> Add Protocol</el-button>
        </div>
        <el-table :data="protocols" stripe style="width: 100%" max-height="350">
          <el-table-column prop="name" label="Protocol Name" min-width="130" />
          <el-table-column prop="category" label="Category" min-width="120" />
          <el-table-column prop="version" label="Version" min-width="90" />
          <el-table-column label="Status" min-width="90">
            <template #default="{ row }"><span class="status-dot" :class="row.status"></span>{{ row.status === 'online' ? 'Online' : 'Offline' }}</template>
          </el-table-column>
          <el-table-column prop="deviceCount" label="Devices" min-width="80" align="center" />
          <el-table-column label="Driver" min-width="140">
            <template #default="{ row }"><span class="driver-name">{{ row.driverClass?.split('.').pop() || 'Driver' }}</span></template>
          </el-table-column>
          <el-table-column label="Actions" min-width="130" align="center">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="editProtocol(row)">Config</el-button>
              <el-button link type="success" size="small" @click="testConnection(row)">Test</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Devices Table -->
<!--      <div class="section-card">-->
<!--        <div class="section-header">-->
<!--          <div class="section-title"><el-icon><Cpu /></el-icon><span>Devices</span><el-tag size="small" type="info">{{ devices.length }}</el-tag></div>-->
<!--          <div style="display: flex; gap: 12px; flex-wrap: wrap;">-->
<!--            <el-input v-model="deviceSearch" placeholder="Search device..." prefix-icon="Search" size="small" clearable style="width: 200px" />-->
<!--            <el-select v-model="protocolFilter" placeholder="Protocol" size="small" clearable style="width: 130px">-->
<!--              <el-option v-for="p in protocols" :key="p.name" :label="p.name" :value="p.name" />-->
<!--            </el-select>-->
<!--            <el-select v-model="statusFilter" placeholder="Status" size="small" clearable style="width: 110px">-->
<!--              <el-option label="Online" value="online" />-->
<!--              <el-option label="Offline" value="offline" />-->
<!--            </el-select>-->
<!--            <el-button type="primary" size="small" @click="openRegisterDevice"><el-icon><Plus /></el-icon> Register</el-button>-->
<!--          </div>-->
<!--        </div>-->
<!--        <el-table :data="filteredDevices" stripe style="width: 100%" max-height="450">-->
<!--          <el-table-column prop="deviceName" label="Device Name" min-width="180" />-->
<!--          <el-table-column prop="deviceCode" label="Device Code" min-width="120" />-->
<!--          <el-table-column prop="protocol" label="Protocol" min-width="100">-->
<!--            <template #default="{ row }"><el-tag size="small" :type="getProtocolType(row.protocol)">{{ row.protocol }}</el-tag></template>-->
<!--          </el-table-column>-->
<!--          <el-table-column label="Status" min-width="80">-->
<!--            <template #default="{ row }"><span class="status-dot" :class="row.status"></span>{{ row.status === 'online' ? 'Online' : 'Offline' }}</template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="did" label="DID" min-width="250" show-overflow-tooltip>-->
<!--            <template #default="{ row }"><span class="did-text">{{ truncateDid(row.did) }}</span></template>-->
<!--          </el-table-column>-->
<!--          <el-table-column prop="lastSeen" label="Last Seen" min-width="120" />-->
<!--          <el-table-column label="Actions" min-width="130" align="center">-->
<!--            <template #default="{ row }">-->
<!--              <el-button link type="primary" size="small" @click="viewDevice(row)">View</el-button>-->
<!--              <el-button link type="warning" size="small" @click="editDevice(row)">Edit</el-button>-->
<!--              <el-button link type="danger" size="small" @click="deleteDevice(row)">Delete</el-button>-->
<!--            </template>-->
<!--          </el-table-column>-->
<!--        </el-table>-->
<!--      </div>-->

      <!-- Two Columns: Standard Field Dictionary + Standard Method Dictionary -->
      <div class="dashboard-two-columns">
        <!-- Standard Field Dictionary -->
        <div class="section-card">
          <div class="section-header">
            <div class="section-title"><el-icon><Grid /></el-icon><span>Standard Field Dictionary</span><el-tag size="small" type="info">{{ standardFields.length }}</el-tag></div>
            <el-button type="primary" size="small" @click="addStandardField"><el-icon><Plus /></el-icon> Add Field</el-button>
          </div>
          <div class="mapping-table-wrapper">
            <el-table :data="standardFields" stripe size="small" style="width: 100%" max-height="400" height="400">
              <el-table-column prop="fieldCode" label="Field Code" min-width="160" />
              <el-table-column prop="fieldType" label="Type" min-width="80" />
              <el-table-column prop="unit" label="Unit" min-width="70" />
              <el-table-column prop="rangeMin" label="Min" min-width="60" />
              <el-table-column prop="rangeMax" label="Max" min-width="60" />
              <el-table-column label="Critical" min-width="80">
                <template #default="{ row }"><el-tag :type="row.isCritical ? 'danger' : 'info'" size="small">{{ row.isCritical ? 'Yes' : 'No' }}</el-tag></template>
              </el-table-column>
              <el-table-column label="Action" width="100" align="center">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="editStandardField(row)">Edit</el-button>
                  <el-button link type="danger" size="small" @click="deleteStandardField(row)">Del</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>

        <!-- Standard Method Dictionary -->
        <div class="section-card">
          <div class="section-header">
            <div class="section-title"><el-icon><Setting /></el-icon><span>Standard Method Dictionary</span><el-tag size="small" type="info">{{ standardMethods.length }}</el-tag></div>
            <el-button type="primary" size="small" @click="addStandardMethod"><el-icon><Plus /></el-icon> Add Method</el-button>
          </div>
          <div class="mapping-table-wrapper">
            <el-table :data="standardMethods" stripe size="small" style="width: 100%" max-height="400" height="400">
              <el-table-column prop="methodCode" label="Method Code" min-width="160" />
              <el-table-column prop="category" label="Category" min-width="100" />
              <el-table-column prop="paramName" label="Parameter" min-width="100" />
              <el-table-column prop="paramType" label="Type" min-width="80" />
              <el-table-column prop="paramRange" label="Range" min-width="100" />
              <el-table-column label="Action" width="100" align="center">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="editStandardMethod(row)">Edit</el-button>
                  <el-button link type="danger" size="small" @click="deleteStandardMethod(row)">Del</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>

      <!-- Device Field Mapping -->
      <div class="section-card">
        <div class="section-header">
          <div class="section-title"><el-icon><Grid /></el-icon><span>Device Field Mapping (Raw → Standard)</span></div>
          <div class="mapping-device-selector">
            <span class="label">Device:</span>
            <el-select v-model="selectedMappingDevice" placeholder="Select device" size="small" filterable style="width: 260px">
              <el-option v-for="d in devices" :key="d.deviceCode" :label="`${d.deviceName} (${d.deviceCode})`" :value="d.deviceCode" />
            </el-select>
            <el-button type="primary" size="small" @click="addFieldMapping"><el-icon><Plus /></el-icon> Add Mapping</el-button>
          </div>
        </div>
        <div class="mapping-table-wrapper">
          <el-table :data="currentDeviceFieldMappings" stripe size="small" style="width: 100%" max-height="350" height="350">
            <el-table-column prop="rawField" label="Raw Field" min-width="140"><template #default="{ row }"><code>{{ row.rawField }}</code></template></el-table-column>
            <el-table-column label="→" width="40" align="center">→</el-table-column>
            <el-table-column prop="standardField" label="Standard Field" min-width="160"><template #default="{ row }"><el-tag size="small" type="success">{{ row.standardField }}</el-tag></template></el-table-column>
            <el-table-column prop="transform" label="Transform" min-width="100"><template #default="{ row }"><code>{{ row.transform || '-' }}</code></template></el-table-column>
            <el-table-column label="Range" min-width="100"><template #default="{ row }">{{ row.rangeMin !== null ? row.rangeMin : '-' }} ~ {{ row.rangeMax !== null ? row.rangeMax : '-' }}</template></el-table-column>
            <el-table-column label="Action" width="100" align="center">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editFieldMapping(row)">Edit</el-button>
                <el-button link type="danger" size="small" @click="deleteFieldMapping(row)">Del</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- Device Method Mapping -->
      <div class="section-card">
        <div class="section-header">
          <div class="section-title"><el-icon><Setting /></el-icon><span>Device Method Mapping (Standard → Raw)</span></div>
          <div class="mapping-device-selector">
            <span class="label">Device:</span>
            <el-select v-model="selectedMethodDevice" placeholder="Select device" size="small" filterable style="width: 260px">
              <el-option v-for="d in devices" :key="d.deviceCode" :label="`${d.deviceName} (${d.deviceCode})`" :value="d.deviceCode" />
            </el-select>
            <el-button type="primary" size="small" @click="addMethodMapping"><el-icon><Plus /></el-icon> Add Mapping</el-button>
          </div>
        </div>
        <div class="mapping-table-wrapper">
          <el-table :data="currentDeviceMethodMappings" stripe size="small" style="width: 100%" max-height="350" height="350">
            <el-table-column prop="standardMethod" label="Standard Method" min-width="160"><template #default="{ row }"><el-tag size="small" type="primary">{{ row.standardMethod }}</el-tag></template></el-table-column>
            <el-table-column label="→" width="40" align="center">→</el-table-column>
            <el-table-column prop="rawPath" label="Raw Path / Topic" min-width="220"><template #default="{ row }"><code>{{ row.rawPath }}</code></template></el-table-column>
            <el-table-column prop="direction" label="Direction" min-width="90"><template #default="{ row }"><el-tag :type="row.direction === 'downlink' ? 'warning' : 'success'" size="small">{{ row.direction }}</el-tag></template></el-table-column>
            <el-table-column prop="paramMapping" label="Param Mapping" min-width="120"><template #default="{ row }"><code>{{ row.paramMapping || 'value' }}</code></template></el-table-column>
            <el-table-column label="Action" width="100" align="center">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editMethodMapping(row)">Edit</el-button>
                <el-button link type="danger" size="small" @click="deleteMethodMapping(row)">Del</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- Real-time Message Stream -->
      <div class="stream-card">
        <div class="section-header">
          <div class="section-title"><el-icon><DataLine /></el-icon><span>Real-time Message Stream</span></div>
          <el-switch v-model="autoScroll" size="small" active-text="Auto Scroll" />
        </div>
        <div class="message-stream" ref="streamContainer">
          <div v-for="msg in messageStream" :key="msg.id" class="message-item">
            <span class="msg-time">{{ msg.time }}</span>
            <el-tag :type="getProtocolType(msg.protocol)" size="small">{{ msg.protocol }}</el-tag>
            <span class="msg-device">{{ msg.deviceCode }}</span>
            <span class="msg-direction" :class="msg.direction">{{ msg.direction === 'uplink' ? '↑ UPLINK' : '↓ DOWNLINK' }}</span>
            <span class="msg-data">{{ msg.data }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Dialogs -->
    <el-dialog v-model="addProtocolDialog" title="Add Protocol" width="480px">
      <el-form :model="newProtocol" label-width="100px">
        <el-form-item label="Protocol Name"><el-input v-model="newProtocol.name" /></el-form-item>
        <el-form-item label="Category"><el-input v-model="newProtocol.category" /></el-form-item>
        <el-form-item label="Version"><el-input v-model="newProtocol.version" /></el-form-item>
        <el-form-item label="Driver Class"><el-input v-model="newProtocol.driverClass" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="addProtocolDialog = false">Cancel</el-button><el-button type="primary" @click="saveProtocol">Save</el-button></template>
    </el-dialog>

    <el-dialog v-model="registerDeviceDialog" title="Register Device" width="520px">
      <el-form :model="newDevice" label-width="110px">
        <el-form-item label="Device Name"><el-input v-model="newDevice.deviceName" /></el-form-item>
        <el-form-item label="Device Code"><el-input v-model="newDevice.deviceCode" /></el-form-item>
        <el-form-item label="Protocol"><el-select v-model="newDevice.protocol" style="width: 100%"><el-option v-for="p in protocols" :key="p.name" :label="p.name" :value="p.name" /></el-select></el-form-item>
        <el-form-item label="Connect Config"><el-input v-model="newDevice.connectConfig" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="Parent DID"><el-input v-model="newDevice.parentDid" placeholder="Optional" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="registerDeviceDialog = false">Cancel</el-button><el-button type="primary" @click="saveDevice">Register</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, Cpu, Document, Timer, Plus, Share, Grid, DataLine, Setting, Link, Search } from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading modules...')
const loadingMessages = ['Loading modules...', 'Loading protocol registry...', 'Loading devices...', 'Loading mappings...', 'Almost ready...']

// ==================== Statistics ====================
const stats = ref({ activeConnections: 127, connectedDevices: 108, supportedProtocols: 42, avgLatency: 18, todayMessages: 284756, dataPoints: 15842 })

// ==================== Filter States ====================
const deviceSearch = ref('')
const protocolFilter = ref('')
const statusFilter = ref('')
const selectedMappingDevice = ref('HVAC_001')
const selectedMethodDevice = ref('HVAC_001')
const autoScroll = ref(true)
const streamContainer = ref(null)

// ==================== Protocols ====================
const protocols = ref([
  { name: 'Modbus TCP', category: 'Industrial', version: 'TCP', status: 'online', deviceCount: 23, driverClass: 'modbus_driver.ModbusDriver' },
  { name: 'Modbus RTU', category: 'Industrial', version: 'RTU', status: 'online', deviceCount: 15, driverClass: 'modbus_driver.ModbusRTUDriver' },
  { name: 'BACnet IP', category: 'Building', version: 'BACnet/IP', status: 'online', deviceCount: 34, driverClass: 'bacnet_driver.BACnetDriver' },
  { name: 'MQTT', category: 'IoT', version: '5.0', status: 'online', deviceCount: 56, driverClass: 'mqtt_driver.MQTTDriver' },
  { name: 'OPC UA', category: 'Industrial', version: '1.04', status: 'online', deviceCount: 12, driverClass: 'opcua_driver.OPCUADriver' },
  { name: 'KNX IP', category: 'Building', version: 'Routing', status: 'online', deviceCount: 9, driverClass: 'knx_driver.KNXIPDriver' },
  { name: 'DALI', category: 'Lighting', version: '2.0', status: 'online', deviceCount: 28, driverClass: 'dali_driver.DALIDriver' },
  { name: 'CoAP', category: 'IoT', version: 'RFC7252', status: 'online', deviceCount: 19, driverClass: 'coap_driver.CoAPDriver' },
  { name: 'REST API', category: 'Cloud', version: 'RESTful', status: 'online', deviceCount: 8, driverClass: 'rest_driver.RESTDriver' },
  { name: 'ONVIF', category: 'Video', version: 'Profile S/T', status: 'online', deviceCount: 31, driverClass: 'onvif_driver.ONVIFDriver' },
  { name: 'IEC 104', category: 'Energy', version: '104', status: 'online', deviceCount: 9, driverClass: 'iec104_driver.IEC104Driver' },
  { name: 'LoRaWAN', category: 'LPWAN', version: '1.0.4', status: 'online', deviceCount: 22, driverClass: 'lorawan_driver.LoRaWANDriver' }
])

// ==================== Devices ====================
const devices = ref([
  { deviceName: 'HVAC Rooftop Unit', deviceCode: 'HVAC_001', protocol: 'MQTT', status: 'online', did: 'did:ibms:device:hvac_001_xyz', lastSeen: '2 seconds ago' },
  { deviceName: 'AHU-03', deviceCode: 'AHU_003', protocol: 'BACnet IP', status: 'online', did: 'did:ibms:device:ahu_003_abc', lastSeen: '3 seconds ago' },
  { deviceName: 'Power Meter PM-101', deviceCode: 'PM_101', protocol: 'Modbus TCP', status: 'online', did: 'did:ibms:device:pm_101_def', lastSeen: '1 second ago' },
  { deviceName: 'Chiller Plant', deviceCode: 'CHILLER_01', protocol: 'OPC UA', status: 'online', did: 'did:ibms:device:chiller_01_stu', lastSeen: '5 seconds ago' },
  { deviceName: 'Lighting Controller', deviceCode: 'LIGHT_01', protocol: 'DALI', status: 'online', did: 'did:ibms:device:light_01_mno', lastSeen: '4 seconds ago' },
  { deviceName: 'Temperature Sensor', deviceCode: 'TEMP_01', protocol: 'CoAP', status: 'offline', did: 'did:ibms:device:temp_01_ghi', lastSeen: '2 hours ago' },
  { deviceName: 'Door Access', deviceCode: 'DOOR_001', protocol: 'KNX IP', status: 'online', did: 'did:ibms:device:door_001_pqr', lastSeen: '10 seconds ago' },
  { deviceName: 'VFD Fan', deviceCode: 'FAN_001', protocol: 'Modbus RTU', status: 'online', did: 'did:ibms:device:fan_001_stu', lastSeen: '6 seconds ago' },
  { deviceName: 'CO2 Sensor', deviceCode: 'CO2_001', protocol: 'LoRaWAN', status: 'online', did: 'did:ibms:device:co2_001_vwx', lastSeen: '30 seconds ago' },
  { deviceName: 'IP Camera', deviceCode: 'CAM_001', protocol: 'ONVIF', status: 'online', did: 'did:ibms:device:cam_001_yz', lastSeen: '2 seconds ago' }
])

const filteredDevices = computed(() => {
  let result = devices.value
  if (deviceSearch.value) result = result.filter(d => d.deviceName.toLowerCase().includes(deviceSearch.value.toLowerCase()) || d.deviceCode.toLowerCase().includes(deviceSearch.value.toLowerCase()))
  if (protocolFilter.value) result = result.filter(d => d.protocol === protocolFilter.value)
  if (statusFilter.value) result = result.filter(d => d.status === statusFilter.value)
  return result
})

// ==================== Standard Fields (带范围) ====================
const standardFields = ref([
  { fieldCode: 'temperature', fieldType: 'float', unit: '°C', rangeMin: -40, rangeMax: 85, isCritical: false },
  { fieldCode: 'temperature_setpoint', fieldType: 'float', unit: '°C', rangeMin: 16, rangeMax: 30, isCritical: false },
  { fieldCode: 'humidity', fieldType: 'float', unit: '%', rangeMin: 0, rangeMax: 100, isCritical: false },
  { fieldCode: 'co2', fieldType: 'float', unit: 'ppm', rangeMin: 300, rangeMax: 5000, isCritical: true },
  { fieldCode: 'pm2_5', fieldType: 'float', unit: 'µg/m³', rangeMin: 0, rangeMax: 500, isCritical: true },
  { fieldCode: 'pressure', fieldType: 'float', unit: 'kPa', rangeMin: 0, rangeMax: 1000, isCritical: false },
  { fieldCode: 'flow_rate', fieldType: 'float', unit: 'm³/h', rangeMin: 0, rangeMax: 10000, isCritical: false },
  { fieldCode: 'power', fieldType: 'float', unit: 'kW', rangeMin: 0, rangeMax: 5000, isCritical: true },
  { fieldCode: 'voltage', fieldType: 'float', unit: 'V', rangeMin: 0, rangeMax: 480, isCritical: false },
  { fieldCode: 'current', fieldType: 'float', unit: 'A', rangeMin: 0, rangeMax: 2000, isCritical: false },
  { fieldCode: 'energy_total', fieldType: 'float', unit: 'kWh', rangeMin: 0, rangeMax: 9999999, isCritical: true },
  { fieldCode: 'speed', fieldType: 'int', unit: 'rpm', rangeMin: 0, rangeMax: 3600, isCritical: false },
  { fieldCode: 'damper_position', fieldType: 'int', unit: '%', rangeMin: 0, rangeMax: 100, isCritical: false },
  { fieldCode: 'illuminance', fieldType: 'float', unit: 'lux', rangeMin: 0, rangeMax: 50000, isCritical: false },
  { fieldCode: 'battery_level', fieldType: 'int', unit: '%', rangeMin: 0, rangeMax: 100, isCritical: false },
  { fieldCode: 'rssi', fieldType: 'int', unit: 'dBm', rangeMin: -100, rangeMax: -30, isCritical: false },
  { fieldCode: 'device_status', fieldType: 'string', unit: '', rangeMin: null, rangeMax: null, isCritical: false },
  { fieldCode: 'error_code', fieldType: 'int', unit: '', rangeMin: 0, rangeMax: 999, isCritical: true }
])

// ==================== Standard Methods (带参数范围) ====================
const standardMethods = ref([
  { methodCode: 'set_temperature', category: 'control', paramName: 'value', paramType: 'float', paramRange: '16 ~ 30 °C' },
  { methodCode: 'set_humidity', category: 'control', paramName: 'value', paramType: 'float', paramRange: '30 ~ 80 %' },
  { methodCode: 'set_power', category: 'control', paramName: 'state', paramType: 'enum', paramRange: 'on, off' },
  { methodCode: 'set_fan_speed', category: 'control', paramName: 'speed', paramType: 'int', paramRange: '0 ~ 100 %' },
  { methodCode: 'set_damper', category: 'control', paramName: 'position', paramType: 'int', paramRange: '0 ~ 100 %' },
  { methodCode: 'set_light_brightness', category: 'control', paramName: 'level', paramType: 'int', paramRange: '0 ~ 100 %' },
  { methodCode: 'set_mode', category: 'control', paramName: 'mode', paramType: 'enum', paramRange: 'auto, cool, heat, fan, dry' },
  { methodCode: 'get_status', category: 'query', paramName: '', paramType: '', paramRange: '' },
  { methodCode: 'get_telemetry', category: 'query', paramName: 'fields', paramType: 'array', paramRange: 'temperature, humidity, power' },
  { methodCode: 'reboot_device', category: 'maintenance', paramName: 'delay', paramType: 'int', paramRange: '0 ~ 300 seconds' },
  { methodCode: 'clear_alarm', category: 'alarm', paramName: 'alarmCode', paramType: 'string', paramRange: 'A001~A999' },
  { methodCode: 'enable_energy_saving', category: 'energy', paramName: 'level', paramType: 'enum', paramRange: 'low, medium, high' }
])

// ==================== Device Field Mappings ====================
const allDeviceFieldMappings = ref([
  { deviceCode: 'HVAC_001', rawField: 'temp', standardField: 'temperature', transform: '*0.1', rangeMin: -40, rangeMax: 85 },
  { deviceCode: 'HVAC_001', rawField: 'sp', standardField: 'temperature_setpoint', transform: null, rangeMin: 16, rangeMax: 30 },
  { deviceCode: 'HVAC_001', rawField: 'humi', standardField: 'humidity', transform: null, rangeMin: 0, rangeMax: 100 },
  { deviceCode: 'HVAC_001', rawField: 'pwr', standardField: 'power', transform: '/1000', rangeMin: 0, rangeMax: 5000 },
  { deviceCode: 'HVAC_001', rawField: 'fan', standardField: 'speed', transform: null, rangeMin: 0, rangeMax: 3600 },
  { deviceCode: 'HVAC_001', rawField: 'damper', standardField: 'damper_position', transform: null, rangeMin: 0, rangeMax: 100 },
  { deviceCode: 'HVAC_001', rawField: 'stat', standardField: 'device_status', transform: null, rangeMin: null, rangeMax: null },
  { deviceCode: 'HVAC_001', rawField: 'err', standardField: 'error_code', transform: null, rangeMin: 0, rangeMax: 999 },
  { deviceCode: 'HVAC_001', rawField: 'co2', standardField: 'co2', transform: null, rangeMin: 300, rangeMax: 5000 },
  { deviceCode: 'HVAC_001', rawField: 'rssi', standardField: 'rssi', transform: null, rangeMin: -100, rangeMax: -30 },
  { deviceCode: 'AHU_003', rawField: 'temp_in', standardField: 'temperature', transform: '*0.1', rangeMin: -40, rangeMax: 85 },
  { deviceCode: 'AHU_003', rawField: 'flow', standardField: 'flow_rate', transform: null, rangeMin: 0, rangeMax: 10000 },
  { deviceCode: 'AHU_003', rawField: 'damper', standardField: 'damper_position', transform: null, rangeMin: 0, rangeMax: 100 },
  { deviceCode: 'AHU_003', rawField: 'stat', standardField: 'device_status', transform: null, rangeMin: null, rangeMax: null },
  { deviceCode: 'AHU_003', rawField: 'co2', standardField: 'co2', transform: null, rangeMin: 300, rangeMax: 5000 },
  { deviceCode: 'PM_101', rawField: 'V', standardField: 'voltage', transform: '/10', rangeMin: 0, rangeMax: 480 },
  { deviceCode: 'PM_101', rawField: 'A', standardField: 'current', transform: '/100', rangeMin: 0, rangeMax: 2000 },
  { deviceCode: 'PM_101', rawField: 'kW', standardField: 'power', transform: null, rangeMin: 0, rangeMax: 5000 },
  { deviceCode: 'PM_101', rawField: 'kWh', standardField: 'energy_total', transform: null, rangeMin: 0, rangeMax: 9999999 },
  { deviceCode: 'PM_101', rawField: 'PF', standardField: 'power_factor', transform: '/100', rangeMin: 0, rangeMax: 100 },
  { deviceCode: 'CHILLER_01', rawField: 'temp_evap', standardField: 'temperature', transform: null, rangeMin: -40, rangeMax: 85 },
  { deviceCode: 'CHILLER_01', rawField: 'pres_suc', standardField: 'pressure', transform: null, rangeMin: 0, rangeMax: 1000 },
  { deviceCode: 'CHILLER_01', rawField: 'load', standardField: 'power', transform: null, rangeMin: 0, rangeMax: 5000 },
  { deviceCode: 'CHILLER_01', rawField: 'stat', standardField: 'device_status', transform: null, rangeMin: null, rangeMax: null },
  { deviceCode: 'LIGHT_01', rawField: 'lux', standardField: 'illuminance', transform: null, rangeMin: 0, rangeMax: 50000 },
  { deviceCode: 'LIGHT_01', rawField: 'dim', standardField: 'damper_position', transform: null, rangeMin: 0, rangeMax: 100 },
  { deviceCode: 'LIGHT_01', rawField: 'stat', standardField: 'device_status', transform: null, rangeMin: null, rangeMax: null },
  { deviceCode: 'TEMP_01', rawField: 't', standardField: 'temperature', transform: '*0.1', rangeMin: -40, rangeMax: 85 },
  { deviceCode: 'TEMP_01', rawField: 'h', standardField: 'humidity', transform: null, rangeMin: 0, rangeMax: 100 },
  { deviceCode: 'TEMP_01', rawField: 'bat', standardField: 'battery_level', transform: null, rangeMin: 0, rangeMax: 100 },
  { deviceCode: 'DOOR_001', rawField: 'door', standardField: 'door_status', transform: null, rangeMin: null, rangeMax: null },
  { deviceCode: 'DOOR_001', rawField: 'bat', standardField: 'battery_level', transform: null, rangeMin: 0, rangeMax: 100 },
  { deviceCode: 'FAN_001', rawField: 'spd', standardField: 'speed', transform: null, rangeMin: 0, rangeMax: 3600 },
  { deviceCode: 'FAN_001', rawField: 'stat', standardField: 'device_status', transform: null, rangeMin: null, rangeMax: null },
  { deviceCode: 'CO2_001', rawField: 'co2', standardField: 'co2', transform: null, rangeMin: 300, rangeMax: 5000 },
  { deviceCode: 'CO2_001', rawField: 'pm25', standardField: 'pm2_5', transform: null, rangeMin: 0, rangeMax: 500 }
])

const currentDeviceFieldMappings = computed(() => {
  return allDeviceFieldMappings.value.filter(m => m.deviceCode === selectedMappingDevice.value)
})

// ==================== Device Method Mappings ====================
const allDeviceMethodMappings = ref([
  { deviceCode: 'HVAC_001', standardMethod: 'set_temperature', rawPath: 'building/hvac/command', direction: 'downlink', paramMapping: 'setpoint' },
  { deviceCode: 'HVAC_001', standardMethod: 'set_power', rawPath: 'building/hvac/command', direction: 'downlink', paramMapping: 'state' },
  { deviceCode: 'HVAC_001', standardMethod: 'set_fan_speed', rawPath: 'building/hvac/command', direction: 'downlink', paramMapping: 'speed' },
  { deviceCode: 'HVAC_001', standardMethod: 'set_mode', rawPath: 'building/hvac/command', direction: 'downlink', paramMapping: 'mode' },
  { deviceCode: 'HVAC_001', standardMethod: 'get_status', rawPath: 'building/hvac/status', direction: 'uplink', paramMapping: '' },
  { deviceCode: 'HVAC_001', standardMethod: 'reboot_device', rawPath: 'building/hvac/system/reboot', direction: 'downlink', paramMapping: 'delay' },
  { deviceCode: 'AHU_003', standardMethod: 'set_temperature', rawPath: 'building/ahu/command', direction: 'downlink', paramMapping: 'setpoint' },
  { deviceCode: 'AHU_003', standardMethod: 'set_damper', rawPath: 'building/ahu/command', direction: 'downlink', paramMapping: 'position' },
  { deviceCode: 'AHU_003', standardMethod: 'get_status', rawPath: 'building/ahu/status', direction: 'uplink', paramMapping: '' },
  { deviceCode: 'PM_101', standardMethod: 'get_energy_report', rawPath: 'energy/power/query', direction: 'uplink', paramMapping: '' },
  { deviceCode: 'PM_101', standardMethod: 'set_power', rawPath: 'energy/power/control', direction: 'downlink', paramMapping: 'state' },
  { deviceCode: 'CHILLER_01', standardMethod: 'set_temperature', rawPath: 'hvac/chiller/command', direction: 'downlink', paramMapping: 'setpoint' },
  { deviceCode: 'CHILLER_01', standardMethod: 'get_status', rawPath: 'hvac/chiller/status', direction: 'uplink', paramMapping: '' },
  { deviceCode: 'CHILLER_01', standardMethod: 'reboot_device', rawPath: 'hvac/chiller/system/reboot', direction: 'downlink', paramMapping: 'delay' },
  { deviceCode: 'LIGHT_01', standardMethod: 'set_light_brightness', rawPath: 'lighting/control', direction: 'downlink', paramMapping: 'level' },
  { deviceCode: 'LIGHT_01', standardMethod: 'set_power', rawPath: 'lighting/control', direction: 'downlink', paramMapping: 'state' },
  { deviceCode: 'LIGHT_01', standardMethod: 'get_status', rawPath: 'lighting/status', direction: 'uplink', paramMapping: '' },
  { deviceCode: 'TEMP_01', standardMethod: 'get_telemetry', rawPath: 'sensors/temperature/data', direction: 'uplink', paramMapping: '' },
  { deviceCode: 'DOOR_001', standardMethod: 'get_status', rawPath: 'access/door/status', direction: 'uplink', paramMapping: '' },
  { deviceCode: 'DOOR_001', standardMethod: 'set_power', rawPath: 'access/door/control', direction: 'downlink', paramMapping: 'state' },
  { deviceCode: 'FAN_001', standardMethod: 'set_power', rawPath: 'hvac/fan/command', direction: 'downlink', paramMapping: 'state' },
  { deviceCode: 'FAN_001', standardMethod: 'get_status', rawPath: 'hvac/fan/status', direction: 'uplink', paramMapping: '' }
])

const currentDeviceMethodMappings = computed(() => {
  return allDeviceMethodMappings.value.filter(m => m.deviceCode === selectedMethodDevice.value)
})

// ==================== Message Stream ====================
const messageStream = ref([
  { id: 1, time: '10:23:15', protocol: 'MQTT', deviceCode: 'HVAC_001', direction: 'uplink', data: '{"temp":235,"humi":65,"pwr":12.5,"stat":"running"}' },
  { id: 2, time: '10:23:12', protocol: 'BACnet IP', deviceCode: 'AHU_003', direction: 'uplink', data: 'AnalogInput:1=23.5, AnalogInput:2=18.2' },
  { id: 3, time: '10:23:08', protocol: 'Modbus TCP', deviceCode: 'PM_101', direction: 'uplink', data: 'Register 40001=1245, 40002=892' },
  { id: 4, time: '10:23:05', protocol: 'MQTT', deviceCode: 'HVAC_001', direction: 'downlink', data: '{"command":"set_setpoint","value":24}' },
  { id: 5, time: '10:23:01', protocol: 'OPC UA', deviceCode: 'CHILLER_01', direction: 'uplink', data: 'Temperature=7.2°C, Pressure=520kPa' }
])

// ==================== Helper Methods ====================
const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const truncateDid = (did) => {
  if (!did) return ''
  return did.length > 35 ? did.substring(0, 32) + '...' : did
}

const getProtocolType = (protocol) => {
  const map = { MQTT: 'warning', 'BACnet IP': 'success', 'Modbus TCP': 'primary', 'OPC UA': 'info', CoAP: 'danger', DALI: 'success', 'KNX IP': 'primary' }
  return map[protocol] || 'info'
}

const getRandomLatency = () => Math.floor(Math.random() * 50) + 10

// ==================== Actions ====================
const openAddProtocol = () => { addProtocolDialog.value = true }
const saveProtocol = () => { ElMessage.success('Protocol added'); addProtocolDialog.value = false }
const editProtocol = (p) => { ElMessage.info(`Configuring ${p.name}`) }
const testConnection = (p) => { ElMessage.success(`${p.name} connection successful! Latency: ${getRandomLatency()}ms`) }

const openRegisterDevice = () => { registerDeviceDialog.value = true }
const saveDevice = () => { ElMessage.success('Device registered with DID'); registerDeviceDialog.value = false }
const viewDevice = (d) => { ElMessage.info(`Viewing ${d.deviceName}`) }
const editDevice = (d) => { ElMessage.info(`Editing ${d.deviceName}`) }
const deleteDevice = async (d) => { try { await ElMessageBox.confirm(`Delete "${d.deviceName}"?`, 'Confirm'); ElMessage.success('Deleted') } catch {} }

// 标准字段操作
const addStandardField = () => { ElMessage.info('Add standard field dialog') }
const editStandardField = (row) => { ElMessage.info(`Editing field: ${row.fieldCode}`) }
const deleteStandardField = async (row) => {
  try { await ElMessageBox.confirm(`Delete field "${row.fieldCode}"?`, 'Confirm'); ElMessage.success('Deleted') } catch {}
}

// 标准方法操作
const addStandardMethod = () => { ElMessage.info('Add standard method dialog') }
const editStandardMethod = (row) => { ElMessage.info(`Editing method: ${row.methodCode}`) }
const deleteStandardMethod = async (row) => {
  try { await ElMessageBox.confirm(`Delete method "${row.methodCode}"?`, 'Confirm'); ElMessage.success('Deleted') } catch {}
}

// 字段映射操作
const addFieldMapping = () => { ElMessage.info('Add field mapping dialog') }
const editFieldMapping = (row) => { ElMessage.info(`Editing mapping: ${row.rawField} → ${row.standardField}`) }
const deleteFieldMapping = async (row) => {
  try { await ElMessageBox.confirm(`Delete mapping "${row.rawField}"?`, 'Confirm'); ElMessage.success('Deleted') } catch {}
}

// 方法映射操作
const addMethodMapping = () => { ElMessage.info('Add method mapping dialog') }
const editMethodMapping = (row) => { ElMessage.info(`Editing mapping: ${row.standardMethod} → ${row.rawPath}`) }
const deleteMethodMapping = async (row) => {
  try { await ElMessageBox.confirm(`Delete mapping "${row.standardMethod}"?`, 'Confirm'); ElMessage.success('Deleted') } catch {}
}

// ==================== Dialog States ====================
const addProtocolDialog = ref(false)
const registerDeviceDialog = ref(false)
const newProtocol = ref({ name: '', category: '', version: '', driverClass: '' })
const newDevice = ref({ deviceName: '', deviceCode: '', protocol: '', connectConfig: '', parentDid: '' })

// ==================== Message Simulation ====================
let messageInterval = null
const startMessageSimulation = () => {
  messageInterval = setInterval(() => {
    const devicesList = ['HVAC_001', 'AHU_003', 'PM_101', 'CHILLER_01']
    const protocolsList = ['MQTT', 'BACnet IP', 'Modbus TCP', 'OPC UA']
    const newMsg = {
      id: Date.now(), time: new Date().toLocaleTimeString(),
      protocol: protocolsList[Math.floor(Math.random() * protocolsList.length)],
      deviceCode: devicesList[Math.floor(Math.random() * devicesList.length)],
      direction: Math.random() > 0.7 ? 'downlink' : 'uplink',
      data: `Value = ${(Math.random() * 100).toFixed(1)}`
    }
    messageStream.value.unshift(newMsg)
    if (messageStream.value.length > 20) messageStream.value.pop()
    if (autoScroll.value && streamContainer.value) nextTick(() => { streamContainer.value.scrollTop = 0 })
  }, 4000)
}

// ==================== Loading ====================
let progressInterval = null, messageIntervalLoad = null
const startLoading = () => {
  let messageIndex = 0
  messageIntervalLoad = setInterval(() => { if (messageIndex < loadingMessages.length - 1) { messageIndex++; loadingMessage.value = loadingMessages[messageIndex] } }, 600)
  progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 12 + 4; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 150)
  setTimeout(() => {
    clearInterval(messageIntervalLoad); clearInterval(progressInterval)
    loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true }, 400)
  }, 2500)
}

onMounted(() => { startLoading(); startMessageSimulation() })
onBeforeUnmount(() => {
  if (progressInterval) clearInterval(progressInterval)
  if (messageIntervalLoad) clearInterval(messageIntervalLoad)
  if (messageInterval) clearInterval(messageInterval)
})
</script>

<style scoped>
.protocol-hub { padding: 24px; background: #f0f2f6; min-height: 100%; }

/* Loading Screen */
.loading-container { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-overlay { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: fadeInUp 0.6s ease-out; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.page-header { margin-bottom: 24px; }
.page-header h1 { margin: 0 0 6px 0; font-size: 26px; font-weight: 600; color: #1a2c3e; }
.subtitle { margin: 0; font-size: 13px; color: #6c757d; }

/* Stats Cards */
.stats-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin-bottom: 24px; }
.stat-card { background: white; border-radius: 16px; padding: 16px; display: flex; align-items: center; gap: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); transition: all 0.2s; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08); }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: 700; color: #1a2c3e; }
.stat-unit { font-size: 12px; font-weight: 400; color: #6c757d; margin-left: 2px; }
.stat-label { font-size: 11px; color: #6c757d; margin-top: 2px; }

/* Section Cards */
.section-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); margin-bottom: 20px; }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.section-title { display: flex; align-items: center; gap: 8px; font-size: 16px; font-weight: 600; color: #1a2c3e; }

/* Status */
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background: #f56c6c; }
.driver-name { font-family: monospace; font-size: 12px; color: #6c757d; }
.did-text { font-family: monospace; font-size: 11px; color: #909399; }

/* Two Columns */
.dashboard-two-columns { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }

/* Mapping */
.mapping-device-selector { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.mapping-device-selector .label { font-size: 12px; font-weight: 500; color: #6c757d; }
.mapping-table-wrapper { overflow-x: auto; margin-top: 12px; }

/* Message Stream */
.stream-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); }
.message-stream { background: #1a2c3e; border-radius: 12px; padding: 16px; height: 260px; overflow-y: auto; margin-top: 12px;scrollbar-width: none; -ms-overflow-style: none; }
.message-item { display: flex; align-items: center; gap: 12px; padding: 8px 12px; border-radius: 8px; margin-bottom: 8px; background: rgba(255, 255, 255, 0.05); }
.msg-time { font-size: 11px; color: #94a3b8; min-width: 70px; font-family: monospace; }
.msg-device { font-size: 11px; color: #94a3b8; min-width: 90px; font-family: monospace; }
.msg-direction { font-size: 10px; font-weight: bold; padding: 2px 8px; border-radius: 12px; }
.msg-direction.uplink { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.msg-direction.downlink { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.msg-data { font-size: 12px; color: #e2e8f0; word-break: break-all; flex: 1; font-family: monospace; }

/* Table Styles */
.el-table .el-table__cell { text-align: center; }
.el-table__body-wrapper { overflow-x: auto; }

/* Responsive */
@media (max-width: 1200px) { .stats-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 1024px) { .dashboard-two-columns { grid-template-columns: 1fr; } }
@media (max-width: 768px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
</style>