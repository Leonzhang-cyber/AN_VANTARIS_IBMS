<template>
  <div class="space-capacity-container">
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
            <span class="loading-title">Loading Space Capacity</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Space Capacity Management</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="space-capacity-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Space Capacity</h1>
          <p class="page-subtitle">Manage rack space, U utilization and capacity planning</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="analyzeCapacity">
            <el-icon><Cpu /></el-icon>
            Analyze Capacity
          </el-button>
          <el-button @click="exportFullReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">
            <el-icon><Grid /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-label">Total U Space</span>
            <span class="stat-value">{{ totalUSpace }} <span class="stat-unit">U</span></span>
          </div>
          <div class="stat-progress">
            <el-progress :percentage="spaceUtilization" :stroke-width="6" :color="spaceColor" :show-text="false" />
            <span class="progress-percent">{{ spaceUtilization }}%</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">
            <el-icon><Menu /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-label">Used U Space</span>
            <span class="stat-value">{{ usedUSpace }} <span class="stat-unit">U</span></span>
          </div>
          <div class="stat-progress">
            <el-progress :percentage="utilization" :stroke-width="6" color="#10b981" :show-text="false" />
            <span class="progress-percent">{{ utilization }}%</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">
            <el-icon><View /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-label">Free U Space</span>
            <span class="stat-value">{{ freeUSpace }} <span class="stat-unit">U</span></span>
          </div>
          <div class="stat-progress">
            <el-progress :percentage="freePercentage" :stroke-width="6" color="#f59e0b" :show-text="false" />
            <span class="progress-percent">{{ freePercentage }}%</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon red">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-label">Fragmentation</span>
            <span class="stat-value">{{ fragmentationRate }}<span class="stat-unit">%</span></span>
          </div>
          <div class="stat-progress">
            <el-progress :percentage="fragmentationRate" :stroke-width="6" :color="fragColor" :show-text="false" />
            <span class="progress-percent" :class="{ warning: fragmentationRate > 10 }">{{ fragmentationRate }}%</span>
          </div>
        </div>
      </div>

      <!-- Distribution Cards - 卡片形式展示各行的空间分布 -->
      <div class="distribution-cards">
        <div class="section-header">
          <h3>Space Distribution by Row</h3>
          <el-radio-group v-model="distributionType" size="small">
            <el-radio-button label="utilization">Utilization</el-radio-button>
            <el-radio-button label="free">Free Space</el-radio-button>
            <el-radio-button label="occupied">Occupied</el-radio-button>
          </el-radio-group>
        </div>
        <div class="row-cards-grid">
          <div
              v-for="row in rowData"
              :key="row.row"
              class="row-card"
              :style="{ borderTopColor: getRowColor(row.utilization) }"
          >
            <div class="row-card-header">
              <span class="row-name">Row {{ row.row }}</span>
              <span class="row-value" v-if="distributionType === 'utilization'">
                {{ row.utilization }}%
              </span>
              <span class="row-value" v-else-if="distributionType === 'free'">
                {{ row.freeU }} U
              </span>
              <span class="row-value" v-else>
                {{ row.usedU }} U
              </span>
            </div>
            <div class="row-progress">
              <div
                  class="progress-fill"
                  :style="{
                  width: distributionType === 'utilization' ? `${row.utilization}%` :
                         distributionType === 'free' ? `${(row.freeU / row.totalU) * 100}%` :
                         `${(row.usedU / row.totalU) * 100}%`,
                  backgroundColor: getRowFillColor(row.utilization)
                }"
              ></div>
            </div>
            <div class="row-stats">
              <div class="stat-detail">
                <span class="dot occupied-dot"></span>
                <span>Used: {{ row.usedU }} U</span>
              </div>
              <div class="stat-detail">
                <span class="dot free-dot"></span>
                <span>Free: {{ row.freeU }} U</span>
              </div>
              <div class="stat-detail">
                <span class="dot reserved-dot"></span>
                <span>Reserved: {{ row.reservedU || 0 }} U</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pie Chart Card - 卡片形式展示空间构成 -->
      <div class="pie-card">
        <div class="section-header">
          <h3>Space Breakdown</h3>
        </div>
        <div class="pie-content">
          <div class="pie-segments">
            <div class="pie-segment occupied-segment" :style="{ width: `${utilization}%` }">
              <span class="segment-label" v-if="utilization > 15">占用 {{ utilization }}%</span>
            </div>
            <div class="pie-segment free-segment" :style="{ width: `${freePercentage}%` }">
              <span class="segment-label" v-if="freePercentage > 15">空闲 {{ freePercentage }}%</span>
            </div>
            <div class="pie-segment reserved-segment" :style="{ width: `${reservedPercentage}%` }">
              <span class="segment-label" v-if="reservedPercentage > 15">预留 {{ reservedPercentage }}%</span>
            </div>
          </div>
          <div class="pie-legend">
            <div class="legend-item">
              <span class="legend-dot occupied"></span>
              <span>Occupied</span>
              <strong>{{ usedUSpace }} U ({{ utilization }}%)</strong>
            </div>
            <div class="legend-item">
              <span class="legend-dot free"></span>
              <span>Free</span>
              <strong>{{ freeUSpace }} U ({{ freePercentage }}%)</strong>
            </div>
            <div class="legend-item">
              <span class="legend-dot reserved"></span>
              <span>Reserved</span>
              <strong>{{ reservedUSpace }} U ({{ reservedPercentage }}%)</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Forecast Cards -->
      <div class="forecast-cards">
        <div class="section-header">
          <h3>Capacity Forecast</h3>
          <el-button type="primary" link @click="generateExpansionPlan">Generate Plan →</el-button>
        </div>
        <div class="forecast-grid">
          <div class="forecast-card">
            <div class="forecast-icon">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="forecast-info">
              <span class="forecast-label">Until Space Full</span>
              <span class="forecast-value">{{ monthsUntilFull }} months</span>
              <el-progress :percentage="(monthsUntilFull / 12) * 100" :stroke-width="6" :show-text="false" />
              <span class="forecast-hint">Based on current growth rate</span>
            </div>
          </div>
          <div class="forecast-card">
            <div class="forecast-icon warning">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="forecast-info">
              <span class="forecast-label">Additional Racks Needed</span>
              <span class="forecast-value">{{ racksNeeded }} racks</span>
              <el-progress :percentage="(racksNeeded / 20) * 100" :stroke-width="6" color="#f59e0b" :show-text="false" />
              <span class="forecast-hint">To meet projected demand</span>
            </div>
          </div>
          <div class="forecast-card">
            <div class="forecast-icon success">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="forecast-info">
              <span class="forecast-label">Annual Growth Rate</span>
              <span class="forecast-value">{{ growthRate }}%</span>
              <el-progress :percentage="growthRate" :stroke-width="6" color="#10b981" :show-text="false" />
              <span class="forecast-hint">Past 12 months average</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Rack Visualization -->
      <div class="rack-viz-card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><Grid /></el-icon>
            <span>Rack View - Row {{ selectedRow }}</span>
          </div>
          <div class="card-controls">
            <el-select v-model="selectedRow" size="small" style="width: 100px">
              <el-option label="Row A" value="A" />
              <el-option label="Row B" value="B" />
              <el-option label="Row C" value="C" />
              <el-option label="Row D" value="D" />
              <el-option label="Row E" value="E" />
            </el-select>
            <el-button-group>
              <el-button size="small" @click="prevRow" :disabled="selectedRow === 'A'">
                <el-icon><ArrowLeft /></el-icon>
              </el-button>
              <el-button size="small" @click="nextRow" :disabled="selectedRow === 'E'">
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>
        <div class="rack-viz-content">
          <div class="rack-grid">
            <div
                v-for="rack in currentRowRacks"
                :key="rack.id"
                class="rack-card"
                :class="{ active: selectedRack?.id === rack.id }"
                @click="selectRack(rack)"
            >
              <div class="rack-card-header">
                <span class="rack-name">{{ rack.name }}</span>
                <div class="rack-badge" :class="getBadgeClass(rack)">
                  {{ rack.utilization }}%
                </div>
              </div>
              <div class="rack-u-viz">
                <div
                    v-for="u in 42"
                    :key="u"
                    class="u-block"
                    :class="{
                    occupied: isUOccupied(rack, u),
                    free: !isUOccupied(rack, u) && !isUReserved(rack, u),
                    reserved: isUReserved(rack, u)
                  }"
                    :style="{ height: '7px' }"
                    :title="`U${u}: ${getUStatusText(rack, u)}`"
                ></div>
              </div>
              <div class="rack-card-footer">
                <span>{{ rack.usedU }}/{{ rack.totalU }} U</span>
                <span>{{ rack.utilization }}% used</span>
              </div>
            </div>
          </div>
        </div>
        <div class="viz-legend">
          <div class="legend-item">
            <span class="legend-dot occupied"></span>
            <span>Occupied</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot free"></span>
            <span>Free</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot reserved"></span>
            <span>Reserved</span>
          </div>
        </div>
      </div>

      <!-- Tabs Section -->
      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="Rack Details" name="details">
          <div class="table-wrapper">
            <div class="table-header">
              <h3>Rack Space Details</h3>
              <el-input v-model="searchQuery" placeholder="Search rack..." prefix-icon="Search" style="width: 240px" clearable />
            </div>
            <el-table :data="filteredRacksList" stripe class="modern-table">
              <el-table-column prop="name" label="Rack" width="80" />
              <el-table-column prop="row" label="Row" width="70" />
              <el-table-column label="Space Utilization" min-width="200">
                <template #default="{ row }">
                  <div class="table-progress">
                    <el-progress :percentage="row.utilization" :stroke-width="8" :color="getUtilColor(row.utilization / 100)" />
                    <span class="progress-value">{{ row.usedU }}/{{ row.totalU }} U</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="usedU" label="Used" width="80" />
              <el-table-column prop="freeU" label="Free" width="80" />
              <el-table-column prop="deviceCount" label="Devices" width="90" />
              <el-table-column label="Status" width="100">
                <template #default="{ row }">
                  <div class="status-badge" :class="getStatusClass(row)">
                    {{ getStatusText(row) }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Action" width="100" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="viewRackDetail(row)">View</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Fragmentation Analysis" name="fragmentation">
          <div class="table-wrapper">
            <h3>Rack Fragmentation Details</h3>
            <el-table :data="fragmentationData" stripe class="modern-table">
              <el-table-column prop="rack" label="Rack" width="100" />
              <el-table-column label="Fragmentation" min-width="200">
                <template #default="{ row }">
                  <el-progress :percentage="row.fragmentation" :stroke-width="8" :color="getFragColor(row.fragmentation)" />
                </template>
              </el-table-column>
              <el-table-column prop="freeBlocks" label="Free Blocks" width="120" />
              <el-table-column prop="largestBlock" label="Largest Block" width="140" />
              <el-table-column prop="recommendation" label="Recommendation" />
              <el-table-column label="Action" width="100">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click="runDefragmentation">Fix</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Placement Suggestions" name="placement">
          <div class="placement-content">
            <div class="table-wrapper">
              <el-table :data="placementSuggestions" stripe class="modern-table">
                <el-table-column prop="device" label="Device" min-width="200" />
                <el-table-column prop="size" label="Size" width="80" />
                <el-table-column prop="suggestedRack" label="Suggested Rack" width="140" />
                <el-table-column prop="suggestedU" label="Suggested U" width="120" />
                <el-table-column prop="reason" label="Reason" />
                <el-table-column label="Action" width="100">
                  <template #default="{ row }">
                    <el-button type="primary" size="small" @click="placeDevice(row)">Place</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="placement-rules">
              <h4>Placement Rules</h4>
              <ul>
                <li>Largest devices first (bin packing)</li>
                <li>Keep similar devices together</li>
                <li>Maintain 1U gap for cooling</li>
                <li>High density devices at bottom</li>
                <li>Network devices at top</li>
              </ul>
              <el-button type="primary" @click="autoPlaceDevices">Auto-Place Devices</el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Rack Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Rack ${selectedRack?.name} Details`" width="600px" class="modern-dialog">
      <div class="dialog-content">
        <div class="dialog-info">
          <div class="info-row">
            <span class="info-label">Location</span>
            <span class="info-value">Row {{ selectedRack?.row }}, Position {{ selectedRack?.position }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Total U Space</span>
            <span class="info-value">{{ selectedRack?.totalU }} U</span>
          </div>
          <div class="info-row">
            <span class="info-label">Used / Free</span>
            <span class="info-value">{{ selectedRack?.usedU }} / {{ selectedRack?.freeU }} U</span>
          </div>
          <div class="info-row">
            <span class="info-label">Utilization</span>
            <div class="info-progress">
              <el-progress :percentage="selectedRack?.utilization" :stroke-width="8" :color="getUtilColor(selectedRack?.utilization / 100)" />
            </div>
          </div>
          <div class="info-row">
            <span class="info-label">Devices</span>
            <span class="info-value">{{ selectedRack?.deviceCount }}</span>
          </div>
        </div>
        <div class="dialog-u-layout">
          <h4>U Space Layout</h4>
          <div class="u-layout-grid">
            <div v-for="u in 42" :key="u" class="u-layout-block"
                 :class="{ occupied: isUOccupied(selectedRack, u), reserved: isUReserved(selectedRack, u) }">
              <span class="u-number">{{ u }}</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editRackSpace">Edit Space</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Grid, Menu, View, Clock, Cpu, Download,
  ArrowLeft, ArrowRight, Search, WarningFilled, TrendCharts
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading space capacity data...')

// ==================== Reactive Data ====================
const activeTab = ref('details')
const distributionType = ref('utilization')
const selectedRow = ref('A')
const searchQuery = ref('')
const selectedRack = ref<any>(null)
const detailDialogVisible = ref(false)

// Space metrics
const totalRacks = ref(60)
const totalUSpace = ref(2520)
const usedUSpace = ref(1680)
const freeUSpace = ref(720)
const reservedUSpace = ref(120)
const utilization = computed(() => Math.round((usedUSpace.value / totalUSpace.value) * 100))
const freePercentage = computed(() => Math.round((freeUSpace.value / totalUSpace.value) * 100))
const reservedPercentage = computed(() => Math.round((reservedUSpace.value / totalUSpace.value) * 100))
const spaceUtilization = computed(() => utilization.value)
const fragmentationRate = ref(15)
const monthsUntilFull = ref(6)
const racksNeeded = ref(8)
const growthRate = ref(8.5)

// Colors
const spaceColor = computed(() => {
  if (spaceUtilization.value < 70) return '#10b981'
  if (spaceUtilization.value < 85) return '#f59e0b'
  return '#ef4444'
})

const fragColor = computed(() => {
  if (fragmentationRate.value < 10) return '#10b981'
  if (fragmentationRate.value < 20) return '#f59e0b'
  return '#ef4444'
})

// Helper functions
const isUOccupied = (rack: any, u: number) => {
  if (!rack || !rack.occupiedU) return false
  return rack.occupiedU.includes(u)
}

const isUReserved = (rack: any, u: number) => {
  if (!rack || !rack.reservedUList) return false
  return rack.reservedUList.includes(u)
}

const getUStatusText = (rack: any, u: number) => {
  if (isUOccupied(rack, u)) return 'Occupied'
  if (isUReserved(rack, u)) return 'Reserved'
  return 'Available'
}

const getBadgeClass = (rack: any) => {
  if (rack.utilization >= 95) return 'danger'
  if (rack.utilization >= 85) return 'warning'
  return 'success'
}

const getStatusClass = (rack: any) => {
  if (rack.status === 'Critical') return 'critical'
  if (rack.status === 'Warning') return 'warning'
  return 'normal'
}

const getStatusText = (rack: any) => {
  if (rack.status === 'Critical') return 'Critical'
  if (rack.status === 'Warning') return 'Warning'
  return 'Normal'
}

const getUtilColor = (ratio: number) => {
  if (ratio < 0.7) return '#10b981'
  if (ratio < 0.85) return '#f59e0b'
  return '#ef4444'
}

const getFragColor = (frag: number) => {
  if (frag < 10) return '#10b981'
  if (frag < 20) return '#f59e0b'
  return '#ef4444'
}

const getRowColor = (util: number) => {
  if (util < 70) return '#10b981'
  if (util < 85) return '#f59e0b'
  return '#ef4444'
}

const getRowFillColor = (util: number) => {
  if (util < 70) return '#10b981'
  if (util < 85) return '#f59e0b'
  return '#ef4444'
}

// Rack data
const racks = ref([
  { id: 1, name: 'A01', row: 'A', position: 1, totalU: 42, usedU: 38, freeU: 4, reservedU: 0, occupiedU: Array.from({ length: 38 }, (_, i) => i + 1), reservedUList: [], utilization: 90, deviceCount: 12, status: 'Normal' },
  { id: 2, name: 'A02', row: 'A', position: 2, totalU: 42, usedU: 35, freeU: 7, reservedU: 0, occupiedU: Array.from({ length: 35 }, (_, i) => i + 1), reservedUList: [], utilization: 83, deviceCount: 11, status: 'Normal' },
  { id: 3, name: 'A03', row: 'A', position: 3, totalU: 42, usedU: 40, freeU: 2, reservedU: 0, occupiedU: Array.from({ length: 40 }, (_, i) => i + 1), reservedUList: [], utilization: 95, deviceCount: 14, status: 'Warning' },
  { id: 4, name: 'A04', row: 'A', position: 4, totalU: 42, usedU: 28, freeU: 11, reservedU: 3, occupiedU: Array.from({ length: 28 }, (_, i) => i + 1), reservedUList: [29, 30, 31], utilization: 67, deviceCount: 9, status: 'Normal' },
  { id: 5, name: 'A05', row: 'A', position: 5, totalU: 42, usedU: 42, freeU: 0, reservedU: 0, occupiedU: Array.from({ length: 42 }, (_, i) => i + 1), reservedUList: [], utilization: 100, deviceCount: 16, status: 'Critical' },
  { id: 6, name: 'B01', row: 'B', position: 1, totalU: 42, usedU: 36, freeU: 6, reservedU: 0, occupiedU: Array.from({ length: 36 }, (_, i) => i + 1), reservedUList: [], utilization: 86, deviceCount: 12, status: 'Normal' },
  { id: 7, name: 'B02', row: 'B', position: 2, totalU: 42, usedU: 32, freeU: 10, reservedU: 0, occupiedU: Array.from({ length: 32 }, (_, i) => i + 1), reservedUList: [], utilization: 76, deviceCount: 10, status: 'Normal' },
  { id: 8, name: 'B03', row: 'B', position: 3, totalU: 42, usedU: 38, freeU: 4, reservedU: 0, occupiedU: Array.from({ length: 38 }, (_, i) => i + 1), reservedUList: [], utilization: 90, deviceCount: 13, status: 'Normal' },
  { id: 9, name: 'B04', row: 'B', position: 4, totalU: 42, usedU: 30, freeU: 9, reservedU: 3, occupiedU: Array.from({ length: 30 }, (_, i) => i + 1), reservedUList: [31, 32, 33], utilization: 71, deviceCount: 9, status: 'Normal' },
  { id: 10, name: 'B05', row: 'B', position: 5, totalU: 42, usedU: 35, freeU: 7, reservedU: 0, occupiedU: Array.from({ length: 35 }, (_, i) => i + 1), reservedUList: [], utilization: 83, deviceCount: 11, status: 'Normal' }
])

// Computed
const currentRowRacks = computed(() => racks.value.filter(r => r.row === selectedRow.value))
const filteredRacksList = computed(() => {
  if (!searchQuery.value) return racks.value
  return racks.value.filter(r => r.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

// Row data for distribution (添加 reservedU 字段避免 NaN)
const rowData = computed(() => {
  const rows = ['A', 'B', 'C', 'D', 'E']
  return rows.map(row => {
    const rowRacks = racks.value.filter(r => r.row === row)
    const totalU = rowRacks.reduce((sum, r) => sum + r.totalU, 0)
    const usedU = rowRacks.reduce((sum, r) => sum + r.usedU, 0)
    const freeU = rowRacks.reduce((sum, r) => sum + r.freeU, 0)
    const reservedU = rowRacks.reduce((sum, r) => sum + (r.reservedU || 0), 0)
    return { row, totalU, usedU, freeU, reservedU, utilization: Math.round((usedU / totalU) * 100) }
  })
})

// Static data
const fragmentationData = ref([
  { rack: 'A02', fragmentation: 12, freeBlocks: 4, largestBlock: '3U', recommendation: 'Consolidate small devices' },
  { rack: 'A04', fragmentation: 18, freeBlocks: 5, largestBlock: '4U', recommendation: 'Rearrange for contiguous space' },
  { rack: 'B02', fragmentation: 15, freeBlocks: 4, largestBlock: '4U', recommendation: 'Move devices to fill gaps' },
  { rack: 'B04', fragmentation: 20, freeBlocks: 6, largestBlock: '3U', recommendation: 'High fragmentation - reorganize' }
])

const placementSuggestions = ref([
  { device: 'New Server - Web Tier', size: 2, suggestedRack: 'A02', suggestedU: '15-16', reason: 'Contiguous free space' },
  { device: 'Storage Array', size: 4, suggestedRack: 'A04', suggestedU: '29-32', reason: 'Reserved space available' },
  { device: 'Network Switch', size: 1, suggestedRack: 'B02', suggestedU: '33', reason: 'Top of rack placement' },
  { device: 'Database Server', size: 2, suggestedRack: 'B04', suggestedU: '34-35', reason: 'Adjacent to similar devices' }
])

// Navigation
const prevRow = () => {
  const rows = ['A', 'B', 'C', 'D', 'E']
  const idx = rows.indexOf(selectedRow.value)
  if (idx > 0) selectedRow.value = rows[idx - 1]
}

const nextRow = () => {
  const rows = ['A', 'B', 'C', 'D', 'E']
  const idx = rows.indexOf(selectedRow.value)
  if (idx < rows.length - 1) selectedRow.value = rows[idx + 1]
}

// Actions
const selectRack = (rack: any) => {
  selectedRack.value = rack
}

const viewRackDetail = (rack: any) => {
  selectedRack.value = rack
  detailDialogVisible.value = true
}

const editRackSpace = () => {
  ElMessage.info(`Editing space allocation for ${selectedRack.value.name}`)
  detailDialogVisible.value = false
}

const exportFullReport = () => {
  ElMessage.success('Full space report export started')
}

const analyzeCapacity = () => {
  ElMessage.success('Capacity analysis started')
}

const generateExpansionPlan = () => {
  ElMessage.success('Expansion plan generated')
}

const runDefragmentation = () => {
  ElMessage.success('Defragmentation plan generated')
}

const placeDevice = (suggestion: any) => {
  ElMessage.success(`Device placed in ${suggestion.suggestedRack} at U${suggestion.suggestedU}`)
}

const autoPlaceDevices = () => {
  ElMessage.success('Auto-placement completed. 4 devices placed.')
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

// Lifecycle
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
.space-capacity-container {
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
.space-capacity-main {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.stat-icon.blue { background: #eff6ff; color: #3b82f6; }
.stat-icon.green { background: #ecfdf5; color: #10b981; }
.stat-icon.orange { background: #fffbeb; color: #f59e0b; }
.stat-icon.red { background: #fef2f2; color: #ef4444; }

.stat-icon .el-icon { font-size: 24px; }

.stat-info {
  margin-bottom: 12px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  display: block;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-unit {
  font-size: 14px;
  font-weight: 400;
  color: #94a3b8;
}

.stat-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-progress .el-progress {
  flex: 1;
}

.progress-percent {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  min-width: 40px;
}

.progress-percent.warning {
  color: #ef4444;
}

/* Distribution Cards */
.distribution-cards {
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
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.row-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.row-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  border-top: 3px solid;
  transition: all 0.2s ease;
}

.row-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.row-card-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 12px;
}

.row-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.row-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.row-progress {
  background: #e2e8f0;
  border-radius: 8px;
  height: 12px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  border-radius: 8px;
  transition: width 0.3s ease;
}

.row-stats {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
}

.stat-detail {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.occupied-dot { background: #3b82f6; }
.free-dot { background: #10b981; }
.reserved-dot { background: #f59e0b; }

/* Pie Card */
.pie-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.pie-content {
  max-width: 500px;
  margin: 0 auto;
}

.pie-segments {
  display: flex;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 20px;
}

.pie-segment {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: width 0.3s ease;
}

.pie-segment.occupied-segment {
  background: #3b82f6;
}

.pie-segment.free-segment {
  background: #10b981;
}

.pie-segment.reserved-segment {
  background: #f59e0b;
}

.segment-label {
  color: white;
  font-size: 12px;
  font-weight: 500;
}

.pie-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
}

.pie-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
}

.pie-legend .legend-item strong {
  color: #1e293b;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 4px;
}

.legend-dot.occupied { background: #3b82f6; }
.legend-dot.free { background: #10b981; }
.legend-dot.reserved { background: #f59e0b; }

/* Forecast Cards */
.forecast-cards {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.forecast-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.forecast-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
  transition: all 0.2s ease;
}

.forecast-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.forecast-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #eff6ff;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.forecast-icon.warning {
  background: #fffbeb;
  color: #f59e0b;
}

.forecast-icon.success {
  background: #ecfdf5;
  color: #10b981;
}

.forecast-info {
  flex: 1;
}

.forecast-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.forecast-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.forecast-hint {
  display: block;
  font-size: 10px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Rack Visualization */
.rack-viz-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
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

.card-controls {
  display: flex;
  gap: 12px;
}

.rack-grid {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.rack-card {
  min-width: 140px;
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
}

.rack-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.rack-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.rack-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rack-name {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.rack-badge {
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.rack-badge.success { background: #d1fae5; color: #059669; }
.rack-badge.warning { background: #fed7aa; color: #ea580c; }
.rack-badge.danger { background: #fee2e2; color: #dc2626; }

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

.u-block.occupied { background: #3b82f6; }
.u-block.free { background: #10b981; }
.u-block.reserved { background: #f59e0b; }

.rack-card-footer {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #64748b;
  margin-top: 8px;
}

.viz-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.viz-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #64748b;
}

/* Custom Tabs */
.custom-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
  background: transparent;
}

.custom-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.custom-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  padding: 0 20px;
}

.custom-tabs :deep(.el-tabs__item.is-active) {
  color: #3b82f6;
}

.custom-tabs :deep(.el-tabs__active-bar) {
  background: #3b82f6;
  height: 3px;
}

/* Table Styles */
.table-wrapper {
  background: white;
  border-radius: 16px;
  padding: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.modern-table :deep(.el-table__header th) {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
  font-size: 13px;
}

.modern-table :deep(.el-table__row:hover) {
  background: #f1f5f9;
}

.table-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.table-progress .el-progress {
  flex: 1;
}

.progress-value {
  font-size: 12px;
  color: #64748b;
  min-width: 60px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.normal {
  background: #d1fae5;
  color: #059669;
}

.status-badge.warning {
  background: #fed7aa;
  color: #ea580c;
}

.status-badge.critical {
  background: #fee2e2;
  color: #dc2626;
}

/* Placement Content */
.placement-content {
  background: white;
  border-radius: 16px;
  overflow: hidden;
}

.placement-rules {
  padding: 20px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.placement-rules h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.placement-rules ul {
  margin: 0 0 16px 0;
  padding-left: 20px;
}

.placement-rules li {
  font-size: 13px;
  color: #64748b;
  margin: 6px 0;
}

/* Dialog */
.modern-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #e2e8f0;
  padding: 20px 24px;
  margin: 0;
}

.modern-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.modern-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.dialog-content {
  display: flex;
  gap: 24px;
}

.dialog-info {
  flex: 1;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #e2e8f0;
}

.info-label {
  font-size: 13px;
  color: #64748b;
}

.info-value {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.info-progress {
  width: 150px;
}

.dialog-u-layout {
  flex: 1;
}

.dialog-u-layout h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.u-layout-grid {
  display: grid;
  grid-template-columns: repeat(14, 1fr);
  gap: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.u-layout-block {
  aspect-ratio: 1;
  background: #e2e8f0;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: #64748b;
}

.u-layout-block.occupied {
  background: #3b82f6;
  color: white;
}

.u-layout-block.reserved {
  background: #f59e0b;
  color: white;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .forecast-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .space-capacity-main { padding: 16px; }
  .stats-grid { grid-template-columns: 1fr; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .rack-grid { flex-wrap: wrap; }
  .dialog-content { flex-direction: column; }
  .pie-legend { flex-direction: column; align-items: center; }
}
</style>