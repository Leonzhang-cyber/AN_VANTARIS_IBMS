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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Audit Trail</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="audit-trail-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Audit Trail</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Audit Trail</h1>
        <p class="description">Complete audit log of all user activities, decision changes, and system events with tamper-proof records</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Audit Log
        </el-button>
        <el-button type="primary" @click="handleVerifyIntegrity">
          <el-icon><Checked /></el-icon>
          Verify Integrity
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Activity Overview Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="16">
        <el-card class="activity-chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Activity Timeline (Last 30 Days)</span>
              <el-radio-group v-model="chartPeriod" size="small">
                <el-radio-button value="daily">Daily</el-radio-button>
                <el-radio-button value="weekly">Weekly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="activityChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="action-distribution-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Actions by Type</span>
            </div>
          </template>
          <div ref="actionChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Blockchain Verification Status -->
    <el-card class="blockchain-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Blockchain Verification Status</span>
          <el-tag type="success" size="default">Verified on Chain</el-tag>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="verification-item">
            <div class="verification-label">Last Verified</div>
            <div class="verification-value">2024-01-20 15:30:00</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="verification-item">
            <div class="verification-label">Blockchain Height</div>
            <div class="verification-value">8,745,231</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="verification-item">
            <div class="verification-label">Total Records</div>
            <div class="verification-value">12,456</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="verification-item">
            <div class="verification-label">Integrity Status</div>
            <div class="verification-value" style="color: #67c23a">✓ Verified</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by user, action, or description"
              prefix-icon="Search"
              clearable
              style="width: 250px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.actionType" placeholder="Action Type" clearable style="width: 150px">
            <el-option label="Create" value="Create" />
            <el-option label="Update" value="Update" />
            <el-option label="Delete" value="Delete" />
            <el-option label="Approve" value="Approve" />
            <el-option label="Reject" value="Reject" />
            <el-option label="View" value="View" />
            <el-option label="Export" value="Export" />
            <el-option label="Login" value="Login" />
          </el-select>
          <el-select v-model="filters.user" placeholder="User" clearable style="width: 150px">
            <el-option label="John Smith" value="John Smith" />
            <el-option label="Sarah Chen" value="Sarah Chen" />
            <el-option label="David Wang" value="David Wang" />
            <el-option label="Lisa Zhang" value="Lisa Zhang" />
            <el-option label="Tom Harris" value="Tom Harris" />
          </el-select>
          <el-select v-model="filters.entityType" placeholder="Entity Type" clearable style="width: 150px">
            <el-option label="Decision" value="Decision" />
            <el-option label="Approval Rule" value="Approval Rule" />
            <el-option label="Document" value="Document" />
            <el-option label="User" value="User" />
            <el-option label="Report" value="Report" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="datetimerange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 360px"
          />
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Audit Log ({{ filteredAuditLogs.length }} records)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchAuditLogs" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedAuditLogs" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="user" label="User" width="130" />
        <el-table-column prop="action" label="Action" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionTag(row.action)" size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entityType" label="Entity Type" width="130">
          <template #default="{ row }">
            <el-tag :type="getEntityTag(row.entityType)" size="small">{{ row.entityType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entityId" label="Entity ID" width="120" />
        <el-table-column prop="entityName" label="Entity Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP Address" width="130" />
        <el-table-column label="Hash" width="80">
          <template #default="{ row }">
            <el-popover placement="top" :width="300" trigger="hover">
              <template #reference>
                <el-tag type="info" size="small" style="cursor: pointer">View Hash</el-tag>
              </template>
              <div class="hash-value">{{ row.blockchainHash }}</div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column label="Details" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">View</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredAuditLogs.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Audit Details Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Audit Details - Record #${currentAudit?.id}`" width="700px" destroy-on-close>
      <div class="audit-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Timestamp">{{ currentAudit?.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="User">{{ currentAudit?.user }}</el-descriptions-item>
          <el-descriptions-item label="Action">
            <el-tag :type="getActionTag(currentAudit?.action || '')" size="small">{{ currentAudit?.action }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="IP Address">{{ currentAudit?.ipAddress }}</el-descriptions-item>
          <el-descriptions-item label="Entity Type">
            <el-tag :type="getEntityTag(currentAudit?.entityType || '')" size="small">{{ currentAudit?.entityType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Entity ID">{{ currentAudit?.entityId }}</el-descriptions-item>
          <el-descriptions-item label="Entity Name" :span="2">{{ currentAudit?.entityName }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentAudit?.description }}</el-descriptions-item>
          <el-descriptions-item label="Blockchain Hash" :span="2">
            <span class="hash-value">{{ currentAudit?.blockchainHash }}</span>
            <el-button link size="small" @click="copyHash">Copy</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Previous Value" :span="2" v-if="currentAudit?.oldValue">
            <pre class="json-value">{{ JSON.stringify(currentAudit.oldValue, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="New Value" :span="2" v-if="currentAudit?.newValue">
            <pre class="json-value">{{ JSON.stringify(currentAudit.newValue, null, 2) }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="User Agent" :span="2">{{ currentAudit?.userAgent }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="verifyOnBlockchain">Verify on Blockchain</el-button>
      </template>
    </el-dialog>

    <!-- Integrity Verification Dialog -->
    <el-dialog v-model="verifyDialogVisible" title="Integrity Verification" width="500px">
      <div class="verification-progress" v-loading="verifying">
        <div v-if="!verifying && verifyResult">
          <el-result
              :icon="verifyResult.success ? 'success' : 'error'"
              :title="verifyResult.success ? 'Verification Passed' : 'Verification Failed'"
              :sub-title="verifyResult.message"
          >
            <template #extra>
              <el-button type="primary" @click="verifyDialogVisible = false">Close</el-button>
            </template>
          </el-result>
          <div v-if="verifyResult.success" class="verify-details">
            <p><strong>Total Records Verified:</strong> {{ verifyResult.totalRecords }}</p>
            <p><strong>Blockchain References:</strong> {{ verifyResult.blockchainRefs }}</p>
            <p><strong>Verification Time:</strong> {{ verifyResult.verifyTime }}</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, View, DataAnalysis, Key, Lock, Files, Medal, User, Edit, CircleCheck
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading audit trail...',
  'Verifying blockchain records...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface AuditRecord {
  id: number
  timestamp: string
  user: string
  userRole: string
  action: string
  entityType: string
  entityId: string
  entityName: string
  description: string
  ipAddress: string
  userAgent: string
  blockchainHash: string
  oldValue?: any
  newValue?: any
}

interface StatCard {
  title: string
  value: string | number
  trend: number
  icon: string
  bgColor: string
  key: string
}

// ==================== Chart References ====================
const activityChartRef = ref<HTMLElement>()
const actionChartRef = ref<HTMLElement>()
let activityChart: echarts.ECharts | null = null
let actionChart: echarts.ECharts | null = null

const chartPeriod = ref<'daily' | 'weekly'>('daily')
const tableLoading = ref(false)
const detailDialogVisible = ref(false)
const verifyDialogVisible = ref(false)
const verifying = ref(false)
const verifyResult = ref<any>(null)
const currentAudit = ref<AuditRecord | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = reactive({
  keyword: '',
  actionType: '',
  user: '',
  entityType: '',
  dateRange: null as [Date, Date] | null
})

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Records', value: '12,456', trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Active Users', value: 28, trend: 5, icon: 'User', bgColor: '#67c23a', key: 'users' },
  { title: 'Avg Response Time', value: '0.8s', trend: -10, icon: 'Clock', bgColor: '#e6a23c', key: 'response' },
  { title: 'Blockchain Verified', value: '100%', trend: 0, icon: 'Key', bgColor: '#f56c6c', key: 'verified' }
])

const auditLogs = ref<AuditRecord[]>([
  {
    id: 1,
    timestamp: '2024-01-20 14:30:22',
    user: 'John Smith',
    userRole: 'Facility Manager',
    action: 'Approve',
    entityType: 'Decision',
    entityId: 'DEC-101',
    entityName: 'Chiller Overhaul Decision',
    description: 'Approved chiller overhaul decision after technical review',
    ipAddress: '192.168.1.105',
    userAgent: 'Chrome 120.0 / Windows 11',
    blockchainHash: '0x8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e',
    oldValue: { status: 'In Review' },
    newValue: { status: 'Approved' }
  },
  {
    id: 2,
    timestamp: '2024-01-20 10:15:45',
    user: 'Sarah Chen',
    userRole: 'Operations Director',
    action: 'Create',
    entityType: 'Approval Rule',
    entityId: 'RULE-045',
    entityName: 'Critical Fault Escalation Rule',
    description: 'Created new approval rule for critical fault escalation',
    ipAddress: '192.168.1.112',
    userAgent: 'Safari 17.0 / macOS',
    blockchainHash: '0x7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6',
    newValue: { ruleName: 'Critical Fault Escalation', priority: 'High' }
  },
  {
    id: 3,
    timestamp: '2024-01-19 16:20:33',
    user: 'Lisa Zhang',
    userRole: 'Energy Manager',
    action: 'Update',
    entityType: 'Decision',
    entityId: 'DEC-102',
    entityName: 'LED Lighting Retrofit',
    description: 'Updated energy savings calculation in decision document',
    ipAddress: '192.168.1.98',
    userAgent: 'Firefox 121.0 / Windows 11',
    blockchainHash: '0x6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5',
    oldValue: { estimatedSavings: 180000 },
    newValue: { estimatedSavings: 185000 }
  },
  {
    id: 4,
    timestamp: '2024-01-19 09:45:12',
    user: 'David Wang',
    userRole: 'Chief Engineer',
    action: 'View',
    entityType: 'Document',
    entityId: 'DOC-089',
    entityName: 'HVAC Technical Specs',
    description: 'Viewed technical specification document',
    ipAddress: '192.168.1.120',
    userAgent: 'Edge 120.0 / Windows 11',
    blockchainHash: '0x5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4'
  },
  {
    id: 5,
    timestamp: '2024-01-18 13:30:08',
    user: 'Emily Zhao',
    userRole: 'ESG Manager',
    action: 'Reject',
    entityType: 'Decision',
    entityId: 'DEC-105',
    entityName: 'HVAC Optimization Algorithm',
    description: 'Rejected HVAC optimization recommendation due to budget constraints',
    ipAddress: '192.168.1.95',
    userAgent: 'Chrome 120.0 / Windows 11',
    blockchainHash: '0x4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3',
    oldValue: { status: 'Under Review' },
    newValue: { status: 'Rejected', reason: 'Budget constraints' }
  },
  {
    id: 6,
    timestamp: '2024-01-18 11:00:00',
    user: 'Tom Harris',
    userRole: 'IT Director',
    action: 'Delete',
    entityType: 'Document',
    entityId: 'DOC-045',
    entityName: 'Old UPS Manual',
    description: 'Deleted obsolete document from repository',
    ipAddress: '192.168.1.88',
    userAgent: 'Safari 17.0 / macOS',
    blockchainHash: '0x3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2'
  },
  {
    id: 7,
    timestamp: '2024-01-17 15:45:22',
    user: 'John Smith',
    userRole: 'Facility Manager',
    action: 'Export',
    entityType: 'Report',
    entityId: 'RPT-012',
    entityName: 'Q4 Maintenance Report',
    description: 'Exported quarterly maintenance report to PDF',
    ipAddress: '192.168.1.105',
    userAgent: 'Chrome 120.0 / Windows 11',
    blockchainHash: '0x2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1'
  },
  {
    id: 8,
    timestamp: '2024-01-17 09:20:15',
    user: 'Anna Kim',
    userRole: 'Finance Controller',
    action: 'Approve',
    entityType: 'Decision',
    entityId: 'DEC-104',
    entityName: 'Solar Panel Installation',
    description: 'Approved budget for solar panel project',
    ipAddress: '192.168.1.125',
    userAgent: 'Edge 120.0 / Windows 11',
    blockchainHash: '0x1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0',
    oldValue: { budgetStatus: 'Pending' },
    newValue: { budgetStatus: 'Approved', amount: 850000 }
  },
  {
    id: 9,
    timestamp: '2024-01-16 14:15:33',
    user: 'Mike Johnson',
    userRole: 'Maintenance Supervisor',
    action: 'Update',
    entityType: 'Approval Rule',
    entityId: 'RULE-023',
    entityName: 'Maintenance Escalation',
    description: 'Updated escalation timeout from 48 to 72 hours',
    ipAddress: '192.168.1.110',
    userAgent: 'Firefox 121.0 / Windows 11',
    blockchainHash: '0x0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9',
    oldValue: { escalationTime: 48 },
    newValue: { escalationTime: 72 }
  },
  {
    id: 10,
    timestamp: '2024-01-16 10:30:00',
    user: 'Sarah Chen',
    userRole: 'Operations Director',
    action: 'Login',
    entityType: 'User',
    entityId: 'USER-002',
    entityName: 'Sarah Chen',
    description: 'User logged in from new device',
    ipAddress: '203.0.113.45',
    userAgent: 'Chrome 120.0 / macOS',
    blockchainHash: '0x9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8'
  }
])

// Generate more mock data
for (let i = 11; i <= 50; i++) {
  const actions = ['Create', 'Update', 'View', 'Approve', 'Reject', 'Export']
  const entities = ['Decision', 'Approval Rule', 'Document', 'Report', 'User']
  const users = ['John Smith', 'Sarah Chen', 'David Wang', 'Lisa Zhang', 'Tom Harris', 'Emily Zhao']
  const randomDate = new Date(2024, 0, Math.floor(Math.random() * 20) + 1, Math.floor(Math.random() * 24), Math.floor(Math.random() * 60))

  auditLogs.value.push({
    id: i,
    timestamp: randomDate.toLocaleString(),
    user: users[Math.floor(Math.random() * users.length)],
    userRole: 'User',
    action: actions[Math.floor(Math.random() * actions.length)],
    entityType: entities[Math.floor(Math.random() * entities.length)],
    entityId: `${entities[Math.floor(Math.random() * entities.length)].substring(0, 3).toUpperCase()}-${Math.floor(Math.random() * 200) + 100}`,
    entityName: `Sample Entity ${i}`,
    description: `User performed ${actions[Math.floor(Math.random() * actions.length)]} action`,
    ipAddress: `192.168.1.${Math.floor(Math.random() * 255)}`,
    userAgent: 'Chrome / Windows',
    blockchainHash: Array.from({ length: 64 }, () => Math.random().toString(16)[2]).join('')
  })
}

// Sort by timestamp descending
auditLogs.value.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())

// ==================== Computed ====================
const filteredAuditLogs = computed(() => {
  let filtered = [...auditLogs.value]

  if (filters.keyword) {
    filtered = filtered.filter(l =>
        l.user.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        l.description.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        l.entityName.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.actionType) {
    filtered = filtered.filter(l => l.action === filters.actionType)
  }

  if (filters.user) {
    filtered = filtered.filter(l => l.user === filters.user)
  }

  if (filters.entityType) {
    filtered = filtered.filter(l => l.entityType === filters.entityType)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(l => {
      const date = new Date(l.timestamp)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedAuditLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAuditLogs.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getActionTag = (action: string): string => {
  const map: Record<string, string> = {
    'Create': 'success',
    'Update': 'warning',
    'Delete': 'danger',
    'Approve': 'success',
    'Reject': 'danger',
    'View': 'info',
    'Export': 'primary',
    'Login': 'info'
  }
  return map[action] || 'info'
}

const getEntityTag = (entity: string): string => {
  const map: Record<string, string> = {
    'Decision': 'primary',
    'Approval Rule': 'warning',
    'Document': 'info',
    'User': 'success',
    'Report': 'danger'
  }
  return map[entity] || 'info'
}

// ==================== Chart Initialization ====================
const initActivityChart = () => {
  if (!activityChartRef.value) return
  if (activityChart) activityChart.dispose()

  activityChart = echarts.init(activityChartRef.value)

  const dailyData = [45, 52, 48, 61, 55, 58, 42, 49, 53, 47, 51, 56, 44, 50, 54, 48, 52, 46, 49, 53, 47, 51, 55, 48, 52, 56, 43, 49, 54, 47]
  const weeklyData = [312, 345, 298, 356, 402, 378, 415, 365, 389, 412]
  const data = chartPeriod.value === 'daily' ? dailyData : weeklyData
  const xAxisData = chartPeriod.value === 'daily'
      ? Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
      : ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData, axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Activities' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbolSize: 6,
      symbol: 'circle'
    }]
  }

  activityChart.setOption(option)
  window.addEventListener('resize', () => activityChart?.resize())
}

const initActionChart = () => {
  if (!actionChartRef.value) return
  if (actionChart) actionChart.dispose()

  actionChart = echarts.init(actionChartRef.value)

  const actionCount = {
    'Create': auditLogs.value.filter(l => l.action === 'Create').length,
    'Update': auditLogs.value.filter(l => l.action === 'Update').length,
    'Delete': auditLogs.value.filter(l => l.action === 'Delete').length,
    'Approve': auditLogs.value.filter(l => l.action === 'Approve').length,
    'View': auditLogs.value.filter(l => l.action === 'View').length,
    'Export': auditLogs.value.filter(l => l.action === 'Export').length
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} actions)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: actionCount['Create'], name: 'Create', itemStyle: { color: '#67c23a' } },
        { value: actionCount['Update'], name: 'Update', itemStyle: { color: '#e6a23c' } },
        { value: actionCount['Delete'], name: 'Delete', itemStyle: { color: '#f56c6c' } },
        { value: actionCount['Approve'], name: 'Approve', itemStyle: { color: '#409eff' } },
        { value: actionCount['View'], name: 'View', itemStyle: { color: '#909399' } },
        { value: actionCount['Export'], name: 'Export', itemStyle: { color: '#67c23a' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  actionChart.setOption(option)
  window.addEventListener('resize', () => actionChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.actionType = ''
  filters.user = ''
  filters.entityType = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredAuditLogs.value.length} audit records...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const handleVerifyIntegrity = () => {
  verifyDialogVisible.value = true
  verifying.value = true
  setTimeout(() => {
    verifying.value = false
    verifyResult.value = {
      success: true,
      message: 'All audit records have been verified against blockchain. No tampering detected.',
      totalRecords: auditLogs.value.length,
      blockchainRefs: auditLogs.value.length,
      verifyTime: new Date().toLocaleString()
    }
  }, 2000)
}

const fetchAuditLogs = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const viewDetails = (record: AuditRecord) => {
  currentAudit.value = record
  detailDialogVisible.value = true
}

const verifyOnBlockchain = () => {
  ElMessage.success(`Verifying record #${currentAudit.value?.id} on blockchain...`)
  setTimeout(() => {
    ElMessage.success('Record verified on blockchain - Authentic and untampered')
  }, 1500)
}

const copyHash = () => {
  if (currentAudit.value?.blockchainHash) {
    navigator.clipboard.writeText(currentAudit.value.blockchainHash)
    ElMessage.success('Hash copied to clipboard')
  }
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initActivityChart()
    initActionChart()
  }, 100)
}

onMounted(() => {
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

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      initCharts()
      fetchAuditLogs()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.audit-trail-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.chart-row {
  margin-bottom: 20px;
}

.activity-chart-card, .action-distribution-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.chart-container {
  width: 100%;
  height: 320px;
}

.pie-chart-container {
  width: 100%;
  height: 300px;
}

.blockchain-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .verification-item {
    text-align: center;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;

    .verification-label {
      font-size: 12px;
      color: #909399;
      margin-bottom: 8px;
    }

    .verification-value {
      font-size: 18px;
      font-weight: 600;
      color: #303133;
    }
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.audit-detail {
  .hash-value {
    font-family: monospace;
    font-size: 12px;
    word-break: break-all;
  }

  .json-value {
    background: #f5f7fa;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
    overflow-x: auto;
    max-height: 200px;
  }
}

.verification-progress {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.verify-details {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;

  p {
    margin: 8px 0;
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>