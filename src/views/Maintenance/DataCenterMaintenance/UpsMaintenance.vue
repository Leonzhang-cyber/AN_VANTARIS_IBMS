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
          <span class="loading-title">UPS Maintenance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Uninterruptible Power Supply Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ups-maintenance-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Monitor /></el-icon>
          UPS Maintenance
        </h1>
        <div class="page-subtitle">Monitor and manage UPS systems health and maintenance activities</div>
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
          <div class="stat-value">{{ stats.totalUPS }}</div>
          <div class="stat-label">Total UPS Units</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.healthyUPS }}</div>
          <div class="stat-label">Healthy</div>
          <div class="stat-trend up">↑ {{ stats.healthRate }}% health rate</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.warningUPS }}</div>
          <div class="stat-label">Warning / Attention</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.criticalUPS }}</div>
          <div class="stat-label">Critical</div>
        </div>
      </div>
    </div>

    <!-- UPS Health Overview Chart -->
    <div class="chart-section">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">UPS Health Overview</span>
          <span class="chart-subtitle">Current status distribution</span>
        </div>
        <div class="chart-container" ref="healthChartEl"></div>
      </div>
      <div class="metrics-card">
        <div class="metrics-header">
          <span>Key Health Metrics</span>
          <el-tag type="primary" size="small">Real-time</el-tag>
        </div>
        <div class="metrics-list">
          <div class="metric-item">
            <div class="metric-info">
              <span class="metric-label">Average Load</span>
              <span class="metric-value">{{ avgLoad }}%</span>
            </div>
            <el-progress :percentage="avgLoad" :stroke-width="6" :color="avgLoad > 80 ? '#f59e0b' : '#22c55e'" />
          </div>
          <div class="metric-item">
            <div class="metric-info">
              <span class="metric-label">Average Battery Health</span>
              <span class="metric-value">{{ avgBatteryHealth }}%</span>
            </div>
            <el-progress :percentage="avgBatteryHealth" :stroke-width="6" :color="avgBatteryHealth < 70 ? '#ef4444' : '#22c55e'" />
          </div>
          <div class="metric-item">
            <div class="metric-info">
              <span class="metric-label">Average Efficiency</span>
              <span class="metric-value">{{ avgEfficiency }}%</span>
            </div>
            <el-progress :percentage="avgEfficiency" :stroke-width="6" :color="avgEfficiency < 85 ? '#f59e0b' : '#22c55e'" />
          </div>
          <div class="metric-item">
            <div class="metric-info">
              <span class="metric-label">Overall Health Score</span>
              <span class="metric-value">{{ overallHealthScore }}</span>
            </div>
            <el-progress :percentage="overallHealthScore" :stroke-width="6" :color="getScoreColor(overallHealthScore)" />
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by UPS name or location..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Healthy" value="healthy" />
          <el-option label="Warning" value="warning" />
          <el-option label="Critical" value="critical" />
        </el-select>
        <el-select v-model="vendorFilter" placeholder="Vendor" clearable filterable style="width: 150px">
          <el-option v-for="v in uniqueVendors" :key="v" :label="v" :value="v" />
        </el-select>
        <el-select v-model="locationFilter" placeholder="Location" clearable style="width: 150px">
          <el-option v-for="l in uniqueLocations" :key="l" :label="l" :value="l" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- UPS Cards Grid -->
    <div class="ups-grid">
      <div
          v-for="ups in paginatedUPS"
          :key="ups.id"
          class="ups-card"
          :class="ups.status"
          @click="viewUPSDetail(ups)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="ups-icon" :class="ups.status">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="ups-info">
            <div class="ups-name">{{ ups.name }}</div>
            <div class="ups-location">{{ ups.location }} | {{ ups.vendor }}</div>
          </div>
          <div class="status-badge" :class="ups.status">
            {{ getStatusText(ups.status) }}
          </div>
        </div>

        <!-- Health Gauge -->
        <div class="health-gauge">
          <div class="gauge-container">
            <div class="gauge-ring">
              <svg width="70" height="70" viewBox="0 0 70 70">
                <circle cx="35" cy="35" r="28" fill="none" stroke="#e2e8f0" stroke-width="5"/>
                <circle cx="35" cy="35" r="28" fill="none"
                        :stroke="getHealthColor(ups.healthScore)"
                        stroke-width="5"
                        :stroke-dasharray="`${ups.healthScore * 1.76}, 176`"
                        stroke-linecap="round"
                        transform="rotate(-90 35 35)"/>
              </svg>
              <div class="gauge-value">{{ ups.healthScore }}<span class="gauge-percent">%</span></div>
            </div>
          </div>
          <div class="health-stats">
            <div class="stat-row">
              <span>Load:</span>
              <span :class="ups.load > 80 ? 'metric-warning' : 'metric-good'">{{ ups.load }}%</span>
            </div>
            <div class="stat-row">
              <span>Battery:</span>
              <span :class="ups.batteryHealth < 70 ? 'metric-bad' : 'metric-good'">{{ ups.batteryHealth }}%</span>
            </div>
            <div class="stat-row">
              <span>Efficiency:</span>
              <span :class="ups.efficiency < 85 ? 'metric-warning' : 'metric-good'">{{ ups.efficiency }}%</span>
            </div>
          </div>
        </div>

        <!-- UPS Info -->
        <div class="ups-info-detail">
          <div class="info-item">
            <el-icon><Connection /></el-icon>
            <span>Model: {{ ups.model }}</span>
          </div>
          <div class="info-item">
            <el-icon><Timer /></el-icon>
            <span>Runtime: {{ ups.runtime }} min</span>
          </div>
          <div class="info-item">
            <el-icon><Calendar /></el-icon>
            <span>Last PM: {{ ups.lastPM }}</span>
          </div>
        </div>

        <!-- Recent Alerts -->
        <div class="alerts" v-if="ups.recentAlerts.length > 0">
          <div class="alerts-header">
            <el-icon><BellFilled /></el-icon>
            Recent Alerts ({{ ups.recentAlerts.length }})
          </div>
          <div class="alerts-list">
            <div v-for="alert in ups.recentAlerts.slice(0, 2)" :key="alert.id" class="alert-item">
              {{ alert.description }}
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-stats">
            <el-tag :type="getPMStatusType(ups.nextPMStatus)" size="small">
              {{ ups.nextPMStatus }}
            </el-tag>
            <span>Next: {{ ups.nextPMDate }}</span>
          </div>
          <el-button type="primary" size="small" @click.stop="viewUPSDetail(ups)">
            View Details →
          </el-button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredUPS.length === 0" class="empty-state">
        <el-empty description="No UPS units found">
          <el-button type="primary" @click="resetFilters">Reset Filters</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="filteredUPS.length > 0">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[6, 12, 18]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next"
          background
      />
    </div>

    <!-- UPS Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedUPS?.name" width="1000px" class="ups-dialog">
      <div v-if="selectedUPS" class="ups-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedUPS.healthScore) }">
              {{ selectedUPS.healthScore }}%
            </div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedUPS.load }}%</div>
            <div class="detail-stat-label">Current Load</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedUPS.batteryHealth }}%</div>
            <div class="detail-stat-label">Battery Health</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedUPS.efficiency }}%</div>
            <div class="detail-stat-label">Efficiency</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="UPS Name">{{ selectedUPS.name }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedUPS.model }}</el-descriptions-item>
          <el-descriptions-item label="Vendor">{{ selectedUPS.vendor }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedUPS.location }}</el-descriptions-item>
          <el-descriptions-item label="Capacity">{{ selectedUPS.capacity }} kVA</el-descriptions-item>
          <el-descriptions-item label="Runtime">{{ selectedUPS.runtime }} minutes</el-descriptions-item>
          <el-descriptions-item label="Installation Date">{{ selectedUPS.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Last PM">{{ selectedUPS.lastPM }}</el-descriptions-item>
          <el-descriptions-item label="Next PM">{{ selectedUPS.nextPMDate }}</el-descriptions-item>
        </el-descriptions>

        <!-- Performance Chart -->
        <div class="detail-section">
          <div class="section-title">Performance Trends (Last 6 Months)</div>
          <div class="trend-chart" ref="trendChartEl"></div>
        </div>

        <!-- Battery Health -->
        <div class="detail-section">
          <div class="section-title">Battery String Health</div>
          <el-table :data="selectedUPS.batteryStrings" border stripe>
            <el-table-column prop="stringId" label="String ID" width="120" />
            <el-table-column prop="voltage" label="Voltage (V)" width="120" />
            <el-table-column prop="temperature" label="Temperature (°C)" width="140" />
            <el-table-column prop="health" label="Health" width="200">
              <template #default="{ row }">
                <el-progress :percentage="row.health" :stroke-width="8" :color="getHealthColor(row.health)" />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.health >= 80 ? 'success' : (row.health >= 60 ? 'warning' : 'danger')" size="small">
                  {{ row.health >= 80 ? 'Good' : (row.health >= 60 ? 'Warning' : 'Critical') }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Maintenance History -->
        <div class="detail-section">
          <div class="section-title">Maintenance History</div>
          <el-table :data="selectedUPS.maintenanceHistory" border stripe>
            <el-table-column prop="date" label="Date" width="120" />
            <el-table-column prop="type" label="Type" width="120">
              <template #default="{ row }">
                <el-tag :type="row.type === 'Preventive' ? 'success' : 'warning'" size="small">{{ row.type }}</el-tag>
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
        <div class="detail-section" v-if="selectedUPS.recentAlerts.length > 0">
          <div class="section-title">Recent Alerts</div>
          <el-table :data="selectedUPS.recentAlerts" border stripe>
            <el-table-column prop="date" label="Date" width="180" />
            <el-table-column prop="severity" label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'High' ? 'danger' : (row.severity === 'Medium' ? 'warning' : 'info')" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="250" />
            <el-table-column prop="resolution" label="Resolution" width="150">
              <template #default="{ row }">
                <el-tag :type="row.resolved ? 'success' : 'warning'" size="small">
                  {{ row.resolved ? 'Resolved' : 'Open' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleMaintenance(selectedUPS)">Schedule Maintenance</el-button>
        <el-button type="warning" @click="generateUPSReport(selectedUPS)">Generate Report</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Maintenance Dialog -->
    <el-dialog v-model="scheduleDialogVisible" title="Schedule UPS Maintenance" width="500px">
      <el-form :model="scheduleForm" label-width="120px">
        <el-form-item label="Select UPS" required>
          <el-select v-model="scheduleForm.upsId" placeholder="Select UPS unit" filterable style="width: 100%">
            <el-option
                v-for="ups in slas.value"
                :key="ups.id"
                :label="ups.name"
                :value="ups.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Maintenance Type" required>
          <el-select v-model="scheduleForm.maintenanceType" placeholder="Select type" style="width: 100%">
            <el-option label="Preventive Maintenance" value="preventive" />
            <el-option label="Corrective Maintenance" value="corrective" />
            <el-option label="Battery Replacement" value="battery" />
            <el-option label="Firmware Update" value="firmware" />
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
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Technician">
          <el-input v-model="scheduleForm.technician" placeholder="Assigned technician" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="scheduleForm.notes" type="textarea" :rows="3" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSchedule">Schedule</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Monitor, Plus, Download, Refresh, Cpu, CircleCheck, Warning, CircleClose,
  Search, RefreshLeft, Connection, Timer, Calendar, BellFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading UPS maintenance data...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading UPS maintenance data...',
  'Fetching UPS health metrics...',
  'Loading battery statistics...',
  'Loading maintenance history...',
  'Almost ready...'
]

// ==================== Types ====================
interface BatteryString {
  stringId: string
  voltage: number
  temperature: number
  health: number
  status: string
}

interface MaintenanceRecord {
  date: string
  type: string
  description: string
  technician: string
  status: string
}

interface UPSAlert {
  id: number
  date: string
  severity: string
  description: string
  resolved: boolean
  resolution?: string
}

interface UPSUnit {
  id: number
  name: string
  model: string
  vendor: string
  location: string
  status: 'healthy' | 'warning' | 'critical'
  healthScore: number
  load: number
  batteryHealth: number
  efficiency: number
  runtime: number
  capacity: number
  installDate: string
  lastPM: string
  nextPMDate: string
  nextPMStatus: string
  recentAlerts: UPSAlert[]
  batteryStrings: BatteryString[]
  maintenanceHistory: MaintenanceRecord[]
}

// ==================== Mock Data ====================
const slas = ref<UPSUnit[]>([
  {
    id: 1, name: 'UPS-DC-01', model: 'Smart-UPS 5000', vendor: 'Schneider Electric', location: 'Data Center A - Row 1',
    status: 'healthy', healthScore: 98, load: 45, batteryHealth: 92, efficiency: 96, runtime: 35,
    capacity: 5000, installDate: '2023-01-15', lastPM: '2024-05-10', nextPMDate: '2024-08-10', nextPMStatus: 'Scheduled',
    recentAlerts: [],
    batteryStrings: [
      { stringId: 'String A', voltage: 432, temperature: 25, health: 95, status: 'Good' },
      { stringId: 'String B', voltage: 428, temperature: 26, health: 92, status: 'Good' }
    ],
    maintenanceHistory: [
      { date: '2024-05-10', type: 'Preventive', description: 'Quarterly preventive maintenance', technician: 'John Tan', status: 'Completed' },
      { date: '2024-02-05', type: 'Preventive', description: 'Battery health check', technician: 'Mike Chen', status: 'Completed' }
    ]
  },
  {
    id: 2, name: 'UPS-DC-02', model: 'Galaxy VX 500', vendor: 'Schneider Electric', location: 'Data Center A - Row 2',
    status: 'healthy', healthScore: 96, load: 52, batteryHealth: 90, efficiency: 94, runtime: 32,
    capacity: 5000, installDate: '2023-02-20', lastPM: '2024-05-08', nextPMDate: '2024-08-08', nextPMStatus: 'Scheduled',
    recentAlerts: [],
    batteryStrings: [
      { stringId: 'String A', voltage: 430, temperature: 26, health: 93, status: 'Good' },
      { stringId: 'String B', voltage: 425, temperature: 27, health: 89, status: 'Good' }
    ],
    maintenanceHistory: [
      { date: '2024-05-08', type: 'Preventive', description: 'Quarterly preventive maintenance', technician: 'John Tan', status: 'Completed' }
    ]
  },
  {
    id: 3, name: 'UPS-DC-03', model: '93E 400kVA', vendor: 'Eaton Singapore', location: 'Data Center B - Row 1',
    status: 'warning', healthScore: 82, load: 75, batteryHealth: 72, efficiency: 88, runtime: 18,
    capacity: 4000, installDate: '2022-06-10', lastPM: '2024-04-15', nextPMDate: '2024-07-15', nextPMStatus: 'Upcoming',
    recentAlerts: [
      { id: 1, date: '2024-05-20 14:30', severity: 'Medium', description: 'Battery temperature elevated above threshold', resolved: false }
    ],
    batteryStrings: [
      { stringId: 'String A', voltage: 410, temperature: 32, health: 75, status: 'Warning' },
      { stringId: 'String B', voltage: 408, temperature: 33, health: 70, status: 'Warning' }
    ],
    maintenanceHistory: [
      { date: '2024-04-15', type: 'Preventive', description: 'Routine maintenance and battery check', technician: 'Ahmad Ibrahim', status: 'Completed' },
      { date: '2024-01-20', type: 'Corrective', description: 'Fan replacement', technician: 'Lim Wei Ming', status: 'Completed' }
    ]
  },
  {
    id: 4, name: 'UPS-DC-04', model: '93PM 200kW', vendor: 'Eaton Singapore', location: 'Data Center B - Row 2',
    status: 'critical', healthScore: 58, load: 85, batteryHealth: 45, efficiency: 82, runtime: 8,
    capacity: 2000, installDate: '2021-08-15', lastPM: '2024-03-10', nextPMDate: '2024-06-10', nextPMStatus: 'Overdue',
    recentAlerts: [
      { id: 2, date: '2024-05-22 09:15', severity: 'High', description: 'Battery string B voltage low - immediate attention required', resolved: false },
      { id: 3, date: '2024-05-18 16:45', severity: 'Medium', description: 'Battery health below 50%', resolved: false }
    ],
    batteryStrings: [
      { stringId: 'String A', voltage: 395, temperature: 35, health: 55, status: 'Critical' },
      { stringId: 'String B', voltage: 380, temperature: 36, health: 40, status: 'Critical' }
    ],
    maintenanceHistory: [
      { date: '2024-03-10', type: 'Preventive', description: 'Routine maintenance', technician: 'Mike Chen', status: 'Completed' },
      { date: '2023-12-05', type: 'Corrective', description: 'Control board replacement', technician: 'John Tan', status: 'Completed' }
    ]
  },
  {
    id: 5, name: 'UPS-SG-01', model: 'Tricon 500kVA', vendor: 'Vertiv Singapore', location: 'Server Room A',
    status: 'healthy', healthScore: 94, load: 48, batteryHealth: 88, efficiency: 93, runtime: 30,
    capacity: 5000, installDate: '2023-09-01', lastPM: '2024-05-05', nextPMDate: '2024-08-05', nextPMStatus: 'Scheduled',
    recentAlerts: [],
    batteryStrings: [
      { stringId: 'String A', voltage: 428, temperature: 24, health: 90, status: 'Good' },
      { stringId: 'String B', voltage: 425, temperature: 25, health: 86, status: 'Good' }
    ],
    maintenanceHistory: [
      { date: '2024-05-05', type: 'Preventive', description: 'Quarterly maintenance', technician: 'Lim Wei Ming', status: 'Completed' }
    ]
  },
  {
    id: 6, name: 'UPS-SG-02', model: 'PowerScale 200kVA', vendor: 'Schneider Electric', location: 'Server Room B',
    status: 'warning', healthScore: 78, load: 65, batteryHealth: 68, efficiency: 86, runtime: 22,
    capacity: 2000, installDate: '2022-11-20', lastPM: '2024-04-20', nextPMDate: '2024-07-20', nextPMStatus: 'Upcoming',
    recentAlerts: [
      { id: 4, date: '2024-05-19 10:00', severity: 'Low', description: 'Load imbalance detected', resolved: true, resolution: 'Load redistributed' }
    ],
    batteryStrings: [
      { stringId: 'String A', voltage: 415, temperature: 30, health: 72, status: 'Warning' },
      { stringId: 'String B', voltage: 412, temperature: 31, health: 65, status: 'Warning' }
    ],
    maintenanceHistory: [
      { date: '2024-04-20', type: 'Preventive', description: 'Preventive maintenance', technician: 'Sarah Koh', status: 'Completed' }
    ]
  },
  {
    id: 7, name: 'UPS-DR-01', model: '93PM 100kW', vendor: 'Eaton Singapore', location: 'Disaster Recovery Site',
    status: 'healthy', healthScore: 95, load: 35, batteryHealth: 94, efficiency: 95, runtime: 40,
    capacity: 1000, installDate: '2023-03-10', lastPM: '2024-04-28', nextPMDate: '2024-07-28', nextPMStatus: 'Scheduled',
    recentAlerts: [],
    batteryStrings: [
      { stringId: 'String A', voltage: 430, temperature: 24, health: 96, status: 'Good' },
      { stringId: 'String B', voltage: 428, temperature: 25, health: 92, status: 'Good' }
    ],
    maintenanceHistory: [
      { date: '2024-04-28', type: 'Preventive', description: 'Scheduled preventive maintenance', technician: 'Ahmad Ibrahim', status: 'Completed' }
    ]
  },
  {
    id: 8, name: 'UPS-DR-02', model: 'Galaxy VM 160kVA', vendor: 'Schneider Electric', location: 'Disaster Recovery Site',
    status: 'healthy', healthScore: 93, load: 42, batteryHealth: 87, efficiency: 92, runtime: 28,
    capacity: 1600, installDate: '2023-04-05', lastPM: '2024-05-01', nextPMDate: '2024-08-01', nextPMStatus: 'Scheduled',
    recentAlerts: [],
    batteryStrings: [
      { stringId: 'String A', voltage: 426, temperature: 26, health: 89, status: 'Good' },
      { stringId: 'String B', voltage: 422, temperature: 27, health: 85, status: 'Good' }
    ],
    maintenanceHistory: [
      { date: '2024-05-01', type: 'Preventive', description: 'Routine maintenance', technician: 'John Tan', status: 'Completed' }
    ]
  }
])

// ==================== State ====================
const searchText = ref('')
const statusFilter = ref('')
const vendorFilter = ref('')
const locationFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(6)
const detailDialogVisible = ref(false)
const scheduleDialogVisible = ref(false)
const selectedUPS = ref<UPSUnit | null>(null)

// Chart refs
let healthChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
const healthChartEl = ref<HTMLElement | null>(null)
const trendChartEl = ref<HTMLElement | null>(null)

const scheduleForm = ref({
  upsId: null as number | null,
  maintenanceType: '',
  scheduleDate: '',
  priority: 'Medium',
  technician: '',
  notes: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalUPS = slas.value.length
  const healthyUPS = slas.value.filter(u => u.status === 'healthy').length
  const warningUPS = slas.value.filter(u => u.status === 'warning').length
  const criticalUPS = slas.value.filter(u => u.status === 'critical').length
  const healthRate = Math.round((healthyUPS / totalUPS) * 100)
  return { totalUPS, healthyUPS, warningUPS, criticalUPS, healthRate }
})

const avgLoad = computed(() => {
  return Math.round(slas.value.reduce((sum, u) => sum + u.load, 0) / slas.value.length)
})

const avgBatteryHealth = computed(() => {
  return Math.round(slas.value.reduce((sum, u) => sum + u.batteryHealth, 0) / slas.value.length)
})

const avgEfficiency = computed(() => {
  return Math.round(slas.value.reduce((sum, u) => sum + u.efficiency, 0) / slas.value.length)
})

const overallHealthScore = computed(() => {
  return Math.round(slas.value.reduce((sum, u) => sum + u.healthScore, 0) / slas.value.length)
})

const uniqueVendors = computed(() => {
  return [...new Set(slas.value.map(u => u.vendor))]
})

const uniqueLocations = computed(() => {
  return [...new Set(slas.value.map(u => u.location))]
})

const filteredUPS = computed(() => {
  let filtered = [...slas.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(u =>
        u.name.toLowerCase().includes(search) ||
        u.location.toLowerCase().includes(search) ||
        u.model.toLowerCase().includes(search)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(u => u.status === statusFilter.value)
  }

  if (vendorFilter.value) {
    filtered = filtered.filter(u => u.vendor === vendorFilter.value)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(u => u.location === locationFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredUPS.value.length)

const paginatedUPS = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredUPS.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getStatusText = (status: string): string => {
  const map: Record<string, string> = { healthy: 'Healthy', warning: 'Warning', critical: 'Critical' }
  return map[status] || status
}

const getHealthColor = (health: number): string => {
  if (health >= 80) return '#22c55e'
  if (health >= 60) return '#f59e0b'
  return '#ef4444'
}

const getScoreColor = (score: number): string => {
  if (score >= 80) return '#22c55e'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

const getPMStatusType = (status: string): string => {
  const map: Record<string, string> = { Scheduled: 'primary', Upcoming: 'warning', Overdue: 'danger' }
  return map[status] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  statusFilter.value = ''
  vendorFilter.value = ''
  locationFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initHealthChart = () => {
  if (!healthChartEl.value) return
  if (healthChart) healthChart.dispose()

  const statusCount = {
    healthy: slas.value.filter(u => u.status === 'healthy').length,
    warning: slas.value.filter(u => u.status === 'warning').length,
    critical: slas.value.filter(u => u.status === 'critical').length
  }

  healthChart = echarts.init(healthChartEl.value)
  healthChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} units)' },
    legend: { orient: 'vertical', left: 'left', data: ['Healthy', 'Warning', 'Critical'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: statusCount.healthy, name: 'Healthy', itemStyle: { color: '#22c55e' } },
        { value: statusCount.warning, name: 'Warning', itemStyle: { color: '#f59e0b' } },
        { value: statusCount.critical, name: 'Critical', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) trendChart.dispose()

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  const loadData = [48, 52, 55, 50, 48, selectedUPS.value?.load || 45]
  const batteryData = [92, 90, 88, 85, 82, selectedUPS.value?.batteryHealth || 90]
  const efficiencyData = [94, 93, 92, 91, 90, selectedUPS.value?.efficiency || 93]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Load %', 'Battery Health %', 'Efficiency %'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Percentage (%)', min: 40, max: 100 },
    series: [
      { name: 'Load %', type: 'line', data: loadData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Battery Health %', type: 'line', data: batteryData, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle' },
      { name: 'Efficiency %', type: 'line', data: efficiencyData, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'circle' }
    ]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initHealthChart()
  })
}

// ==================== Actions ====================
const viewUPSDetail = (ups: UPSUnit) => {
  selectedUPS.value = ups
  detailDialogVisible.value = true
  nextTick(() => initTrendChart())
}

const openScheduleDialog = () => {
  scheduleForm.value = {
    upsId: null,
    maintenanceType: '',
    scheduleDate: '',
    priority: 'Medium',
    technician: '',
    notes: ''
  }
  scheduleDialogVisible.value = true
}

const scheduleMaintenance = (ups: UPSUnit | null) => {
  if (ups) {
    scheduleForm.value.upsId = ups.id
    scheduleDialogVisible.value = true
  } else {
    openScheduleDialog()
  }
}

const saveSchedule = () => {
  if (!scheduleForm.value.upsId) {
    ElMessage.warning('Please select a UPS unit')
    return
  }
  if (!scheduleForm.value.maintenanceType) {
    ElMessage.warning('Please select maintenance type')
    return
  }
  if (!scheduleForm.value.scheduleDate) {
    ElMessage.warning('Please select schedule date')
    return
  }

  ElMessage.success('Maintenance scheduled successfully')
  scheduleDialogVisible.value = false
}

const generateUPSReport = (ups: UPSUnit | null) => {
  if (!ups) return
  ElMessage.success(`Generating report for ${ups.name}...`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Exporting UPS maintenance data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  refreshCharts()
  ElMessage.success('Data refreshed')
}

// ==================== Watch ====================
watch([searchText, statusFilter, vendorFilter, locationFilter], () => {
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
  window.addEventListener('resize', () => {
    healthChart?.resize()
    trendChart?.resize()
  })
})
</script>

<style scoped>
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

/* ==================== Loading Screen ==================== */
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

/* ==================== Main Page ==================== */
.ups-maintenance-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
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

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.up { color: #22c55e; }

/* Chart Section */
.chart-section {
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

.metrics-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.metrics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  color: #1e293b;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.metric-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 13px;
  color: #64748b;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
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

/* UPS Grid */
.ups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.ups-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.ups-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.ups-card.healthy { border-left: 4px solid #22c55e; }
.ups-card.warning { border-left: 4px solid #f59e0b; }
.ups-card.critical { border-left: 4px solid #ef4444; }

.card-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid #eef2f8;
}

.ups-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.ups-icon.healthy { background: #dcfce7; color: #22c55e; }
.ups-icon.warning { background: #fef3c7; color: #f59e0b; }
.ups-icon.critical { background: #fee2e2; color: #ef4444; }

.ups-info {
  flex: 1;
}

.ups-name {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 4px;
}

.ups-location {
  font-size: 12px;
  color: #64748b;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.healthy { background: #dcfce7; color: #16a34a; }
.status-badge.warning { background: #fef3c7; color: #d97706; }
.status-badge.critical { background: #fee2e2; color: #dc2626; }

/* Health Gauge */
.health-gauge {
  padding: 16px 20px;
  display: flex;
  gap: 20px;
  border-bottom: 1px solid #eef2f8;
  background: #f8fafc;
}

.gauge-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.gauge-ring {
  position: relative;
  width: 70px;
  height: 70px;
}

.gauge-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 18px;
  font-weight: 700;
}

.gauge-percent {
  font-size: 9px;
}

.health-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.stat-row span:first-child {
  color: #64748b;
}

.metric-good { color: #22c55e; font-weight: 600; }
.metric-warning { color: #f59e0b; font-weight: 600; }
.metric-bad { color: #ef4444; font-weight: 600; }

/* UPS Info Detail */
.ups-info-detail {
  padding: 12px 20px;
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  border-bottom: 1px solid #eef2f8;
  font-size: 12px;
  color: #64748b;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Alerts */
.alerts {
  padding: 12px 20px;
  border-bottom: 1px solid #eef2f8;
  background: #fef2f2;
}

.alerts-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 8px;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alert-item {
  font-size: 11px;
  color: #dc2626;
}

/* Card Footer */
.card-footer {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-stats {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 11px;
  color: #64748b;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: flex-end;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 60px;
  background: white;
  border-radius: 20px;
  text-align: center;
}

/* Dialog */
.ups-dialog :deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}

.ups-detail {
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

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .chart-section {
    flex-direction: column;
  }
  .ups-grid {
    grid-template-columns: 1fr;
  }
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
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
  max-height: 550px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>