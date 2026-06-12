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
        <div class="loading-tip">Trust & Identity - Decision Traceability</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="decision-traceability-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Decision Traceability</h1>
        <p>Complete audit trail of all governance decisions with full lifecycle tracking</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportTraceReport">
          <el-icon><Download /></el-icon>
          Export Trace Report
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalDecisions }}</div>
            <div class="stat-label">Total Decisions</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.traceableDecisions }}</div>
            <div class="stat-label">Traceable</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgTraceTime }}s</div>
            <div class="stat-label">Avg Trace Time</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.auditCompleteness }}%</div>
            <div class="stat-label">Audit Completeness</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Search & Filter -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by decision ID, title, or maker..."
          clearable
          style="width: 260px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All Status" value="" />
        <el-option label="Draft" value="draft" />
        <el-option label="Under Review" value="review" />
        <el-option label="Approved" value="approved" />
        <el-option label="Rejected" value="rejected" />
        <el-option label="Implemented" value="implemented" />
      </el-select>
      <el-select v-model="filters.type" placeholder="Type" clearable style="width: 140px">
        <el-option label="All Types" value="" />
        <el-option label="Policy Change" value="policy" />
        <el-option label="Approval" value="approval" />
        <el-option label="Budget" value="budget" />
        <el-option label="Strategic" value="strategic" />
      </el-select>
      <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="to"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          style="width: 260px"
      />
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- Decisions Table -->
    <div class="decisions-table-wrapper">
      <el-table :data="filteredDecisions" stripe v-loading="tableLoading" style="width: 100%" @row-click="viewDecisionTrace">
        <el-table-column prop="id" label="Decision ID" width="120" />
        <el-table-column prop="title" label="Title" min-width="220" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ formatDecisionType(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ formatStatus(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="maker" label="Decision Maker" width="160" />
        <el-table-column prop="createdAt" label="Created" width="160" />
        <el-table-column prop="updatedAt" label="Last Updated" width="160" />
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="viewDecisionTrace(row)">
              View Trace
            </el-button>
            <el-button link type="success" size="small" @click.stop="exportDecisionTrace(row)">
              Export
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Decision Trace Dialog -->
    <el-dialog v-model="traceDialog.visible" :title="`Decision Trace - ${traceDialog.decision?.id}`" width="900px" class="trace-dialog">
      <div v-if="traceDialog.decision" class="trace-content">
        <!-- Decision Header -->
        <div class="decision-header">
          <div class="decision-title">
            <h2>{{ traceDialog.decision.title }}</h2>
            <el-tag :type="getStatusTagType(traceDialog.decision.status)" size="large">
              {{ formatStatus(traceDialog.decision.status) }}
            </el-tag>
          </div>
          <div class="decision-meta">
            <span><el-icon><User /></el-icon> Maker: {{ traceDialog.decision.maker }}</span>
            <span><el-icon><Calendar /></el-icon> Created: {{ traceDialog.decision.createdAt }}</span>
            <span><el-icon><Document /></el-icon> Type: {{ formatDecisionType(traceDialog.decision.type) }}</span>
          </div>
        </div>

        <el-tabs v-model="traceTab">
          <el-tab-pane label="Lifecycle Timeline" name="timeline">
            <div class="timeline-container">
              <el-timeline>
                <el-timeline-item
                    v-for="event in traceDialog.decision.timeline"
                    :key="event.id"
                    :timestamp="event.timestamp"
                    placement="top"
                    :type="event.type"
                    :hollow="event.type === 'info'"
                >
                  <div class="timeline-event">
                    <div class="event-title">{{ event.title }}</div>
                    <div class="event-description">{{ event.description }}</div>
                    <div class="event-user">
                      <el-icon><User /></el-icon>
                      {{ event.user }}
                    </div>
                    <div v-if="event.evidence" class="event-evidence">
                      <el-link :href="event.evidence" type="primary">View Evidence</el-link>
                    </div>
                  </div>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Decision Chain" name="chain">
            <div class="decision-chain">
              <div class="chain-visualization">
                <div class="chain-nodes">
                  <div v-for="(node, idx) in traceDialog.decision.chain" :key="idx" class="chain-node">
                    <div class="node-content" :class="node.type">
                      <div class="node-title">{{ node.title }}</div>
                      <div class="node-decision">{{ node.decision }}</div>
                      <div class="node-meta">{{ node.date }} by {{ node.user }}</div>
                    </div>
                    <div v-if="idx < traceDialog.decision.chain.length - 1" class="chain-arrow">
                      <el-icon><ArrowRight /></el-icon>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Approval Workflow" name="approvals">
            <div class="approvals-container">
              <el-steps :active="getApprovalStep(traceDialog.decision)" finish-status="success" align-center>
                <el-step title="Draft" :status="getApprovalStatus(traceDialog.decision, 0)" />
                <el-step title="Initial Review" :status="getApprovalStatus(traceDialog.decision, 1)" />
                <el-step title="Committee Review" :status="getApprovalStatus(traceDialog.decision, 2)" />
                <el-step title="Final Approval" :status="getApprovalStatus(traceDialog.decision, 3)" />
              </el-steps>

              <div class="approval-details">
                <div v-for="approval in traceDialog.decision.approvals" :key="approval.step" class="approval-item">
                  <div class="approval-step">{{ approval.step }}</div>
                  <div class="approval-status">
                    <el-tag :type="approval.status === 'approved' ? 'success' : approval.status === 'rejected' ? 'danger' : 'warning'" size="small">
                      {{ approval.status }}
                    </el-tag>
                  </div>
                  <div class="approval-reviewer">{{ approval.reviewer }}</div>
                  <div class="approval-date">{{ approval.date || 'Pending' }}</div>
                  <div v-if="approval.comments" class="approval-comments">{{ approval.comments }}</div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Blockchain Anchoring" name="blockchain">
            <div class="blockchain-info">
              <el-alert
                  title="Decision Anchored on Blockchain"
                  type="success"
                  :description="`Decision anchored at block ${traceDialog.decision.blockchain?.blockNumber} with transaction hash: ${traceDialog.decision.blockchain?.txHash}`"
                  show-icon
                  :closable="false"
              />
              <div class="blockchain-details">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="Transaction Hash">
                    <code>{{ traceDialog.decision.blockchain?.txHash }}</code>
                    <el-button link size="small" @click="viewOnExplorer(traceDialog.decision.blockchain?.txHash)">View</el-button>
                  </el-descriptions-item>
                  <el-descriptions-item label="Block Number">{{ traceDialog.decision.blockchain?.blockNumber }}</el-descriptions-item>
                  <el-descriptions-item label="Block Hash">{{ traceDialog.decision.blockchain?.blockHash }}</el-descriptions-item>
                  <el-descriptions-item label="Network">{{ traceDialog.decision.blockchain?.network }}</el-descriptions-item>
                  <el-descriptions-item label="Anchored At">{{ traceDialog.decision.blockchain?.timestamp }}</el-descriptions-item>
                  <el-descriptions-item label="Anchored By">{{ traceDialog.decision.blockchain?.anchoredBy }}</el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Evidence & Attachments" name="evidence">
            <div class="evidence-list">
              <div v-for="doc in traceDialog.decision.evidence" :key="doc.id" class="evidence-item">
                <div class="evidence-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="evidence-info">
                  <div class="evidence-name">{{ doc.name }}</div>
                  <div class="evidence-meta">{{ doc.type }} • {{ doc.size }} • Uploaded by {{ doc.uploadedBy }} on {{ doc.date }}</div>
                </div>
                <div class="evidence-actions">
                  <el-button link type="primary" size="small" @click="downloadEvidence(doc)">Download</el-button>
                  <el-button link type="info" size="small" @click="verifyEvidence(doc)">Verify</el-button>
                </div>
              </div>
              <div v-if="!traceDialog.decision.evidence?.length" class="no-evidence">
                <span>No evidence attached</span>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Full Audit Log" name="audit">
            <div class="audit-log">
              <el-table :data="traceDialog.decision.auditLog" stripe size="small">
                <el-table-column prop="timestamp" label="Timestamp" width="180" />
                <el-table-column prop="action" label="Action" width="150" />
                <el-table-column prop="user" label="User" width="160" />
                <el-table-column prop="details" label="Details" min-width="250" show-overflow-tooltip />
                <el-table-column prop="ipAddress" label="IP Address" width="140" />
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>

        <!-- Version Comparison -->
        <div class="version-comparison" v-if="traceDialog.decision.versions?.length > 1">
          <div class="comparison-header">
            <h4>Version History</h4>
            <el-select v-model="compareVersion1" placeholder="Version 1" size="small" style="width: 140px">
              <el-option v-for="v in traceDialog.decision.versions" :key="v.version" :label="`v${v.version}`" :value="v.version" />
            </el-select>
            <el-icon><ArrowRight /></el-icon>
            <el-select v-model="compareVersion2" placeholder="Version 2" size="small" style="width: 140px">
              <el-option v-for="v in traceDialog.decision.versions" :key="v.version" :label="`v${v.version}`" :value="v.version" />
            </el-select>
            <el-button size="small" @click="compareVersions">Compare</el-button>
          </div>
          <div v-if="comparisonResult" class="comparison-result">
            <div v-for="diff in comparisonResult" :key="diff.field" class="diff-item">
              <span class="diff-field">{{ diff.field }}:</span>
              <span class="diff-old">{{ diff.oldValue }}</span>
              <el-icon><ArrowRight /></el-icon>
              <span class="diff-new">{{ diff.newValue }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="traceDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="exportFullTrace">
          Export Full Trace
        </el-button>
      </template>
    </el-dialog>

    <!-- Compare Versions Dialog -->
    <el-dialog v-model="compareDialog.visible" title="Version Comparison" width="650px">
      <div v-if="compareDialog.result" class="compare-diff">
        <div v-for="diff in compareDialog.result" :key="diff.field" class="diff-row">
          <div class="diff-field">{{ diff.field }}</div>
          <div class="diff-old-value">
            <span class="diff-label">v{{ diff.oldVersion }}:</span>
            <span class="diff-value">{{ diff.oldValue || '(empty)' }}</span>
          </div>
          <div class="diff-new-value">
            <span class="diff-label">v{{ diff.newVersion }}:</span>
            <span class="diff-value diff-changed">{{ diff.newValue || '(empty)' }}</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Download,
  Refresh,
  Document,
  CircleCheck,
  Clock,
  DataAnalysis,
  Search,
  RefreshLeft,
  User,
  Calendar,
  ArrowRight,
  Warning,
  Link
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading decision registry...',
  'Building traceability graph...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface Decision {
  id: string
  title: string
  description: string
  type: string
  status: string
  maker: string
  createdAt: string
  updatedAt: string
  timeline: any[]
  chain: any[]
  approvals: any[]
  blockchain: any
  evidence: any[]
  auditLog: any[]
  versions?: any[]
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalDecisions: 156,
  traceableDecisions: 152,
  avgTraceTime: 1.2,
  auditCompleteness: 98
})

const decisions = ref<Decision[]>([
  {
    id: 'DEC-001',
    title: 'AI Model Deployment Approval - Energy Optimization v2.0',
    description: 'Approval for deploying the Energy Optimization AI model to production environment',
    type: 'approval',
    status: 'implemented',
    maker: 'John Smith (CTO)',
    createdAt: '2024-06-01 10:00:00',
    updatedAt: '2024-06-15 14:30:00',
    timeline: [
      { id: 1, type: 'primary', title: 'Decision Drafted', description: 'Initial decision document created', user: 'John Smith', timestamp: '2024-06-01 10:00:00' },
      { id: 2, type: 'primary', title: 'Technical Review', description: 'Technical feasibility review completed', user: 'Sarah Lee', timestamp: '2024-06-05 14:30:00' },
      { id: 3, type: 'success', title: 'Approved', description: 'Decision approved by committee', user: 'Mike Chen', timestamp: '2024-06-10 09:15:00' },
      { id: 4, type: 'success', title: 'Implemented', description: 'Decision fully implemented', user: 'System', timestamp: '2024-06-15 14:30:00' }
    ],
    chain: [
      { title: 'Initial Proposal', decision: 'Propose deployment of AI model', date: '2024-06-01', user: 'John Smith', type: 'proposal' },
      { title: 'Technical Review', decision: 'Recommend approval with conditions', date: '2024-06-05', user: 'Sarah Lee', type: 'review' },
      { title: 'Committee Vote', decision: 'Approved (5-0)', date: '2024-06-10', user: 'Committee', type: 'vote' },
      { title: 'Final Decision', decision: 'Implementation approved', date: '2024-06-10', user: 'Mike Chen', type: 'decision' }
    ],
    approvals: [
      { step: 'Draft', status: 'approved', reviewer: 'John Smith', date: '2024-06-01', comments: 'Initial draft complete' },
      { step: 'Initial Review', status: 'approved', reviewer: 'Sarah Lee', date: '2024-06-05', comments: 'Technically sound' },
      { step: 'Committee Review', status: 'approved', reviewer: 'Committee', date: '2024-06-10', comments: 'Unanimous approval' },
      { step: 'Final Approval', status: 'approved', reviewer: 'Mike Chen', date: '2024-06-10', comments: 'Proceed with implementation' }
    ],
    blockchain: {
      txHash: '0x7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b',
      blockNumber: 18234567,
      blockHash: '0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8',
      network: 'Ethereum',
      timestamp: '2024-06-10 14:30:00',
      anchoredBy: '0x742d...bEb0'
    },
    evidence: [
      { id: 1, name: 'Technical_Assessment.pdf', type: 'PDF', size: '2.4 MB', uploadedBy: 'Sarah Lee', date: '2024-06-05' },
      { id: 2, name: 'Model_Performance_Report.pdf', type: 'PDF', size: '1.8 MB', uploadedBy: 'John Smith', date: '2024-06-01' }
    ],
    auditLog: [
      { timestamp: '2024-06-01 10:00:00', action: 'Create', user: 'John Smith', details: 'Decision created', ipAddress: '192.168.1.100' },
      { timestamp: '2024-06-05 14:30:00', action: 'Update', user: 'Sarah Lee', details: 'Technical review completed', ipAddress: '192.168.1.101' },
      { timestamp: '2024-06-10 09:15:00', action: 'Approve', user: 'Mike Chen', details: 'Decision approved', ipAddress: '192.168.1.102' }
    ],
    versions: [
      { version: 1, title: 'AI Model Deployment Approval v1', description: 'Initial version', updatedAt: '2024-06-01' },
      { version: 2, title: 'AI Model Deployment Approval v2', description: 'Updated with technical review feedback', updatedAt: '2024-06-05' },
      { version: 3, title: 'AI Model Deployment Approval v3', description: 'Final approved version', updatedAt: '2024-06-10' }
    ]
  },
  {
    id: 'DEC-002',
    title: 'Budget Allocation - AI Infrastructure Upgrade',
    description: 'Approval of $500,000 budget for AI compute infrastructure',
    type: 'budget',
    status: 'approved',
    maker: 'Mike Chen (CFO)',
    createdAt: '2024-06-03 11:00:00',
    updatedAt: '2024-06-12 10:00:00',
    timeline: [
      { id: 1, type: 'primary', title: 'Budget Request', description: 'Budget proposal submitted', user: 'Mike Chen', timestamp: '2024-06-03 11:00:00' },
      { id: 2, type: 'primary', title: 'Finance Review', description: 'Financial review completed', user: 'Anna Zhang', timestamp: '2024-06-07 15:00:00' },
      { id: 3, type: 'success', title: 'Approved', description: 'Budget approved by board', user: 'Board', timestamp: '2024-06-12 10:00:00' }
    ],
    chain: [
      { title: 'Budget Request', decision: 'Request $500k for infrastructure', date: '2024-06-03', user: 'Mike Chen', type: 'proposal' },
      { title: 'Finance Review', decision: 'Recommend approval', date: '2024-06-07', user: 'Anna Zhang', type: 'review' },
      { title: 'Board Decision', decision: 'Approved', date: '2024-06-12', user: 'Board', type: 'decision' }
    ],
    approvals: [
      { step: 'Draft', status: 'approved', reviewer: 'Mike Chen', date: '2024-06-03', comments: '' },
      { step: 'Initial Review', status: 'approved', reviewer: 'Anna Zhang', date: '2024-06-07', comments: 'Within budget' },
      { step: 'Committee Review', status: 'approved', reviewer: 'Committee', date: '2024-06-10', comments: '' },
      { step: 'Final Approval', status: 'approved', reviewer: 'Board', date: '2024-06-12', comments: 'Approved' }
    ],
    blockchain: {
      txHash: '0x8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
      blockNumber: 18234890,
      blockHash: '0x8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7',
      network: 'Ethereum',
      timestamp: '2024-06-12 10:00:00',
      anchoredBy: '0x742d...bEb0'
    },
    evidence: [
      { id: 1, name: 'Budget_Proposal.xlsx', type: 'Excel', size: '856 KB', uploadedBy: 'Mike Chen', date: '2024-06-03' }
    ],
    auditLog: [
      { timestamp: '2024-06-03 11:00:00', action: 'Create', user: 'Mike Chen', details: 'Budget request created', ipAddress: '192.168.1.100' },
      { timestamp: '2024-06-12 10:00:00', action: 'Approve', user: 'Board', details: 'Budget approved', ipAddress: '192.168.1.105' }
    ]
  }
])

const filters = reactive({
  search: '',
  status: '',
  type: '',
  dateRange: null as Date[] | null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const traceDialog = reactive({
  visible: false,
  decision: null as Decision | null
})

const compareDialog = reactive({
  visible: false,
  result: null as any
})

const traceTab = ref('timeline')
const compareVersion1 = ref(1)
const compareVersion2 = ref(2)
const comparisonResult = ref<any[]>([])

// ==================== 计算属性 ====================
const filteredDecisions = computed(() => {
  let filtered = [...decisions.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(d =>
        d.id.toLowerCase().includes(searchLower) ||
        d.title.toLowerCase().includes(searchLower) ||
        d.maker.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(d => d.status === filters.status)
  }

  if (filters.type) {
    filtered = filtered.filter(d => d.type === filters.type)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(d => {
      const date = new Date(d.createdAt)
      return date >= start && date <= end
    })
  }

  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== 辅助函数 ====================
const formatDecisionType = (type: string) => {
  const map: Record<string, string> = {
    'policy': 'Policy Change',
    'approval': 'Approval',
    'budget': 'Budget',
    'strategic': 'Strategic'
  }
  return map[type] || type
}

const formatStatus = (status: string) => {
  const map: Record<string, string> = {
    'draft': 'Draft',
    'review': 'Under Review',
    'approved': 'Approved',
    'rejected': 'Rejected',
    'implemented': 'Implemented'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'draft': 'info',
    'review': 'warning',
    'approved': 'success',
    'rejected': 'danger',
    'implemented': 'success'
  }
  return map[status] || 'info'
}

const getApprovalStep = (decision: Decision) => {
  const approvedCount = decision.approvals.filter(a => a.status === 'approved').length
  return Math.min(approvedCount, 4)
}

const getApprovalStatus = (decision: Decision, stepIndex: number) => {
  if (stepIndex < decision.approvals.length && decision.approvals[stepIndex].status === 'approved') {
    return 'success'
  }
  if (stepIndex === decision.approvals.length) {
    return 'wait'
  }
  return 'process'
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.type = ''
  filters.dateRange = null
  pagination.currentPage = 1
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const viewDecisionTrace = (decision: Decision) => {
  traceDialog.decision = decision
  traceTab.value = 'timeline'
  compareVersion1.value = 1
  compareVersion2.value = decision.versions ? decision.versions.length : 2
  comparisonResult.value = []
  traceDialog.visible = true
}

const exportDecisionTrace = (decision: Decision) => {
  const traceData = {
    decision: {
      id: decision.id,
      title: decision.title,
      status: decision.status,
      maker: decision.maker,
      createdAt: decision.createdAt
    },
    timeline: decision.timeline,
    approvals: decision.approvals,
    blockchain: decision.blockchain,
    auditLog: decision.auditLog
  }
  const data = JSON.stringify(traceData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `decision-trace-${decision.id}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Decision trace exported')
}

const exportFullTrace = () => {
  if (traceDialog.decision) {
    exportDecisionTrace(traceDialog.decision)
  }
}

const exportTraceReport = () => {
  const report = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    decisions: decisions.value
  }
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `traceability-report-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Trace report exported')
}

const viewOnExplorer = (txHash: string) => {
  window.open(`https://etherscan.io/tx/${txHash}`, '_blank')
}

const downloadEvidence = (doc: any) => {
  ElMessage.success(`Downloading ${doc.name}`)
}

const verifyEvidence = (doc: any) => {
  ElMessage.info(`Verifying ${doc.name} against blockchain...`)
}

const compareVersions = () => {
  if (!traceDialog.decision?.versions) return

  const v1 = traceDialog.decision.versions.find(v => v.version === compareVersion1.value)
  const v2 = traceDialog.decision.versions.find(v => v.version === compareVersion2.value)

  if (v1 && v2) {
    const differences = []
    if (v1.title !== v2.title) {
      differences.push({ field: 'Title', oldValue: v1.title, newValue: v2.title })
    }
    if (v1.description !== v2.description) {
      differences.push({ field: 'Description', oldValue: v1.description, newValue: v2.description })
    }
    comparisonResult.value = differences
  }
}

// ==================== 数据加载 ====================
const loadData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
  }, 500)
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})
</script>

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

/* ==================== Main Content Styles ==================== */
.decision-traceability-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
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
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Cards */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Decisions Table */
.decisions-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

/* Trace Dialog */
.trace-dialog :deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
  padding-top: 0;
}

.decision-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  margin: -20px -20px 20px -20px;
  padding: 20px 24px;
  color: white;
  border-radius: 12px 12px 0 0;
}

.decision-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.decision-title h2 {
  margin: 0;
  font-size: 18px;
}

.decision-meta {
  display: flex;
  gap: 24px;
  font-size: 13px;
  opacity: 0.9;
}

.decision-meta .el-icon {
  margin-right: 4px;
}

/* Timeline */
.timeline-container {
  max-height: 500px;
  overflow-y: auto;
  padding: 8px 0;
}

.timeline-event {
  padding-bottom: 8px;
}

.event-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.event-description {
  font-size: 13px;
  color: #5e6e82;
  margin-bottom: 4px;
}

.event-user {
  font-size: 11px;
  color: #8c9aab;
  display: flex;
  align-items: center;
  gap: 4px;
}

.event-evidence {
  margin-top: 8px;
}

/* Decision Chain */
.decision-chain {
  padding: 20px;
}

.chain-visualization {
  overflow-x: auto;
}

.chain-nodes {
  display: flex;
  align-items: center;
  min-width: 800px;
}

.chain-node {
  display: flex;
  align-items: center;
  flex: 1;
}

.node-content {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
  min-width: 200px;
  border-left: 4px solid #409eff;
}

.node-content.proposal { border-left-color: #e6a23c; }
.node-content.review { border-left-color: #409eff; }
.node-content.vote { border-left-color: #909399; }
.node-content.decision { border-left-color: #67c23a; }

.node-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 8px;
}

.node-decision {
  font-size: 13px;
  color: #1f2f3d;
  margin-bottom: 8px;
}

.node-meta {
  font-size: 11px;
  color: #8c9aab;
}

.chain-arrow {
  margin: 0 12px;
  color: #c0c4cc;
}

/* Approvals */
.approvals-container {
  padding: 20px;
}

.approval-details {
  margin-top: 32px;
}

.approval-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.approval-step {
  width: 140px;
  font-weight: 500;
}

.approval-status {
  width: 100px;
}

.approval-reviewer {
  width: 140px;
}

.approval-date {
  width: 140px;
  color: #8c9aab;
  font-size: 12px;
}

.approval-comments {
  flex: 1;
  font-size: 12px;
  color: #5e6e82;
}

/* Blockchain Info */
.blockchain-info {
  padding: 20px;
}

.blockchain-details {
  margin-top: 20px;
}

/* Evidence List */
.evidence-list {
  padding: 8px 0;
}

.evidence-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #ebeef5;
}

.evidence-icon {
  font-size: 32px;
  color: #8c9aab;
}

.evidence-info {
  flex: 1;
}

.evidence-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.evidence-meta {
  font-size: 11px;
  color: #8c9aab;
}

.evidence-actions {
  display: flex;
  gap: 8px;
}

.no-evidence {
  text-align: center;
  padding: 40px;
  color: #8c9aab;
}

/* Audit Log */
.audit-log {
  padding: 8px 0;
}

/* Version Comparison */
.version-comparison {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.comparison-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.comparison-header h4 {
  margin: 0;
}

.comparison-result {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.diff-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
}

.diff-field {
  width: 100px;
  font-weight: 500;
}

.diff-old {
  color: #f56c6c;
  text-decoration: line-through;
}

.diff-new {
  color: #67c23a;
}

/* Compare Dialog */
.compare-diff {
  padding: 8px 0;
}

.diff-row {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.diff-field {
  font-weight: 600;
  margin-bottom: 8px;
}

.diff-old-value, .diff-new-value {
  font-size: 13px;
  margin-left: 16px;
  margin-bottom: 4px;
}

.diff-label {
  display: inline-block;
  width: 40px;
  color: #8c9aab;
}

.diff-value {
  color: #5e6e82;
}

.diff-changed {
  color: #67c23a;
  font-weight: 500;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}

:deep(.el-step__title) {
  font-size: 12px;
}
</style>