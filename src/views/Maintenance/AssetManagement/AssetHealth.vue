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
          <span class="loading-title">Asset Health</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Health Monitoring System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="asset-health-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><DataBoard /></el-icon>
          Asset Health
        </h1>
        <div class="page-subtitle">Real-time health monitoring and predictive analytics</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runHealthCheck">
          <el-icon><Refresh /></el-icon> Run Health Check
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Health Overview Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.healthy }}</div>
          <div class="stat-label">Healthy (80-100%)</div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="(stats.healthy / stats.total) * 100" :stroke-width="6" color="#22c55e" :show-text="false" />
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.warning }}</div>
          <div class="stat-label">Warning (60-79%)</div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="(stats.warning / stats.total) * 100" :stroke-width="6" color="#f59e0b" :show-text="false" />
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon critical">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.critical }}</div>
          <div class="stat-label">Critical (< 60%)</div>
        </div>
        <div class="stat-progress">
          <el-progress :percentage="(stats.critical / stats.total) * 100" :stroke-width="6" color="#ef4444" :show-text="false" />
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgHealth }}<span class="unit">%</span></div>
          <div class="stat-label">Average Health</div>
        </div>
        <div class="stat-trend" :class="stats.trendDirection">
          <el-icon><Top /></el-icon> {{ stats.trend }}% from last month
        </div>
      </div>
    </div>

    <!-- Health Gauge Chart Section -->
    <div class="chart-section">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Health Score Distribution</span>
          <el-radio-group v-model="chartType" size="small">
            <el-radio-button label="gauge">Gauge</el-radio-button>
            <el-radio-button label="bar">Bar Chart</el-radio-button>
          </el-radio-group>
        </div>
        <div class="chart-container" ref="chartContainer"></div>
      </div>
      <div class="health-summary-card">
        <div class="summary-header">
          <span>Health Summary</span>
          <el-tag type="primary" size="small">Last updated: today</el-tag>
        </div>
        <div class="summary-stats">
          <div class="summary-item">
            <div class="summary-label">Overall Health Index</div>
            <div class="summary-value" :style="{ color: getOverallHealthColor(stats.avgHealth) }">
              {{ stats.avgHealth }}%
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-label">Assets Needing Attention</div>
            <div class="summary-value critical">{{ stats.critical + stats.warning }}</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">Predicted Failures (30d)</div>
            <div class="summary-value warning">{{ stats.predictedFailures }}</div>
          </div>
        </div>
        <div class="health-tips">
          <div class="tips-title">AI Recommendations</div>
          <ul class="tips-list">
            <li v-for="tip in healthTips" :key="tip.id">
              <el-icon><InfoFilled /></el-icon>
              {{ tip.message }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by asset name..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 130px">
          <el-option label="All Categories" value="" />
          <el-option label="UPS" value="UPS" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Generator" value="Generator" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="Transformer" value="Transformer" />
          <el-option label="HVAC" value="HVAC" />
        </el-select>
        <el-select v-model="healthFilter" placeholder="Health Status" clearable style="width: 130px">
          <el-option label="All" value="" />
          <el-option label="Healthy (80-100%)" value="healthy" />
          <el-option label="Warning (60-79%)" value="warning" />
          <el-option label="Critical (<60%)" value="critical" />
        </el-select>
        <el-select v-model="locationFilter" placeholder="Location" clearable style="width: 150px">
          <el-option label="Server Room A" value="Server Room A" />
          <el-option label="Server Room B" value="Server Room B" />
          <el-option label="Server Room C" value="Server Room C" />
          <el-option label="Data Center" value="Data Center" />
          <el-option label="Generator Room" value="Generator Room" />
          <el-option label="Chiller Plant" value="Chiller Plant" />
          <el-option label="Electrical Room" value="Electrical Room" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Showing {{ filteredAssets.length }} assets</span>
      </div>
    </div>

    <!-- Asset Health Cards Grid -->
    <div class="health-grid">
      <div
          v-for="asset in paginatedAssets"
          :key="asset.id"
          class="health-card"
          :class="getHealthLevel(asset.healthScore)"
          @click="viewAssetDetail(asset)"
      >
        <!-- Card Glow Border -->
        <div class="card-glow" :class="getHealthLevel(asset.healthScore)"></div>

        <div class="card-header">
          <div class="asset-icon" :class="asset.category.toLowerCase()">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="asset-info">
            <div class="asset-name">{{ asset.name }}</div>
            <div class="asset-category">{{ asset.category }}</div>
          </div>
          <div class="health-badge" :class="getHealthLevel(asset.healthScore)">
            {{ asset.healthScore }}%
          </div>
        </div>

        <div class="health-gauge">
          <div class="gauge-track">
            <div class="gauge-fill" :style="{ width: asset.healthScore + '%', background: getHealthColor(asset.healthScore) }"></div>
          </div>
          <div class="gauge-labels">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        <div class="asset-metrics">
          <div class="metric">
            <span class="metric-label">Remaining Life</span>
            <span class="metric-value">{{ asset.remainingLife }} years</span>
          </div>
          <div class="metric">
            <span class="metric-label">MTBF</span>
            <span class="metric-value">{{ asset.mtbf }} hrs</span>
          </div>
          <div class="metric">
            <span class="metric-label">MTTR</span>
            <span class="metric-value">{{ asset.mttr }} hrs</span>
          </div>
          <div class="metric">
            <span class="metric-label">Last Maintenance</span>
            <span class="metric-value">{{ formatDate(asset.lastMaintenance) }}</span>
          </div>
        </div>

        <div class="trend-indicator" :class="asset.healthTrend">
          <el-icon><Top v-if="asset.healthTrend === 'up'" /><Bottom v-else-if="asset.healthTrend === 'down'" /><Right v-else /></el-icon>
          {{ asset.healthTrend === 'up' ? 'Improving' : (asset.healthTrend === 'down' ? 'Declining' : 'Stable') }}
        </div>

        <div class="card-footer">
          <div class="footer-stats">
            <span><el-icon><Clock /></el-icon> {{ asset.uptime }}% uptime</span>
            <span><el-icon><Warning /></el-icon> {{ asset.activeAlerts }} alerts</span>
          </div>
          <el-button type="primary" link size="small" @click.stop="viewAssetDetail(asset)">
            Details →
          </el-button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredAssets.length === 0" class="empty-state">
        <el-empty description="No assets found">
          <el-button type="primary" @click="resetFilters">Reset Filters</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="filteredAssets.length > 0">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[9, 18, 27]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next"
          background
      />
    </div>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAsset?.name" width="850px" class="health-dialog">
      <div v-if="selectedAsset" class="asset-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedAsset.healthScore) }">
              {{ selectedAsset.healthScore }}%
            </div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.remainingLife }} yrs</div>
            <div class="detail-stat-label">Remaining Life</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.mtbf }} hrs</div>
            <div class="detail-stat-label">MTBF</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.mttr }} hrs</div>
            <div class="detail-stat-label">MTTR</div>
          </div>
        </div>

        <!-- Health History Chart -->
        <div class="detail-section">
          <div class="section-title">Health Score History (12 months)</div>
          <div class="history-chart" ref="historyChartContainer"></div>
        </div>

        <!-- Key Metrics Table -->
        <div class="detail-section">
          <div class="section-title">Key Performance Indicators</div>
          <el-table :data="selectedAsset.kpis" border stripe size="small">
            <el-table-column prop="metric" label="Metric" width="200" />
            <el-table-column prop="current" label="Current Value" width="150">
              <template #default="{ row }">
                <span :class="getKPIClass(row.current, row.threshold)">{{ row.current }} {{ row.unit }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="threshold" label="Threshold" width="150">
              <template #default="{ row }">{{ row.threshold }} {{ row.unit }}</template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'normal' ? 'success' : (row.status === 'warning' ? 'warning' : 'danger')" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="trend" label="Trend" width="80">
              <template #default="{ row }">
                <span :class="row.trend === 'up' ? 'trend-up' : (row.trend === 'down' ? 'trend-down' : 'trend-stable')">
                  {{ row.trend === 'up' ? '↑' : (row.trend === 'down' ? '↓' : '→') }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Recommendations -->
        <div class="detail-section">
          <div class="section-title">Maintenance Recommendations</div>
          <div class="recommendations-list">
            <div v-for="(rec, idx) in selectedAsset.recommendations" :key="idx" class="recommendation-item" :class="rec.priority">
              <div class="rec-icon">
                <el-icon><WarningFilled /></el-icon>
              </div>
              <div class="rec-content">
                <div class="rec-title">{{ rec.title }}</div>
                <div class="rec-description">{{ rec.description }}</div>
                <div class="rec-deadline">Due by: {{ rec.dueDate }}</div>
              </div>
              <el-button type="primary" size="small">Schedule</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataBoard, Refresh, Download, CircleCheck, Warning, CircleClose,
  TrendCharts, Top, Bottom, Right, Cpu, Clock, InfoFilled, Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading health data...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading health data...',
  'Analyzing metrics...',
  'Calculating health scores...',
  'Almost ready...'
]

// ==================== Types ====================
interface KPI {
  metric: string
  current: number
  threshold: number
  unit: string
  status: 'normal' | 'warning' | 'critical'
  trend: 'up' | 'down' | 'stable'
}

interface Recommendation {
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  dueDate: string
}

interface AssetHealth {
  id: number
  name: string
  category: string
  location: string
  healthScore: number
  healthTrend: 'up' | 'down' | 'stable'
  remainingLife: number
  mtbf: number
  mttr: number
  uptime: number
  activeAlerts: number
  lastMaintenance: string
  kpis: KPI[]
  recommendations: Recommendation[]
}

// ==================== Mock Data (20 assets) ====================
const assets = ref<AssetHealth[]>([
  { id: 1, name: 'UPS-01', category: 'UPS', location: 'Server Room A', healthScore: 92, healthTrend: 'stable', remainingLife: 8.5, mtbf: 45000, mttr: 4.2, uptime: 99.99, activeAlerts: 0, lastMaintenance: '2024-05-15',
    kpis: [
      { metric: 'Battery Health', current: 88, threshold: 80, unit: '%', status: 'normal', trend: 'stable' },
      { metric: 'Input Voltage', current: 220, threshold: 240, unit: 'V', status: 'normal', trend: 'stable' },
      { metric: 'Output Voltage', current: 218, threshold: 230, unit: 'V', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Battery Capacity Test', description: 'Schedule battery capacity testing', priority: 'low', dueDate: '2024-08-15' }] },
  { id: 2, name: 'CRAC-01', category: 'CRAC', location: 'Data Center', healthScore: 78, healthTrend: 'down', remainingLife: 4.2, mtbf: 28000, mttr: 5.5, uptime: 99.95, activeAlerts: 1, lastMaintenance: '2024-04-10',
    kpis: [
      { metric: 'Compressor Efficiency', current: 72, threshold: 85, unit: '%', status: 'warning', trend: 'down' },
      { metric: 'Air Flow', current: 2800, threshold: 3000, unit: 'CFM', status: 'warning', trend: 'down' },
      { metric: 'Refrigerant Level', current: 45, threshold: 40, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Compressor Inspection', description: 'Compressor efficiency dropping', priority: 'high', dueDate: '2024-06-25' }] },
  { id: 3, name: 'Generator-01', category: 'Generator', location: 'Generator Room', healthScore: 45, healthTrend: 'down', remainingLife: 1.5, mtbf: 15000, mttr: 8.0, uptime: 99.85, activeAlerts: 2, lastMaintenance: '2024-03-20',
    kpis: [
      { metric: 'Engine Temp', current: 95, threshold: 90, unit: '°C', status: 'critical', trend: 'up' },
      { metric: 'Oil Pressure', current: 28, threshold: 35, unit: 'psi', status: 'critical', trend: 'down' },
      { metric: 'Battery Voltage', current: 11.8, threshold: 12.5, unit: 'V', status: 'critical', trend: 'down' }
    ],
    recommendations: [{ title: 'Emergency Maintenance', description: 'Immediate engine inspection required', priority: 'high', dueDate: '2024-06-05' }] },
  { id: 4, name: 'PDU-A01', category: 'PDU', location: 'Server Row A', healthScore: 88, healthTrend: 'stable', remainingLife: 6.8, mtbf: 52000, mttr: 2.5, uptime: 99.98, activeAlerts: 0, lastMaintenance: '2024-05-01',
    kpis: [
      { metric: 'Phase Balance', current: 5, threshold: 10, unit: '%', status: 'normal', trend: 'stable' },
      { metric: 'Load Capacity', current: 72, threshold: 80, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Load Balancing', description: 'Monitor load distribution', priority: 'low', dueDate: '2024-07-30' }] },
  { id: 5, name: 'Chiller-01', category: 'Chiller', location: 'Chiller Plant', healthScore: 82, healthTrend: 'stable', remainingLife: 5.5, mtbf: 35000, mttr: 6.0, uptime: 99.92, activeAlerts: 0, lastMaintenance: '2024-04-25',
    kpis: [
      { metric: 'Evaporator Pressure', current: 72, threshold: 80, unit: 'psi', status: 'normal', trend: 'stable' },
      { metric: 'Condenser Pressure', current: 195, threshold: 220, unit: 'psi', status: 'normal', trend: 'up' }
    ],
    recommendations: [{ title: 'Condenser Cleaning', description: 'Schedule condenser coil cleaning', priority: 'medium', dueDate: '2024-07-10' }] },
  { id: 6, name: 'Transformer-01', category: 'Transformer', location: 'Electrical Room', healthScore: 95, healthTrend: 'up', remainingLife: 12.0, mtbf: 68000, mttr: 3.5, uptime: 99.99, activeAlerts: 0, lastMaintenance: '2024-05-20',
    kpis: [
      { metric: 'Oil Temperature', current: 65, threshold: 85, unit: '°C', status: 'normal', trend: 'stable' },
      { metric: 'Winding Temp', current: 72, threshold: 95, unit: '°C', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Oil Analysis', description: 'Schedule DGA oil analysis', priority: 'low', dueDate: '2024-08-01' }] },
  { id: 7, name: 'HVAC-AHU-01', category: 'HVAC', location: 'Mechanical Room', healthScore: 72, healthTrend: 'down', remainingLife: 3.8, mtbf: 22000, mttr: 4.5, uptime: 99.88, activeAlerts: 1, lastMaintenance: '2024-04-05',
    kpis: [
      { metric: 'Motor Temp', current: 78, threshold: 75, unit: '°C', status: 'warning', trend: 'up' },
      { metric: 'Belt Tension', current: 82, threshold: 90, unit: '%', status: 'warning', trend: 'down' }
    ],
    recommendations: [{ title: 'Belt Replacement', description: 'Replace drive belt', priority: 'medium', dueDate: '2024-06-15' }] },
  { id: 8, name: 'CoolingTower-01', category: 'Cooling Tower', location: 'Roof', healthScore: 68, healthTrend: 'down', remainingLife: 3.2, mtbf: 20000, mttr: 5.0, uptime: 99.85, activeAlerts: 1, lastMaintenance: '2024-04-18',
    kpis: [
      { metric: 'Fan Vibration', current: 4.8, threshold: 4.0, unit: 'mm/s', status: 'critical', trend: 'up' },
      { metric: 'Water Temp', current: 32, threshold: 30, unit: '°C', status: 'warning', trend: 'up' }
    ],
    recommendations: [{ title: 'Fan Balancing', description: 'Balance fan blades', priority: 'high', dueDate: '2024-06-18' }] },
  { id: 9, name: 'UPS-02', category: 'UPS', location: 'Server Room B', healthScore: 85, healthTrend: 'stable', remainingLife: 6.5, mtbf: 42000, mttr: 4.0, uptime: 99.97, activeAlerts: 0, lastMaintenance: '2024-05-10',
    kpis: [
      { metric: 'Battery Health', current: 82, threshold: 80, unit: '%', status: 'normal', trend: 'stable' },
      { metric: 'Input Voltage', current: 222, threshold: 240, unit: 'V', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Battery Check', description: 'Inspect battery terminals', priority: 'low', dueDate: '2024-07-20' }] },
  { id: 10, name: 'CRAC-02', category: 'CRAC', location: 'Data Center', healthScore: 81, healthTrend: 'stable', remainingLife: 5.0, mtbf: 30000, mttr: 5.0, uptime: 99.94, activeAlerts: 0, lastMaintenance: '2024-05-01',
    kpis: [
      { metric: 'Compressor Efficiency', current: 78, threshold: 85, unit: '%', status: 'warning', trend: 'stable' },
      { metric: 'Air Flow', current: 2900, threshold: 3000, unit: 'CFM', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Filter Replacement', description: 'Replace air filters', priority: 'medium', dueDate: '2024-07-01' }] },
  { id: 11, name: 'PDU-B01', category: 'PDU', location: 'Server Row B', healthScore: 91, healthTrend: 'up', remainingLife: 7.2, mtbf: 55000, mttr: 2.5, uptime: 99.99, activeAlerts: 0, lastMaintenance: '2024-05-20',
    kpis: [
      { metric: 'Phase Balance', current: 3, threshold: 10, unit: '%', status: 'normal', trend: 'stable' },
      { metric: 'Load Capacity', current: 60, threshold: 80, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Routine Check', description: 'Quarterly inspection', priority: 'low', dueDate: '2024-08-01' }] },
  { id: 12, name: 'Generator-02', category: 'Generator', location: 'Generator Room', healthScore: 82, healthTrend: 'stable', remainingLife: 4.5, mtbf: 18000, mttr: 7.5, uptime: 99.90, activeAlerts: 0, lastMaintenance: '2024-04-15',
    kpis: [
      { metric: 'Engine Temp', current: 88, threshold: 90, unit: '°C', status: 'normal', trend: 'stable' },
      { metric: 'Oil Pressure', current: 32, threshold: 35, unit: 'psi', status: 'warning', trend: 'stable' }
    ],
    recommendations: [{ title: 'Oil Change', description: 'Schedule oil and filter change', priority: 'medium', dueDate: '2024-07-10' }] },
  { id: 13, name: 'UPS-03', category: 'UPS', location: 'Server Room C', healthScore: 94, healthTrend: 'up', remainingLife: 9.0, mtbf: 48000, mttr: 3.8, uptime: 99.99, activeAlerts: 0, lastMaintenance: '2024-05-25',
    kpis: [
      { metric: 'Battery Health', current: 90, threshold: 80, unit: '%', status: 'normal', trend: 'up' },
      { metric: 'Output Voltage', current: 219, threshold: 230, unit: 'V', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Routine Test', description: 'Monthly load test', priority: 'low', dueDate: '2024-07-25' }] },
  { id: 14, name: 'Chiller-02', category: 'Chiller', location: 'Chiller Plant', healthScore: 75, healthTrend: 'down', remainingLife: 3.5, mtbf: 32000, mttr: 6.5, uptime: 99.88, activeAlerts: 1, lastMaintenance: '2024-04-18',
    kpis: [
      { metric: 'Evaporator Pressure', current: 78, threshold: 80, unit: 'psi', status: 'warning', trend: 'up' },
      { metric: 'Refrigerant Level', current: 42, threshold: 40, unit: '%', status: 'warning', trend: 'down' }
    ],
    recommendations: [{ title: 'Refrigerant Check', description: 'Check for leaks', priority: 'high', dueDate: '2024-06-20' }] },
  { id: 15, name: 'Transformer-02', category: 'Transformer', location: 'Electrical Room', healthScore: 88, healthTrend: 'stable', remainingLife: 8.5, mtbf: 65000, mttr: 3.0, uptime: 99.98, activeAlerts: 0, lastMaintenance: '2024-05-18',
    kpis: [
      { metric: 'Oil Temperature', current: 70, threshold: 85, unit: '°C', status: 'normal', trend: 'stable' },
      { metric: 'Winding Temp', current: 78, threshold: 95, unit: '°C', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Oil Sampling', description: 'Schedule oil analysis', priority: 'low', dueDate: '2024-08-10' }] },
  { id: 16, name: 'HVAC-AHU-02', category: 'HVAC', location: 'Mechanical Room', healthScore: 70, healthTrend: 'down', remainingLife: 2.8, mtbf: 20000, mttr: 5.0, uptime: 99.82, activeAlerts: 1, lastMaintenance: '2024-03-28',
    kpis: [
      { metric: 'Motor Temp', current: 82, threshold: 75, unit: '°C', status: 'critical', trend: 'up' },
      { metric: 'Air Flow', current: 2600, threshold: 3000, unit: 'CFM', status: 'critical', trend: 'down' }
    ],
    recommendations: [{ title: 'Motor Replacement', description: 'Motor overheating', priority: 'high', dueDate: '2024-06-22' }] },
  { id: 17, name: 'CoolingTower-02', category: 'Cooling Tower', location: 'Roof', healthScore: 73, healthTrend: 'stable', remainingLife: 4.0, mtbf: 22000, mttr: 5.5, uptime: 99.88, activeAlerts: 0, lastMaintenance: '2024-04-12',
    kpis: [
      { metric: 'Fan Vibration', current: 4.5, threshold: 4.0, unit: 'mm/s', status: 'warning', trend: 'stable' },
      { metric: 'Water Temp', current: 31, threshold: 30, unit: '°C', status: 'warning', trend: 'stable' }
    ],
    recommendations: [{ title: 'Water Treatment', description: 'Check chemical treatment', priority: 'medium', dueDate: '2024-07-05' }] },
  { id: 18, name: 'PDU-C01', category: 'PDU', location: 'Server Row C', healthScore: 90, healthTrend: 'stable', remainingLife: 7.5, mtbf: 53000, mttr: 2.5, uptime: 99.98, activeAlerts: 0, lastMaintenance: '2024-05-10',
    kpis: [
      { metric: 'Phase Balance', current: 4, threshold: 10, unit: '%', status: 'normal', trend: 'stable' },
      { metric: 'Load Capacity', current: 62, threshold: 80, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Capacity Planning', description: 'Monitor load growth', priority: 'low', dueDate: '2024-08-15' }] },
  { id: 19, name: 'CRAC-03', category: 'CRAC', location: 'Data Center', healthScore: 84, healthTrend: 'up', remainingLife: 5.5, mtbf: 31000, mttr: 4.8, uptime: 99.95, activeAlerts: 0, lastMaintenance: '2024-05-01',
    kpis: [
      { metric: 'Compressor Efficiency', current: 82, threshold: 85, unit: '%', status: 'normal', trend: 'up' },
      { metric: 'Air Flow', current: 2950, threshold: 3000, unit: 'CFM', status: 'normal', trend: 'up' }
    ],
    recommendations: [{ title: 'Preventive Maintenance', description: 'Schedule quarterly maintenance', priority: 'low', dueDate: '2024-07-20' }] },
  { id: 20, name: 'Generator-03', category: 'Generator', location: 'Generator Room', healthScore: 87, healthTrend: 'up', remainingLife: 6.0, mtbf: 20000, mttr: 7.0, uptime: 99.92, activeAlerts: 0, lastMaintenance: '2024-05-15',
    kpis: [
      { metric: 'Engine Temp', current: 86, threshold: 90, unit: '°C', status: 'normal', trend: 'stable' },
      { metric: 'Battery Voltage', current: 12.4, threshold: 12.5, unit: 'V', status: 'normal', trend: 'stable' }
    ],
    recommendations: [{ title: 'Monthly Test', description: 'Run generator under load', priority: 'low', dueDate: '2024-07-15' }] }
])

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const healthFilter = ref('')
const locationFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(9)
const chartType = ref('gauge')
const detailDialogVisible = ref(false)
const selectedAsset = ref<AssetHealth | null>(null)

let chartInstance: echarts.ECharts | null = null
let historyChartInstance: echarts.ECharts | null = null
const chartContainer = ref<HTMLElement | null>(null)
const historyChartContainer = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const total = assets.value.length
  const healthy = assets.value.filter(a => a.healthScore >= 80).length
  const warning = assets.value.filter(a => a.healthScore >= 60 && a.healthScore < 80).length
  const critical = assets.value.filter(a => a.healthScore < 60).length
  const avgHealth = Math.round(assets.value.reduce((sum, a) => sum + a.healthScore, 0) / total)
  const previousAvg = 76
  const trend = ((avgHealth - previousAvg) / previousAvg * 100).toFixed(1)

  return {
    total,
    healthy,
    warning,
    critical,
    avgHealth,
    trend: Math.abs(Number(trend)),
    trendDirection: Number(trend) >= 0 ? 'up' : 'down',
    predictedFailures: 3
  }
})

const healthTips = computed(() => [
  { id: 1, message: 'Generator-01 requires immediate attention - health score dropped to 45%' },
  { id: 2, message: '3 CRAC units showing declining efficiency - schedule maintenance' },
  { id: 3, message: 'UPS batteries aging - 2 units need replacement within 6 months' }
])

const filteredAssets = computed(() => {
  let filtered = [...assets.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a => a.name.toLowerCase().includes(search))
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(a => a.category === categoryFilter.value)
  }

  if (healthFilter.value) {
    if (healthFilter.value === 'healthy') filtered = filtered.filter(a => a.healthScore >= 80)
    else if (healthFilter.value === 'warning') filtered = filtered.filter(a => a.healthScore >= 60 && a.healthScore < 80)
    else if (healthFilter.value === 'critical') filtered = filtered.filter(a => a.healthScore < 60)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(a => a.location === locationFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredAssets.value.length)

const paginatedAssets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAssets.value.slice(start, end)
})

// ==================== Helper Functions ====================
const formatDate = (date: string) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const getHealthLevel = (score: number) => {
  if (score >= 80) return 'healthy'
  if (score >= 60) return 'warning'
  return 'critical'
}

const getHealthColor = (score: number) => {
  if (score >= 80) return '#22c55e'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

const getOverallHealthColor = (score: number) => {
  if (score >= 80) return '#22c55e'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

const getKPIClass = (value: number, threshold: number) => {
  if (value >= threshold * 1.1) return 'kpi-critical'
  if (value >= threshold) return 'kpi-warning'
  return 'kpi-normal'
}

const viewAssetDetail = (asset: AssetHealth) => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
  nextTick(() => {
    initHistoryChart(asset)
  })
}

const resetFilters = () => {
  searchText.value = ''
  categoryFilter.value = ''
  healthFilter.value = ''
  locationFilter.value = ''
}

const runHealthCheck = () => {
  ElMessage.success('Health check initiated')
  setTimeout(() => {
    ElMessage.success('Health check completed - all systems nominal')
  }, 2000)
}

const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Health report exported')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Charts ====================
const initChart = () => {
  if (!chartContainer.value) return
  if (chartInstance) chartInstance.dispose()

  const categories = ['UPS', 'CRAC', 'PDU', 'Generator', 'Chiller', 'Transformer', 'HVAC', 'Cooling Tower']
  const healthData = [88, 79, 90, 71, 79, 92, 71, 71]

  chartInstance = echarts.init(chartContainer.value)

  if (chartType.value === 'gauge') {
    chartInstance.setOption({
      tooltip: { trigger: 'axis' },
      radar: {
        indicator: categories.map(c => ({ name: c, max: 100 })),
        shape: 'circle',
        center: ['50%', '50%'],
        radius: '65%'
      },
      series: [{
        type: 'radar',
        data: [{ value: healthData, name: 'Health Score' }],
        areaStyle: { color: 'rgba(34, 197, 94, 0.2)' },
        lineStyle: { color: '#22c55e', width: 2 },
        itemStyle: { color: '#22c55e' }
      }]
    })
  } else {
    chartInstance.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 20, left: 50, right: 20, bottom: 20, containLabel: true },
      xAxis: { type: 'value', name: 'Health Score (%)', max: 100 },
      yAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } },
      series: [{
        type: 'bar',
        data: healthData,
        itemStyle: {
          borderRadius: [0, 4, 4, 0],
          color: (params: any) => getHealthColor(params.value)
        },
        label: { show: true, position: 'right', formatter: '{c}%' }
      }]
    })
  }

  chartInstance.resize()
}

const initHistoryChart = (asset: AssetHealth) => {
  if (!historyChartContainer.value) return
  if (historyChartInstance) historyChartInstance.dispose()

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const healthHistory = [88, 86, 85, 84, 82, 80, 78, 76, 74, 72, 70, 68]

  historyChartInstance = echarts.init(historyChartContainer.value)
  historyChartInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 0, max: 100 },
    series: [{
      type: 'line',
      data: healthHistory,
      smooth: true,
      lineStyle: { color: getHealthColor(asset.healthScore), width: 3 },
      areaStyle: { opacity: 0.1, color: getHealthColor(asset.healthScore) },
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: getHealthColor(asset.healthScore) }
    }]
  })
  historyChartInstance.resize()
}

// Watch for chart type changes
watch(chartType, () => {
  nextTick(() => initChart())
})

// Watch for window resize
window.addEventListener('resize', () => {
  chartInstance?.resize()
  historyChartInstance?.resize()
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
      nextTick(() => initChart())
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
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
*::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
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
.asset-health-page {
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

.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.warning { background: #fef3c7; color: #f59e0b; }
.stat-icon.critical { background: #fee2e2; color: #ef4444; }
.stat-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-progress {
  width: 80px;
}

.stat-trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
  margin-top: 8px;
}

.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }

/* Chart Section */
.chart-section {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1.5;
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
  color: #1e293b;
}

.chart-container {
  height: 280px;
  width: 100%;
}

.health-summary-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  color: #1e293b;
}

.summary-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.summary-item {
  text-align: center;
}

.summary-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
}

.summary-value.critical { color: #ef4444; }
.summary-value.warning { color: #f59e0b; }

.health-tips {
  background: #f0fdf4;
  border-radius: 12px;
  padding: 16px;
}

.tips-title {
  font-weight: 600;
  color: #166534;
  margin-bottom: 12px;
}

.tips-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tips-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #166534;
  margin-bottom: 8px;
}

.tips-list li:last-child {
  margin-bottom: 0;
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
  font-size: 14px;
  color: #64748b;
}

.filter-label {
  font-weight: 500;
  color: #1e293b;
}

/* Health Grid */
.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.health-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  position: relative;
}

.health-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.card-glow.healthy { background: linear-gradient(90deg, #22c55e, #4ade80); }
.card-glow.warning { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.card-glow.critical { background: linear-gradient(90deg, #ef4444, #f87171); }

.card-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.asset-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.asset-icon.ups { background: #eef2ff; color: #3b82f6; }
.asset-icon.crac { background: #dcfce7; color: #22c55e; }
.asset-icon.pdu { background: #fef3c7; color: #f59e0b; }
.asset-icon.generator { background: #fee2e2; color: #ef4444; }
.asset-icon.chiller { background: #e0e7ff; color: #4f46e5; }
.asset-icon.transformer { background: #f3e8ff; color: #8b5cf6; }
.asset-icon.hvac { background: #fce7f3; color: #ec489a; }
.asset-icon.cooling\ tower { background: #fef3c7; color: #d97706; }

.asset-name {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
}

.asset-category {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.health-badge {
  margin-left: auto;
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 18px;
}

.health-badge.healthy { background: #dcfce7; color: #16a34a; }
.health-badge.warning { background: #fef3c7; color: #d97706; }
.health-badge.critical { background: #fee2e2; color: #dc2626; }

.health-gauge {
  padding: 0 20px 12px;
}

.gauge-track {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.gauge-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.gauge-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #94a3b8;
  margin-top: 4px;
}

.asset-metrics {
  padding: 12px 20px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  background: #f8fafc;
  border-top: 1px solid #eef2f8;
  border-bottom: 1px solid #eef2f8;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 11px;
  color: #64748b;
}

.metric-value {
  font-size: 12px;
  font-weight: 600;
  color: #1e293b;
}

.trend-indicator {
  padding: 10px 20px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.trend-indicator.up { color: #22c55e; }
.trend-indicator.down { color: #ef4444; }
.trend-indicator.stable { color: #3b82f6; }

.card-footer {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #eef2f8;
}

.footer-stats {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #64748b;
}

.footer-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
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

/* Detail Dialog */
.health-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.asset-detail {
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
  font-size: 28px;
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

.history-chart {
  height: 250px;
  width: 100%;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  gap: 14px;
  padding: 14px;
  background: #f8fafc;
  border-radius: 12px;
  align-items: flex-start;
}

.recommendation-item.high { border-left: 3px solid #ef4444; }
.recommendation-item.medium { border-left: 3px solid #f59e0b; }
.recommendation-item.low { border-left: 3px solid #22c55e; }

.rec-icon {
  font-size: 20px;
  color: #f59e0b;
}

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
}

.rec-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.rec-deadline {
  font-size: 11px;
  color: #8b5cf6;
}

.kpi-normal { color: #22c55e; }
.kpi-warning { color: #f59e0b; }
.kpi-critical { color: #ef4444; }

.trend-up { color: #ef4444; }
.trend-down { color: #22c55e; }
.trend-stable { color: #3b82f6; }

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-section {
    flex-direction: column;
  }

  .health-grid {
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
</style>