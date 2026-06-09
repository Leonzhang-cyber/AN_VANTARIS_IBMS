<template>
  <div class="u-space-management-container">
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
            <span class="loading-title">Loading U Space Management</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">U Space Management</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="u-space-management-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">U Space Management</h1>
          <p class="page-subtitle">Manage rack U space utilization and device placement</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="optimizeSpace">
            <el-icon><MagicStick /></el-icon>
            Optimize Space
          </el-button>
          <el-button @click="exportLayout">
            <el-icon><Download /></el-icon>
            Export Layout
          </el-button>
        </div>
      </div>

      <!-- Rack Selector -->
      <div class="rack-selector-section">
        <el-card class="selector-card" shadow="never">
          <div class="selector-row">
            <span class="selector-label">Select Rack:</span>
            <el-select v-model="selectedRackId" placeholder="Select a rack" filterable style="width: 200px" @change="onRackChange">
              <el-option
                  v-for="rack in racks"
                  :key="rack.id"
                  :label="rack.name"
                  :value="rack.id"
              >
                <span>{{ rack.name }}</span>
                <span style="float: right; color: #8492a6; font-size: 12px">
                  {{ rack.usedU }}/{{ rack.totalU }} U
                </span>
              </el-option>
            </el-select>
            <div class="rack-summary" v-if="currentRack">
              <div class="summary-item">
                <span class="summary-label">Utilization:</span>
                <span class="summary-value" :style="{ color: getUtilColor(utilizationPercent) }">
                  {{ utilizationPercent }}%
                </span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Free U:</span>
                <span class="summary-value">{{ currentRack.availableU }} U</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Devices:</span>
                <span class="summary-value">{{ currentRack.devices?.length || 0 }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">Fragmentation:</span>
                <span class="summary-value" :style="{ color: fragmentationRate > 20 ? '#ef4444' : fragmentationRate > 10 ? '#f59e0b' : '#10b981' }">
                  {{ fragmentationRate }}%
                </span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Main Content Area -->
      <div class="main-content-area" v-if="currentRack">
        <el-row :gutter="24">
          <!-- Left: U Space Visualization -->
          <el-col :span="14">
            <el-card class="u-space-viz-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Grid /></el-icon>
                  <span>{{ currentRack.name }} - U Space Layout</span>
                </div>
                <div class="card-controls">
                  <el-button size="small" @click="zoomIn">Zoom In</el-button>
                  <el-button size="small" @click="zoomOut">Zoom Out</el-button>
                  <el-button size="small" type="primary" @click="addDevice">Add Device</el-button>
                </div>
              </div>
              <div class="u-space-viz" :style="{ zoom: zoomLevel }">
                <div
                    v-for="u in currentRack.totalU"
                    :key="u"
                    class="u-unit-card"
                    :class="{
                    'occupied': isUOccupied(u),
                    'free': !isUOccupied(u),
                    'selected': selectedU === u,
                    'drag-over': dragOverU === u
                  }"
                    @click="selectU(u)"
                    @dragover.prevent="onDragOver(u)"
                    @dragleave="onDragLeave"
                    @drop="onDrop(u)"
                >
                  <div class="u-number">U{{ u }}</div>
                  <div class="u-device" v-if="getDeviceAtU(u)">
                    <div class="device-name">{{ getDeviceAtU(u)?.name }}</div>
                    <div class="device-size">{{ getDeviceAtU(u)?.uSize }}U</div>
                    <div class="device-power">{{ getDeviceAtU(u)?.power }}W</div>
                  </div>
                  <div class="u-empty" v-else>
                    <span class="empty-text">Empty</span>
                  </div>
                </div>
              </div>
              <div class="viz-legend">
                <div class="legend-item">
                  <span class="legend-color occupied"></span>
                  <span>Occupied</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color free"></span>
                  <span>Free</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color selected"></span>
                  <span>Selected</span>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- Right: Device List & Controls -->
          <el-col :span="10">
            <!-- Device List -->
            <el-card class="device-list-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><List /></el-icon>
                  <span>Installed Devices</span>
                </div>
                <el-button size="small" type="primary" @click="addDevice">
                  <el-icon><Plus /></el-icon>
                  Add
                </el-button>
              </div>
              <div class="device-list">
                <div
                    v-for="device in sortedDevices"
                    :key="device.id"
                    class="device-item"
                    :class="{ 'selected': selectedDevice?.id === device.id }"
                    @click="selectDevice(device)"
                    draggable="true"
                    @dragstart="onDragStart($event, device)"
                    @dragend="onDragEnd"
                >
                  <div class="device-info">
                    <div class="device-name">{{ device.name }}</div>
                    <div class="device-details">
                      <span class="device-model">{{ device.model }}</span>
                      <span class="device-size">{{ device.uSize }}U</span>
                      <span class="device-power">{{ device.power }}W</span>
                    </div>
                  </div>
                  <div class="device-actions">
                    <el-button size="small" circle @click.stop="editDevice(device)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button size="small" circle type="danger" @click.stop="removeDevice(device)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
                <div v-if="!currentRack.devices?.length" class="empty-devices">
                  <el-empty description="No devices installed" :image-size="80" />
                </div>
              </div>
            </el-card>

            <!-- Fragmentation Analysis -->
            <el-card class="fragmentation-card" shadow="hover" style="margin-top: 20px">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>Fragmentation Analysis</span>
                </div>
              </div>
              <div class="fragmentation-content">
                <div class="fragmentation-stats">
                  <div class="stat">
                    <span class="stat-label">Fragmentation Rate</span>
                    <span class="stat-value" :style="{ color: fragmentationRate > 20 ? '#ef4444' : fragmentationRate > 10 ? '#f59e0b' : '#10b981' }">
                      {{ fragmentationRate }}%
                    </span>
                  </div>
                  <div class="stat">
                    <span class="stat-label">Free Blocks</span>
                    <span class="stat-value">{{ freeBlocks }}</span>
                  </div>
                  <div class="stat">
                    <span class="stat-label">Largest Block</span>
                    <span class="stat-value">{{ largestFreeBlock }} U</span>
                  </div>
                </div>
                <div class="fragmentation-bars">
                  <div class="frag-bar" v-for="(block, index) in freeBlocksList" :key="index">
                    <div class="bar" :style="{ width: (block.size / currentRack.totalU) * 100 + '%' }"></div>
                    <span class="bar-label">{{ block.startU }}-{{ block.endU }} ({{ block.size }}U)</span>
                  </div>
                </div>
                <el-button v-if="fragmentationRate > 15" type="primary" size="small" @click="suggestOptimization">
                  Suggest Optimization
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Add/Edit Device Dialog -->
      <el-dialog v-model="deviceDialogVisible" :title="deviceDialogTitle" width="550px">
        <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="100px">
          <el-form-item label="Device Name" prop="name">
            <el-input v-model="deviceForm.name" placeholder="e.g., Web Server-01" />
          </el-form-item>
          <el-form-item label="Model" prop="model">
            <el-input v-model="deviceForm.model" placeholder="e.g., Dell R750" />
          </el-form-item>
          <el-form-item label="Manufacturer" prop="manufacturer">
            <el-input v-model="deviceForm.manufacturer" placeholder="e.g., Dell" />
          </el-form-item>
          <el-form-item label="U Position" prop="uPosition">
            <el-input-number v-model="deviceForm.uPosition" :min="1" :max="currentRack?.totalU || 42" />
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

      <!-- Optimization Suggestions Dialog -->
      <el-dialog v-model="optimizationDialogVisible" title="Space Optimization Suggestions" width="600px">
        <div class="optimization-content">
          <div class="optimization-stats">
            <div class="stat-item">
              <span>Current Free Space:</span>
              <strong>{{ currentRack?.availableU }} U</strong>
            </div>
            <div class="stat-item">
              <span>Fragmentation Rate:</span>
              <strong :style="{ color: fragmentationRate > 20 ? '#ef4444' : '#f59e0b' }">{{ fragmentationRate }}%</strong>
            </div>
            <div class="stat-item">
              <span>Potential Gain:</span>
              <strong class="success">+{{ potentialGain }} U</strong>
            </div>
          </div>
          <div class="optimization-suggestions">
            <h4>Recommendations</h4>
            <ul>
              <li v-for="suggestion in optimizationSuggestions" :key="suggestion">
                {{ suggestion }}
              </li>
            </ul>
          </div>
        </div>
        <template #footer>
          <el-button @click="optimizationDialogVisible = false">Close</el-button>
          <el-button type="primary" @click="applyOptimization">Apply Optimization</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, List, Plus, Edit, Delete, Download, MagicStick, DataAnalysis } from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading U space management...')

// ==================== Reactive Data ====================
const selectedRackId = ref(1)
const selectedU = ref<number | null>(null)
const selectedDevice = ref<any>(null)
const dragOverU = ref<number | null>(null)
const zoomLevel = ref(1)
const deviceDialogVisible = ref(false)
const optimizationDialogVisible = ref(false)
const deviceDialogTitle = ref('Add Device')
const editingDevice = ref<any>(null)

// Form refs
const deviceFormRef = ref()

// Form data
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
    power: 8.5, maxPower: 15, status: 'Normal',
    devices: [
      { id: 1, name: 'Web Server-01', model: 'R750', manufacturer: 'Dell', uPosition: 1, uSize: 2, power: 450, serialNumber: 'DL12345' },
      { id: 2, name: 'Web Server-02', model: 'R750', manufacturer: 'Dell', uPosition: 3, uSize: 2, power: 450, serialNumber: 'DL12346' },
      { id: 3, name: 'Storage Array', model: 'AFF A250', manufacturer: 'NetApp', uPosition: 5, uSize: 4, power: 600, serialNumber: 'NT98765' },
      { id: 4, name: 'Switch-01', model: '9300', manufacturer: 'Cisco', uPosition: 9, uSize: 1, power: 150, serialNumber: 'CS54321' },
      { id: 5, name: 'Switch-02', model: '9300', manufacturer: 'Cisco', uPosition: 10, uSize: 1, power: 150, serialNumber: 'CS54322' },
      { id: 6, name: 'Database Server', model: 'R760', manufacturer: 'Dell', uPosition: 15, uSize: 2, power: 550, serialNumber: 'DL12347' },
      { id: 7, name: 'Backup Server', model: 'R750', manufacturer: 'Dell', uPosition: 20, uSize: 2, power: 400, serialNumber: 'DL12348' }
    ]
  },
  {
    id: 2, name: 'A02', row: 'A', position: 2, totalU: 42, usedU: 35, availableU: 7,
    power: 7.8, maxPower: 15, status: 'Normal',
    devices: [
      { id: 8, name: 'App Server-01', model: 'R750', manufacturer: 'Dell', uPosition: 1, uSize: 2, power: 450 },
      { id: 9, name: 'App Server-02', model: 'R750', manufacturer: 'Dell', uPosition: 3, uSize: 2, power: 450 }
    ]
  },
  {
    id: 3, name: 'A03', row: 'A', position: 3, totalU: 42, usedU: 40, availableU: 2,
    power: 12.5, maxPower: 15, status: 'Warning',
    devices: []
  },
  {
    id: 4, name: 'B01', row: 'B', position: 1, totalU: 42, usedU: 36, availableU: 6,
    power: 8.2, maxPower: 15, status: 'Normal',
    devices: []
  },
  {
    id: 5, name: 'B02', row: 'B', position: 2, totalU: 42, usedU: 32, availableU: 10,
    power: 7.2, maxPower: 15, status: 'Normal',
    devices: []
  }
])

// Current rack
const currentRack = computed(() => {
  return racks.value.find(r => r.id === selectedRackId.value)
})

// Utilization percent
const utilizationPercent = computed(() => {
  if (!currentRack.value) return 0
  return ((currentRack.value.usedU / currentRack.value.totalU) * 100).toFixed(1)
})

// Sorted devices by U position
const sortedDevices = computed(() => {
  if (!currentRack.value?.devices) return []
  return [...currentRack.value.devices].sort((a, b) => a.uPosition - b.uPosition)
})

// Free blocks analysis
const freeBlocksList = computed(() => {
  if (!currentRack.value) return []

  const blocks: { startU: number; endU: number; size: number }[] = []
  let currentBlock: { startU: number; endU: number; size: number } | null = null

  for (let u = 1; u <= currentRack.value.totalU; u++) {
    const isOccupied = isUOccupied(u)
    if (!isOccupied) {
      if (!currentBlock) {
        currentBlock = { startU: u, endU: u, size: 1 }
      } else {
        currentBlock.endU = u
        currentBlock.size++
      }
    } else {
      if (currentBlock) {
        blocks.push(currentBlock)
        currentBlock = null
      }
    }
  }

  if (currentBlock) {
    blocks.push(currentBlock)
  }

  return blocks
})

const freeBlocks = computed(() => freeBlocksList.value.length)
const largestFreeBlock = computed(() => {
  if (freeBlocksList.value.length === 0) return 0
  return Math.max(...freeBlocksList.value.map(b => b.size))
})

const fragmentationRate = computed(() => {
  if (!currentRack.value) return 0
  const freeU = currentRack.value.availableU
  if (freeU === 0) return 0
  const largestBlock = largestFreeBlock.value
  return Math.round(((freeU - largestBlock) / freeU) * 100)
})

const potentialGain = computed(() => {
  return Math.min(largestFreeBlock.value * 0.3, 10)
})

const optimizationSuggestions = ref([
  'Move small devices to create larger contiguous space',
  'Consolidate 1U devices into a single area',
  'Consider rearranging devices based on size and heat output',
  'Plan for future expansion in the bottom of the rack'
])

// Helper functions
const getUtilColor = (percent: number) => {
  if (percent < 70) return '#10b981'
  if (percent < 85) return '#f59e0b'
  return '#ef4444'
}

const isUOccupied = (u: number) => {
  if (!currentRack.value?.devices) return false
  return currentRack.value.devices.some(device => {
    const startU = device.uPosition
    const endU = startU + device.uSize - 1
    return u >= startU && u <= endU
  })
}

const getDeviceAtU = (u: number) => {
  if (!currentRack.value?.devices) return null
  return currentRack.value.devices.find(device => {
    const startU = device.uPosition
    const endU = startU + device.uSize - 1
    return u >= startU && u <= endU
  })
}

const selectU = (u: number) => {
  selectedU.value = u
  const device = getDeviceAtU(u)
  if (device) {
    selectedDevice.value = device
  }
}

const selectDevice = (device: any) => {
  selectedDevice.value = device
  selectedU.value = device.uPosition
}

// Device management
const addDevice = () => {
  if (!currentRack.value) return
  deviceForm.value = {
    name: '',
    model: '',
    manufacturer: '',
    uPosition: findBestAvailableU(),
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

const findBestAvailableU = () => {
  const largestBlock = freeBlocksList.value.reduce((max, block) => {
    return block.size > max.size ? block : max
  }, { size: 0, startU: 1 })
  return largestBlock.startU || 1
}

const saveDevice = async () => {
  if (!currentRack.value) return

  try {
    await deviceFormRef.value?.validate()

    // Check for overlapping U positions
    const startU = deviceForm.value.uPosition
    const endU = startU + deviceForm.value.uSize - 1
    const existingDevices = currentRack.value.devices || []

    // Exclude current device when editing
    const overlapping = existingDevices.some((d: any) => {
      if (editingDevice.value && d.id === editingDevice.value.id) {
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
      const index = currentRack.value.devices.findIndex((d: any) => d.id === editingDevice.value.id)
      if (index !== -1) {
        currentRack.value.devices[index] = { ...deviceForm.value, id: editingDevice.value.id }
        ElMessage.success('Device updated successfully')
      }
    } else {
      // Add new device
      const newId = Math.max(...(currentRack.value.devices.map((d: any) => d.id) || [0]), 0) + 1
      if (!currentRack.value.devices) {
        currentRack.value.devices = []
      }
      currentRack.value.devices.push({ ...deviceForm.value, id: newId })
      ElMessage.success('Device added successfully')
    }

    // Update rack metrics
    currentRack.value.usedU = currentRack.value.devices.reduce((sum: number, d: any) => sum + d.uSize, 0)
    currentRack.value.availableU = currentRack.value.totalU - currentRack.value.usedU
    currentRack.value.power = (currentRack.value.devices.reduce((sum: number, d: any) => sum + d.power, 0) / 1000).toFixed(1)

    const utilization = (currentRack.value.usedU / currentRack.value.totalU) * 100
    if (utilization >= 95) currentRack.value.status = 'Critical'
    else if (utilization >= 85) currentRack.value.status = 'Warning'
    else currentRack.value.status = 'Normal'

    deviceDialogVisible.value = false
    selectedDevice.value = null
    selectedU.value = null
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
    if (!currentRack.value) return

    const index = currentRack.value.devices.findIndex((d: any) => d.id === device.id)
    if (index !== -1) {
      currentRack.value.devices.splice(index, 1)

      // Update rack metrics
      currentRack.value.usedU = currentRack.value.devices.reduce((sum: number, d: any) => sum + d.uSize, 0)
      currentRack.value.availableU = currentRack.value.totalU - currentRack.value.usedU
      currentRack.value.power = (currentRack.value.devices.reduce((sum: number, d: any) => sum + d.power, 0) / 1000).toFixed(1)

      const utilization = (currentRack.value.usedU / currentRack.value.totalU) * 100
      if (utilization >= 95) currentRack.value.status = 'Critical'
      else if (utilization >= 85) currentRack.value.status = 'Warning'
      else currentRack.value.status = 'Normal'

      ElMessage.success('Device removed successfully')
      selectedDevice.value = null
      selectedU.value = null
    }
  }).catch(() => {})
}

// Drag and drop
let draggedDevice: any = null

const onDragStart = (event: DragEvent, device: any) => {
  draggedDevice = device
  event.dataTransfer?.setData('text/plain', JSON.stringify(device))
  event.dataTransfer!.effectAllowed = 'move'
}

const onDragOver = (u: number) => {
  dragOverU.value = u
}

const onDragLeave = () => {
  dragOverU.value = null
}

const onDragEnd = () => {
  draggedDevice = null
  dragOverU.value = null
}

const onDrop = (targetU: number) => {
  if (!draggedDevice || !currentRack.value) {
    dragOverU.value = null
    return
  }

  const newStartU = targetU
  const newEndU = newStartU + draggedDevice.uSize - 1

  // Check if new position is within rack bounds
  if (newEndU > currentRack.value.totalU) {
    ElMessage.warning('Device would extend beyond rack bounds')
    dragOverU.value = null
    return
  }

  // Check for overlap with other devices
  const overlapping = currentRack.value.devices.some((d: any) => {
    if (d.id === draggedDevice.id) return false
    const dStart = d.uPosition
    const dEnd = dStart + d.uSize - 1
    return !(newEndU < dStart || newStartU > dEnd)
  })

  if (overlapping) {
    ElMessage.warning('Cannot move device: position overlaps with another device')
    dragOverU.value = null
    return
  }

  // Move the device
  const deviceIndex = currentRack.value.devices.findIndex((d: any) => d.id === draggedDevice.id)
  if (deviceIndex !== -1) {
    currentRack.value.devices[deviceIndex].uPosition = newStartU
    ElMessage.success(`Device moved to U${newStartU}-U${newEndU}`)
  }

  dragOverU.value = null
  draggedDevice = null
}

// UI Controls
const zoomIn = () => {
  if (zoomLevel.value < 1.5) zoomLevel.value += 0.1
}

const zoomOut = () => {
  if (zoomLevel.value > 0.7) zoomLevel.value -= 0.1
}

const onRackChange = () => {
  selectedDevice.value = null
  selectedU.value = null
}

const optimizeSpace = () => {
  optimizationDialogVisible.value = true
}

const applyOptimization = () => {
  ElMessage.success('Optimization applied. Devices have been rearranged.')
  optimizationDialogVisible.value = false
}

const suggestOptimization = () => {
  optimizationDialogVisible.value = true
}

const exportLayout = () => {
  ElMessage.success('Layout exported successfully')
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
.u-space-management-container {
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
.u-space-management-main {
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

/* Rack Selector */
.rack-selector-section {
  margin-bottom: 24px;
}

.selector-card {
  border-radius: 16px;
  background: white;
}

.selector-row {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.selector-label {
  font-weight: 600;
  color: #1e293b;
}

.rack-summary {
  display: flex;
  gap: 24px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-size: 13px;
  color: #64748b;
}

.summary-value {
  font-weight: 600;
  color: #1e293b;
}

/* U Space Visualization Card */
.u-space-viz-card {
  border-radius: 20px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.card-title .el-icon {
  font-size: 18px;
  color: #3b82f6;
}

.u-space-viz {
  display: flex;
  flex-direction: column-reverse;
  gap: 8px;
  max-height: 600px;
  overflow-y: auto;
  transition: zoom 0.2s;
}

.u-unit-card {
  display: flex;
  align-items: center;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 8px 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.u-unit-card:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.u-unit-card.occupied {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.u-unit-card.free {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.u-unit-card.selected {
  border-color: #3b82f6;
  background: #dbeafe;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.u-unit-card.drag-over {
  border-color: #10b981;
  background: #d1fae5;
}

.u-number {
  width: 50px;
  font-weight: 600;
  font-size: 14px;
  color: #64748b;
}

.u-device {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
}

.device-name {
  font-weight: 600;
  color: #1e293b;
  min-width: 150px;
}

.device-size {
  font-size: 12px;
  color: #64748b;
  background: #e2e8f0;
  padding: 2px 8px;
  border-radius: 12px;
}

.device-power {
  font-size: 12px;
  color: #f59e0b;
}

.u-empty {
  flex: 1;
  text-align: center;
}

.empty-text {
  font-size: 12px;
  color: #94a3b8;
}

/* Viz Legend */
.viz-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #64748b;
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 4px;
}

.legend-color.occupied { background: #3b82f6; }
.legend-color.free { background: #10b981; }
.legend-color.selected { background: #3b82f6; border: 2px solid #1e40af; }

/* Device List Card */
.device-list-card {
  border-radius: 20px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  height: auto;
}

.device-list {
  max-height: 400px;
  overflow-y: auto;
}

.device-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.device-item:hover {
  background: #f1f5f9;
  transform: translateX(4px);
}

.device-item.selected {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}

.device-info {
  flex: 1;
}

.device-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.device-details {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #64748b;
}

.device-actions {
  display: flex;
  gap: 8px;
}

.empty-devices {
  padding: 40px;
}

/* Fragmentation Card */
.fragmentation-card {
  border-radius: 20px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.fragmentation-content {
  padding: 8px 0;
}

.fragmentation-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.stat {
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
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.fragmentation-bars {
  margin-bottom: 16px;
}

.frag-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.bar {
  height: 8px;
  background: #10b981;
  border-radius: 4px;
  transition: width 0.3s;
}

.bar-label {
  font-size: 11px;
  color: #64748b;
  min-width: 80px;
}

/* Optimization Dialog */
.optimization-content {
  padding: 8px 0;
}

.optimization-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.optimization-stats .stat-item {
  text-align: center;
}

.optimization-stats .stat-item span {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.optimization-stats .stat-item strong {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.optimization-stats .stat-item strong.success {
  color: #10b981;
}

.optimization-suggestions h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.optimization-suggestions ul {
  margin: 0;
  padding-left: 20px;
}

.optimization-suggestions li {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

/* Responsive */
@media (max-width: 1200px) {
  .u-space-management-main { padding: 16px; }
  .selector-row { flex-direction: column; align-items: flex-start; }
  .rack-summary { flex-wrap: wrap; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .u-unit-card { flex-direction: column; align-items: flex-start; gap: 8px; }
  .u-device { flex-wrap: wrap; }
  .device-name { min-width: auto; }
}
</style>