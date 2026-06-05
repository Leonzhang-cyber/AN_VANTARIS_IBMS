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
          <span class="loading-title">Waste Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Sustainable Waste Management Platform</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="waste-management-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <div class="title-icon">
            <el-icon><Delete /></el-icon>
          </div>
          Waste Management
        </h1>
        <div class="page-subtitle">Track, monitor and optimize waste disposal and recycling</div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="openAddRecord">
          <el-icon><Plus /></el-icon> Add Record
        </el-button>
        <el-button @click="exportReport">
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
          <el-icon><Delete /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(stats.totalWaste) }}<span class="unit">kg</span></div>
          <div class="stat-label">Total Waste</div>
          <div class="stat-trend up">+8.5% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><RefreshRight /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(stats.recycledWaste) }}<span class="unit">kg</span></div>
          <div class="stat-label">Recycled</div>
          <div class="stat-trend up">+12.3% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.recyclingRate }}<span class="unit">%</span></div>
          <div class="stat-label">Recycling Rate</div>
          <div class="stat-trend up">+3.2% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ formatNumber(stats.costSavings) }}</div>
          <div class="stat-label">Cost Savings</div>
          <div class="stat-trend up">+5.7% vs last month</div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot"></span>
            Waste by Category
          </div>
          <el-radio-group v-model="chartType" size="small">
            <el-radio-button label="pie">Pie Chart</el-radio-button>
            <el-radio-button label="bar">Bar Chart</el-radio-button>
          </el-radio-group>
        </div>
        <div class="chart-container" ref="wasteChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div class="chart-title">
            <span class="title-dot green"></span>
            Monthly Waste Trends
          </div>
          <span class="chart-badge">Last 6 months</span>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search waste type or location..."
            style="width: 260px"
            clearable
            :prefix-icon="Search"
            class="filter-input"
        />
        <el-select v-model="categoryFilter" placeholder="Waste Category" clearable style="width: 150px" class="filter-select">
          <el-option label="All Categories" value="" />
          <el-option label="General" value="General" />
          <el-option label="Recyclable" value="Recyclable" />
          <el-option label="Hazardous" value="Hazardous" />
          <el-option label="E-Waste" value="E-Waste" />
          <el-option label="Organic" value="Organic" />
        </el-select>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            class="date-picker"
        />
      </div>
      <div class="filter-right">
        <div class="record-count">
          <el-icon><Document /></el-icon>
          {{ filteredRecords.length }} Records
        </div>
      </div>
    </div>

    <!-- Waste Records Cards Grid -->
    <div class="records-grid">
      <div
          v-for="record in paginatedRecords"
          :key="record.id"
          class="record-card"
          :class="record.category.toLowerCase()"
      >
        <div class="card-header">
          <div class="waste-icon" :class="record.category.toLowerCase()">
            <el-icon v-if="record.category === 'General'"><Delete /></el-icon>
            <el-icon v-else-if="record.category === 'Recyclable'"><RefreshRight /></el-icon>
            <el-icon v-else-if="record.category === 'Hazardous'"><Warning /></el-icon>
            <el-icon v-else-if="record.category === 'E-Waste'"><Monitor /></el-icon>
            <el-icon v-else><Apple /></el-icon>
          </div>
          <div class="card-info">
            <div class="waste-type">{{ record.wasteType }}</div>
            <div class="waste-date">{{ record.date }}</div>
          </div>
          <div class="recycled-badge" v-if="record.recycled">
            <el-icon><CircleCheck /></el-icon> Recycled
          </div>
          <div class="recycled-badge no" v-else>
            <el-icon><CircleClose /></el-icon> Landfill
          </div>
        </div>

        <div class="card-details">
          <div class="detail-item">
            <span class="label">Quantity:</span>
            <span class="value">{{ record.quantity }} <span class="unit">kg</span></span>
          </div>
          <div class="detail-item">
            <span class="label">Location:</span>
            <span class="value">{{ record.collectionPoint }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Disposal:</span>
            <span class="value">{{ record.disposalMethod }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Vendor:</span>
            <span class="value">{{ record.vendor }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Cost:</span>
            <span class="value cost">${{ formatNumber(record.cost) }}</span>
          </div>
        </div>

        <div class="card-footer">
          <el-button text size="small" @click="viewRecord(record)">
            View Details
          </el-button>
          <el-button text size="small" type="danger" @click="deleteRecord(record)">
            Delete
          </el-button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredRecords.length === 0" class="empty-state">
        <el-empty description="No waste records found">
          <el-button type="primary" @click="openAddRecord">Add Record</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="filteredRecords.length > 0">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[9, 18, 27]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next"
          background
      />
    </div>

    <!-- Add/Edit Record Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" class="record-dialog" destroy-on-close>
      <el-form :model="recordForm" :rules="formRules" ref="formRef" label-width="130px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Date" prop="date">
              <el-date-picker
                  v-model="recordForm.date"
                  type="date"
                  placeholder="Select date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Waste Type" prop="wasteType">
              <el-input v-model="recordForm.wasteType" placeholder="Enter waste type" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Category" prop="category">
              <el-select v-model="recordForm.category" placeholder="Select category" style="width: 100%">
                <el-option label="General" value="General" />
                <el-option label="Recyclable" value="Recyclable" />
                <el-option label="Hazardous" value="Hazardous" />
                <el-option label="E-Waste" value="E-Waste" />
                <el-option label="Organic" value="Organic" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Quantity (kg)" prop="quantity">
              <el-input-number v-model="recordForm.quantity" :min="0" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Collection Point" prop="collectionPoint">
              <el-select v-model="recordForm.collectionPoint" placeholder="Select location" style="width: 100%">
                <el-option label="Main Bin Area" value="Main Bin Area" />
                <el-option label="Loading Dock" value="Loading Dock" />
                <el-option label="Server Room" value="Server Room" />
                <el-option label="Data Center" value="Data Center" />
                <el-option label="Office Area" value="Office Area" />
                <el-option label="Cafeteria" value="Cafeteria" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Disposal Method" prop="disposalMethod">
              <el-select v-model="recordForm.disposalMethod" placeholder="Select method" style="width: 100%">
                <el-option label="Landfill" value="Landfill" />
                <el-option label="Recycling Center" value="Recycling Center" />
                <el-option label="Incineration" value="Incineration" />
                <el-option label="Composting" value="Composting" />
                <el-option label="E-Waste Recycling" value="E-Waste Recycling" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Vendor" prop="vendor">
              <el-input v-model="recordForm.vendor" placeholder="Enter vendor name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Cost ($)" prop="cost">
              <el-input-number v-model="recordForm.cost" :min="0" :step="50" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Recycled" prop="recycled">
          <el-switch v-model="recordForm.recycled" active-text="Yes" inactive-text="No" />
        </el-form-item>

        <el-form-item label="Remarks" prop="remarks">
          <el-input v-model="recordForm.remarks" type="textarea" :rows="2" placeholder="Additional remarks..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRecord">Save Record</el-button>
      </template>
    </el-dialog>

    <!-- View Record Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="selectedRecord?.wasteType" width="650px" class="view-dialog">
      <div v-if="selectedRecord" class="record-detail">
        <div class="detail-header" :class="selectedRecord.category.toLowerCase()">
          <div class="detail-icon">
            <el-icon v-if="selectedRecord.category === 'General'"><Delete /></el-icon>
            <el-icon v-else-if="selectedRecord.category === 'Recyclable'"><RefreshRight /></el-icon>
            <el-icon v-else-if="selectedRecord.category === 'Hazardous'"><Warning /></el-icon>
            <el-icon v-else-if="selectedRecord.category === 'E-Waste'"><Monitor /></el-icon>
            <el-icon v-else><Apple /></el-icon>
          </div>
          <div class="detail-title">
            <h3>{{ selectedRecord.wasteType }}</h3>
            <p>{{ selectedRecord.date }}</p>
          </div>
          <div class="detail-status">
            <el-tag :type="selectedRecord.recycled ? 'success' : 'info'" size="large">
              {{ selectedRecord.recycled ? 'Recycled' : 'Landfill' }}
            </el-tag>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryTagType(selectedRecord.category)" size="small">{{ selectedRecord.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Quantity">{{ selectedRecord.quantity }} kg</el-descriptions-item>
          <el-descriptions-item label="Collection Point">{{ selectedRecord.collectionPoint }}</el-descriptions-item>
          <el-descriptions-item label="Disposal Method">{{ selectedRecord.disposalMethod }}</el-descriptions-item>
          <el-descriptions-item label="Vendor">{{ selectedRecord.vendor }}</el-descriptions-item>
          <el-descriptions-item label="Cost">${{ formatNumber(selectedRecord.cost) }}</el-descriptions-item>
          <el-descriptions-item label="Remarks" :span="2">{{ selectedRecord.remarks || 'No remarks' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editRecord(selectedRecord)">Edit Record</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Delete, Plus, Download, Refresh, Search, RefreshRight,
  TrendCharts, Money, Document, Warning, Monitor, Apple,
  CircleCheck, CircleClose
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading waste data...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading waste data...',
  'Loading recycling metrics...',
  'Analyzing trends...',
  'Almost ready...'
]

// ==================== Types ====================
interface WasteRecord {
  id: number
  date: string
  wasteType: string
  category: string
  quantity: number
  collectionPoint: string
  disposalMethod: string
  vendor: string
  cost: number
  recycled: boolean
  remarks: string
}

// ==================== Mock Data ====================
const wasteRecords = ref<WasteRecord[]>([
  { id: 1, date: '2024-06-01', wasteType: 'Cardboard Boxes', category: 'Recyclable', quantity: 150, collectionPoint: 'Main Bin Area', disposalMethod: 'Recycling Center', vendor: 'Green Earth Recycling', cost: 75, recycled: true, remarks: 'Monthly cardboard collection' },
  { id: 2, date: '2024-06-02', wasteType: 'Office Paper', category: 'Recyclable', quantity: 80, collectionPoint: 'Office Area', disposalMethod: 'Recycling Center', vendor: 'Green Earth Recycling', cost: 40, recycled: true, remarks: '' },
  { id: 3, date: '2024-06-03', wasteType: 'Plastic Bottles', category: 'Recyclable', quantity: 45, collectionPoint: 'Cafeteria', disposalMethod: 'Recycling Center', vendor: 'Plastic Recycling Co.', cost: 22, recycled: true, remarks: 'Mixed plastics' },
  { id: 4, date: '2024-06-04', wasteType: 'General Trash', category: 'General', quantity: 300, collectionPoint: 'Main Bin Area', disposalMethod: 'Landfill', vendor: 'City Waste Management', cost: 150, recycled: false, remarks: '' },
  { id: 5, date: '2024-06-05', wasteType: 'Electronic Waste', category: 'E-Waste', quantity: 35, collectionPoint: 'Server Room', disposalMethod: 'E-Waste Recycling', vendor: 'Tech Recycle Pte Ltd', cost: 85, recycled: true, remarks: 'Old servers and switches' },
  { id: 6, date: '2024-06-06', wasteType: 'UPS Batteries', category: 'Hazardous', quantity: 12, collectionPoint: 'Maintenance Room', disposalMethod: 'Recycling Center', vendor: 'Battery Recycling Co.', cost: 60, recycled: true, remarks: 'UPS batteries replacement' },
  { id: 7, date: '2024-06-07', wasteType: 'Food Waste', category: 'Organic', quantity: 120, collectionPoint: 'Cafeteria', disposalMethod: 'Composting', vendor: 'Compost Solutions', cost: 30, recycled: true, remarks: 'Food waste from cafeteria' },
  { id: 8, date: '2024-06-08', wasteType: 'Metal Scrap', category: 'Recyclable', quantity: 60, collectionPoint: 'Loading Dock', disposalMethod: 'Recycling Center', vendor: 'Metal Recycling Ltd', cost: 30, recycled: true, remarks: '' },
  { id: 9, date: '2024-06-09', wasteType: 'Glass Bottles', category: 'Recyclable', quantity: 40, collectionPoint: 'Main Bin Area', disposalMethod: 'Recycling Center', vendor: 'Glass Recycling Co.', cost: 20, recycled: true, remarks: '' },
  { id: 10, date: '2024-06-10', wasteType: 'Chemical Containers', category: 'Hazardous', quantity: 25, collectionPoint: 'Maintenance Room', disposalMethod: 'Incineration', vendor: 'HazMat Solutions', cost: 200, recycled: false, remarks: 'Chemical containers from cleaning' },
  { id: 11, date: '2024-05-25', wasteType: 'Corrugated Cardboard', category: 'Recyclable', quantity: 140, collectionPoint: 'Main Bin Area', disposalMethod: 'Recycling Center', vendor: 'Green Earth Recycling', cost: 70, recycled: true, remarks: '' },
  { id: 12, date: '2024-05-26', wasteType: 'Network Equipment', category: 'E-Waste', quantity: 28, collectionPoint: 'Data Center', disposalMethod: 'E-Waste Recycling', vendor: 'Tech Recycle Pte Ltd', cost: 68, recycled: true, remarks: 'Old network equipment' },
  { id: 13, date: '2024-05-27', wasteType: 'Mixed Waste', category: 'General', quantity: 280, collectionPoint: 'Main Bin Area', disposalMethod: 'Landfill', vendor: 'City Waste Management', cost: 140, recycled: false, remarks: '' },
  { id: 14, date: '2024-05-28', wasteType: 'Plastic Packaging', category: 'Recyclable', quantity: 50, collectionPoint: 'Office Area', disposalMethod: 'Recycling Center', vendor: 'Plastic Recycling Co.', cost: 25, recycled: true, remarks: '' },
  { id: 15, date: '2024-05-29', wasteType: 'Battery Packs', category: 'Hazardous', quantity: 10, collectionPoint: 'Server Room', disposalMethod: 'Recycling Center', vendor: 'Battery Recycling Co.', cost: 50, recycled: true, remarks: 'UPS battery disposal' },
  { id: 16, date: '2024-05-20', wasteType: 'Printer Paper', category: 'Recyclable', quantity: 75, collectionPoint: 'Office Area', disposalMethod: 'Recycling Center', vendor: 'Green Earth Recycling', cost: 38, recycled: true, remarks: '' },
  { id: 17, date: '2024-05-21', wasteType: 'Kitchen Waste', category: 'Organic', quantity: 110, collectionPoint: 'Cafeteria', disposalMethod: 'Composting', vendor: 'Compost Solutions', cost: 28, recycled: true, remarks: '' },
  { id: 18, date: '2024-05-22', wasteType: 'Aluminum Cans', category: 'Recyclable', quantity: 55, collectionPoint: 'Loading Dock', disposalMethod: 'Recycling Center', vendor: 'Metal Recycling Ltd', cost: 28, recycled: true, remarks: '' },
  { id: 19, date: '2024-05-23', wasteType: 'Hazardous Liquids', category: 'Hazardous', quantity: 20, collectionPoint: 'Maintenance Room', disposalMethod: 'Incineration', vendor: 'HazMat Solutions', cost: 160, recycled: false, remarks: '' },
  { id: 20, date: '2024-05-24', wasteType: 'Glass Jars', category: 'Recyclable', quantity: 35, collectionPoint: 'Main Bin Area', disposalMethod: 'Recycling Center', vendor: 'Glass Recycling Co.', cost: 18, recycled: true, remarks: '' },
  { id: 21, date: '2024-05-15', wasteType: 'Monitors & Screens', category: 'E-Waste', quantity: 30, collectionPoint: 'Data Center', disposalMethod: 'E-Waste Recycling', vendor: 'Tech Recycle Pte Ltd', cost: 72, recycled: true, remarks: 'Old monitors and peripherals' },
  { id: 22, date: '2024-05-16', wasteType: 'Shipping Boxes', category: 'Recyclable', quantity: 160, collectionPoint: 'Main Bin Area', disposalMethod: 'Recycling Center', vendor: 'Green Earth Recycling', cost: 80, recycled: true, remarks: '' },
  { id: 23, date: '2024-05-17', wasteType: 'General Debris', category: 'General', quantity: 320, collectionPoint: 'Main Bin Area', disposalMethod: 'Landfill', vendor: 'City Waste Management', cost: 160, recycled: false, remarks: '' },
  { id: 24, date: '2024-05-18', wasteType: 'Lithium Batteries', category: 'Hazardous', quantity: 8, collectionPoint: 'Server Room', disposalMethod: 'Recycling Center', vendor: 'Battery Recycling Co.', cost: 40, recycled: true, remarks: '' },
  { id: 25, date: '2024-05-19', wasteType: 'Plastic Cups', category: 'Recyclable', quantity: 55, collectionPoint: 'Cafeteria', disposalMethod: 'Recycling Center', vendor: 'Plastic Recycling Co.', cost: 28, recycled: true, remarks: '' }
])

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const dateRange = ref<string[]>([])
const chartType = ref('pie')
const currentPage = ref(1)
const pageSize = ref(9)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('Add Waste Record')
const selectedRecord = ref<WasteRecord | null>(null)
const editingRecord = ref<WasteRecord | null>(null)
const formRef = ref()

let wasteChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
const wasteChartEl = ref<HTMLElement | null>(null)
const trendChartEl = ref<HTMLElement | null>(null)

const recordForm = ref({
  id: null as number | null,
  date: '',
  wasteType: '',
  category: '',
  quantity: 0,
  collectionPoint: '',
  disposalMethod: '',
  vendor: '',
  cost: 0,
  recycled: false,
  remarks: ''
})

const formRules = {
  date: [{ required: true, message: 'Please select date', trigger: 'change' }],
  wasteType: [{ required: true, message: 'Please enter waste type', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  quantity: [{ required: true, message: 'Please enter quantity', trigger: 'blur' }],
  vendor: [{ required: true, message: 'Please enter vendor', trigger: 'blur' }]
}

// ==================== Computed ====================
const stats = computed(() => {
  const totalWaste = wasteRecords.value.reduce((sum, r) => sum + r.quantity, 0)
  const recycledWaste = wasteRecords.value.filter(r => r.recycled).reduce((sum, r) => sum + r.quantity, 0)
  const recyclingRate = totalWaste > 0 ? Math.round((recycledWaste / totalWaste) * 100) : 0
  const costSavings = wasteRecords.value.filter(r => r.recycled).reduce((sum, r) => sum + r.cost * 0.35, 0)

  return { totalWaste, recycledWaste, recyclingRate, costSavings: Math.round(costSavings) }
})

const filteredRecords = computed(() => {
  let filtered = [...wasteRecords.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.wasteType.toLowerCase().includes(search) ||
        r.vendor.toLowerCase().includes(search) ||
        r.collectionPoint.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(r => r.category === categoryFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    filtered = filtered.filter(r =>
        r.date >= dateRange.value[0] && r.date <= dateRange.value[1]
    )
  }

  return filtered
})

const totalRecords = computed(() => filteredRecords.value.length)

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// ==================== Helper Functions ====================
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    General: 'info', Recyclable: 'success', Hazardous: 'danger', 'E-Waste': 'warning', Organic: 'success'
  }
  return map[category] || 'info'
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const openAddRecord = () => {
  dialogTitle.value = 'Add Waste Record'
  editingRecord.value = null
  recordForm.value = {
    id: null,
    date: new Date().toISOString().slice(0, 10),
    wasteType: '',
    category: '',
    quantity: 0,
    collectionPoint: '',
    disposalMethod: '',
    vendor: '',
    cost: 0,
    recycled: false,
    remarks: ''
  }
  dialogVisible.value = true
}

const editRecord = (record: WasteRecord | null) => {
  if (!record) return
  dialogTitle.value = 'Edit Waste Record'
  editingRecord.value = record
  recordForm.value = {
    id: record.id,
    date: record.date,
    wasteType: record.wasteType,
    category: record.category,
    quantity: record.quantity,
    collectionPoint: record.collectionPoint,
    disposalMethod: record.disposalMethod,
    vendor: record.vendor,
    cost: record.cost,
    recycled: record.recycled,
    remarks: record.remarks
  }
  dialogVisible.value = true
}

const viewRecord = (record: WasteRecord) => {
  selectedRecord.value = record
  viewDialogVisible.value = true
}

const deleteRecord = (record: WasteRecord) => {
  ElMessageBox.confirm(
      `Delete waste record for "${record.wasteType}" on ${record.date}?`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = wasteRecords.value.findIndex(r => r.id === record.id)
    if (index !== -1) {
      wasteRecords.value.splice(index, 1)
      ElMessage.success('Record deleted')
      refreshCharts()
    }
  }).catch(() => {})
}

const saveRecord = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    if (editingRecord.value) {
      const index = wasteRecords.value.findIndex(r => r.id === editingRecord.value!.id)
      if (index !== -1) {
        wasteRecords.value[index] = {
          ...wasteRecords.value[index],
          date: recordForm.value.date,
          wasteType: recordForm.value.wasteType,
          category: recordForm.value.category,
          quantity: recordForm.value.quantity,
          collectionPoint: recordForm.value.collectionPoint,
          disposalMethod: recordForm.value.disposalMethod,
          vendor: recordForm.value.vendor,
          cost: recordForm.value.cost,
          recycled: recordForm.value.recycled,
          remarks: recordForm.value.remarks
        }
        ElMessage.success('Record updated')
      }
    } else {
      const newId = Math.max(...wasteRecords.value.map(r => r.id), 0) + 1
      wasteRecords.value.push({
        id: newId,
        date: recordForm.value.date,
        wasteType: recordForm.value.wasteType,
        category: recordForm.value.category,
        quantity: recordForm.value.quantity,
        collectionPoint: recordForm.value.collectionPoint,
        disposalMethod: recordForm.value.disposalMethod,
        vendor: recordForm.value.vendor,
        cost: recordForm.value.cost,
        recycled: recordForm.value.recycled,
        remarks: recordForm.value.remarks
      })
      ElMessage.success('Record added')
    }

    dialogVisible.value = false
    refreshCharts()
  })
}

const exportReport = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Waste report exported')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
  refreshCharts()
}

// ==================== Charts ====================
const initWasteChart = () => {
  if (!wasteChartEl.value) return
  if (wasteChart) wasteChart.dispose()

  const categories = ['General', 'Recyclable', 'Hazardous', 'E-Waste', 'Organic']
  const quantities = [900, 635, 67, 93, 230]
  const colors = ['#64748b', '#22c55e', '#ef4444', '#f59e0b', '#8b5cf6']

  wasteChart = echarts.init(wasteChartEl.value)

  if (chartType.value === 'pie') {
    wasteChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} kg ({d}%)' },
      legend: { orient: 'vertical', left: 'left', textStyle: { color: '#475569' }, data: categories },
      series: [{
        type: 'pie',
        radius: ['45%', '65%'],
        center: ['50%', '50%'],
        data: categories.map((name, idx) => ({ value: quantities[idx], name, itemStyle: { color: colors[idx] } })),
        label: { show: true, formatter: '{b}: {d}%', fontSize: 11 },
        emphasis: { scale: true },
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
      }]
    })
  } else {
    wasteChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}: {c} kg' },
      grid: { top: 30, left: 60, right: 30, bottom: 20, containLabel: true },
      xAxis: { type: 'category', data: categories, axisLabel: { rotate: 15, fontSize: 11 } },
      yAxis: { type: 'value', name: 'Quantity (kg)', nameTextStyle: { color: '#64748b' } },
      series: [{
        type: 'bar',
        data: quantities,
        itemStyle: {
          borderRadius: [6, 6, 0, 0],
          color: (params: any) => colors[params.dataIndex]
        },
        label: { show: true, position: 'top', formatter: '{c} kg', fontSize: 11 }
      }]
    })
  }
  wasteChart.resize()
}

const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) trendChart.dispose()

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  const totalData = [850, 820, 780, 790, 810, 845]
  const recycledData = [520, 510, 490, 495, 510, 530]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Total Waste', 'Recycled'], bottom: 0, textStyle: { color: '#475569' } },
    grid: { top: 40, left: 60, right: 30, bottom: 40, containLabel: true },
    xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', name: 'Quantity (kg)', nameTextStyle: { color: '#64748b' } },
    series: [
      { name: 'Total Waste', type: 'line', data: totalData, smooth: true, lineStyle: { color: '#3b82f6', width: 3 }, symbol: 'circle', symbolSize: 8, areaStyle: { opacity: 0.1, color: '#3b82f6' } },
      { name: 'Recycled', type: 'line', data: recycledData, smooth: true, lineStyle: { color: '#22c55e', width: 3 }, symbol: 'circle', symbolSize: 8, areaStyle: { opacity: 0.1, color: '#22c55e' } }
    ]
  })
  trendChart.resize()
}

const refreshCharts = () => {
  nextTick(() => {
    initWasteChart()
    initTrendChart()
  })
}

// ==================== Watch for chart updates ====================
watch(chartType, () => {
  nextTick(() => initWasteChart())
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
      nextTick(() => {
        initWasteChart()
        initTrendChart()
      })
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
.waste-management-page {
  min-height: 100vh;
  background: #f0f2f6;
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

.header-left {
  flex: 1;
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

.title-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-right {
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
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
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

.stat-icon.blue { background: linear-gradient(135deg, #eef2ff, #e0e7ff); color: #3b82f6; }
.stat-icon.green { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #22c55e; }
.stat-icon.orange { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #f59e0b; }
.stat-icon.purple { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); color: #8b5cf6; }

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

.stat-trend {
  font-size: 11px;
  margin-top: 6px;
}

.stat-trend.up { color: #22c55e; }

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.title-dot {
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
}

.title-dot.green { background: #22c55e; }

.chart-badge {
  font-size: 11px;
  padding: 4px 10px;
  background: #f1f5f9;
  border-radius: 20px;
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
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-input :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.filter-select :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.date-picker :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: none;
}

.record-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
  background: #f1f5f9;
  padding: 6px 14px;
  border-radius: 20px;
}

/* Records Grid */
.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.record-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.record-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.record-card.general { border-top: 4px solid #64748b; }
.record-card.recyclable { border-top: 4px solid #22c55e; }
.record-card.hazardous { border-top: 4px solid #ef4444; }
.record-card.e-waste { border-top: 4px solid #f59e0b; }
.record-card.organic { border-top: 4px solid #8b5cf6; }

.card-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid #f1f5f9;
}

.waste-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.waste-icon.general { background: #f1f5f9; color: #64748b; }
.waste-icon.recyclable { background: #dcfce7; color: #22c55e; }
.waste-icon.hazardous { background: #fee2e2; color: #ef4444; }
.waste-icon.e-waste { background: #fef3c7; color: #f59e0b; }
.waste-icon.organic { background: #f3e8ff; color: #8b5cf6; }

.card-info {
  flex: 1;
}

.waste-type {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 4px;
}

.waste-date {
  font-size: 11px;
  color: #64748b;
}

.recycled-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 20px;
  background: #dcfce7;
  color: #16a34a;
}

.recycled-badge.no {
  background: #fee2e2;
  color: #dc2626;
}

.card-details {
  padding: 16px 20px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  background: #fafcff;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  font-size: 13px;
}

.detail-item .label {
  color: #64748b;
}

.detail-item .value {
  font-weight: 500;
  color: #1e293b;
}

.detail-item .value.cost {
  color: #3b82f6;
  font-weight: 600;
}

.detail-item .value .unit {
  font-size: 10px;
  color: #64748b;
}

.card-footer {
  padding: 12px 20px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  border-top: 1px solid #f1f5f9;
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
.record-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.view-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.record-detail {
  padding: 8px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 20px;
}

.detail-header.general { background: #f1f5f9; }
.detail-header.recyclable { background: #dcfce7; }
.detail-header.hazardous { background: #fee2e2; }
.detail-header.e-waste { background: #fef3c7; }
.detail-header.organic { background: #f3e8ff; }

.detail-icon {
  width: 60px;
  height: 60px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.detail-header.general .detail-icon { background: white; color: #64748b; }
.detail-header.recyclable .detail-icon { background: white; color: #22c55e; }
.detail-header.hazardous .detail-icon { background: white; color: #ef4444; }
.detail-header.e-waste .detail-icon { background: white; color: #f59e0b; }
.detail-header.organic .detail-icon { background: white; color: #8b5cf6; }

.detail-title {
  flex: 1;
}

.detail-title h3 {
  margin: 0 0 4px;
  font-size: 20px;
  color: #1e293b;
}

.detail-title p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
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
  .filter-left .el-select,
  .filter-left .el-date-editor {
    width: 100% !important;
  }

  .records-grid {
    grid-template-columns: 1fr;
  }
}
</style>