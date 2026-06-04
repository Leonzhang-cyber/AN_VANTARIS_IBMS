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
          <span class="loading-title">Cooling Maintenance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">HVAC & Cooling System Performance Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cooling-maintenance-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><ColdDrink /></el-icon>
          Cooling Maintenance
        </h1>
        <div class="page-subtitle">Monitor cooling systems, efficiency metrics, and maintenance schedules</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openScheduleDialog">
          <el-icon><Plus /></el-icon> Schedule Maintenance
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
          <el-icon><ColdDrink /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalUnits }}</div>
          <div class="stat-label">Total Cooling Units</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.healthyUnits }}</div>
          <div class="stat-label">Healthy (≥90%)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.warningUnits }}</div>
          <div class="stat-label">Warning (70-89%)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.criticalUnits }}</div>
          <div class="stat-label">Critical (<70%)</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Average PUE</div>
        <div class="metric-value">{{ metrics.avgPUE }}</div>
        <div class="metric-trend" :class="metrics.pueTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.pueTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.pueTrend) }} vs last month
        </div>
        <div class="metric-target">Target: ≤ 1.4</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Cooling Efficiency</div>
        <div class="metric-value">{{ metrics.coolingEfficiency }}<span class="metric-unit">%</span></div>
        <div class="metric-trend" :class="metrics.efficiencyTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.efficiencyTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.efficiencyTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Temperature</div>
        <div class="metric-value">{{ metrics.avgTemp }}<span class="metric-unit">°C</span></div>
        <div class="metric-trend" :class="metrics.tempTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.tempTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.tempTrend) }}°C vs last month
        </div>
        <div class="metric-target">Target: 22-24°C</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Free Cooling Hours</div>
        <div class="metric-value">{{ metrics.freeCoolingHours }}</div>
        <div class="metric-trend positive">↑ {{ metrics.freeCoolingGrowth }} hrs vs last year</div>
        <div class="metric-target">Energy savings: ${{ metrics.energySavings }}K</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">PUE Trend</span>
          <span class="chart-subtitle">Power Usage Effectiveness over time</span>
        </div>
        <div class="chart-container" ref="pueChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cooling Unit Health Distribution</span>
          <span class="chart-subtitle">Current health status by range</span>
        </div>
        <div class="chart-container" ref="healthChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Temperature & Humidity Trends</span>
          <span class="chart-subtitle">Hot aisle / Cold aisle monitoring</span>
        </div>
        <div class="chart-container" ref="tempChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Energy Consumption by Cooling System</span>
          <span class="chart-subtitle">Percentage of total cooling load</span>
        </div>
        <div class="chart-container" ref="energyChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by unit name or location..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="typeFilter" placeholder="Unit Type" clearable style="width: 140px">
          <el-option label="CRAC" value="CRAC" />
          <el-option label="CRAH" value="CRAH" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="Cooling Tower" value="Cooling Tower" />
          <el-option label="Air Handler" value="AHU" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Healthy" value="healthy" />
          <el-option label="Warning" value="warning" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="locationFilter" placeholder="Location" clearable filterable style="width: 150px">
          <el-option v-for="l in uniqueLocations" :key="l" :label="l" :value="l" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Cooling Units Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Cooling Units Inventory</span>
        <el-button size="small" @click="viewAllUnits">View All →</el-button>
      </div>
      <el-table :data="paginatedUnits" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewUnitDetail">
        <el-table-column prop="id" label="Unit ID" width="120" />
        <el-table-column prop="name" label="Unit Name" min-width="160" />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="Location" width="180" />
        <el-table-column prop="health" label="Health" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.health" :stroke-width="8" :color="getHealthColor(row.health)" />
          </template>
        </el-table-column>
        <el-table-column prop="supplyTemp" label="Supply Temp" width="110">
          <template #default="{ row }">
            <span :class="getTempClass(row.supplyTemp, row.targetTemp)">{{ row.supplyTemp }}°C</span>
          </template>
        </el-table-column>
        <el-table-column prop="returnTemp" label="Return Temp" width="110">
          <template #default="{ row }">
            <span>{{ row.returnTemp }}°C</span>
          </template>
        </el-table-column>
        <el-table-column prop="power" label="Power (kW)" width="100" />
        <el-table-column prop="lastPM" label="Last PM" width="120" />
        <el-table-column label="Actions" width="120" fixed="right">
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

    <!-- Unit Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedUnit?.name" width="1000px" class="cooling-dialog">
      <div v-if="selectedUnit" class="unit-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedUnit.health) }">
              {{ selectedUnit.health }}%
            </div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedUnit.supplyTemp }}°C</div>
            <div class="detail-stat-label">Supply Temp</div>
            <div class="detail-stat-sub">Target: {{ selectedUnit.targetTemp }}°C</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedUnit.returnTemp }}°C</div>
            <div class="detail-stat-label">Return Temp</div>
            <div class="detail-stat-sub">Delta T: {{ (selectedUnit.returnTemp - selectedUnit.supplyTemp).toFixed(1) }}°C</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedUnit.power }} kW</div>
            <div class="detail-stat-label">Power Consumption</div>
            <div class="detail-stat-sub">{{ selectedUnit.capacity }} kW capacity</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="Unit ID">{{ selectedUnit.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedUnit.type }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedUnit.model }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedUnit.location }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedUnit.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Capacity">{{ selectedUnit.capacity }} kW</el-descriptions-item>
          <el-descriptions-item label="Fan Speed">{{ selectedUnit.fanSpeed }}%</el-descriptions-item>
          <el-descriptions-item label="Compressor Status">{{ selectedUnit.compressorStatus }}</el-descriptions-item>
          <el-descriptions-item label="Refrigerant">{{ selectedUnit.refrigerant }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedUnit.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Last PM">{{ selectedUnit.lastPM }}</el-descriptions-item>
          <el-descriptions-item label="Next PM">{{ selectedUnit.nextPM }}</el-descriptions-item>
        </el-descriptions>

        <!-- Performance Chart -->
        <div class="detail-section">
          <div class="section-title">Performance Trends</div>
          <div class="trend-chart" ref="performanceChartEl"></div>
        </div>

        <!-- Component Status -->
        <div class="detail-section">
          <div class="section-title">Component Status</div>
          <el-table :data="selectedUnit.components" border stripe>
            <el-table-column prop="name" label="Component" width="200" />
            <el-table-column prop="status" label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Good' ? 'success' : (row.status === 'Warning' ? 'warning' : 'danger')" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="value" label="Reading" width="150" />
            <el-table-column prop="threshold" label="Threshold" width="150" />
            <el-table-column prop="lastCheck" label="Last Check" width="120" />
          </el-table>
        </div>

        <!-- Maintenance History -->
        <div class="detail-section">
          <div class="section-title">Maintenance History</div>
          <el-table :data="selectedUnit.maintenanceHistory" border stripe>
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

        <!-- Recent Alerts -->
        <div class="detail-section" v-if="selectedUnit.recentAlerts.length > 0">
          <div class="section-title">Recent Alerts</div>
          <el-table :data="selectedUnit.recentAlerts" border stripe>
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

        <!-- Recommendations -->
        <div class="detail-section" v-if="selectedUnit.recommendations">
          <div class="section-title">Recommendations</div>
          <el-alert
              :title="selectedUnit.recommendations.title"
              :type="selectedUnit.recommendations.type"
              :description="selectedUnit.recommendations.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleMaintenance(selectedUnit)">Schedule Maintenance</el-button>
        <el-button type="warning" @click="generateUnitReport(selectedUnit)">Generate Report</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Maintenance Dialog -->
    <el-dialog v-model="scheduleDialogVisible" title="Schedule Cooling Maintenance" width="550px">
      <el-form :model="scheduleForm" label-width="130px">
        <el-form-item label="Cooling Unit" required>
          <el-input :value="scheduleForm.unitName" disabled />
        </el-form-item>
        <el-form-item label="Maintenance Type" required>
          <el-select v-model="scheduleForm.maintenanceType" placeholder="Select type" style="width: 100%">
            <el-option label="Preventive Maintenance" value="preventive" />
            <el-option label="Corrective Maintenance" value="corrective" />
            <el-option label="Filter Replacement" value="filter" />
            <el-option label="Coil Cleaning" value="cleaning" />
            <el-option label="Refrigerant Recharge" value="refrigerant" />
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
            <el-option label="John Tan - HVAC Specialist" value="John Tan" />
            <el-option label="Mike Chen - Cooling Expert" value="Mike Chen" />
            <el-option label="Ahmad Ibrahim - Chiller Tech" value="Ahmad Ibrahim" />
            <el-option label="Lim Wei Ming - Field Engineer" value="Lim Wei Ming" />
            <el-option label="Sarah Koh - HVAC Tech" value="Sarah Koh" />
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
  ColdDrink, Plus, Download, Refresh, CircleCheck, Warning, CircleClose,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading cooling maintenance data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading cooling system data...',
  'Fetching PUE metrics...',
  'Analyzing efficiency trends...',
  'Loading maintenance schedules...',
  'Almost ready...'
]

// ==================== Types ====================
interface Component {
  name: string
  status: string
  value: string
  threshold: string
  lastCheck: string
}

interface MaintenanceRecord {
  date: string
  type: string
  description: string
  technician: string
  status: string
}

interface CoolingAlert {
  id: number
  date: string
  severity: string
  description: string
  resolved: boolean
}

interface Recommendation {
  title: string
  type: 'warning' | 'error' | 'info' | 'success'
  description: string
}

interface CoolingUnit {
  id: string
  name: string
  type: string
  model: string
  location: string
  manufacturer: string
  capacity: number
  health: number
  supplyTemp: number
  returnTemp: number
  targetTemp: number
  power: number
  fanSpeed: number
  compressorStatus: string
  refrigerant: string
  installDate: string
  lastPM: string
  nextPM: string
  performanceHistory: { date: string; supplyTemp: number; returnTemp: number; power: number }[]
  components: Component[]
  maintenanceHistory: MaintenanceRecord[]
  recentAlerts: CoolingAlert[]
  recommendations?: Recommendation
}

// ==================== Mock Data (30 cooling units) ====================
const generateCoolingData = (): CoolingUnit[] => {
  const locations = [
    'Data Center A - Cold Aisle 1', 'Data Center A - Cold Aisle 2', 'Data Center B - Row 1', 'Data Center B - Row 2',
    'Server Room North', 'Server Room South', 'Main UPS Room', 'Chiller Plant Room'
  ]

  const types = ['CRAC', 'CRAH', 'Chiller', 'Cooling Tower', 'AHU']
  const manufacturers = ['Schneider Electric', 'Vertiv', 'Stulz', 'Trane', 'Carrier', 'Daikin', 'Johnson Controls']
  const models = ['DX-1000', 'CW-2000', 'EC-1500', 'HV-3000', 'CRAC-500']

  const units: CoolingUnit[] = []

  for (let i = 1; i <= 30; i++) {
    const type = types[Math.floor(Math.random() * types.length)]
    const installDate = new Date()
    installDate.setMonth(installDate.getMonth() - Math.random() * 60)
    const installDateStr = installDate.toISOString().slice(0, 10)

    const ageYears = (new Date().getTime() - installDate.getTime()) / (1000 * 60 * 60 * 24 * 365)
    const baseHealth = Math.max(50, Math.min(100, 100 - ageYears * 8 + (Math.random() * 10 - 5)))
    const health = Math.round(baseHealth)

    const capacity = type === 'Chiller' ? [200, 300, 500][Math.floor(Math.random() * 3)] : [50, 80, 100, 150][Math.floor(Math.random() * 4)]
    const power = Math.round(capacity * (0.3 + Math.random() * 0.4))

    const supplyTemp = 18 + Math.random() * 6
    const returnTemp = supplyTemp + 8 + Math.random() * 4
    const targetTemp = 22

    const performanceHistory = []
    for (let m = 0; m <= 6; m++) {
      performanceHistory.push({
        date: new Date(Date.now() - m * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 7),
        supplyTemp: parseFloat((18 + Math.random() * 6 + m * 0.2).toFixed(1)),
        returnTemp: parseFloat((26 + Math.random() * 4 + m * 0.1).toFixed(1)),
        power: Math.round(power * (0.9 + Math.random() * 0.2))
      })
    }

    const components: Component[] = [
      { name: 'Compressor', status: health > 80 ? 'Good' : (health > 60 ? 'Warning' : 'Critical'), value: `${Math.round(65 + Math.random() * 20)}% load`, threshold: '< 85% load', lastCheck: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) },
      { name: 'Fan Motor', status: health > 75 ? 'Good' : 'Warning', value: `${Math.round(40 + Math.random() * 50)}% speed`, threshold: 'Normal operation', lastCheck: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) },
      { name: 'Filter', status: Math.random() > 0.7 ? 'Warning' : 'Good', value: `${Math.round(30 + Math.random() * 70)}% clogged`, threshold: '< 60% clogged', lastCheck: new Date(Date.now() - Math.random() * 15 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) },
      { name: 'Refrigerant', status: health > 70 ? 'Good' : 'Warning', value: `${Math.round(70 + Math.random() * 30)}% charge`, threshold: '> 60% charge', lastCheck: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) }
    ]

    const maintenanceHistory = []
    const pmDates = [3, 6, 9, 12, 15, 18].map(months => {
      const date = new Date(installDate)
      date.setMonth(date.getMonth() + months)
      return date
    }).filter(d => d < new Date())

    pmDates.forEach((date, idx) => {
      maintenanceHistory.push({
        date: date.toISOString().slice(0, 10),
        type: 'Preventive',
        description: `Quarterly preventive maintenance - Filter change and coil cleaning`,
        technician: ['John Tan', 'Mike Chen', 'Ahmad Ibrahim', 'Lim Wei Ming'][idx % 4],
        status: 'Completed'
      })
    })

    const recentAlerts: CoolingAlert[] = []
    if (health < 70) {
      recentAlerts.push({
        id: i * 100 + 1,
        date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: 'High',
        description: `Cooling capacity below threshold - health at ${health}%`,
        resolved: false
      })
    }
    if (supplyTemp > targetTemp + 3) {
      recentAlerts.push({
        id: i * 100 + 2,
        date: new Date(Date.now() - Math.random() * 10 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: 'Medium',
        description: `Supply temperature high (${supplyTemp.toFixed(1)}°C) - check setpoints`,
        resolved: supplyTemp < targetTemp + 2
      })
    }

    let recommendations: Recommendation | undefined
    if (health < 60) {
      recommendations = {
        title: 'Major Overhaul Required',
        type: 'error',
        description: `Unit health is critically low (${health}%). Schedule major maintenance or replacement.`
      }
    } else if (health < 80) {
      recommendations = {
        title: 'Preventive Maintenance Due',
        type: 'warning',
        description: `Unit health is below optimal level (${health}%). Schedule preventive maintenance soon.`
      }
    }

    units.push({
      id: `CL-${String(i).padStart(3, '0')}`,
      name: `${type} ${String.fromCharCode(65 + Math.floor((i - 1) / 5))}${((i - 1) % 5) + 1}`,
      type: type,
      model: models[Math.floor(Math.random() * models.length)],
      location: locations[(i - 1) % locations.length],
      manufacturer: manufacturers[Math.floor(Math.random() * manufacturers.length)],
      capacity: capacity,
      health: health,
      supplyTemp: parseFloat(supplyTemp.toFixed(1)),
      returnTemp: parseFloat(returnTemp.toFixed(1)),
      targetTemp: targetTemp,
      power: power,
      fanSpeed: Math.round(40 + Math.random() * 50),
      compressorStatus: health > 70 ? 'Running' : (health > 50 ? 'Degraded' : 'Fault'),
      refrigerant: type === 'Chiller' ? 'R-134a' : 'R-410A',
      installDate: installDateStr,
      lastPM: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      nextPM: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      performanceHistory: performanceHistory.reverse(),
      components: components,
      maintenanceHistory: maintenanceHistory,
      recentAlerts: recentAlerts,
      recommendations: recommendations
    })
  }

  return units
}

const coolingUnits = ref<CoolingUnit[]>(generateCoolingData())

// ==================== State ====================
const searchText = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const locationFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const scheduleDialogVisible = ref(false)
const selectedUnit = ref<CoolingUnit | null>(null)

// Chart refs
let pueChart: echarts.ECharts | null = null
let healthChart: echarts.ECharts | null = null
let tempChart: echarts.ECharts | null = null
let energyChart: echarts.ECharts | null = null
let performanceChart: echarts.ECharts | null = null

const pueChartEl = ref<HTMLElement | null>(null)
const healthChartEl = ref<HTMLElement | null>(null)
const tempChartEl = ref<HTMLElement | null>(null)
const energyChartEl = ref<HTMLElement | null>(null)
const performanceChartEl = ref<HTMLElement | null>(null)

const scheduleForm = ref({
  unitId: '',
  unitName: '',
  maintenanceType: 'preventive',
  scheduleDate: '',
  priority: 'Medium',
  technician: '',
  notes: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalUnits = coolingUnits.value.length
  const healthyUnits = coolingUnits.value.filter(u => u.health >= 90).length
  const warningUnits = coolingUnits.value.filter(u => u.health >= 70 && u.health < 90).length
  const criticalUnits = coolingUnits.value.filter(u => u.health < 70).length
  return { totalUnits, healthyUnits, warningUnits, criticalUnits }
})

const metrics = computed(() => {
  const avgPUE = (1.35 + Math.random() * 0.1).toFixed(2)
  const coolingEfficiency = Math.round(coolingUnits.value.reduce((sum, u) => sum + u.health, 0) / coolingUnits.value.length)
  const avgTemp = (coolingUnits.value.reduce((sum, u) => sum + u.supplyTemp, 0) / coolingUnits.value.length).toFixed(1)
  const freeCoolingHours = 1850
  const freeCoolingGrowth = 120
  const energySavings = 45

  return {
    avgPUE: parseFloat(avgPUE),
    pueTrend: -0.03,
    coolingEfficiency,
    efficiencyTrend: 2.5,
    avgTemp: parseFloat(avgTemp),
    tempTrend: -0.5,
    freeCoolingHours,
    freeCoolingGrowth,
    energySavings
  }
})

const uniqueLocations = computed(() => {
  return [...new Set(coolingUnits.value.map(u => u.location))]
})

const filteredUnits = computed(() => {
  let filtered = [...coolingUnits.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(u =>
        u.id.toLowerCase().includes(search) ||
        u.name.toLowerCase().includes(search) ||
        u.location.toLowerCase().includes(search)
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(u => u.type === typeFilter.value)
  }

  if (statusFilter.value) {
    if (statusFilter.value === 'healthy') filtered = filtered.filter(u => u.health >= 90)
    else if (statusFilter.value === 'warning') filtered = filtered.filter(u => u.health >= 70 && u.health < 90)
    else if (statusFilter.value === 'critical') filtered = filtered.filter(u => u.health < 70)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(u => u.location === locationFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredUnits.value.length)

const paginatedUnits = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUnits.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getHealthColor = (health: number): string => {
  if (health >= 90) return '#22c55e'
  if (health >= 70) return '#f59e0b'
  return '#ef4444'
}

const getTypeTagType = (type: string): string => {
  const map: Record<string, string> = { CRAC: 'primary', CRAH: 'success', Chiller: 'warning', 'Cooling Tower': 'info', AHU: '' }
  return map[type] || 'info'
}

const getTempClass = (temp: number, target: number): string => {
  if (temp <= target + 1) return 'metric-good'
  if (temp <= target + 3) return 'metric-warning'
  return 'metric-bad'
}

const resetFilters = () => {
  searchText.value = ''
  typeFilter.value = ''
  statusFilter.value = ''
  locationFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initPueChart = () => {
  if (!pueChartEl.value) return
  if (pueChart) {
    pueChart.dispose()
    pueChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  const pueData = [1.52, 1.49, 1.47, 1.44, 1.41, 1.38]

  pueChart = echarts.init(pueChartEl.value)
  pueChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 30, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'PUE', min: 1.3, max: 1.6 },
    series: [{
      type: 'line',
      data: pueData,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initHealthChart = () => {
  if (!healthChartEl.value) return
  if (healthChart) {
    healthChart.dispose()
    healthChart = null
  }

  const healthy = coolingUnits.value.filter(u => u.health >= 90).length
  const warning = coolingUnits.value.filter(u => u.health >= 70 && u.health < 90).length
  const critical = coolingUnits.value.filter(u => u.health < 70).length

  healthChart = echarts.init(healthChartEl.value)
  healthChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} units)' },
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

const initTempChart = () => {
  if (!tempChartEl.value) return
  if (tempChart) {
    tempChart.dispose()
    tempChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  const coldAisle = [22.5, 22.8, 23.1, 23.4, 23.6, 23.8]
  const hotAisle = [28.5, 28.8, 29.1, 29.4, 29.6, 29.8]

  tempChart = echarts.init(tempChartEl.value)
  tempChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Cold Aisle Temp', 'Hot Aisle Temp'], bottom: 0 },
    grid: { top: 30, left: 50, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Temperature (°C)', min: 20, max: 32 },
    series: [
      { name: 'Cold Aisle Temp', type: 'line', data: coldAisle, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Hot Aisle Temp', type: 'line', data: hotAisle, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle' }
    ]
  })
}

const initEnergyChart = () => {
  if (!energyChartEl.value) return
  if (energyChart) {
    energyChart.dispose()
    energyChart = null
  }

  energyChart = echarts.init(energyChartEl.value)
  energyChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: ['CRAC Units', 'CRAH Units', 'Chillers', 'Cooling Towers', 'Pumps'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: 35, name: 'CRAC Units', itemStyle: { color: '#3b82f6' } },
        { value: 25, name: 'CRAH Units', itemStyle: { color: '#22c55e' } },
        { value: 25, name: 'Chillers', itemStyle: { color: '#f59e0b' } },
        { value: 10, name: 'Cooling Towers', itemStyle: { color: '#8b5cf6' } },
        { value: 5, name: 'Pumps', itemStyle: { color: '#ec489a' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initPerformanceChart = () => {
  if (!performanceChartEl.value || !selectedUnit.value) return
  if (performanceChart) {
    performanceChart.dispose()
    performanceChart = null
  }

  const months = selectedUnit.value.performanceHistory.map(h => h.date)
  const supplyTempData = selectedUnit.value.performanceHistory.map(h => h.supplyTemp)
  const returnTempData = selectedUnit.value.performanceHistory.map(h => h.returnTemp)

  performanceChart = echarts.init(performanceChartEl.value)
  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Supply Temp', 'Return Temp'], bottom: 0 },
    grid: { top: 30, left: 50, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Temperature (°C)' },
    series: [
      { name: 'Supply Temp', type: 'line', data: supplyTempData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Return Temp', type: 'line', data: returnTempData, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle' }
    ]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initPueChart()
    initHealthChart()
    initTempChart()
    initEnergyChart()
  })
}

// ==================== Actions ====================
const viewUnitDetail = (unit: CoolingUnit) => {
  selectedUnit.value = unit
  detailDialogVisible.value = true
  nextTick(() => initPerformanceChart())
}

const viewHistory = (unit: CoolingUnit) => {
  viewUnitDetail(unit)
}

const scheduleMaintenance = (unit: CoolingUnit | null) => {
  if (unit) {
    scheduleForm.value = {
      unitId: unit.id,
      unitName: unit.name,
      maintenanceType: unit.health < 70 ? 'corrective' : 'preventive',
      scheduleDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      priority: unit.health < 70 ? 'High' : (unit.health < 85 ? 'Medium' : 'Low'),
      technician: '',
      notes: ''
    }
    scheduleDialogVisible.value = true
  } else {
    scheduleForm.value = {
      unitId: '',
      unitName: '',
      maintenanceType: 'preventive',
      scheduleDate: new Date().toISOString().slice(0, 10),
      priority: 'Medium',
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

  ElMessage.success(`Maintenance scheduled for ${scheduleForm.value.unitName}`)
  scheduleDialogVisible.value = false
}

const generateUnitReport = (unit: CoolingUnit | null) => {
  if (!unit) return
  ElMessage.success(`Generating report for ${unit.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const viewAllUnits = () => {
  ElMessage.info('Viewing all cooling units')
}

const exportData = () => {
  ElMessage.success('Exporting cooling maintenance data...')
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

const openScheduleDialog = () => {
  scheduleMaintenance(null)
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [pueChart, healthChart, tempChart, energyChart, performanceChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, typeFilter, statusFilter, locationFilter], () => {
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
  const charts = [pueChart, healthChart, tempChart, energyChart, performanceChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.cooling-maintenance-page {
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

/* Unit Detail */
.unit-detail {
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

.trend-chart {
  height: 280px;
  width: 100%;
}

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