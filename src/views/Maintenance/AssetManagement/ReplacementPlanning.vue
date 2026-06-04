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
          <span class="loading-title">Replacement Planning</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Asset Replacement Strategy</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="replacement-planning-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><RefreshRight /></el-icon>
          Replacement Planning
        </h1>
        <div class="page-subtitle">Strategic asset replacement forecasting and budget planning</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddPlan">
          <el-icon><Plus /></el-icon> Create Plan
        </el-button>
        <el-button @click="generateReport">
          <el-icon><Document /></el-icon> Generate Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon urgent">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ urgentReplacements }}</div>
          <div class="stat-label">Urgent (< 1 year)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon planned">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ plannedReplacements }}</div>
          <div class="stat-label">Planned (1-3 years)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon future">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ futureReplacements }}</div>
          <div class="stat-label">Future (> 3 years)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon budget">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ formatNumber(totalReplacementBudget) }}</div>
          <div class="stat-label">Total Budget Required</div>
        </div>
      </div>
    </div>

    <!-- Budget Forecast Chart -->
    <div class="chart-section">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Replacement Budget Forecast</span>
          <el-radio-group v-model="budgetView" size="small">
            <el-radio-button label="bar">Bar Chart</el-radio-button>
            <el-radio-button label="line">Line Chart</el-radio-button>
          </el-radio-group>
        </div>
        <div class="chart-container" ref="budgetChart"></div>
      </div>
      <div class="summary-card">
        <div class="summary-header">
          <span>Replacement Summary</span>
          <el-tag type="primary" size="small">Next 5 Years</el-tag>
        </div>
        <div class="summary-stats">
          <div class="summary-item">
            <div class="summary-value">{{ totalAssetsToReplace }}</div>
            <div class="summary-label">Assets to Replace</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">${{ formatNumber(avgReplacementCost) }}</div>
            <div class="summary-label">Avg Cost per Asset</div>
          </div>
          <div class="summary-item">
            <div class="summary-value">{{ avgRemainingLife.toFixed(1) }} yrs</div>
            <div class="summary-label">Avg Remaining Life</div>
          </div>
        </div>
        <div class="priority-list">
          <div class="priority-header">Top Priority Replacements</div>
          <div class="priority-items">
            <div v-for="asset in topPriorityAssets.slice(0, 4)" :key="asset.id" class="priority-item">
              <span class="priority-name">{{ asset.name }}</span>
              <span class="priority-value">{{ asset.remainingLife.toFixed(1) }} yrs left</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by asset name..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="priorityFilter" placeholder="Priority" clearable style="width: 130px">
          <el-option label="All Priorities" value="" />
          <el-option label="Urgent (< 1 year)" value="urgent" />
          <el-option label="Planned (1-3 years)" value="planned" />
          <el-option label="Future (> 3 years)" value="future" />
        </el-select>
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 130px">
          <el-option label="All Categories" value="" />
          <el-option label="UPS" value="UPS" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Generator" value="Generator" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="Transformer" value="Transformer" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Total Assets: {{ filteredAssets.length }}</span>
      </div>
    </div>

    <!-- Replacement Table -->
    <div class="table-container">
      <el-table
          :data="paginatedAssets"
          stripe
          border
          style="width: 100%"
          @row-click="viewAssetDetail"
      >
        <el-table-column prop="code" label="Asset Code" width="130" sortable />
        <el-table-column prop="name" label="Asset Name" min-width="160" sortable />
        <el-table-column prop="category" label="Category" width="110">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="installationDate" label="Install Date" width="110" sortable />
        <el-table-column prop="expectedLife" label="Expected Life" width="110" sortable>
          <template #default="{ row }">{{ row.expectedLife }} years</template>
        </el-table-column>
        <el-table-column prop="remainingLife" label="Remaining Life" width="120" sortable>
          <template #default="{ row }">
            <span :class="getRemainingLifeClass(row.remainingLife)">
              {{ row.remainingLife.toFixed(1) }} years
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="replacementCost" label="Replacement Cost" width="140" sortable>
          <template #default="{ row }">${{ formatNumber(row.replacementCost) }}</template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="110">
          <template #default="{ row }">
            <span class="priority-badge" :class="row.priority">
              {{ getPriorityText(row.priority) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : (row.status === 'approved' ? 'success' : 'info')" size="small">
              {{ row.status === 'pending' ? 'Pending' : (row.status === 'approved' ? 'Approved' : 'Completed') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="viewAssetDetail(row)">View</el-button>
            <el-button type="primary" link size="small" @click.stop="approveReplacement(row)">Approve</el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAsset?.name" width="800px" class="replacement-dialog">
      <div v-if="selectedAsset" class="asset-detail">
        <div class="detail-stats">
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.remainingLife.toFixed(1) }} yrs</div>
            <div class="detail-stat-label">Remaining Life</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">${{ formatNumber(selectedAsset.replacementCost) }}</div>
            <div class="detail-stat-label">Est. Replacement Cost</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ getPriorityText(selectedAsset.priority) }}</div>
            <div class="detail-stat-label">Priority</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">Q{{ selectedAsset.recommendedQuarter }} {{ selectedAsset.recommendedYear }}</div>
            <div class="detail-stat-label">Recommended Timeline</div>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Asset Code">{{ selectedAsset.code }}</el-descriptions-item>
          <el-descriptions-item label="Category">{{ selectedAsset.category }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedAsset.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedAsset.model }}</el-descriptions-item>
          <el-descriptions-item label="Installation Date">{{ selectedAsset.installationDate }}</el-descriptions-item>
          <el-descriptions-item label="Expected Life">{{ selectedAsset.expectedLife }} years</el-descriptions-item>
          <el-descriptions-item label="Current Value">${{ formatNumber(selectedAsset.currentValue) }}</el-descriptions-item>
          <el-descriptions-item label="Salvage Value">${{ formatNumber(selectedAsset.salvageValue) }}</el-descriptions-item>
          <el-descriptions-item label="Replacement Cost">${{ formatNumber(selectedAsset.replacementCost) }}</el-descriptions-item>
          <el-descriptions-item label="Net Cost">${{ formatNumber(selectedAsset.replacementCost - selectedAsset.salvageValue) }}</el-descriptions-item>
          <el-descriptions-item label="Justification" :span="2">{{ selectedAsset.justification }}</el-descriptions-item>
          <el-descriptions-item label="Notes" :span="2">{{ selectedAsset.notes || 'No additional notes' }}</el-descriptions-item>
        </el-descriptions>

        <div class="recommendation-section">
          <div class="section-title">Replacement Recommendation</div>
          <div class="recommendation-text" :class="selectedAsset.priority">
            <el-icon><InfoFilled /></el-icon>
            <span>{{ getRecommendationText(selectedAsset) }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="approveReplacement(selectedAsset)">Approve Replacement</el-button>
      </template>
    </el-dialog>

    <!-- Create Plan Dialog -->
    <el-dialog v-model="planDialogVisible" title="Create Replacement Plan" width="550px">
      <el-form :model="planForm" label-width="130px">
        <el-form-item label="Asset" required>
          <el-select v-model="planForm.assetId" placeholder="Select asset" filterable style="width: 100%">
            <el-option
                v-for="asset in assets"
                :key="asset.id"
                :label="`${asset.code} - ${asset.name}`"
                :value="asset.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Target Replacement Date">
          <el-date-picker v-model="planForm.targetDate" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Budget Allocation">
          <el-input-number v-model="planForm.budgetAllocation" :min="0" :step="5000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Justification">
          <el-input v-model="planForm.justification" type="textarea" :rows="3" placeholder="Reason for replacement..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePlan">Create Plan</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  RefreshRight, Plus, Document, Refresh, Warning, Clock,
  Calendar, Money, Search, InfoFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading replacement data...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading replacement data...',
  'Analyzing asset lifecycles...',
  'Calculating budget forecasts...',
  'Generating recommendations...'
]

// ==================== Types ====================
interface ReplacementAsset {
  id: number
  code: string
  name: string
  category: string
  manufacturer: string
  model: string
  installationDate: string
  expectedLife: number
  remainingLife: number
  currentValue: number
  salvageValue: number
  replacementCost: number
  priority: 'urgent' | 'planned' | 'future'
  status: 'pending' | 'approved' | 'completed'
  recommendedQuarter: number
  recommendedYear: number
  justification: string
  notes: string
}

// ==================== Mock Data (20 assets) ====================
const assets = ref<ReplacementAsset[]>([
  { id: 1, code: 'AST-001', name: 'UPS-01', category: 'UPS', manufacturer: 'Schneider Electric', model: 'Galaxy VX', installationDate: '2022-03-15', expectedLife: 10, remainingLife: 7.5, currentValue: 38000, salvageValue: 5000, replacementCost: 52000, priority: 'future', status: 'pending', recommendedQuarter: 3, recommendedYear: 2031, justification: 'Unit still in good condition, monitoring recommended.', notes: '' },
  { id: 2, code: 'AST-002', name: 'CRAC-01', category: 'CRAC', manufacturer: 'Vertiv', model: 'Liebert CRV', installationDate: '2021-11-20', expectedLife: 8, remainingLife: 4.2, currentValue: 21000, salvageValue: 3000, replacementCost: 32000, priority: 'planned', status: 'pending', recommendedQuarter: 2, recommendedYear: 2028, justification: 'Compressor efficiency declining, plan replacement before major failure.', notes: '' },
  { id: 3, code: 'AST-003', name: 'Generator-01', category: 'Generator', manufacturer: 'Caterpillar', model: '3516', installationDate: '2020-08-10', expectedLife: 15, remainingLife: 10.5, currentValue: 85000, salvageValue: 15000, replacementCost: 140000, priority: 'future', status: 'pending', recommendedQuarter: 4, recommendedYear: 2034, justification: 'Good condition, regular maintenance performed.', notes: '' },
  { id: 4, code: 'AST-004', name: 'PDU-A01', category: 'PDU', manufacturer: 'Raritan', model: 'PX-5000', installationDate: '2023-01-10', expectedLife: 7, remainingLife: 5.2, currentValue: 7800, salvageValue: 1000, replacementCost: 9500, priority: 'future', status: 'pending', recommendedQuarter: 1, recommendedYear: 2029, justification: 'No issues detected.', notes: '' },
  { id: 5, code: 'AST-005', name: 'Chiller-01', category: 'Chiller', manufacturer: 'Trane', model: 'CenTraVac', installationDate: '2019-06-05', expectedLife: 12, remainingLife: 6.5, currentValue: 45000, salvageValue: 8000, replacementCost: 105000, priority: 'planned', status: 'approved', recommendedQuarter: 3, recommendedYear: 2030, justification: 'High maintenance costs, efficiency degradation.', notes: 'Approved for FY2030 budget' },
  { id: 6, code: 'AST-006', name: 'Transformer-01', category: 'Transformer', manufacturer: 'ABB', model: 'RESIBLOC', installationDate: '2021-04-12', expectedLife: 20, remainingLife: 16.5, currentValue: 26000, salvageValue: 4000, replacementCost: 38000, priority: 'future', status: 'pending', recommendedQuarter: 2, recommendedYear: 2040, justification: 'Excellent condition.', notes: '' },
  { id: 7, code: 'AST-007', name: 'HVAC-AHU-01', category: 'HVAC', manufacturer: 'Carrier', model: '39CQ', installationDate: '2020-10-18', expectedLife: 10, remainingLife: 5.8, currentValue: 12000, salvageValue: 2000, replacementCost: 22000, priority: 'planned', status: 'pending', recommendedQuarter: 1, recommendedYear: 2030, justification: 'Motor showing signs of wear, belt replacement frequency increasing.', notes: '' },
  { id: 8, code: 'AST-008', name: 'CoolingTower-01', category: 'Cooling Tower', manufacturer: 'Baltimore', model: 'NC8400', installationDate: '2021-09-22', expectedLife: 15, remainingLife: 11.5, currentValue: 18500, salvageValue: 3000, replacementCost: 28000, priority: 'future', status: 'pending', recommendedQuarter: 3, recommendedYear: 2035, justification: 'Regular maintenance ensures longevity.', notes: '' },
  { id: 9, code: 'AST-009', name: 'UPS-02', category: 'UPS', manufacturer: 'Eaton', model: '9395', installationDate: '2023-06-01', expectedLife: 10, remainingLife: 8.8, currentValue: 52000, salvageValue: 6000, replacementCost: 58000, priority: 'future', status: 'pending', recommendedQuarter: 2, recommendedYear: 2032, justification: 'New installation.', notes: '' },
  { id: 10, code: 'AST-010', name: 'Generator-02', category: 'Generator', manufacturer: 'Cummins', model: 'C2000D5', installationDate: '2018-11-10', expectedLife: 12, remainingLife: 2.5, currentValue: 25000, salvageValue: 8000, replacementCost: 125000, priority: 'urgent', status: 'approved', recommendedQuarter: 2, recommendedYear: 2026, justification: 'Major engine issues, high repair costs. Replacement cost-effective.', notes: 'Urgent replacement approved' },
  { id: 11, code: 'AST-011', name: 'PDU-B01', category: 'PDU', manufacturer: 'Schneider Electric', model: 'APC AP8858', installationDate: '2023-03-20', expectedLife: 7, remainingLife: 5.5, currentValue: 6700, salvageValue: 800, replacementCost: 8200, priority: 'future', status: 'pending', recommendedQuarter: 1, recommendedYear: 2029, justification: 'Normal operation.', notes: '' },
  { id: 12, code: 'AST-012', name: 'CRAC-02', category: 'CRAC', manufacturer: 'Stulz', model: 'CyberAir', installationDate: '2022-05-10', expectedLife: 8, remainingLife: 5.2, currentValue: 30000, salvageValue: 3500, replacementCost: 36000, priority: 'future', status: 'pending', recommendedQuarter: 3, recommendedYear: 2029, justification: 'Good performance.', notes: '' },
  { id: 13, code: 'AST-013', name: 'UPS-03', category: 'UPS', manufacturer: 'Vertiv', model: 'Liebert EXM', installationDate: '2023-08-05', expectedLife: 10, remainingLife: 8.8, currentValue: 36000, salvageValue: 4500, replacementCost: 42000, priority: 'future', status: 'pending', recommendedQuarter: 4, recommendedYear: 2032, justification: 'Recently installed.', notes: '' },
  { id: 14, code: 'AST-014', name: 'Chiller-02', category: 'Chiller', manufacturer: 'York', model: 'YVAA', installationDate: '2022-04-18', expectedLife: 12, remainingLife: 9.5, currentValue: 73000, salvageValue: 10000, replacementCost: 96000, priority: 'future', status: 'pending', recommendedQuarter: 2, recommendedYear: 2033, justification: 'Efficient operation.', notes: '' },
  { id: 15, code: 'AST-015', name: 'Transformer-02', category: 'Transformer', manufacturer: 'Siemens', model: 'GEAFOL', installationDate: '2019-12-01', expectedLife: 20, remainingLife: 14.5, currentValue: 30000, salvageValue: 5000, replacementCost: 40000, priority: 'future', status: 'pending', recommendedQuarter: 4, recommendedYear: 2038, justification: 'Normal condition.', notes: '' },
  { id: 16, code: 'AST-016', name: 'HVAC-AHU-02', category: 'HVAC', manufacturer: 'Daikin', model: 'MPS', installationDate: '2021-12-12', expectedLife: 10, remainingLife: 6.2, currentValue: 10500, salvageValue: 1500, replacementCost: 18000, priority: 'planned', status: 'pending', recommendedQuarter: 1, recommendedYear: 2030, justification: 'Fan motor maintenance frequency increasing.', notes: '' },
  { id: 17, code: 'AST-017', name: 'CoolingTower-02', category: 'Cooling Tower', manufacturer: 'EVAPCO', model: 'ATC', installationDate: '2020-09-15', expectedLife: 15, remainingLife: 10.8, currentValue: 20000, salvageValue: 2500, replacementCost: 28000, priority: 'future', status: 'pending', recommendedQuarter: 3, recommendedYear: 2034, justification: 'Good condition.', notes: '' },
  { id: 18, code: 'AST-018', name: 'CRAC-03', category: 'CRAC', manufacturer: 'Schneider Electric', model: 'Uniflair', installationDate: '2019-04-10', expectedLife: 8, remainingLife: 2.2, currentValue: 15000, salvageValue: 2500, replacementCost: 35000, priority: 'urgent', status: 'pending', recommendedQuarter: 1, recommendedYear: 2026, justification: 'Compressor failure imminent, high repair cost.', notes: 'Critical condition' },
  { id: 19, code: 'AST-019', name: 'PDU-C01', category: 'PDU', manufacturer: 'ServerTech', model: 'Sentry', installationDate: '2023-06-10', expectedLife: 7, remainingLife: 5.8, currentValue: 6300, salvageValue: 700, replacementCost: 7800, priority: 'future', status: 'pending', recommendedQuarter: 2, recommendedYear: 2029, justification: 'Normal.', notes: '' },
  { id: 20, code: 'AST-020', name: 'Generator-03', category: 'Generator', manufacturer: 'Kohler', model: 'KD2000', installationDate: '2023-10-15', expectedLife: 15, remainingLife: 13.8, currentValue: 105000, salvageValue: 12000, replacementCost: 130000, priority: 'future', status: 'pending', recommendedQuarter: 4, recommendedYear: 2037, justification: 'New installation.', notes: '' }
])

// ==================== State ====================
const searchText = ref('')
const priorityFilter = ref('')
const categoryFilter = ref('')
const budgetView = ref('bar')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const planDialogVisible = ref(false)
const selectedAsset = ref<ReplacementAsset | null>(null)

const planForm = ref({
  assetId: null as number | null,
  targetDate: '',
  budgetAllocation: 0,
  justification: ''
})

let budgetChartInstance: echarts.ECharts | null = null
const budgetChart = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const urgentReplacements = computed(() => {
  return assets.value.filter(a => a.priority === 'urgent' && a.status !== 'completed').length
})

const plannedReplacements = computed(() => {
  return assets.value.filter(a => a.priority === 'planned' && a.status !== 'completed').length
})

const futureReplacements = computed(() => {
  return assets.value.filter(a => a.priority === 'future' && a.status !== 'completed').length
})

const totalReplacementBudget = computed(() => {
  return assets.value
      .filter(a => a.priority !== 'future' || a.status === 'approved')
      .reduce((sum, a) => sum + a.replacementCost, 0)
})

const totalAssetsToReplace = computed(() => {
  return assets.value.filter(a => a.priority !== 'future').length
})

const avgReplacementCost = computed(() => {
  const filtered = assets.value.filter(a => a.priority !== 'future')
  if (filtered.length === 0) return 0
  return Math.round(filtered.reduce((sum, a) => sum + a.replacementCost, 0) / filtered.length)
})

const avgRemainingLife = computed(() => {
  return assets.value.reduce((sum, a) => sum + a.remainingLife, 0) / assets.value.length
})

const topPriorityAssets = computed(() => {
  return [...assets.value]
      .sort((a, b) => a.remainingLife - b.remainingLife)
      .slice(0, 6)
})

const filteredAssets = computed(() => {
  let filtered = [...assets.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a => a.name.toLowerCase().includes(search))
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(a => a.priority === priorityFilter.value)
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(a => a.category === categoryFilter.value)
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
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getCategoryTagType = (category: string) => {
  const map: Record<string, string> = {
    UPS: 'primary', CRAC: 'success', PDU: 'warning', Generator: 'danger',
    Chiller: 'info', Transformer: 'primary', HVAC: 'info', 'Cooling Tower': 'warning'
  }
  return map[category] || 'info'
}

const getPriorityText = (priority: string) => {
  const map: Record<string, string> = { urgent: 'Urgent', planned: 'Planned', future: 'Future' }
  return map[priority] || priority
}

const getRemainingLifeClass = (life: number) => {
  if (life < 1) return 'life-urgent'
  if (life < 3) return 'life-warning'
  return 'life-good'
}

const getRecommendationText = (asset: ReplacementAsset) => {
  if (asset.priority === 'urgent') {
    return `⚠️ CRITICAL: This asset has only ${asset.remainingLife.toFixed(1)} years of remaining life. Immediate replacement planning is recommended to avoid operational disruption.`
  } else if (asset.priority === 'planned') {
    return `📋 This asset should be replaced within the next ${asset.remainingLife.toFixed(1)} years. Recommended replacement window: Q${asset.recommendedQuarter} ${asset.recommendedYear}.`
  } else {
    return `✅ This asset is in good condition with ${asset.remainingLife.toFixed(1)} years of expected life remaining. Continue regular monitoring and maintenance.`
  }
}

const viewAssetDetail = (asset: ReplacementAsset) => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
}

const approveReplacement = (asset: ReplacementAsset | null) => {
  if (!asset) return
  ElMessageBox.confirm(
      `Approve replacement plan for ${asset.name}?`,
      'Confirm Approval',
      { confirmButtonText: 'Approve', cancelButtonText: 'Cancel', type: 'info' }
  ).then(() => {
    const index = assets.value.findIndex(a => a.id === asset.id)
    if (index !== -1) {
      assets.value[index].status = 'approved'
      ElMessage.success(`Replacement approved for ${asset.name}`)
    }
    detailDialogVisible.value = false
  }).catch(() => {})
}

const openAddPlan = () => {
  planForm.value = {
    assetId: null,
    targetDate: '',
    budgetAllocation: 0,
    justification: ''
  }
  planDialogVisible.value = true
}

const savePlan = () => {
  if (!planForm.value.assetId) {
    ElMessage.warning('Please select an asset')
    return
  }
  ElMessage.success('Replacement plan created')
  planDialogVisible.value = false
}

const generateReport = () => {
  ElMessage.success('Report generation started')
  setTimeout(() => {
    ElMessage.success('Replacement report generated')
  }, 1500)
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Charts ====================
const initBudgetChart = () => {
  if (!budgetChart.value) return
  if (budgetChartInstance) budgetChartInstance.dispose()

  const years = ['2025', '2026', '2027', '2028', '2029', '2030']
  const budgetData = [125000, 250000, 180000, 220000, 195000, 280000]

  budgetChartInstance = echarts.init(budgetChart.value)

  if (budgetView.value === 'bar') {
    budgetChartInstance.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: ${c}' },
      grid: { top: 30, left: 60, right: 20, bottom: 20 },
      xAxis: { type: 'category', data: years, name: 'Year' },
      yAxis: { type: 'value', name: 'Budget ($)', axisLabel: { formatter: (v: number) => '$' + (v / 1000) + 'k' } },
      series: [{
        type: 'bar',
        data: budgetData,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: (params: any) => {
            const colors = ['#3b82f6', '#ef4444', '#f59e0b', '#22c55e', '#8b5cf6', '#06b6d4']
            return colors[params.dataIndex]
          }
        },
        label: { show: true, position: 'top', formatter: (p: any) => '$' + (p.value / 1000) + 'k' }
      }]
    })
  } else {
    budgetChartInstance.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: ${c}' },
      grid: { top: 30, left: 60, right: 20, bottom: 20 },
      xAxis: { type: 'category', data: years, name: 'Year' },
      yAxis: { type: 'value', name: 'Budget ($)', axisLabel: { formatter: (v: number) => '$' + (v / 1000) + 'k' } },
      series: [{
        type: 'line',
        data: budgetData,
        smooth: true,
        lineStyle: { color: '#3b82f6', width: 3 },
        areaStyle: { opacity: 0.2 },
        symbol: 'circle',
        symbolSize: 8,
        label: { show: true, formatter: (p: any) => '$' + (p.value / 1000) + 'k' }
      }]
    })
  }

  budgetChartInstance.resize()
}

watch(budgetView, () => {
  nextTick(() => initBudgetChart())
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
      nextTick(() => initBudgetChart())
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
.replacement-planning-page {
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

.stat-icon.urgent { background: #fee2e2; color: #ef4444; }
.stat-icon.planned { background: #fef3c7; color: #f59e0b; }
.stat-icon.future { background: #dcfce7; color: #22c55e; }
.stat-icon.budget { background: #eef2ff; color: #3b82f6; }

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

.summary-card {
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
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.summary-item {
  text-align: center;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.summary-label {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.priority-list {
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
}

.priority-header {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
  margin-bottom: 12px;
}

.priority-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.priority-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.priority-name {
  color: #475569;
}

.priority-value {
  color: #ef4444;
  font-weight: 500;
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

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.priority-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.priority-badge.urgent { background: #fee2e2; color: #dc2626; }
.priority-badge.planned { background: #fef3c7; color: #d97706; }
.priority-badge.future { background: #dcfce7; color: #16a34a; }

.life-urgent { color: #ef4444; font-weight: 600; }
.life-warning { color: #f59e0b; font-weight: 600; }
.life-good { color: #22c55e; font-weight: 600; }

/* Replacement Dialog */
.replacement-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.asset-detail {
  padding: 8px;
}

.detail-stats {
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

.recommendation-section {
  margin-top: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.recommendation-text {
  padding: 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.recommendation-text.urgent { background: #fee2e2; color: #dc2626; }
.recommendation-text.planned { background: #fef3c7; color: #d97706; }
.recommendation-text.future { background: #dcfce7; color: #16a34a; }

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-section {
    flex-direction: column;
  }

  .detail-stats {
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