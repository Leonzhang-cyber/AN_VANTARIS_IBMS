<template>
  <div class="dashboard">
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
          <div class="loading-tip">CDE Executive Dashboard</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- AI Decision Intelligence Banner - 当前激活的决策 -->
      <div v-if="currentActiveDecision" class="decision-banner" :class="currentActiveDecision.severity">
        <div class="banner-icon">
          <el-icon :size="24"><ChatDotRound /></el-icon>
        </div>
        <div class="banner-content">
          <div class="banner-title">
            AI Decision Intelligence
            <span class="priority-badge" :class="currentActiveDecision.severity">
              {{ currentActiveDecision.priority }} · {{ currentActiveDecision.category }}
            </span>
          </div>
          <div class="banner-message">{{ currentActiveDecision.message }}</div>
          <div class="banner-impact">💰 {{ currentActiveDecision.impact }}</div>
        </div>
        <div class="banner-actions">
          <el-button type="primary" size="default" @click="executeDecision(currentActiveDecision)">
            {{ currentActiveDecision.actionText }}
          </el-button>
          <el-button size="default" @click="dismissDecision(currentActiveDecision.id)">
            Dismiss
          </el-button>
        </div>
      </div>
      <div v-else class="decision-banner idle">
        <div class="banner-icon">
          <el-icon :size="24"><CircleCheck /></el-icon>
        </div>
        <div class="banner-content">
          <div class="banner-title">AI Decision Intelligence</div>
          <div class="banner-message">All systems operating normally. No pending decisions.</div>
        </div>
      </div>

      <!-- KPI Cards -->
      <div class="kpi-grid">
        <div class="kpi-card" v-for="kpi in kpiList" :key="kpi.key">
          <div class="kpi-icon" :style="{ background: kpi.bgColor }">
            <el-icon :size="24"><component :is="kpi.icon" /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-value">
              {{ kpi.value }}
              <span class="kpi-unit">{{ kpi.unit }}</span>
            </div>
            <div class="kpi-trend" :class="kpi.trend > 0 ? 'trend-up' : 'trend-down'">
              <el-icon><component :is="kpi.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
              {{ Math.abs(kpi.trend) }}% vs yesterday
            </div>
          </div>
        </div>
      </div>

      <!-- Two Columns -->
      <div class="two-columns">
        <!-- Site Health Map -->
        <div class="card site-health-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><Location /></el-icon>
              Site Health Map
            </span>
          </div>
          <div class="site-list">
            <div v-for="site in siteHealthData" :key="site.name" class="site-item" @click="goToSite(site)">
              <div class="site-info">
                <div class="site-name">
                  <span class="site-dot" :style="{ background: site.statusColor }"></span>
                  {{ site.name }}
                </div>
                <div class="site-metrics">
                  <span class="metric-alarm" :class="{ 'high': site.alarmCount > 5 }">
                    <el-icon><Bell /></el-icon> {{ site.alarmCount }}
                  </span>
                  <span class="metric-energy">
                    <el-icon><Lightning /></el-icon> {{ site.energyIntensity }} kWh/㎡
                  </span>
                </div>
              </div>
              <div class="site-progress">
                <el-progress :percentage="site.healthScore" :color="getHealthColor(site.healthScore)" :stroke-width="8" :show-text="false" />
                <span class="site-score">{{ site.healthScore }} pts</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Real-time Alarm Stream -->
        <div class="card alarm-stream-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><AlarmClock /></el-icon>
              Real-time Alarm Stream
            </span>
            <el-button text type="primary" size="small" @click="clearAllAlerts">Clear All</el-button>
          </div>
          <div class="alarm-list">
            <div v-for="alarm in recentAlarms" :key="alarm.id" class="alarm-item" :class="alarm.severity">
              <div class="alarm-level">
                <el-tag :type="getAlarmTagType(alarm.severity)" size="small" effect="dark">
                  {{ alarm.severity.toUpperCase() }}
                </el-tag>
              </div>
              <div class="alarm-detail">
                <div class="alarm-device">{{ alarm.device }} - {{ alarm.message }}</div>
                <div class="alarm-time">{{ alarm.time }}</div>
              </div>
              <div class="alarm-action">
                <el-button size="small" link type="primary" @click="acknowledgeAlarm(alarm.id)">
                  Acknowledge
                </el-button>
              </div>
            </div>
            <div v-if="recentAlarms.length === 0" class="empty-state">No active alarms</div>
          </div>
        </div>
      </div>

      <!-- Energy & Carbon Trend Chart -->
      <div class="card chart-card">
        <div class="card-header">
          <span class="card-title">
            <el-icon><TrendCharts /></el-icon>
            Energy & Carbon Emission Trend
          </span>
          <div class="chart-controls">
            <el-radio-group v-model="trendPeriod" size="small" @change="updateTrendChart">
              <el-radio-button label="week">Week</el-radio-button>
              <el-radio-button label="month">Month</el-radio-button>
              <el-radio-button label="quarter">Quarter</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div class="chart-container">
          <div ref="trendChartRef" style="width: 100%; height: 100%;"></div>
        </div>
        <div class="chart-stats">
          <div class="stat-item">
            <div class="stat-label">Cumulative Carbon</div>
            <div class="stat-value">{{ cumulativeCarbon }} <span class="stat-unit">t CO₂</span></div>
          </div>
          <div class="stat-item">
            <div class="stat-label">Clean Energy Ratio</div>
            <div class="stat-value">{{ cleanEnergyRatio }}<span class="stat-unit">%</span></div>
          </div>
          <div class="stat-item">
            <div class="stat-label">vs Yesterday</div>
            <div class="stat-value" :class="energyCompare > 0 ? 'text-warning' : 'text-success'">
              {{ energyCompare > 0 ? '+' : '' }}{{ energyCompare }}<span class="stat-unit">%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Device Health + Operational Efficiency -->
      <div class="two-columns">
        <div class="card device-health-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><Cpu /></el-icon>
              Device Health Status
            </span>
          </div>
          <el-table :data="deviceHealthData" stripe size="small" style="width: 100%">
            <el-table-column prop="type" label="Device Type" align="center" />
            <el-table-column prop="onlineRate" label="Online Rate" align="center">
              <template #default="{ row }">
                <div class="online-rate-cell">
                  <el-progress :percentage="row.onlineRate" :color="row.onlineRate >= 95 ? '#67c23a' : '#e6a23c'" :stroke-width="6" :show-text="false" style="width: 80px" />
                  <span class="rate-value">{{ row.onlineRate }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="faultCount" label="Faults" align="center">
              <template #default="{ row }">
                <span :class="{ 'fault-high': row.faultCount > 10 }">{{ row.faultCount }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="trend" label="Trend" align="center">
              <template #default="{ row }">
                <span :class="row.trend > 0 ? 'trend-up-text' : 'trend-down-text'">
                  <el-icon><component :is="row.trend > 0 ? 'CaretTop' : 'CaretBottom'" /></el-icon>
                  {{ Math.abs(row.trend) }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="card ops-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><DataAnalysis /></el-icon>
              Operational Efficiency
            </span>
          </div>
          <div class="ops-grid">
            <div class="ops-item" v-for="item in opsData" :key="item.key">
              <div class="ops-value">{{ item.value }}<span class="ops-unit">{{ item.unit }}</span></div>
              <div class="ops-label">{{ item.label }}</div>
              <div class="ops-progress">
                <el-progress :percentage="item.percentage" :color="item.percentage >= 70 ? '#67c23a' : '#e6a23c'" :stroke-width="4" :show-text="false" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Event Logs -->
      <div class="card events-card">
        <div class="card-header">
          <span class="card-title">
            <el-icon><Document /></el-icon>
            Recent Event Logs
          </span>
        </div>
        <el-table :data="recentEvents" stripe size="small" style="width: 100%">
          <el-table-column prop="time" label="Time" align="center" />
          <el-table-column prop="operator" label="Operator" align="center" />
          <el-table-column prop="action" label="Action" align="center" />
          <el-table-column prop="target" label="Target" align="center" />
        </el-table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  Refresh, Monitor, AlarmClock, Lightning, Wallet, Coin, Location, Bell,
  TrendCharts, Cpu, DataAnalysis, Document, ArrowUp, ArrowDown, CaretTop,
  CaretBottom, ColdDrink, Sunny, Lock, Warning, Odometer, Connection,
  ChatDotRound, Timer, WarningFilled, CircleCheck, List
} from '@element-plus/icons-vue'

const router = useRouter()
// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading modules...')

const loadingMessages = [
  'Loading modules...',
  'Initializing dashboard...',
  'Connecting to data sources...',
  'Loading images...',
  'Rendering charts...',
  'Almost ready...'
]

// ==================== AI Decision Queue ====================
const decisionQueue = ref([])
const currentActiveDecision = ref(null)
let nextDecisionId = 1

const decisionTemplates = [
  {
    category: 'Energy',
    severity: 'critical',
    priority: 'P0',
    message: 'Shopping Mall energy consumption 22% above target. Immediate optimization needed.',
    impact: 'Estimated loss: 15k SGD/month if not addressed',
    actionText: 'Apply Optimization',
    action: 'optimize_hvac'
  },
  {
    category: 'Maintenance',
    severity: 'critical',
    priority: 'P0',
    message: 'Factory HVAC-03 compressor high temperature. Failure risk within 48 hours.',
    impact: 'Estimated downtime cost: 12k SGD/hour',
    actionText: 'Schedule Maintenance',
    action: 'schedule_maintenance'
  },
  {
    category: 'Revenue',
    severity: 'high',
    priority: 'P1',
    message: 'Parking occupancy at 78%, dynamic pricing opportunity detected.',
    impact: 'Potential revenue increase: 12%',
    actionText: 'Enable Pricing',
    action: 'dynamic_pricing'
  },
  {
    category: 'Maintenance',
    severity: 'high',
    priority: 'P1',
    message: 'Sensors network shows 15 devices with communication delay.',
    impact: 'Data accuracy affected in 3 zones',
    actionText: 'Update Firmware',
    action: 'firmware_update'
  },
  {
    category: 'Carbon',
    severity: 'medium',
    priority: 'P2',
    message: 'Carbon credit revenue +15.3% this month. Consider increasing renewable investment.',
    impact: 'Additional 8% ROI projected',
    actionText: 'View Analysis',
    action: 'view_roi'
  },
  {
    category: 'Maintenance',
    severity: 'medium',
    priority: 'P2',
    message: 'Lighting system in Parking B1 has 12% failure rate.',
    impact: 'Replacement cost: 8k SGD, savings: 3k SGD/month',
    actionText: 'Order Parts',
    action: 'order_parts'
  },
  {
    category: 'Maintenance',
    severity: 'low',
    priority: 'P3',
    message: 'UPS battery health below 80%. Preventive replacement recommended.',
    impact: 'Risk of failure in 60 days',
    actionText: 'Schedule Replacement',
    action: 'schedule_replacement'
  },
  {
    category: 'Energy',
    severity: 'low',
    priority: 'P3',
    message: 'Building lighting schedule can be optimized for off-hours.',
    impact: 'Estimated saving: 2k SGD/month',
    actionText: 'Optimize Schedule',
    action: 'optimize_lighting'
  }
]

const sortDecisionQueue = () => {
  const priorityOrder = { P0: 0, P1: 1, P2: 2, P3: 3 }
  decisionQueue.value.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority])
}

const updateActiveDecision = () => {
  currentActiveDecision.value = decisionQueue.value.length > 0 ? decisionQueue.value[0] : null
}

const addDecisionToQueue = (template) => {
  const newDecision = { id: nextDecisionId++, ...template, createdAt: new Date() }
  decisionQueue.value.push(newDecision)
  sortDecisionQueue()
  updateActiveDecision()
  ElMessage({ message: `New AI Decision: ${template.message.substring(0, 50)}...`, type: 'warning', duration: 5000 })
}

const executeDecision = async (decision) => {
  try {
    await ElMessageBox.confirm(`Execute: ${decision.message}\n\nImpact: ${decision.impact}`, 'AI Decision Execution', { confirmButtonText: 'Execute', cancelButtonText: 'Cancel', type: 'info' })

    switch(decision.action) {
      case 'optimize_hvac':
        ElMessage.success('HVAC optimization applied! Expected 15% energy reduction')
        kpiList.value[2].value = '148.2'
        kpiList.value[2].trend = -5.8
        break
      case 'schedule_maintenance':
        ElMessage.success('Maintenance scheduled for tomorrow 09:00')
        break
      case 'dynamic_pricing':
        ElMessage.success('Dynamic pricing enabled for parking')
        break
      case 'firmware_update':
        ElMessage.success('Firmware update initiated for 15 sensors')
        deviceHealthData.value[4].onlineRate = 95.8
        break
      case 'view_roi':
        ElMessage.info('Opening ROI analysis...')
        break
      case 'order_parts':
        ElMessage.success('Parts ordered. Estimated delivery: 3 days')
        break
      case 'schedule_replacement':
        ElMessage.success('UPS replacement scheduled for next month')
        break
      case 'optimize_lighting':
        ElMessage.success('Lighting schedule optimized')
        break
      default:
        ElMessage.success(`Decision executed: ${decision.actionText}`)
    }

    recentEvents.value.unshift({ time: new Date().toLocaleTimeString(), operator: 'AI System', action: 'Decision Executed', target: decision.message.substring(0, 50) })
    if (recentEvents.value.length > 10) recentEvents.value.pop()

    decisionQueue.value = decisionQueue.value.filter(d => d.id !== decision.id)
    updateActiveDecision()
  } catch {}
}

const dismissDecision = (decisionId) => {
  decisionQueue.value = decisionQueue.value.filter(d => d.id !== decisionId)
  updateActiveDecision()
  ElMessage.info('Decision dismissed')
}

let decisionInterval = null
const startDecisionSimulation = () => {
  // 初始化时只添加1条决策
  setTimeout(() => {
    addDecisionToQueue(decisionTemplates[1])
    // 初始化完成后开始循环调度
    scheduleNextDecision()
  }, 500)
}

// 添加一个获取随机间隔的函数（30秒到120秒之间）
const getRandomInterval = () => {
  return Math.floor(Math.random() * (120000 - 30000 + 1) + 30000)
}

// 需要让每次执行后重新设置间隔，所以改用递归 setTimeout 而不是 setInterval
let decisionTimeout = null

const scheduleNextDecision = () => {
  const interval = getRandomInterval()
  decisionTimeout = setTimeout(() => {
    if (Math.random() > 0.6) {
      const randomIndex = Math.floor(Math.random() * decisionTemplates.length)
      addDecisionToQueue({ ...decisionTemplates[randomIndex] })
    }
    scheduleNextDecision() // 继续调度下一次
  }, interval)
}
// 跳转到站点页面
const goToSite = (site) => {
  const routeMap = {
    'Factory': '/sites/Factory',
    'Building': '/sites/Building',
    'Airport': '/sites/Airport',
    'Shopping Mall': '/sites/Shopping',
    'Hospital': '/sites/Hospital',
    'Hotel': '/sites/Hotel'
  }
  const path = routeMap[site.name]
  if (path) {
    router.push(path)
  }
}


// ==================== KPI Data ====================
const kpiList = ref([
  { key: 'device', label: 'Total Devices / Online Rate', value: '1,284 / 96.8%', unit: '', icon: 'Monitor', bgColor: '#667eea', trend: 2.3 },
  { key: 'alarm', label: 'Active Alarms', value: '23', unit: '', icon: 'AlarmClock', bgColor: '#f59e0b', trend: -12.5 },
  { key: 'energy', label: 'Cumulative Energy', value: '156.8', unit: 'k kWh', icon: 'Lightning', bgColor: '#10b981', trend: -3.2 },
  { key: 'carbon', label: 'Estimated Carbon', value: '1,234', unit: 't CO₂', icon: 'Connection', bgColor: '#3b82f6', trend: -5.6 },
  { key: 'saving', label: 'Energy Savings Cost', value: '45.2', unit: 'k SGD', icon: 'Wallet', bgColor: '#8b5cf6', trend: 8.1 },
  { key: 'credit', label: 'Carbon Credit Revenue', value: '12.8', unit: 'k SGD', icon: 'Coin', bgColor: '#ec489a', trend: 15.3 }
])

// ==================== Site Health Data ====================
const siteHealthData = ref([
  { name: 'Factory', healthScore: 94, alarmCount: 3, energyIntensity: 12.4, statusColor: '#10b981', route: '/sites/Factory' },
  { name: 'Building', healthScore: 87, alarmCount: 7, energyIntensity: 18.2, statusColor: '#f59e0b', route: '/sites/Building' },
  { name: 'Airport', healthScore: 96, alarmCount: 2, energyIntensity: 15.6, statusColor: '#10b981', route: '/sites/Airport' },
  { name: 'Shopping Mall', healthScore: 82, alarmCount: 12, energyIntensity: 22.3, statusColor: '#ef4444', route: '/sites/Shopping' },
  { name: 'Hospital', healthScore: 91, alarmCount: 5, energyIntensity: 19.8, statusColor: '#10b981', route: '/sites/Hospital' },
  { name: 'Hotel', healthScore: 89, alarmCount: 4, energyIntensity: 16.4, statusColor: '#f59e0b', route: '/sites/Hotel' }
])

// ==================== Real-time Alarm Data ====================
const recentAlarms = ref([
  { id: 1, severity: 'critical', device: 'HVAC-03', message: 'Compressor high temperature shutdown', time: '2 mins ago' },
  { id: 2, severity: 'major', device: 'Lighting-Parking B1', message: 'Lamp failure rate exceeds threshold', time: '15 mins ago' },
  { id: 3, severity: 'major', device: 'Access Control-North Gate', message: 'Card reader offline', time: '32 mins ago' },
  { id: 4, severity: 'minor', device: 'Sensor-TH-08', message: 'Communication delay high', time: '1 hour ago' },
  { id: 5, severity: 'warning', device: 'Elevator-L1', message: 'Maintenance due soon', time: '2 hours ago' },
  { id: 6, severity: 'critical', device: 'Fire Alarm System', message: 'Smoke detector triggered in Zone 3', time: '3 hours ago' },
  { id: 7, severity: 'major', device: 'Chiller-02', message: 'Low refrigerant pressure detected', time: '4 hours ago' },
  { id: 8, severity: 'minor', device: 'Lighting-Office Area', message: 'Motion sensor calibration required', time: '5 hours ago' },
  { id: 9, severity: 'warning', device: 'UPS-Backup', message: 'Battery health below 75%', time: '6 hours ago' },
  { id: 10, severity: 'major', device: 'Ventilation-Fan-07', message: 'Abnormal vibration detected', time: '8 hours ago' }
])

// ==================== Energy Data ====================
const trendPeriod = ref('week')
const trendChartRef = ref(null)
let trendChart = null
const cumulativeCarbon = ref(1234.5)
const cleanEnergyRatio = ref(32.6)
const energyCompare = ref(-3.2)

// ==================== Device Health Data ====================
const deviceHealthData = ref([
  { type: 'HVAC', onlineRate: 94.2, faultCount: 8, trend: -2.1 },
  { type: 'Lighting', onlineRate: 97.5, faultCount: 4, trend: -1.3 },
  { type: 'Access Control', onlineRate: 98.1, faultCount: 3, trend: -0.8 },
  { type: 'Fire Safety', onlineRate: 99.2, faultCount: 1, trend: -0.2 },
  { type: 'Sensors', onlineRate: 91.3, faultCount: 15, trend: 3.5 },
  { type: 'Plumbing', onlineRate: 96.4, faultCount: 6, trend: -1.5 }
])

// ==================== Operational Efficiency Data ====================
const opsData = ref([
  { key: 'parking', label: 'Parking Occupancy', value: 78, unit: '%', percentage: 78 },
  { key: 'space', label: 'Space Utilization', value: 65, unit: '%', percentage: 65 },
  { key: 'visitor', label: 'Today\'s Visitors', value: 342, unit: '', percentage: 57 },
  { key: 'staff', label: 'Staff Saturation', value: 82, unit: '%', percentage: 82 }
])

// ==================== Recent Events ====================
const recentEvents = ref([
  { time: '10:23:15', operator: 'Zhang Ming', action: 'Device Control', target: 'Start HVAC-03 cooling mode' },
  { time: '10:15:42', operator: 'Li Fang', action: 'Work Order', target: 'Complete work order #WO-0042' },
  { time: '10:08:33', operator: 'Wang Qiang', action: 'Alarm Acknowledged', target: 'Acknowledge alarm #A-1023' },
  { time: '09:56:21', operator: 'Zhao Min', action: 'System Login', target: 'Login to system' },
  { time: '09:45:17', operator: 'Sun Wei', action: 'Report Export', target: 'Export monthly carbon report' },
  { time: '09:32:08', operator: 'Zhou Li', action: 'Parameter Change', target: 'Adjust energy saving strategy' }
])

// ==================== Helper Methods ====================
const getHealthColor = (score) => {
  if (score >= 90) return '#10b981'
  if (score >= 80) return '#f59e0b'
  return '#ef4444'
}

const getAlarmTagType = (severity) => {
  const map = { critical: 'danger', major: 'warning', minor: 'info', warning: 'warning' }
  return map[severity] || 'info'
}

const acknowledgeAlarm = (id) => {
  recentAlarms.value = recentAlarms.value.filter(a => a.id !== id)
  ElMessage.success(`Alarm acknowledged`)
}

const clearAllAlerts = () => {
  ElMessageBox.confirm('Clear all active alarms?', 'Confirm', { confirmButtonText: 'Clear', type: 'warning' })
      .then(() => {
        recentAlarms.value = []
        ElMessage.success('All alarms cleared')
      })
}

// ==================== Chart Methods ====================
const getTrendData = (period) => {
  if (period === 'week') {
    return {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      energy: [18500, 19200, 17800, 19500, 18800, 16500, 15800],
      carbon: [9250, 9600, 8900, 9750, 9400, 8250, 7900]
    }
  } else if (period === 'month') {
    return {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      energy: [125000, 132000, 128000, 135000],
      carbon: [62500, 66000, 64000, 67500]
    }
  } else {
    return {
      labels: ['Jan', 'Feb', 'Mar'],
      energy: [520000, 498000, 485000],
      carbon: [260000, 249000, 242500]
    }
  }
}

// 图表自适应调整函数
const resizeChart = () => {
  if (trendChart && trendChartRef.value) {
    // 使用 requestAnimationFrame 优化性能
    requestAnimationFrame(() => {
      trendChart.resize()
    })
  }
}

// 监听全屏变化
// 修改这部分代码
const handleFullscreenChange = () => {
  // 延迟执行，等待 DOM 完全渲染后重绘
  setTimeout(() => {
    if (trendChart) {
      trendChart.resize()
    }
  }, 100)
  // 再次延迟确保完全适配
  setTimeout(() => {
    if (trendChart) {
      trendChart.resize()
    }
  }, 300)
}
const initTrendChart = async () => {
  await nextTick()
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)
  const data = getTrendData('week')

  trendChart.setOption({
    tooltip: {trigger: 'axis', axisPointer: {type: 'shadow'}},
    legend: {show: false},
    grid: {left: '3%', right: '3%', top: '10%', bottom: '5%', containLabel: true},
    xAxis: {type: 'category', data: data.labels, axisLine: {lineStyle: {color: '#a0aec0'}}, axisLabel: {fontSize: 11}},
    yAxis: {
      type: 'value',
      name: 'kWh / kg CO₂',
      nameTextStyle: {fontSize: 11, color: '#a0aec0'},
      splitLine: {lineStyle: {color: '#e9ecef', type: 'dashed'}}
    },
    series: [
      {
        name: 'Energy', type: 'line', data: data.energy, smooth: true, symbol: 'circle', symbolSize: 6,
        lineStyle: {width: 3, color: '#f59e0b'},
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(245, 158, 11, 0.3)'}, {offset: 1, color: 'rgba(245, 158, 11, 0.02)'}
          ])
        },
        itemStyle: {color: '#f59e0b', borderColor: '#fff', borderWidth: 2}
      },
      {
        name: 'Carbon', type: 'line', data: data.carbon, smooth: true, symbol: 'diamond', symbolSize: 6,
        lineStyle: {width: 3, color: '#10b981'},
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {offset: 0, color: 'rgba(16, 185, 129, 0.3)'}, {offset: 1, color: 'rgba(16, 185, 129, 0.02)'}
          ])
        },
        itemStyle: {color: '#10b981', borderColor: '#fff', borderWidth: 2}
      }
    ]
  })

  // 监听窗口大小变化
  window.addEventListener('resize', resizeChart)
  // 监听全屏变化
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.addEventListener('mozfullscreenchange', handleFullscreenChange)
  document.addEventListener('MSFullscreenChange', handleFullscreenChange)
}

const updateTrendChart = () => {
  if (trendChart) {
    const data = getTrendData(trendPeriod.value)
    trendChart.setOption({xAxis: {data: data.labels}, series: [{data: data.energy}, {data: data.carbon}]})
  }
}

// ==================== Image Preloading ====================
const getAllImageUrls = () => ['https://aegisnx.com/wp-content/uploads/2026/05/favicon.ico']
const preloadImage = (url) => new Promise((resolve) => {
  const img = new Image();
  img.onload = () => resolve(url);
  img.onerror = () => resolve(url);
  img.src = url
})
const preloadAllImages = async () => {
  const urls = getAllImageUrls();
  if (urls.length) await Promise.all(urls.map(url => preloadImage(url)))
}

// ==================== Loading & Real-time Updates ====================
let progressInterval = null, messageInterval = null, alarmInterval = null

const startLoading = async () => {
  let messageIndex = 0
  messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
      if (loadingMessage.value === 'Loading images...') preloadAllImages().then(() => loadingProgress.value = 85)
    }
  }, 800)
  progressInterval = setInterval(() => {
    if (loadingProgress.value < 85) {
      loadingProgress.value += Math.random() * 8 + 3
      if (loadingProgress.value > 85) loadingProgress.value = 85
    } else if (loadingProgress.value >= 85 && loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 5 + 2
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 150)
  await preloadAllImages()
  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => initTrendChart())
    }, 400)
  }, 3000)
}

const startRealtimeUpdates = () => {
  alarmInterval = setInterval(() => {
    if (Math.random() > 0.7) {
      const newAlarm = {
        id: Date.now(),
        severity: ['critical', 'major', 'warning'][Math.floor(Math.random() * 3)],
        device: ['HVAC', 'Lighting', 'Sensors'][Math.floor(Math.random() * 3)] + '-' + Math.floor(Math.random() * 20),
        message: ['Device offline', 'Temperature anomaly', 'Communication failure'][Math.floor(Math.random() * 3)],
        time: 'Just now'
      }
      recentAlarms.value.unshift(newAlarm)
      if (recentAlarms.value.length > 10) recentAlarms.value.pop()
      kpiList.value[1].value = recentAlarms.value.length
    }
  }, 30000)
}

onMounted(() => {
  startLoading()
  startDecisionSimulation()
  startRealtimeUpdates()
})

onBeforeUnmount(() => {
  if (trendChart) {
    trendChart.dispose()
  }
  window.removeEventListener('resize', resizeChart)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
  document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
  document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
  document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
  if (progressInterval) clearInterval(progressInterval)
  if (messageInterval) clearInterval(messageInterval)
  if (decisionTimeout) clearTimeout(decisionTimeout)     // 新增这行
  if (alarmInterval) clearInterval(alarmInterval)
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100%;
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
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
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

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.3;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
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
  0% {
    background-position: 0% 0%;
  }
  100% {
    background-position: 200% 0%;
  }
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
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ==================== Decision Banner ==================== */
.decision-banner {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 16px;
  padding: 16px 24px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-left: 4px solid #3b82f6;
}

.decision-banner.critical {
  border-left-color: #f56c6c;
}

.decision-banner.high {
  border-left-color: #f59e0b;
}

.decision-banner.medium {
  border-left-color: #409eff;
}

.decision-banner.low {
  border-left-color: #909399;
}

.decision-banner.idle {
  border-left-color: #67c23a;
}

.banner-icon {
  width: 48px;
  height: 48px;
  background: rgba(59, 130, 246, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.banner-content {
  flex: 1;
}

.banner-title {
  font-size: 14px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 6px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.priority-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
}

.priority-badge.critical {
  background: #fef2f2;
  color: #f56c6c;
}

.priority-badge.high {
  background: #fffbeb;
  color: #f59e0b;
}

.priority-badge.medium {
  background: #ecf5ff;
  color: #409eff;
}

.priority-badge.low {
  background: #f4f4f5;
  color: #909399;
}

.banner-message {
  font-size: 15px;
  font-weight: 500;
  color: #e2e8f0;
  margin-bottom: 6px;
}

.banner-impact {
  font-size: 12px;
  color: #f59e0b;
}

.banner-actions {
  display: flex;
  gap: 12px;
}

/* ==================== KPI Cards ==================== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.kpi-content {
  flex: 1;
}

.kpi-label {
  font-size: 13px;
  color: #6c757d;
  margin-bottom: 6px;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a2c3e;
  line-height: 1.2;
}

.kpi-unit {
  font-size: 13px;
  font-weight: 400;
  color: #6c757d;
  margin-left: 4px;
}

.kpi-trend {
  font-size: 12px;
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 2px;
}

.kpi-trend.trend-up {
  color: #f56c6c;
}

.kpi-trend.trend-down {
  color: #67c23a;
}

/* ==================== Two Columns ==================== */
.two-columns {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a2c3e;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ==================== Site Health ==================== */
.site-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.site-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.site-item:hover {
  background: #f1f5f9;
  transform: translateX(4px);
}

.site-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.site-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 14px;
}

.site-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.site-metrics {
  display: flex;
  gap: 12px;
  font-size: 12px;
}

.metric-alarm {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #f59e0b;
}

.metric-alarm.high {
  color: #f56c6c;
}

.metric-energy {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #6c757d;
}

.site-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.site-progress .el-progress {
  flex: 1;
}

.site-score {
  font-size: 12px;
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}

/* ==================== Alarm List ==================== */
.alarm-list {
  max-height: 460px;
  overflow-y: auto;
  scrollbar-width: none;
}

.alarm-list::-webkit-scrollbar {
  width: 0;
  display: none;
}

.alarm-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.alarm-item.critical .alarm-device {
  color: #f56c6c;
}

.alarm-detail {
  flex: 1;
  margin-left: 12px;
}

.alarm-device {
  font-size: 13px;
  font-weight: 500;
  color: #1a2c3e;
}

.alarm-time {
  font-size: 11px;
  color: #a0aec0;
  margin-top: 4px;
}

/* ==================== Chart ==================== */
.chart-card {
  margin-bottom: 20px;
}

.chart-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-bottom: 16px;
}

.chart-container {
  height: 300px;
  width: 100%;
  margin-top: 8px;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.stat-item {
  text-align: center;
  padding: 8px 16px;
  border-radius: 8px;
}

.stat-label {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1a2c3e;
}

.stat-unit {
  font-size: 12px;
  font-weight: 400;
  color: #6c757d;
}

.text-warning {
  color: #f59e0b;
}

.text-success {
  color: #67c23a;
}

/* ==================== Tables ==================== */
.online-rate-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.rate-value {
  font-size: 12px;
}

.fault-high {
  color: #f56c6c;
  font-weight: 600;
}

.trend-up-text {
  color: #f56c6c;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.trend-down-text {
  color: #67c23a;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

/* 表格列平均分配 */
.el-table .el-table__cell {
  text-align: center !important;
}

.el-table .cell {
  text-align: center !important;
}

.ops-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.ops-item {
  text-align: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.ops-value {
  font-size: 32px;
  font-weight: 700;
  color: #1a2c3e;
}

.ops-unit {
  font-size: 13px;
  font-weight: 400;
  color: #6c757d;
}

.ops-label {
  font-size: 13px;
  color: #6c757d;
  margin: 6px 0 10px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #a0aec0;
}

/* ==================== Responsive ==================== */
@media (max-width: 1024px) {
  .two-columns {
    grid-template-columns: 1fr;
  }

  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 12px;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .decision-banner {
    flex-direction: column;
    text-align: center;
  }

  .banner-actions {
    justify-content: center;
  }

  .ops-grid {
    grid-template-columns: 1fr;
  }
}
</style>