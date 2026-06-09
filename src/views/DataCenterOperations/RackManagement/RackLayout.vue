<template>
  <div class="rack-layout-container">
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
            <span class="loading-title">Loading Rack Layout</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Rack Layout Visualization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="rack-layout-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Rack Layout</h1>
          <p class="page-subtitle">Visualize and manage rack configurations</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="addRack">
            <el-icon><Plus /></el-icon>
            Add Rack
          </el-button>
          <el-button @click="exportLayout">
            <el-icon><Download /></el-icon>
            Export Layout
          </el-button>
          <el-button @click="editMode = !editMode" :type="editMode ? 'warning' : 'default'">
            <el-icon><Edit /></el-icon>
            {{ editMode ? 'Exit Edit' : 'Edit Mode' }}
          </el-button>
        </div>
      </div>

      <!-- Data Hall Layout -->
      <div class="data-hall-section">
        <div class="section-header">
          <h3>Data Hall Layout</h3>
          <div class="view-controls">
            <el-radio-group v-model="viewType" size="small">
              <el-radio-button label="top">Top View</el-radio-button>
              <el-radio-button label="front">Front View</el-radio-button>
            </el-radio-group>
            <el-select v-model="selectedRow" size="small" placeholder="Select Row" style="width: 120px" v-if="viewType === 'front'">
              <el-option label="Row A" value="A" />
              <el-option label="Row B" value="B" />
              <el-option label="Row C" value="C" />
              <el-option label="Row D" value="D" />
            </el-select>
          </div>
        </div>

        <!-- Top View Layout -->
        <div class="top-view" v-if="viewType === 'top'">
          <div class="room-layout">
            <!-- Cold Aisle -->
            <div class="aisle cold-aisle">
              <div class="aisle-label">Cold Aisle</div>
            </div>

            <!-- Row A Racks -->
            <div class="rack-row row-a">
              <div class="row-label">Row A</div>
              <div class="racks-container">
                <div
                    v-for="rack in rowARacks"
                    :key="rack.id"
                    class="rack-top-item"
                    :class="{
                    'selected': selectedRack?.id === rack.id,
                    'edit-mode': editMode
                  }"
                    @click="selectRack(rack)"
                >
                  <div class="rack-top-content">
                    <span class="rack-name">{{ rack.name }}</span>
                    <div class="rack-stats">
                      <span class="utilization" :style="{ color: getUtilColor(rack.utilization) }">
                        {{ rack.utilization }}%
                      </span>
                    </div>
                  </div>
                  <div v-if="editMode" class="rack-actions">
                    <el-button size="small" circle @click.stop="editRack(rack)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button size="small" circle type="danger" @click.stop="deleteRack(rack)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Hot Aisle -->
            <div class="aisle hot-aisle">
              <div class="aisle-label">Hot Aisle</div>
            </div>

            <!-- Row B Racks -->
            <div class="rack-row row-b">
              <div class="row-label">Row B</div>
              <div class="racks-container">
                <div
                    v-for="rack in rowBRacks"
                    :key="rack.id"
                    class="rack-top-item"
                    :class="{
                    'selected': selectedRack?.id === rack.id,
                    'edit-mode': editMode
                  }"
                    @click="selectRack(rack)"
                >
                  <div class="rack-top-content">
                    <span class="rack-name">{{ rack.name }}</span>
                    <div class="rack-stats">
                      <span class="utilization" :style="{ color: getUtilColor(rack.utilization) }">
                        {{ rack.utilization }}%
                      </span>
                    </div>
                  </div>
                  <div v-if="editMode" class="rack-actions">
                    <el-button size="small" circle @click.stop="editRack(rack)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button size="small" circle type="danger" @click.stop="deleteRack(rack)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Cold Aisle -->
            <div class="aisle cold-aisle">
              <div class="aisle-label">Cold Aisle</div>
            </div>

            <!-- Row C Racks -->
            <div class="rack-row row-c">
              <div class="row-label">Row C</div>
              <div class="racks-container">
                <div
                    v-for="rack in rowCRacks"
                    :key="rack.id"
                    class="rack-top-item"
                    :class="{
                    'selected': selectedRack?.id === rack.id,
                    'edit-mode': editMode
                  }"
                    @click="selectRack(rack)"
                >
                  <div class="rack-top-content">
                    <span class="rack-name">{{ rack.name }}</span>
                    <div class="rack-stats">
                      <span class="utilization" :style="{ color: getUtilColor(rack.utilization) }">
                        {{ rack.utilization }}%
                      </span>
                    </div>
                  </div>
                  <div v-if="editMode" class="rack-actions">
                    <el-button size="small" circle @click.stop="editRack(rack)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button size="small" circle type="danger" @click.stop="deleteRack(rack)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Hot Aisle -->
            <div class="aisle hot-aisle">
              <div class="aisle-label">Hot Aisle</div>
            </div>

            <!-- Row D Racks -->
            <div class="rack-row row-d">
              <div class="row-label">Row D</div>
              <div class="racks-container">
                <div
                    v-for="rack in rowDRacks"
                    :key="rack.id"
                    class="rack-top-item"
                    :class="{
                    'selected': selectedRack?.id === rack.id,
                    'edit-mode': editMode
                  }"
                    @click="selectRack(rack)"
                >
                  <div class="rack-top-content">
                    <span class="rack-name">{{ rack.name }}</span>
                    <div class="rack-stats">
                      <span class="utilization" :style="{ color: getUtilColor(rack.utilization) }">
                        {{ rack.utilization }}%
                      </span>
                    </div>
                  </div>
                  <div v-if="editMode" class="rack-actions">
                    <el-button size="small" circle @click.stop="editRack(rack)">
                      <el-icon><Edit /></el-icon>
                    </el-button>
                    <el-button size="small" circle type="danger" @click.stop="deleteRack(rack)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Front View Layout -->
        <div class="front-view" v-else>
          <div class="front-view-container">
            <div class="rack-front-list">
              <div
                  v-for="rack in currentRowRacksFront"
                  :key="rack.id"
                  class="rack-front-item"
                  :class="{
                  'selected': selectedRack?.id === rack.id,
                  'edit-mode': editMode
                }"
                  @click="selectRack(rack)"
              >
                <div class="rack-front-header">
                  <span class="rack-name">{{ rack.name }}</span>
                  <el-tag :type="getStatusTag(rack)" size="small">{{ rack.status }}</el-tag>
                </div>
                <div class="rack-u-viz">
                  <div
                      v-for="u in 42"
                      :key="u"
                      class="u-block"
                      :class="{
                      occupied: isUOccupied(rack, u),
                      free: !isUOccupied(rack, u)
                    }"
                      :style="{ height: '8px' }"
                      :title="`U${u}: ${isUOccupied(rack, u) ? getDeviceAtU(rack, u) : 'Empty'}`"
                  ></div>
                </div>
                <div class="rack-front-footer">
                  <span>{{ rack.usedU }}/42 U</span>
                  <span>{{ rack.utilization }}% used</span>
                  <span>{{ rack.power }} kW</span>
                </div>
                <div v-if="editMode" class="rack-front-actions">
                  <el-button size="small" @click.stop="editRack(rack)">Edit</el-button>
                  <el-button size="small" type="danger" @click.stop="deleteRack(rack)">Delete</el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Legend -->
        <div class="layout-legend">
          <div class="legend-item">
            <span class="legend-color cold-aisle"></span>
            <span>Cold Aisle</span>
          </div>
          <div class="legend-item">
            <span class="legend-color hot-aisle"></span>
            <span>Hot Aisle</span>
          </div>
          <div class="legend-item">
            <span class="legend-color rack-normal"></span>
            <span>Rack (&lt;70%)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color rack-warning"></span>
            <span>Rack (70-85%)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color rack-critical"></span>
            <span>Rack (&gt;85%)</span>
          </div>
          <div class="legend-item">
            <span class="legend-color occupied"></span>
            <span>Occupied U</span>
          </div>
          <div class="legend-item">
            <span class="legend-color free"></span>
            <span>Free U</span>
          </div>
        </div>
      </div>

      <!-- Selected Rack Details -->
      <div class="rack-details-section" v-if="selectedRack">
        <div class="section-header">
          <h3>Rack Details: {{ selectedRack.name }}</h3>
          <div class="details-actions">
            <el-button size="small" @click="addDevice">
              <el-icon><Plus /></el-icon>
              Add Device
            </el-button>
            <el-button size="small" @click="editRack(selectedRack)">
              <el-icon><Edit /></el-icon>
              Edit Rack
            </el-button>
          </div>
        </div>
        <div class="rack-details-content">
          <div class="details-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Location">Row {{ selectedRack.row }}, Position {{ selectedRack.position }}</el-descriptions-item>
              <el-descriptions-item label="Status">
                <el-tag :type="getStatusTag(selectedRack)">{{ selectedRack.status }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="U Space">{{ selectedRack.usedU }}/42 U used</el-descriptions-item>
              <el-descriptions-item label="Utilization">{{ selectedRack.utilization }}%</el-descriptions-item>
              <el-descriptions-item label="Power">{{ selectedRack.power }} kW</el-descriptions-item>
              <el-descriptions-item label="Device Count">{{ selectedRack.devices?.length || 0 }}</el-descriptions-item>
            </el-descriptions>
          </div>
          <div class="details-devices">
            <h4>Installed Devices</h4>
            <el-table :data="selectedRack.devices || []" size="small" border>
              <el-table-column prop="name" label="Device Name" min-width="150" />
              <el-table-column prop="model" label="Model" width="120" />
              <el-table-column prop="uPosition" label="U Position" width="100" />
              <el-table-column prop="uSize" label="Size (U)" width="80" />
              <el-table-column prop="power" label="Power (W)" width="100" />
              <el-table-column label="Actions" width="100">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="editDevice(row)">Edit</el-button>
                  <el-button type="danger" link size="small" @click="removeDevice(row)">Remove</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>

      <!-- Add/Edit Rack Dialog -->
      <el-dialog v-model="rackDialogVisible" :title="dialogTitle" width="500px">
        <el-form :model="rackForm" label-width="100px">
          <el-form-item label="Rack Name" required>
            <el-input v-model="rackForm.name" placeholder="e.g., A01" />
          </el-form-item>
          <el-form-item label="Row">
            <el-select v-model="rackForm.row" placeholder="Select Row">
              <el-option label="Row A" value="A" />
              <el-option label="Row B" value="B" />
              <el-option label="Row C" value="C" />
              <el-option label="Row D" value="D" />
            </el-select>
          </el-form-item>
          <el-form-item label="Position">
            <el-input-number v-model="rackForm.position" :min="1" :max="20" />
          </el-form-item>
          <el-form-item label="Max Power (kW)">
            <el-input-number v-model="rackForm.maxPower" :min="5" :max="30" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="rackDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveRack">Save</el-button>
        </template>
      </el-dialog>

      <!-- Add/Edit Device Dialog -->
      <el-dialog v-model="deviceDialogVisible" title="Add/Edit Device" width="500px">
        <el-form :model="deviceForm" label-width="100px">
          <el-form-item label="Device Name" required>
            <el-input v-model="deviceForm.name" placeholder="e.g., Server-01" />
          </el-form-item>
          <el-form-item label="Model">
            <el-input v-model="deviceForm.model" placeholder="e.g., Dell PowerEdge" />
          </el-form-item>
          <el-form-item label="U Position" required>
            <el-input-number v-model="deviceForm.uPosition" :min="1" :max="42" />
          </el-form-item>
          <el-form-item label="Size (U)" required>
            <el-select v-model="deviceForm.uSize">
              <el-option label="1U" :value="1" />
              <el-option label="2U" :value="2" />
              <el-option label="3U" :value="3" />
              <el-option label="4U" :value="4" />
              <el-option label="6U" :value="6" />
              <el-option label="8U" :value="8" />
            </el-select>
          </el-form-item>
          <el-form-item label="Power (W)">
            <el-input-number v-model="deviceForm.power" :min="0" :step="50" />
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
import { Plus, Edit, Delete, Download } from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading rack layout...')

// ==================== Reactive Data ====================
const viewType = ref('top')
const selectedRow = ref('A')
const editMode = ref(false)
const selectedRack = ref<any>(null)
const rackDialogVisible = ref(false)
const deviceDialogVisible = ref(false)
const dialogTitle = ref('Add Rack')

// Form data
const rackForm = ref({
  id: null,
  name: '',
  row: 'A',
  position: 1,
  maxPower: 15,
  usedU: 0,
  utilization: 0,
  power: 0,
  status: 'Normal',
  devices: []
})

const deviceForm = ref({
  name: '',
  model: '',
  uPosition: 1,
  uSize: 1,
  power: 0
})

// Helper functions
const getUtilColor = (util: number) => {
  if (util < 70) return '#10b981'
  if (util < 85) return '#f59e0b'
  return '#ef4444'
}

const getStatusTag = (rack: any) => {
  if (rack.utilization >= 95) return 'danger'
  if (rack.utilization >= 85) return 'warning'
  return 'success'
}

const isUOccupied = (rack: any, u: number) => {
  if (!rack.devices) return false
  return rack.devices.some((device: any) => {
    const startU = device.uPosition
    const endU = startU + device.uSize - 1
    return u >= startU && u <= endU
  })
}

const getDeviceAtU = (rack: any, u: number) => {
  if (!rack.devices) return ''
  const device = rack.devices.find((d: any) => {
    const startU = d.uPosition
    const endU = startU + d.uSize - 1
    return u >= startU && u <= endU
  })
  return device ? device.name : ''
}

// Rack data
const racks = ref([
  {
    id: 1, name: 'A01', row: 'A', position: 1, usedU: 38, utilization: 90, power: 8.5, maxPower: 15, status: 'Normal',
    devices: [
      { name: 'Server-01', model: 'Dell R750', uPosition: 1, uSize: 2, power: 450 },
      { name: 'Server-02', model: 'Dell R750', uPosition: 3, uSize: 2, power: 450 },
      { name: 'Storage-01', model: 'NetApp AFF', uPosition: 5, uSize: 4, power: 600 },
      { name: 'Network-01', model: 'Cisco 9300', uPosition: 9, uSize: 1, power: 150 }
    ]
  },
  { id: 2, name: 'A02', row: 'A', position: 2, usedU: 35, utilization: 83, power: 7.8, maxPower: 15, status: 'Normal', devices: [] },
  { id: 3, name: 'A03', row: 'A', position: 3, usedU: 40, utilization: 95, power: 12.5, maxPower: 15, status: 'Warning', devices: [] },
  { id: 4, name: 'A04', row: 'A', position: 4, usedU: 28, utilization: 67, power: 6.2, maxPower: 15, status: 'Normal', devices: [] },
  { id: 5, name: 'A05', row: 'A', position: 5, usedU: 42, utilization: 100, power: 14.2, maxPower: 15, status: 'Critical', devices: [] },
  { id: 6, name: 'B01', row: 'B', position: 1, usedU: 36, utilization: 86, power: 8.2, maxPower: 15, status: 'Normal', devices: [] },
  { id: 7, name: 'B02', row: 'B', position: 2, usedU: 32, utilization: 76, power: 7.2, maxPower: 15, status: 'Normal', devices: [] },
  { id: 8, name: 'B03', row: 'B', position: 3, usedU: 38, utilization: 90, power: 9.5, maxPower: 15, status: 'Normal', devices: [] },
  { id: 9, name: 'B04', row: 'B', position: 4, usedU: 30, utilization: 71, power: 6.8, maxPower: 15, status: 'Normal', devices: [] },
  { id: 10, name: 'B05', row: 'B', position: 5, usedU: 35, utilization: 83, power: 8.0, maxPower: 15, status: 'Normal', devices: [] },
  { id: 11, name: 'C01', row: 'C', position: 1, usedU: 34, utilization: 81, power: 7.5, maxPower: 15, status: 'Normal', devices: [] },
  { id: 12, name: 'C02', row: 'C', position: 2, usedU: 28, utilization: 67, power: 6.0, maxPower: 15, status: 'Normal', devices: [] },
  { id: 13, name: 'C03', row: 'C', position: 3, usedU: 40, utilization: 95, power: 11.0, maxPower: 15, status: 'Warning', devices: [] },
  { id: 14, name: 'C04', row: 'C', position: 4, usedU: 25, utilization: 60, power: 5.5, maxPower: 15, status: 'Normal', devices: [] },
  { id: 15, name: 'C05', row: 'C', position: 5, usedU: 38, utilization: 90, power: 8.8, maxPower: 15, status: 'Normal', devices: [] },
  { id: 16, name: 'D01', row: 'D', position: 1, usedU: 32, utilization: 76, power: 7.0, maxPower: 15, status: 'Normal', devices: [] },
  { id: 17, name: 'D02', row: 'D', position: 2, usedU: 28, utilization: 67, power: 6.2, maxPower: 15, status: 'Normal', devices: [] },
  { id: 18, name: 'D03', row: 'D', position: 3, usedU: 35, utilization: 83, power: 7.8, maxPower: 15, status: 'Normal', devices: [] },
  { id: 19, name: 'D04', row: 'D', position: 4, usedU: 30, utilization: 71, power: 6.5, maxPower: 15, status: 'Normal', devices: [] },
  { id: 20, name: 'D05', row: 'D', position: 5, usedU: 38, utilization: 90, power: 8.5, maxPower: 15, status: 'Normal', devices: [] }
])

// Computed rows
const rowARacks = computed(() => racks.value.filter(r => r.row === 'A').sort((a, b) => a.position - b.position))
const rowBRacks = computed(() => racks.value.filter(r => r.row === 'B').sort((a, b) => a.position - b.position))
const rowCRacks = computed(() => racks.value.filter(r => r.row === 'C').sort((a, b) => a.position - b.position))
const rowDRacks = computed(() => racks.value.filter(r => r.row === 'D').sort((a, b) => a.position - b.position))

const currentRowRacksFront = computed(() => {
  return racks.value.filter(r => r.row === selectedRow.value).sort((a, b) => a.position - b.position)
})

// Actions
const selectRack = (rack: any) => {
  selectedRack.value = rack
}

const addRack = () => {
  rackForm.value = {
    id: null,
    name: '',
    row: 'A',
    position: 1,
    maxPower: 15,
    usedU: 0,
    utilization: 0,
    power: 0,
    status: 'Normal',
    devices: []
  }
  dialogTitle.value = 'Add Rack'
  rackDialogVisible.value = true
}

const editRack = (rack: any) => {
  rackForm.value = { ...rack }
  dialogTitle.value = 'Edit Rack'
  rackDialogVisible.value = true
}

const saveRack = () => {
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
      utilization: 0,
      power: 0,
      status: 'Normal',
      devices: []
    }
    racks.value.push(newRack)
    ElMessage.success('Rack added successfully')
  }
  rackDialogVisible.value = false
}

const deleteRack = (rack: any) => {
  ElMessageBox.confirm(`Delete rack ${rack.name}?`, 'Confirm', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = racks.value.findIndex(r => r.id === rack.id)
    if (index !== -1) {
      racks.value.splice(index, 1)
      if (selectedRack.value?.id === rack.id) {
        selectedRack.value = null
      }
      ElMessage.success('Rack deleted successfully')
    }
  }).catch(() => {})
}

const addDevice = () => {
  if (!selectedRack.value) {
    ElMessage.warning('Please select a rack first')
    return
  }
  deviceForm.value = {
    name: '',
    model: '',
    uPosition: 1,
    uSize: 1,
    power: 0
  }
  deviceDialogVisible.value = true
}

const editDevice = (device: any) => {
  deviceForm.value = { ...device }
  deviceDialogVisible.value = true
}

const saveDevice = () => {
  if (!selectedRack.value) return

  if (!selectedRack.value.devices) {
    selectedRack.value.devices = []
  }

  // Check for overlapping U positions
  const startU = deviceForm.value.uPosition
  const endU = startU + deviceForm.value.uSize - 1
  const overlapping = selectedRack.value.devices.some((d: any) => {
    const dStart = d.uPosition
    const dEnd = dStart + d.uSize - 1
    return !(endU < dStart || startU > dEnd)
  })

  if (overlapping) {
    ElMessage.warning('U position overlaps with existing device')
    return
  }

  selectedRack.value.devices.push({ ...deviceForm.value })

  // Update rack metrics
  selectedRack.value.usedU = selectedRack.value.devices.reduce((sum: number, d: any) => sum + d.uSize, 0)
  selectedRack.value.utilization = Math.round((selectedRack.value.usedU / 42) * 100)
  selectedRack.value.power = (selectedRack.value.devices.reduce((sum: number, d: any) => sum + d.power, 0) / 1000).toFixed(1)

  if (selectedRack.value.utilization >= 95) selectedRack.value.status = 'Critical'
  else if (selectedRack.value.utilization >= 85) selectedRack.value.status = 'Warning'
  else selectedRack.value.status = 'Normal'

  deviceDialogVisible.value = false
  ElMessage.success('Device added successfully')
}

const removeDevice = (device: any) => {
  if (!selectedRack.value) return

  const index = selectedRack.value.devices.findIndex((d: any) => d.name === device.name && d.uPosition === device.uPosition)
  if (index !== -1) {
    selectedRack.value.devices.splice(index, 1)

    // Update rack metrics
    selectedRack.value.usedU = selectedRack.value.devices.reduce((sum: number, d: any) => sum + d.uSize, 0)
    selectedRack.value.utilization = Math.round((selectedRack.value.usedU / 42) * 100)
    selectedRack.value.power = (selectedRack.value.devices.reduce((sum: number, d: any) => sum + d.power, 0) / 1000).toFixed(1)

    if (selectedRack.value.utilization >= 95) selectedRack.value.status = 'Critical'
    else if (selectedRack.value.utilization >= 85) selectedRack.value.status = 'Warning'
    else selectedRack.value.status = 'Normal'

    ElMessage.success('Device removed successfully')
  }
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
.rack-layout-container {
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
.rack-layout-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
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

/* Data Hall Section */
.data-hall-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.view-controls {
  display: flex;
  gap: 12px;
}

/* Top View Layout */
.top-view {
  overflow-x: auto;
}

.room-layout {
  min-width: 800px;
}

.aisle {
  padding: 16px;
  margin: 4px 0;
  border-radius: 12px;
  text-align: center;
}

.aisle.cold-aisle {
  background: #dbeafe;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

.aisle.hot-aisle {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.aisle-label {
  font-size: 12px;
  font-weight: 500;
}

.rack-row {
  display: flex;
  align-items: center;
  margin: 8px 0;
  gap: 12px;
}

.row-label {
  width: 60px;
  font-weight: 600;
  font-size: 14px;
  color: #64748b;
}

.racks-container {
  display: flex;
  flex: 1;
  gap: 8px;
  flex-wrap: wrap;
}

.rack-top-item {
  width: 100px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.rack-top-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rack-top-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.rack-top-item.edit-mode:hover {
  cursor: grab;
}

.rack-top-content {
  text-align: center;
}

.rack-name {
  display: block;
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 8px;
}

.rack-stats {
  margin-top: 4px;
}

.utilization {
  font-size: 12px;
  font-weight: 600;
}

.rack-actions {
  position: absolute;
  top: -10px;
  right: -10px;
  display: flex;
  gap: 4px;
}

/* Front View Layout */
.front-view {
  overflow-x: auto;
}

.front-view-container {
  min-width: 800px;
}

.rack-front-list {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.rack-front-item {
  width: 180px;
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.rack-front-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rack-front-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.rack-front-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rack-front-header .rack-name {
  font-size: 16px;
  margin: 0;
}

.rack-u-viz {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin: 12px 0;
  background: #e2e8f0;
  border-radius: 8px;
  padding: 4px;
}

.u-block {
  border-radius: 3px;
  transition: all 0.1s;
}

.u-block.occupied {
  background: #3b82f6;
}

.u-block.free {
  background: #10b981;
}

.rack-front-footer {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #64748b;
  margin-top: 8px;
}

.rack-front-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* Legend */
.layout-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
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

.legend-color.cold-aisle { background: #dbeafe; border: 1px solid #bfdbfe; }
.legend-color.hot-aisle { background: #fee2e2; border: 1px solid #fecaca; }
.legend-color.rack-normal { background: #10b981; }
.legend-color.rack-warning { background: #f59e0b; }
.legend-color.rack-critical { background: #ef4444; }
.legend-color.occupied { background: #3b82f6; }
.legend-color.free { background: #10b981; }

/* Rack Details Section */
.rack-details-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.details-actions {
  display: flex;
  gap: 8px;
}

.rack-details-content {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.details-info {
  flex: 1;
  min-width: 300px;
}

.details-devices {
  flex: 2;
  min-width: 400px;
}

.details-devices h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .rack-details-content {
    flex-direction: column;
  }
  .details-devices {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .rack-layout-main { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .section-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .rack-top-item { width: 80px; }
  .rack-front-list { flex-wrap: wrap; }
}
</style>