<template>
  <div v-if="isPageLoaded" class="anchoring-page">
    <div class="page-container">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>Blockchain Anchoring</h1>
          <p>Immutable data anchoring · Audit trail · Blockchain verification</p>
        </div>
        <div class="header-actions">
          <el-dropdown @command="handleExportCommand" trigger="click">
            <el-button type="primary" size="small" :loading="exporting">
              <el-icon><Download /></el-icon> Export
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="pdf">Export as PDF Report</el-dropdown-item>
                <el-dropdown-item command="csv">Export as CSV</el-dropdown-item>
                <el-dropdown-item command="excel">Export as Excel</el-dropdown-item>
                <el-dropdown-item command="json">Export as JSON</el-dropdown-item>
                <el-dropdown-item divided command="full">Export Full Audit Report</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button type="success" size="small" plain @click="refreshData" :loading="refreshing">
            <el-icon><Refresh /></el-icon> Refresh
          </el-button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue"><el-icon><Document /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ formatNumber(stats.totalAnchors) }}</div>
            <div class="stat-label">Total Anchors</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green"><el-icon><Plus /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.todayNew }}</div>
            <div class="stat-label">Today Added</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange"><el-icon><DataAnalysis /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.chainSize }} MB</div>
            <div class="stat-label">Chain Size</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple"><el-icon><Timer /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgLatency }} s</div>
            <div class="stat-label">Avg Latency</div>
          </div>
        </div>
      </div>

      <!-- Chart and Distribution -->
      <div class="two-columns">
        <div class="chart-card">
          <div class="card-header">
            <span><el-icon><PieChart /></el-icon> Data Type Distribution</span>
          </div>
          <div ref="distributionChartRef" class="chart-box" style="height: 280px;"></div>
        </div>
        <div class="chart-card">
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Anchor Trend (Last 7 Days)</span>
          </div>
          <div ref="trendChartRef" class="chart-box" style="height: 280px;"></div>
        </div>
      </div>

      <!-- Anchor Strategy Configuration -->
      <div class="section-title">
        <el-icon><Setting /></el-icon>
        <span>Anchor Strategy Configuration</span>
        <el-button size="small" type="primary" plain @click="editStrategy">
          <el-icon><Edit /></el-icon> Edit Strategy
        </el-button>
      </div>

      <div class="strategy-config">
        <div class="strategy-grid">
          <div v-for="type in dataTypes" :key="type.name" class="strategy-item">
            <div class="strategy-icon" :style="{ background: type.color }">
              <el-icon :size="20"><component :is="type.icon" /></el-icon>
            </div>
            <div class="strategy-info">
              <div class="strategy-name">{{ type.name }}</div>
              <div class="strategy-status">
                <el-switch v-model="type.enabled" size="small" />
                <span class="strategy-trigger">{{ type.trigger }}</span>
              </div>
            </div>
            <div class="strategy-chain">
              <el-tag size="small" :type="type.chain === 'Mainnet' ? 'danger' : 'info'">{{ type.chain }}</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Queue -->
      <div class="section-title">
        <el-icon><List /></el-icon>
        <span>Pending Anchor Queue</span>
        <el-tag v-if="pendingQueue.length > 0" type="warning" size="small">{{ pendingQueue.length }} pending</el-tag>
      </div>

      <el-table :data="pendingQueue" stripe size="small" style="width: 100%">
        <el-table-column prop="dataId" label="Data ID" min-width="180" />
        <el-table-column prop="dataType" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="Time" width="160" />
        <el-table-column prop="hash" label="Hash" min-width="220">
          <template #default="{ row }">
            <span class="mono">{{ shortenHash(row.hash) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="100" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="retryAnchor(row)">Anchor Now</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Anchor Records -->
      <div class="section-title">
        <el-icon><Stamp /></el-icon>
        <span>Anchor Records</span>
        <div class="title-controls">
          <el-date-picker v-model="dateRange" type="daterange" range-separator="-" start-placeholder="Start" end-placeholder="End" size="small" style="width: 240px" />
          <el-input v-model="searchKeyword" placeholder="Search Data ID or Hash" size="small" clearable style="width: 200px" :prefix-icon="Search" />
          <el-select v-model="filterType" placeholder="Filter by Type" size="small" clearable style="width: 130px">
            <el-option v-for="t in dataTypeOptions" :key="t" :label="t" :value="t" />
          </el-select>
          <el-select v-model="filterStatus" placeholder="Status" size="small" clearable style="width: 100px">
            <el-option label="Verified" value="verified" />
            <el-option label="Pending" value="pending" />
            <el-option label="Failed" value="failed" />
          </el-select>
        </div>
      </div>

      <el-table :data="paginatedRecords" stripe size="small" style="width: 100%">
        <el-table-column prop="dataId" label="Data ID" min-width="180" show-overflow-tooltip />
        <el-table-column prop="dataType" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dataHash" label="Data Hash" min-width="220">
          <template #default="{ row }">
            <span class="mono">{{ shortenHash(row.dataHash) }}</span>
            <el-icon class="copy-icon" @click="copyText(row.dataHash)"><CopyDocument /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="blockNumber" label="Block" width="100" />
        <el-table-column prop="txHash" label="Tx Hash" min-width="200">
          <template #default="{ row }">
            <span class="mono tx-link" @click="openExplorer(row.txHash)">{{ shortenHash(row.txHash) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="anchorTime" label="Anchor Time" width="160" />
        <el-table-column prop="status" label="Status" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'verified' ? 'success' : row.status === 'pending' ? 'warning' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="80" align="center">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="verifyRecord(row)">Verify</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]" :total="filteredAnchorRecords.length" layout="total, sizes, prev, pager, next" small background />
      </div>

      <!-- Verification Tool -->
      <div class="section-title">
        <el-icon><Search /></el-icon>
        <span>Verification Tool</span>
      </div>

      <div class="verification-tool">
        <div class="verify-input">
          <el-radio-group v-model="verifyMode" size="small">
            <el-radio label="dataId">By Data ID</el-radio>
            <el-radio label="rawData">By Raw Data</el-radio>
          </el-radio-group>
          <el-input v-model="verifyInput" :placeholder="verifyMode === 'dataId' ? 'Enter Data ID to verify' : 'Enter raw data content'" style="flex: 1" clearable />
          <el-button type="primary" @click="verifyData" :loading="verifying">Verify</el-button>
        </div>

        <div v-if="verifyResult" class="verify-result-layout">
          <!-- 左侧：详细信息 -->
          <div class="verify-result-left">
            <div class="result-details">
              <div class="detail-row"><span class="label">Data ID:</span><span class="mono">{{ verifyResult.dataId || verifyInput }}</span></div>
              <div class="detail-row"><span class="label">Chain Hash:</span><span class="mono">{{ shortenHash(verifyResult.chainHash) }}</span></div>
              <div class="detail-row"><span class="label">Computed Hash:</span><span class="mono">{{ shortenHash(verifyResult.computedHash) }}</span></div>
              <div class="detail-row"><span class="label">Block Number:</span>{{ verifyResult.blockNumber }}</div>
              <div class="detail-row"><span class="label">Timestamp:</span>{{ verifyResult.timestamp }}</div>
              <div class="detail-row"><span class="label">Confirmations:</span>{{ verifyResult.confirmations }}</div>
            </div>
          </div>
          <!-- 右侧：结果徽章 -->
          <div class="verify-result-right" :class="verifyResult.isValid ? 'success' : 'error'">
            <div class="result-badge">
              <el-icon :size="48">{{ verifyResult.isValid ? 'SuccessFilled' : 'CircleCloseFilled' }}</el-icon>
            </div>
            <div class="result-status-text">{{ verifyResult.isValid ? 'VERIFIED' : 'TAMPERED' }}</div>
            <div class="result-sub-text">{{ verifyResult.isValid ? 'Data integrity confirmed' : 'Data has been modified!' }}</div>
            <el-button size="small" :type="verifyResult.isValid ? 'success' : 'danger'" plain @click="exportVerificationReport" style="margin-top: 12px">
              Export Report
            </el-button>
          </div>
        </div>
      </div>

      <!-- Anchor Report Summary -->
      <div class="section-title">
        <el-icon><Document /></el-icon>
        <span>Anchor Report Summary</span>
        <el-button size="small" type="primary" plain @click="generateFullReport">
          <el-icon><DataLine /></el-icon> Generate Full Report
        </el-button>
      </div>

      <div class="report-summary">
        <div class="report-item">
          <div class="report-label">Success Rate</div>
          <div class="report-value" :class="reportStats.successRate >= 99 ? 'success' : 'warning'">{{ reportStats.successRate }}%</div>
        </div>
        <div class="report-item">
          <div class="report-label">Avg Latency</div>
          <div class="report-value">{{ reportStats.avgLatency }} s</div>
        </div>
        <div class="report-item">
          <div class="report-label">Total Anchors</div>
          <div class="report-value">{{ formatNumber(reportStats.totalAnchors) }}</div>
        </div>
        <div class="report-item">
          <div class="report-label">Failed Anchors</div>
          <div class="report-value" :class="reportStats.failedAnchors > 0 ? 'danger' : 'success'">{{ reportStats.failedAnchors }}</div>
        </div>
        <div class="report-item">
          <div class="report-label">This Week</div>
          <div class="report-value">{{ reportStats.weeklyAnchors }}</div>
        </div>
        <div class="report-item">
          <div class="report-label">This Month</div>
          <div class="report-value">{{ reportStats.monthlyAnchors }}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Loading Screen -->
  <div v-else class="loading-container">
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
        <div class="loading-tip">Blockchain Anchoring System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Document, Plus, DataAnalysis, Timer, PieChart, TrendCharts,
  Setting, Edit, List, Stamp, Search, CopyDocument, Download,
  SuccessFilled, CircleCloseFilled, DataLine, ArrowDown
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing assets...')
const refreshing = ref(false)
const exporting = ref(false)

const loadingMessages = [
  'Preparing assets...',
  'Loading blockchain data...',
  'Initializing modules...',
  'Connecting to chain...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Statistics ====================
const stats = ref({
  totalAnchors: 12480,
  todayNew: 127,
  chainSize: 486.5,
  avgLatency: 2.8
})

// ==================== Data Types Configuration ====================
const dataTypes = ref([
  { name: 'Alarm Logs', icon: 'Bell', color: '#ef4444', enabled: true, trigger: 'Real-time', chain: 'Mainnet', count: 3842 },
  { name: 'Energy Records', icon: 'Lightning', color: '#f59e0b', enabled: true, trigger: 'Batch (5min)', chain: 'Sidechain', count: 5670 },
  { name: 'Device Operations', icon: 'Cpu', color: '#3b82f6', enabled: true, trigger: 'Real-time', chain: 'Mainnet', count: 8924 },
  { name: 'Contract Executions', icon: 'Document', color: '#8b5cf6', enabled: true, trigger: 'Real-time', chain: 'Mainnet', count: 2340 }
])

const dataTypeOptions = ['Alarm Logs', 'Energy Records', 'Device Operations', 'Contract Executions']

// ==================== Pending Queue ====================
const pendingQueue = ref([
  { dataId: 'ALM-20260521-001', dataType: 'Alarm Logs', timestamp: '2026-05-21 09:32:15', hash: '0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b' },
  { dataId: 'ENG-20260521-088', dataType: 'Energy Records', timestamp: '2026-05-21 09:28:42', hash: '0x8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7' },
  { dataId: 'DEV-20260521-456', dataType: 'Device Operations', timestamp: '2026-05-21 09:15:23', hash: '0x9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8' }
])

// ==================== Generate Realistic Anchor Records ====================
const generateAnchorRecords = () => {
  const records = []
  const types = ['Alarm Logs', 'Energy Records', 'Device Operations', 'Contract Executions']
  const dataIdPrefix = {
    'Alarm Logs': 'ALM',
    'Energy Records': 'ENG',
    'Device Operations': 'DEV',
    'Contract Executions': 'CTR'
  }

  for (let i = 1; i <= 850; i++) {
    const type = types[Math.floor(Math.random() * types.length)]
    const date = new Date()
    date.setDate(date.getDate() - Math.floor(Math.random() * 30))
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hour = String(Math.floor(Math.random() * 24)).padStart(2, '0')
    const minute = String(Math.floor(Math.random() * 60)).padStart(2, '0')
    const second = String(Math.floor(Math.random() * 60)).padStart(2, '0')

    const randomId = String(Math.floor(Math.random() * 9999)).padStart(4, '0')
    const dataId = `${dataIdPrefix[type]}-${year}${month}${day}-${randomId}`

    const hashChars = '0123456789abcdef'
    let hash = '0x'
    for (let j = 0; j < 64; j++) {
      hash += hashChars[Math.floor(Math.random() * 16)]
    }

    let txHash = '0x'
    for (let j = 0; j < 64; j++) {
      txHash += hashChars[Math.floor(Math.random() * 16)]
    }

    const status = Math.random() > 0.05 ? (Math.random() > 0.02 ? 'verified' : 'pending') : 'failed'

    records.push({
      id: i,
      dataId,
      dataType: type,
      dataHash: hash,
      blockNumber: 12400 + Math.floor(Math.random() * 500),
      txHash,
      anchorTime: `${year}-${month}-${day} ${hour}:${minute}:${second}`,
      status
    })
  }

  records.sort((a, b) => b.anchorTime.localeCompare(a.anchorTime))
  return records
}

const anchorRecords = ref(generateAnchorRecords())

// ==================== Report Stats ====================
const reportStats = ref({
  successRate: 99.2,
  avgLatency: 2.8,
  totalAnchors: 12480,
  failedAnchors: 98,
  weeklyAnchors: 843,
  monthlyAnchors: 3560
})

// ==================== Filter & Search ====================
const searchKeyword = ref('')
const filterType = ref('')
const filterStatus = ref('')
const dateRange = ref<[Date, Date] | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)

const filteredAnchorRecords = computed(() => {
  let result = anchorRecords.value

  if (filterType.value) {
    result = result.filter(r => r.dataType === filterType.value)
  }
  if (filterStatus.value) {
    result = result.filter(r => r.status === filterStatus.value)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(r => r.dataId.toLowerCase().includes(keyword) || r.dataHash.toLowerCase().includes(keyword))
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const start = dateRange.value[0].toISOString().slice(0, 10)
    const end = dateRange.value[1].toISOString().slice(0, 10)
    result = result.filter(r => {
      const recordDate = r.anchorTime.slice(0, 10)
      return recordDate >= start && recordDate <= end
    })
  }

  return result
})

const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAnchorRecords.value.slice(start, end)
})

// ==================== Verification Tool ====================
const verifyMode = ref('dataId')
const verifyInput = ref('')
const verifying = ref(false)
const verifyResult = ref<any>(null)

// ==================== Chart ====================
const distributionChartRef = ref(null)
const trendChartRef = ref(null)
let distributionChart: any = null
let trendChart: any = null

const initCharts = () => {
  if (distributionChartRef.value) {
    distributionChart = echarts.init(distributionChartRef.value)
    distributionChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { orient: 'vertical', left: 'left', textStyle: { color: '#64748b' } },
      series: [{
        type: 'pie',
        radius: '55%',
        data: dataTypes.value.map(t => ({ name: t.name, value: t.count, itemStyle: { color: t.color } })),
        label: { show: true, formatter: '{b}: {d}%', color: '#475569' },
        emphasis: { scale: true, label: { show: true } }
      }]
    })
  }

  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'axis' },
      grid: { left: '8%', right: '5%', bottom: '5%', top: '5%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['05/15', '05/16', '05/17', '05/18', '05/19', '05/20', '05/21'],
        axisLabel: { color: '#64748b' },
        axisLine: { lineStyle: { color: '#e9ecef' } }
      },
      yAxis: {
        type: 'value',
        name: 'Anchors',
        nameTextStyle: { color: '#64748b' },
        axisLabel: { color: '#64748b' },
        splitLine: { lineStyle: { color: '#e9ecef', type: 'dashed' } }
      },
      series: [{
        data: [145, 178, 192, 210, 188, 234, 195],
        type: 'line',
        smooth: true,
        name: 'Anchors',
        lineStyle: { color: '#409eff', width: 3 },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#409eff40' },
            { offset: 1, color: '#409eff05' }
          ]) },
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#409eff', borderColor: '#ffffff', borderWidth: 2 },
        label: { show: true, position: 'top', color: '#409eff', fontSize: 11 }
      }]
    })
  }
}

// ==================== Helper Functions ====================
const formatNumber = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  return num.toLocaleString()
}

const shortenHash = (hash: string) => {
  if (!hash) return ''
  if (hash.length <= 20) return hash
  return `${hash.slice(0, 12)}...${hash.slice(-8)}`
}

const copyText = (text: string) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('Copied to clipboard')
}

const openExplorer = (txHash: string) => {
  window.open(`https://etherscan.io/tx/${txHash}`, '_blank')
}

const getDataTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Alarm Logs': 'danger',
    'Energy Records': 'warning',
    'Device Operations': 'primary',
    'Contract Executions': 'success'
  }
  return map[type] || 'info'
}

// ==================== Export Functions ====================
const exportVerificationReport = () => {
  ElMessage.success('Verification report exported as PDF')
}

const generateFullReport = () => {
  ElMessage.success('Full report generation started')
}

const handleExportCommand = async (command: string) => {
  exporting.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  const fileName = `anchor_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}`

  switch (command) {
    case 'pdf':
      ElMessage.success(`PDF report "${fileName}.pdf" exported successfully`)
      break
    case 'csv':
      exportToCSV()
      break
    case 'excel':
      ElMessage.success(`Excel file "${fileName}.xlsx" exported successfully`)
      break
    case 'json':
      exportToJSON()
      break
    case 'full':
      exportFullAuditReport()
      break
  }
  exporting.value = false
}

const exportToCSV = () => {
  const headers = ['Data ID', 'Data Type', 'Data Hash', 'Block Number', 'Tx Hash', 'Anchor Time', 'Status']
  const rows = filteredAnchorRecords.value.map(r => [
    r.dataId, r.dataType, r.dataHash, r.blockNumber, r.txHash, r.anchorTime, r.status
  ])

  const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n')
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.href = url
  link.setAttribute('download', `anchor_records_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success('CSV file exported successfully')
}

const exportToJSON = () => {
  const data = {
    exportTime: new Date().toISOString(),
    totalRecords: filteredAnchorRecords.value.length,
    stats: stats.value,
    reportStats: reportStats.value,
    records: filteredAnchorRecords.value
  }
  const jsonStr = JSON.stringify(data, null, 2)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.href = url
  link.setAttribute('download', `anchor_data_${new Date().toISOString().slice(0, 10)}.json`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  ElMessage.success('JSON file exported successfully')
}

const exportFullAuditReport = () => {
  ElMessage.success('Full audit report generated and ready for download')
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  anchorRecords.value = generateAnchorRecords()
  ElMessage.success('Data refreshed')
  refreshing.value = false
}

const editStrategy = () => {
  ElMessage.info('Strategy configuration dialog would open here')
}

const retryAnchor = (row: any) => {
  const index = pendingQueue.value.findIndex(p => p.dataId === row.dataId)
  if (index !== -1) pendingQueue.value.splice(index, 1)
  ElMessage.success(`Retrying anchor for ${row.dataId}`)
}

const verifyRecord = (row: any) => {
  verifyMode.value = 'dataId'
  verifyInput.value = row.dataId
  verifyData()
}

const verifyData = async () => {
  if (!verifyInput.value) {
    ElMessage.warning('Please enter Data ID or raw data')
    return
  }
  verifying.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  const isValid = Math.random() > 0.05
  const foundRecord = anchorRecords.value.find(r => r.dataId === verifyInput.value)

  verifyResult.value = {
    isValid,
    dataId: verifyInput.value,
    chainHash: foundRecord?.dataHash || '0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b',
    computedHash: isValid ? (foundRecord?.dataHash || '0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b') : '0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b',
    blockNumber: foundRecord?.blockNumber || 12456,
    timestamp: foundRecord?.anchorTime || '2026-05-21 09:32:20 UTC+8',
    confirmations: 12456 - 12300
  }
  verifying.value = false
}

// ==================== Watch for pagination reset ====================
watch([filterType, filterStatus, searchKeyword, dateRange], () => {
  currentPage.value = 1
})

// ==================== Loading ====================
const startLoading = () => {
  let progress = 0
  let msgIndex = 0

  const msgInterval = setInterval(() => {
    if (msgIndex < loadingMessages.length - 1) {
      msgIndex++
      loadingMessage.value = loadingMessages[msgIndex]
    }
  }, 800)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 10
      loadingProgress.value = Math.min(progress, 90)
      if (progress > 80 && loadingMessage.value !== loadingMessages[5]) loadingMessage.value = loadingMessages[5]
      else if (progress > 60 && loadingMessage.value !== loadingMessages[4]) loadingMessage.value = loadingMessages[4]
      else if (progress > 40 && loadingMessage.value !== loadingMessages[3]) loadingMessage.value = loadingMessages[3]
      else if (progress > 20 && loadingMessage.value !== loadingMessages[2]) loadingMessage.value = loadingMessages[2]
      else if (progress > 10 && loadingMessage.value !== loadingMessages[1]) loadingMessage.value = loadingMessages[1]
    }
  }, 100)

  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progressInterval)
    loadingMessage.value = 'Ready!'
    loadingProgress.value = 100
    setTimeout(() => {
      isPageLoaded.value = true
      nextTick(() => {
        setTimeout(initCharts, 200)
      })
    }, 500)
  }, 2500)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
.anchoring-page {
  background: #f5f7fa;
  min-height: 100%;
  padding: 24px;
}

.page-container {
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a2c3e;
  margin: 0;
}

.page-header p {
  color: #6c757d;
  margin: 4px 0 0;
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.stat-icon.blue { background: #e3f2fd; color: #2196f3; }
.stat-icon.green { background: #e8f5e9; color: #4caf50; }
.stat-icon.orange { background: #fff3e0; color: #ff9800; }
.stat-icon.purple { background: #f3e5f5; color: #9c27b0; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 28px; font-weight: 700; color: #1a2c3e; }
.stat-label { font-size: 13px; color: #6c757d; }

.two-columns {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.card-header {
  font-size: 16px;
  font-weight: 600;
  color: #1a2c3e;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-box { width: 100%; }

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #1a2c3e;
  margin: 28px 0 16px 0;
}

.title-controls {
  margin-left: auto;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.strategy-config {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.strategy-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.strategy-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.2s;
}

.strategy-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.strategy-info { flex: 1; }
.strategy-name { font-size: 14px; font-weight: 600; color: #1a2c3e; }
.strategy-status { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
.strategy-trigger { font-size: 11px; color: #6c757d; }

/* Verification Tool - New Layout */
.verification-tool {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.verify-input {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.verify-result-layout {
  margin-top: 20px;
  display: flex;
  gap: 24px;
  border-radius: 16px;
  overflow: hidden;
}

.verify-result-left {
  flex: 2;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  font-size: 13px;
  line-height: 1.5;
}

.detail-row .label {
  width: 110px;
  color: #6c757d;
  flex-shrink: 0;
}

.detail-row .mono {
  font-family: monospace;
  font-size: 12px;
  color: #495057;
  word-break: break-all;
}

.verify-result-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px;
  border-radius: 12px;
  text-align: center;
}

.verify-result-right.success {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  border: 1px solid #a5d6a7;
}

.verify-result-right.error {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  border: 1px solid #ef9a9a;
}

.result-badge {
  margin-bottom: 12px;
}

.verify-result-right.success .result-badge {
  color: #4caf50;
}

.verify-result-right.error .result-badge {
  color: #f44336;
}

.result-status-text {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 8px;
}

.verify-result-right.success .result-status-text {
  color: #2e7d32;
}

.verify-result-right.error .result-status-text {
  color: #c62828;
}

.result-sub-text {
  font-size: 12px;
  color: #6c757d;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.report-item { text-align: center; }
.report-label { font-size: 12px; color: #6c757d; margin-bottom: 4px; }
.report-value { font-size: 24px; font-weight: 700; }
.report-value.success { color: #4caf50; }
.report-value.warning { color: #ff9800; }
.report-value.danger { color: #f44336; }

.mono { font-family: monospace; font-size: 12px; }
.tx-link { color: #409eff; cursor: pointer; }
.tx-link:hover { text-decoration: underline; }
.copy-icon { margin-left: 6px; cursor: pointer; opacity: 0.6; }
.copy-icon:hover { opacity: 1; }

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

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
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
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
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .two-columns { grid-template-columns: 1fr; }
  .strategy-grid { grid-template-columns: repeat(2, 1fr); }
  .report-summary { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 768px) {
  .anchoring-page { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .stats-grid { grid-template-columns: 1fr; }
  .strategy-grid { grid-template-columns: 1fr; }
  .verify-input { flex-direction: column; align-items: stretch; }
  .verify-result-layout { flex-direction: column; }
  .title-controls { margin-left: 0; width: 100%; flex-wrap: wrap; }
  .report-summary { grid-template-columns: repeat(2, 1fr); }
}

:deep(.el-table) {
  --el-table-bg-color: #ffffff;
  --el-table-tr-bg-color: #ffffff;
  --el-table-header-bg-color: #f8f9fa;
}
:deep(.el-table th) {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #1a2c3e;
}
</style>