<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Rack Maintenance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Server Rack & Infrastructure Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="rack-maintenance-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Box /></el-icon>
          Rack Maintenance
        </h1>
        <div class="page-subtitle">Monitor rack health, capacity, and maintenance schedules</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddRackDialog">
          <el-icon><Plus /></el-icon> Add Rack
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalRacks }}</div>
          <div class="stat-label">Total Racks</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.healthyRacks }}</div>
          <div class="stat-label">Healthy</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.warningRacks }}</div>
          <div class="stat-label">Warning</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.criticalRacks }}</div>
          <div class="stat-label">Critical</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Average Power Density</div>
        <div class="metric-value">{{ metrics.avgPowerDensity }}<span class="metric-unit">kW/rack</span></div>
        <div class="metric-trend" :class="metrics.powerTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.powerTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.powerTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average U Utilization</div>
        <div class="metric-value">{{ metrics.avgUtilization }}<span class="metric-unit">%</span></div>
        <div class="metric-trend positive">↑ {{ metrics.utilizationGrowth }}% vs last month</div>
        <div class="metric-target">Target: 80-85%</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Temperature</div>
        <div class="metric-value">{{ metrics.avgTemp }}<span class="metric-unit">°C</span></div>
        <div class="metric-trend" :class="metrics.tempTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.tempTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.tempTrend) }}°C vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Available U Space</div>
        <div class="metric-value">{{ metrics.availableUSpace }}</div>
        <div class="metric-sub">Total: {{ metrics.totalUSpace }} U</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Rack Health Distribution</span>
          <span class="chart-subtitle">Current health status by rack</span>
        </div>
        <div class="chart-container" ref="healthChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">U Space Utilization by Row</span>
          <span class="chart-subtitle">Space usage per rack row</span>
        </div>
        <div class="chart-container" ref="utilizationChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Temperature Distribution</span>
          <span class="chart-subtitle">Rack inlet temperatures</span>
        </div>
        <div class="chart-container" ref="tempChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Power Consumption by Row</span>
          <span class="chart-subtitle">Total power per rack row (kW)</span>
        </div>
        <div class="chart-container" ref="powerChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by rack ID or location..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="rowFilter" placeholder="Row" clearable style="width: 120px">
          <el-option v-for="r in uniqueRows" :key="r" :label="r" :value="r" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Healthy" value="healthy" />
          <el-option label="Warning" value="warning" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="coolingTypeFilter" placeholder="Cooling Type" clearable style="width: 150px">
          <el-option label="Cold Aisle Containment" value="Cold Aisle" />
          <el-option label="Hot Aisle Containment" value="Hot Aisle" />
          <el-option label="In-Row Cooling" value="In-Row" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Racks Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Rack Inventory</span>
        <el-button size="small" @click="viewAllRacks">View All →</el-button>
      </div>
      <el-table :data="paginatedRacks" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewRackDetail">
        <el-table-column prop="id" label="Rack ID"  />
        <el-table-column prop="name" label="Rack Name"  />
        <el-table-column prop="row" label="Row"  />
        <el-table-column prop="location" label="Location" />
        <el-table-column prop="health" label="Health">
          <template #default="{ row }">
            <el-progress :percentage="row.health" :stroke-width="8" :color="getHealthColor(row.health)" />
          </template>
        </el-table-column>
        <el-table-column prop="utilization" label="U Space Usage" >
          <template #default="{ row }">
            <el-progress :percentage="row.utilization" :stroke-width="8" :color="getUtilizationColor(row.utilization)">
              <span>{{ row.usedUSpace }}/{{ row.totalUSpace }} U</span>
            </el-progress>
          </template>
        </el-table-column>
        <el-table-column prop="power" label="Power (kW)">
          <template #default="{ row }">
            <span :class="getPowerClass(row.power, row.powerCapacity)">{{ row.power }} / {{ row.powerCapacity }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="temp" label="Inlet Temp" >
          <template #default="{ row }">
            <span :class="getTempClass(row.temp)">{{ row.temp }}°C</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastMaintenance" label="Last Maintenance" width="120" />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="scheduleMaintenance(row)">Maintain</el-button>
            <el-button link type="warning" size="small" @click.stop="viewHistory(row)">History</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Rack Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedRack?.name" width="1000px" class="rack-dialog">
      <div v-if="selectedRack" class="rack-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedRack.health) }">
              {{ selectedRack.health }}%
            </div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedRack.utilization }}%</div>
            <div class="detail-stat-label">U Space Usage</div>
            <div class="detail-stat-sub">{{ selectedRack.usedUSpace }}/{{ selectedRack.totalUSpace }} U</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedRack.power }} kW</div>
            <div class="detail-stat-label">Power Load</div>
            <div class="detail-stat-sub">Capacity: {{ selectedRack.powerCapacity }} kW</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedRack.temp }}°C</div>
            <div class="detail-stat-label">Inlet Temp</div>
            <div class="detail-stat-sub">Target: 22-24°C</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="Rack ID">{{ selectedRack.id }}</el-descriptions-item>
          <el-descriptions-item label="Row">{{ selectedRack.row }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedRack.location }}</el-descriptions-item>
          <el-descriptions-item label="Cooling Type">{{ selectedRack.coolingType }}</el-descriptions-item>
          <el-descriptions-item label="PDU Type">{{ selectedRack.pduType }}</el-descriptions-item>
          <el-descriptions-item label="Network Switches">{{ selectedRack.networkSwitches }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedRack.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedRack.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedRack.nextMaintenance }}</el-descriptions-item>
        </el-descriptions>

        <!-- U Space Visualization -->
        <div class="detail-section">
          <div class="section-title">U Space Map</div>
          <div class="u-space-map">
            <div
                v-for="u in selectedRack.uSpaceMap"
                :key="u.uPosition"
                class="u-unit"
                :class="u.status"
                @mouseenter="showUTooltip(u)"
                @mouseleave="hideUTooltip"
            >
              <div class="u-number">{{ u.uPosition }}</div>
              <div class="u-tooltip" v-if="hoveredU === u.uPosition">
                <div class="tooltip-title">{{ u.deviceName || 'Empty Slot' }}</div>
                <div class="tooltip-info" v-if="u.deviceName">
                  <span>Power: {{ u.power }}W</span>
                  <span>Temp: {{ u.temp }}°C</span>
                </div>
              </div>
            </div>
          </div>
          <div class="u-legend">
            <span><span class="legend-box occupied"></span> Occupied</span>
            <span><span class="legend-box empty"></span> Empty</span>
            <span><span class="legend-box warning"></span> Warning</span>
            <span><span class="legend-box critical"></span> Critical</span>
          </div>
        </div>

        <!-- Equipment List -->
        <div class="detail-section">
          <div class="section-title">Installed Equipment</div>
          <el-table :data="selectedRack.equipment" border stripe>
            <el-table-column prop="position" label="U Position" width="100" />
            <el-table-column prop="name" label="Device Name" min-width="200" />
            <el-table-column prop="type" label="Type" width="120" />
            <el-table-column prop="power" label="Power (W)" width="100" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Good' ? 'success' : (row.status === 'Warning' ? 'warning' : 'danger')" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastMaintenance" label="Last Maintenance" width="120" />
          </el-table>
        </div>

        <!-- Maintenance History -->
        <div class="detail-section">
          <div class="section-title">Maintenance History</div>
          <el-table :data="selectedRack.maintenanceHistory" border stripe>
            <el-table-column prop="date" label="Date" width="120" />
            <el-table-column prop="type" label="Type" width="120">
              <template #default="{ row }">
                <el-tag :type="row.type === 'Preventive' ? 'success' : (row.type === 'Corrective' ? 'warning' : 'info')" size="small">
                  {{ row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="250" />
            <el-table-column prop="technician" label="Technician" width="140" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Completed' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Sensors Data -->
        <div class="detail-section">
          <div class="section-title">Environment Sensors</div>
          <el-table :data="selectedRack.sensors" border stripe>
            <el-table-column prop="sensorId" label="Sensor ID" width="120" />
            <el-table-column prop="type" label="Type" width="120" />
            <el-table-column prop="value" label="Value" width="120" />
            <el-table-column prop="unit" label="Unit" width="80" />
            <el-table-column prop="threshold" label="Threshold" width="120" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Normal' ? 'success' : (row.status === 'Warning' ? 'warning' : 'danger')" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Alerts -->
        <div class="detail-section" v-if="selectedRack.alerts.length > 0">
          <div class="section-title">Recent Alerts</div>
          <el-table :data="selectedRack.alerts" border stripe>
            <el-table-column prop="date" label="Date" width="180" />
            <el-table-column prop="severity" label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'High' ? 'danger' : (row.severity === 'Medium' ? 'warning' : 'info')" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="250" />
            <el-table-column prop="resolved" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.resolved ? 'success' : 'danger'" size="small">
                  {{ row.resolved ? 'Resolved' : 'Open' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleMaintenance(selectedRack)">Schedule Maintenance</el-button>
        <el-button type="warning" @click="generateRackReport(selectedRack)">Generate Report</el-button>
      </template>
    </el-dialog>

    <!-- Add Rack Dialog -->
    <el-dialog v-model="addRackDialogVisible" title="Add New Rack" width="550px">
      <el-form :model="rackForm" label-width="120px">
        <el-form-item label="Rack Name" required>
          <el-input v-model="rackForm.name" placeholder="e.g., Rack A-01" />
        </el-form-item>
        <el-form-item label="Row" required>
          <el-select v-model="rackForm.row" placeholder="Select row" style="width: 100%">
            <el-option label="Row A" value="Row A" />
            <el-option label="Row B" value="Row B" />
            <el-option label="Row C" value="Row C" />
            <el-option label="Row D" value="Row D" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location" required>
          <el-input v-model="rackForm.location" placeholder="e.g., Data Center A" />
        </el-form-item>
        <el-form-item label="Total U Space">
          <el-select v-model="rackForm.totalUSpace" style="width: 100%">
            <el-option label="42U" value="42" />
            <el-option label="45U" value="45" />
            <el-option label="48U" value="48" />
          </el-select>
        </el-form-item>
        <el-form-item label="Power Capacity (kW)">
          <el-input-number v-model="rackForm.powerCapacity" :min="10" :max="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Cooling Type">
          <el-select v-model="rackForm.coolingType" style="width: 100%">
            <el-option label="Cold Aisle Containment" value="Cold Aisle" />
            <el-option label="Hot Aisle Containment" value="Hot Aisle" />
            <el-option label="In-Row Cooling" value="In-Row" />
          </el-select>
        </el-form-item>
        <el-form-item label="PDU Type">
          <el-select v-model="rackForm.pduType" style="width: 100%">
            <el-option label="Dual PDU - 2x30A" value="Dual PDU - 2x30A" />
            <el-option label="Dual PDU - 2x60A" value="Dual PDU - 2x60A" />
            <el-option label="Single PDU - 1x60A" value="Single PDU - 1x60A" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addRackDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRack">Add Rack</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Maintenance Dialog -->
    <el-dialog v-model="scheduleDialogVisible" title="Schedule Rack Maintenance" width="550px">
      <el-form :model="scheduleForm" label-width="130px">
        <el-form-item label="Rack Unit" required>
          <el-input :value="scheduleForm.rackName" disabled />
        </el-form-item>
        <el-form-item label="Maintenance Type" required>
          <el-select v-model="scheduleForm.maintenanceType" placeholder="Select type" style="width: 100%">
            <el-option label="Preventive Maintenance" value="preventive" />
            <el-option label="Corrective Maintenance" value="corrective" />
            <el-option label="Cable Management" value="cable" />
            <el-option label="Cleaning" value="cleaning" />
            <el-option label="Hardware Upgrade" value="upgrade" />
          </el-select>
        </el-form-item>
        <el-form-item label="Schedule Date" required>
          <el-date-picker
              v-model="scheduleForm.scheduleDate"
              type="date"
              placeholder="Select date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Priority">
          <el-select v-model="scheduleForm.priority" placeholder="Select priority" style="width: 100%">
            <el-option label="High - Critical" value="High" />
            <el-option label="Medium - Normal" value="Medium" />
            <el-option label="Low - Routine" value="Low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Assigned Technician">
          <el-select v-model="scheduleForm.technician" placeholder="Select technician" filterable style="width: 100%">
            <el-option label="John Tan - Rack Specialist" value="John Tan" />
            <el-option label="Mike Chen - Hardware Tech" value="Mike Chen" />
            <el-option label="Ahmad Ibrahim - Infrastructure" value="Ahmad Ibrahim" />
            <el-option label="Lim Wei Ming - Field Engineer" value="Lim Wei Ming" />
            <el-option label="Sarah Koh - Data Center Tech" value="Sarah Koh" />
          </el-select>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="scheduleForm.notes" type="textarea" :rows="3" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSchedule">Schedule Maintenance</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Box, Plus, Download, Refresh, CircleCheck, Warning, CircleClose,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading rack maintenance data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading rack data...',
  'Fetching utilization metrics...',
  'Analyzing power distribution...',
  'Loading maintenance schedules...',
  'Almost ready...'
]

// ==================== Types ====================
interface Equipment {
  position: string
  name: string
  type: string
  power: number
  status: string
  lastMaintenance: string
}

interface MaintenanceRecord {
  date: string
  type: string
  description: string
  technician: string
  status: string
}

interface Sensor {
  sensorId: string
  type: string
  value: number
  unit: string
  threshold: string
  status: string
}

interface RackAlert {
  id: number
  date: string
  severity: string
  description: string
  resolved: boolean
}

interface USpaceSlot {
  uPosition: number
  status: 'empty' | 'occupied' | 'warning' | 'critical'
  deviceName?: string
  power?: number
  temp?: number
}

interface RackUnit {
  id: string
  name: string
  row: string
  location: string
  health: number
  totalUSpace: number
  usedUSpace: number
  utilization: number
  power: number
  powerCapacity: number
  temp: number
  coolingType: string
  pduType: string
  networkSwitches: string
  installDate: string
  lastMaintenance: string
  nextMaintenance: string
  uSpaceMap: USpaceSlot[]
  equipment: Equipment[]
  maintenanceHistory: MaintenanceRecord[]
  sensors: Sensor[]
  alerts: RackAlert[]
}

// ==================== Mock Data (40 racks) ====================
const generateRackData = (): RackUnit[] => {
  const rows = ['Row A', 'Row B', 'Row C', 'Row D']
  const locations = ['Data Center A', 'Data Center B', 'Data Center C']
  const coolingTypes = ['Cold Aisle', 'Hot Aisle', 'In-Row']
  const pduTypes = ['Dual PDU - 2x30A', 'Dual PDU - 2x60A', 'Single PDU - 1x60A']

  const racks: RackUnit[] = []

  for (let i = 1; i <= 40; i++) {
    const row = rows[Math.floor(Math.random() * rows.length)]
    const rackNumber = String(i).padStart(2, '0')
    const name = `Rack ${row.charAt(row.length - 1)}-${rackNumber}`

    const totalUSpace = [42, 45, 48][Math.floor(Math.random() * 3)]
    const usedUSpace = Math.floor(Math.random() * totalUSpace)
    const utilization = Math.round((usedUSpace / totalUSpace) * 100)

    const powerCapacity = [20, 30, 40, 60][Math.floor(Math.random() * 4)]
    const power = Math.round(powerCapacity * (0.3 + Math.random() * 0.6))

    const temp = 20 + Math.random() * 8
    const health = Math.max(50, Math.min(100, 100 - (temp - 22) * 8 + (utilization / 100) * 10 + (Math.random() * 10 - 5)))

    // Generate U space map
    const uSpaceMap: USpaceSlot[] = []
    for (let u = 1; u <= totalUSpace; u++) {
      const isOccupied = u <= usedUSpace
      const deviceHealth = isOccupied ? (Math.random() > 0.2 ? 'occupied' : (Math.random() > 0.5 ? 'warning' : 'critical')) : 'empty'
      uSpaceMap.push({
        uPosition: u,
        status: deviceHealth as any,
        deviceName: isOccupied ? `Server ${Math.floor(Math.random() * 100)}` : undefined,
        power: isOccupied ? Math.round(200 + Math.random() * 800) : undefined,
        temp: isOccupied ? 22 + Math.random() * 10 : undefined
      })
    }

    // Generate equipment list
    const equipment: Equipment[] = []
    const deviceTypes = ['Server', 'Storage', 'Network Switch', 'Firewall', 'Load Balancer']
    for (let e = 1; e <= Math.min(usedUSpace, 15); e++) {
      equipment.push({
        position: `${e}U`,
        name: `${deviceTypes[Math.floor(Math.random() * deviceTypes.length)]}-${Math.floor(Math.random() * 100)}`,
        type: deviceTypes[Math.floor(Math.random() * deviceTypes.length)],
        power: Math.round(200 + Math.random() * 800),
        status: Math.random() > 0.8 ? 'Warning' : 'Good',
        lastMaintenance: new Date(Date.now() - Math.random() * 180 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
      })
    }

    // Generate maintenance history
    const maintenanceHistory: MaintenanceRecord[] = []
    const maintenanceDates = [3, 6, 9, 12].map(months => {
      const date = new Date()
      date.setMonth(date.getMonth() - months)
      return date
    })
    maintenanceDates.forEach((date, idx) => {
      maintenanceHistory.push({
        date: date.toISOString().slice(0, 10),
        type: 'Preventive',
        description: `Routine maintenance - cable management and cleaning`,
        technician: ['John Tan', 'Mike Chen', 'Ahmad Ibrahim'][idx % 3],
        status: 'Completed'
      })
    })

    // Generate sensors
    const sensors: Sensor[] = [
      { sensorId: `TEMP-${i}`, type: 'Temperature', value: parseFloat((20 + Math.random() * 8).toFixed(1)), unit: '°C', threshold: '18-27°C', status: temp < 27 ? 'Normal' : (temp < 30 ? 'Warning' : 'Critical') },
      { sensorId: `HUM-${i}`, type: 'Humidity', value: Math.round(40 + Math.random() * 30), unit: '%', threshold: '40-60%', status: Math.random() > 0.8 ? 'Warning' : 'Normal' },
      { sensorId: `PWR-${i}`, type: 'Power Load', value: power, unit: 'kW', threshold: `${powerCapacity} kW`, status: power < powerCapacity * 0.8 ? 'Normal' : (power < powerCapacity * 0.9 ? 'Warning' : 'Critical') }
    ]

    // Generate alerts
    const alerts: RackAlert[] = []
    if (temp > 28) {
      alerts.push({
        id: i * 100 + 1,
        date: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: temp > 30 ? 'High' : 'Medium',
        description: `High inlet temperature detected (${temp.toFixed(1)}°C)`,
        resolved: temp < 27
      })
    }
    if (power > powerCapacity * 0.85) {
      alerts.push({
        id: i * 100 + 2,
        date: new Date(Date.now() - Math.random() * 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: power > powerCapacity * 0.95 ? 'High' : 'Medium',
        description: `Power load approaching capacity (${power}/${powerCapacity} kW)`,
        resolved: false
      })
    }

    racks.push({
      id: `RCK-${String(i).padStart(3, '0')}`,
      name: name,
      row: row,
      location: locations[Math.floor(Math.random() * locations.length)],
      health: Math.round(health),
      totalUSpace: totalUSpace,
      usedUSpace: usedUSpace,
      utilization: utilization,
      power: power,
      powerCapacity: powerCapacity,
      temp: parseFloat(temp.toFixed(1)),
      coolingType: coolingTypes[Math.floor(Math.random() * coolingTypes.length)],
      pduType: pduTypes[Math.floor(Math.random() * pduTypes.length)],
      networkSwitches: `${Math.floor(Math.random() * 4)}x Switches`,
      installDate: new Date(Date.now() - Math.random() * 1095 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      lastMaintenance: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      nextMaintenance: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      uSpaceMap: uSpaceMap,
      equipment: equipment,
      maintenanceHistory: maintenanceHistory,
      sensors: sensors,
      alerts: alerts
    })
  }

  return racks
}

const racks = ref<RackUnit[]>(generateRackData())
const hoveredU = ref<number | null>(null)

// ==================== State ====================
const searchText = ref('')
const rowFilter = ref('')
const statusFilter = ref('')
const coolingTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const scheduleDialogVisible = ref(false)
const addRackDialogVisible = ref(false)
const selectedRack = ref<RackUnit | null>(null)

// Chart refs
let healthChart: echarts.ECharts | null = null
let utilizationChart: echarts.ECharts | null = null
let tempChart: echarts.ECharts | null = null
let powerChart: echarts.ECharts | null = null

const healthChartEl = ref<HTMLElement | null>(null)
const utilizationChartEl = ref<HTMLElement | null>(null)
const tempChartEl = ref<HTMLElement | null>(null)
const powerChartEl = ref<HTMLElement | null>(null)

const rackForm = ref({
  name: '',
  row: '',
  location: '',
  totalUSpace: '42',
  powerCapacity: 30,
  coolingType: 'Cold Aisle',
  pduType: 'Dual PDU - 2x30A'
})

const scheduleForm = ref({
  rackId: '',
  rackName: '',
  maintenanceType: 'preventive',
  scheduleDate: '',
  priority: 'Medium',
  technician: '',
  notes: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalRacks = racks.value.length
  const healthyRacks = racks.value.filter(r => r.health >= 90).length
  const warningRacks = racks.value.filter(r => r.health >= 70 && r.health < 90).length
  const criticalRacks = racks.value.filter(r => r.health < 70).length
  return { totalRacks, healthyRacks, warningRacks, criticalRacks }
})

const metrics = computed(() => {
  const avgPowerDensity = (racks.value.reduce((sum, r) => sum + r.power, 0) / racks.value.length).toFixed(1)
  const avgUtilization = Math.round(racks.value.reduce((sum, r) => sum + r.utilization, 0) / racks.value.length)
  const avgTemp = (racks.value.reduce((sum, r) => sum + r.temp, 0) / racks.value.length).toFixed(1)
  const totalUSpace = racks.value.reduce((sum, r) => sum + r.totalUSpace, 0)
  const usedUSpace = racks.value.reduce((sum, r) => sum + r.usedUSpace, 0)
  const availableUSpace = totalUSpace - usedUSpace

  return {
    avgPowerDensity: parseFloat(avgPowerDensity),
    powerTrend: 5.2,
    avgUtilization,
    utilizationGrowth: 3.8,
    avgTemp: parseFloat(avgTemp),
    tempTrend: -0.3,
    availableUSpace,
    totalUSpace
  }
})

const uniqueRows = computed(() => {
  return [...new Set(racks.value.map(r => r.row))]
})

const filteredRacks = computed(() => {
  let filtered = [...racks.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.id.toLowerCase().includes(search) ||
        r.name.toLowerCase().includes(search) ||
        r.location.toLowerCase().includes(search)
    )
  }

  if (rowFilter.value) {
    filtered = filtered.filter(r => r.row === rowFilter.value)
  }

  if (statusFilter.value) {
    if (statusFilter.value === 'healthy') filtered = filtered.filter(r => r.health >= 90)
    else if (statusFilter.value === 'warning') filtered = filtered.filter(r => r.health >= 70 && r.health < 90)
    else if (statusFilter.value === 'critical') filtered = filtered.filter(r => r.health < 70)
  }

  if (coolingTypeFilter.value) {
    filtered = filtered.filter(r => r.coolingType === coolingTypeFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredRacks.value.length)

const paginatedRacks = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRacks.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getHealthColor = (health: number): string => {
  if (health >= 90) return '#22c55e'
  if (health >= 70) return '#f59e0b'
  return '#ef4444'
}

const getUtilizationColor = (utilization: number): string => {
  if (utilization <= 75) return '#22c55e'
  if (utilization <= 85) return '#f59e0b'
  return '#ef4444'
}

const getPowerClass = (power: number, capacity: number): string => {
  const ratio = power / capacity
  if (ratio <= 0.7) return 'metric-good'
  if (ratio <= 0.85) return 'metric-warning'
  return 'metric-bad'
}

const getTempClass = (temp: number): string => {
  if (temp <= 24) return 'metric-good'
  if (temp <= 27) return 'metric-warning'
  return 'metric-bad'
}

const resetFilters = () => {
  searchText.value = ''
  rowFilter.value = ''
  statusFilter.value = ''
  coolingTypeFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const showUTooltip = (u: USpaceSlot) => {
  hoveredU.value = u.uPosition
}

const hideUTooltip = () => {
  hoveredU.value = null
}

// ==================== Chart Functions ====================
const initHealthChart = () => {
  if (!healthChartEl.value) return
  if (healthChart) {
    healthChart.dispose()
    healthChart = null
  }

  const healthy = racks.value.filter(r => r.health >= 90).length
  const warning = racks.value.filter(r => r.health >= 70 && r.health < 90).length
  const critical = racks.value.filter(r => r.health < 70).length

  healthChart = echarts.init(healthChartEl.value)
  healthChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} racks)' },
    legend: { orient: 'vertical', left: 'left', data: ['Healthy (≥90%)', 'Warning (70-89%)', 'Critical (<70%)'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: healthy, name: 'Healthy (≥90%)', itemStyle: { color: '#22c55e' } },
        { value: warning, name: 'Warning (70-89%)', itemStyle: { color: '#f59e0b' } },
        { value: critical, name: 'Critical (<70%)', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initUtilizationChart = () => {
  if (!utilizationChartEl.value) return
  if (utilizationChart) {
    utilizationChart.dispose()
    utilizationChart = null
  }

  const rows = ['Row A', 'Row B', 'Row C', 'Row D']
  const utilizations = rows.map(row => {
    const rowRacks = racks.value.filter(r => r.row === row)
    if (rowRacks.length === 0) return 0
    return Math.round(rowRacks.reduce((sum, r) => sum + r.utilization, 0) / rowRacks.length)
  })

  utilizationChart = echarts.init(utilizationChartEl.value)
  utilizationChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Avg Utilization: {c}%' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: rows },
    yAxis: { type: 'value', name: 'Utilization (%)', max: 100 },
    series: [{
      type: 'bar',
      data: utilizations,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value <= 75) return '#22c55e'
          if (value <= 85) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initTempChart = () => {
  if (!tempChartEl.value) return
  if (tempChart) {
    tempChart.dispose()
    tempChart = null
  }

  const rows = ['Row A', 'Row B', 'Row C', 'Row D']
  const temps = rows.map(row => {
    const rowRacks = racks.value.filter(r => r.row === row)
    if (rowRacks.length === 0) return 0
    return (rowRacks.reduce((sum, r) => sum + r.temp, 0) / rowRacks.length).toFixed(1)
  })

  tempChart = echarts.init(tempChartEl.value)
  tempChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: rows },
    yAxis: { type: 'value', name: 'Temperature (°C)', min: 20, max: 30 },
    series: [{
      type: 'line',
      data: temps,
      smooth: true,
      lineStyle: { color: '#f59e0b', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#f59e0b' },
      label: { show: true, position: 'top', formatter: '{c}°C' }
    }]
  })
}

const initPowerChart = () => {
  if (!powerChartEl.value) return
  if (powerChart) {
    powerChart.dispose()
    powerChart = null
  }

  const rows = ['Row A', 'Row B', 'Row C', 'Row D']
  const powerData = rows.map(row => {
    const rowRacks = racks.value.filter(r => r.row === row)
    return Math.round(rowRacks.reduce((sum, r) => sum + r.power, 0))
  })

  powerChart = echarts.init(powerChartEl.value)
  powerChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Total Power: {c} kW' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: rows },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [{
      type: 'bar',
      data: powerData,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c} kW' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initHealthChart()
    initUtilizationChart()
    initTempChart()
    initPowerChart()
  })
}

// ==================== Actions ====================
const viewRackDetail = (rack: RackUnit) => {
  selectedRack.value = rack
  detailDialogVisible.value = true
}

const viewHistory = (rack: RackUnit) => {
  viewRackDetail(rack)
}

const scheduleMaintenance = (rack: RackUnit | null) => {
  if (rack) {
    scheduleForm.value = {
      rackId: rack.id,
      rackName: rack.name,
      maintenanceType: rack.health < 70 ? 'corrective' : 'preventive',
      scheduleDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      priority: rack.health < 70 ? 'High' : (rack.health < 85 ? 'Medium' : 'Low'),
      technician: '',
      notes: ''
    }
    scheduleDialogVisible.value = true
  }
}

const saveSchedule = () => {
  if (!scheduleForm.value.scheduleDate) {
    ElMessage.warning('Please select schedule date')
    return
  }

  ElMessage.success(`Maintenance scheduled for ${scheduleForm.value.rackName}`)
  scheduleDialogVisible.value = false
}

const generateRackReport = (rack: RackUnit | null) => {
  if (!rack) return
  ElMessage.success(`Generating report for ${rack.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const viewAllRacks = () => {
  ElMessage.info('Viewing all racks')
}

const exportData = () => {
  ElMessage.success('Exporting rack data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  refreshCharts()
  ElMessage.success('Data refreshed')
}

const openAddRackDialog = () => {
  rackForm.value = {
    name: '',
    row: '',
    location: '',
    totalUSpace: '42',
    powerCapacity: 30,
    coolingType: 'Cold Aisle',
    pduType: 'Dual PDU - 2x30A'
  }
  addRackDialogVisible.value = true
}

const saveRack = () => {
  if (!rackForm.value.name || !rackForm.value.row || !rackForm.value.location) {
    ElMessage.warning('Please fill in required fields')
    return
  }
  ElMessage.success(`Rack ${rackForm.value.name} added successfully`)
  addRackDialogVisible.value = false
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [healthChart, utilizationChart, tempChart, powerChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, rowFilter, statusFilter, coolingTypeFilter], () => {
  currentPage.value = 1
})

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => refreshCharts())
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  const charts = [healthChart, utilizationChart, tempChart, powerChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.rack-maintenance-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* Loading Screen */
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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-title {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.metric-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
}

.metric-trend {
  font-size: 12px;
  margin: 8px 0 4px;
}

.metric-trend.positive { color: #22c55e; }
.metric-trend.negative { color: #ef4444; }

.metric-target {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.metric-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* Charts Row */
.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 280px;
  width: 100%;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Rack Detail */
.rack-detail {
  padding: 8px;
}

.detail-header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.detail-stat {
  text-align: center;
}

.detail-stat-value {
  font-size: 24px;
  font-weight: 700;
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.detail-stat-sub {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 2px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

/* U Space Map */
.u-space-map {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(50px, 70px));
  gap: 4px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.u-unit {
  position: relative;
  background: #e2e8f0;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  text-align: center;
  padding: 8px 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.u-unit:hover {
  transform: scale(1.05);
  z-index: 10;
}

.u-unit.occupied {
  background: #dcfce7;
  border-color: #22c55e;
}

.u-unit.empty {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

.u-unit.warning {
  background: #fef3c7;
  border-color: #f59e0b;
}

.u-unit.critical {
  background: #fee2e2;
  border-color: #ef4444;
}

.u-number {
  font-size: 11px;
  font-weight: 600;
}

.u-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #1e293b;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 11px;
  white-space: nowrap;
  z-index: 100;
  margin-bottom: 8px;
}

.u-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 5px;
  border-style: solid;
  border-color: #1e293b transparent transparent transparent;
}

.tooltip-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.tooltip-info {
  display: flex;
  gap: 12px;
}

.u-legend {
  display: flex;
  gap: 24px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 8px;
  margin-top: 12px;
  font-size: 12px;
}

.legend-box {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 3px;
  margin-right: 6px;
  vertical-align: middle;
}

.legend-box.occupied { background: #dcfce7; border: 1px solid #22c55e; }
.legend-box.empty { background: #f1f5f9; border: 1px solid #cbd5e1; }
.legend-box.warning { background: #fef3c7; border: 1px solid #f59e0b; }
.legend-box.critical { background: #fee2e2; border: 1px solid #ef4444; }

.metric-good { color: #22c55e; font-weight: 600; }
.metric-warning { color: #f59e0b; font-weight: 600; }
.metric-bad { color: #ef4444; font-weight: 600; }

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid, .metrics-row {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select {
    width: 100% !important;
  }
  .u-space-map {
    grid-template-columns: repeat(auto-fill, minmax(45px, 55px));
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>