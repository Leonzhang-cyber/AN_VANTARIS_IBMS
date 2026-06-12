<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Sort, Top, Rank
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Calculating risk scores...',
  'Ranking equipment...',
  'Analyzing impact factors...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedRiskLevel = ref('all')
const selectedType = ref('all')
const detailsVisible = ref(false)
const chartRef = ref(null)
const heatmapRef = ref(null)

let riskChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null

// Risk level filters
const riskLevelOptions = [
  { value: 'all', label: 'All Levels' },
  { value: 'critical', label: 'Critical', color: '#F56C6C' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Type filters
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'hvac', label: 'HVAC' },
  { value: 'electrical', label: 'Electrical' },
  { value: 'pump', label: 'Pump' },
  { value: 'chiller', label: 'Chiller' }
]

// Risk ranking data
const riskRanking = ref([
  {
    id: 'RISK001', equipment: 'Chiller-1', type: 'chiller', riskLevel: 'critical',
    riskScore: 94, probability: 85, impact: 96, priority: 1,
    factors: ['Age (8 years)', 'Vibration high', 'Temp spikes', 'Maintenance overdue'],
    recommendation: 'Immediate replacement required',
    estimatedCost: 25000, downtime: '48 hours', lastInspection: '2023-11-15'
  },
  {
    id: 'RISK002', equipment: 'AHU-2', type: 'hvac', riskLevel: 'high',
    riskScore: 82, probability: 78, impact: 85, priority: 2,
    factors: ['Bearing wear', 'Energy efficiency drop', 'Unusual noise'],
    recommendation: 'Schedule bearing replacement within 2 weeks',
    estimatedCost: 4500, downtime: '8 hours', lastInspection: '2023-12-10'
  },
  {
    id: 'RISK003', equipment: 'Cooling Tower', type: 'hvac', riskLevel: 'high',
    riskScore: 76, probability: 72, impact: 80, priority: 3,
    factors: ['Fan motor issues', 'Vibration', 'Corrosion signs'],
    recommendation: 'Motor inspection and balancing',
    estimatedCost: 3800, downtime: '6 hours', lastInspection: '2023-12-05'
  },
  {
    id: 'RISK004', equipment: 'Main Switchboard', type: 'electrical', riskLevel: 'medium',
    riskScore: 58, probability: 52, impact: 64, priority: 4,
    factors: ['Age (12 years)', 'Thermal hotspots', 'Loose connections'],
    recommendation: 'Thermal imaging inspection',
    estimatedCost: 1200, downtime: '4 hours', lastInspection: '2023-11-20'
  },
  {
    id: 'RISK005', equipment: 'VFD Pump', type: 'pump', riskLevel: 'medium',
    riskScore: 52, probability: 48, impact: 56, priority: 5,
    factors: ['Seal wear', 'Efficiency loss', 'Age (6 years)'],
    recommendation: 'Seal replacement and calibration',
    estimatedCost: 2800, downtime: '5 hours', lastInspection: '2023-12-12'
  },
  {
    id: 'RISK006', equipment: 'Chiller-2', type: 'chiller', riskLevel: 'medium',
    riskScore: 45, probability: 42, impact: 48, priority: 6,
    factors: ['Refrigerant leak detected', 'Reduced capacity'],
    recommendation: 'Leak repair and recharge',
    estimatedCost: 5200, downtime: '10 hours', lastInspection: '2023-12-01'
  },
  {
    id: 'RISK007', equipment: 'AHU-1', type: 'hvac', riskLevel: 'low',
    riskScore: 28, probability: 25, impact: 32, priority: 7,
    factors: ['Filter clogging', 'Minor efficiency drop'],
    recommendation: 'Filter replacement and cleaning',
    estimatedCost: 450, downtime: '2 hours', lastInspection: '2023-12-18'
  },
  {
    id: 'RISK008', equipment: 'Air Compressor', type: 'pump', riskLevel: 'low',
    riskScore: 22, probability: 20, impact: 24, priority: 8,
    factors: ['Normal wear', 'Routine maintenance due'],
    recommendation: 'Scheduled oil change and inspection',
    estimatedCost: 380, downtime: '3 hours', lastInspection: '2023-12-15'
  }
])

// Risk statistics
const riskStats = reactive({
  total: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  avgRiskScore: 0,
  totalCost: 0,
  topRisk: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: riskRanking.value.length
})

// Filtered rankings
const filteredRankings = computed(() => {
  let filtered = riskRanking.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.equipment.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedRiskLevel.value !== 'all') {
    filtered = filtered.filter(r => r.riskLevel === selectedRiskLevel.value)
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(r => r.type === selectedType.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
      setTimeout(() => {
        initChart()
        initHeatmap()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  riskChart = echarts.init(chartRef.value)
  riskChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Risk Score'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: riskRanking.value.map(r => r.equipment), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Risk Score', min: 0, max: 100 },
    series: [{
      name: 'Risk Score',
      type: 'bar',
      data: riskRanking.value.map(r => r.riskScore),
      itemStyle: {
        color: (params: any) => {
          const value = params.value
          if (value >= 80) return '#F56C6C'
          if (value >= 50) return '#E6A23C'
          return '#67C23A'
        },
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  })
}

const initHeatmap = () => {
  if (!heatmapRef.value) return

  // Probability vs Impact heatmap data
  const heatmapData = riskRanking.value.map((r, index) => [
    r.probability,
    r.impact,
    r.riskScore,
    r.equipment
  ])

  heatmapChart = echarts.init(heatmapRef.value)
  heatmapChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const data = params.data
        return `<strong>${data[3]}</strong><br/>
                Probability: ${data[0]}%<br/>
                Impact: ${data[1]}%<br/>
                Risk Score: ${data[2]}`
      }
    },
    xAxis: { type: 'value', name: 'Probability (%)', min: 0, max: 100 },
    yAxis: { type: 'value', name: 'Impact (%)', min: 0, max: 100 },
    series: [{
      type: 'scatter',
      data: heatmapData,
      symbolSize: (val: any) => {
        return 15 + (val[2] / 100) * 25
      },
      itemStyle: {
        color: (params: any) => {
          const score = params.data[2]
          if (score >= 80) return '#F56C6C'
          if (score >= 50) return '#E6A23C'
          return '#67C23A'
        },
        borderColor: '#fff',
        borderWidth: 2,
        shadowBlur: 10,
        shadowColor: 'rgba(0,0,0,0.3)'
      },
      label: {
        show: true,
        formatter: (params: any) => params.data[3],
        position: 'right',
        offset: [5, 0],
        fontSize: 11
      }
    }]
  })
}

const updateStats = () => {
  riskStats.total = riskRanking.value.length
  riskStats.critical = riskRanking.value.filter(r => r.riskLevel === 'critical').length
  riskStats.high = riskRanking.value.filter(r => r.riskLevel === 'high').length
  riskStats.medium = riskRanking.value.filter(r => r.riskLevel === 'medium').length
  riskStats.low = riskRanking.value.filter(r => r.riskLevel === 'low').length
  riskStats.avgRiskScore = Math.round(riskRanking.value.reduce((sum, r) => sum + r.riskScore, 0) / riskRanking.value.length)
  riskStats.totalCost = riskRanking.value.reduce((sum, r) => sum + r.estimatedCost, 0)
  riskStats.topRisk = riskRanking.value[0]?.equipment || 'N/A'
}

const handleResize = () => {
  riskChart?.resize()
  heatmapChart?.resize()
}

// ==================== Risk Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  initChart()
  loading.value = false
  ElMessage.success('Risk ranking refreshed successfully')
}

const viewDetails = (risk: any) => {
  selectedRisk.value = risk
  detailsVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getRiskColor = (level: string) => {
  switch (level) {
    case 'critical': return '#F56C6C'
    case 'high': return '#F56C6C'
    case 'medium': return '#E6A23C'
    case 'low': return '#67C23A'
    default: return '#909399'
  }
}

const getRiskIcon = (level: string) => {
  switch (level) {
    case 'critical': return '🔴'
    case 'high': return '🟠'
    case 'medium': return '🟡'
    case 'low': return '🟢'
    default: return '⚪'
  }
}

const formatCurrency = (value: number) => {
  return `$${value.toLocaleString()}`
}

const selectedRisk = ref<any>(null)
</script>

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
          <span class="loading-title">Loading Risk Ranking</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Predictive Maintenance - Risk Ranking</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="risk-ranking-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Risk Ranking</h1>
        <p class="page-subtitle">Prioritized equipment risk assessment based on probability and impact</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button size="large">
          <el-icon><Setting /></el-icon>
          Settings
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ riskStats.total }}</div>
          <div class="stat-label">Total Equipment</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ riskStats.critical }} Critical</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon score-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ riskStats.avgRiskScore }}</div>
          <div class="stat-label">Avg Risk Score</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="riskStats.avgRiskScore" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon cost-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatCurrency(riskStats.totalCost) }}</div>
          <div class="stat-label">Estimated Risk Cost</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+15% this quarter</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon top-icon">
          <el-icon><Top /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ riskStats.topRisk }}</div>
          <div class="stat-label">Highest Risk</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">Score: {{ riskRanking[0]?.riskScore || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- Risk Level Legend -->
    <div class="risk-legend">
      <div class="legend-item">
        <span class="legend-dot critical"></span>
        <span>Critical (80-100) - Immediate Action</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot high"></span>
        <span>High (60-79) - High Priority</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot medium"></span>
        <span>Medium (40-59) - Monitor Closely</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot low"></span>
        <span>Low (0-39) - Routine</span>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Risk Score by Equipment</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="risk-chart" style="height: 320px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Probability vs Impact Matrix</h3>
          <el-button text type="primary" @click="initHeatmap">Refresh</el-button>
        </div>
        <div ref="heatmapRef" class="heatmap-chart" style="height: 320px"></div>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search equipment..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="risk-filters">
          <button
              v-for="r in riskLevelOptions"
              :key="r.value"
              class="risk-chip"
              :class="{ active: selectedRiskLevel === r.value }"
              @click="selectedRiskLevel = r.value"
          >
            <span class="chip-dot" :style="{ background: r.color }"></span>
            <span>{{ r.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedType" placeholder="Equipment Type" clearable style="width: 150px">
          <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>
    </div>

    <!-- Risk Ranking Table -->
    <el-card shadow="never" class="ranking-card">
      <template #header>
        <div class="table-header">
          <span>Risk Ranking List</span>
          <div class="table-actions">
            <el-tag type="info" size="small">Sorted by risk score (highest first)</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredRankings" stripe style="width: 100%">
        <el-table-column label="Rank" width="70" align="center">
          <template #default="{ $index }">
            <div class="rank-badge" :class="{
              'rank-1': $index === 0,
              'rank-2': $index === 1,
              'rank-3': $index === 2
            }">
              #{{ $index + 1 }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="equipment" label="Equipment" min-width="150" />
        <el-table-column prop="type" label="Type" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Risk Score" width="130" align="center">
          <template #default="{ row }">
            <div class="risk-score-cell">
              <span class="score-value" :style="{ color: getRiskColor(row.riskLevel) }">
                {{ row.riskScore }}
              </span>
              <el-progress
                  :percentage="row.riskScore"
                  :stroke-width="6"
                  :show-text="false"
                  :color="getRiskColor(row.riskLevel)"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Probability" width="110" align="center">
          <template #default="{ row }">
            {{ row.probability }}%
          </template>
        </el-table-column>
        <el-table-column label="Impact" width="100" align="center">
          <template #default="{ row }">
            {{ row.impact }}%
          </template>
        </el-table-column>
        <el-table-column label="Risk Level" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="row.riskLevel === 'critical' || row.riskLevel === 'high' ? 'danger' : row.riskLevel === 'medium' ? 'warning' : 'success'" size="small">
              {{ getRiskIcon(row.riskLevel) }} {{ row.riskLevel.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Est. Cost" width="120" align="center">
          <template #default="{ row }">
            {{ formatCurrency(row.estimatedCost) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[8, 12, 16, 24]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Risk Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedRisk?.equipment" width="650px">
      <div class="dialog-content">
        <div class="risk-summary" :class="selectedRisk?.riskLevel">
          <div class="risk-score-large">
            <span class="score-value">{{ selectedRisk?.riskScore }}</span>
            <span class="score-label">Risk Score</span>
          </div>
          <div class="risk-details">
            <div class="detail-item">
              <span class="label">Probability:</span>
              <span class="value">{{ selectedRisk?.probability }}%</span>
            </div>
            <div class="detail-item">
              <span class="label">Impact:</span>
              <span class="value">{{ selectedRisk?.impact }}%</span>
            </div>
            <div class="detail-item">
              <span class="label">Priority Rank:</span>
              <span class="value">#{{ selectedRisk?.priority }}</span>
            </div>
          </div>
        </div>

        <el-divider />

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Equipment ID">{{ selectedRisk?.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedRisk?.type?.toUpperCase() }}</el-descriptions-item>
          <el-descriptions-item label="Risk Level" :span="2">
            <el-tag :type="selectedRisk?.riskLevel === 'critical' || selectedRisk?.riskLevel === 'high' ? 'danger' : selectedRisk?.riskLevel === 'medium' ? 'warning' : 'success'" size="small">
              {{ getRiskIcon(selectedRisk?.riskLevel) }} {{ selectedRisk?.riskLevel?.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Risk Factors" :span="2">
            <div class="factors-list">
              <el-tag v-for="factor in selectedRisk?.factors" :key="factor" size="small" style="margin: 2px">
                {{ factor }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Recommendation" :span="2">{{ selectedRisk?.recommendation }}</el-descriptions-item>
          <el-descriptions-item label="Estimated Cost">{{ formatCurrency(selectedRisk?.estimatedCost) }}</el-descriptions-item>
          <el-descriptions-item label="Expected Downtime">{{ selectedRisk?.downtime }}</el-descriptions-item>
          <el-descriptions-item label="Last Inspection">{{ selectedRisk?.lastInspection }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedRisk?.riskLevel === 'critical'" class="critical-alert">
          <el-alert
              title="Critical Risk - Immediate Action Required"
              type="error"
              show-icon
              :closable="false"
          >
            <template #default>
              <p>This equipment poses a critical risk to operations. Schedule immediate maintenance.</p>
            </template>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="detailsVisible = false">Schedule Mitigation</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

/* ==================== Main Content ==================== */
.risk-ranking-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.score-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.cost-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.top-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  color: #67c23a;
}

/* Risk Legend */
.risk-legend {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 24px;
  padding: 12px 20px;
  background: white;
  border-radius: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.critical { background: #F56C6C; }
.legend-dot.high { background: #F56C6C; }
.legend-dot.medium { background: #E6A23C; }
.legend-dot.low { background: #67C23A; }

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.risk-chart,
.heatmap-chart {
  width: 100%;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.risk-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.risk-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.risk-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.risk-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Ranking Card */
.ranking-card {
  margin-top: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* Table Cell Styles */
.rank-badge {
  display: inline-block;
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
  background: #f5f7fa;
  color: #606266;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #8B6914;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #c0c0c0, #e0e0e0);
  color: #555;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #cd7f32, #e8a870);
  color: #5c3a1e;
}

.risk-score-cell {
  width: 100%;
}

.score-value {
  font-weight: 700;
  font-size: 16px;
  display: block;
  margin-bottom: 4px;
}

/* Dialog Styles */
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.risk-summary {
  display: flex;
  gap: 24px;
  padding: 20px;
  border-radius: 16px;
}

.risk-summary.critical {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
}

.risk-summary.high {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
}

.risk-summary.medium {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
}

.risk-summary.low {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
}

.risk-score-large {
  text-align: center;
  min-width: 100px;
}

.risk-score-large .score-value {
  font-size: 48px;
  font-weight: 700;
  display: block;
}

.risk-summary.critical .risk-score-large .score-value { color: #f56c6c; }
.risk-summary.high .risk-score-large .score-value { color: #f56c6c; }
.risk-summary.medium .risk-score-large .score-value { color: #e6a23c; }
.risk-summary.low .risk-score-large .score-value { color: #67c23a; }

.risk-score-large .score-label {
  font-size: 12px;
  color: #909399;
}

.risk-details {
  flex: 1;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-item .label {
  color: #909399;
}

.detail-item .value {
  font-weight: 600;
  color: #1e293b;
}

.factors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.critical-alert {
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .risk-ranking-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .risk-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .risk-summary {
    flex-direction: column;
    align-items: center;
  }

  .risk-legend {
    flex-direction: column;
    align-items: center;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>