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
          <span class="loading-title">Cleaning Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Performance Analytics & Reporting System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cleaning-reports-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          Cleaning Reports
        </h1>
        <div class="page-subtitle">Comprehensive cleaning performance analytics and reports</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="generateReport">
          <el-icon><Document /></el-icon> Generate Report
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Report Type Tabs -->
    <div class="report-tabs">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane name="overview">
          <template #label>
            <span><el-icon><DataLine /></el-icon> Overview</span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="daily">
          <template #label>
            <span><el-icon><Sunny /></el-icon> Daily Reports</span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="weekly">
          <template #label>
            <span><el-icon><Calendar /></el-icon> Weekly Reports</span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="monthly">
          <template #label>
            <span><el-icon><Calendar /></el-icon> Monthly Reports</span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="performance">
          <template #label>
            <span><el-icon><TrendCharts /></el-icon> Performance</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Date Range Filter -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 280px"
            @change="filterReports"
        />
        <el-select v-model="zoneFilter" placeholder="Zone" clearable style="width: 130px" @change="filterReports">
          <el-option v-for="z in zones" :key="z" :label="z" :value="z" />
        </el-select>
        <el-select v-model="staffFilter" placeholder="Staff" clearable style="width: 150px" @change="filterReports">
          <el-option v-for="s in staffList" :key="s.id" :label="s.name" :value="s.name" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Overview Tab Content -->
    <div v-show="activeTab === 'overview'">
      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-icon green">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ kpi.completionRate }}<span class="kpi-unit">%</span></div>
            <div class="kpi-label">Task Completion Rate</div>
            <div class="kpi-trend up">↑ {{ kpi.completionTrend }}% vs last month</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon blue">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ kpi.avgResponseTime }}<span class="kpi-unit">min</span></div>
            <div class="kpi-label">Avg Response Time</div>
            <div class="kpi-trend down">↓ {{ kpi.responseTrend }}% vs last month</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon orange">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ kpi.avgCleaningTime }}<span class="kpi-unit">min</span></div>
            <div class="kpi-label">Avg Cleaning Time</div>
            <div class="kpi-trend down">↓ {{ kpi.cleaningTrend }}% vs last month</div>
          </div>
        </div>
        <div class="kpi-card">
          <div class="kpi-icon purple">
            <el-icon><Star /></el-icon>
          </div>
          <div class="kpi-info">
            <div class="kpi-value">{{ kpi.satisfactionScore }}<span class="kpi-unit">/5</span></div>
            <div class="kpi-label">Satisfaction Score</div>
            <div class="kpi-trend up">↑ {{ kpi.satisfactionTrend }}% vs last month</div>
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">Task Completion Trend</span>
            <span class="chart-subtitle">Last 30 days</span>
          </div>
          <div class="chart-container" ref="completionChartEl" style="height: 320px"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">Cleaning Time by Zone</span>
            <span class="chart-subtitle">Average minutes per task</span>
          </div>
          <div class="chart-container" ref="timeByZoneChartEl" style="height: 320px"></div>
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">Staff Performance</span>
            <span class="chart-subtitle">Tasks completed vs target</span>
          </div>
          <div class="chart-container" ref="staffPerformanceChartEl" style="height: 320px"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">Issue Categories</span>
            <span class="chart-subtitle">Most common cleaning issues</span>
          </div>
          <div class="chart-container" ref="issuesChartEl" style="height: 320px"></div>
        </div>
      </div>
    </div>

    <!-- Daily Reports Tab -->
    <div v-show="activeTab === 'daily'">
      <div class="table-container">
        <div class="table-header">
          <span class="table-title">Daily Cleaning Reports</span>
          <el-button size="small" type="primary" @click="exportDailyReport">
            <el-icon><Download /></el-icon> Export Daily Report
          </el-button>
        </div>
        <el-table :data="paginatedDailyReports" stripe style="width: 100%" v-loading="tableLoading">
          <el-table-column prop="date" label="Date" width="120" />
          <el-table-column prop="totalTasks" label="Total Tasks" width="100" align="center" />
          <el-table-column prop="completedTasks" label="Completed" width="100" align="center" />
          <el-table-column prop="completionRate" label="Completion Rate" width="120" align="center">
            <template #default="{ row }">
              <el-progress :percentage="row.completionRate" :stroke-width="6" :show-text="false" />
              <span style="font-size: 12px; margin-left: 8px">{{ row.completionRate }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="avgResponseTime" label="Avg Response" width="110" align="center">
            <template #default="{ row }">{{ row.avgResponseTime }} min</template>
          </el-table-column>
          <el-table-column prop="avgCleaningTime" label="Avg Cleaning" width="110" align="center">
            <template #default="{ row }">{{ row.avgCleaningTime }} min</template>
          </el-table-column>
          <el-table-column prop="satisfactionScore" label="Satisfaction" width="100" align="center">
            <template #default="{ row }">{{ row.satisfactionScore }}/5</template>
          </el-table-column>
          <el-table-column prop="issuesReported" label="Issues" width="90" align="center" />
          <el-table-column label="Actions" width="100" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewDetailReport(row)">View Details</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
              v-model:current-page="dailyCurrentPage"
              v-model:page-size="dailyPageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredDailyReports.length"
              layout="total, sizes, prev, pager, next"
              background
          />
        </div>
      </div>
    </div>

    <!-- Weekly Reports Tab -->
    <div v-show="activeTab === 'weekly'">
      <div class="table-container">
        <div class="table-header">
          <span class="table-title">Weekly Cleaning Reports</span>
          <el-button size="small" type="primary" @click="exportWeeklyReport">
            <el-icon><Download /></el-icon> Export Weekly Report
          </el-button>
        </div>
        <el-table :data="paginatedWeeklyReports" stripe style="width: 100%" v-loading="tableLoading">
          <el-table-column prop="week" label="Week" width="120" />
          <el-table-column prop="totalTasks" label="Total Tasks" width="100" align="center" />
          <el-table-column prop="completedTasks" label="Completed" width="100" align="center" />
          <el-table-column prop="completionRate" label="Completion Rate" width="120" align="center">
            <template #default="{ row }">
              <el-progress :percentage="row.completionRate" :stroke-width="6" :show-text="false" />
              <span style="font-size: 12px; margin-left: 8px">{{ row.completionRate }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="avgResponseTime" label="Avg Response" width="110" align="center">
            <template #default="{ row }">{{ row.avgResponseTime }} min</template>
          </el-table-column>
          <el-table-column prop="totalHours" label="Total Hours" width="100" align="center" />
          <el-table-column prop="overtimeHours" label="Overtime" width="90" align="center" />
          <el-table-column prop="satisfactionScore" label="Satisfaction" width="100" align="center">
            <template #default="{ row }">{{ row.satisfactionScore }}/5</template>
          </el-table-column>
          <el-table-column label="Actions" width="100" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewDetailReport(row)">View Details</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
              v-model:current-page="weeklyCurrentPage"
              v-model:page-size="weeklyPageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredWeeklyReports.length"
              layout="total, sizes, prev, pager, next"
              background
          />
        </div>
      </div>
    </div>

    <!-- Monthly Reports Tab -->
    <div v-show="activeTab === 'monthly'">
      <div class="table-container">
        <div class="table-header">
          <span class="table-title">Monthly Cleaning Reports</span>
          <el-button size="small" type="primary" @click="exportMonthlyReport">
            <el-icon><Download /></el-icon> Export Monthly Report
          </el-button>
        </div>
        <el-table :data="paginatedMonthlyReports" stripe style="width: 100%" v-loading="tableLoading">
          <el-table-column prop="month" label="Month" width="120" />
          <el-table-column prop="totalTasks" label="Total Tasks" width="100" align="center" />
          <el-table-column prop="completedTasks" label="Completed" width="100" align="center" />
          <el-table-column prop="completionRate" label="Completion Rate" width="120" align="center">
            <template #default="{ row }">
              <el-progress :percentage="row.completionRate" :stroke-width="6" :show-text="false" />
              <span style="font-size: 12px; margin-left: 8px">{{ row.completionRate }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="avgResponseTime" label="Avg Response" width="110" align="center">
            <template #default="{ row }">{{ row.avgResponseTime }} min</template>
          </el-table-column>
          <el-table-column prop="totalCost" label="Total Cost" width="120" align="center">
            <template #default="{ row }">${{ row.totalCost }}k</template>
          </el-table-column>
          <el-table-column prop="budgetUtilization" label="Budget Used" width="120" align="center">
            <template #default="{ row }">{{ row.budgetUtilization }}%</template>
          </el-table-column>
          <el-table-column prop="satisfactionScore" label="Satisfaction" width="100" align="center">
            <template #default="{ row }">{{ row.satisfactionScore }}/5</template>
          </el-table-column>
          <el-table-column label="Actions" width="100" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewDetailReport(row)">View Details</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
              v-model:current-page="monthlyCurrentPage"
              v-model:page-size="monthlyPageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredMonthlyReports.length"
              layout="total, sizes, prev, pager, next"
              background
          />
        </div>
      </div>
    </div>

    <!-- Performance Tab -->
    <div v-show="activeTab === 'performance'">
      <!-- Staff Performance Table -->
      <div class="table-container">
        <div class="table-header">
          <span class="table-title">Staff Performance Summary</span>
          <el-button size="small" type="primary" @click="exportPerformanceReport">
            <el-icon><Download /></el-icon> Export Performance Report
          </el-button>
        </div>
        <el-table :data="paginatedStaffPerformance" stripe style="width: 100%" v-loading="tableLoading">
          <el-table-column prop="rank" label="Rank" width="70" align="center">
            <template #default="{ row }">
              <span :class="getRankClass(row.rank)">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="Staff Name" width="140" />
          <el-table-column prop="role" label="Role" width="120" />
          <el-table-column prop="tasksCompleted" label="Tasks Completed" width="120" align="center" />
          <el-table-column prop="targetAchieved" label="Target Achieved" width="120" align="center">
            <template #default="{ row }">{{ row.targetAchieved }}%</template>
          </el-table-column>
          <el-table-column prop="avgResponseTime" label="Avg Response" width="110" align="center">
            <template #default="{ row }">{{ row.avgResponseTime }} min</template>
          </el-table-column>
          <el-table-column prop="avgCleaningTime" label="Avg Cleaning" width="110" align="center">
            <template #default="{ row }">{{ row.avgCleaningTime }} min</template>
          </el-table-column>
          <el-table-column prop="satisfactionScore" label="Satisfaction" width="100" align="center">
            <template #default="{ row }">{{ row.satisfactionScore }}/5</template>
          </el-table-column>
          <el-table-column prop="performance" label="Performance" width="150" align="center">
            <template #default="{ row }">
              <el-progress :percentage="row.performance" :stroke-width="8" :color="getPerformanceColor(row.performance)" />
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
              v-model:current-page="performanceCurrentPage"
              v-model:page-size="performancePageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredStaffPerformance.length"
              layout="total, sizes, prev, pager, next"
              background
          />
        </div>
      </div>

      <!-- Performance Chart -->
      <div class="chart-card" style="margin-top: 20px">
        <div class="chart-header">
          <span class="chart-title">Staff Performance Ranking</span>
          <span class="chart-subtitle">Top performers this month</span>
        </div>
        <div class="chart-container" ref="rankingChartEl" style="height: 400px"></div>
      </div>
    </div>

    <!-- Report Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Report Details - ${selectedReport?.date || selectedReport?.week || selectedReport?.month || 'Performance'}`" width="700px">
      <div v-if="selectedReport" class="report-detail">
        <el-descriptions :column="2" border>
          <template v-for="(value, key) in selectedReport" :key="key">
            <el-descriptions-item :label="formatLabel(key)" v-if="shouldShowDetail(key)">
              <template v-if="key === 'completionRate' || key === 'budgetUtilization' || key === 'performance' || key === 'targetAchieved'">
                <el-progress :percentage="value" :stroke-width="8" />
              </template>
              <template v-else-if="key === 'satisfactionScore'">
                <span>{{ value }}/5</span>
                <el-rate :model-value="value" disabled show-score text-color="#ff9900" :score-template="`${value} points`" />
              </template>
              <template v-else>
                {{ value }}
              </template>
            </el-descriptions-item>
          </template>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="printReport">Print</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataAnalysis, Document, Download, Refresh, DataLine, Sunny,
  Calendar, TrendCharts, CircleCheck, Timer, Clock, Star,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Types ====================
interface DailyReport {
  date: string
  totalTasks: number
  completedTasks: number
  completionRate: number
  avgResponseTime: number
  avgCleaningTime: number
  satisfactionScore: number
  issuesReported: number
}

interface WeeklyReport {
  week: string
  totalTasks: number
  completedTasks: number
  completionRate: number
  avgResponseTime: number
  totalHours: number
  overtimeHours: number
  satisfactionScore: number
}

interface MonthlyReport {
  month: string
  totalTasks: number
  completedTasks: number
  completionRate: number
  avgResponseTime: number
  totalCost: number
  budgetUtilization: number
  satisfactionScore: number
}

interface StaffPerformance {
  rank: number
  name: string
  role: string
  tasksCompleted: number
  targetAchieved: number
  avgResponseTime: number
  avgCleaningTime: number
  satisfactionScore: number
  performance: number
}

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading cleaning reports...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading cleaning reports...',
  'Fetching performance data...',
  'Analyzing trends...',
  'Preparing charts...',
  'Almost ready...'
]

// ==================== Mock Data ====================
const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']

const staffList = [
  { id: 'STF001', name: 'John Smith', role: 'Team Lead' },
  { id: 'STF002', name: 'Sarah Johnson', role: 'Cleaner' },
  { id: 'STF003', name: 'Mike Wilson', role: 'Cleaner' },
  { id: 'STF004', name: 'Emma Davis', role: 'Cleaner' },
  { id: 'STF005', name: 'David Brown', role: 'Supervisor' },
  { id: 'STF006', name: 'Lisa Anderson', role: 'Cleaner' },
  { id: 'STF007', name: 'James Taylor', role: 'Cleaner' },
  { id: 'STF008', name: 'Maria Garcia', role: 'Cleaner' }
]

const generateDailyReports = (): DailyReport[] => {
  const reports: DailyReport[] = []
  const today = new Date()

  for (let i = 29; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().slice(0, 10)

    const totalTasks = 45 + Math.floor(Math.random() * 20)
    const completedTasks = Math.floor(totalTasks * (0.85 + Math.random() * 0.1))
    const completionRate = Math.round((completedTasks / totalTasks) * 100)

    reports.push({
      date: dateStr,
      totalTasks,
      completedTasks,
      completionRate,
      avgResponseTime: Math.floor(5 + Math.random() * 10),
      avgCleaningTime: Math.floor(12 + Math.random() * 15),
      satisfactionScore: parseFloat((3.5 + Math.random() * 1.5).toFixed(1)),
      issuesReported: Math.floor(Math.random() * 8)
    })
  }
  return reports
}

const generateWeeklyReports = (): WeeklyReport[] => {
  const reports: WeeklyReport[] = []
  const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']

  for (const week of weeks) {
    const totalTasks = 280 + Math.floor(Math.random() * 80)
    const completedTasks = Math.floor(totalTasks * (0.88 + Math.random() * 0.1))
    reports.push({
      week,
      totalTasks,
      completedTasks,
      completionRate: Math.round((completedTasks / totalTasks) * 100),
      avgResponseTime: Math.floor(8 + Math.random() * 8),
      totalHours: 160 + Math.floor(Math.random() * 40),
      overtimeHours: Math.floor(Math.random() * 15),
      satisfactionScore: parseFloat((3.8 + Math.random() * 1.2).toFixed(1))
    })
  }
  return reports
}

const generateMonthlyReports = (): MonthlyReport[] => {
  const reports: MonthlyReport[] = []
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  for (const month of months) {
    const totalTasks = 1100 + Math.floor(Math.random() * 300)
    const completedTasks = Math.floor(totalTasks * (0.9 + Math.random() * 0.08))
    reports.push({
      month,
      totalTasks,
      completedTasks,
      completionRate: Math.round((completedTasks / totalTasks) * 100),
      avgResponseTime: Math.floor(7 + Math.random() * 7),
      totalCost: parseFloat((8 + Math.random() * 4).toFixed(1)),
      budgetUtilization: Math.floor(70 + Math.random() * 25),
      satisfactionScore: parseFloat((3.9 + Math.random() * 1.1).toFixed(1))
    })
  }
  return reports
}

const generateStaffPerformance = (): StaffPerformance[] => {
  return staffList.map((staff, index) => {
    const tasksCompleted = 180 + Math.floor(Math.random() * 100)
    const target = 200
    const targetAchieved = Math.min(100, Math.round((tasksCompleted / target) * 100))
    const performance = 65 + Math.floor(Math.random() * 35)

    return {
      rank: index + 1,
      name: staff.name,
      role: staff.role,
      tasksCompleted,
      targetAchieved,
      avgResponseTime: Math.floor(4 + Math.random() * 12),
      avgCleaningTime: Math.floor(10 + Math.random() * 15),
      satisfactionScore: parseFloat((3.5 + Math.random() * 1.5).toFixed(1)),
      performance
    }
  }).sort((a, b) => b.performance - a.performance).map((p, idx) => ({ ...p, rank: idx + 1 }))
}

const dailyReports = ref<DailyReport[]>(generateDailyReports())
const weeklyReports = ref<WeeklyReport[]>(generateWeeklyReports())
const monthlyReports = ref<MonthlyReport[]>(generateMonthlyReports())
const staffPerformance = ref<StaffPerformance[]>(generateStaffPerformance())

// ==================== State ====================
const activeTab = ref('overview')
const dateRange = ref<Date[] | null>(null)
const zoneFilter = ref('')
const staffFilter = ref('')
const detailDialogVisible = ref(false)
const selectedReport = ref<any>(null)

// Pagination
const dailyCurrentPage = ref(1)
const dailyPageSize = ref(10)
const weeklyCurrentPage = ref(1)
const weeklyPageSize = ref(10)
const monthlyCurrentPage = ref(1)
const monthlyPageSize = ref(10)
const performanceCurrentPage = ref(1)
const performancePageSize = ref(10)

// Chart refs
let completionChart: echarts.ECharts | null = null
let timeByZoneChart: echarts.ECharts | null = null
let staffPerformanceChart: echarts.ECharts | null = null
let issuesChart: echarts.ECharts | null = null
let rankingChart: echarts.ECharts | null = null

const completionChartEl = ref<HTMLElement | null>(null)
const timeByZoneChartEl = ref<HTMLElement | null>(null)
const staffPerformanceChartEl = ref<HTMLElement | null>(null)
const issuesChartEl = ref<HTMLElement | null>(null)
const rankingChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const kpi = computed(() => {
  const recentReports = dailyReports.value.slice(-30)
  const avgCompletion = recentReports.reduce((acc, r) => acc + r.completionRate, 0) / recentReports.length
  const avgResponse = recentReports.reduce((acc, r) => acc + r.avgResponseTime, 0) / recentReports.length
  const avgCleaning = recentReports.reduce((acc, r) => acc + r.avgCleaningTime, 0) / recentReports.length
  const avgSatisfaction = recentReports.reduce((acc, r) => acc + r.satisfactionScore, 0) / recentReports.length

  const prevMonthReports = dailyReports.value.slice(-60, -30)
  const prevAvgCompletion = prevMonthReports.length ? prevMonthReports.reduce((acc, r) => acc + r.completionRate, 0) / prevMonthReports.length : avgCompletion

  return {
    completionRate: Math.round(avgCompletion),
    completionTrend: Math.round(((avgCompletion - prevAvgCompletion) / prevAvgCompletion) * 100),
    avgResponseTime: Math.round(avgResponse),
    responseTrend: Math.round(Math.random() * 15),
    avgCleaningTime: Math.round(avgCleaning),
    cleaningTrend: Math.round(Math.random() * 10),
    satisfactionScore: avgSatisfaction.toFixed(1),
    satisfactionTrend: Math.round(Math.random() * 8)
  }
})

const filteredDailyReports = computed(() => {
  let filtered = [...dailyReports.value]
  if (zoneFilter.value) {
    // Filter logic would need to be implemented with actual zone data
    filtered = filtered
  }
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(r => {
      const reportDate = new Date(r.date)
      return reportDate >= start && reportDate <= end
    })
  }
  return filtered
})

const filteredWeeklyReports = computed(() => {
  let filtered = [...weeklyReports.value]
  if (zoneFilter.value) filtered = filtered
  return filtered
})

const filteredMonthlyReports = computed(() => {
  let filtered = [...monthlyReports.value]
  if (zoneFilter.value) filtered = filtered
  return filtered
})

const filteredStaffPerformance = computed(() => {
  let filtered = [...staffPerformance.value]
  if (staffFilter.value) {
    filtered = filtered.filter(s => s.name === staffFilter.value)
  }
  return filtered
})

const paginatedDailyReports = computed(() => {
  const start = (dailyCurrentPage.value - 1) * dailyPageSize.value
  const end = start + dailyPageSize.value
  return filteredDailyReports.value.slice(start, end)
})

const paginatedWeeklyReports = computed(() => {
  const start = (weeklyCurrentPage.value - 1) * weeklyPageSize.value
  const end = start + weeklyPageSize.value
  return filteredWeeklyReports.value.slice(start, end)
})

const paginatedMonthlyReports = computed(() => {
  const start = (monthlyCurrentPage.value - 1) * monthlyPageSize.value
  const end = start + monthlyPageSize.value
  return filteredMonthlyReports.value.slice(start, end)
})

const paginatedStaffPerformance = computed(() => {
  const start = (performanceCurrentPage.value - 1) * performancePageSize.value
  const end = start + performancePageSize.value
  return filteredStaffPerformance.value.slice(start, end)
})

// ==================== Helper Functions ====================
const formatLabel = (key: string) => {
  const labels: Record<string, string> = {
    date: 'Date', week: 'Week', month: 'Month', totalTasks: 'Total Tasks',
    completedTasks: 'Completed Tasks', completionRate: 'Completion Rate',
    avgResponseTime: 'Avg Response Time', avgCleaningTime: 'Avg Cleaning Time',
    satisfactionScore: 'Satisfaction Score', issuesReported: 'Issues Reported',
    totalHours: 'Total Hours', overtimeHours: 'Overtime Hours', totalCost: 'Total Cost',
    budgetUtilization: 'Budget Utilization', rank: 'Rank', name: 'Name',
    role: 'Role', tasksCompleted: 'Tasks Completed', targetAchieved: 'Target Achieved',
    performance: 'Performance'
  }
  return labels[key] || key
}

const shouldShowDetail = (key: string) => {
  const exclude = ['id', 'rank']
  return !exclude.includes(key)
}

const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-1'
  if (rank === 2) return 'rank-2'
  if (rank === 3) return 'rank-3'
  return ''
}

const getPerformanceColor = (value: number) => {
  if (value >= 90) return '#22c55e'
  if (value >= 75) return '#3b82f6'
  if (value >= 60) return '#f59e0b'
  return '#ef4444'
}

const filterReports = () => {
  dailyCurrentPage.value = 1
  weeklyCurrentPage.value = 1
  monthlyCurrentPage.value = 1
}

const resetFilters = () => {
  dateRange.value = null
  zoneFilter.value = ''
  staffFilter.value = ''
  filterReports()
  ElMessage.success('Filters reset')
}

const viewDetailReport = (report: any) => {
  selectedReport.value = report
  detailDialogVisible.value = true
}

const generateReport = () => {
  ElMessage.success('Generating new report...')
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Exporting data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const exportDailyReport = () => exportData()
const exportWeeklyReport = () => exportData()
const exportMonthlyReport = () => exportData()
const exportPerformanceReport = () => exportData()

const printReport = () => {
  ElMessage.info('Print dialog opened')
  detailDialogVisible.value = false
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  dailyReports.value = generateDailyReports()
  weeklyReports.value = generateWeeklyReports()
  monthlyReports.value = generateMonthlyReports()
  staffPerformance.value = generateStaffPerformance()
  refreshCharts()
  refreshing.value = false
  tableLoading.value = false
  ElMessage.success('Data refreshed')
}

const handleTabChange = () => {
  nextTick(() => refreshCharts())
}

// ==================== Chart Functions ====================
const initCompletionChart = () => {
  if (!completionChartEl.value) return
  if (completionChart) completionChart.dispose()

  const dates = dailyReports.value.slice(-30).map(r => r.date.slice(5))
  const completionData = dailyReports.value.slice(-30).map(r => r.completionRate)

  completionChart = echarts.init(completionChartEl.value)
  completionChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: dates, axisLabel: { rotate: 45, interval: 5 } },
    yAxis: { type: 'value', name: 'Completion Rate (%)', min: 70, max: 100 },
    series: [{
      type: 'line', data: completionData, smooth: true,
      lineStyle: { color: '#22c55e', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle', symbolSize: 6,
      label: { show: true, position: 'top', formatter: '{c}%', interval: 5 }
    }]
  })
}

const initTimeByZoneChart = () => {
  if (!timeByZoneChartEl.value) return
  if (timeByZoneChart) timeByZoneChart.dispose()

  const zoneData = [15, 22, 18, 25, 12]

  timeByZoneChart = echarts.init(timeByZoneChartEl.value)
  timeByZoneChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: zones },
    yAxis: { type: 'value', name: 'Minutes' },
    series: [{
      type: 'bar', data: zoneData,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c} min' }
    }]
  })
}

const initStaffPerformanceChart = () => {
  if (!staffPerformanceChartEl.value) return
  if (staffPerformanceChart) staffPerformanceChart.dispose()

  const names = staffPerformance.value.slice(0, 8).map(s => s.name.split(' ')[0])
  const completed = staffPerformance.value.slice(0, 8).map(s => s.tasksCompleted)
  const target = 200

  staffPerformanceChart = echarts.init(staffPerformanceChartEl.value)
  staffPerformanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Completed', 'Target'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: names },
    yAxis: { type: 'value', name: 'Tasks' },
    series: [
      { name: 'Completed', type: 'bar', data: completed, itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] } },
      { name: 'Target', type: 'line', data: Array(8).fill(target), lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } }
    ]
  })
}

const initIssuesChart = () => {
  if (!issuesChartEl.value) return
  if (issuesChart) issuesChart.dispose()

  const issues = ['Low Soap', 'Low TP', 'High Odor', 'Clogged', 'Broken Fixture', 'Other']
  const counts = [45, 52, 38, 25, 18, 22]

  issuesChart = echarts.init(issuesChartEl.value)
  issuesChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} incidents ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: issues },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: issues.map((i, idx) => ({ name: i, value: counts[idx] })),
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initRankingChart = () => {
  if (!rankingChartEl.value) return
  if (rankingChart) rankingChart.dispose()

  const names = staffPerformance.value.slice(0, 8).map(s => s.name.split(' ')[0])
  const performanceData = staffPerformance.value.slice(0, 8).map(s => s.performance)

  rankingChart = echarts.init(rankingChartEl.value)
  rankingChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'value', name: 'Performance Score', max: 100 },
    yAxis: { type: 'category', data: names.reverse(), axisLabel: { fontSize: 12 } },
    series: [{
      type: 'bar', data: performanceData.reverse(),
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: (params: any) => getPerformanceColor(params.value)
      },
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initCompletionChart()
    initTimeByZoneChart()
    initStaffPerformanceChart()
    initIssuesChart()
    if (activeTab.value === 'performance') {
      initRankingChart()
    }
  })
}

watch(activeTab, () => {
  if (activeTab.value === 'performance') {
    nextTick(() => initRankingChart())
  }
})

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [completionChart, timeByZoneChart, staffPerformanceChart, issuesChart, rankingChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

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
      refreshCharts()
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
  const charts = [completionChart, timeByZoneChart, staffPerformanceChart, issuesChart, rankingChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.cleaning-reports-page {
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

/* Loading Screen (same as previous pages) */
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
  font-size: 24px;
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

/* Report Tabs */
.report-tabs {
  background: white;
  border-radius: 16px;
  padding: 0 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__nav-wrap) {
  padding: 8px 0;
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

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.kpi-icon.green { background: #dcfce7; color: #22c55e; }
.kpi-icon.blue { background: #eef2ff; color: #3b82f6; }
.kpi-icon.orange { background: #fef3c7; color: #f59e0b; }
.kpi-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.kpi-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.kpi-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.kpi-trend {
  font-size: 11px;
  margin-top: 4px;
}

.kpi-trend.up { color: #22c55e; }
.kpi-trend.down { color: #ef4444; }

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
  flex-wrap: wrap;
  gap: 12px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  width: 100%;
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Report Detail */
.report-detail {
  padding: 8px;
}

/* Rank Styles */
.rank-1 { color: #fbbf24; font-weight: bold; }
.rank-2 { color: #94a3b8; font-weight: bold; }
.rank-3 { color: #cd7f32; font-weight: bold; }

/* Responsive */
@media (max-width: 1000px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .kpi-grid {
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
  padding: 20px;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
:deep(.el-tabs__item.is-active) {
  color: #3b82f6;
}
:deep(.el-tabs__active-bar) {
  background-color: #3b82f6;
}
</style>