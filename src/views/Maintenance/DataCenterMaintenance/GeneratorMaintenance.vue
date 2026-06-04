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
          <span class="loading-title">Generator Maintenance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Diesel Generator Performance & Maintenance Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="generator-maintenance-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Cpu /></el-icon>
          Generator Maintenance
        </h1>
        <div class="page-subtitle">Monitor generator health, fuel status, and maintenance schedules</div>
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
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalGenerators }}</div>
          <div class="stat-label">Total Generators</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.healthyGenerators }}</div>
          <div class="stat-label">Healthy</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.warningGenerators }}</div>
          <div class="stat-label">Warning</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.criticalGenerators }}</div>
          <div class="stat-label">Critical</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Average Fuel Level</div>
        <div class="metric-value">{{ metrics.avgFuelLevel }}<span class="metric-unit">%</span></div>
        <div class="metric-trend" :class="metrics.fuelTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.fuelTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.fuelTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Runtime Hours</div>
        <div class="metric-value">{{ metrics.avgRuntime }}<span class="metric-unit">hrs</span></div>
        <div class="metric-sub">Since last overhaul</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Estimated Fuel Duration</div>
        <div class="metric-value">{{ metrics.fuelDuration }}<span class="metric-unit">hrs</span></div>
        <div class="metric-trend positive">At full load</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Monthly Test Compliance</div>
        <div class="metric-value">{{ metrics.testCompliance }}<span class="metric-unit">%</span></div>
        <div class="metric-trend" :class="metrics.testTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.testTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.testTrend) }}% vs target
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Generator Health Distribution</span>
          <span class="chart-subtitle">Current health status</span>
        </div>
        <div class="chart-container" ref="healthChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Fuel Level by Generator</span>
          <span class="chart-subtitle">Current fuel status</span>
        </div>
        <div class="chart-container" ref="fuelChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Load Test Performance</span>
          <span class="chart-subtitle">Last 6 months load test results</span>
        </div>
        <div class="chart-container" ref="loadTestChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Runtime Hours by Generator</span>
          <span class="chart-subtitle">Cumulative runtime hours</span>
        </div>
        <div class="chart-container" ref="runtimeChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by generator name or location..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Healthy" value="healthy" />
          <el-option label="Warning" value="warning" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="manufacturerFilter" placeholder="Manufacturer" clearable filterable style="width: 160px">
          <el-option v-for="m in uniqueManufacturers" :key="m" :label="m" :value="m" />
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

    <!-- Generators Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Generator Inventory</span>
        <el-button size="small" @click="viewAllGenerators">View All →</el-button>
      </div>
      <el-table :data="paginatedGenerators" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewGeneratorDetail">
        <el-table-column prop="id" label="Generator ID" width="120" />
        <el-table-column prop="name" label="Generator Name" min-width="160" />
        <el-table-column prop="manufacturer" label="Manufacturer" width="150" />
        <el-table-column prop="model" label="Model" width="120" />
        <el-table-column prop="location" label="Location" width="150" />
        <el-table-column prop="health" label="Health" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.health" :stroke-width="8" :color="getHealthColor(row.health)" />
          </template>
        </el-table-column>
        <el-table-column prop="fuelLevel" label="Fuel Level" width="130">
          <template #default="{ row }">
            <el-progress :percentage="row.fuelLevel" :stroke-width="8" :color="getFuelColor(row.fuelLevel)" />
          </template>
        </el-table-column>
        <el-table-column prop="runtime" label="Runtime (hrs)" width="110" />
        <el-table-column prop="lastTest" label="Last Test" width="120" />
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

    <!-- Generator Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedGenerator?.name" width="1000px" class="generator-dialog">
      <div v-if="selectedGenerator" class="generator-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedGenerator.health) }">
              {{ selectedGenerator.health }}%
            </div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedGenerator.fuelLevel }}%</div>
            <div class="detail-stat-label">Fuel Level</div>
            <div class="detail-stat-sub">{{ selectedGenerator.fuelVolume }} / {{ selectedGenerator.fuelCapacity }} L</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedGenerator.runtime }} hrs</div>
            <div class="detail-stat-label">Runtime Hours</div>
            <div class="detail-stat-sub">Since last overhaul: {{ selectedGenerator.runtimeSinceOverhaul }} hrs</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedGenerator.powerOutput }} kW</div>
            <div class="detail-stat-label">Power Output</div>
            <div class="detail-stat-sub">Rated: {{ selectedGenerator.ratedPower }} kW</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="Generator ID">{{ selectedGenerator.id }}</el-descriptions-item>
          <el-descriptions-item label="Name">{{ selectedGenerator.name }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedGenerator.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedGenerator.model }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedGenerator.location }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedGenerator.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Rated Power">{{ selectedGenerator.ratedPower }} kW</el-descriptions-item>
          <el-descriptions-item label="Fuel Type">{{ selectedGenerator.fuelType }}</el-descriptions-item>
          <el-descriptions-item label="Last Oil Change">{{ selectedGenerator.lastOilChange }}</el-descriptions-item>
          <el-descriptions-item label="Last Filter Change">{{ selectedGenerator.lastFilterChange }}</el-descriptions-item>
          <el-descriptions-item label="Last Battery Check">{{ selectedGenerator.lastBatteryCheck }}</el-descriptions-item>
          <el-descriptions-item label="Next Major Service">{{ selectedGenerator.nextMajorService }}</el-descriptions-item>
        </el-descriptions>

        <!-- Performance Chart -->
        <div class="detail-section">
          <div class="section-title">Performance Trends (Last 12 Months)</div>
          <div class="trend-chart" ref="performanceChartEl"></div>
        </div>

        <!-- Component Status -->
        <div class="detail-section">
          <div class="section-title">Component Status</div>
          <el-table :data="selectedGenerator.components" border stripe>
            <el-table-column prop="component" label="Component" width="200" />
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

        <!-- Load Test History -->
        <div class="detail-section">
          <div class="section-title">Load Test History</div>
          <el-table :data="selectedGenerator.loadTests" border stripe>
            <el-table-column prop="date" label="Date" width="120" />
            <el-table-column prop="loadLevel" label="Load Level (%)" width="120">
              <template #default="{ row }">
                <el-progress :percentage="row.loadLevel" :stroke-width="6" />
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="Duration (min)" width="120" />
            <el-table-column prop="voltageStability" label="Voltage Stability" width="140">
              <template #default="{ row }">
                <el-tag :type="row.voltageStability >= 95 ? 'success' : (row.voltageStability >= 90 ? 'warning' : 'danger')" size="small">
                  {{ row.voltageStability }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="frequencyStability" label="Frequency Stability" width="140">
              <template #default="{ row }">
                <el-tag :type="row.frequencyStability >= 95 ? 'success' : (row.frequencyStability >= 90 ? 'warning' : 'danger')" size="small">
                  {{ row.frequencyStability }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="result" label="Result" width="100">
              <template #default="{ row }">
                <el-tag :type="row.result === 'Passed' ? 'success' : 'danger'" size="small">{{ row.result }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Maintenance History -->
        <div class="detail-section">
          <div class="section-title">Maintenance History</div>
          <el-table :data="selectedGenerator.maintenanceHistory" border stripe>
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

        <!-- Alerts -->
        <div class="detail-section" v-if="selectedGenerator.alerts.length > 0">
          <div class="section-title">Recent Alerts</div>
          <el-table :data="selectedGenerator.alerts" border stripe>
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
        <div class="detail-section" v-if="selectedGenerator.recommendations">
          <div class="section-title">Maintenance Recommendations</div>
          <el-alert
              :title="selectedGenerator.recommendations.title"
              :type="selectedGenerator.recommendations.type"
              :description="selectedGenerator.recommendations.description"
              :closable="false"
              show-icon
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleMaintenance(selectedGenerator)">Schedule Maintenance</el-button>
        <el-button type="warning" @click="generateGeneratorReport(selectedGenerator)">Generate Report</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Maintenance Dialog -->
    <el-dialog v-model="scheduleDialogVisible" title="Schedule Generator Maintenance" width="550px">
      <el-form :model="scheduleForm" label-width="140px">
        <el-form-item label="Generator" required>
          <el-input :value="scheduleForm.generatorName" disabled />
        </el-form-item>
        <el-form-item label="Maintenance Type" required>
          <el-select v-model="scheduleForm.maintenanceType" placeholder="Select type" style="width: 100%">
            <el-option label="Preventive Maintenance" value="preventive" />
            <el-option label="Oil Change" value="oil" />
            <el-option label="Filter Replacement" value="filter" />
            <el-option label="Battery Replacement" value="battery" />
            <el-option label="Load Bank Test" value="loadtest" />
            <el-option label="Major Overhaul" value="overhaul" />
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
            <el-option label="John Tan - Generator Specialist" value="John Tan" />
            <el-option label="Mike Chen - Diesel Expert" value="Mike Chen" />
            <el-option label="Ahmad Ibrahim - Power Systems" value="Ahmad Ibrahim" />
            <el-option label="Lim Wei Ming - Field Engineer" value="Lim Wei Ming" />
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
  Cpu, Plus, Download, Refresh, CircleCheck, Warning, CircleClose,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading generator maintenance data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading generator data...',
  'Fetching fuel levels...',
  'Analyzing load test results...',
  'Loading maintenance schedules...',
  'Almost ready...'
]

// ==================== Types ====================
interface Component {
  component: string
  status: string
  value: string
  threshold: string
  lastCheck: string
}

interface LoadTest {
  date: string
  loadLevel: number
  duration: number
  voltageStability: number
  frequencyStability: number
  result: string
}

interface MaintenanceRecord {
  date: string
  type: string
  description: string
  technician: string
  status: string
}

interface GeneratorAlert {
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

interface GeneratorUnit {
  id: string
  name: string
  manufacturer: string
  model: string
  location: string
  health: number
  fuelLevel: number
  fuelVolume: number
  fuelCapacity: number
  runtime: number
  runtimeSinceOverhaul: number
  powerOutput: number
  ratedPower: number
  fuelType: string
  installDate: string
  lastOilChange: string
  lastFilterChange: string
  lastBatteryCheck: string
  nextMajorService: string
  performanceData: { date: string; powerOutput: number; fuelEfficiency: number }[]
  components: Component[]
  loadTests: LoadTest[]
  maintenanceHistory: MaintenanceRecord[]
  alerts: GeneratorAlert[]
  recommendations?: Recommendation
}

// ==================== Mock Data (25 generators) ====================
const generateGeneratorData = (): GeneratorUnit[] => {
  const locations = [
    'Main Generator Room', 'Backup Power Building A', 'Emergency Power Building B',
    'Data Center A - Ground Floor', 'Data Center B - Generator Yard', 'East Wing Generator Room'
  ]

  const manufacturers = ['Caterpillar', 'Cummins', 'MTU', 'Kohler', 'Generac', 'Mitsubishi']
  const models = ['3516B', 'QSK95', '4000 Series', 'KD Series', 'SD Series', 'MGS Series']
  const fuelTypes = ['Diesel', 'Natural Gas', 'Biodiesel']

  const generators: GeneratorUnit[] = []

  for (let i = 1; i <= 25; i++) {
    const manufacturer = manufacturers[Math.floor(Math.random() * manufacturers.length)]
    const installDate = new Date()
    installDate.setMonth(installDate.getMonth() - Math.random() * 120)
    const installDateStr = installDate.toISOString().slice(0, 10)

    const ageYears = (new Date().getTime() - installDate.getTime()) / (1000 * 60 * 60 * 24 * 365)
    const baseHealth = Math.max(55, Math.min(100, 100 - ageYears * 6 + (Math.random() * 10 - 5)))
    const health = Math.round(baseHealth)

    const fuelLevel = Math.max(20, Math.min(100, 60 + Math.random() * 40))
    const fuelCapacity = [2000, 3000, 5000, 10000][Math.floor(Math.random() * 4)]
    const fuelVolume = Math.round(fuelCapacity * fuelLevel / 100)

    const runtime = Math.floor(ageYears * 200 + Math.random() * 500)
    const runtimeSinceOverhaul = runtime % 5000
    const ratedPower = [500, 750, 1000, 1500, 2000][Math.floor(Math.random() * 5)]
    const powerOutput = Math.round(ratedPower * (0.5 + Math.random() * 0.4))

    // Generate performance data
    const performanceData = []
    for (let m = 0; m <= 11; m++) {
      const date = new Date()
      date.setMonth(date.getMonth() - m)
      performanceData.push({
        date: date.toISOString().slice(0, 7),
        powerOutput: Math.round(ratedPower * (0.6 + Math.random() * 0.35)),
        fuelEfficiency: parseFloat((35 + Math.random() * 10 + (ageYears * 0.5)).toFixed(1))
      })
    }

    // Generate components
    const components: Component[] = [
      { component: 'Engine', status: health > 80 ? 'Good' : (health > 60 ? 'Warning' : 'Critical'), value: `${Math.round(80 + Math.random() * 20)}% efficiency`, threshold: '>75% efficiency', lastCheck: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) },
      { component: 'Alternator', status: health > 85 ? 'Good' : 'Warning', value: `${Math.round(90 + Math.random() * 10)}% output`, threshold: '>85% output', lastCheck: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) },
      { component: 'Cooling System', status: fuelLevel > 30 ? 'Good' : 'Warning', value: `${Math.round(70 + Math.random() * 30)}% capacity`, threshold: 'Normal operation', lastCheck: new Date(Date.now() - Math.random() * 45 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) },
      { component: 'Battery System', status: Math.random() > 0.2 ? 'Good' : 'Warning', value: `${Math.round(11 + Math.random() * 2)}V`, threshold: '>12V', lastCheck: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) },
      { component: 'Fuel System', status: fuelLevel > 20 ? 'Good' : 'Critical', value: `${fuelLevel}% fuel`, threshold: '>20% fuel', lastCheck: new Date(Date.now() - Math.random() * 15 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) }
    ]

    // Generate load tests
    const loadTests: LoadTest[] = []
    for (let t = 0; t <= 5; t++) {
      const testDate = new Date()
      testDate.setMonth(testDate.getMonth() - t * 2)
      const loadLevel = [50, 75, 100][Math.floor(Math.random() * 3)]
      const voltageStability = Math.min(100, Math.max(85, 90 + Math.random() * 10 - (health / 100) * 5))
      const frequencyStability = Math.min(100, Math.max(85, 90 + Math.random() * 10 - (health / 100) * 5))
      loadTests.push({
        date: testDate.toISOString().slice(0, 10),
        loadLevel: loadLevel,
        duration: 60 + Math.random() * 120,
        voltageStability: parseFloat(voltageStability.toFixed(1)),
        frequencyStability: parseFloat(frequencyStability.toFixed(1)),
        result: voltageStability >= 90 && frequencyStability >= 90 ? 'Passed' : 'Failed'
      })
    }

    // Generate maintenance history
    const maintenanceHistory: MaintenanceRecord[] = []
    const maintenanceDates = [3, 6, 9, 12, 15, 18].map(months => {
      const date = new Date(installDate)
      date.setMonth(date.getMonth() + months)
      return date
    }).filter(d => d < new Date())

    const maintenanceTypes = ['Preventive', 'Oil Change', 'Filter Change', 'Battery Check']
    maintenanceDates.forEach((date, idx) => {
      maintenanceHistory.push({
        date: date.toISOString().slice(0, 10),
        type: maintenanceTypes[idx % maintenanceTypes.length],
        description: `Routine ${maintenanceTypes[idx % maintenanceTypes.length]} - full inspection`,
        technician: ['John Tan', 'Mike Chen', 'Ahmad Ibrahim', 'Lim Wei Ming'][idx % 4],
        status: 'Completed'
      })
    })

    // Generate alerts
    const alerts: GeneratorAlert[] = []
    if (fuelLevel < 25) {
      alerts.push({
        id: i * 100 + 1,
        date: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: fuelLevel < 15 ? 'High' : 'Medium',
        description: `Low fuel level: ${fuelLevel}% remaining`,
        resolved: false
      })
    }
    if (health < 65) {
      alerts.push({
        id: i * 100 + 2,
        date: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: health < 50 ? 'High' : 'Medium',
        description: `Generator health degraded to ${health}% - maintenance recommended`,
        resolved: false
      })
    }
    if (runtimeSinceOverhaul > 4000) {
      alerts.push({
        id: i * 100 + 3,
        date: new Date(Date.now() - Math.random() * 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        severity: 'Medium',
        description: `Major overhaul due in ${5000 - runtimeSinceOverhaul} hours`,
        resolved: false
      })
    }

    let recommendations: Recommendation | undefined
    if (health < 60) {
      recommendations = {
        title: 'Major Service Required',
        type: 'error',
        description: `Generator health is critically low (${health}%). Schedule major overhaul immediately.`
      }
    } else if (health < 80) {
      recommendations = {
        title: 'Preventive Maintenance Due',
        type: 'warning',
        description: `Generator health is below optimal level (${health}%). Schedule preventive maintenance soon.`
      }
    } else if (fuelLevel < 30) {
      recommendations = {
        title: 'Fuel Refill Recommended',
        type: 'warning',
        description: `Fuel level is low (${fuelLevel}%). Schedule fuel delivery to ensure emergency readiness.`
      }
    }

    generators.push({
      id: `GEN-${String(i).padStart(3, '0')}`,
      name: `Generator ${String.fromCharCode(64 + Math.ceil(i / 5))}${((i - 1) % 5) + 1}`,
      manufacturer: manufacturer,
      model: models[Math.floor(Math.random() * models.length)],
      location: locations[(i - 1) % locations.length],
      health: health,
      fuelLevel: fuelLevel,
      fuelVolume: fuelVolume,
      fuelCapacity: fuelCapacity,
      runtime: runtime,
      runtimeSinceOverhaul: runtimeSinceOverhaul,
      powerOutput: powerOutput,
      ratedPower: ratedPower,
      fuelType: fuelTypes[Math.floor(Math.random() * fuelTypes.length)],
      installDate: installDateStr,
      lastOilChange: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      lastFilterChange: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      lastBatteryCheck: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      nextMajorService: new Date(Date.now() + (5000 - runtimeSinceOverhaul) * 24 * 60 * 60 * 1000 / 200).toISOString().slice(0, 10),
      performanceData: performanceData.reverse(),
      components: components,
      loadTests: loadTests.reverse(),
      maintenanceHistory: maintenanceHistory,
      alerts: alerts,
      recommendations: recommendations
    })
  }

  return generators
}

const generators = ref<GeneratorUnit[]>(generateGeneratorData())

// ==================== State ====================
const searchText = ref('')
const statusFilter = ref('')
const manufacturerFilter = ref('')
const locationFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const scheduleDialogVisible = ref(false)
const selectedGenerator = ref<GeneratorUnit | null>(null)

// Chart refs
let healthChart: echarts.ECharts | null = null
let fuelChart: echarts.ECharts | null = null
let loadTestChart: echarts.ECharts | null = null
let runtimeChart: echarts.ECharts | null = null
let performanceChart: echarts.ECharts | null = null

const healthChartEl = ref<HTMLElement | null>(null)
const fuelChartEl = ref<HTMLElement | null>(null)
const loadTestChartEl = ref<HTMLElement | null>(null)
const runtimeChartEl = ref<HTMLElement | null>(null)
const performanceChartEl = ref<HTMLElement | null>(null)

const scheduleForm = ref({
  generatorId: '',
  generatorName: '',
  maintenanceType: 'preventive',
  scheduleDate: '',
  priority: 'Medium',
  technician: '',
  notes: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalGenerators = generators.value.length
  const healthyGenerators = generators.value.filter(g => g.health >= 85).length
  const warningGenerators = generators.value.filter(g => g.health >= 65 && g.health < 85).length
  const criticalGenerators = generators.value.filter(g => g.health < 65).length
  return { totalGenerators, healthyGenerators, warningGenerators, criticalGenerators }
})

const metrics = computed(() => {
  const avgFuelLevel = Math.round(generators.value.reduce((sum, g) => sum + g.fuelLevel, 0) / generators.value.length)
  const avgRuntime = Math.round(generators.value.reduce((sum, g) => sum + g.runtime, 0) / generators.value.length)
  const avgFuelConsumption = 250 // L/hr at full load
  const fuelDuration = Math.floor(avgFuelLevel * 100 / avgFuelConsumption)
  const testCompliance = Math.round(generators.value.filter(g => {
    const lastTest = g.loadTests[0]
    return lastTest && lastTest.result === 'Passed'
  }).length / generators.value.length * 100)

  return {
    avgFuelLevel,
    fuelTrend: -2.5,
    avgRuntime,
    fuelDuration,
    testCompliance,
    testTrend: 3.2
  }
})

const uniqueManufacturers = computed(() => {
  return [...new Set(generators.value.map(g => g.manufacturer))]
})

const uniqueLocations = computed(() => {
  return [...new Set(generators.value.map(g => g.location))]
})

const filteredGenerators = computed(() => {
  let filtered = [...generators.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(g =>
        g.id.toLowerCase().includes(search) ||
        g.name.toLowerCase().includes(search) ||
        g.location.toLowerCase().includes(search)
    )
  }

  if (statusFilter.value) {
    if (statusFilter.value === 'healthy') filtered = filtered.filter(g => g.health >= 85)
    else if (statusFilter.value === 'warning') filtered = filtered.filter(g => g.health >= 65 && g.health < 85)
    else if (statusFilter.value === 'critical') filtered = filtered.filter(g => g.health < 65)
  }

  if (manufacturerFilter.value) {
    filtered = filtered.filter(g => g.manufacturer === manufacturerFilter.value)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(g => g.location === locationFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredGenerators.value.length)

const paginatedGenerators = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredGenerators.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getHealthColor = (health: number): string => {
  if (health >= 85) return '#22c55e'
  if (health >= 65) return '#f59e0b'
  return '#ef4444'
}

const getFuelColor = (fuel: number): string => {
  if (fuel >= 50) return '#22c55e'
  if (fuel >= 25) return '#f59e0b'
  return '#ef4444'
}

const resetFilters = () => {
  searchText.value = ''
  statusFilter.value = ''
  manufacturerFilter.value = ''
  locationFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initHealthChart = () => {
  if (!healthChartEl.value) return
  if (healthChart) {
    healthChart.dispose()
    healthChart = null
  }

  const healthy = generators.value.filter(g => g.health >= 85).length
  const warning = generators.value.filter(g => g.health >= 65 && g.health < 85).length
  const critical = generators.value.filter(g => g.health < 65).length

  healthChart = echarts.init(healthChartEl.value)
  healthChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} units)' },
    legend: { orient: 'vertical', left: 'left', data: ['Healthy (≥85%)', 'Warning (65-84%)', 'Critical (<65%)'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: healthy, name: 'Healthy (≥85%)', itemStyle: { color: '#22c55e' } },
        { value: warning, name: 'Warning (65-84%)', itemStyle: { color: '#f59e0b' } },
        { value: critical, name: 'Critical (<65%)', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initFuelChart = () => {
  if (!fuelChartEl.value) return
  if (fuelChart) {
    fuelChart.dispose()
    fuelChart = null
  }

  const topGenerators = generators.value.slice(0, 8)
  const names = topGenerators.map(g => g.name)
  const fuelLevels = topGenerators.map(g => g.fuelLevel)

  fuelChart = echarts.init(fuelChartEl.value)
  fuelChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: '{b}<br/>Fuel Level: {c}%'
    },
    grid: { top: 30, left: 50, right: 20, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { rotate: 30, fontSize: 11 }
    },
    yAxis: {
      type: 'value',
      name: 'Fuel Level (%)',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      type: 'bar',
      data: fuelLevels,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 50) return '#22c55e'
          if (value >= 25) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: {
        show: true,
        position: 'top',
        formatter: (params: any) => {
          return params.value.toFixed(1) + '%'
        }
      }
    }]
  })
}

const initLoadTestChart = () => {
  if (!loadTestChartEl.value) return
  if (loadTestChart) {
    loadTestChart.dispose()
    loadTestChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  const passRates = [92, 94, 93, 95, 96, 95]

  loadTestChart = echarts.init(loadTestChartEl.value)
  loadTestChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Pass Rate (%)', min: 85, max: 100 },
    series: [{
      type: 'line',
      data: passRates,
      smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#22c55e' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initRuntimeChart = () => {
  if (!runtimeChartEl.value) return
  if (runtimeChart) {
    runtimeChart.dispose()
    runtimeChart = null
  }

  const topGenerators = generators.value.slice(0, 6)
  const names = topGenerators.map(g => g.name)
  const runtimes = topGenerators.map(g => g.runtime)

  runtimeChart = echarts.init(runtimeChartEl.value)
  runtimeChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Runtime Hours' },
    series: [{
      type: 'bar',
      data: runtimes,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c} hrs' }
    }]
  })
}

const initPerformanceChart = () => {
  if (!performanceChartEl.value || !selectedGenerator.value) return
  if (performanceChart) {
    performanceChart.dispose()
    performanceChart = null
  }

  const months = selectedGenerator.value.performanceData.map(d => d.date)
  const powerData = selectedGenerator.value.performanceData.map(d => d.powerOutput)
  const efficiencyData = selectedGenerator.value.performanceData.map(d => d.fuelEfficiency)

  performanceChart = echarts.init(performanceChartEl.value)
  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Power Output (kW)', 'Fuel Efficiency (L/kWh)'], bottom: 0 },
    grid: { top: 30, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: [
      { type: 'value', name: 'Power Output (kW)', position: 'left' },
      { type: 'value', name: 'Fuel Efficiency (L/kWh)', position: 'right' }
    ],
    series: [
      { name: 'Power Output (kW)', type: 'line', data: powerData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Fuel Efficiency (L/kWh)', type: 'line', data: efficiencyData, lineStyle: { color: '#f59e0b', width: 2 }, yAxisIndex: 1, symbol: 'circle' }
    ]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initHealthChart()
    initFuelChart()
    initLoadTestChart()
    initRuntimeChart()
  })
}

// ==================== Actions ====================
const viewGeneratorDetail = (generator: GeneratorUnit) => {
  selectedGenerator.value = generator
  detailDialogVisible.value = true
  nextTick(() => initPerformanceChart())
}

const viewHistory = (generator: GeneratorUnit) => {
  viewGeneratorDetail(generator)
}

const scheduleMaintenance = (generator: GeneratorUnit | null) => {
  if (generator) {
    scheduleForm.value = {
      generatorId: generator.id,
      generatorName: generator.name,
      maintenanceType: generator.health < 70 ? 'overhaul' : 'preventive',
      scheduleDate: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      priority: generator.health < 70 ? 'High' : (generator.health < 85 ? 'Medium' : 'Low'),
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

  ElMessage.success(`Maintenance scheduled for ${scheduleForm.value.generatorName}`)
  scheduleDialogVisible.value = false
}

const generateGeneratorReport = (generator: GeneratorUnit | null) => {
  if (!generator) return
  ElMessage.success(`Generating report for ${generator.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const viewAllGenerators = () => {
  ElMessage.info('Viewing all generators')
}

const exportData = () => {
  ElMessage.success('Exporting generator data...')
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
  scheduleForm.value = {
    generatorId: '',
    generatorName: '',
    maintenanceType: 'preventive',
    scheduleDate: new Date().toISOString().slice(0, 10),
    priority: 'Medium',
    technician: '',
    notes: ''
  }
  scheduleDialogVisible.value = true
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [healthChart, fuelChart, loadTestChart, runtimeChart, performanceChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, statusFilter, manufacturerFilter, locationFilter], () => {
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
  const charts = [healthChart, fuelChart, loadTestChart, runtimeChart, performanceChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.generator-maintenance-page {
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

/* Generator Detail */
.generator-detail {
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