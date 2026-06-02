<template>
  <!-- Global Pre Loading Screen -->
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
        <div class="loading-tip">ASSET TAG MANAGEMENT</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="asset-tag-container">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalAssets }}</span>
          <span class="stat-label">Total Assets</span>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ taggedAssets }}</span>
          <span class="stat-label">Tagged Assets</span>
        </div>
        <div class="stat-percent">{{ taggedPercent }}%</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ expiringWarranty }}</span>
          <span class="stat-label">Warranty Expiring</span>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalValue.toLocaleString() }}</span>
          <span class="stat-label">Total Value ($)</span>
        </div>
      </div>
    </div>

    <!-- 筛选卡片 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="Asset Name">
          <el-input v-model="filterForm.assetName" placeholder="Search by name" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="Tag ID">
          <el-input v-model="filterForm.tagId" placeholder="Search by tag ID" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="Category">
          <el-select v-model="filterForm.category" placeholder="Category" clearable style="width: 140px">
            <el-option label="HVAC" value="hvac" />
            <el-option label="Lighting" value="lighting" />
            <el-option label="Security" value="security" />
            <el-option label="Fire Alarm" value="fire" />
            <el-option label="Plumbing" value="plumbing" />
            <el-option label="Electrical" value="electrical" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location">
          <el-select v-model="filterForm.location" placeholder="Location" clearable style="width: 140px">
            <el-option label="Basement B2" value="Basement B2" />
            <el-option label="Parking B1" value="Parking B1" />
            <el-option label="Lobby 1F" value="Lobby 1F" />
            <el-option label="Office 2F" value="Office 2F" />
            <el-option label="Executive 3F" value="Executive 3F" />
            <el-option label="Roof" value="Roof" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetFilter">Reset</el-button>
          <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
          <el-button type="success" :icon="Plus" @click="openCreateDialog">Generate Asset Tag</el-button>
          <el-button :icon="Download" @click="exportTags">Export Tags</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">Assets by Category</div>
        </template>
        <div ref="pieChartRef" class="pie-chart-box"></div>
      </el-card>

      <el-card class="stats-chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">Assets by Location</div>
        </template>
        <div ref="barChartRef" class="bar-chart-box"></div>
      </el-card>
    </div>

    <!-- 资产标签列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Asset Tags List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="400" v-loading="tableLoading">
        <el-table-column label="Tag ID" prop="tagId" width="140" />
        <el-table-column label="Asset Name" prop="assetName" min-width="200" show-overflow-tooltip />
        <el-table-column label="Category" prop="category" width="120">
          <template #default="scope">
            <el-tag :type="getCategoryTag(scope.row.category)" size="small">{{ getCategoryLabel(scope.row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Location" prop="location" width="140" />
        <el-table-column label="QR Code" width="100">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="showQRCode(scope.row)">
              <el-icon><View /></el-icon> View
            </el-button>
          </template>
        </el-table-column>
        <el-table-column label="Purchase Date" prop="purchaseDate" width="120" />
        <el-table-column label="Warranty End" prop="warrantyEnd" width="120">
          <template #default="scope">
            <span :class="{ 'text-warning': isWarrantyExpiring(scope.row.warrantyEnd), 'text-danger': isWarrantyExpired(scope.row.warrantyEnd) }">
              {{ scope.row.warrantyEnd }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Value" prop="value" width="120">
          <template #default="scope">${{ scope.row.value.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="Status" prop="status" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'" size="small">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Operation" width="160" fixed="right" align="center">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="printTag(scope.row)">Print</el-button>
            <el-button text type="danger" size="small" @click="deleteTag(scope.row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrap">
        <el-pagination
            v-model:current-page="pageInfo.pageNum"
            v-model:page-size="pageInfo.pageSize"
            :page-sizes="[15, 30, 50, 100]"
            :total="pageInfo.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 生成标签对话框 -->
    <el-dialog v-model="dialogVisible" title="Generate Asset Tag" width="600px" @closed="resetForm">
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Asset Name" prop="assetName">
              <el-input v-model="tagForm.assetName" placeholder="e.g., AHU-B2-01" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Category" prop="category">
              <el-select v-model="tagForm.category" style="width: 100%">
                <el-option label="HVAC" value="hvac" />
                <el-option label="Lighting" value="lighting" />
                <el-option label="Security" value="security" />
                <el-option label="Fire Alarm" value="fire" />
                <el-option label="Plumbing" value="plumbing" />
                <el-option label="Electrical" value="electrical" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Model" prop="model">
              <el-input v-model="tagForm.model" placeholder="e.g., Carrier 39G" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Manufacturer" prop="manufacturer">
              <el-input v-model="tagForm.manufacturer" placeholder="e.g., Carrier" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Serial Number" prop="serialNumber">
              <el-input v-model="tagForm.serialNumber" placeholder="Unique serial number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Location" prop="location">
              <el-select v-model="tagForm.location" style="width: 100%">
                <el-option label="Basement B2" value="Basement B2" />
                <el-option label="Parking B1" value="Parking B1" />
                <el-option label="Lobby 1F" value="Lobby 1F" />
                <el-option label="Office 2F" value="Office 2F" />
                <el-option label="Executive 3F" value="Executive 3F" />
                <el-option label="Roof" value="Roof" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Purchase Date" prop="purchaseDate">
              <el-date-picker v-model="tagForm.purchaseDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Warranty End" prop="warrantyEnd">
              <el-date-picker v-model="tagForm.warrantyEnd" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Purchase Value ($)" prop="value">
              <el-input-number v-model="tagForm.value" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Tag Type" prop="tagType">
              <el-radio-group v-model="tagForm.tagType">
                <el-radio label="qr">QR Code</el-radio>
                <el-radio label="barcode">Barcode</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Notes">
          <el-input v-model="tagForm.notes" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="generateTag" :loading="generating">Generate Tag</el-button>
      </template>
    </el-dialog>

    <!-- QR Code 查看对话框 -->
    <el-dialog v-model="qrDialogVisible" :title="`QR Code - ${selectedAsset?.assetName}`" width="400px">
      <div class="qr-container">
        <canvas ref="qrCanvasRef" class="qr-canvas"></canvas>
        <div class="qr-info">
          <p><strong>Tag ID:</strong> {{ selectedAsset?.tagId }}</p>
          <p><strong>Asset:</strong> {{ selectedAsset?.assetName }}</p>
          <p><strong>Location:</strong> {{ selectedAsset?.location }}</p>
        </div>
        <div class="qr-actions">
          <el-button type="primary" size="small" @click="downloadQRCode">Download QR Code</el-button>
          <el-button size="small" @click="printQRCode">Print</el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 批量打印对话框 -->
    <el-dialog v-model="batchPrintDialogVisible" title="Batch Print Tags" width="500px">
      <div class="batch-print">
        <p>Select tags to print:</p>
        <el-select
            v-model="selectedPrintTags"
            multiple
            filterable
            placeholder="Select tags"
            style="width: 100%"
        >
          <el-option v-for="asset in allAssets" :key="asset.id" :label="`${asset.tagId} - ${asset.assetName}`" :value="asset.id" />
        </el-select>
        <div class="print-options">
          <el-checkbox v-model="printOptions.includeQR">Include QR Code</el-checkbox>
          <el-checkbox v-model="printOptions.includeBarcode">Include Barcode</el-checkbox>
          <el-checkbox v-model="printOptions.includeDetails">Include Asset Details</el-checkbox>
        </div>
      </div>
      <template #footer>
        <el-button @click="batchPrintDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmBatchPrint" :disabled="selectedPrintTags.length === 0">Print {{ selectedPrintTags.length }} Tags</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import QRCode from 'qrcode'
import type { FormInstance, FormRules } from 'element-plus'
import { Connection, CircleCheckFilled, WarningFilled, DataLine, Refresh, Plus, Download, View } from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading asset data...',
  'Generating QR codes...',
  'Almost ready...'
]

// ========== Chart References ==========
const pieChartRef = ref<HTMLDivElement | null>(null)
const barChartRef = ref<HTMLDivElement | null>(null)
let pieInstance: echarts.ECharts | null = null
let barInstance: echarts.ECharts | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const generating = ref(false)
const tagFormRef = ref<FormInstance>()
const qrCanvasRef = ref<HTMLCanvasElement>()

// ========== Filter Form ==========
const filterForm = reactive({
  assetName: '',
  tagId: '',
  category: '',
  location: ''
})

// ========== Pagination ==========
const pageInfo = reactive({
  pageNum: 1,
  pageSize: 15,
  total: 0
})

// ========== Dialog State ==========
const dialogVisible = ref(false)
const qrDialogVisible = ref(false)
const batchPrintDialogVisible = ref(false)
const selectedAsset = ref<any>(null)
const selectedPrintTags = ref<string[]>([])
const printOptions = ref({
  includeQR: true,
  includeBarcode: true,
  includeDetails: true
})

// ========== Asset Data ==========
const allAssets = ref<any[]>([])

// 统计数据
const totalAssets = computed(() => allAssets.value.length)
const taggedAssets = computed(() => allAssets.value.filter(a => a.tagGenerated).length)
const taggedPercent = computed(() => totalAssets.value ? Math.round(taggedAssets.value / totalAssets.value * 100) : 0)
const expiringWarranty = computed(() => allAssets.value.filter(a => isWarrantyExpiring(a.warrantyEnd)).length)
const totalValue = computed(() => allAssets.value.reduce((sum, a) => sum + a.value, 0))

// 分页数据
const paginatedTableData = computed(() => {
  let filtered = [...allAssets.value]

  if (filterForm.assetName) {
    filtered = filtered.filter(a => a.assetName?.toLowerCase().includes(filterForm.assetName.toLowerCase()))
  }
  if (filterForm.tagId) {
    filtered = filtered.filter(a => a.tagId?.toLowerCase().includes(filterForm.tagId.toLowerCase()))
  }
  if (filterForm.category) {
    filtered = filtered.filter(a => a.category === filterForm.category)
  }
  if (filterForm.location) {
    filtered = filtered.filter(a => a.location === filterForm.location)
  }

  pageInfo.total = filtered.length
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return filtered.slice(start, start + pageInfo.pageSize)
})

// ========== Form Data ==========
const tagForm = reactive({
  assetName: '',
  category: 'hvac',
  model: '',
  manufacturer: '',
  serialNumber: '',
  location: 'Basement B2',
  purchaseDate: new Date(),
  warrantyEnd: new Date(Date.now() + 365 * 24 * 3600000),
  value: 0,
  tagType: 'qr',
  notes: ''
})

const tagRules: FormRules = {
  assetName: [{ required: true, message: 'Please enter asset name', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  location: [{ required: true, message: 'Please select location', trigger: 'change' }]
}

// ========== 生成模拟数据 ==========
const generateAssetData = () => {
  const assets = [
    { id: '1', tagId: 'AST-2024-001', assetName: 'AHU-B2-01 Air Handler', category: 'hvac', location: 'Basement B2', model: 'Carrier 39G', manufacturer: 'Carrier', serialNumber: 'CA-2024-B201', purchaseDate: '2024-01-10', warrantyEnd: '2026-01-10', value: 25000, status: 'active', tagGenerated: true, notes: 'Main HVAC unit' },
    { id: '2', tagId: 'AST-2024-002', assetName: 'FCU-B2-01 Fan Coil', category: 'hvac', location: 'Basement B2', model: 'Daikin FXMQ', manufacturer: 'Daikin', serialNumber: 'DK-2024-B201', purchaseDate: '2024-02-15', warrantyEnd: '2026-02-15', value: 3500, status: 'active', tagGenerated: true, notes: 'Fan coil unit' },
    { id: '3', tagId: 'AST-2024-003', assetName: 'CH-B2-01 Chiller', category: 'hvac', location: 'Basement B2', model: 'Carrier AquaEdge', manufacturer: 'Carrier', serialNumber: 'CA-2024-B202', purchaseDate: '2024-01-05', warrantyEnd: '2026-01-05', value: 85000, status: 'active', tagGenerated: true, notes: 'Central chiller' },
    { id: '4', tagId: 'AST-2024-004', assetName: 'LIGHT-B2-01 Controller', category: 'lighting', location: 'Basement B2', model: 'Philips Dynalite', manufacturer: 'Philips', serialNumber: 'PH-2024-B201', purchaseDate: '2024-01-20', warrantyEnd: '2026-01-20', value: 1200, status: 'active', tagGenerated: true, notes: 'Lighting control' },
    { id: '5', tagId: 'AST-2024-005', assetName: 'ACS-1F-01 Entrance', category: 'security', location: 'Lobby 1F', model: 'HID VertX', manufacturer: 'HID', serialNumber: 'HD-2024-1F01', purchaseDate: '2024-01-05', warrantyEnd: '2026-01-05', value: 800, status: 'active', tagGenerated: true, notes: 'Access control' },
    { id: '6', tagId: 'AST-2024-006', assetName: 'SD-1F-01 Smoke Detector', category: 'fire', location: 'Lobby 1F', model: 'Honeywell XLS', manufacturer: 'Honeywell', serialNumber: 'HW-2024-1F01', purchaseDate: '2024-01-01', warrantyEnd: '2025-01-01', value: 150, status: 'warning', tagGenerated: true, notes: 'Smoke detector' },
    { id: '7', tagId: 'AST-2024-007', assetName: 'PUMP-B2-02 Booster', category: 'plumbing', location: 'Basement B2', model: 'Grundfos CR', manufacturer: 'Grundfos', serialNumber: 'GF-2024-B202', purchaseDate: '2023-11-20', warrantyEnd: '2025-11-20', value: 4500, status: 'active', tagGenerated: true, notes: 'Water booster pump' },
    { id: '8', tagId: 'AST-2024-008', assetName: 'Main Switchboard', category: 'electrical', location: 'Basement B2', model: 'ABB MNS', manufacturer: 'ABB', serialNumber: 'AB-2024-B201', purchaseDate: '2024-01-15', warrantyEnd: '2027-01-15', value: 45000, status: 'active', tagGenerated: false, notes: 'Main electrical panel' }
  ]
  allAssets.value = assets
}

// ========== 图表初始化 ==========
const initPieChart = async () => {
  await nextTick()
  if (!pieChartRef.value) {
    setTimeout(() => initPieChart(), 100)
    return
  }

  if (pieInstance) pieInstance.dispose()
  pieInstance = echarts.init(pieChartRef.value)

  const hvacCount = allAssets.value.filter(a => a.category === 'hvac').length
  const lightingCount = allAssets.value.filter(a => a.category === 'lighting').length
  const securityCount = allAssets.value.filter(a => a.category === 'security').length
  const fireCount = allAssets.value.filter(a => a.category === 'fire').length
  const plumbingCount = allAssets.value.filter(a => a.category === 'plumbing').length
  const electricalCount = allAssets.value.filter(a => a.category === 'electrical').length

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['HVAC', 'Lighting', 'Security', 'Fire Alarm', 'Plumbing', 'Electrical'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'HVAC', value: hvacCount, itemStyle: { color: '#409eff' } },
        { name: 'Lighting', value: lightingCount, itemStyle: { color: '#67c23a' } },
        { name: 'Security', value: securityCount, itemStyle: { color: '#e6a23c' } },
        { name: 'Fire Alarm', value: fireCount, itemStyle: { color: '#f56c6c' } },
        { name: 'Plumbing', value: plumbingCount, itemStyle: { color: '#909399' } },
        { name: 'Electrical', value: electricalCount, itemStyle: { color: '#5470c6' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}', position: 'outside' }
    }]
  }
  pieInstance.setOption(option)
}

const initBarChart = async () => {
  await nextTick()
  if (!barChartRef.value) {
    setTimeout(() => initBarChart(), 100)
    return
  }

  if (barInstance) barInstance.dispose()
  barInstance = echarts.init(barChartRef.value)

  const locationMap: Record<string, number> = {}
  allAssets.value.forEach(a => {
    locationMap[a.location] = (locationMap[a.location] || 0) + 1
  })

  const locations = Object.keys(locationMap)
  const counts = locations.map(l => locationMap[l])

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '10%', right: '5%', top: '10%', bottom: '10%', containLabel: true },
    xAxis: { type: 'category', data: locations, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Number of Assets' },
    series: [{
      name: 'Assets',
      type: 'bar',
      data: counts,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#409eff' },
      label: { show: true, position: 'top' }
    }]
  }
  barInstance.setOption(option)
}

const updatePieChart = () => {
  if (!pieInstance) return
  const hvacCount = allAssets.value.filter(a => a.category === 'hvac').length
  const lightingCount = allAssets.value.filter(a => a.category === 'lighting').length
  const securityCount = allAssets.value.filter(a => a.category === 'security').length
  const fireCount = allAssets.value.filter(a => a.category === 'fire').length
  const plumbingCount = allAssets.value.filter(a => a.category === 'plumbing').length
  const electricalCount = allAssets.value.filter(a => a.category === 'electrical').length
  pieInstance.setOption({ series: [{ data: [
        { name: 'HVAC', value: hvacCount },
        { name: 'Lighting', value: lightingCount },
        { name: 'Security', value: securityCount },
        { name: 'Fire Alarm', value: fireCount },
        { name: 'Plumbing', value: plumbingCount },
        { name: 'Electrical', value: electricalCount }
      ] }] })
}

const updateBarChart = () => {
  if (!barInstance) return
  const locationMap: Record<string, number> = {}
  allAssets.value.forEach(a => {
    locationMap[a.location] = (locationMap[a.location] || 0) + 1
  })
  const locations = Object.keys(locationMap)
  const counts = locations.map(l => locationMap[l])
  barInstance.setOption({ xAxis: { data: locations }, series: [{ data: counts }] })
}

const handleChartResize = () => {
  if (pieInstance) pieInstance.resize()
  if (barInstance) barInstance.resize()
}

// ========== Helper Functions ==========
const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    hvac: 'HVAC', lighting: 'Lighting', security: 'Security', fire: 'Fire Alarm', plumbing: 'Plumbing', electrical: 'Electrical'
  }
  return labels[category] || category
}

const getCategoryTag = (category: string) => {
  const tags: Record<string, string> = {
    hvac: 'primary', lighting: 'success', security: 'warning', fire: 'danger', plumbing: 'info', electrical: 'info'
  }
  return tags[category] || 'info'
}

const isWarrantyExpiring = (dateStr: string) => {
  const daysLeft = (new Date(dateStr).getTime() - new Date().getTime()) / (1000 * 3600 * 24)
  return daysLeft <= 90 && daysLeft > 0
}

const isWarrantyExpired = (dateStr: string) => {
  return new Date(dateStr) < new Date()
}

// ========== Actions ==========
const handleSearch = () => { pageInfo.pageNum = 1 }
const resetFilter = () => {
  filterForm.assetName = ''
  filterForm.tagId = ''
  filterForm.category = ''
  filterForm.location = ''
  pageInfo.pageNum = 1
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  generateAssetData()
  updatePieChart()
  updateBarChart()
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pageInfo.pageNum = 1 }
const handlePageChange = () => {}

const viewDetail = (row: any) => {
  ElMessage.info(`Viewing details for asset: ${row.assetName}`)
}

const printTag = (row: any) => {
  ElMessage.info(`Printing tag for ${row.assetName}`)
}

const deleteTag = async (row: any) => {
  try {
    await ElMessageBox.confirm(
        `Delete asset tag for "${row.assetName}"? This action cannot be undone.`,
        'Confirm Delete',
        { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
    allAssets.value = allAssets.value.filter(a => a.id !== row.id)
    updatePieChart()
    updateBarChart()
    ElMessage.success('Asset tag deleted')
  } catch (error) {
    // cancelled
  }
}

const openCreateDialog = () => {
  resetForm()
  dialogVisible.value = true
}

const resetForm = () => {
  tagForm.assetName = ''
  tagForm.category = 'hvac'
  tagForm.model = ''
  tagForm.manufacturer = ''
  tagForm.serialNumber = ''
  tagForm.location = 'Basement B2'
  tagForm.purchaseDate = new Date()
  tagForm.warrantyEnd = new Date(Date.now() + 365 * 24 * 3600000)
  tagForm.value = 0
  tagForm.tagType = 'qr'
  tagForm.notes = ''
  if (tagFormRef.value) tagFormRef.value.clearValidate()
}

const generateTag = async () => {
  if (!tagFormRef.value) return
  await tagFormRef.value.validate(async (valid) => {
    if (valid) {
      generating.value = true
      await new Promise(resolve => setTimeout(resolve, 800))

      const newTag = {
        id: (allAssets.value.length + 1).toString(),
        tagId: `AST-${new Date().getFullYear()}-${String(allAssets.value.length + 1).padStart(3, '0')}`,
        assetName: tagForm.assetName,
        category: tagForm.category,
        location: tagForm.location,
        model: tagForm.model,
        manufacturer: tagForm.manufacturer,
        serialNumber: tagForm.serialNumber,
        purchaseDate: tagForm.purchaseDate.toISOString().split('T')[0],
        warrantyEnd: tagForm.warrantyEnd.toISOString().split('T')[0],
        value: tagForm.value,
        status: 'active',
        tagGenerated: true,
        notes: tagForm.notes
      }

      allAssets.value.unshift(newTag)
      updatePieChart()
      updateBarChart()
      dialogVisible.value = false
      generating.value = false
      ElMessage.success(`Asset tag generated: ${newTag.tagId}`)
    }
  })
}

const showQRCode = async (row: any) => {
  selectedAsset.value = row
  qrDialogVisible.value = true
  await nextTick()
  if (qrCanvasRef.value) {
    const qrData = JSON.stringify({
      tagId: row.tagId,
      assetName: row.assetName,
      model: row.model,
      serialNumber: row.serialNumber,
      location: row.location,
      url: `${window.location.origin}/asset/${row.tagId}`
    })
    QRCode.toCanvas(qrCanvasRef.value, qrData, { width: 200, margin: 2 }, (error) => {
      if (error) console.error(error)
    })
  }
}

const downloadQRCode = () => {
  if (qrCanvasRef.value) {
    const link = document.createElement('a')
    link.download = `${selectedAsset.value?.tagId}.png`
    link.href = qrCanvasRef.value.toDataURL()
    link.click()
    ElMessage.success('QR Code downloaded')
  }
}

const printQRCode = () => {
  if (qrCanvasRef.value) {
    const win = window.open()
    if (win) {
      win.document.write(`
        <html>
          <head><title>QR Code - ${selectedAsset.value?.tagId}</title></head>
          <body style="display:flex;justify-content:center;align-items:center;min-height:100vh">
            <img src="${qrCanvasRef.value.toDataURL()}" />
          </body>
        </html>
      `)
      win.print()
      win.close()
    }
  }
}

const exportTags = () => {
  ElMessage.success('Exporting asset tags to CSV')
}

const confirmBatchPrint = () => {
  ElMessage.success(`Printing ${selectedPrintTags.value.length} tags`)
  batchPrintDialogVisible.value = false
}

// ========== Lifecycle ==========
onMounted(async () => {
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

  setTimeout(async () => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(async () => {
      generateAssetData()
      isLoaded.value = true
      await nextTick()

      setTimeout(async () => {
        await initPieChart()
        await initBarChart()
        window.addEventListener('resize', handleChartResize)
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleChartResize)
  if (pieInstance) pieInstance.dispose()
  if (barInstance) barInstance.dispose()
})
</script>

<style scoped lang="scss">
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

/* Page Content */
.asset-tag-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon .el-icon {
  font-size: 32px;
  color: #3b82f6;
}

.stat-card.success .stat-icon .el-icon { color: #67c23a; }
.stat-card.warning .stat-icon .el-icon { color: #e6a23c; }
.stat-card.info .stat-icon .el-icon { color: #409eff; }

.stat-info { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }
.stat-percent { font-size: 20px; font-weight: 600; color: #67c23a; }

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-card :deep(.el-card__body) {
  padding: 20px;
}

.filter-card :deep(.el-form) {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 16px;
}

.filter-card :deep(.el-form-item) {
  margin-bottom: 0;
}

.filter-card :deep(.el-form-item__label) {
  font-size: 13px;
  font-weight: 500;
  padding-bottom: 4px;
}

.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card, .stats-chart-card {
  flex: 1;
  border-radius: 12px;
}

.card-header-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
}

.pie-chart-box, .bar-chart-box {
  width: 100%;
  height: 320px;
}

.text-warning { color: #e6a23c; font-weight: 500; }
.text-danger { color: #f56c6c; font-weight: 500; }

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.qr-container {
  text-align: center;
  padding: 20px;
}

.qr-canvas {
  display: inline-block;
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
  padding: 10px;
}

.qr-info {
  text-align: left;
  margin: 16px 0;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.qr-info p {
  margin: 4px 0;
  font-size: 13px;
}

.qr-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.batch-print {
  padding: 8px;
}

.print-options {
  margin-top: 16px;
  display: flex;
  gap: 16px;
  flex-direction: column;
}

@media (max-width: 1024px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .asset-tag-container {
    padding: 12px;
  }
  .stats-cards {
    grid-template-columns: 1fr;
  }
  .filter-card :deep(.el-form) {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-card :deep(.el-form-item) {
    width: 100%;
  }
  .filter-card :deep(.el-input),
  .filter-card :deep(.el-select) {
    width: 100% !important;
  }
  .pie-chart-box, .bar-chart-box {
    height: 250px;
  }
}
</style>