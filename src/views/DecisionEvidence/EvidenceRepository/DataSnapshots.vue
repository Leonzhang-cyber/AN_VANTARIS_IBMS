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
        <div class="loading-tip">Data Snapshots Repository</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="snapshots-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Evidence Repository</el-breadcrumb-item>
            <el-breadcrumb-item>Data Snapshots</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Snapshots</h1>
        <p class="description">Capture and manage historical data snapshots for trend analysis, decision validation, and compliance evidence</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateSnapshot">
          <el-icon><Plus /></el-icon>
          New Snapshot
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Snapshot Trend Chart -->
    <el-card class="trend-chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Data Points Over Time</span>
          <div class="chart-controls">
            <el-radio-group v-model="trendMetric" size="small">
              <el-radio-button value="energy">Energy (kWh)</el-radio-button>
              <el-radio-button value="temperature">Temperature (°C)</el-radio-button>
              <el-radio-button value="efficiency">Efficiency (%)</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>
      <div ref="trendChartRef" class="trend-chart-container"></div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by snapshot name"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.dataCategory" placeholder="Data Category" clearable style="width: 140px">
            <el-option label="Energy" value="Energy" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Electrical" value="Electrical" />
            <el-option label="Water" value="Water" />
            <el-option label="Environmental" value="Environmental" />
            <el-option label="Carbon" value="Carbon" />
          </el-select>
          <el-select v-model="filters.snapshotType" placeholder="Snapshot Type" clearable style="width: 130px">
            <el-option label="Hourly" value="Hourly" />
            <el-option label="Daily" value="Daily" />
            <el-option label="Weekly" value="Weekly" />
            <el-option label="Monthly" value="Monthly" />
            <el-option label="Quarterly" value="Quarterly" />
          </el-select>
          <el-select v-model="filters.source" placeholder="Source" clearable style="width: 140px">
            <el-option label="BMS" value="BMS" />
            <el-option label="SCADA" value="SCADA" />
            <el-option label="IoT Sensors" value="IoT Sensors" />
            <el-option label="Manual Entry" value="Manual Entry" />
            <el-option label="API" value="API" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 260px"
          />
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Snapshot Comparison View -->
    <el-card class="comparison-card" shadow="hover" v-if="selectedSnapshot1 && selectedSnapshot2">
      <template #header>
        <div class="card-header">
          <span>Snapshot Comparison</span>
          <el-button size="small" @click="clearComparison">Clear Comparison</el-button>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="12">
          <div class="comparison-item">
            <h4>{{ selectedSnapshot1.name }}</h4>
            <p class="comparison-date">{{ selectedSnapshot1.timestamp }}</p>
            <el-table :data="getSnapshotMetrics(selectedSnapshot1)" size="small" border>
              <el-table-column prop="metric" label="Metric" />
              <el-table-column prop="value" label="Value" />
              <el-table-column prop="unit" label="Unit" width="80" />
            </el-table>
          </div>
        </el-col>
        <el-col :span="12">
          <div class="comparison-item">
            <h4>{{ selectedSnapshot2.name }}</h4>
            <p class="comparison-date">{{ selectedSnapshot2.timestamp }}</p>
            <el-table :data="getSnapshotMetrics(selectedSnapshot2)" size="small" border>
              <el-table-column prop="metric" label="Metric" />
              <el-table-column prop="value" label="Value" />
              <el-table-column prop="unit" label="Unit" width="80" />
            </el-table>
          </div>
        </el-col>
      </el-row>
      <div class="comparison-diff" v-if="selectedSnapshot1 && selectedSnapshot2">
        <h4>Changes</h4>
        <el-table :data="getComparisonDiff()" size="small" border>
          <el-table-column prop="metric" label="Metric" />
          <el-table-column prop="value1" label="Snapshot 1" width="120" />
          <el-table-column prop="value2" label="Snapshot 2" width="120" />
          <el-table-column prop="change" label="Change" width="100">
            <template #default="{ row }">
              <span :style="{ color: row.changeType === 'positive' ? '#67c23a' : (row.changeType === 'negative' ? '#f56c6c' : '#909399') }">
                {{ row.changeValue }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="changePercent" label="% Change" width="100">
            <template #default="{ row }">
              <span :style="{ color: row.changeType === 'positive' ? '#67c23a' : (row.changeType === 'negative' ? '#f56c6c' : '#909399') }">
                {{ row.changePercent }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Data Snapshots ({{ filteredSnapshots.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchSnapshots" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedSnapshots" stripe style="width: 100%" v-loading="loading">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="Snapshot Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="dataCategory" label="Category" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.dataCategory)" size="small">{{ row.dataCategory }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="snapshotType" label="Type" width="100" />
        <el-table-column prop="source" label="Source" width="120" />
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="dataPoints" label="Data Points" width="100" align="center" />
        <el-table-column prop="fileSize" label="Size" width="90" />
        <el-table-column label="Actions" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewSnapshot(row)">View</el-button>
            <el-button link type="success" size="small" @click="compareSnapshot(row)">Compare</el-button>
            <el-button link type="info" size="small" @click="exportSnapshot(row)">Export</el-button>
            <el-button link type="danger" size="small" @click="deleteSnapshot(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredSnapshots.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Create Snapshot Dialog -->
    <el-dialog v-model="createDialogVisible" title="Create Data Snapshot" width="600px" destroy-on-close>
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="120px">
        <el-form-item label="Snapshot Name" prop="name">
          <el-input v-model="createForm.name" placeholder="Enter snapshot name" />
        </el-form-item>
        <el-form-item label="Data Category" prop="dataCategory">
          <el-select v-model="createForm.dataCategory" placeholder="Select category" style="width: 100%">
            <el-option label="Energy" value="Energy" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Electrical" value="Electrical" />
            <el-option label="Water" value="Water" />
            <el-option label="Environmental" value="Environmental" />
            <el-option label="Carbon" value="Carbon" />
          </el-select>
        </el-form-item>
        <el-form-item label="Snapshot Type" prop="snapshotType">
          <el-select v-model="createForm.snapshotType" placeholder="Select type" style="width: 100%">
            <el-option label="Hourly" value="Hourly" />
            <el-option label="Daily" value="Daily" />
            <el-option label="Weekly" value="Weekly" />
            <el-option label="Monthly" value="Monthly" />
            <el-option label="Custom" value="Custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Time Range" prop="timeRange">
          <el-date-picker
              v-model="createForm.timeRange"
              type="datetimerange"
              range-separator="to"
              start-placeholder="Start Time"
              end-placeholder="End Time"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Data Sources" prop="dataSources">
          <el-select v-model="createForm.dataSources" multiple placeholder="Select data sources" style="width: 100%">
            <el-option label="BMS" value="BMS" />
            <el-option label="SCADA" value="SCADA" />
            <el-option label="IoT Sensors" value="IoT Sensors" />
            <el-option label="Weather API" value="Weather API" />
            <el-option label="Utility Meters" value="Utility Meters" />
          </el-select>
        </el-form-item>
        <el-form-item label="Include Metrics" prop="includeMetrics">
          <el-checkbox-group v-model="createForm.includeMetrics">
            <el-checkbox label="Energy Consumption">Energy Consumption</el-checkbox>
            <el-checkbox label="Temperature">Temperature</el-checkbox>
            <el-checkbox label="Humidity">Humidity</el-checkbox>
            <el-checkbox label="Pressure">Pressure</el-checkbox>
            <el-checkbox label="Flow Rate">Flow Rate</el-checkbox>
            <el-checkbox label="Power Quality">Power Quality</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="createForm.description" type="textarea" :rows="2" placeholder="Enter snapshot description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="creating" @click="submitCreate">Create Snapshot</el-button>
      </template>
    </el-dialog>

    <!-- View Snapshot Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="currentSnapshot?.name" width="800px" destroy-on-close>
      <div class="snapshot-detail">
        <div class="snapshot-header">
          <div class="snapshot-meta">
            <el-tag :type="getCategoryTag(currentSnapshot?.dataCategory || '')" size="default">{{ currentSnapshot?.dataCategory }}</el-tag>
            <el-tag type="info" size="default">{{ currentSnapshot?.snapshotType }}</el-tag>
            <el-tag type="success" size="default">{{ currentSnapshot?.source }}</el-tag>
          </div>
          <div class="snapshot-date">Captured: {{ currentSnapshot?.timestamp }}</div>
        </div>

        <div class="snapshot-content">
          <div class="snapshot-section">
            <h4>Summary Statistics</h4>
            <el-row :gutter="16">
              <el-col :span="6" v-for="stat in currentSnapshot?.summaryStats" :key="stat.name">
                <div class="stat-card-mini">
                  <div class="stat-name">{{ stat.name }}</div>
                  <div class="stat-value">{{ stat.value }}</div>
                  <div class="stat-unit">{{ stat.unit }}</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <div class="snapshot-section">
            <h4>Data Overview</h4>
            <div ref="detailChartRef" class="detail-chart-container"></div>
          </div>

          <div class="snapshot-section">
            <h4>Detailed Metrics</h4>
            <el-table :data="currentSnapshot?.metrics || []" size="small" border>
              <el-table-column prop="timestamp" label="Timestamp" width="160" />
              <el-table-column prop="metric" label="Metric" />
              <el-table-column prop="value" label="Value" />
              <el-table-column prop="unit" label="Unit" width="80" />
              <el-table-column prop="threshold" label="Threshold" width="100" />
              <el-table-column label="Status" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.value > row.threshold ? 'danger' : 'success'" size="small">
                    {{ row.value > row.threshold ? 'Alert' : 'Normal' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <div class="snapshot-section" v-if="currentSnapshot?.tags">
            <h4>Tags</h4>
            <div>
              <el-tag v-for="tag in currentSnapshot.tags" :key="tag" size="small" style="margin-right: 8px">{{ tag }}</el-tag>
            </div>
          </div>

          <div class="snapshot-section" v-if="currentSnapshot?.description">
            <h4>Description</h4>
            <p>{{ currentSnapshot.description }}</p>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportCurrentSnapshot">Export Data</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete snapshot "{{ deleteTarget?.name }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, DataAnalysis, Collection, Coin, Connection
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading data snapshots...',
  'Compiling metrics...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface DataSnapshot {
  id: number
  name: string
  description: string
  dataCategory: string
  snapshotType: string
  source: string
  timestamp: string
  dataPoints: number
  fileSize: string
  summaryStats: Array<{ name: string; value: string; unit: string }>
  metrics: Array<{ timestamp: string; metric: string; value: number; unit: string; threshold: number }>
  tags: string[]
  url: string
}

interface StatCard {
  title: string
  value: string | number
  trend: number
  icon: string
  bgColor: string
  key: string
}

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const detailChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let detailChart: echarts.ECharts | null = null

const trendMetric = ref<'energy' | 'temperature' | 'efficiency'>('energy')
const selectedSnapshot1 = ref<DataSnapshot | null>(null)
const selectedSnapshot2 = ref<DataSnapshot | null>(null)

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Snapshots', value: 124, trend: 12, icon: 'Collection', bgColor: '#409eff', key: 'total' },
  { title: 'Data Points', value: '48.2K', trend: 18, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'points' },
  { title: 'Storage Size', value: '156 MB', trend: 8, icon: 'Document', bgColor: '#e6a23c', key: 'storage' },
  { title: 'Avg. Retention', value: '45 days', trend: -5, icon: 'Clock', bgColor: '#f56c6c', key: 'retention' }
])

const snapshots = ref<DataSnapshot[]>([
  {
    id: 1,
    name: 'Q4 2023 Energy Consumption Snapshot',
    description: 'Quarterly energy consumption data snapshot for Q4 2023, including daily usage patterns and peak demand',
    dataCategory: 'Energy',
    snapshotType: 'Quarterly',
    source: 'BMS',
    timestamp: '2024-01-01 00:00:00',
    dataPoints: 8640,
    fileSize: '2.4 MB',
    summaryStats: [
      { name: 'Total Consumption', value: '1,245,000', unit: 'kWh' },
      { name: 'Avg Daily', value: '13,530', unit: 'kWh' },
      { name: 'Peak Demand', value: '1,850', unit: 'kW' },
      { name: 'Cost', value: '$148,500', unit: 'USD' }
    ],
    metrics: [
      { timestamp: '2024-01-01', metric: 'Energy Consumption', value: 14200, unit: 'kWh', threshold: 15000 },
      { timestamp: '2024-01-02', metric: 'Energy Consumption', value: 13800, unit: 'kWh', threshold: 15000 },
      { timestamp: '2024-01-03', metric: 'Energy Consumption', value: 14500, unit: 'kWh', threshold: 15000 },
      { timestamp: '2024-01-04', metric: 'Energy Consumption', value: 14100, unit: 'kWh', threshold: 15000 },
      { timestamp: '2024-01-05', metric: 'Energy Consumption', value: 13900, unit: 'kWh', threshold: 15000 }
    ],
    tags: ['energy', 'quarterly', 'consumption', '2024'],
    url: '#'
  },
  {
    id: 2,
    name: 'HVAC System Performance - January 2024',
    description: 'Hourly HVAC performance data including temperatures, airflow, and efficiency metrics',
    dataCategory: 'HVAC',
    snapshotType: 'Hourly',
    source: 'BMS',
    timestamp: '2024-01-15 08:00:00',
    dataPoints: 720,
    fileSize: '1.8 MB',
    summaryStats: [
      { name: 'Avg Temperature', value: '22.5', unit: '°C' },
      { name: 'Avg Humidity', value: '48', unit: '%' },
      { name: 'System Efficiency', value: '87', unit: '%' },
      { name: 'Energy Use', value: '45,200', unit: 'kWh' }
    ],
    metrics: [
      { timestamp: '2024-01-15 00:00', metric: 'Supply Temp', value: 12.5, unit: '°C', threshold: 15 },
      { timestamp: '2024-01-15 04:00', metric: 'Supply Temp', value: 12.8, unit: '°C', threshold: 15 },
      { timestamp: '2024-01-15 08:00', metric: 'Supply Temp', value: 13.2, unit: '°C', threshold: 15 },
      { timestamp: '2024-01-15 12:00', metric: 'Supply Temp', value: 13.5, unit: '°C', threshold: 15 },
      { timestamp: '2024-01-15 16:00', metric: 'Supply Temp', value: 13.8, unit: '°C', threshold: 15 }
    ],
    tags: ['hvac', 'performance', 'january'],
    url: '#'
  },
  {
    id: 3,
    name: 'Carbon Emissions Baseline - 2023',
    description: 'Baseline carbon emissions data for 2023, segmented by scope and source',
    dataCategory: 'Carbon',
    snapshotType: 'Annual',
    source: 'Manual Entry',
    timestamp: '2024-01-10 10:00:00',
    dataPoints: 365,
    fileSize: '1.2 MB',
    summaryStats: [
      { name: 'Scope 1', value: '1,850', unit: 'tCO₂e' },
      { name: 'Scope 2', value: '3,200', unit: 'tCO₂e' },
      { name: 'Scope 3', value: '2,450', unit: 'tCO₂e' },
      { name: 'Total', value: '7,500', unit: 'tCO₂e' }
    ],
    metrics: [
      { timestamp: '2023-01-01', metric: 'Scope 1 Emissions', value: 1850, unit: 'tCO₂e', threshold: 2000 },
      { timestamp: '2023-01-01', metric: 'Scope 2 Emissions', value: 3200, unit: 'tCO₂e', threshold: 3500 },
      { timestamp: '2023-01-01', metric: 'Scope 3 Emissions', value: 2450, unit: 'tCO₂e', threshold: 3000 }
    ],
    tags: ['carbon', 'emissions', 'baseline', 'esg'],
    url: '#'
  },
  {
    id: 4,
    name: 'Water Usage - December 2023',
    description: 'Daily water consumption data for December 2023',
    dataCategory: 'Water',
    snapshotType: 'Daily',
    source: 'Utility Meters',
    timestamp: '2024-01-05 00:00:00',
    dataPoints: 31,
    fileSize: '0.5 MB',
    summaryStats: [
      { name: 'Total Usage', value: '185,000', unit: 'gallons' },
      { name: 'Avg Daily', value: '5,967', unit: 'gallons' },
      { name: 'Peak Day', value: '7,200', unit: 'gallons' }
    ],
    metrics: [
      { timestamp: '2023-12-01', metric: 'Water Usage', value: 5800, unit: 'gallons', threshold: 7000 },
      { timestamp: '2023-12-08', metric: 'Water Usage', value: 6200, unit: 'gallons', threshold: 7000 },
      { timestamp: '2023-12-15', metric: 'Water Usage', value: 5900, unit: 'gallons', threshold: 7000 },
      { timestamp: '2023-12-22', metric: 'Water Usage', value: 6100, unit: 'gallons', threshold: 7000 },
      { timestamp: '2023-12-29', metric: 'Water Usage', value: 6400, unit: 'gallons', threshold: 7000 }
    ],
    tags: ['water', 'consumption', 'december'],
    url: '#'
  },
  {
    id: 5,
    name: 'Temperature & Humidity - Server Room',
    description: 'Environmental monitoring data for data center server room',
    dataCategory: 'Environmental',
    snapshotType: 'Hourly',
    source: 'IoT Sensors',
    timestamp: '2024-01-20 12:00:00',
    dataPoints: 168,
    fileSize: '2.1 MB',
    summaryStats: [
      { name: 'Avg Temp', value: '22.3', unit: '°C' },
      { name: 'Max Temp', value: '24.5', unit: '°C' },
      { name: 'Avg Humidity', value: '45', unit: '%' },
      { name: 'Max Humidity', value: '52', unit: '%' }
    ],
    metrics: [
      { timestamp: '2024-01-20 00:00', metric: 'Temperature', value: 22.1, unit: '°C', threshold: 25 },
      { timestamp: '2024-01-20 04:00', metric: 'Temperature', value: 22.0, unit: '°C', threshold: 25 },
      { timestamp: '2024-01-20 08:00', metric: 'Temperature', value: 22.3, unit: '°C', threshold: 25 },
      { timestamp: '2024-01-20 12:00', metric: 'Temperature', value: 22.8, unit: '°C', threshold: 25 },
      { timestamp: '2024-01-20 16:00', metric: 'Temperature', value: 23.2, unit: '°C', threshold: 25 }
    ],
    tags: ['temperature', 'humidity', 'server', 'dcim'],
    url: '#'
  },
  {
    id: 6,
    name: 'Power Quality Analysis - January 2024',
    description: 'Power quality metrics including voltage, current, and power factor',
    dataCategory: 'Electrical',
    snapshotType: 'Daily',
    source: 'SCADA',
    timestamp: '2024-01-25 23:59:59',
    dataPoints: 1440,
    fileSize: '3.2 MB',
    summaryStats: [
      { name: 'Avg Voltage', value: '480', unit: 'V' },
      { name: 'Power Factor', value: '0.95', unit: '' },
      { name: 'THD', value: '2.8', unit: '%' },
      { name: 'Avg Current', value: '425', unit: 'A' }
    ],
    metrics: [
      { timestamp: '2024-01-25', metric: 'Power Factor', value: 0.95, unit: '', threshold: 0.9 },
      { timestamp: '2024-01-25', metric: 'THD', value: 2.8, unit: '%', threshold: 5 },
      { timestamp: '2024-01-25', metric: 'Voltage', value: 480, unit: 'V', threshold: 500 }
    ],
    tags: ['power', 'quality', 'electrical'],
    url: '#'
  },
  {
    id: 7,
    name: 'Chiller Efficiency - December 2023',
    description: 'Chiller COP and efficiency data for December 2023',
    dataCategory: 'HVAC',
    snapshotType: 'Daily',
    source: 'BMS',
    timestamp: '2024-01-04 00:00:00',
    dataPoints: 31,
    fileSize: '0.8 MB',
    summaryStats: [
      { name: 'Avg COP', value: '4.2', unit: '' },
      { name: 'Max COP', value: '4.8', unit: '' },
      { name: 'Energy Use', value: '32,500', unit: 'kWh' }
    ],
    metrics: [
      { timestamp: '2023-12-01', metric: 'COP', value: 4.2, unit: '', threshold: 3.5 },
      { timestamp: '2023-12-08', metric: 'COP', value: 4.3, unit: '', threshold: 3.5 },
      { timestamp: '2023-12-15', metric: 'COP', value: 4.1, unit: '', threshold: 3.5 },
      { timestamp: '2023-12-22', metric: 'COP', value: 4.4, unit: '', threshold: 3.5 },
      { timestamp: '2023-12-29', metric: 'COP', value: 4.2, unit: '', threshold: 3.5 }
    ],
    tags: ['chiller', 'efficiency', 'cop'],
    url: '#'
  },
  {
    id: 8,
    name: 'Renewable Energy Generation - 2023',
    description: 'Solar PV generation data for the full year 2023',
    dataCategory: 'Energy',
    snapshotType: 'Monthly',
    source: 'IoT Sensors',
    timestamp: '2024-01-02 00:00:00',
    dataPoints: 12,
    fileSize: '0.3 MB',
    summaryStats: [
      { name: 'Total Generation', value: '425,000', unit: 'kWh' },
      { name: 'Peak Month', value: '52,000', unit: 'kWh' },
      { name: 'CO₂ Offset', value: '195', unit: 'tCO₂e' }
    ],
    metrics: [
      { timestamp: '2023-01-01', metric: 'Solar Generation', value: 25000, unit: 'kWh', threshold: 30000 },
      { timestamp: '2023-02-01', metric: 'Solar Generation', value: 28000, unit: 'kWh', threshold: 30000 },
      { timestamp: '2023-03-01', metric: 'Solar Generation', value: 35000, unit: 'kWh', threshold: 30000 },
      { timestamp: '2023-04-01', metric: 'Solar Generation', value: 42000, unit: 'kWh', threshold: 30000 },
      { timestamp: '2023-05-01', metric: 'Solar Generation', value: 48000, unit: 'kWh', threshold: 30000 }
    ],
    tags: ['renewable', 'solar', 'generation'],
    url: '#'
  }
])

// ==================== Reactive Variables ====================
const loading = ref(false)
const creating = ref(false)
const createDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const currentSnapshot = ref<DataSnapshot | null>(null)
const deleteTarget = ref<DataSnapshot | null>(null)
const createFormRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)

const filters = reactive({
  keyword: '',
  dataCategory: '',
  snapshotType: '',
  source: '',
  dateRange: null as [Date, Date] | null
})

const createForm = reactive({
  name: '',
  dataCategory: '',
  snapshotType: '',
  timeRange: null as [Date, Date] | null,
  dataSources: [] as string[],
  includeMetrics: [] as string[],
  description: ''
})

const createRules = {
  name: [{ required: true, message: 'Please enter snapshot name', trigger: 'blur' }],
  dataCategory: [{ required: true, message: 'Please select data category', trigger: 'change' }],
  snapshotType: [{ required: true, message: 'Please select snapshot type', trigger: 'change' }],
  timeRange: [{ required: true, message: 'Please select time range', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredSnapshots = computed(() => {
  let filtered = [...snapshots.value]

  if (filters.keyword) {
    filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        s.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.dataCategory) {
    filtered = filtered.filter(s => s.dataCategory === filters.dataCategory)
  }

  if (filters.snapshotType) {
    filtered = filtered.filter(s => s.snapshotType === filters.snapshotType)
  }

  if (filters.source) {
    filtered = filtered.filter(s => s.source === filters.source)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(s => {
      const date = new Date(s.timestamp)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedSnapshots = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSnapshots.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getCategoryTag = (category: string): string => {
  const map: Record<string, string> = {
    'Energy': 'success',
    'HVAC': 'primary',
    'Electrical': 'warning',
    'Water': 'info',
    'Environmental': 'success',
    'Carbon': 'danger'
  }
  return map[category] || 'info'
}

const getSnapshotMetrics = (snapshot: DataSnapshot) => {
  return snapshot.summaryStats
}

const getComparisonDiff = () => {
  if (!selectedSnapshot1.value || !selectedSnapshot2.value) return []

  const diffs = []
  for (let i = 0; i < selectedSnapshot1.value.summaryStats.length; i++) {
    const stat1 = selectedSnapshot1.value.summaryStats[i]
    const stat2 = selectedSnapshot2.value.summaryStats.find(s => s.name === stat1.name)

    if (stat2) {
      const num1 = parseFloat(stat1.value.replace(/[^0-9.-]/g, ''))
      const num2 = parseFloat(stat2.value.replace(/[^0-9.-]/g, ''))
      const change = num2 - num1
      const changePercent = ((change / num1) * 100).toFixed(1)

      diffs.push({
        metric: stat1.name,
        value1: stat1.value,
        value2: stat2.value,
        changeValue: `${change > 0 ? '+' : ''}${change.toFixed(1)}`,
        changePercent: `${changePercent}%`,
        changeType: change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'
      })
    }
  }
  return diffs
}

// ==================== Chart Initialization ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const energyData = [14200, 13800, 14500, 14100, 13900, 14300, 14800, 15100, 14700, 15200, 14900, 14600]
  const tempData = [22.1, 22.0, 22.3, 22.8, 23.2, 23.5, 23.8, 24.0, 23.7, 23.4, 23.1, 22.8]
  const efficiencyData = [85, 86, 87, 87, 88, 88, 89, 89, 90, 89, 88, 87]

  let seriesData
  let yAxisName
  let color

  if (trendMetric.value === 'energy') {
    seriesData = energyData
    yAxisName = 'Energy Consumption (kWh)'
    color = '#409eff'
  } else if (trendMetric.value === 'temperature') {
    seriesData = tempData
    yAxisName = 'Temperature (°C)'
    color = '#f56c6c'
  } else {
    seriesData = efficiencyData
    yAxisName = 'Efficiency (%)'
    color = '#67c23a'
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      name: 'Month'
    },
    yAxis: {
      type: 'value',
      name: yAxisName
    },
    series: [{
      type: 'line',
      data: seriesData,
      smooth: true,
      lineStyle: { width: 3, color: color },
      areaStyle: { opacity: 0.1, color: color },
      symbolSize: 8,
      symbol: 'circle'
    }]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.dataCategory = ''
  filters.snapshotType = ''
  filters.source = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredSnapshots.value.length} snapshots metadata...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchSnapshots = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleCreateSnapshot = () => {
  createDialogVisible.value = true
}

const submitCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate((valid: boolean) => {
    if (valid) {
      creating.value = true
      setTimeout(() => {
        creating.value = false
        createDialogVisible.value = false
        ElMessage.success(`Snapshot "${createForm.name}" created successfully`)

        const newSnapshot: DataSnapshot = {
          id: Date.now(),
          name: createForm.name,
          description: createForm.description,
          dataCategory: createForm.dataCategory,
          snapshotType: createForm.snapshotType,
          source: createForm.dataSources.join(', '),
          timestamp: new Date().toLocaleString(),
          dataPoints: 0,
          fileSize: '0 MB',
          summaryStats: [],
          metrics: [],
          tags: [],
          url: '#'
        }
        snapshots.value.unshift(newSnapshot)

        createFormRef.value?.resetFields()
        initTrendChart()
      }, 2000)
    }
  })
}

const viewSnapshot = (snapshot: DataSnapshot) => {
  currentSnapshot.value = snapshot
  viewDialogVisible.value = true
  nextTick(() => {
    if (detailChartRef.value) {
      if (detailChart) detailChart.dispose()
      detailChart = echarts.init(detailChartRef.value)
      detailChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: snapshot.metrics.map(m => m.timestamp) },
        yAxis: { type: 'value', name: snapshot.metrics[0]?.unit || 'Value' },
        series: [{
          type: 'line',
          data: snapshot.metrics.map(m => m.value),
          smooth: true,
          lineStyle: { width: 3, color: '#409eff' }
        }]
      })
    }
  })
}

const compareSnapshot = (snapshot: DataSnapshot) => {
  if (!selectedSnapshot1.value) {
    selectedSnapshot1.value = snapshot
    ElMessage.success(`Selected "${snapshot.name}" for comparison. Select another snapshot to compare.`)
  } else if (!selectedSnapshot2.value && selectedSnapshot1.value.id !== snapshot.id) {
    selectedSnapshot2.value = snapshot
    ElMessage.success(`Comparing "${selectedSnapshot1.value.name}" vs "${snapshot.name}"`)
  } else if (selectedSnapshot1.value.id === snapshot.id) {
    ElMessage.warning('Cannot compare a snapshot with itself')
  } else {
    ElMessage.info('Clear existing comparison first')
  }
}

const clearComparison = () => {
  selectedSnapshot1.value = null
  selectedSnapshot2.value = null
  ElMessage.success('Comparison cleared')
}

const exportSnapshot = (snapshot: DataSnapshot) => {
  ElMessage.success(`Exporting snapshot: ${snapshot.name}`)
}

const exportCurrentSnapshot = () => {
  if (currentSnapshot.value) {
    exportSnapshot(currentSnapshot.value)
  }
}

const deleteSnapshot = (snapshot: DataSnapshot) => {
  deleteTarget.value = snapshot
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = snapshots.value.findIndex(s => s.id === deleteTarget.value!.id)
    if (index !== -1) {
      snapshots.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.name}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
  }, 100)
}

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
      initCharts()
      fetchSnapshots()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Page Styles ==================== */
.snapshots-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.trend-chart-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .chart-controls {
      display: flex;
      gap: 8px;
    }
  }
}

.trend-chart-container {
  width: 100%;
  height: 320px;
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.comparison-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .comparison-item {
    h4 {
      margin: 0 0 4px 0;
      color: #303133;
    }

    .comparison-date {
      font-size: 12px;
      color: #909399;
      margin-bottom: 12px;
    }
  }

  .comparison-diff {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;

    h4 {
      margin: 0 0 12px 0;
      color: #303133;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.snapshot-detail {
  .snapshot-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #ebeef5;

    .snapshot-meta {
      display: flex;
      gap: 8px;
    }

    .snapshot-date {
      color: #909399;
      font-size: 13px;
    }
  }

  .snapshot-content {
    .snapshot-section {
      margin-bottom: 24px;

      h4 {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #409eff;
        display: inline-block;
      }

      .stat-card-mini {
        background: #f5f7fa;
        border-radius: 8px;
        padding: 12px;
        text-align: center;

        .stat-name {
          font-size: 12px;
          color: #909399;
          margin-bottom: 8px;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
        }

        .stat-unit {
          font-size: 11px;
          color: #909399;
          margin-top: 4px;
        }
      }
    }
  }
}

.detail-chart-container {
  width: 100%;
  height: 300px;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>