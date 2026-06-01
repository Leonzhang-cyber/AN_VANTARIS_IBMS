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
        <div class="loading-tip">Capacity Zones</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="capacity-zones">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Capacity Zones</h2>
        <p class="subtitle">Manage power, cooling, and rack capacity zones across data center spaces</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddZoneDialog">
          <el-icon><Plus /></el-icon> Add Capacity Zone
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalPowerCapacity }} kW</div>
          <div class="stat-label">Total Power Capacity</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">❄️</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalCoolingCapacity }} kW</div>
          <div class="stat-label">Total Cooling Capacity</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgPowerUtilization }}%</div>
          <div class="stat-label">Avg Power Utilization</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🖥️</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalRackUnits }}</div>
          <div class="stat-label">Total Rack Units (U)</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by zone name, location or type..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterBuilding" placeholder="Building" clearable style="width: 180px">
          <el-option label="All Buildings" value="all" />
          <el-option v-for="b in uniqueBuildings" :key="b" :label="b" :value="b" />
        </el-select>
        <el-select v-model="filterZoneType" placeholder="Zone Type" clearable style="width: 160px">
          <el-option label="All Types" value="all" />
          <el-option label="Power Zone" value="power" />
          <el-option label="Cooling Zone" value="cooling" />
          <el-option label="Rack Zone" value="rack" />
          <el-option label="Mixed Zone" value="mixed" />
        </el-select>
      </div>
    </div>

    <!-- Capacity Zones Grid -->
    <div class="zones-grid">
      <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="getZoneStatusClass(zone)">
        <div class="zone-header">
          <div class="zone-icon">{{ getZoneIcon(zone.zoneType) }}</div>
          <div class="zone-info">
            <div class="zone-name">{{ zone.name }}</div>
            <div class="zone-code">{{ zone.code }}</div>
          </div>
          <div class="zone-status">
            <span class="status-badge" :class="getZoneStatus(zone)">{{ getZoneStatusText(zone) }}</span>
          </div>
        </div>

        <div class="zone-location">
          <el-icon><Location /></el-icon>
          <span>{{ zone.buildingName }} - Floor {{ zone.floorLevel }} ({{ zone.floorCode }})</span>
        </div>

        <!-- Power Capacity Section -->
        <div v-if="zone.zoneType === 'power' || zone.zoneType === 'mixed'" class="capacity-section">
          <div class="section-title">Power Capacity</div>
          <div class="capacity-bar">
            <div class="bar-label">Total: {{ zone.powerCapacity }} kW</div>
            <div class="progress-wrapper">
              <el-progress :percentage="zone.powerUtilization" :stroke-width="10" :color="getUtilizationColor(zone.powerUtilization)" />
            </div>
            <div class="bar-detail">
              <span>Used: {{ zone.powerUsed }} kW</span>
              <span>Available: {{ zone.powerAvailable }} kW</span>
              <span>Redundant: {{ zone.powerRedundant }} kW</span>
            </div>
          </div>
        </div>

        <!-- Cooling Capacity Section -->
        <div v-if="zone.zoneType === 'cooling' || zone.zoneType === 'mixed'" class="capacity-section">
          <div class="section-title">Cooling Capacity</div>
          <div class="capacity-bar">
            <div class="bar-label">Total: {{ zone.coolingCapacity }} kW</div>
            <div class="progress-wrapper">
              <el-progress :percentage="zone.coolingUtilization" :stroke-width="10" :color="getUtilizationColor(zone.coolingUtilization)" />
            </div>
            <div class="bar-detail">
              <span>Used: {{ zone.coolingUsed }} kW</span>
              <span>Available: {{ zone.coolingAvailable }} kW</span>
              <span>Reserve: {{ zone.coolingReserve }} kW</span>
            </div>
          </div>
        </div>

        <!-- Rack Capacity Section -->
        <div v-if="zone.zoneType === 'rack' || zone.zoneType === 'mixed'" class="capacity-section">
          <div class="section-title">Rack Capacity</div>
          <div class="capacity-bar">
            <div class="bar-label">Total: {{ zone.rackTotal }} U</div>
            <div class="progress-wrapper">
              <el-progress :percentage="zone.rackUtilization" :stroke-width="10" :color="getUtilizationColor(zone.rackUtilization)" />
            </div>
            <div class="bar-detail">
              <span>Occupied: {{ zone.rackOccupied }} U</span>
              <span>Available: {{ zone.rackAvailable }} U</span>
              <span>Racks: {{ zone.rackCount }} units</span>
            </div>
          </div>
        </div>

        <div class="zone-alerts" v-if="zone.alerts && zone.alerts.length > 0">
          <div v-for="alert in zone.alerts" :key="alert.time" class="alert-item">
            <el-icon><Warning /></el-icon>
            <span>{{ alert.message }}</span>
          </div>
        </div>

        <div class="zone-actions">
          <el-button size="small" type="primary" plain @click="viewZone(zone)">
            <el-icon><View /></el-icon> Details
          </el-button>
          <el-button size="small" type="info" plain @click="editZone(zone)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteZone(zone)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredZones.length === 0" class="empty-state">
      <div class="empty-icon">⚡</div>
      <div class="empty-title">No capacity zones found</div>
      <div class="empty-desc">Add a capacity zone to start managing power and cooling resources</div>
      <el-button type="primary" @click="openAddZoneDialog">Add Capacity Zone</el-button>
    </div>

    <!-- Add/Edit Zone Dialog -->
    <el-dialog v-model="showZoneDialog" :title="dialogTitle" width="700px">
      <el-form :model="zoneForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Zone Name" required>
              <el-input v-model="zoneForm.name" placeholder="Enter zone name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Zone Code">
              <el-input v-model="zoneForm.code" placeholder="e.g., PWR-ZN-01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Building" required>
          <el-select v-model="zoneForm.buildingId" placeholder="Select building" style="width: 100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Floor" required>
          <el-select v-model="zoneForm.floorId" placeholder="Select floor" style="width: 100%" :disabled="!zoneForm.buildingId">
            <el-option v-for="f in availableFloors" :key="f.id" :label="`Floor ${f.level} - ${f.code}`" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Zone Type" required>
          <el-select v-model="zoneForm.zoneType" style="width: 100%">
            <el-option label="Power Zone" value="power" />
            <el-option label="Cooling Zone" value="cooling" />
            <el-option label="Rack Zone" value="rack" />
            <el-option label="Mixed Zone" value="mixed" />
          </el-select>
        </el-form-item>

        <div v-if="zoneForm.zoneType === 'power' || zoneForm.zoneType === 'mixed'">
          <div class="dialog-section-title">Power Configuration</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="Total Power Capacity (kW)">
                <el-input-number v-model="zoneForm.powerCapacity" :min="0" :step="50" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Redundant Capacity (kW)">
                <el-input-number v-model="zoneForm.powerRedundant" :min="0" :step="50" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div v-if="zoneForm.zoneType === 'cooling' || zoneForm.zoneType === 'mixed'">
          <div class="dialog-section-title">Cooling Configuration</div>
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="Total Cooling Capacity (kW)">
                <el-input-number v-model="zoneForm.coolingCapacity" :min="0" :step="50" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Reserve Capacity (kW)">
                <el-input-number v-model="zoneForm.coolingReserve" :min="0" :step="50" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div v-if="zoneForm.zoneType === 'rack' || zoneForm.zoneType === 'mixed'">
          <div class="dialog-section-title">Rack Configuration</div>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item label="Number of Racks">
                <el-input-number v-model="zoneForm.rackCount" :min="0" :step="1" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Total Rack Units (U)">
                <el-input-number v-model="zoneForm.rackTotal" :min="0" :step="100" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Max Power per Rack (kW)">
                <el-input-number v-model="zoneForm.maxPowerPerRack" :min="0" :step="5" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <el-form-item label="Description">
          <el-input v-model="zoneForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showZoneDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveZone">Save Zone</el-button>
      </template>
    </el-dialog>

    <!-- Zone Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedZone?.name" width="800px">
      <div v-if="selectedZone">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Zone ID">{{ selectedZone.id }}</el-descriptions-item>
          <el-descriptions-item label="Zone Code">{{ selectedZone.code }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedZone.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Floor">Floor {{ selectedZone.floorLevel }} ({{ selectedZone.floorCode }})</el-descriptions-item>
          <el-descriptions-item label="Zone Type">{{ getZoneTypeLabel(selectedZone.zoneType) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', getZoneStatus(selectedZone)]">{{ getZoneStatusText(selectedZone) }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedZone.zoneType === 'power' || selectedZone.zoneType === 'mixed'" class="detail-section">
          <h4>Power Capacity</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Total Capacity">{{ selectedZone.powerCapacity }} kW</el-descriptions-item>
            <el-descriptions-item label="Currently Used">{{ selectedZone.powerUsed }} kW</el-descriptions-item>
            <el-descriptions-item label="Available">{{ selectedZone.powerAvailable }} kW</el-descriptions-item>
            <el-descriptions-item label="Redundant">{{ selectedZone.powerRedundant }} kW</el-descriptions-item>
            <el-descriptions-item label="Utilization">
              <el-progress :percentage="selectedZone.powerUtilization" :stroke-width="12" :color="getUtilizationColor(selectedZone.powerUtilization)" />
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="selectedZone.zoneType === 'cooling' || selectedZone.zoneType === 'mixed'" class="detail-section">
          <h4>Cooling Capacity</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Total Capacity">{{ selectedZone.coolingCapacity }} kW</el-descriptions-item>
            <el-descriptions-item label="Currently Used">{{ selectedZone.coolingUsed }} kW</el-descriptions-item>
            <el-descriptions-item label="Available">{{ selectedZone.coolingAvailable }} kW</el-descriptions-item>
            <el-descriptions-item label="Reserve">{{ selectedZone.coolingReserve }} kW</el-descriptions-item>
            <el-descriptions-item label="Utilization">
              <el-progress :percentage="selectedZone.coolingUtilization" :stroke-width="12" :color="getUtilizationColor(selectedZone.coolingUtilization)" />
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="selectedZone.zoneType === 'rack' || selectedZone.zoneType === 'mixed'" class="detail-section">
          <h4>Rack Capacity</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Number of Racks">{{ selectedZone.rackCount }}</el-descriptions-item>
            <el-descriptions-item label="Total Rack Units">{{ selectedZone.rackTotal }} U</el-descriptions-item>
            <el-descriptions-item label="Occupied">{{ selectedZone.rackOccupied }} U</el-descriptions-item>
            <el-descriptions-item label="Available">{{ selectedZone.rackAvailable }} U</el-descriptions-item>
            <el-descriptions-item label="Max Power per Rack">{{ selectedZone.maxPowerPerRack }} kW</el-descriptions-item>
            <el-descriptions-item label="Utilization">
              <el-progress :percentage="selectedZone.rackUtilization" :stroke-width="12" :color="getUtilizationColor(selectedZone.rackUtilization)" />
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editZone(selectedZone); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, Location, Warning } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading capacity zones data...',
  'Fetching power and cooling metrics...',
  'Calculating utilization rates...',
  'Almost ready...'
]

// Building interface
interface Building {
  id: number
  name: string
}

// Floor interface
interface Floor {
  id: number
  buildingId: number
  level: number
  code: string
}

// Capacity Zone interface
interface CapacityZone {
  id: number
  name: string
  code: string
  buildingId: number
  buildingName: string
  floorId: number
  floorLevel: number
  floorCode: string
  zoneType: string
  powerCapacity: number
  powerUsed: number
  powerAvailable: number
  powerRedundant: number
  powerUtilization: number
  coolingCapacity: number
  coolingUsed: number
  coolingAvailable: number
  coolingReserve: number
  coolingUtilization: number
  rackCount: number
  rackTotal: number
  rackOccupied: number
  rackAvailable: number
  rackUtilization: number
  maxPowerPerRack: number
  alerts: { severity: string; message: string; time: string }[]
  description: string
}

// Sample buildings data
const buildings = ref<Building[]>([
  { id: 1, name: 'Data Center A' },
  { id: 2, name: 'Data Center B' }
])

// Sample floors data
const floors = ref<Floor[]>([
  { id: 1, buildingId: 1, level: 1, code: 'L1' },
  { id: 2, buildingId: 1, level: 2, code: 'L2' },
  { id: 3, buildingId: 1, level: 3, code: 'L3' },
  { id: 4, buildingId: 2, level: 1, code: 'L1' },
  { id: 5, buildingId: 2, level: 2, code: 'L2' }
])

// Sample capacity zones data
const capacityZones = ref<CapacityZone[]>([
  {
    id: 1,
    name: 'Power Zone A',
    code: 'PWR-ZN-A',
    buildingId: 1,
    buildingName: 'Data Center A',
    floorId: 1,
    floorLevel: 1,
    floorCode: 'L1',
    zoneType: 'power',
    powerCapacity: 500,
    powerUsed: 380,
    powerAvailable: 120,
    powerRedundant: 100,
    powerUtilization: 76,
    coolingCapacity: 0,
    coolingUsed: 0,
    coolingAvailable: 0,
    coolingReserve: 0,
    coolingUtilization: 0,
    rackCount: 0,
    rackTotal: 0,
    rackOccupied: 0,
    rackAvailable: 0,
    rackUtilization: 0,
    maxPowerPerRack: 0,
    alerts: [],
    description: 'Primary power distribution zone'
  },
  {
    id: 2,
    name: 'Cooling Zone 1',
    code: 'COL-ZN-01',
    buildingId: 1,
    buildingName: 'Data Center A',
    floorId: 2,
    floorLevel: 2,
    floorCode: 'L2',
    zoneType: 'cooling',
    powerCapacity: 0,
    powerUsed: 0,
    powerAvailable: 0,
    powerRedundant: 0,
    powerUtilization: 0,
    coolingCapacity: 400,
    coolingUsed: 310,
    coolingAvailable: 90,
    coolingReserve: 50,
    coolingUtilization: 77.5,
    rackCount: 0,
    rackTotal: 0,
    rackOccupied: 0,
    rackAvailable: 0,
    rackUtilization: 0,
    maxPowerPerRack: 0,
    alerts: [],
    description: 'Server room cooling zone'
  },
  {
    id: 3,
    name: 'Rack Zone R01',
    code: 'RCK-ZN-R01',
    buildingId: 1,
    buildingName: 'Data Center A',
    floorId: 2,
    floorLevel: 2,
    floorCode: 'L2',
    zoneType: 'rack',
    powerCapacity: 0,
    powerUsed: 0,
    powerAvailable: 0,
    powerRedundant: 0,
    powerUtilization: 0,
    coolingCapacity: 0,
    coolingUsed: 0,
    coolingAvailable: 0,
    coolingReserve: 0,
    coolingUtilization: 0,
    rackCount: 12,
    rackTotal: 504,
    rackOccupied: 380,
    rackAvailable: 124,
    rackUtilization: 75.4,
    maxPowerPerRack: 8,
    alerts: [
      { severity: 'warning', message: 'High density rack cluster approaching power limit', time: '2025-01-16 09:30:00' }
    ],
    description: 'Main server rack zone'
  },
  {
    id: 4,
    name: 'Mixed Zone - West Wing',
    code: 'MIX-ZN-W01',
    buildingId: 1,
    buildingName: 'Data Center A',
    floorId: 3,
    floorLevel: 3,
    floorCode: 'L3',
    zoneType: 'mixed',
    powerCapacity: 350,
    powerUsed: 280,
    powerAvailable: 70,
    powerRedundant: 50,
    powerUtilization: 80,
    coolingCapacity: 300,
    coolingUsed: 240,
    coolingAvailable: 60,
    coolingReserve: 30,
    coolingUtilization: 80,
    rackCount: 8,
    rackTotal: 336,
    rackOccupied: 250,
    rackAvailable: 86,
    rackUtilization: 74.4,
    maxPowerPerRack: 10,
    alerts: [],
    description: 'Mixed use zone with colocation space'
  },
  {
    id: 5,
    name: 'Power Zone B',
    code: 'PWR-ZN-B',
    buildingId: 2,
    buildingName: 'Data Center B',
    floorId: 4,
    floorLevel: 1,
    floorCode: 'L1',
    zoneType: 'power',
    powerCapacity: 800,
    powerUsed: 520,
    powerAvailable: 280,
    powerRedundant: 150,
    powerUtilization: 65,
    coolingCapacity: 0,
    coolingUsed: 0,
    coolingAvailable: 0,
    coolingReserve: 0,
    coolingUtilization: 0,
    rackCount: 0,
    rackTotal: 0,
    rackOccupied: 0,
    rackAvailable: 0,
    rackUtilization: 0,
    maxPowerPerRack: 0,
    alerts: [
      { severity: 'info', message: 'New UPS installed - capacity increased', time: '2025-01-15 14:00:00' }
    ],
    description: 'Secondary power distribution'
  },
  {
    id: 6,
    name: 'Rack Zone R02',
    code: 'RCK-ZN-R02',
    buildingId: 2,
    buildingName: 'Data Center B',
    floorId: 5,
    floorLevel: 2,
    floorCode: 'L2',
    zoneType: 'rack',
    powerCapacity: 0,
    powerUsed: 0,
    powerAvailable: 0,
    powerRedundant: 0,
    powerUtilization: 0,
    coolingCapacity: 0,
    coolingUsed: 0,
    coolingAvailable: 0,
    coolingReserve: 0,
    coolingUtilization: 0,
    rackCount: 15,
    rackTotal: 630,
    rackOccupied: 420,
    rackAvailable: 210,
    rackUtilization: 66.7,
    maxPowerPerRack: 7,
    alerts: [],
    description: 'High density compute zone'
  }
])

// UI State
const searchText = ref('')
const filterBuilding = ref('all')
const filterZoneType = ref('all')
const showZoneDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedZone = ref<CapacityZone | null>(null)

const zoneForm = ref({
  name: '',
  code: '',
  buildingId: 1,
  floorId: 1,
  zoneType: 'power',
  powerCapacity: 0,
  powerRedundant: 0,
  coolingCapacity: 0,
  coolingReserve: 0,
  rackCount: 0,
  rackTotal: 0,
  maxPowerPerRack: 0,
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Capacity Zone' : 'Add Capacity Zone')

const totalPowerCapacity = computed(() => capacityZones.value.reduce((sum, z) => sum + z.powerCapacity, 0))
const totalCoolingCapacity = computed(() => capacityZones.value.reduce((sum, z) => sum + z.coolingCapacity, 0))
const avgPowerUtilization = computed(() => {
  const total = capacityZones.value.reduce((sum, z) => sum + z.powerUtilization, 0)
  return Math.round(total / capacityZones.value.filter(z => z.zoneType !== 'cooling').length)
})
const totalRackUnits = computed(() => capacityZones.value.reduce((sum, z) => sum + z.rackTotal, 0))

const uniqueBuildings = computed(() => {
  const buildingsSet = new Set(capacityZones.value.map(z => z.buildingName))
  return Array.from(buildingsSet)
})

const availableFloors = computed(() => {
  if (!zoneForm.value.buildingId) return []
  return floors.value.filter(f => f.buildingId === zoneForm.value.buildingId)
})

const filteredZones = computed(() => {
  let filtered = [...capacityZones.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(z =>
        z.name.toLowerCase().includes(keyword) ||
        z.code.toLowerCase().includes(keyword)
    )
  }

  if (filterBuilding.value !== 'all') {
    filtered = filtered.filter(z => z.buildingName === filterBuilding.value)
  }

  if (filterZoneType.value !== 'all') {
    filtered = filtered.filter(z => z.zoneType === filterZoneType.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getZoneIcon = (type: string) => {
  const map: Record<string, string> = {
    power: '⚡',
    cooling: '❄️',
    rack: '🖥️',
    mixed: '🎯'
  }
  return map[type] || '📍'
}

const getZoneTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    power: 'Power Zone',
    cooling: 'Cooling Zone',
    rack: 'Rack Zone',
    mixed: 'Mixed Zone'
  }
  return map[type] || type
}

const getUtilizationColor = (percentage: number) => {
  if (percentage >= 85) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#67c23a'
}

const getZoneStatus = (zone: CapacityZone) => {
  if (zone.zoneType === 'power' && zone.powerUtilization >= 85) return 'critical'
  if (zone.zoneType === 'cooling' && zone.coolingUtilization >= 85) return 'critical'
  if (zone.zoneType === 'rack' && zone.rackUtilization >= 85) return 'critical'
  if (zone.zoneType === 'power' && zone.powerUtilization >= 70) return 'warning'
  if (zone.zoneType === 'cooling' && zone.coolingUtilization >= 70) return 'warning'
  if (zone.zoneType === 'rack' && zone.rackUtilization >= 70) return 'warning'
  if (zone.alerts && zone.alerts.length > 0) return 'warning'
  return 'healthy'
}

const getZoneStatusClass = (zone: CapacityZone) => {
  const status = getZoneStatus(zone)
  return status === 'critical' ? 'critical' : status === 'warning' ? 'warning' : 'healthy'
}

const getZoneStatusText = (zone: CapacityZone) => {
  const status = getZoneStatus(zone)
  return status === 'critical' ? 'Critical' : status === 'warning' ? 'Warning' : 'Healthy'
}

// Watch building change
watch(() => zoneForm.value.buildingId, (newVal) => {
  if (newVal && availableFloors.value.length > 0) {
    zoneForm.value.floorId = availableFloors.value[0].id
  }
})

// Zone CRUD operations
const openAddZoneDialog = () => {
  isEditing.value = false
  zoneForm.value = {
    name: '',
    code: '',
    buildingId: buildings.value[0]?.id || 1,
    floorId: 1,
    zoneType: 'power',
    powerCapacity: 0,
    powerRedundant: 0,
    coolingCapacity: 0,
    coolingReserve: 0,
    rackCount: 0,
    rackTotal: 0,
    maxPowerPerRack: 0,
    description: ''
  }
  showZoneDialog.value = true
}

const editZone = (zone: CapacityZone) => {
  isEditing.value = true
  selectedZone.value = zone
  zoneForm.value = {
    name: zone.name,
    code: zone.code,
    buildingId: zone.buildingId,
    floorId: zone.floorId,
    zoneType: zone.zoneType,
    powerCapacity: zone.powerCapacity,
    powerRedundant: zone.powerRedundant,
    coolingCapacity: zone.coolingCapacity,
    coolingReserve: zone.coolingReserve,
    rackCount: zone.rackCount,
    rackTotal: zone.rackTotal,
    maxPowerPerRack: zone.maxPowerPerRack,
    description: zone.description || ''
  }
  showZoneDialog.value = true
}

const saveZone = () => {
  if (!zoneForm.value.name.trim()) {
    ElMessage.warning('Please enter zone name')
    return
  }

  const building = buildings.value.find(b => b.id === zoneForm.value.buildingId)
  const floor = floors.value.find(f => f.id === zoneForm.value.floorId)

  if (!building || !floor) {
    ElMessage.warning('Please select building and floor')
    return
  }

  if (isEditing.value && selectedZone.value) {
    const index = capacityZones.value.findIndex(z => z.id === selectedZone.value!.id)
    if (index !== -1) {
      capacityZones.value[index] = {
        ...capacityZones.value[index],
        name: zoneForm.value.name,
        code: zoneForm.value.code,
        buildingId: zoneForm.value.buildingId,
        buildingName: building.name,
        floorId: zoneForm.value.floorId,
        floorLevel: floor.level,
        floorCode: floor.code,
        zoneType: zoneForm.value.zoneType,
        powerCapacity: zoneForm.value.powerCapacity,
        powerRedundant: zoneForm.value.powerRedundant,
        coolingCapacity: zoneForm.value.coolingCapacity,
        coolingReserve: zoneForm.value.coolingReserve,
        rackCount: zoneForm.value.rackCount,
        rackTotal: zoneForm.value.rackTotal,
        maxPowerPerRack: zoneForm.value.maxPowerPerRack,
        description: zoneForm.value.description
      }
      ElMessage.success('Zone updated successfully')
    }
  } else {
    const newZone: CapacityZone = {
      id: Date.now(),
      name: zoneForm.value.name,
      code: zoneForm.value.code || `ZN-${capacityZones.value.length + 1}`,
      buildingId: zoneForm.value.buildingId,
      buildingName: building.name,
      floorId: zoneForm.value.floorId,
      floorLevel: floor.level,
      floorCode: floor.code,
      zoneType: zoneForm.value.zoneType,
      powerCapacity: zoneForm.value.powerCapacity,
      powerUsed: 0,
      powerAvailable: zoneForm.value.powerCapacity,
      powerRedundant: zoneForm.value.powerRedundant,
      powerUtilization: 0,
      coolingCapacity: zoneForm.value.coolingCapacity,
      coolingUsed: 0,
      coolingAvailable: zoneForm.value.coolingCapacity,
      coolingReserve: zoneForm.value.coolingReserve,
      coolingUtilization: 0,
      rackCount: zoneForm.value.rackCount,
      rackTotal: zoneForm.value.rackTotal,
      rackOccupied: 0,
      rackAvailable: zoneForm.value.rackTotal,
      rackUtilization: 0,
      maxPowerPerRack: zoneForm.value.maxPowerPerRack,
      alerts: [],
      description: zoneForm.value.description
    }
    capacityZones.value.push(newZone)
    ElMessage.success('Zone added successfully')
  }

  showZoneDialog.value = false
}

const viewZone = (zone: CapacityZone) => {
  selectedZone.value = zone
  showDetailDialog.value = true
}

const deleteZone = (zone: CapacityZone) => {
  ElMessageBox.confirm(
      `Delete capacity zone "${zone.name}"? This will also remove all associated capacity data.`,
      'Delete Zone',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = capacityZones.value.findIndex(z => z.id === zone.id)
    if (index !== -1) {
      capacityZones.value.splice(index, 1)
      ElMessage.success('Zone deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredZones.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `capacity_zones_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Export completed')
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

// Loading animation
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
    }, 400)
  }, 2000)
})
</script>

<style scoped>
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

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.capacity-zones {
  padding: 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1565c0, #1976d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #1565c0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
}

.filter-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Zones Grid */
.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}

.zone-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid;
}

.zone-card.healthy { border-left-color: #67c23a; }
.zone-card.warning { border-left-color: #e6a23c; }
.zone-card.critical { border-left-color: #f56c6c; }

.zone-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.zone-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.zone-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.zone-info {
  flex: 1;
}

.zone-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.zone-code {
  font-size: 11px;
  color: #909399;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.healthy { background: #e8f5e9; color: #67c23a; }
.status-badge.warning { background: #fff7e6; color: #e6a23c; }
.status-badge.critical { background: #ffefef; color: #f56c6c; }

.zone-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.capacity-section {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.capacity-bar {
  margin-bottom: 8px;
}

.bar-label {
  font-size: 12px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 6px;
}

.progress-wrapper {
  margin-bottom: 8px;
}

.bar-detail {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #909399;
  flex-wrap: wrap;
  gap: 8px;
}

.zone-alerts {
  background: #fff7e6;
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 16px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #e6a23c;
  margin-bottom: 4px;
}

.zone-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
  margin-top: 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

/* Dialog */
.dialog-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
  margin: 16px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.detail-section {
  margin-top: 20px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .capacity-zones { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .zones-grid { grid-template-columns: 1fr; }
  .bar-detail { flex-direction: column; gap: 4px; }
}
</style>