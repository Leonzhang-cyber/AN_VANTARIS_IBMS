<template>
  <div class="rack-inventory-container">
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
            <span class="loading-title">Loading Rack Inventory</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Rack Inventory Management</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="rack-inventory-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Rack Inventory</h1>
          <p class="page-subtitle">Manage all racks and equipment in your data center</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="openAddRackDialog">
            <el-icon><Plus /></el-icon>
            Add Rack
          </el-button>
          <el-button @click="exportInventory">
            <el-icon><Download /></el-icon>
            Export Inventory
          </el-button>
          <el-button @click="importInventory">
            <el-icon><Upload /></el-icon>
            Import
          </el-button>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <el-card class="filters-card" shadow="never">
          <div class="filters-row">
            <el-input
                v-model="searchQuery"
                placeholder="Search by rack name, location..."
                prefix-icon="Search"
                style="width: 250px"
                clearable
            />
            <el-select v-model="filterRow" placeholder="Filter by Row" clearable style="width: 120px">
              <el-option label="Row A" value="A" />
              <el-option label="Row B" value="B" />
              <el-option label="Row C" value="C" />
              <el-option label="Row D" value="D" />
            </el-select>
            <el-select v-model="filterStatus" placeholder="Filter by Status" clearable style="width: 140px">
              <el-option label="Normal" value="Normal" />
              <el-option label="Warning" value="Warning" />
              <el-option label="Critical" value="Critical" />
            </el-select>
            <el-select v-model="filterUtilization" placeholder="Utilization" clearable style="width: 140px">
              <el-option label="&lt; 50%" value="low" />
              <el-option label="50% - 70%" value="medium" />
              <el-option label="70% - 85%" value="high" />
              <el-option label="&gt; 85%" value="critical" />
            </el-select>
            <el-button type="primary" @click="clearFilters">Clear Filters</el-button>
          </div>
        </el-card>
      </div>

      <!-- Rack Cards Grid -->
      <div class="racks-grid">
        <div
            v-for="rack in filteredRacks"
            :key="rack.id"
            class="rack-card"
            :class="{
            'status-warning': rack.status === 'Warning',
            'status-critical': rack.status === 'Critical'
          }"
            @click="viewRackDetail(rack)"
        >
          <div class="rack-card-header">
            <div class="rack-title">
              <span class="rack-name">{{ rack.name }}</span>
              <span class="rack-location">{{ rack.row }}{{ rack.position }}</span>
            </div>
            <el-tag :type="getStatusTagType(rack.status)" size="small">
              {{ rack.status }}
            </el-tag>
          </div>

          <div class="rack-card-stats">
            <div class="stat-item">
              <span class="stat-label">U Space</span>
              <span class="stat-value">{{ rack.usedU }}/{{ rack.totalU }} U</span>
              <el-progress :percentage="(rack.usedU / rack.totalU) * 100" :stroke-width="6" :color="getUtilColor((rack.usedU / rack.totalU) * 100)" :show-text="false" />
            </div>
            <div class="stat-item">
              <span class="stat-label">Power</span>
              <span class="stat-value">{{ rack.power }} / {{ rack.maxPower }} kW</span>
              <el-progress :percentage="(rack.power / rack.maxPower) * 100" :stroke-width="6" :color="getPowerColor((rack.power / rack.maxPower) * 100)" :show-text="false" />
            </div>
            <div class="stat-item">
              <span class="stat-label">Devices</span>
              <span class="stat-value">{{ rack.deviceCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Utilization</span>
              <span class="stat-value" :style="{ color: getUtilColor((rack.usedU / rack.totalU) * 100) }">
                {{ ((rack.usedU / rack.totalU) * 100).toFixed(1) }}%
              </span>
            </div>
          </div>

          <div class="rack-card-footer">
            <div class="quick-stats">
              <div class="quick-stat">
                <span class="dot" :class="{ 'success': rack.availableU > 10, 'warning': rack.availableU <= 10 && rack.availableU > 5, 'danger': rack.availableU <= 5 }"></span>
                <span>{{ rack.availableU }}U free</span>
              </div>
              <div class="quick-stat">
                <span class="dot" :class="{ 'success': (rack.maxPower - rack.power) > 5, 'warning': (rack.maxPower - rack.power) <= 5 && (rack.maxPower - rack.power) > 2, 'danger': (rack.maxPower - rack.power) <= 2 }"></span>
                <span>{{ (rack.maxPower - rack.power).toFixed(1) }} kW free</span>
              </div>
            </div>
            <div class="rack-actions">
              <el-button size="small" @click.stop="viewDevices(rack)">Devices</el-button>
              <el-button size="small" type="primary" @click.stop="editRack(rack)">Edit</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Summary Statistics -->
      <div class="summary-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon blue">
                <el-icon><Grid /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Total Racks</span>
                <span class="summary-value">{{ filteredRacks.length }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon green">
                <el-icon><Menu /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Total U Space</span>
                <span class="summary-value">{{ totalUSpace }} U</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon orange">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Total Power</span>
                <span class="summary-value">{{ totalPower }} kW</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon purple">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Total Devices</span>
                <span class="summary-value">{{ totalDevices }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Rack Detail Dialog -->
      <el-dialog v-model="detailDialogVisible" :title="`Rack ${selectedRack?.name} - Device List`" width="900px" class="detail-dialog">
        <div class="rack-detail-header">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="Location">{{ selectedRack?.row }}{{ selectedRack?.position }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="getStatusTagType(selectedRack?.status)">{{ selectedRack?.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="U Space">{{ selectedRack?.usedU }}/{{ selectedRack?.totalU }} U</el-descriptions-item>
            <el-descriptions-item label="Power">{{ selectedRack?.power }}/{{ selectedRack?.maxPower }} kW</el-descriptions-item>
            <el-descriptions-item label="Utilization">{{ ((selectedRack?.usedU / selectedRack?.totalU) * 100).toFixed(1) }}%</el-descriptions-item>
            <el-descriptions-item label="Devices">{{ selectedRack?.deviceCount }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="rack-detail-devices">
          <div class="device-list-header">
            <h4>Installed Devices</h4>
            <el-button size="small" type="primary" @click="openAddDeviceDialog">
              <el-icon><Plus /></el-icon>
              Add Device
            </el-button>
          </div>
          <el-table :data="selectedRack?.devices || []" border stripe>
            <el-table-column prop="name" label="Device Name" min-width="150" />
            <el-table-column prop="model" label="Model" width="140" />
            <el-table-column prop="manufacturer" label="Manufacturer" width="120" />
            <el-table-column prop="uPosition" label="U Position" width="100" />
            <el-table-column prop="uSize" label="Size (U)" width="80" />
            <el-table-column prop="power" label="Power (W)" width="100" />
            <el-table-column label="Actions" width="120">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="editDevice(row)">Edit</el-button>
                <el-button type="danger" link size="small" @click="removeDevice(row)">Remove</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <template #footer>
          <el-button @click="detailDialogVisible = false">Close</el-button>
          <el-button type="primary" @click="editRack(selectedRack)">Edit Rack</el-button>
        </template>
      </el-dialog>

      <!-- Add/Edit Rack Dialog -->
      <el-dialog v-model="rackDialogVisible" :title="rackDialogTitle" width="550px">
        <el-form :model="rackForm" :rules="rackRules" ref="rackFormRef" label-width="100px">
          <el-form-item label="Rack Name" prop="name">
            <el-input v-model="rackForm.name" placeholder="e.g., A01" />
          </el-form-item>
          <el-form-item label="Row" prop="row">
            <el-select v-model="rackForm.row" placeholder="Select Row">
              <el-option label="Row A" value="A" />
              <el-option label="Row B" value="B" />
              <el-option label="Row C" value="C" />
              <el-option label="Row D" value="D" />
            </el-select>
          </el-form-item>
          <el-form-item label="Position" prop="position">
            <el-input-number v-model="rackForm.position" :min="1" :max="20" />
          </el-form-item>
          <el-form-item label="Total U" prop="totalU">
            <el-select v-model="rackForm.totalU">
              <el-option label="42U" :value="42" />
              <el-option label="45U" :value="45" />
              <el-option label="48U" :value="48" />
            </el-select>
          </el-form-item>
          <el-form-item label="Max Power (kW)" prop="maxPower">
            <el-input-number v-model="rackForm.maxPower" :min="5" :max="50" :step="5" />
          </el-form-item>
          <el-form-item label="PDU Type">
            <el-select v-model="rackForm.pduType" placeholder="Select PDU Type">
              <el-option label="Single-phase" value="single" />
              <el-option label="Three-phase" value="three" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="rackDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveRack">Save</el-button>
        </template>
      </el-dialog>

      <!-- Add/Edit Device Dialog -->
      <el-dialog v-model="deviceDialogVisible" :title="deviceDialogTitle" width="550px">
        <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="100px">
          <el-form-item label="Device Name" prop="name">
            <el-input v-model="deviceForm.name" placeholder="e.g., Dell PowerEdge R750" />
          </el-form-item>
          <el-form-item label="Model" prop="model">
            <el-input v-model="deviceForm.model" placeholder="e.g., R750" />
          </el-form-item>
          <el-form-item label="Manufacturer" prop="manufacturer">
            <el-input v-model="deviceForm.manufacturer" placeholder="e.g., Dell" />
          </el-form-item>
          <el-form-item label="U Position" prop="uPosition">
            <el-input-number v-model="deviceForm.uPosition" :min="1" :max="rackForm.totalU || 42" />
          </el-form-item>
          <el-form-item label="Size (U)" prop="uSize">
            <el-select v-model="deviceForm.uSize">
              <el-option label="1U" :value="1" />
              <el-option label="2U" :value="2" />
              <el-option label="3U" :value="3" />
              <el-option label="4U" :value="4" />
              <el-option label="6U" :value="6" />
              <el-option label="8U" :value="8" />
            </el-select>
          </el-form-item>
          <el-form-item label="Power (W)" prop="power">
            <el-input-number v-model="deviceForm.power" :min="0" :step="50" />
          </el-form-item>
          <el-form-item label="Serial Number">
            <el-input v-model="deviceForm.serialNumber" placeholder="Optional" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="deviceDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveDevice">Save</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, Upload, Grid, Menu, Cpu, Monitor } from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading rack inventory...')

// ==================== Reactive Data ====================
const searchQuery = ref('')
const filterRow = ref('')
const filterStatus = ref('')
const filterUtilization = ref('')
const detailDialogVisible = ref(false)
const rackDialogVisible = ref(false)
const deviceDialogVisible = ref(false)
const rackDialogTitle = ref('Add Rack')
const deviceDialogTitle = ref('Add Device')
const selectedRack = ref<any>(null)
const editingDevice = ref<any>(null)

// Form refs
const rackFormRef = ref()
const deviceFormRef = ref()

// Form data
const rackForm = ref({
  id: null,
  name: '',
  row: 'A',
  position: 1,
  totalU: 42,
  maxPower: 15,
  pduType: 'three',
  usedU: 0,
  power: 0,
  status: 'Normal',
  devices: [],
  deviceCount: 0,
  availableU: 42
})

const deviceForm = ref({
  name: '',
  model: '',
  manufacturer: '',
  uPosition: 1,
  uSize: 1,
  power: 0,
  serialNumber: ''
})

// Form rules
const rackRules = {
  name: [{ required: true, message: 'Please enter rack name', trigger: 'blur' }],
  row: [{ required: true, message: 'Please select row', trigger: 'change' }],
  position: [{ required: true, message: 'Please enter position', trigger: 'blur' }],
  totalU: [{ required: true, message: 'Please select total U', trigger: 'change' }],
  maxPower: [{ required: true, message: 'Please enter max power', trigger: 'blur' }]
}

const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  model: [{ required: true, message: 'Please enter model', trigger: 'blur' }],
  manufacturer: [{ required: true, message: 'Please enter manufacturer', trigger: 'blur' }],
  uPosition: [{ required: true, message: 'Please enter U position', trigger: 'blur' }],
  uSize: [{ required: true, message: 'Please select size', trigger: 'change' }]
}

// Rack data
const racks = ref([
  {
    id: 1, name: 'A01', row: 'A', position: 1, totalU: 42, usedU: 38, availableU: 4,
    power: 8.5, maxPower: 15, status: 'Normal', deviceCount: 12,
    devices: [
      { name: 'Web Server-01', model: 'R750', manufacturer: 'Dell', uPosition: 1, uSize: 2, power: 450, serialNumber: 'DL12345' },
      { name: 'Web Server-02', model: 'R750', manufacturer: 'Dell', uPosition: 3, uSize: 2, power: 450, serialNumber: 'DL12346' },
      { name: 'Storage Array', model: 'AFF A250', manufacturer: 'NetApp', uPosition: 5, uSize: 4, power: 600, serialNumber: 'NT98765' },
      { name: 'Switch-01', model: '9300', manufacturer: 'Cisco', uPosition: 9, uSize: 1, power: 150, serialNumber: 'CS54321' }
    ]
  },
  { id: 2, name: 'A02', row: 'A', position: 2, totalU: 42, usedU: 35, availableU: 7, power: 7.8, maxPower: 15, status: 'Normal', deviceCount: 11, devices: [] },
  { id: 3, name: 'A03', row: 'A', position: 3, totalU: 42, usedU: 40, availableU: 2, power: 12.5, maxPower: 15, status: 'Warning', deviceCount: 14, devices: [] },
  { id: 4, name: 'A04', row: 'A', position: 4, totalU: 42, usedU: 28, availableU: 14, power: 6.2, maxPower: 15, status: 'Normal', deviceCount: 9, devices: [] },
  { id: 5, name: 'A05', row: 'A', position: 5, totalU: 42, usedU: 42, availableU: 0, power: 14.2, maxPower: 15, status: 'Critical', deviceCount: 16, devices: [] },
  { id: 6, name: 'B01', row: 'B', position: 1, totalU: 42, usedU: 36, availableU: 6, power: 8.2, maxPower: 15, status: 'Normal', deviceCount: 12, devices: [] },
  { id: 7, name: 'B02', row: 'B', position: 2, totalU: 42, usedU: 32, availableU: 10, power: 7.2, maxPower: 15, status: 'Normal', deviceCount: 10, devices: [] },
  { id: 8, name: 'B03', row: 'B', position: 3, totalU: 42, usedU: 38, availableU: 4, power: 9.5, maxPower: 15, status: 'Normal', deviceCount: 13, devices: [] },
  { id: 9, name: 'B04', row: 'B', position: 4, totalU: 42, usedU: 30, availableU: 12, power: 6.8, maxPower: 15, status: 'Normal', deviceCount: 9, devices: [] },
  { id: 10, name: 'B05', row: 'B', position: 5, totalU: 42, usedU: 35, availableU: 7, power: 8.0, maxPower: 15, status: 'Normal', deviceCount: 11, devices: [] },
  { id: 11, name: 'C01', row: 'C', position: 1, totalU: 42, usedU: 34, availableU: 8, power: 7.5, maxPower: 15, status: 'Normal', deviceCount: 10, devices: [] },
  { id: 12, name: 'C02', row: 'C', position: 2, totalU: 42, usedU: 28, availableU: 14, power: 6.0, maxPower: 15, status: 'Normal', deviceCount: 8, devices: [] },
  { id: 13, name: 'C03', row: 'C', position: 3, totalU: 42, usedU: 40, availableU: 2, power: 11.0, maxPower: 15, status: 'Warning', deviceCount: 13, devices: [] },
  { id: 14, name: 'C04', row: 'C', position: 4, totalU: 42, usedU: 25, availableU: 17, power: 5.5, maxPower: 15, status: 'Normal', deviceCount: 7, devices: [] },
  { id: 15, name: 'C05', row: 'C', position: 5, totalU: 42, usedU: 38, availableU: 4, power: 8.8, maxPower: 15, status: 'Normal', deviceCount: 12, devices: [] },
  { id: 16, name: 'D01', row: 'D', position: 1, totalU: 42, usedU: 32, availableU: 10, power: 7.0, maxPower: 15, status: 'Normal', deviceCount: 10, devices: [] },
  { id: 17, name: 'D02', row: 'D', position: 2, totalU: 42, usedU: 28, availableU: 14, power: 6.2, maxPower: 15, status: 'Normal', deviceCount: 8, devices: [] },
  { id: 18, name: 'D03', row: 'D', position: 3, totalU: 42, usedU: 35, availableU: 7, power: 7.8, maxPower: 15, status: 'Normal', deviceCount: 11, devices: [] },
  { id: 19, name: 'D04', row: 'D', position: 4, totalU: 42, usedU: 30, availableU: 12, power: 6.5, maxPower: 15, status: 'Normal', deviceCount: 9, devices: [] },
  { id: 20, name: 'D05', row: 'D', position: 5, totalU: 42, usedU: 38, availableU: 4, power: 8.5, maxPower: 15, status: 'Normal', deviceCount: 12, devices: [] }
])

// Computed
const filteredRacks = computed(() => {
  let result = racks.value

  if (searchQuery.value) {
    result = result.filter(r =>
        r.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        `${r.row}${r.position}`.includes(searchQuery.value)
    )
  }

  if (filterRow.value) {
    result = result.filter(r => r.row === filterRow.value)
  }

  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value)
  }

  if (filterUtilization.value) {
    result = result.filter(r => {
      const util = (r.usedU / r.totalU) * 100
      if (filterUtilization.value === 'low') return util < 50
      if (filterUtilization.value === 'medium') return util >= 50 && util < 70
      if (filterUtilization.value === 'high') return util >= 70 && util < 85
      if (filterUtilization.value === 'critical') return util >= 85
      return true
    })
  }

  return result
})

const totalUSpace = computed(() => {
  return filteredRacks.value.reduce((sum, r) => sum + r.usedU, 0)
})

const totalPower = computed(() => {
  return filteredRacks.value.reduce((sum, r) => sum + r.power, 0).toFixed(1)
})

const totalDevices = computed(() => {
  return filteredRacks.value.reduce((sum, r) => sum + r.deviceCount, 0)
})

// Helper functions
const getStatusTagType = (status: string) => {
  if (status === 'Critical') return 'danger'
  if (status === 'Warning') return 'warning'
  return 'success'
}

const getUtilColor = (percentage: number) => {
  if (percentage < 70) return '#10b981'
  if (percentage < 85) return '#f59e0b'
  return '#ef4444'
}

const getPowerColor = (percentage: number) => {
  if (percentage < 70) return '#10b981'
  if (percentage < 85) return '#f59e0b'
  return '#ef4444'
}

// Actions
const clearFilters = () => {
  searchQuery.value = ''
  filterRow.value = ''
  filterStatus.value = ''
  filterUtilization.value = ''
}

const viewRackDetail = (rack: any) => {
  selectedRack.value = rack
  detailDialogVisible.value = true
}

const viewDevices = (rack: any) => {
  selectedRack.value = rack
  detailDialogVisible.value = true
}

const openAddRackDialog = () => {
  rackForm.value = {
    id: null,
    name: '',
    row: 'A',
    position: 1,
    totalU: 42,
    maxPower: 15,
    pduType: 'three',
    usedU: 0,
    power: 0,
    status: 'Normal',
    devices: [],
    deviceCount: 0,
    availableU: 42
  }
  rackDialogTitle.value = 'Add Rack'
  rackDialogVisible.value = true
}

const editRack = (rack: any) => {
  rackForm.value = { ...rack }
  rackDialogTitle.value = 'Edit Rack'
  rackDialogVisible.value = true
}

const saveRack = async () => {
  try {
    await rackFormRef.value?.validate()

    if (rackForm.value.id) {
      // Update existing rack
      const index = racks.value.findIndex(r => r.id === rackForm.value.id)
      if (index !== -1) {
        racks.value[index] = { ...rackForm.value }
        ElMessage.success('Rack updated successfully')
      }
    } else {
      // Add new rack
      const newId = Math.max(...racks.value.map(r => r.id), 0) + 1
      const newRack = {
        ...rackForm.value,
        id: newId,
        usedU: 0,
        power: 0,
        status: 'Normal',
        devices: [],
        deviceCount: 0,
        availableU: rackForm.value.totalU
      }
      racks.value.push(newRack)
      ElMessage.success('Rack added successfully')
    }
    rackDialogVisible.value = false
  } catch (error) {
    console.error('Validation failed:', error)
  }
}

const openAddDeviceDialog = () => {
  if (!selectedRack.value) return
  deviceForm.value = {
    name: '',
    model: '',
    manufacturer: '',
    uPosition: 1,
    uSize: 1,
    power: 0,
    serialNumber: ''
  }
  editingDevice.value = null
  deviceDialogTitle.value = 'Add Device'
  deviceDialogVisible.value = true
}

const editDevice = (device: any) => {
  editingDevice.value = device
  deviceForm.value = { ...device }
  deviceDialogTitle.value = 'Edit Device'
  deviceDialogVisible.value = true
}

const saveDevice = async () => {
  if (!selectedRack.value) return

  try {
    await deviceFormRef.value?.validate()

    // Check for overlapping U positions
    const startU = deviceForm.value.uPosition
    const endU = startU + deviceForm.value.uSize - 1
    const existingDevices = selectedRack.value.devices || []

    // Exclude current device when editing
    const overlapping = existingDevices.some((d: any) => {
      if (editingDevice.value && d.name === editingDevice.value.name && d.uPosition === editingDevice.value.uPosition) {
        return false
      }
      const dStart = d.uPosition
      const dEnd = dStart + d.uSize - 1
      return !(endU < dStart || startU > dEnd)
    })

    if (overlapping) {
      ElMessage.warning('U position overlaps with existing device')
      return
    }

    if (editingDevice.value) {
      // Update existing device
      const index = selectedRack.value.devices.findIndex((d: any) =>
          d.name === editingDevice.value.name && d.uPosition === editingDevice.value.uPosition
      )
      if (index !== -1) {
        selectedRack.value.devices[index] = { ...deviceForm.value }
        ElMessage.success('Device updated successfully')
      }
    } else {
      // Add new device
      if (!selectedRack.value.devices) {
        selectedRack.value.devices = []
      }
      selectedRack.value.devices.push({ ...deviceForm.value })
      ElMessage.success('Device added successfully')
    }

    // Update rack metrics
    selectedRack.value.usedU = selectedRack.value.devices.reduce((sum: number, d: any) => sum + d.uSize, 0)
    selectedRack.value.availableU = selectedRack.value.totalU - selectedRack.value.usedU
    selectedRack.value.power = (selectedRack.value.devices.reduce((sum: number, d: any) => sum + d.power, 0) / 1000).toFixed(1)
    selectedRack.value.deviceCount = selectedRack.value.devices.length

    const utilization = (selectedRack.value.usedU / selectedRack.value.totalU) * 100
    if (utilization >= 95) selectedRack.value.status = 'Critical'
    else if (utilization >= 85) selectedRack.value.status = 'Warning'
    else selectedRack.value.status = 'Normal'

    // Update the rack in the main list
    const rackIndex = racks.value.findIndex(r => r.id === selectedRack.value.id)
    if (rackIndex !== -1) {
      racks.value[rackIndex] = { ...selectedRack.value }
    }

    deviceDialogVisible.value = false
  } catch (error) {
    console.error('Validation failed:', error)
  }
}

const removeDevice = (device: any) => {
  ElMessageBox.confirm(`Remove device ${device.name}?`, 'Confirm', {
    confirmButtonText: 'Remove',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    if (!selectedRack.value) return

    const index = selectedRack.value.devices.findIndex((d: any) =>
        d.name === device.name && d.uPosition === device.uPosition
    )
    if (index !== -1) {
      selectedRack.value.devices.splice(index, 1)

      // Update rack metrics
      selectedRack.value.usedU = selectedRack.value.devices.reduce((sum: number, d: any) => sum + d.uSize, 0)
      selectedRack.value.availableU = selectedRack.value.totalU - selectedRack.value.usedU
      selectedRack.value.power = (selectedRack.value.devices.reduce((sum: number, d: any) => sum + d.power, 0) / 1000).toFixed(1)
      selectedRack.value.deviceCount = selectedRack.value.devices.length

      const utilization = (selectedRack.value.usedU / selectedRack.value.totalU) * 100
      if (utilization >= 95) selectedRack.value.status = 'Critical'
      else if (utilization >= 85) selectedRack.value.status = 'Warning'
      else selectedRack.value.status = 'Normal'

      // Update the rack in the main list
      const rackIndex = racks.value.findIndex(r => r.id === selectedRack.value.id)
      if (rackIndex !== -1) {
        racks.value[rackIndex] = { ...selectedRack.value }
      }

      ElMessage.success('Device removed successfully')
    }
  }).catch(() => {})
}

const exportInventory = () => {
  ElMessage.success('Inventory exported successfully')
}

const importInventory = () => {
  ElMessage.info('Import feature will be available soon')
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
    }, 400)
  }, 2800)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.rack-inventory-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
}

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
  font-size: 24px;
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
  width: 320px;
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

/* ==================== Main Content ==================== */
.rack-inventory-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Filters Section */
.filters-section {
  margin-bottom: 24px;
}

.filters-card {
  border-radius: 16px;
  background: white;
}

.filters-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

/* Racks Grid */
.racks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.rack-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
  cursor: pointer;
  border-left: 4px solid #10b981;
}

.rack-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.rack-card.status-warning {
  border-left-color: #f59e0b;
}

.rack-card.status-critical {
  border-left-color: #ef4444;
}

.rack-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.rack-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.rack-name {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.rack-location {
  font-size: 12px;
  color: #64748b;
}

.rack-card-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.rack-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.quick-stats {
  display: flex;
  gap: 16px;
}

.quick-stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.success {
  background: #10b981;
}

.dot.warning {
  background: #f59e0b;
}

.dot.danger {
  background: #ef4444;
}

.rack-actions {
  display: flex;
  gap: 8px;
}

/* Summary Section */
.summary-section {
  margin-top: 24px;
}

.summary-card {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.summary-icon.blue { background: #eff6ff; color: #3b82f6; }
.summary-icon.green { background: #ecfdf5; color: #10b981; }
.summary-icon.orange { background: #fffbeb; color: #f59e0b; }
.summary-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.summary-info {
  flex: 1;
}

.summary-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.summary-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

/* Dialog Styles */
.detail-dialog :deep(.el-dialog__body) {
  padding-top: 0;
}

.rack-detail-header {
  margin-bottom: 20px;
}

.rack-detail-devices {
  margin-top: 20px;
}

.device-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.device-list-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* Responsive */
@media (max-width: 768px) {
  .rack-inventory-main { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .racks-grid { grid-template-columns: 1fr; }
  .filters-row { flex-direction: column; align-items: stretch; }
  .filters-row .el-input,
  .filters-row .el-select { width: 100% !important; }
}
</style>