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
          <span class="loading-title">Asset Register</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Asset Inventory & Lifecycle Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="asset-register-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Files /></el-icon>
          Asset Register
        </h1>
        <div class="page-subtitle">Complete asset inventory, lifecycle tracking, and management</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddAssetDialog">
          <el-icon><Plus /></el-icon> Add Asset
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
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
          <el-icon><Files /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalAssets }}</div>
          <div class="stat-label">Total Assets</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.activeAssets }}</div>
          <div class="stat-label">Active</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.maintenanceAssets }}</div>
          <div class="stat-label">Under Maintenance</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.retiredAssets }}</div>
          <div class="stat-label">Retired</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Total Asset Value</div>
        <div class="metric-value">${{ metrics.totalValue.toLocaleString() }}</div>
        <div class="metric-trend positive">↑ {{ metrics.valueGrowth }}% vs last year</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Asset Age</div>
        <div class="metric-value">{{ metrics.avgAge }}<span class="metric-unit">years</span></div>
        <div class="metric-trend" :class="metrics.ageTrend > 0 ? 'negative' : 'positive'">
          {{ metrics.ageTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.ageTrend) }}% vs target
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Assets Near EOL</div>
        <div class="metric-value">{{ metrics.nearEOL }}</div>
        <div class="metric-sub">End of Life within 2 years</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Annual Depreciation</div>
        <div class="metric-value">${{ metrics.annualDepreciation.toLocaleString() }}</div>
        <div class="metric-trend negative">↓ {{ metrics.depreciationRate }}% average rate</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Asset Distribution by Category</span>
          <span class="chart-subtitle">Value by asset type</span>
        </div>
        <div class="chart-container" ref="categoryChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Asset Status Breakdown</span>
          <span class="chart-subtitle">Current operational status</span>
        </div>
        <div class="chart-container" ref="statusChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Asset Value by Location</span>
          <span class="chart-subtitle">Total asset value per site</span>
        </div>
        <div class="chart-container" ref="locationChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Asset Age Distribution</span>
          <span class="chart-subtitle">Age profile of asset fleet</span>
        </div>
        <div class="chart-container" ref="ageChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by asset name, tag, or location..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option v-for="c in uniqueCategories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Active" value="active" />
          <el-option label="Maintenance" value="maintenance" />
          <el-option label="Retired" value="retired" />
        </el-select>
        <el-select v-model="locationFilter" placeholder="Location" clearable filterable style="width: 160px">
          <el-option v-for="l in uniqueLocations" :key="l" :label="l" :value="l" />
        </el-select>
        <el-select v-model="priorityFilter" placeholder="Criticality" clearable style="width: 130px">
          <el-option label="Critical" value="Critical" />
          <el-option label="High" value="High" />
          <el-option label="Medium" value="Medium" />
          <el-option label="Low" value="Low" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Assets Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Asset Inventory</span>
        <el-button size="small" @click="viewAllAssets">View All →</el-button>
      </div>
      <el-table :data="paginatedAssets" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewAssetDetail">
        <el-table-column prop="tag" label="Asset Tag" width="130" />
        <el-table-column prop="name" label="Asset Name" min-width="180" />
        <el-table-column prop="category" label="Category" width="140">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="manufacturer" label="Manufacturer" width="140" />
        <el-table-column prop="model" label="Model" width="120" />
        <el-table-column prop="location" label="Location" width="160" />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="healthScore" label="Health" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.healthScore" :stroke-width="6" :color="getHealthColor(row.healthScore)" />
          </template>
        </el-table-column>
        <el-table-column prop="purchaseDate" label="Purchase Date" width="120" />
        <el-table-column prop="currentValue" label="Current Value" width="130">
          <template #default="{ row }">
            ${{ row.currentValue.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="130" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="editAsset(row)">Edit</el-button>
            <el-button link type="warning" size="small" @click.stop="viewMaintenance(row)">History</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAsset?.name" width="1000px" class="asset-dialog">
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
            <div class="detail-stat-value">${{ selectedAsset.currentValue.toLocaleString() }}</div>
            <div class="detail-stat-label">Current Value</div>
            <div class="detail-stat-sub">Purchase: ${{ selectedAsset.purchasePrice.toLocaleString() }}</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.age }} yrs</div>
            <div class="detail-stat-label">Asset Age</div>
            <div class="detail-stat-sub">EOL: {{ selectedAsset.endOfLife }}</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.criticality }}</div>
            <div class="detail-stat-label">Criticality</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="Asset Tag">{{ selectedAsset.tag }}</el-descriptions-item>
          <el-descriptions-item label="Category">{{ selectedAsset.category }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedAsset.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedAsset.model }}</el-descriptions-item>
          <el-descriptions-item label="Serial Number">{{ selectedAsset.serialNumber }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedAsset.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedAsset.status)" size="small">{{ getStatusText(selectedAsset.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Criticality">
            <el-tag :type="getCriticalityTagType(selectedAsset.criticality)" size="small">{{ selectedAsset.criticality }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Warranty Expiry">{{ selectedAsset.warrantyExpiry }}</el-descriptions-item>
          <el-descriptions-item label="Purchase Date">{{ selectedAsset.purchaseDate }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedAsset.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedAsset.lastMaintenance }}</el-descriptions-item>
        </el-descriptions>

        <!-- Depreciation Chart -->
        <div class="detail-section">
          <div class="section-title">Depreciation Trend</div>
          <div class="trend-chart" ref="depreciationChartEl"></div>
        </div>

        <!-- Maintenance History -->
        <div class="detail-section">
          <div class="section-title">Maintenance History</div>
          <el-table :data="selectedAsset.maintenanceHistory" border stripe>
            <el-table-column prop="date" label="Date" width="120" />
            <el-table-column prop="type" label="Type" width="120">
              <template #default="{ row }">
                <el-tag :type="row.type === 'Preventive' ? 'success' : (row.type === 'Corrective' ? 'warning' : 'info')" size="small">
                  {{ row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="250" />
            <el-table-column prop="cost" label="Cost" width="120">
              <template #default="{ row }">
                ${{ row.cost.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="technician" label="Technician" width="140" />
          </el-table>
        </div>

        <!-- Documents -->
        <div class="detail-section">
          <div class="section-title">Associated Documents</div>
          <el-table :data="selectedAsset.documents" border stripe>
            <el-table-column prop="name" label="Document Name" min-width="200" />
            <el-table-column prop="type" label="Type" width="120" />
            <el-table-column prop="date" label="Upload Date" width="120" />
            <el-table-column label="Action" width="80">
              <template #default>
                <el-button link type="primary" size="small">View</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editAsset(selectedAsset)">Edit Asset</el-button>
        <el-button type="warning" @click="scheduleMaintenance(selectedAsset)">Schedule Maintenance</el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Asset Dialog -->
    <el-dialog v-model="assetDialogVisible" :title="dialogTitle" width="700px">
      <el-form :model="assetForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Asset Name" required>
              <el-input v-model="assetForm.name" placeholder="Enter asset name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Asset Tag" required>
              <el-input v-model="assetForm.tag" placeholder="e.g., UPS-001" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Category" required>
              <el-select v-model="assetForm.category" placeholder="Select category" style="width: 100%">
                <el-option label="UPS" value="UPS" />
                <el-option label="Generator" value="Generator" />
                <el-option label="CRAC" value="CRAC" />
                <el-option label="Chiller" value="Chiller" />
                <el-option label="Switchgear" value="Switchgear" />
                <el-option label="Server" value="Server" />
                <el-option label="Storage" value="Storage" />
                <el-option label="Network" value="Network" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Manufacturer" required>
              <el-input v-model="assetForm.manufacturer" placeholder="Manufacturer name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Model">
              <el-input v-model="assetForm.model" placeholder="Model number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Serial Number">
              <el-input v-model="assetForm.serialNumber" placeholder="Serial number" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Location" required>
              <el-select v-model="assetForm.location" placeholder="Select location" filterable style="width: 100%">
                <el-option label="Data Center A" value="Data Center A" />
                <el-option label="Data Center B" value="Data Center B" />
                <el-option label="Server Room 1" value="Server Room 1" />
                <el-option label="Server Room 2" value="Server Room 2" />
                <el-option label="Generator Room" value="Generator Room" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Criticality">
              <el-select v-model="assetForm.criticality" style="width: 100%">
                <el-option label="Critical" value="Critical" />
                <el-option label="High" value="High" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Low" value="Low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Purchase Date">
              <el-date-picker v-model="assetForm.purchaseDate" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Purchase Price">
              <el-input-number v-model="assetForm.purchasePrice" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Install Date">
              <el-date-picker v-model="assetForm.installDate" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Warranty Expiry">
              <el-date-picker v-model="assetForm.warrantyExpiry" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="assetForm.description" type="textarea" :rows="2" placeholder="Asset description..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assetDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveAsset">Save Asset</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Files, Plus, Download, Refresh, CircleCheck, Warning, CircleClose,
  Search, RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading asset register data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading asset register data...',
  'Fetching asset valuations...',
  'Analyzing depreciation...',
  'Loading maintenance records...',
  'Almost ready...'
]

// ==================== Types ====================
interface MaintenanceRecord {
  date: string
  type: string
  description: string
  cost: number
  technician: string
}

interface Document {
  name: string
  type: string
  date: string
  url: string
}

interface Asset {
  id: number
  tag: string
  name: string
  category: string
  manufacturer: string
  model: string
  serialNumber: string
  location: string
  status: 'active' | 'maintenance' | 'retired'
  healthScore: number
  criticality: string
  purchaseDate: string
  purchasePrice: number
  currentValue: number
  installDate: string
  warrantyExpiry: string
  lastMaintenance: string
  endOfLife: string
  age: number
  description: string
  maintenanceHistory: MaintenanceRecord[]
  documents: Document[]
}

// ==================== Mock Data (80 assets) ====================
const generateAssetData = (): Asset[] => {
  const categories = ['UPS', 'Generator', 'CRAC', 'Chiller', 'Switchgear', 'Server', 'Storage', 'Network']
  const manufacturers = {
    'UPS': ['Schneider Electric', 'Eaton', 'Vertiv', 'ABB'],
    'Generator': ['Caterpillar', 'Cummins', 'MTU', 'Kohler'],
    'CRAC': ['Stulz', 'Vertiv', 'Schneider Electric', 'Daikin'],
    'Chiller': ['Trane', 'Carrier', 'York', 'Daikin'],
    'Switchgear': ['ABB', 'Siemens', 'Schneider Electric', 'Eaton'],
    'Server': ['Dell', 'HP', 'Cisco', 'Lenovo'],
    'Storage': ['Dell EMC', 'NetApp', 'Pure Storage', 'HPE'],
    'Network': ['Cisco', 'Juniper', 'Arista', 'Huawei']
  }
  const locations = ['Data Center A', 'Data Center B', 'Server Room 1', 'Server Room 2', 'Generator Room', 'UPS Room', 'Chiller Plant']
  const criticalities = ['Critical', 'High', 'Medium', 'Low']
  const statuses: ('active' | 'maintenance' | 'retired')[] = ['active', 'active', 'active', 'active', 'maintenance', 'retired']

  const assets: Asset[] = []

  for (let i = 1; i <= 80; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)]
    const manufacturerList = manufacturers[category as keyof typeof manufacturers] || ['Generic']
    const manufacturer = manufacturerList[Math.floor(Math.random() * manufacturerList.length)]

    const purchaseDate = new Date()
    purchaseDate.setMonth(purchaseDate.getMonth() - Math.random() * 120)
    const purchaseDateStr = purchaseDate.toISOString().slice(0, 10)

    const ageYears = (new Date().getTime() - purchaseDate.getTime()) / (1000 * 60 * 60 * 24 * 365)
    const baseHealth = Math.max(40, Math.min(100, 100 - ageYears * 8 + (Math.random() * 10 - 5)))
    const healthScore = Math.round(baseHealth)

    const purchasePrice = [5000, 10000, 25000, 50000, 100000, 250000][Math.floor(Math.random() * 6)] * (0.5 + Math.random())
    const depreciationRate = 0.1 + Math.random() * 0.1
    const currentValue = Math.round(purchasePrice * Math.pow(1 - depreciationRate, ageYears))

    const endOfLife = new Date(purchaseDate)
    endOfLife.setFullYear(endOfLife.getFullYear() + 10)

    const status = healthScore < 50 ? 'retired' : (healthScore < 70 ? 'maintenance' : 'active')

    // Generate maintenance history
    const maintenanceHistory: MaintenanceRecord[] = []
    const maintenanceCount = Math.floor(Math.random() * 8) + 2
    for (let m = 0; m < maintenanceCount; m++) {
      const maintDate = new Date(purchaseDate)
      maintDate.setMonth(maintDate.getMonth() + Math.random() * ageYears * 12)
      if (maintDate > new Date()) continue
      maintenanceHistory.push({
        date: maintDate.toISOString().slice(0, 10),
        type: Math.random() > 0.7 ? 'Corrective' : 'Preventive',
        description: `Routine ${Math.random() > 0.7 ? 'corrective' : 'preventive'} maintenance performed`,
        cost: Math.round(500 + Math.random() * 5000),
        technician: ['John Tan', 'Mike Chen', 'Ahmad Ibrahim', 'Lim Wei Ming'][Math.floor(Math.random() * 4)]
      })
    }
    maintenanceHistory.sort((a, b) => b.date.localeCompare(a.date))

    // Generate documents
    const documents: Document[] = [
      { name: `${category}_${i}_Datasheet.pdf`, type: 'Datasheet', date: purchaseDateStr, url: '#' },
      { name: `${category}_${i}_Warranty.pdf`, type: 'Warranty', date: purchaseDateStr, url: '#' },
      { name: `${category}_${i}_Installation.pdf`, type: 'Installation Guide', date: purchaseDateStr, url: '#' }
    ]

    assets.push({
      id: i,
      tag: `${category.substring(0, 3).toUpperCase()}-${String(i).padStart(4, '0')}`,
      name: `${category} ${String.fromCharCode(64 + Math.ceil(i / 10))}${((i - 1) % 10) + 1}`,
      category: category,
      manufacturer: manufacturer,
      model: `${category}-${Math.floor(Math.random() * 1000)}`,
      serialNumber: `SN${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
      location: locations[Math.floor(Math.random() * locations.length)],
      status: status,
      healthScore: healthScore,
      criticality: criticalities[Math.floor(Math.random() * criticalities.length)],
      purchaseDate: purchaseDateStr,
      purchasePrice: Math.round(purchasePrice),
      currentValue: currentValue,
      installDate: new Date(purchaseDate.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      warrantyExpiry: new Date(purchaseDate.getTime() + 3 * 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      lastMaintenance: maintenanceHistory.length > 0 ? maintenanceHistory[0].date : purchaseDateStr,
      endOfLife: endOfLife.toISOString().slice(0, 10),
      age: parseFloat(ageYears.toFixed(1)),
      description: `${manufacturer} ${category} unit installed at ${locations[Math.floor(Math.random() * locations.length)]}`,
      maintenanceHistory: maintenanceHistory,
      documents: documents
    })
  }

  return assets
}

const assets = ref<Asset[]>(generateAssetData())

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const locationFilter = ref('')
const priorityFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(15)
const detailDialogVisible = ref(false)
const assetDialogVisible = ref(false)
const dialogTitle = ref('Add Asset')
const selectedAsset = ref<Asset | null>(null)
const editingAsset = ref<Asset | null>(null)

// Chart refs
let categoryChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null
let locationChart: echarts.ECharts | null = null
let ageChart: echarts.ECharts | null = null
let depreciationChart: echarts.ECharts | null = null

const categoryChartEl = ref<HTMLElement | null>(null)
const statusChartEl = ref<HTMLElement | null>(null)
const locationChartEl = ref<HTMLElement | null>(null)
const ageChartEl = ref<HTMLElement | null>(null)
const depreciationChartEl = ref<HTMLElement | null>(null)

const assetForm = ref({
  name: '',
  tag: '',
  category: '',
  manufacturer: '',
  model: '',
  serialNumber: '',
  location: '',
  criticality: 'Medium',
  purchaseDate: '',
  purchasePrice: 0,
  installDate: '',
  warrantyExpiry: '',
  description: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalAssets = assets.value.length
  const activeAssets = assets.value.filter(a => a.status === 'active').length
  const maintenanceAssets = assets.value.filter(a => a.status === 'maintenance').length
  const retiredAssets = assets.value.filter(a => a.status === 'retired').length
  return { totalAssets, activeAssets, maintenanceAssets, retiredAssets }
})

const metrics = computed(() => {
  const totalValue = assets.value.reduce((sum, a) => sum + a.currentValue, 0)
  const avgAge = (assets.value.reduce((sum, a) => sum + a.age, 0) / assets.value.length).toFixed(1)
  const nearEOL = assets.value.filter(a => {
    const eolDate = new Date(a.endOfLife)
    const now = new Date()
    const yearsToEOL = (eolDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24 * 365)
    return yearsToEOL <= 2 && yearsToEOL > 0
  }).length
  const annualDepreciation = assets.value.reduce((sum, a) => sum + (a.purchasePrice - a.currentValue) / a.age, 0)

  return {
    totalValue,
    valueGrowth: 8.5,
    avgAge: parseFloat(avgAge),
    ageTrend: 2.3,
    nearEOL,
    annualDepreciation: Math.round(annualDepreciation),
    depreciationRate: 12.5
  }
})

const uniqueCategories = computed(() => {
  return [...new Set(assets.value.map(a => a.category))]
})

const uniqueLocations = computed(() => {
  return [...new Set(assets.value.map(a => a.location))]
})

const filteredAssets = computed(() => {
  let filtered = [...assets.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a =>
        a.name.toLowerCase().includes(search) ||
        a.tag.toLowerCase().includes(search) ||
        a.location.toLowerCase().includes(search) ||
        a.manufacturer.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(a => a.category === categoryFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(a => a.status === statusFilter.value)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(a => a.location === locationFilter.value)
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(a => a.criticality === priorityFilter.value)
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
const getHealthColor = (health: number): string => {
  if (health >= 80) return '#22c55e'
  if (health >= 60) return '#f59e0b'
  return '#ef4444'
}

const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    'UPS': 'primary', 'Generator': 'warning', 'CRAC': 'info', 'Chiller': 'danger',
    'Switchgear': 'success', 'Server': '', 'Storage': '', 'Network': ''
  }
  return map[category] || 'info'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { active: 'Active', maintenance: 'Maintenance', retired: 'Retired' }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { active: 'success', maintenance: 'warning', retired: 'info' }
  return map[status] || 'info'
}

const getCriticalityTagType = (criticality: string): string => {
  const map: Record<string, string> = { Critical: 'danger', High: 'warning', Medium: 'info', Low: '' }
  return map[criticality] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  categoryFilter.value = ''
  statusFilter.value = ''
  locationFilter.value = ''
  priorityFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initCategoryChart = () => {
  if (!categoryChartEl.value) return
  if (categoryChart) {
    categoryChart.dispose()
    categoryChart = null
  }

  const categoryMap = new Map<string, number>()
  assets.value.forEach(a => {
    categoryMap.set(a.category, (categoryMap.get(a.category) || 0) + a.currentValue)
  })

  const data = Array.from(categoryMap.entries())
      .sort((a, b) => b[1] - a[1])
      .map(([name, value]) => ({ name, value: Math.round(value / 1000) }))

  categoryChart = echarts.init(categoryChartEl.value)
  categoryChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}<br/>Value: ${c}K' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: ${c}K' },
      emphasis: { scale: true }
    }]
  })
}

const initStatusChart = () => {
  if (!statusChartEl.value) return
  if (statusChart) {
    statusChart.dispose()
    statusChart = null
  }

  const active = assets.value.filter(a => a.status === 'active').length
  const maintenance = assets.value.filter(a => a.status === 'maintenance').length
  const retired = assets.value.filter(a => a.status === 'retired').length

  statusChart = echarts.init(statusChartEl.value)
  statusChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} assets)' },
    legend: { orient: 'vertical', left: 'left', data: ['Active', 'Maintenance', 'Retired'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: active, name: 'Active', itemStyle: { color: '#22c55e' } },
        { value: maintenance, name: 'Maintenance', itemStyle: { color: '#f59e0b' } },
        { value: retired, name: 'Retired', itemStyle: { color: '#94a3b8' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initLocationChart = () => {
  if (!locationChartEl.value) return
  if (locationChart) {
    locationChart.dispose()
    locationChart = null
  }

  const locationMap = new Map<string, number>()
  assets.value.forEach(a => {
    locationMap.set(a.location, (locationMap.get(a.location) || 0) + a.currentValue)
  })

  const data = Array.from(locationMap.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 6)

  locationChart = echarts.init(locationChartEl.value)
  locationChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Value: ${c}K' },
    grid: { top: 30, left: 60, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: data.map(d => d[0]), axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Asset Value (K$)' },
    series: [{
      type: 'bar',
      data: data.map(d => Math.round(d[1] / 1000)),
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '${c}K' }
    }]
  })
}

const initAgeChart = () => {
  if (!ageChartEl.value) return
  if (ageChart) {
    ageChart.dispose()
    ageChart = null
  }

  const ageRanges = ['<1 year', '1-3 years', '3-5 years', '5-8 years', '8-10 years', '>10 years']
  const counts = [0, 0, 0, 0, 0, 0]

  assets.value.forEach(a => {
    if (a.age < 1) counts[0]++
    else if (a.age < 3) counts[1]++
    else if (a.age < 5) counts[2]++
    else if (a.age < 8) counts[3]++
    else if (a.age < 10) counts[4]++
    else counts[5]++
  })

  ageChart = echarts.init(ageChartEl.value)
  ageChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: ageRanges, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Number of Assets' },
    series: [{
      type: 'bar',
      data: counts,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const idx = params.dataIndex
          if (idx <= 1) return '#22c55e'
          if (idx <= 3) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initDepreciationChart = () => {
  if (!depreciationChartEl.value || !selectedAsset.value) return
  if (depreciationChart) {
    depreciationChart.dispose()
    depreciationChart = null
  }

  const years = []
  const values = []
  const purchaseValue = selectedAsset.value.purchasePrice
  const currentAge = selectedAsset.value.age
  const depreciationRate = 0.12

  for (let i = 0; i <= Math.min(10, Math.ceil(currentAge) + 5); i++) {
    years.push(`Year ${i}`)
    values.push(Math.round(purchaseValue * Math.pow(1 - depreciationRate, i)))
  }

  depreciationChart = echarts.init(depreciationChartEl.value)
  depreciationChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}<br/>Value: ${c}' },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Asset Value ($)' },
    series: [{
      type: 'line',
      data: values,
      smooth: true,
      lineStyle: { color: '#ef4444', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#ef4444' },
      label: { show: true, position: 'top', formatter: '${c}' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initCategoryChart()
    initStatusChart()
    initLocationChart()
    initAgeChart()
  })
}

// ==================== Actions ====================
const viewAssetDetail = (asset: Asset) => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
  nextTick(() => initDepreciationChart())
}

const viewMaintenance = (asset: Asset) => {
  viewAssetDetail(asset)
}

const editAsset = (asset: Asset | null) => {
  if (asset) {
    dialogTitle.value = 'Edit Asset'
    editingAsset.value = asset
    assetForm.value = {
      name: asset.name,
      tag: asset.tag,
      category: asset.category,
      manufacturer: asset.manufacturer,
      model: asset.model,
      serialNumber: asset.serialNumber,
      location: asset.location,
      criticality: asset.criticality,
      purchaseDate: asset.purchaseDate,
      purchasePrice: asset.purchasePrice,
      installDate: asset.installDate,
      warrantyExpiry: asset.warrantyExpiry,
      description: asset.description
    }
    assetDialogVisible.value = true
  }
}

const scheduleMaintenance = (asset: Asset | null) => {
  if (asset) {
    ElMessage.success(`Maintenance scheduled for ${asset.name}`)
  }
}

const viewAllAssets = () => {
  ElMessage.info('Viewing all assets')
}

const exportData = () => {
  ElMessage.success('Exporting asset data...')
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

const openAddAssetDialog = () => {
  dialogTitle.value = 'Add Asset'
  editingAsset.value = null
  assetForm.value = {
    name: '',
    tag: '',
    category: '',
    manufacturer: '',
    model: '',
    serialNumber: '',
    location: '',
    criticality: 'Medium',
    purchaseDate: new Date().toISOString().slice(0, 10),
    purchasePrice: 0,
    installDate: new Date().toISOString().slice(0, 10),
    warrantyExpiry: '',
    description: ''
  }
  assetDialogVisible.value = true
}

const saveAsset = () => {
  if (!assetForm.value.name || !assetForm.value.tag || !assetForm.value.category) {
    ElMessage.warning('Please fill in required fields')
    return
  }

  if (editingAsset.value) {
    ElMessage.success(`Asset ${assetForm.value.name} updated successfully`)
  } else {
    ElMessage.success(`Asset ${assetForm.value.name} added successfully`)
  }
  assetDialogVisible.value = false
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [categoryChart, statusChart, locationChart, ageChart, depreciationChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, categoryFilter, statusFilter, locationFilter, priorityFilter], () => {
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
  const charts = [categoryChart, statusChart, locationChart, ageChart, depreciationChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.asset-register-page {
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
  font-size: 28px;
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

/* Asset Detail */
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

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
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
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
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