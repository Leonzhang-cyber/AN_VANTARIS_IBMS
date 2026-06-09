<template>
  <div class="rack-utilization-container">
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
            <span class="loading-title">Loading Rack Utilization</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Rack Utilization Analysis</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="rack-utilization-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Rack Utilization</h1>
          <p class="page-subtitle">Monitor and analyze rack space, power and cooling utilization</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon blue">
                <el-icon><Grid /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Avg Space Utilization</span>
                <span class="card-value" :style="{ color: avgSpaceColor }">{{ avgSpaceUtilization }}%</span>
                <el-progress :percentage="avgSpaceUtilization" :stroke-width="6" :color="avgSpaceColor" :show-text="false" />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon green">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Avg Power Utilization</span>
                <span class="card-value" :style="{ color: avgPowerColor }">{{ avgPowerUtilization }}%</span>
                <el-progress :percentage="avgPowerUtilization" :stroke-width="6" color="#10b981" :show-text="false" />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon orange">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Avg Cooling Utilization</span>
                <span class="card-value" :style="{ color: avgCoolingColor }">{{ avgCoolingUtilization }}%</span>
                <el-progress :percentage="avgCoolingUtilization" :stroke-width="6" color="#f59e0b" :show-text="false" />
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon purple">
                <el-icon><Monitor /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Racks Monitored</span>
                <span class="card-value">{{ racks.length }}</span>
                <el-progress :percentage="100" :stroke-width="6" color="#8b5cf6" :show-text="false" />
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Utilization Heatmap -->
      <div class="heatmap-section">
        <el-card class="heatmap-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Grid /></el-icon>
              <span>Rack Utilization Heatmap</span>
            </div>
            <el-radio-group v-model="heatmapType" size="small">
              <el-radio-button label="space">Space</el-radio-button>
              <el-radio-button label="power">Power</el-radio-button>
              <el-radio-button label="cooling">Cooling</el-radio-button>
            </el-radio-group>
          </div>
          <div class="heatmap-container">
            <div class="heatmap-grid">
              <div class="heatmap-header">
                <div class="corner"></div>
                <div v-for="pos in 5" :key="pos" class="position-label">Pos {{ pos }}</div>
              </div>
              <div v-for="row in rows" :key="row" class="heatmap-row">
                <div class="row-label">Row {{ row }}</div>
                <div
                    v-for="pos in 5"
                    :key="pos"
                    class="heatmap-cell"
                    :style="{ backgroundColor: getCellColor(row, pos) }"
                    @click="showRackDetail(row, pos)"
                >
                  <div class="cell-value">{{ getCellValue(row, pos) }}%</div>
                  <div class="cell-label">{{ getRackName(row, pos) }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="heatmap-legend">
            <div class="legend-title">Utilization Scale:</div>
            <div class="legend-color" style="background: #10b981"></div>
            <span>0-30%</span>
            <div class="legend-color" style="background: #84cc16"></div>
            <span>30-50%</span>
            <div class="legend-color" style="background: #f59e0b"></div>
            <span>50-70%</span>
            <div class="legend-color" style="background: #ef4444"></div>
            <span>70-85%</span>
            <div class="legend-color" style="background: #7c2d12"></div>
            <span>85-100%</span>
          </div>
        </el-card>
      </div>

      <!-- Utilization Rankings -->
      <div class="rankings-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="ranking-card" shadow="hover">
              <div class="ranking-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Highest Space Utilization</span>
              </div>
              <div class="ranking-list">
                <div v-for="(rack, index) in highestSpaceUtilization" :key="rack.id" class="ranking-item">
                  <div class="rank">{{ index + 1 }}</div>
                  <div class="rank-name">{{ rack.name }}</div>
                  <div class="rank-value" :style="{ color: getUtilColor(rack.spaceUtil) }">{{ rack.spaceUtil }}%</div>
                  <div class="rank-bar">
                    <div class="bar-fill" :style="{ width: rack.spaceUtil + '%', backgroundColor: getUtilColor(rack.spaceUtil) }"></div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="ranking-card" shadow="hover">
              <div class="ranking-header">
                <el-icon><Cpu /></el-icon>
                <span>Highest Power Utilization</span>
              </div>
              <div class="ranking-list">
                <div v-for="(rack, index) in highestPowerUtilization" :key="rack.id" class="ranking-item">
                  <div class="rank">{{ index + 1 }}</div>
                  <div class="rank-name">{{ rack.name }}</div>
                  <div class="rank-value" :style="{ color: getPowerColor(rack.powerUtil) }">{{ rack.powerUtil }}%</div>
                  <div class="rank-bar">
                    <div class="bar-fill" :style="{ width: rack.powerUtil + '%', backgroundColor: getPowerColor(rack.powerUtil) }"></div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="ranking-card" shadow="hover">
              <div class="ranking-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Highest Cooling Utilization</span>
              </div>
              <div class="ranking-list">
                <div v-for="(rack, index) in highestCoolingUtilization" :key="rack.id" class="ranking-item">
                  <div class="rank">{{ index + 1 }}</div>
                  <div class="rank-name">{{ rack.name }}</div>
                  <div class="rank-value" :style="{ color: getCoolingColor(rack.coolingUtil) }">{{ rack.coolingUtil }}%</div>
                  <div class="rank-bar">
                    <div class="bar-fill" :style="{ width: rack.coolingUtil + '%', backgroundColor: getCoolingColor(rack.coolingUtil) }"></div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Detailed Table -->
      <div class="table-section">
        <div class="section-header">
          <h3>Rack Utilization Details</h3>
          <div class="header-controls">
            <el-input v-model="searchQuery" placeholder="Search rack..." prefix-icon="Search" style="width: 200px" clearable />
            <el-select v-model="filterRow" placeholder="Filter by Row" clearable style="width: 120px">
              <el-option label="Row A" value="A" />
              <el-option label="Row B" value="B" />
              <el-option label="Row C" value="C" />
              <el-option label="Row D" value="D" />
            </el-select>
            <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 120px">
              <el-option label="Normal" value="Normal" />
              <el-option label="Warning" value="Warning" />
              <el-option label="Critical" value="Critical" />
            </el-select>
          </div>
        </div>
        <el-table :data="filteredRacks" stripe class="utilization-table">
          <el-table-column prop="name" label="Rack" width="80" />
          <el-table-column prop="row" label="Row" width="70" />
          <el-table-column label="Space Utilization" min-width="180">
            <template #default="{ row }">
              <div class="table-progress">
                <el-progress :percentage="row.spaceUtil" :stroke-width="10" :color="getUtilColor(row.spaceUtil)" />
                <span class="progress-value">{{ row.usedU }}/{{ row.totalU }} U</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Power Utilization" min-width="180">
            <template #default="{ row }">
              <div class="table-progress">
                <el-progress :percentage="row.powerUtil" :stroke-width="10" :color="getPowerColor(row.powerUtil)" />
                <span class="progress-value">{{ row.power }}/{{ row.maxPower }} kW</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Cooling Utilization" min-width="180">
            <template #default="{ row }">
              <div class="table-progress">
                <el-progress :percentage="row.coolingUtil" :stroke-width="10" :color="getCoolingColor(row.coolingUtil)" />
                <span class="progress-value">{{ row.heatLoad }}/{{ row.maxCooling }} kW</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Status" width="100">
            <template #default="{ row }">
              <div class="status-badge" :class="getStatusClass(row)">
                {{ row.status }}
              </div>
            </template>
          </el-table-column>
          <el-table-column label="Trend" width="100">
            <template #default="{ row }">
              <el-tag :type="row.trend === 'up' ? 'danger' : row.trend === 'down' ? 'success' : 'info'" size="small">
                {{ row.trend === 'up' ? '↑ Increasing' : row.trend === 'down' ? '↓ Decreasing' : '→ Stable' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Utilization Trends Chart -->
      <div class="trends-section">
        <el-card class="trends-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              <span>Utilization Trends (Last 12 Months)</span>
            </div>
            <el-select v-model="trendRack" placeholder="Select Rack" style="width: 150px" @change="refreshTrendChart">
              <el-option v-for="rack in racks" :key="rack.id" :label="rack.name" :value="rack.id" />
            </el-select>
          </div>
          <div class="trends-chart-container">
            <canvas id="trendChart"></canvas>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Rack Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`${selectedRack?.name} - Utilization Details`" width="700px" class="detail-dialog">
      <div class="detail-content">
        <div class="detail-section">
          <h4>Space Utilization</h4>
          <div class="detail-progress">
            <el-progress :percentage="selectedRack?.spaceUtil" :stroke-width="12" :color="getUtilColor(selectedRack?.spaceUtil)" />
            <div class="detail-stats">
              <span>Used: {{ selectedRack?.usedU }} U</span>
              <span>Free: {{ selectedRack?.totalU - selectedRack?.usedU }} U</span>
              <span>Total: {{ selectedRack?.totalU }} U</span>
            </div>
          </div>
        </div>
        <div class="detail-section">
          <h4>Power Utilization</h4>
          <div class="detail-progress">
            <el-progress :percentage="selectedRack?.powerUtil" :stroke-width="12" :color="getPowerColor(selectedRack?.powerUtil)" />
            <div class="detail-stats">
              <span>Current: {{ selectedRack?.power }} kW</span>
              <span>Available: {{ (selectedRack?.maxPower - selectedRack?.power).toFixed(1) }} kW</span>
              <span>Capacity: {{ selectedRack?.maxPower }} kW</span>
            </div>
          </div>
        </div>
        <div class="detail-section">
          <h4>Cooling Utilization</h4>
          <div class="detail-progress">
            <el-progress :percentage="selectedRack?.coolingUtil" :stroke-width="12" :color="getCoolingColor(selectedRack?.coolingUtil)" />
            <div class="detail-stats">
              <span>Heat Load: {{ selectedRack?.heatLoad }} kW</span>
              <span>Available: {{ (selectedRack?.maxCooling - selectedRack?.heatLoad).toFixed(1) }} kW</span>
              <span>Capacity: {{ selectedRack?.maxCooling }} kW</span>
            </div>
          </div>
        </div>
        <div class="detail-section">
          <h4>Recommendations</h4>
          <ul class="recommendations-list">
            <li v-for="rec in getRecommendations(selectedRack)" :key="rec">{{ rec }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="optimizeRack(selectedRack)">Optimize</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { Grid, Cpu, Monitor, Refresh, Download, TrendCharts, Search } from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading rack utilization data...')

// ==================== Reactive Data ====================
const heatmapType = ref('space')
const searchQuery = ref('')
const filterRow = ref('')
const filterStatus = ref('')
const trendRack = ref(1)
const detailDialogVisible = ref(false)
const selectedRack = ref<any>(null)

// Rack data
const racks = ref([
  { id: 1, name: 'A01', row: 'A', totalU: 42, usedU: 38, spaceUtil: 90, power: 8.5, maxPower: 15, powerUtil: 57, heatLoad: 8.2, maxCooling: 15, coolingUtil: 55, status: 'Normal', trend: 'stable' },
  { id: 2, name: 'A02', row: 'A', totalU: 42, usedU: 35, spaceUtil: 83, power: 7.8, maxPower: 15, powerUtil: 52, heatLoad: 7.5, maxCooling: 15, coolingUtil: 50, status: 'Normal', trend: 'up' },
  { id: 3, name: 'A03', row: 'A', totalU: 42, usedU: 40, spaceUtil: 95, power: 12.5, maxPower: 15, powerUtil: 83, heatLoad: 12.0, maxCooling: 15, coolingUtil: 80, status: 'Warning', trend: 'up' },
  { id: 4, name: 'A04', row: 'A', totalU: 42, usedU: 28, spaceUtil: 67, power: 6.2, maxPower: 15, powerUtil: 41, heatLoad: 5.8, maxCooling: 15, coolingUtil: 39, status: 'Normal', trend: 'stable' },
  { id: 5, name: 'A05', row: 'A', totalU: 42, usedU: 42, spaceUtil: 100, power: 14.2, maxPower: 15, powerUtil: 95, heatLoad: 13.8, maxCooling: 15, coolingUtil: 92, status: 'Critical', trend: 'up' },
  { id: 6, name: 'B01', row: 'B', totalU: 42, usedU: 36, spaceUtil: 86, power: 8.2, maxPower: 15, powerUtil: 55, heatLoad: 7.8, maxCooling: 15, coolingUtil: 52, status: 'Normal', trend: 'stable' },
  { id: 7, name: 'B02', row: 'B', totalU: 42, usedU: 32, spaceUtil: 76, power: 7.2, maxPower: 15, powerUtil: 48, heatLoad: 6.8, maxCooling: 15, coolingUtil: 45, status: 'Normal', trend: 'down' },
  { id: 8, name: 'B03', row: 'B', totalU: 42, usedU: 38, spaceUtil: 90, power: 9.5, maxPower: 15, powerUtil: 63, heatLoad: 9.0, maxCooling: 15, coolingUtil: 60, status: 'Normal', trend: 'stable' },
  { id: 9, name: 'B04', row: 'B', totalU: 42, usedU: 30, spaceUtil: 71, power: 6.8, maxPower: 15, powerUtil: 45, heatLoad: 6.5, maxCooling: 15, coolingUtil: 43, status: 'Normal', trend: 'down' },
  { id: 10, name: 'B05', row: 'B', totalU: 42, usedU: 35, spaceUtil: 83, power: 8.0, maxPower: 15, powerUtil: 53, heatLoad: 7.6, maxCooling: 15, coolingUtil: 51, status: 'Normal', trend: 'up' },
  { id: 11, name: 'C01', row: 'C', totalU: 42, usedU: 34, spaceUtil: 81, power: 7.5, maxPower: 15, powerUtil: 50, heatLoad: 7.2, maxCooling: 15, coolingUtil: 48, status: 'Normal', trend: 'stable' },
  { id: 12, name: 'C02', row: 'C', totalU: 42, usedU: 28, spaceUtil: 67, power: 6.0, maxPower: 15, powerUtil: 40, heatLoad: 5.8, maxCooling: 15, coolingUtil: 39, status: 'Normal', trend: 'stable' },
  { id: 13, name: 'C03', row: 'C', totalU: 42, usedU: 40, spaceUtil: 95, power: 11.0, maxPower: 15, powerUtil: 73, heatLoad: 10.5, maxCooling: 15, coolingUtil: 70, status: 'Warning', trend: 'up' },
  { id: 14, name: 'C04', row: 'C', totalU: 42, usedU: 25, spaceUtil: 60, power: 5.5, maxPower: 15, powerUtil: 37, heatLoad: 5.2, maxCooling: 15, coolingUtil: 35, status: 'Normal', trend: 'down' },
  { id: 15, name: 'C05', row: 'C', totalU: 42, usedU: 38, spaceUtil: 90, power: 8.8, maxPower: 15, powerUtil: 59, heatLoad: 8.4, maxCooling: 15, coolingUtil: 56, status: 'Normal', trend: 'stable' },
  { id: 16, name: 'D01', row: 'D', totalU: 42, usedU: 32, spaceUtil: 76, power: 7.0, maxPower: 15, powerUtil: 47, heatLoad: 6.8, maxCooling: 15, coolingUtil: 45, status: 'Normal', trend: 'stable' },
  { id: 17, name: 'D02', row: 'D', totalU: 42, usedU: 28, spaceUtil: 67, power: 6.2, maxPower: 15, powerUtil: 41, heatLoad: 6.0, maxCooling: 15, coolingUtil: 40, status: 'Normal', trend: 'down' },
  { id: 18, name: 'D03', row: 'D', totalU: 42, usedU: 35, spaceUtil: 83, power: 7.8, maxPower: 15, powerUtil: 52, heatLoad: 7.5, maxCooling: 15, coolingUtil: 50, status: 'Normal', trend: 'up' },
  { id: 19, name: 'D04', row: 'D', totalU: 42, usedU: 30, spaceUtil: 71, power: 6.5, maxPower: 15, powerUtil: 43, heatLoad: 6.2, maxCooling: 15, coolingUtil: 41, status: 'Normal', trend: 'stable' },
  { id: 20, name: 'D05', row: 'D', totalU: 42, usedU: 38, spaceUtil: 90, power: 8.5, maxPower: 15, powerUtil: 57, heatLoad: 8.2, maxCooling: 15, coolingUtil: 55, status: 'Normal', trend: 'stable' }
])

// Computed values
const avgSpaceUtilization = computed(() => {
  const sum = racks.value.reduce((acc, r) => acc + r.spaceUtil, 0)
  return Math.round(sum / racks.value.length)
})

const avgPowerUtilization = computed(() => {
  const sum = racks.value.reduce((acc, r) => acc + r.powerUtil, 0)
  return Math.round(sum / racks.value.length)
})

const avgCoolingUtilization = computed(() => {
  const sum = racks.value.reduce((acc, r) => acc + r.coolingUtil, 0)
  return Math.round(sum / racks.value.length)
})

const avgSpaceColor = computed(() => getUtilColor(avgSpaceUtilization.value))
const avgPowerColor = computed(() => getPowerColor(avgPowerUtilization.value))
const avgCoolingColor = computed(() => getCoolingColor(avgCoolingUtilization.value))

const rows = ['A', 'B', 'C', 'D']

// Highest utilization rankings
const highestSpaceUtilization = computed(() => {
  return [...racks.value].sort((a, b) => b.spaceUtil - a.spaceUtil).slice(0, 5)
})

const highestPowerUtilization = computed(() => {
  return [...racks.value].sort((a, b) => b.powerUtil - a.powerUtil).slice(0, 5)
})

const highestCoolingUtilization = computed(() => {
  return [...racks.value].sort((a, b) => b.coolingUtil - a.coolingUtil).slice(0, 5)
})

// Filtered racks
const filteredRacks = computed(() => {
  let result = racks.value

  if (searchQuery.value) {
    result = result.filter(r => r.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }

  if (filterRow.value) {
    result = result.filter(r => r.row === filterRow.value)
  }

  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value)
  }

  return result
})

// Helper functions
const getUtilColor = (percent: number) => {
  if (percent < 50) return '#10b981'
  if (percent < 70) return '#84cc16'
  if (percent < 85) return '#f59e0b'
  return '#ef4444'
}

const getPowerColor = (percent: number) => {
  if (percent < 50) return '#10b981'
  if (percent < 70) return '#84cc16'
  if (percent < 85) return '#f59e0b'
  return '#ef4444'
}

const getCoolingColor = (percent: number) => {
  if (percent < 50) return '#10b981'
  if (percent < 70) return '#84cc16'
  if (percent < 85) return '#f59e0b'
  return '#ef4444'
}

const getStatusClass = (rack: any) => {
  if (rack.status === 'Critical') return 'critical'
  if (rack.status === 'Warning') return 'warning'
  return 'normal'
}

const getRackAtPosition = (row: string, pos: number) => {
  return racks.value.find(r => r.row === row && r.position === pos)
}

const getCellColor = (row: string, pos: number) => {
  const rack = getRackAtPosition(row, pos)
  if (!rack) return '#e2e8f0'

  let value = 0
  if (heatmapType.value === 'space') value = rack.spaceUtil
  else if (heatmapType.value === 'power') value = rack.powerUtil
  else value = rack.coolingUtil

  if (value < 30) return '#10b981'
  if (value < 50) return '#84cc16'
  if (value < 70) return '#f59e0b'
  if (value < 85) return '#ef4444'
  return '#7c2d12'
}

const getCellValue = (row: string, pos: number) => {
  const rack = getRackAtPosition(row, pos)
  if (!rack) return 0

  if (heatmapType.value === 'space') return rack.spaceUtil
  if (heatmapType.value === 'power') return rack.powerUtil
  return rack.coolingUtil
}

const getRackName = (row: string, pos: number) => {
  const rack = getRackAtPosition(row, pos)
  return rack ? rack.name : ''
}

const showRackDetail = (row: string, pos: number) => {
  const rack = getRackAtPosition(row, pos)
  if (rack) {
    selectedRack.value = rack
    detailDialogVisible.value = true
  }
}

const getRecommendations = (rack: any) => {
  const recs = []
  if (rack.spaceUtil > 85) {
    recs.push('Space utilization is high. Consider adding new racks or consolidating equipment.')
  }
  if (rack.powerUtil > 80) {
    recs.push('Power utilization is critical. Upgrade power distribution or redistribute load.')
  }
  if (rack.coolingUtil > 80) {
    recs.push('Cooling capacity is insufficient. Add supplemental cooling units.')
  }
  if (rack.spaceUtil < 50 && rack.powerUtil < 50) {
    recs.push('Underutilized rack. Consider consolidating with other racks.')
  }
  if (recs.length === 0) {
    recs.push('Rack utilization is within optimal range. Continue monitoring.')
  }
  return recs
}

const optimizeRack = (rack: any) => {
  ElMessage.info(`Optimization plan for ${rack.name} is being generated.`)
}

const refreshData = () => {
  ElMessage.success('Data refreshed successfully')
}

const exportReport = () => {
  ElMessage.success('Report exported successfully')
}

// Trend chart
let trendChart: echarts.ECharts | null = null

const generateTrendData = (rackId: number) => {
  const baseSpace = 60
  const basePower = 45
  const baseCooling = 40
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  const rack = racks.value.find(r => r.id === rackId)
  const variation = rack ? (rack.spaceUtil - 60) / 5 : 0

  const spaceData = months.map((_, i) => {
    return Math.min(100, Math.max(20, baseSpace + variation * i + (Math.random() - 0.5) * 5))
  })
  const powerData = months.map((_, i) => {
    return Math.min(100, Math.max(20, basePower + variation * i * 0.7 + (Math.random() - 0.5) * 4))
  })
  const coolingData = months.map((_, i) => {
    return Math.min(100, Math.max(20, baseCooling + variation * i * 0.8 + (Math.random() - 0.5) * 4))
  })

  return { months, spaceData, powerData, coolingData }
}

const initTrendChart = () => {
  const canvas = document.getElementById('trendChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const rect = container.getBoundingClientRect()
  const width = rect.width
  const height = 350

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  updateTrendChart()
}

const updateTrendChart = () => {
  if (!trendChart) return

  const { months, spaceData, powerData, coolingData } = generateTrendData(trendRack.value)

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Space Utilization', 'Power Utilization', 'Cooling Utilization'], bottom: 0, left: 'center' },
    grid: { top: 40, left: 60, right: 40, bottom: 50, containLabel: true },
    xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', name: 'Utilization (%)', min: 0, max: 100, axisLabel: { fontSize: 11 } },
    series: [
      { name: 'Space Utilization', type: 'line', data: spaceData, smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Power Utilization', type: 'line', data: powerData, smooth: true, lineStyle: { color: '#f59e0b', width: 2 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Cooling Utilization', type: 'line', data: coolingData, smooth: true, lineStyle: { color: '#10b981', width: 2 }, areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 6 }
    ]
  })
}

const refreshTrendChart = () => {
  updateTrendChart()
}

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (trendChart) {
      const canvas = document.getElementById('trendChart') as HTMLCanvasElement
      if (canvas && canvas.parentElement) {
        const width = canvas.parentElement.clientWidth
        const height = 350
        canvas.width = width * (window.devicePixelRatio || 1)
        canvas.height = height * (window.devicePixelRatio || 1)
        canvas.style.width = `${width}px`
        canvas.style.height = `${height}px`
        trendChart.resize({ width, height })
      }
    }
  }, 200)
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
      nextTick(() => {
        setTimeout(() => {
          initTrendChart()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  if (trendChart) trendChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.rack-utilization-container {
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
.rack-utilization-main {
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

/* Overview Cards */
.overview-section {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.card-icon.blue { background: #eff6ff; color: #3b82f6; }
.card-icon.green { background: #ecfdf5; color: #10b981; }
.card-icon.orange { background: #fffbeb; color: #f59e0b; }
.card-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.card-info {
  flex: 1;
}

.card-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.card-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

/* Heatmap Section */
.heatmap-section {
  margin-bottom: 24px;
}

.heatmap-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
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

.heatmap-grid {
  overflow-x: auto;
}

.heatmap-header,
.heatmap-row {
  display: flex;
  margin-bottom: 4px;
}

.corner {
  width: 60px;
}

.position-label {
  width: 100px;
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  padding: 8px;
}

.row-label {
  width: 60px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.heatmap-cell {
  width: 100px;
  height: 80px;
  margin: 2px;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.heatmap-cell:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.cell-value {
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.cell-label {
  font-size: 11px;
  color: white;
  opacity: 0.9;
  margin-top: 4px;
}

.heatmap-legend {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  flex-wrap: wrap;
}

.legend-title {
  font-size: 13px;
  font-weight: 500;
  color: #64748b;
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 4px;
}

/* Rankings Section */
.rankings-section {
  margin-bottom: 24px;
}

.ranking-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.ranking-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rank {
  width: 30px;
  font-size: 14px;
  font-weight: 700;
  color: #64748b;
}

.rank-name {
  width: 50px;
  font-weight: 600;
  color: #1e293b;
}

.rank-value {
  width: 45px;
  font-size: 14px;
  font-weight: 700;
}

.rank-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

/* Table Section */
.table-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.utilization-table {
  border-radius: 16px;
  overflow: hidden;
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
  min-width: 70px;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
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

/* Trends Section */
.trends-section {
  margin-bottom: 24px;
}

.trends-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.trends-chart-container {
  width: 100%;
  min-height: 350px;
  position: relative;
}

/* Detail Dialog */
.detail-dialog :deep(.el-dialog__body) {
  padding: 20px 24px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-section h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.detail-progress {
  padding: 8px 0;
}

.detail-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #64748b;
}

.recommendations-list {
  margin: 0;
  padding-left: 20px;
}

.recommendations-list li {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

/* Responsive */
@media (max-width: 1200px) {
  .rack-utilization-main { padding: 16px; }
  .heatmap-cell { width: 70px; height: 70px; }
  .position-label { width: 70px; }
  .cell-value { font-size: 14px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .heatmap-cell { width: 55px; height: 65px; }
  .position-label { width: 55px; font-size: 10px; }
  .cell-value { font-size: 12px; }
  .cell-label { font-size: 9px; }
  .section-header { flex-direction: column; align-items: flex-start; }
}
</style>