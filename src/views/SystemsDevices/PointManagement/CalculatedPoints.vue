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
        <div class="loading-tip">CALCULATED POINTS MODULE</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Page Content -->
  <div v-else class="calculated-points-container">
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalCalculations }}</span>
          <span class="stat-label">Calculated Points</span>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon"><el-icon><CircleCheckFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ activeCalculations }}</span>
          <span class="stat-label">Active</span>
        </div>
        <div class="stat-percent">{{ activePercent }}%</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon"><el-icon><WarningFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ errorCalculations }}</span>
          <span class="stat-label">Error</span>
        </div>
      </div>
      <div class="stat-card info">
        <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ avgExecTime.toFixed(1) }}ms</span>
          <span class="stat-label">Avg Exec Time</span>
        </div>
      </div>
    </div>

    <!-- 筛选卡片 -->
    <el-card class="filter-card" shadow="hover">
      <el-form :model="filterForm" inline>
        <el-form-item label="Point Name">
          <el-input v-model="filterForm.pointName" placeholder="Search by name" clearable style="width: 180px" />
        </el-form-item>
        <el-form-item label="Formula Type">
          <el-select v-model="filterForm.formulaType" placeholder="Select Type" clearable style="width: 140px">
            <el-option label="Mathematical" value="math" />
            <el-option label="Trigonometric" value="trig" />
            <el-option label="Statistical" value="stats" />
            <el-option label="Logical" value="logic" />
            <el-option label="Business Rule" value="rule" />
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
            <el-option label="Error" value="error" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="resetFilter">Reset</el-button>
          <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
          <el-button type="success" :icon="Plus" @click="openCreateDialog">Create Calculated Point</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">
            <span>Calculated Value Trend</span>
            <el-select v-model="trendPointId" placeholder="Select Calculated Point" size="small" style="width: 220px" filterable @change="updateTrendChart">
              <el-option v-for="point in numericCalculations" :key="point.id" :label="point.pointName" :value="point.id" />
            </el-select>
          </div>
        </template>
        <div ref="trendChartRef" class="chart-box"></div>
      </el-card>

      <el-card class="stats-chart-card" shadow="hover">
        <template #header>
          <div class="card-header-title">Formula Type Distribution</div>
        </template>
        <div ref="pieChartRef" class="pie-chart-box"></div>
      </el-card>
    </div>

    <!-- 计算点列表 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header-title">Calculated Points List</div>
      </template>
      <el-table :data="paginatedTableData" border stripe height="400" v-loading="tableLoading">
        <el-table-column label="Name" prop="pointName" min-width="180" show-overflow-tooltip />
        <el-table-column label="Formula Type" prop="formulaType" width="120">
          <template #default="scope">
            <el-tag :type="getFormulaTypeTag(scope.row.formulaType)" size="small">{{ getFormulaTypeLabel(scope.row.formulaType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Formula" prop="formula" min-width="250" show-overflow-tooltip />
        <el-table-column label="Data Type" prop="dataType" width="100" />
        <el-table-column label="Current Value" prop="currentValue" width="150">
          <template #default="scope">
            <span :class="getValueClass(scope.row)">{{ formatValue(scope.row.currentValue) }}</span>
            <span class="unit">{{ scope.row.unit || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" prop="status" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === 'active' ? 'success' : 'danger'" size="small">{{ scope.row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Exec Time" prop="executionTime" width="100">
          <template #default="scope">
            <span :class="{ 'text-warning': scope.row.executionTime > 50 }">{{ scope.row.executionTime }}ms</span>
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

    <!-- 创建/编辑计算点对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingPoint ? 'Edit Calculated Point' : 'Create Calculated Point'" width="700px" @closed="resetForm">
      <el-form :model="pointForm" :rules="pointRules" ref="pointFormRef" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Point Name" prop="pointName">
              <el-input v-model="pointForm.pointName" placeholder="e.g., Energy Efficiency Ratio" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Formula Type" prop="formulaType">
              <el-select v-model="pointForm.formulaType" style="width: 100%" @change="onFormulaTypeChange">
                <el-option label="➕ Mathematical" value="math" />
                <el-option label="📐 Trigonometric" value="trig" />
                <el-option label="📊 Statistical" value="stats" />
                <el-option label="⚖️ Logical" value="logic" />
                <el-option label="📋 Business Rule" value="rule" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- Mathematical Formula -->
        <div v-if="pointForm.formulaType === 'math'" class="formula-section">
          <el-form-item label="Mathematical Formula" prop="formula">
            <el-input
                v-model="pointForm.formula"
                type="textarea"
                :rows="3"
                placeholder="Examples:&#10;temperature * 1.8 + 32&#10;power / voltage&#10;sqrt(pressure) * 10&#10;log(energy) / log(1.1)"
            />
          </el-form-item>
          <div class="formula-hint">
            <el-icon><InfoFilled /></el-icon>
            Available functions: +, -, *, /, ^, sqrt(), log(), ln(), exp(), abs(), round(), floor(), ceil()
          </div>
        </div>

        <!-- Trigonometric Formula -->
        <div v-if="pointForm.formulaType === 'trig'" class="formula-section">
          <el-form-item label="Trigonometric Formula" prop="formula">
            <el-input
                v-model="pointForm.formula"
                type="textarea"
                :rows="3"
                placeholder="Examples:&#10;sin(angle) * 10&#10;cos(angle)&#10;tan(angle)&#10;atan2(y, x)"
            />
          </el-form-item>
          <div class="formula-hint">
            <el-icon><InfoFilled /></el-icon>
            Available functions: sin(), cos(), tan(), asin(), acos(), atan(), atan2(), degrees(), radians()
          </div>
        </div>

        <!-- Statistical Formula -->
        <div v-if="pointForm.formulaType === 'stats'" class="formula-section">
          <el-form-item label="Statistical Formula" prop="formula">
            <el-input
                v-model="pointForm.formula"
                type="textarea"
                :rows="3"
                placeholder="Examples:&#10;avg(temperature1, temperature2, temperature3)&#10;max(power1, power2) - min(power1, power2)&#10;stdev(reading1, reading2, reading3)"
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
          <div class="formula-hint">
            <el-icon><InfoFilled /></el-icon>
            Functions: avg(), sum(), min(), max(), count(), stdev(), variance(), median()
          </div>
        </div>

        <!-- Logical Formula -->
        <div v-if="pointForm.formulaType === 'logic'" class="formula-section">
          <el-form-item label="Logical Expression" prop="formula">
            <el-input
                v-model="pointForm.formula"
                type="textarea"
                :rows="3"
                placeholder="Examples:&#10;temperature > 28 ? 'High' : 'Normal'&#10;power > 100 && voltage < 200 ? 'Alert' : 'OK'&#10;status == 'running' ? 1 : 0"
            />
          </el-form-item>
          <div class="formula-hint">
            <el-icon><InfoFilled /></el-icon>
            Operators: >, <, >=, <=, ==, !=, &&, ||, ? : (ternary)
          </div>
        </div>

        <!-- Business Rule -->
        <div v-if="pointForm.formulaType === 'rule'" class="formula-section">
          <el-form-item label="Business Rule" prop="formula">
            <el-input
                v-model="pointForm.formula"
                type="textarea"
                :rows="5"
                placeholder="// JavaScript business rule&#10;// Example: HVAC energy efficiency rating&#10;var efficiency = points.power / points.flowRate;&#10;if (efficiency < 0.5) return 'Excellent';&#10;else if (efficiency < 0.7) return 'Good';&#10;else if (efficiency < 0.85) return 'Fair';&#10;else return 'Poor';"
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
          <el-col :span="8">
            <el-form-item label="Data Type" prop="dataType">
              <el-select v-model="pointForm.dataType" style="width: 100%">
                <el-option label="Number" value="number" />
                <el-option label="Boolean" value="boolean" />
                <el-option label="String" value="string" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Unit">
              <el-input v-model="pointForm.unit" placeholder="e.g., kWh, °C, %" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Decimal Places">
              <el-input-number v-model="pointForm.decimalPlaces" :min="0" :max="6" style="width: 100%" />
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

        <el-divider>Test Formula</el-divider>

        <div class="test-section">
          <div class="test-inputs">
            <span class="test-label">Test Values:</span>
            <div class="test-values">
              <el-tag
                  v-for="(value, idx) in testValues"
                  :key="idx"
                  closable
                  @close="removeTestValue(idx)"
                  class="test-tag"
              >
                {{ value }}
              </el-tag>
              <el-input
                  v-model="newTestValue"
                  placeholder="Add test value (e.g., temperature=25)"
                  size="small"
                  style="width: 180px"
                  @keyup.enter="addTestValue"
              />
              <el-button size="small" @click="addTestValue" :icon="Plus">Add</el-button>
            </div>
          </div>
          <div class="test-result">
            <span class="test-label">Result:</span>
            <span class="result-value">{{ testResult }}</span>
          </div>
          <el-button size="small" type="primary" @click="testFormula">Test Formula</el-button>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePoint" :loading="saving">Save Calculated Point</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import type { FormInstance, FormRules } from 'element-plus'
import { Connection, CircleCheckFilled, WarningFilled, DataLine, Refresh, Plus, InfoFilled } from '@element-plus/icons-vue'

// ========== Loading State ==========
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = [
  'Preparing...',
  'Loading calculated points...',
  'Initializing formula engine...',
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

// ========== Test Formula ==========
const testValues = ref<string[]>([])
const newTestValue = ref('')
const testResult = ref('')

// ========== Filter Form ==========
const filterForm = reactive({
  pointName: '',
  formulaType: '',
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

// ========== Calculated Points Data ==========
const allCalculations = ref<any[]>([])
const availableSourcePoints = ref<any[]>([])

// 统计数据
const totalCalculations = computed(() => allCalculations.value.length)
const activeCalculations = computed(() => allCalculations.value.filter(p => p.status === 'active').length)
const errorCalculations = computed(() => allCalculations.value.filter(p => p.status === 'error').length)
const activePercent = computed(() => totalCalculations.value ? Math.round(activeCalculations.value / totalCalculations.value * 100) : 0)
const avgExecTime = computed(() => {
  const active = allCalculations.value.filter(p => p.status === 'active')
  if (active.length === 0) return 0
  const sum = active.reduce((s, p) => s + (p.executionTime || 0), 0)
  return sum / active.length
})

// 数值型计算点（用于趋势图）
const numericCalculations = computed(() =>
    allCalculations.value.filter(p => p.dataType === 'number' && p.status === 'active')
)

// 分页数据
const paginatedTableData = computed(() => {
  let filtered = [...allCalculations.value]

  if (filterForm.pointName) {
    filtered = filtered.filter(p => p.pointName?.toLowerCase().includes(filterForm.pointName.toLowerCase()))
  }
  if (filterForm.formulaType) {
    filtered = filtered.filter(p => p.formulaType === filterForm.formulaType)
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
  formulaType: 'math',
  formula: '',
  inputPoints: [] as string[],
  dataType: 'number',
  unit: '',
  decimalPlaces: 2,
  updateInterval: 60,
  isActive: true
})

const pointRules: FormRules = {
  pointName: [{ required: true, message: 'Please enter point name', trigger: 'blur' }],
  formula: [{ required: true, message: 'Please enter formula', trigger: 'blur' }]
}

// ========== 生成模拟数据 ==========
const generateCalculatedPoints = () => {
  const sourcePoints = [
    { id: 'src_1', pointName: 'Supply Air Temp', value: 22.5 },
    { id: 'src_2', pointName: 'Return Air Temp', value: 24.2 },
    { id: 'src_3', pointName: 'Chiller Power', value: 85.3 },
    { id: 'src_4', pointName: 'Pump Power', value: 22.5 },
    { id: 'src_5', pointName: 'Outside Temp', value: 18.0 },
    { id: 'src_6', pointName: 'Flow Rate', value: 1250 },
    { id: 'src_7', pointName: 'Voltage', value: 230 },
    { id: 'src_8', pointName: 'Current', value: 32.5 }
  ]

  availableSourcePoints.value = sourcePoints

  const calculations = [
    {
      id: '1',
      pointName: 'Temperature in Fahrenheit',
      formulaType: 'math',
      formula: 'temperature * 1.8 + 32',
      inputPoints: ['src_1'],
      dataType: 'number',
      unit: '°F',
      status: 'active',
      currentValue: 72.5,
      executionTime: 5,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '2',
      pointName: 'Temperature Delta',
      formulaType: 'math',
      formula: 'supplyTemp - returnTemp',
      inputPoints: ['src_1', 'src_2'],
      dataType: 'number',
      unit: '°C',
      status: 'active',
      currentValue: 1.7,
      executionTime: 4,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '3',
      pointName: 'Power Factor',
      formulaType: 'math',
      formula: 'power / (voltage * current / 1000)',
      inputPoints: ['src_3', 'src_7', 'src_8'],
      dataType: 'number',
      unit: '',
      status: 'active',
      currentValue: 0.95,
      executionTime: 8,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '4',
      pointName: 'Energy Efficiency Ratio',
      formulaType: 'stats',
      formula: 'avg(chillerPower, pumpPower)',
      inputPoints: ['src_3', 'src_4'],
      dataType: 'number',
      unit: 'kW',
      status: 'active',
      currentValue: 53.9,
      executionTime: 10,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '5',
      pointName: 'HVAC Status',
      formulaType: 'logic',
      formula: 'temperature > 26 ? "Cooling Required" : (temperature < 20 ? "Heating Required" : "Normal")',
      inputPoints: ['src_1'],
      dataType: 'string',
      unit: '',
      status: 'active',
      currentValue: 'Normal',
      executionTime: 6,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '6',
      pointName: 'Energy Alert',
      formulaType: 'rule',
      formula: 'if (chillerPower > 100) return "Critical"; else if (chillerPower > 80) return "Warning"; else return "Normal"',
      inputPoints: ['src_3'],
      dataType: 'string',
      unit: '',
      status: 'active',
      currentValue: 'Normal',
      executionTime: 12,
      lastUpdate: new Date().toLocaleString()
    },
    {
      id: '7',
      pointName: 'System Efficiency',
      formulaType: 'math',
      formula: '(supplyTemp - returnTemp) / power * 100',
      inputPoints: ['src_1', 'src_2', 'src_3'],
      dataType: 'number',
      unit: '%',
      status: 'active',
      currentValue: 2.0,
      executionTime: 7,
      lastUpdate: new Date().toLocaleString()
    }
  ]

  allCalculations.value = calculations
  if (numericCalculations.value.length > 0) {
    trendPointId.value = numericCalculations.value[0].id.toString()
  }
}

// 更新计算点值
const updateCalculatedValues = () => {
  for (const point of allCalculations.value) {
    if (point.status === 'active') {
      // 模拟值变化
      if (point.dataType === 'number') {
        const change = (Math.random() - 0.5) * (point.currentValue * 0.03)
        let newVal = point.currentValue + change
        if (point.unit === '%') newVal = Math.max(0, Math.min(100, newVal))
        if (point.unit === '°F') newVal = Math.max(32, Math.min(120, newVal))
        if (point.unit === '°C') newVal = Math.max(15, Math.min(35, newVal))
        point.currentValue = Number(newVal.toFixed(point.decimalPlaces || 2))
      } else if (point.dataType === 'string') {
        const options = ['Normal', 'Warning', 'Critical', 'Optimal']
        point.currentValue = options[Math.floor(Math.random() * options.length)]
      } else if (point.dataType === 'boolean') {
        point.currentValue = Math.random() > 0.8
      }

      point.executionTime = Math.floor(4 + Math.random() * 15)
      point.lastUpdate = new Date().toLocaleString()
    }
  }

  // 更新源点值
  for (const src of availableSourcePoints.value) {
    const change = (Math.random() - 0.5) * 2
    src.value = Number(Math.max(0, src.value + change).toFixed(1))
  }
}

// ========== 趋势图数据 ==========
const trendHistory = ref<{ timestamps: string[]; values: number[] }>({
  timestamps: [],
  values: []
})

// 获取计算点历史数据
const getPointHistory = () => {
  const point = numericCalculations.value.find(p => p.id.toString() === trendPointId.value)
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
  const point = numericCalculations.value.find(p => p.id.toString() === trendPointId.value)
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

  const point = numericCalculations.value.find(p => p.id.toString() === trendPointId.value)
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

  const mathCount = allCalculations.value.filter(p => p.formulaType === 'math').length
  const trigCount = allCalculations.value.filter(p => p.formulaType === 'trig').length
  const statsCount = allCalculations.value.filter(p => p.formulaType === 'stats').length
  const logicCount = allCalculations.value.filter(p => p.formulaType === 'logic').length
  const ruleCount = allCalculations.value.filter(p => p.formulaType === 'rule').length

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: ['Mathematical', 'Trigonometric', 'Statistical', 'Logical', 'Business Rule'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { name: 'Mathematical', value: mathCount, itemStyle: { color: '#409eff' } },
        { name: 'Trigonometric', value: trigCount, itemStyle: { color: '#67c23a' } },
        { name: 'Statistical', value: statsCount, itemStyle: { color: '#e6a23c' } },
        { name: 'Logical', value: logicCount, itemStyle: { color: '#f56c6c' } },
        { name: 'Business Rule', value: ruleCount, itemStyle: { color: '#909399' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}', position: 'outside' }
    }]
  }
  pieInstance.setOption(option)
}

const updatePieChart = () => {
  if (!pieInstance) return
  const mathCount = allCalculations.value.filter(p => p.formulaType === 'math').length
  const trigCount = allCalculations.value.filter(p => p.formulaType === 'trig').length
  const statsCount = allCalculations.value.filter(p => p.formulaType === 'stats').length
  const logicCount = allCalculations.value.filter(p => p.formulaType === 'logic').length
  const ruleCount = allCalculations.value.filter(p => p.formulaType === 'rule').length
  pieInstance.setOption({ series: [{ data: [
        { name: 'Mathematical', value: mathCount },
        { name: 'Trigonometric', value: trigCount },
        { name: 'Statistical', value: statsCount },
        { name: 'Logical', value: logicCount },
        { name: 'Business Rule', value: ruleCount }
      ] }] })
}

const handleChartResize = () => {
  if (trendInstance) trendInstance.resize()
  if (pieInstance) pieInstance.resize()
}

// ========== Helper Functions ==========
const getFormulaTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    math: 'Mathematical',
    trig: 'Trigonometric',
    stats: 'Statistical',
    logic: 'Logical',
    rule: 'Business Rule'
  }
  return labels[type] || type
}

const getFormulaTypeTag = (type: string) => {
  const tags: Record<string, string> = {
    math: 'primary',
    trig: 'success',
    stats: 'warning',
    logic: 'danger',
    rule: 'info'
  }
  return tags[type] || 'info'
}

const formatValue = (value: any) => {
  if (typeof value === 'number') return value.toFixed(2)
  if (typeof value === 'boolean') return value ? 'True' : 'False'
  return value
}

const getValueClass = (row: any) => {
  if (row.status === 'error') return 'text-danger'
  return ''
}

const onFormulaTypeChange = () => {
  pointForm.formula = ''
  pointForm.inputPoints = []
}

// ========== Test Formula ==========
const addTestValue = () => {
  if (newTestValue.value.trim()) {
    testValues.value.push(newTestValue.value.trim())
    newTestValue.value = ''
  }
}

const removeTestValue = (idx: number) => {
  testValues.value.splice(idx, 1)
}

const testFormula = () => {
  // 模拟公式测试
  if (!pointForm.formula) {
    testResult.value = 'Please enter a formula'
    return
  }

  // 解析测试值
  const testMap: Record<string, number> = {}
  for (const val of testValues.value) {
    const [key, value] = val.split('=')
    if (key && value) {
      testMap[key.trim()] = parseFloat(value)
    }
  }

  // 模拟计算结果
  const formulaLower = pointForm.formula.toLowerCase()
  if (formulaLower.includes('temperature') || formulaLower.includes('temp')) {
    const temp = testMap.temperature || testMap.temp || 25
    if (formulaLower.includes('fahrenheit')) {
      testResult.value = `${(temp * 1.8 + 32).toFixed(2)}`
    } else if (formulaLower.includes('delta')) {
      const returnTemp = testMap.returnTemp || 23
      testResult.value = `${(temp - returnTemp).toFixed(2)}`
    } else {
      testResult.value = `${(temp * 1.2).toFixed(2)}`
    }
  } else if (formulaLower.includes('power')) {
    const power = testMap.power || 100
    testResult.value = `${(power * 0.85).toFixed(2)}`
  } else if (formulaLower.includes('efficiency')) {
    testResult.value = `${(85.5).toFixed(2)}%`
  } else if (formulaLower.includes('?')) {
    const temp = testMap.temperature || 25
    testResult.value = temp > 26 ? 'Cooling Required' : (temp < 20 ? 'Heating Required' : 'Normal')
  } else {
    testResult.value = `${(Math.random() * 100).toFixed(2)}`
  }

  ElMessage.success('Formula test completed')
}

// ========== Actions ==========
const handleSearch = () => { pageInfo.pageNum = 1 }
const resetFilter = () => {
  filterForm.pointName = ''
  filterForm.formulaType = ''
  filterForm.dataType = ''
  filterForm.status = ''
  pageInfo.pageNum = 1
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  generateCalculatedPoints()
  updatePieChart()
  if (numericCalculations.value.length > 0 && !trendPointId.value) {
    trendPointId.value = numericCalculations.value[0].id.toString()
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
  ElMessage.info(`Viewing details for calculated point: ${row.pointName}`)
}

const editPoint = (row: any) => {
  editingPoint.value = row
  pointForm.pointName = row.pointName
  pointForm.formulaType = row.formulaType
  pointForm.formula = row.formula
  pointForm.inputPoints = row.inputPoints || []
  pointForm.dataType = row.dataType
  pointForm.unit = row.unit || ''
  pointForm.decimalPlaces = row.decimalPlaces || 2
  pointForm.updateInterval = 60
  pointForm.isActive = row.status === 'active'
  testValues.value = []
  testResult.value = ''
  dialogVisible.value = true
}

const openCreateDialog = () => {
  editingPoint.value = null
  resetForm()
  dialogVisible.value = true
}

const resetForm = () => {
  pointForm.pointName = ''
  pointForm.formulaType = 'math'
  pointForm.formula = ''
  pointForm.inputPoints = []
  pointForm.dataType = 'number'
  pointForm.unit = ''
  pointForm.decimalPlaces = 2
  pointForm.updateInterval = 60
  pointForm.isActive = true
  testValues.value = []
  testResult.value = ''
  if (pointFormRef.value) pointFormRef.value.clearValidate()
}

const savePoint = async () => {
  if (!pointFormRef.value) return
  await pointFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      await new Promise(resolve => setTimeout(resolve, 800))

      const newPoint = {
        id: editingPoint.value ? editingPoint.value.id : (allCalculations.value.length + 1).toString(),
        pointName: pointForm.pointName,
        formulaType: pointForm.formulaType,
        formula: pointForm.formula,
        inputPoints: pointForm.inputPoints,
        dataType: pointForm.dataType,
        unit: pointForm.unit,
        decimalPlaces: pointForm.decimalPlaces,
        status: pointForm.isActive ? 'active' : 'inactive',
        currentValue: 0,
        executionTime: 0,
        lastUpdate: new Date().toLocaleString()
      }

      if (editingPoint.value) {
        const index = allCalculations.value.findIndex(p => p.id === editingPoint.value.id)
        if (index !== -1) {
          allCalculations.value[index] = newPoint
        }
        ElMessage.success('Calculated point updated')
      } else {
        allCalculations.value.unshift(newPoint)
        ElMessage.success('Calculated point created')
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
        `Delete calculated point "${row.pointName}"? This action cannot be undone.`,
        'Confirm Delete',
        { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
    allCalculations.value = allCalculations.value.filter(p => p.id !== row.id)
    updatePieChart()
    ElMessage.success('Calculated point deleted')
  } catch (error) {
    // cancelled
  }
}

// 定时计算
const startCalculations = () => {
  calculationTimer = window.setInterval(() => {
    updateCalculatedValues()
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
      generateCalculatedPoints()
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
.calculated-points-container {
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

.formula-section {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.formula-hint {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.test-section {
  background: #f8fafc;
  padding: 16px;
  border-radius: 8px;
}

.test-inputs {
  margin-bottom: 12px;
}

.test-label {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
  margin-right: 12px;
}

.test-values {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.test-tag {
  margin: 0;
}

.test-result {
  margin: 12px 0;
  padding: 10px;
  background: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-value {
  font-family: monospace;
  font-weight: 600;
  color: #409eff;
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
  .calculated-points-container {
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