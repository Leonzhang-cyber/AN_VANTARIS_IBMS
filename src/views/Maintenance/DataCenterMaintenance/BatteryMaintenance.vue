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
          <span class="loading-title">Battery Maintenance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Battery Health & Performance Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="battery-maintenance-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Iphone /></el-icon>
          Battery Maintenance
        </h1>
        <div class="page-subtitle">Monitor battery health, performance metrics, and maintenance schedules</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openScheduleDialog">
          <el-icon><Plus /></el-icon> Schedule Replacement
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
          <el-icon><Iphone /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalBatteries }}</div>
          <div class="stat-label">Total Batteries</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.healthyBatteries }}</div>
          <div class="stat-label">Healthy (≥80%)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.warningBatteries }}</div>
          <div class="stat-label">Warning (50-79%)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.criticalBatteries }}</div>
          <div class="stat-label">Critical (<50%)</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Average Battery Health</div>
        <div class="metric-value">{{ metrics.avgHealth }}<span class="metric-unit">%</span></div>
        <div class="metric-trend" :class="metrics.healthTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.healthTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.healthTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Batteries Due for Replacement</div>
        <div class="metric-value">{{ metrics.dueForReplacement }}</div>
        <div class="metric-sub">Within next 3 months</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Estimated Replacement Cost</div>
        <div class="metric-value">${{ metrics.estimatedCost.toLocaleString() }}</div>
        <div class="metric-sub">Annual budget forecast</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Battery Age</div>
        <div class="metric-value">{{ metrics.avgAge }}<span class="metric-unit">years</span></div>
        <div class="metric-trend" :class="metrics.ageTrend > 0 ? 'negative' : 'positive'">
          {{ metrics.ageTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.ageTrend) }} months vs target
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Battery Health Distribution</span>
          <span class="chart-subtitle">Current health status by range</span>
        </div>
        <div class="chart-container" ref="healthDistChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Battery Degradation Trend</span>
          <el-select v-model="degradationPeriod" size="small" style="width: 100px" @change="updateDegradationChart">
            <el-option label="Last 6 Months" value="6" />
            <el-option label="Last 12 Months" value="12" />
          </el-select>
        </div>
        <div class="chart-container" ref="degradationChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Temperature Impact Analysis</span>
          <span class="chart-subtitle">Battery temperature vs health correlation</span>
        </div>
        <div class="chart-container" ref="tempChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Replacement Forecast</span>
          <span class="chart-subtitle">Projected replacements by quarter</span>
        </div>
        <div class="chart-container" ref="forecastChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by battery ID or UPS..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="healthFilter" placeholder="Health Status" clearable style="width: 140px">
          <el-option label="Healthy (≥80%)" value="healthy" />
          <el-option label="Warning (50-79%)" value="warning" />
          <el-option label="Critical (<50%)" value="critical" />
        </el-select>
        <el-select v-model="typeFilter" placeholder="Battery Type" clearable style="width: 140px">
          <el-option label="VRLA" value="VRLA" />
          <el-option label="Li-ion" value="Li-ion" />
          <el-option label="Ni-Cd" value="Ni-Cd" />
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

    <!-- Battery Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Battery Inventory</span>
        <el-button size="small" @click="viewAllBatteries">View All →</el-button>
      </div>
      <el-table :data="paginatedBatteries" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewBatteryDetail">
        <el-table-column prop="id" label="Battery ID" width="120" />
        <el-table-column prop="name" label="Battery Name" min-width="150" />
        <el-table-column prop="type" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'Li-ion' ? 'success' : (row.type === 'VRLA' ? 'primary' : 'warning')" size="small">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ups" label="Associated UPS" width="150" />
        <el-table-column prop="location" label="Location" width="180" />
        <el-table-column prop="health" label="Health" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.health" :stroke-width="8" :color="getHealthColor(row.health)" />
          </template>
        </el-table-column>
        <el-table-column prop="voltage" label="Voltage (V)" width="100" />
        <el-table-column prop="temperature" label="Temp (°C)" width="100">
          <template #default="{ row }">
            <span :class="row.temperature > 30 ? 'metric-warning' : 'metric-good'">{{ row.temperature }}°C</span>
          </template>
        </el-table-column>
        <el-table-column prop="installDate" label="Install Date" width="120" />
        <el-table-column prop="nextPM" label="Next PM" width="120" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="scheduleReplacement(row)">Replace</el-button>
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

    <!-- Battery Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedBattery?.name" width="1000px" class="battery-dialog">
      <div v-if="selectedBattery" class="battery-detail">
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedBattery.health) }">
              {{ selectedBattery.health }}%
            </div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedBattery.voltage }}V</div>
            <div class="detail-stat-label">Current Voltage</div>
            <div class="detail-stat-sub">Nominal: {{ selectedBattery.nominalVoltage }}V</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedBattery.temperature }}°C</div>
            <div class="detail-stat-label">Temperature</div>
            <div class="detail-stat-sub" :class="selectedBattery.temperature > 30 ? 'metric-warning' : 'metric-good'">
              {{ selectedBattery.temperature > 30 ? 'Above optimal' : 'Optimal' }}
            </div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedBattery.cycleCount }}</div>
            <div class="detail-stat-label">Cycle Count</div>
            <div class="detail-stat-sub">Design life: {{ selectedBattery.designCycles }} cycles</div>
          </div>
        </div>

        <el-descriptions :column="3" border>
          <el-descriptions-item label="Battery ID">{{ selectedBattery.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedBattery.type }}</el-descriptions-item>
          <el-descriptions-item label="Capacity">{{ selectedBattery.capacity }} Ah</el-descriptions-item>
          <el-descriptions-item label="Associated UPS">{{ selectedBattery.ups }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedBattery.location }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedBattery.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedBattery.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Warranty Expiry">{{ selectedBattery.warrantyExpiry }}</el-descriptions-item>
          <el-descriptions-item label="Last Test Date">{{ selectedBattery.lastTestDate }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-section">
          <div class="section-title">Health Degradation Trend</div>
          <div class="trend-chart" ref="detailTrendChartEl"></div>
        </div>

        <div class="detail-section">
          <div class="section-title">Internal Resistance</div>
          <el-table :data="selectedBattery.resistanceHistory" border stripe>
            <el-table-column prop="date" label="Test Date" width="150" />
            <el-table-column prop="resistance" label="Resistance (mΩ)" width="150">
              <template #default="{ row }">
                <span :class="row.resistance > row.baseline * 1.2 ? 'metric-bad' : 'metric-good'">
                  {{ row.resistance }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="baseline" label="Baseline (mΩ)" width="150" />
            <el-table-column prop="deviation" label="Deviation" width="120">
              <template #default="{ row }">
                <span :class="row.resistance > row.baseline * 1.2 ? 'metric-bad' : 'metric-good'">
                  +{{ ((row.resistance - row.baseline) / row.baseline * 100).toFixed(1) }}%
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="row.resistance <= row.baseline * 1.1 ? 'success' : (row.resistance <= row.baseline * 1.2 ? 'warning' : 'danger')" size="small">
                  {{ row.resistance <= row.baseline * 1.1 ? 'Normal' : (row.resistance <= row.baseline * 1.2 ? 'Warning' : 'Critical') }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="detail-section">
          <div class="section-title">Maintenance History</div>
          <el-table :data="selectedBattery.maintenanceHistory" border stripe>
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

        <div class="detail-section" v-if="selectedBattery.recentAlerts.length > 0">
          <div class="section-title">Recent Alerts</div>
          <el-table :data="selectedBattery.recentAlerts" border stripe>
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

        <div class="detail-section" v-if="selectedBattery.recommendations">
          <div class="section-title">Replacement Recommendations</div>
          <el-alert
              :title="selectedBattery.recommendations.title"
              :type="selectedBattery.recommendations.type"
              :description="selectedBattery.recommendations.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleReplacement(selectedBattery)">Schedule Replacement</el-button>
        <el-button type="warning" @click="generateBatteryReport(selectedBattery)">Generate Report</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Replacement Dialog -->
    <el-dialog v-model="scheduleDialogVisible" title="Schedule Battery Replacement" width="550px">
      <el-form :model="scheduleForm" label-width="130px">
        <el-form-item label="Battery Unit" required>
          <el-input :value="scheduleForm.batteryName" disabled />
        </el-form-item>
        <el-form-item label="Replacement Type" required>
          <el-select v-model="scheduleForm.replacementType" placeholder="Select type" style="width: 100%">
            <el-option label="Full String Replacement" value="full" />
            <el-option label="Partial Replacement" value="partial" />
            <el-option label="Individual Battery" value="individual" />
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
            <el-option label="High - Urgent Replacement" value="High" />
            <el-option label="Medium - Plan within 30 days" value="Medium" />
            <el-option label="Low - Plan within 90 days" value="Low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Assigned Technician">
          <el-select v-model="scheduleForm.technician" placeholder="Select technician" filterable style="width: 100%">
            <el-option label="John Tan - UPS Specialist" value="John Tan" />
            <el-option label="Mike Chen - Senior Tech" value="Mike Chen" />
            <el-option label="Ahmad Ibrahim - Battery Expert" value="Ahmad Ibrahim" />
            <el-option label="Lim Wei Ming - Field Engineer" value="Lim Wei Ming" />
            <el-option label="Sarah Koh - Maintenance Tech" value="Sarah Koh" />
          </el-select>
        </el-form-item>
        <el-form-item label="Estimated Cost">
          <el-input-number v-model="scheduleForm.estimatedCost" :min="500" :step="500" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="scheduleForm.notes" type="textarea" :rows="3" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSchedule">Schedule Replacement</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Iphone, Plus, Download, Refresh, CircleCheck, Warning, CircleClose,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading battery maintenance data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading battery maintenance data...',
  'Fetching battery health metrics...',
  'Analyzing degradation patterns...',
  'Loading replacement forecasts...',
  'Almost ready...'
]

// ==================== Types ====================
interface ResistanceRecord {
  date: string
  resistance: number
  baseline: number
  deviation: number
  status: string
}

interface MaintenanceRecord {
  date: string
  type: string
  description: string
  technician: string
  status: string
}

interface BatteryAlert {
  id: number
  date: string
  severity: string
  description: string
  resolved: boolean
  resolution?: string
}

interface Recommendation {
  title: string
  type: 'warning' | 'error' | 'info' | 'success'
  description: string
}

interface BatteryUnit {
  id: string
  name: string
  type: string
  ups: string
  location: string
  manufacturer: string
  capacity: number
  health: number
  voltage: number
  nominalVoltage: number
  temperature: number
  cycleCount: number
  designCycles: number
  installDate: string
  warrantyExpiry: string
  lastTestDate: string
  nextPM: string
  healthHistory: number[]
  resistanceHistory: ResistanceRecord[]
  maintenanceHistory: MaintenanceRecord[]
  recentAlerts: BatteryAlert[]
  recommendations?: Recommendation
}

// ==================== Mock Data (35 batteries) ====================
const generateBatteryData = (): BatteryUnit[] => {
  const locations = [
    'Data Center A - Row 1', 'Data Center A - Row 2', 'Data Center B - Row 1', 'Data Center B - Row 2',
    'Server Room A', 'Server Room B', 'Disaster Recovery Site', 'Main UPS Room'
  ]

  const upsNames = [
    'UPS-DC-01', 'UPS-DC-02', 'UPS-DC-03', 'UPS-DC-04', 'UPS-SG-01', 'UPS-SG-02', 'UPS-DR-01', 'UPS-DR-02'
  ]

  const manufacturers = ['Schneider Electric', 'Eaton', 'Vertiv', 'GS Yuasa', 'Exide', 'Enersys']
  const types = ['VRLA', 'Li-ion', 'Ni-Cd']

  const batteries: BatteryUnit[] = []

  for (let i = 1; i <= 35; i++) {
    const type = types[Math.floor(Math.random() * types.length)]
    const installDate = new Date()
    installDate.setMonth(installDate.getMonth() - Math.random() * 48)
    const installDateStr = installDate.toISOString().slice(0, 10)

    const ageYears = (new Date().getTime() - installDate.getTime()) / (1000 * 60 * 60 * 24 * 365)
    const baseHealth = Math.max(30, Math.min(98, 100 - ageYears * 12 + (Math.random() * 10 - 5)))
    const health = Math.round(baseHealth)

    const warrantyExpiry = new Date(installDate)
    warrantyExpiry.setFullYear(warrantyExpiry.getFullYear() + 3)

    const capacity = type === 'Li-ion' ? [50, 100, 150][Math.floor(Math.random() * 3)] : [40, 65, 100][Math.floor(Math.random() * 3)]

    const temperature = 22 + Math.random() * 15
    const voltage = type === 'Li-ion' ? 48 + (Math.random() * 4 - 2) : 12 + (Math.random() * 2 - 1)

    const cycleCount = Math.floor(ageYears * 365 * (Math.random() * 0.5 + 0.3))
    const designCycles = type === 'Li-ion' ? 3000 : type === 'VRLA' ? 800 : 1500

    const healthHistory = []
    for (let m = 0; m <= 6; m++) {
      healthHistory.push(Math.max(20, Math.min(100, health + (Math.random() * 10 - 5) - m * 1.5)))
    }

    const resistanceHistory = []
    const baseResistance = type === 'Li-ion' ? 15 : type === 'VRLA' ? 8 : 12
    for (let t = 0; t <= 4; t++) {
      const testDate = new Date()
      testDate.setMonth(testDate.getMonth() - t * 3)
      const resistance = baseResistance + (ageYears * 1.5) + (Math.random() * 3)
      resistanceHistory.push({
        date: testDate.toISOString().slice(0, 10),
        resistance: parseFloat(resistance.toFixed(1)),
        baseline: baseResistance,
        deviation: parseFloat(((resistance - baseResistance) / baseResistance * 100).toFixed(1)),
        status: resistance <= baseResistance * 1.1 ? 'Normal' : (resistance <= baseResistance * 1.2 ? 'Warning' : 'Critical')
      })
    }

    const maintenanceHistory = []
    const pmDates = [3, 6, 9, 12].map(months => {
      const date = new Date(installDate)
      date.setMonth(date.getMonth() + months)
      return date
    }).filter(d => d < new Date())

    pmDates.forEach((date, idx) => {
      maintenanceHistory.push({
        date: date.toISOString().slice(0, 10),
        type: 'Preventive',
        description: `Quarterly preventive maintenance - ${idx + 1}`,
        technician: ['John Tan', 'Mike Chen', 'Ahmad Ibrahim', 'Lim Wei Ming'][idx % 4],
        status: 'Completed'
      })
    })

    const recentAlerts = []
    if (health < 60) {
      recentAlerts.push({
        id: i * 100 + 1,
        date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: health < 50 ? 'High' : 'Medium',
        description: `Battery health below ${health}% - replacement recommended`,
        resolved: false
      })
    }
    if (temperature > 32) {
      recentAlerts.push({
        id: i * 100 + 2,
        date: new Date(Date.now() - Math.random() * 15 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: 'Medium',
        description: `High temperature detected (${temperature.toFixed(1)}°C) - check cooling`,
        resolved: temperature < 30
      })
    }

    let recommendations: Recommendation | undefined
    if (health < 50) {
      recommendations = {
        title: 'Urgent Replacement Required',
        type: 'error',
        description: `Battery health is critically low (${health}%). Immediate replacement recommended to prevent UPS failure.`
      }
    } else if (health < 70) {
      recommendations = {
        title: 'Replacement Recommended',
        type: 'warning',
        description: `Battery health is below optimal level (${health}%). Plan replacement within 90 days.`
      }
    }

    batteries.push({
      id: `BAT-${String(i).padStart(3, '0')}`,
      name: `Battery String ${String.fromCharCode(65 + Math.floor((i - 1) / 4))}-${((i - 1) % 4) + 1}`,
      type: type,
      ups: upsNames[(i - 1) % upsNames.length],
      location: locations[(i - 1) % locations.length],
      manufacturer: manufacturers[Math.floor(Math.random() * manufacturers.length)],
      capacity: capacity,
      health: health,
      voltage: parseFloat(voltage.toFixed(1)),
      nominalVoltage: type === 'Li-ion' ? 48 : 12,
      temperature: parseFloat(temperature.toFixed(1)),
      cycleCount: cycleCount,
      designCycles: designCycles,
      installDate: installDateStr,
      warrantyExpiry: warrantyExpiry.toISOString().slice(0, 10),
      lastTestDate: new Date().toISOString().slice(0, 10),
      nextPM: new Date(Date.now() + 60 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      healthHistory: healthHistory.reverse(),
      resistanceHistory: resistanceHistory.reverse(),
      maintenanceHistory: maintenanceHistory,
      recentAlerts: recentAlerts,
      recommendations: recommendations
    })
  }

  return batteries
}

const batteries = ref<BatteryUnit[]>(generateBatteryData())

// ==================== State ====================
const searchText = ref('')
const healthFilter = ref('')
const typeFilter = ref('')
const locationFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const degradationPeriod = ref('6')
const detailDialogVisible = ref(false)
const scheduleDialogVisible = ref(false)
const selectedBattery = ref<BatteryUnit | null>(null)

// Chart refs
let healthDistChart: echarts.ECharts | null = null
let degradationChart: echarts.ECharts | null = null
let tempChart: echarts.ECharts | null = null
let forecastChart: echarts.ECharts | null = null
let detailTrendChart: echarts.ECharts | null = null

const healthDistChartEl = ref<HTMLElement | null>(null)
const degradationChartEl = ref<HTMLElement | null>(null)
const tempChartEl = ref<HTMLElement | null>(null)
const forecastChartEl = ref<HTMLElement | null>(null)
const detailTrendChartEl = ref<HTMLElement | null>(null)

const scheduleForm = ref({
  batteryId: '',
  batteryName: '',
  replacementType: 'full',
  scheduleDate: '',
  priority: 'Medium',
  technician: '',
  estimatedCost: 5000,
  notes: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalBatteries = batteries.value.length
  const healthyBatteries = batteries.value.filter(b => b.health >= 80).length
  const warningBatteries = batteries.value.filter(b => b.health >= 50 && b.health < 80).length
  const criticalBatteries = batteries.value.filter(b => b.health < 50).length
  return { totalBatteries, healthyBatteries, warningBatteries, criticalBatteries }
})

const metrics = computed(() => {
  const avgHealth = Math.round(batteries.value.reduce((sum, b) => sum + b.health, 0) / batteries.value.length)
  const dueForReplacement = batteries.value.filter(b => b.health < 65).length
  const estimatedCost = dueForReplacement * 4500
  const avgAge = batteries.value.reduce((sum, b) => {
    const age = (new Date().getTime() - new Date(b.installDate).getTime()) / (1000 * 60 * 60 * 24 * 365)
    return sum + age
  }, 0) / batteries.value.length

  return {
    avgHealth,
    healthTrend: -2.5,
    dueForReplacement,
    estimatedCost,
    avgAge: parseFloat(avgAge.toFixed(1)),
    ageTrend: 1.2
  }
})

const uniqueLocations = computed(() => {
  return [...new Set(batteries.value.map(b => b.location))]
})

const filteredBatteries = computed(() => {
  let filtered = [...batteries.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(b =>
        b.id.toLowerCase().includes(search) ||
        b.name.toLowerCase().includes(search) ||
        b.ups.toLowerCase().includes(search)
    )
  }

  if (healthFilter.value) {
    if (healthFilter.value === 'healthy') filtered = filtered.filter(b => b.health >= 80)
    else if (healthFilter.value === 'warning') filtered = filtered.filter(b => b.health >= 50 && b.health < 80)
    else if (healthFilter.value === 'critical') filtered = filtered.filter(b => b.health < 50)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(b => b.type === typeFilter.value)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(b => b.location === locationFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredBatteries.value.length)

const paginatedBatteries = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredBatteries.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getHealthColor = (health: number): string => {
  if (health >= 80) return '#22c55e'
  if (health >= 50) return '#f59e0b'
  return '#ef4444'
}

const resetFilters = () => {
  searchText.value = ''
  healthFilter.value = ''
  typeFilter.value = ''
  locationFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initHealthDistChart = () => {
  if (!healthDistChartEl.value) return
  if (healthDistChart) {
    healthDistChart.dispose()
    healthDistChart = null
  }

  const healthy = batteries.value.filter(b => b.health >= 80).length
  const warning = batteries.value.filter(b => b.health >= 50 && b.health < 80).length
  const critical = batteries.value.filter(b => b.health < 50).length

  healthDistChart = echarts.init(healthDistChartEl.value)
  healthDistChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} batteries)' },
    legend: { orient: 'vertical', left: 'left', data: ['Healthy (≥80%)', 'Warning (50-79%)', 'Critical (<50%)'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: healthy, name: 'Healthy (≥80%)', itemStyle: { color: '#22c55e' } },
        { value: warning, name: 'Warning (50-79%)', itemStyle: { color: '#f59e0b' } },
        { value: critical, name: 'Critical (<50%)', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initDegradationChart = () => {
  if (!degradationChartEl.value) return
  if (degradationChart) {
    degradationChart.dispose()
    degradationChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  const avgHealthData = [94, 92, 89, 86, 82, 78]

  degradationChart = echarts.init(degradationChartEl.value)
  degradationChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 40, left: 50, right: 30, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Average Health (%)', min: 60, max: 100 },
    series: [{
      type: 'line',
      data: avgHealthData,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#3b82f6' },
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

  const data = batteries.value.map(b => [b.temperature, b.health])

  tempChart = echarts.init(tempChartEl.value)
  tempChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'value', name: 'Temperature (°C)', axisLabel: { formatter: '{value}°C' } },
    yAxis: { type: 'value', name: 'Battery Health (%)', min: 20, max: 100 },
    series: [{
      type: 'scatter',
      data: data,
      symbolSize: 10,
      itemStyle: {
        color: (params: any) => {
          const health = params.value[1]
          if (health >= 80) return '#22c55e'
          if (health >= 50) return '#f59e0b'
          return '#ef4444'
        }
      }
    }]
  })
}

const initForecastChart = () => {
  if (!forecastChartEl.value) return
  if (forecastChart) {
    forecastChart.dispose()
    forecastChart = null
  }

  const quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025']
  const replacements = [8, 12, 15, 18, 22, 25]

  forecastChart = echarts.init(forecastChartEl.value)
  forecastChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: quarters, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Number of Replacements' },
    series: [{
      type: 'bar',
      data: replacements,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: '#f59e0b',
        label: { show: true, position: 'top' }
      }
    }]
  })
}

const initDetailTrendChart = () => {
  if (!detailTrendChartEl.value || !selectedBattery.value) return
  if (detailTrendChart) {
    detailTrendChart.dispose()
    detailTrendChart = null
  }

  const months = ['6 months ago', '5 months', '4 months', '3 months', '2 months', 'Last month', 'Current']
  const healthData = selectedBattery.value.healthHistory

  detailTrendChart = echarts.init(detailTrendChartEl.value)
  detailTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Health (%)', min: 20, max: 100 },
    series: [{
      type: 'line',
      data: healthData,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const updateDegradationChart = () => {
  initDegradationChart()
}

const refreshCharts = () => {
  nextTick(() => {
    initHealthDistChart()
    initDegradationChart()
    initTempChart()
    initForecastChart()
  })
}

// ==================== Actions ====================
const viewBatteryDetail = (battery: BatteryUnit) => {
  selectedBattery.value = battery
  detailDialogVisible.value = true
  nextTick(() => initDetailTrendChart())
}

const viewHistory = (battery: BatteryUnit) => {
  viewBatteryDetail(battery)
}

const scheduleReplacement = (battery: BatteryUnit | null) => {
  if (battery) {
    scheduleForm.value = {
      batteryId: battery.id,
      batteryName: battery.name,
      replacementType: battery.health < 60 ? 'full' : 'partial',
      scheduleDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      priority: battery.health < 50 ? 'High' : (battery.health < 70 ? 'Medium' : 'Low'),
      technician: '',
      estimatedCost: battery.type === 'Li-ion' ? 8000 : 4500,
      notes: ''
    }
    scheduleDialogVisible.value = true
  } else {
    scheduleForm.value = {
      batteryId: '',
      batteryName: '',
      replacementType: 'full',
      scheduleDate: new Date().toISOString().slice(0, 10),
      priority: 'Medium',
      technician: '',
      estimatedCost: 5000,
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

  ElMessage.success(`Replacement scheduled for ${scheduleForm.value.batteryName}`)
  scheduleDialogVisible.value = false
}

const generateBatteryReport = (battery: BatteryUnit | null) => {
  if (!battery) return
  ElMessage.success(`Generating report for ${battery.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const viewAllBatteries = () => {
  ElMessage.info('Viewing all batteries')
}

const exportData = () => {
  ElMessage.success('Exporting battery maintenance data...')
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
  scheduleReplacement(null)
}

// 安全的窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (healthDistChart && !healthDistChart.isDisposed()) healthDistChart.resize()
    if (degradationChart && !degradationChart.isDisposed()) degradationChart.resize()
    if (tempChart && !tempChart.isDisposed()) tempChart.resize()
    if (forecastChart && !forecastChart.isDisposed()) forecastChart.resize()
    if (detailTrendChart && !detailTrendChart.isDisposed()) detailTrendChart.resize()
  }, 100)
}

// ==================== Watch ====================
watch([searchText, healthFilter, typeFilter, locationFilter], () => {
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
  const charts = [healthDistChart, degradationChart, tempChart, forecastChart, detailTrendChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.battery-maintenance-page {
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

/* Battery Detail */
.battery-detail {
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
  .filter-left .el-select,
  .filter-left .el-date-editor {
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