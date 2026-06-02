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
        <div class="loading-tip">VIRTUAL POINTS MODULE</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="virtual-points-container">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalVirtualPoints }}</span>
          <span class="stat-label">Virtual Points</span>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ activePoints }}</span>
          <span class="stat-label">Active</span>
        </div>
        <div class="stat-percent">{{ activePercent }}%</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ warningPoints }}</span>
          <span class="stat-label">Warning</span>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ avgCalculationTime.toFixed(1) }}ms</span>
          <span class="stat-label">Avg Calc Time</span>
        </div>
      </div>
    </div>

    <!-- 筛选卡片 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="Point Name">
          <el-input v-model="filterForm.pointName" placeholder="Search by name" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="Point Type">
          <el-select v-model="filterForm.pointType" placeholder="Select Type" clearable style="width: 140px">
            <el-option label="Calculation" value="calculation" />
            <el-option label="Aggregation" value="aggregation" />
            <el-option label="Derived" value="derived" />
            <el-option label="Custom Expression" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Data Type">
          <el-select v-model="filterForm.dataType" placeholder="Data Type" clearable style="width: 120px">
            <el-option label="Number" value="number" />
            <el-option label="Boolean" value="boolean" />
            <el-option label="String" value="string" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="filterForm.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="All" value="" />
            <el-option label="Active" value="active" />
            <el-option label="Warning" value="warning" />
            <el-option label="Error" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetFilter">Reset</el-button>
          <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
          <el-button type="success" :icon="Plus" @click="openCreateDialog">Create Virtual Point</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span>Virtual Point Value Trend</span>
            <el-select v-model="trendPointId" placeholder="Select Virtual Point" size="small" style="width: 220px" filterable @change="updateTrendChart">
              <el-option v-for="point in numericVirtualPoints" :key="point.id" :label="point.pointName" :value="point.id" />
            </el-select>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-box"></div>
      </el-card>

      <el-card class="stats-chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">Virtual Point Type Distribution</div>
        </template>
        <div ref="pieChartRef" class="pie-chart-box"></div>
      </el-card>
    </div>

    <!-- 虚拟点列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Virtual Points List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="400" v-loading="tableLoading">
        <el-table-column label="Name" prop="pointName" min-width="180" show-overflow-tooltip />
        <el-table-column label="Type" prop="pointType" width="120">
          <template #default="scope">
            <el-tag :type="getPointTypeTag(scope.row.pointType)" size="small">{{ getPointTypeLabel(scope.row.pointType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Expression" prop="expression" min-width="250" show-overflow-tooltip />
        <el-table-column label="Data Type" prop="dataType" width="100" />
        <el-table-column label="Current Value" prop="currentValue" width="150">
          <template #default="scope">
            <span :class="getValueClass(scope.row)">{{ formatValue(scope.row.currentValue) }}</span>
            <span class="unit">{{ scope.row.unit || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" prop="status" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : scope.row.status === 'warning' ? 'warning' : 'danger'" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Calc Time" prop="calculationTime" width="100">
          <template #default="scope">
            <span :class="{ 'text-warning': scope.row.calculationTime > 50 }">{{ scope.row.calculationTime }}ms</span>
          </template>
        </el-table-column>
        <el-table-column label="Last Update" prop="lastUpdate" width="160" />
        <el-table-column label="Operation" width="160" fixed="right">
          <template #default="scope">
            <el-button text type="primary" size="small" @click="viewDetail(scope.row)">Detail</el-button>
            <el-button text type="warning" size="small" @click="editPoint(scope.row)">Edit</el-button>
            <el-button text type="danger" size="small" @click="deletePoint(scope.row)">Delete</el-button>
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

    <!-- 创建/编辑虚拟点对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingPoint ? 'Edit Virtual Point' : 'Create Virtual Point'" width="650px" @closed="resetForm">
      <el-form :model="pointForm" :rules="pointRules" ref="pointFormRef" label-width="120px">
        <el-form-item label="Point Name" prop="pointName">
          <el-input v-model="pointForm.pointName" placeholder="e.g., Total Energy Consumption" />
        </el-form-item>
        <el-form-item label="Point Type" prop="pointType">
          <el-select v-model="pointForm.pointType" style="width: 100%" @change="onPointTypeChange">
            <el-option label="Calculation (Formula)" value="calculation">
              <span>🧮 Calculation (Formula)</span>
            </el-option>
            <el-option label="Aggregation (Sum/Avg/Min/Max)" value="aggregation">
              <span>📊 Aggregation (Sum/Avg/Min/Max)</span>
            </el-option>
            <el-option label="Derived (Rate/Difference)" value="derived">
              <span>📈 Derived (Rate/Difference)</span>
            </el-option>
            <el-option label="Custom Expression" value="custom">
              <span>⚙️ Custom Expression (JavaScript)</span>
            </el-option>
          </el-select>
        </el-form-item>

        <!-- Calculation Type Specific Fields -->
        <div v-if="pointForm.pointType === 'calculation'" class="form-section">
          <el-form-item label="Formula" prop="expression">
            <el-input
                v-model="pointForm.expression"
                type="textarea"
                :rows="3"
                placeholder="e.g., (temperature - 32) * 5/9&#10;or&#10;power * time / 1000"
            />
          </el-form-item>
          <el-form-item label="Input Points">
            <el-select
                v-model="pointForm.inputPoints"
                multiple
                filterable
                placeholder="Select source points"
                style="width: 100%"
            >
              <el-option v-for="point in availableSourcePoints" :key="point.id" :label="point.pointName" :value="point.id" />
            </el-select>
          </el-form-item>
        </div>

        <!-- Aggregation Type Specific Fields -->
        <div v-if="pointForm.pointType === 'aggregation'" class="form-section">
          <el-form-item label="Aggregation Function" prop="aggregationFunc">
            <el-select v-model="pointForm.aggregationFunc" style="width: 100%">
              <el-option label="Sum" value="sum" />
              <el-option label="Average" value="avg" />
              <el-option label="Minimum" value="min" />
              <el-option label="Maximum" value="max" />
              <el-option label="Count" value="count" />
            </el-select>
          </el-form-item>
          <el-form-item label="Source Points" prop="inputPoints">
            <el-select
                v-model="pointForm.inputPoints"
                multiple
                filterable
                placeholder="Select points to aggregate"
                style="width: 100%"
            >
              <el-option v-for="point in availableSourcePoints" :key="point.id" :label="point.pointName" :value="point.id" />
            </el-select>
          </el-form-item>
        </div>

        <!-- Derived Type Specific Fields -->
        <div v-if="pointForm.pointType === 'derived'" class="form-section">
          <el-form-item label="Derived Type" prop="derivedType">
            <el-select v-model="pointForm.derivedType" style="width: 100%">
              <el-option label="Rate of Change (per minute)" value="rate" />
              <el-option label="Difference from previous" value="delta" />
              <el-option label="Cumulative sum" value="cumulative" />
              <el-option label="Running average" value="runningAvg" />
            </el-select>
          </el-form-item>
          <el-form-item label="Source Point" prop="sourcePointId">
            <el-select v-model="pointForm.sourcePointId" filterable placeholder="Select source point" style="width: 100%">
              <el-option v-for="point in numericSourcePoints" :key="point.id" :label="point.pointName" :value="point.id" />
            </el-select>
          </el-form-item>
        </div>

        <!-- Custom Expression Specific Fields -->
        <div v-if="pointForm.pointType === 'custom'" class="form-section">
          <el-form-item label="JavaScript Expression" prop="expression">
            <el-input
                v-model="pointForm.expression"
                type="textarea"
                :rows="5"
                placeholder="// Custom JavaScript expression&#10;// Available variables: points (object with all source point values)&#10;// Example:&#10;// points.temperature * points.flowRate / 3600"
            />
          </el-form-item>
          <el-form-item label="Input Points">
            <el-select
                v-model="pointForm.inputPoints"
                multiple
                filterable
                placeholder="Select source points"
                style="width: 100%"
            >
              <el-option v-for="point in availableSourcePoints" :key="point.id" :label="point.pointName" :value="point.id" />
            </el-select>
          </el-form-item>
        </div>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Data Type" prop="dataType">
              <el-select v-model="pointForm.dataType" style="width: 100%">
                <el-option label="Number" value="number" />
                <el-option label="Boolean" value="boolean" />
                <el-option label="String" value="string" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Unit">
              <el-input v-model="pointForm.unit" placeholder="e.g., kWh, °C, %" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Update Interval (s)">
              <el-input-number v-model="pointForm.updateInterval" :min="1" :max="3600" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status">
              <el-switch v-model="pointForm.isActive" active-text="Active" inactive-text="Inactive" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>Threshold Alerts</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Warning Min">
              <el-input-number v-model="pointForm.warningMin" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Warning Max">
              <el-input-number v-model="pointForm.warningMax" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Critical Min">
              <el-input-number v-model="pointForm.criticalMin" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Critical Max">
              <el-input-number v-model="pointForm.criticalMax" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePoint" :loading="saving">Save Virtual Point</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import type { FormInstance, FormRules } from 'element-plus'
import { Connection, CircleCheckFilled, WarningFilled, DataLine, Refresh, Plus } from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading virtual points...',
  'Initializing calculation engine...',
  'Almost ready...'
]

// ========== Chart References ==========
const trendChartRef = ref<HTMLDivElement | null>(null)
const pieChartRef = ref<HTMLDivElement | null>(null)
let trendInstance: echarts.ECharts | null = null
let pieInstance: echarts.ECharts | null = null
let calculationTimer: number | null = null
const refreshing = ref(false)
const tableLoading = ref(false)
const saving = ref(false)
const trendPointId = ref('')
const pointFormRef = ref<FormInstance>()

// ========== Filter Form ==========
const filterForm = reactive({
  pointName: '',
  pointType: '',
  dataType: '',
  status: ''
})

// ========== Pagination ==========
const pageInfo = reactive({
  pageNum: 1,
  pageSize: 15,
  total: 0
})

// ========== Dialog State ==========
const dialogVisible = ref(false)
const editingPoint = ref<any>(null)

// ========== Virtual Points Data ==========
const allVirtualPoints = ref<any[]>([])
const availableSourcePoints = ref<any[]>([])

// 统计数据
const totalVirtualPoints = computed(() => allVirtualPoints.value.length)
const activePoints = computed(() => allVirtualPoints.value.filter(p => p.status === 'active').length)
const warningPoints = computed(() => allVirtualPoints.value.filter(p => p.status === 'warning').length)
const activePercent = computed(() => totalVirtualPoints.value ? Math.round(activePoints.value / totalVirtualPoints.value * 100) : 0)
const avgCalculationTime = computed(() => {
  const active = allVirtualPoints.value.filter(p => p.status === 'active')
  if (active.length === 0) return 0
  const sum = active.reduce((s, p) => s + (p.calculationTime || 0), 0)
  return sum / active.length
})

// 数值型虚拟点（用于趋势图）
const numericVirtualPoints = computed(() =>
    allVirtualPoints.value.filter(p => p.dataType === 'number' && p.status === 'active')
)

// 数值型源点（用于派生类型）
const numericSourcePoints = computed(() =>
    availableSourcePoints.value.filter(p => p.dataType === 'number')
)

// 分页数据
const paginatedTableData = computed(() => {
  let filtered = [...allVirtualPoints.value]

  if (filterForm.pointName) {
    filtered = filtered.filter(p => p.pointName?.toLowerCase().includes(filterForm.pointName.toLowerCase()))
  }
  if (filterForm.pointType) {
    filtered = filtered.filter(p => p.pointType === filterForm.pointType)
  }
  if (filterForm.dataType) {
    filtered = filtered.filter(p => p.dataType === filterForm.dataType)
  }
  if (filterForm.status) {
    filtered = filtered.filter(p => p.status === filterForm.status)
  }

  pageInfo.total = filtered.length
  const start = (pageInfo.pageNum - 1) * pageInfo.pageSize
  return filtered.slice(start, start + pageInfo.pageSize)
})

// ========== Form Data ==========
const pointForm = reactive({
  pointName: '',
  pointType: 'calculation',
  expression: '',
  inputPoints: [] as string[],
  aggregationFunc: 'avg',
  derivedType: 'rate',
  sourcePointId: '',
  dataType: 'number',
  unit: '',
  updateInterval: 60,
  isActive: true,
  warningMin: null as number | null,
  warningMax: null as number | null,
  criticalMin: null as number | null,
  criticalMax: null as number | null
})

const pointRules: FormRules = {
  pointName: [{ required: true, message: 'Please enter point name', trigger: 'blur' }]
}

// ========== 生成模拟数据 ==========
const generateVirtualPoints = () => {
  const sourcePoints = [
    { id: 'src_1', pointName: 'AHU Supply Temp', dataType: 'number', unit: '°C', currentValue: 22.5 },
    { id: 'src_2', pointName: 'AHU Return Temp', dataType: 'number', unit: '°C', currentValue: 24.2 },
    { id: 'src_3', pointName: 'Chiller Power', dataType: 'number', unit: 'kW', currentValue: 85.3 },
    { id: 'src_4', pointName: 'Pump Power', dataType: 'number', unit: 'kW', currentValue: 22.5 },
    { id: 'src_5', pointName: 'Lighting Power', dataType: 'number', unit: 'kW', currentValue: 15.2 },
    { id: 'src_6', pointName: 'Fan Status', dataType: 'boolean', unit: '', currentValue: true },
    { id: 'src_7', pointName: 'Valve Position', dataType: 'number', unit: '%', currentValue: 65 },
    { id: 'src_8', pointName: 'Flow Rate', dataType: 'number', unit: 'm³/h', currentValue: 1250 }
  ]

  availableSourcePoints.value = sourcePoints

  const virtualPoints = [
    {
      id: '1',
      pointName: 'Total Energy Consumption',
      pointType: 'calculation',
      expression: '(chillerPower + pumpPower + lightingPower) * time',
      inputPoints: ['src_3', 'src_4', 'src_5'],
      dataType: 'number',
      unit: 'kWh',
      status: 'active',
      currentValue: 125.8,
      calculationTime: 12,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '2',
      pointName: 'Average AHU Temperature',
      pointType: 'aggregation',
      expression: 'avg(supplyTemp, returnTemp)',
      inputPoints: ['src_1', 'src_2'],
      aggregationFunc: 'avg',
      dataType: 'number',
      unit: '°C',
      status: 'active',
      currentValue: 23.35,
      calculationTime: 8,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '3',
      pointName: 'Temperature Delta',
      pointType: 'derived',
      expression: 'delta(supplyTemp)',
      inputPoints: ['src_1'],
      derivedType: 'delta',
      sourcePointId: 'src_1',
      dataType: 'number',
      unit: '°C',
      status: 'active',
      currentValue: 0.3,
      calculationTime: 5,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '4',
      pointName: 'HVAC Efficiency',
      pointType: 'custom',
      expression: 'points.chillerPower / (points.supplyTemp - points.returnTemp)',
      inputPoints: ['src_1', 'src_2', 'src_3'],
      dataType: 'number',
      unit: 'kW/°C',
      status: 'active',
      currentValue: 5.2,
      calculationTime: 15,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '5',
      pointName: 'System Health Score',
      pointType: 'custom',
      expression: 'Math.min(100, Math.max(0, 100 - (points.fanStatus ? 0 : 20) - (points.valvePosition < 50 ? 10 : 0)))',
      inputPoints: ['src_6', 'src_7'],
      dataType: 'number',
      unit: '%',
      status: 'warning',
      currentValue: 85,
      calculationTime: 10,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '6',
      pointName: 'Energy Trend',
      pointType: 'derived',
      expression: 'rate(chillerPower)',
      inputPoints: ['src_3'],
      derivedType: 'rate',
      sourcePointId: 'src_3',
      dataType: 'number',
      unit: 'kW/min',
      status: 'active',
      currentValue: 0.5,
      calculationTime: 6,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '7',
      pointName: 'Total Power Sum',
      pointType: 'aggregation',
      expression: 'sum(chillerPower, pumpPower, lightingPower)',
      inputPoints: ['src_3', 'src_4', 'src_5'],
      aggregationFunc: 'sum',
      dataType: 'number',
      unit: 'kW',
      status: 'active',
      currentValue: 123.0,
      calculationTime: 7,
      lastUpdate: new Date().toLocaleString()
    }
  ]

  allVirtualPoints.value = virtualPoints
  if (numericVirtualPoints.value.length > 0) {
    trendPointId.value = numericVirtualPoints.value[0].id.toString()
  }
}

// 更新虚拟点值
const updateVirtualPointValues = () => {
  for (const point of allVirtualPoints.value) {
    if (point.status === 'active') {
      // 模拟值变化
      if (point.dataType === 'number') {
        const change = (Math.random() - 0.5) * (point.currentValue * 0.05)
        let newVal = point.currentValue + change
        if (point.unit === '%') newVal = Math.max(0, Math.min(100, newVal))
        if (point.unit === '°C') newVal = Math.max(15, Math.min(35, newVal))
        point.currentValue = Number(newVal.toFixed(2))
      } else if (point.dataType === 'boolean') {
        point.currentValue = Math.random() > 0.9 ? !point.currentValue : point.currentValue
      }

      point.calculationTime = Math.floor(5 + Math.random() * 20)
      point.lastUpdate = new Date().toLocaleString()

      // 检查阈值
      if (point.warningMin !== null && point.currentValue < point.warningMin) {
        point.status = 'warning'
      } else if (point.warningMax !== null && point.currentValue > point.warningMax) {
        point.status = 'warning'
      } else {
        point.status = 'active'
      }
    }
  }

  // 更新源点值
  for (const src of availableSourcePoints.value) {
    if (src.dataType === 'number') {
      const change = (Math.random() - 0.5) * 1.5
      src.currentValue = Number(Math.max(0, src.currentValue + change).toFixed(1))
    } else if (src.dataType === 'boolean') {
      src.currentValue = Math.random() > 0.95 ? !src.currentValue : src.currentValue
    }
  }
}

// ========== 趋势图数据 ==========
const trendHistory = ref<{ timestamps: string[]; values: number[] }>({
  timestamps: [],
  values: []
})

// 获取虚拟点历史数据
const getPointHistory = () => {
  const point = numericVirtualPoints.value.find(p => p.id.toString() === trendPointId.value)
  if (!point) return

  const timestamps = []
  const values = []
  const now = new Date()
  const baseValue = typeof point.currentValue === 'number' ? point.currentValue : 50

  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 3600000)
    timestamps.push(`${String(time.getHours()).padStart(2, '0')}:00`)
    const variation = Math.sin(i * 0.3) * (baseValue * 0.1) + (Math.random() - 0.5) * (baseValue * 0.05)
    values.push(Number(Math.max(0, baseValue + variation).toFixed(2)))
  }

  trendHistory.value = { timestamps, values }
}

// 添加新数据点
const appendTrendData = () => {
  const point = numericVirtualPoints.value.find(p => p.id.toString() === trendPointId.value)
  if (!point) return

  const now = new Date()
  const timeStr = `${String(now.getHours()).padStart(2, '0')}:00`
  const newValue = typeof point.currentValue === 'number' ? point.currentValue : 0

  trendHistory.value.timestamps.push(timeStr)
  trendHistory.value.values.push(newValue)

  if (trendHistory.value.timestamps.length > 48) {
    trendHistory.value.timestamps.shift()
    trendHistory.value.values.shift()
  }

  updateTrendChart()
}

// 初始化趋势图
const initTrendChart = async () => {
  await nextTick()
  if (!trendChartRef.value) {
    setTimeout(() => initTrendChart(), 100)
    return
  }

  if (trendInstance) trendInstance.dispose()

  getPointHistory()
  trendInstance = echarts.init(trendChartRef.value)
  updateTrendChart()
  window.addEventListener('resize', handleChartResize)
}

const updateTrendChart = () => {
  if (!trendInstance || !trendHistory.value.timestamps.length) return

  const point = numericVirtualPoints.value.find(p => p.id.toString() === trendPointId.value)
  const unit = point?.unit || ''

  const option = {
    tooltip: { trigger: 'axis', formatter: (params: any) => `${params[0].axisValue}<br/>Value: ${params[0].value} ${unit}` },
    grid: { left: '8%', right: '5%', top: '12%', bottom: '8%', containLabel: true },
    xAxis: { type: 'category', data: trendHistory.value.timestamps, axisLabel: { rotate: 45, interval: 4, fontSize: 10 } },
    yAxis: { type: 'value', name: `Value (${unit})`, nameTextStyle: { fontSize: 12 } },
    series: [{
      name: point?.pointName || 'Value',
      type: 'line',
      data: trendHistory.value.values,
      smooth: true,
      lineStyle: { color: '#409eff', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle',
      symbolSize: 5
    }]
  }
  trendInstance.setOption(option, true)
}

// 初始化饼图
const initPieChart = async () => {
  await nextTick()
  if (!pieChartRef.value) {
    setTimeout(() => initPieChart(), 100)
    return
  }

  if (pieInstance) pieInstance.dispose()
  pieInstance = echarts.init(pieChartRef.value)

  const calcCount = allVirtualPoints.value.filter(p => p.pointType === 'calculation').length
  const aggCount = allVirtualPoints.value.filter(p => p.pointType === 'aggregation').length
  const derivedCount = allVirtualPoints.value.filter(p => p.pointType === 'derived').length
  const customCount = allVirtualPoints.value.filter(p => p.pointType === 'custom').length

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['Calculation', 'Aggregation', 'Derived', 'Custom'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'Calculation', value: calcCount, itemStyle: { color: '#409eff' } },
        { name: 'Aggregation', value: aggCount, itemStyle: { color: '#67c23a' } },
        { name: 'Derived', value: derivedCount, itemStyle: { color: '#e6a23c' } },
        { name: 'Custom', value: customCount, itemStyle: { color: '#f56c6c' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}', position: 'outside' }
    }]
  }
  pieInstance.setOption(option)
}

const updatePieChart = () => {
  if (!pieInstance) return
  const calcCount = allVirtualPoints.value.filter(p => p.pointType === 'calculation').length
  const aggCount = allVirtualPoints.value.filter(p => p.pointType === 'aggregation').length
  const derivedCount = allVirtualPoints.value.filter(p => p.pointType === 'derived').length
  const customCount = allVirtualPoints.value.filter(p => p.pointType === 'custom').length
  pieInstance.setOption({ series: [{ data: [{ name: 'Calculation', value: calcCount }, { name: 'Aggregation', value: aggCount }, { name: 'Derived', value: derivedCount }, { name: 'Custom', value: customCount }] }] })
}

const handleChartResize = () => {
  if (trendInstance) trendInstance.resize()
  if (pieInstance) pieInstance.resize()
}

// ========== Helper Functions ==========
const getPointTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    calculation: 'Calculation',
    aggregation: 'Aggregation',
    derived: 'Derived',
    custom: 'Custom'
  }
  return labels[type] || type
}

const getPointTypeTag = (type: string) => {
  const tags: Record<string, string> = {
    calculation: 'primary',
    aggregation: 'success',
    derived: 'warning',
    custom: 'danger'
  }
  return tags[type] || 'info'
}

const formatValue = (value: any) => {
  if (typeof value === 'number') return value.toFixed(2)
  if (typeof value === 'boolean') return value ? 'True' : 'False'
  return value
}

const getValueClass = (row: any) => {
  if (row.status === 'warning') return 'text-warning'
  if (row.status === 'error') return 'text-danger'
  return ''
}

const onPointTypeChange = () => {
  // Reset type-specific fields
  pointForm.expression = ''
  pointForm.inputPoints = []
  pointForm.aggregationFunc = 'avg'
  pointForm.derivedType = 'rate'
  pointForm.sourcePointId = ''
}

// ========== Actions ==========
const handleSearch = () => { pageInfo.pageNum = 1 }
const resetFilter = () => {
  filterForm.pointName = ''
  filterForm.pointType = ''
  filterForm.dataType = ''
  filterForm.status = ''
  pageInfo.pageNum = 1
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  generateVirtualPoints()
  updatePieChart()
  if (numericVirtualPoints.value.length > 0 && !trendPointId.value) {
    trendPointId.value = numericVirtualPoints.value[0].id.toString()
    getPointHistory()
    updateTrendChart()
  }
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

const handlePageSizeChange = () => { pageInfo.pageNum = 1 }
const handlePageChange = () => {}

const viewDetail = (row: any) => {
  ElMessage.info(`Viewing details for virtual point: ${row.pointName}`)
}

const editPoint = (row: any) => {
  editingPoint.value = row
  pointForm.pointName = row.pointName
  pointForm.pointType = row.pointType
  pointForm.expression = row.expression || ''
  pointForm.inputPoints = row.inputPoints || []
  pointForm.aggregationFunc = row.aggregationFunc || 'avg'
  pointForm.derivedType = row.derivedType || 'rate'
  pointForm.sourcePointId = row.sourcePointId || ''
  pointForm.dataType = row.dataType
  pointForm.unit = row.unit || ''
  pointForm.updateInterval = 60
  pointForm.isActive = row.status === 'active'
  pointForm.warningMin = row.warningMin || null
  pointForm.warningMax = row.warningMax || null
  pointForm.criticalMin = row.criticalMin || null
  pointForm.criticalMax = row.criticalMax || null
  dialogVisible.value = true
}

const openCreateDialog = () => {
  editingPoint.value = null
  resetForm()
  dialogVisible.value = true
}

const resetForm = () => {
  pointForm.pointName = ''
  pointForm.pointType = 'calculation'
  pointForm.expression = ''
  pointForm.inputPoints = []
  pointForm.aggregationFunc = 'avg'
  pointForm.derivedType = 'rate'
  pointForm.sourcePointId = ''
  pointForm.dataType = 'number'
  pointForm.unit = ''
  pointForm.updateInterval = 60
  pointForm.isActive = true
  pointForm.warningMin = null
  pointForm.warningMax = null
  pointForm.criticalMin = null
  pointForm.criticalMax = null
  if (pointFormRef.value) pointFormRef.value.clearValidate()
}

const savePoint = async () => {
  if (!pointFormRef.value) return
  await pointFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      await new Promise(resolve => setTimeout(resolve, 800))

      const newPoint = {
        id: editingPoint.value ? editingPoint.value.id : (allVirtualPoints.value.length + 1).toString(),
        pointName: pointForm.pointName,
        pointType: pointForm.pointType,
        expression: pointForm.expression,
        inputPoints: pointForm.inputPoints,
        aggregationFunc: pointForm.aggregationFunc,
        derivedType: pointForm.derivedType,
        sourcePointId: pointForm.sourcePointId,
        dataType: pointForm.dataType,
        unit: pointForm.unit,
        status: pointForm.isActive ? 'active' : 'inactive',
        currentValue: 0,
        calculationTime: 0,
        lastUpdate: new Date().toLocaleString(),
        warningMin: pointForm.warningMin,
        warningMax: pointForm.warningMax,
        criticalMin: pointForm.criticalMin,
        criticalMax: pointForm.criticalMax
      }

      if (editingPoint.value) {
        const index = allVirtualPoints.value.findIndex(p => p.id === editingPoint.value.id)
        if (index !== -1) {
          allVirtualPoints.value[index] = newPoint
        }
        ElMessage.success('Virtual point updated')
      } else {
        allVirtualPoints.value.unshift(newPoint)
        ElMessage.success('Virtual point created')
      }

      updatePieChart()
      dialogVisible.value = false
      saving.value = false
    }
  })
}

const deletePoint = async (row: any) => {
  try {
    await ElMessageBox.confirm(
        `Delete virtual point "${row.pointName}"? This action cannot be undone.`,
        'Confirm Delete',
        { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
    allVirtualPoints.value = allVirtualPoints.value.filter(p => p.id !== row.id)
    updatePieChart()
    ElMessage.success('Virtual point deleted')
  } catch (error) {
    // cancelled
  }
}

// 定时计算
const startCalculations = () => {
  calculationTimer = window.setInterval(() => {
    updateVirtualPointValues()
    appendTrendData()
  }, 5000)
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
      generateVirtualPoints()
      isLoaded.value = true
      await nextTick()

      setTimeout(async () => {
        await initTrendChart()
        await initPieChart()
        startCalculations()
      }, 200)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (calculationTimer) clearInterval(calculationTimer)
  if (trendInstance) trendInstance.dispose()
  if (pieInstance) pieInstance.dispose()
  window.removeEventListener('resize', handleChartResize)
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
.virtual-points-container {
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
  flex-wrap: wrap;
  gap: 12px;
}

.chart-box, .pie-chart-box {
  width: 100%;
  height: 320px;
}

.form-section {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.text-warning { color: #e6a23c; font-weight: 500; }
.text-danger { color: #f56c6c; font-weight: 500; }

.unit {
  font-size: 11px;
  color: #94a3b8;
  margin-left: 2px;
}

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
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
  .virtual-points-container {
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
  .chart-box, .pie-chart-box {
    height: 250px;
  }
}
</style>