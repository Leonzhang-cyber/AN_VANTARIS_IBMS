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
        <div class="loading-tip">OpenBIM Integration - ISO 19650 CDE Link</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cde-link-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>ISO 19650 CDE Link</h1>
        <p>Connect to Common Data Environment (CDE) for collaborative BIM information management</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="syncCDE" :loading="isSyncing">
          <el-icon><Refresh /></el-icon>
          Sync with CDE
        </el-button>
        <el-button @click="exportMetadata">
          <el-icon><Download /></el-icon>
          Export Metadata
        </el-button>
        <el-button @click="configureConnection">
          <el-icon><Setting /></el-icon>
          Configure
        </el-button>
      </div>
    </div>

    <!-- Connection Status -->
    <div class="status-card">
      <div class="connection-status" :class="connectionStatus">
        <div class="status-indicator"></div>
        <div class="status-text">
          <strong>{{ connectionStatus === 'connected' ? 'Connected to CDE' : connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected' }}</strong>
          <span v-if="connectionStatus === 'connected'">Last sync: {{ lastSyncTime }}</span>
        </div>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Folder /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalContainers }}</div>
            <div class="stat-label">Total Containers</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalDocuments }}</div>
            <div class="stat-label">Documents</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingReviews }}</div>
            <div class="stat-label">Pending Reviews</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeUsers }}</div>
            <div class="stat-label">Active Users</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- CDE Containers Navigation -->
      <el-col :xs="24" :lg="10">
        <div class="containers-card">
          <div class="card-header">
            <h3>CDE Containers</h3>
            <div class="search-input">
              <el-input
                  v-model="containerSearch"
                  placeholder="Search containers..."
                  clearable
                  size="small"
                  style="width: 160px"
                  :prefix-icon="Search"
              />
            </div>
          </div>
          <div class="container-tree">
            <el-tree
                :data="filteredContainerTree"
                :props="containerTreeProps"
                node-key="id"
                :expand-on-click-node="false"
                @node-click="onContainerSelect"
                highlight-current
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <el-icon><component :is="getContainerIcon(data.type)" /></el-icon>
                  <span>{{ data.name }}</span>
                  <el-tag v-if="data.status" :type="getStatusTagType(data.status)" size="small" class="status-tag">
                    {{ data.status }}
                  </el-tag>
                  <span class="node-count">{{ data.count || '' }}</span>
                </span>
              </template>
            </el-tree>
          </div>
        </div>
      </el-col>

      <!-- Documents & Workflow -->
      <el-col :xs="24" :lg="14">
        <div class="documents-card" v-if="selectedContainer">
          <div class="card-header">
            <h3>{{ selectedContainer.name }} - Documents</h3>
            <div class="doc-actions">
              <el-button size="small" @click="uploadDocument">
                <el-icon><Upload /></el-icon>
                Upload
              </el-button>
              <el-button size="small" @click="refreshDocuments">
                <el-icon><Refresh /></el-icon>
                Refresh
              </el-button>
            </div>
          </div>
          <el-table :data="documents" stripe v-loading="docLoading" style="width: 100%">
            <el-table-column prop="name" label="Document Name" min-width="200" show-overflow-tooltip />
            <el-table-column prop="type" label="Type" width="100" />
            <el-table-column prop="version" label="Version" width="80" />
            <el-table-column prop="status" label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="lastModified" label="Modified" width="160" />
            <el-table-column prop="modifiedBy" label="Modified By" width="140" />
            <el-table-column label="Actions" width="140" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewDocument(row)">View</el-button>
                <el-button link type="success" size="small" @click="downloadDocument(row)">Download</el-button>
                <el-button v-if="row.status === 'WIP'" link type="warning" size="small" @click="submitForReview(row)">Submit</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="documents.length === 0" class="no-documents">
            <el-empty description="No documents in this container" :image-size="60" />
          </div>
        </div>

        <div class="placeholder-card" v-else>
          <el-icon><FolderOpened /></el-icon>
          <span>Select a container from the left to view documents</span>
        </div>

        <!-- Workflow Tasks -->
        <div class="tasks-card" v-if="pendingTasks.length > 0">
          <div class="card-header">
            <h3>Pending Workflow Tasks</h3>
            <el-button size="small" @click="refreshTasks">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
          </div>
          <el-table :data="pendingTasks" stripe>
            <el-table-column prop="title" label="Task" min-width="200" />
            <el-table-column prop="document" label="Document" width="180" show-overflow-tooltip />
            <el-table-column prop="assignedTo" label="Assigned To" width="140" />
            <el-table-column prop="dueDate" label="Due Date" width="120">
              <template #default="{ row }">
                <span :class="{ overdue: isOverdue(row.dueDate) }">{{ row.dueDate }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="120">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="approveTask(row)">Approve</el-button>
                <el-button link type="danger" size="small" @click="rejectTask(row)">Reject</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <!-- Document Detail Dialog -->
    <el-dialog v-model="docDialog.visible" :title="docDialog.document?.name" width="600px">
      <div v-if="docDialog.document">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Document ID">{{ docDialog.document.id }}</el-descriptions-item>
          <el-descriptions-item label="Version">{{ docDialog.document.version }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(docDialog.document.status)" size="small">
              {{ docDialog.document.status }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Size">{{ docDialog.document.size }}</el-descriptions-item>
          <el-descriptions-item label="Created By">{{ docDialog.document.createdBy }}</el-descriptions-item>
          <el-descriptions-item label="Created Date">{{ docDialog.document.createdDate }}</el-descriptions-item>
          <el-descriptions-item label="Modified By">{{ docDialog.document.modifiedBy }}</el-descriptions-item>
          <el-descriptions-item label="Modified Date">{{ docDialog.document.modifiedDate }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ docDialog.document.description || 'No description' }}</el-descriptions-item>
          <el-descriptions-item label="Revision History" :span="2">
            <div class="revision-history">
              <div v-for="rev in docDialog.document.revisions" :key="rev.version" class="revision-item">
                <strong>v{{ rev.version }}</strong> - {{ rev.date }} by {{ rev.user }}: {{ rev.comment }}
              </div>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="docDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="downloadDocument(docDialog.document)">Download</el-button>
      </template>
    </el-dialog>

    <!-- Submit for Review Dialog -->
    <el-dialog v-model="submitDialog.visible" title="Submit for Review" width="450px">
      <el-form :model="submitForm" label-width="100px">
        <el-form-item label="Document">
          <el-input :value="submitDialog.document?.name" disabled />
        </el-form-item>
        <el-form-item label="Version">
          <el-input :value="submitDialog.document?.version" disabled />
        </el-form-item>
        <el-form-item label="Reviewer" required>
          <el-select v-model="submitForm.reviewer" placeholder="Select reviewer" style="width: 100%">
            <el-option label="John Smith (Lead Architect)" value="john.smith@example.com" />
            <el-option label="Sarah Lee (BIM Manager)" value="sarah.lee@example.com" />
            <el-option label="Mike Chen (QA)" value="mike.chen@example.com" />
            <el-option label="Anna Zhang (Project Manager)" value="anna.zhang@example.com" />
          </el-select>
        </el-form-item>
        <el-form-item label="Comments">
          <el-input v-model="submitForm.comments" type="textarea" :rows="2" placeholder="Add comments for reviewer..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmSubmit">Submit</el-button>
      </template>
    </el-dialog>

    <!-- Approval Dialog -->
    <el-dialog v-model="approvalDialog.visible" title="Review Document" width="500px">
      <el-form :model="approvalForm" label-width="100px">
        <el-form-item label="Decision">
          <el-radio-group v-model="approvalForm.decision">
            <el-radio value="approved">Approved</el-radio>
            <el-radio value="rejected">Rejected</el-radio>
            <el-radio value="rework">Rework Required</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Comments">
          <el-input v-model="approvalForm.comments" type="textarea" :rows="3" placeholder="Add review comments..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approvalDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmApproval">Submit Review</el-button>
      </template>
    </el-dialog>

    <!-- Sync Progress Dialog -->
    <el-dialog v-model="syncDialog.visible" title="Synchronizing with CDE" width="450px" :close-on-click-modal="false" :show-close="false">
      <div class="sync-progress">
        <el-progress :percentage="syncProgress" :stroke-width="10" />
        <div class="sync-status">{{ syncStatus }}</div>
        <div class="sync-details">{{ syncDetails }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Download,
  Setting,
  Folder,
  Document,
  Clock,
  User,
  Search,
  Upload,
  FolderOpened,
  InfoFilled,
  Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const isSyncing = ref(false)
const docLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Connecting to CDE...',
  'Loading container structure...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface ContainerNode {
  id: string
  name: string
  type: string
  status: string
  count?: number
  children?: ContainerNode[]
}

interface Document {
  id: string
  name: string
  type: string
  version: string
  status: 'WIP' | 'Shared' | 'Published' | 'Archived' | 'Under Review'
  size: string
  createdBy: string
  createdDate: string
  modifiedBy: string
  modifiedDate: string
  description: string
  revisions: Array<{ version: string; date: string; user: string; comment: string }>
}

interface WorkflowTask {
  id: string
  title: string
  document: string
  documentId: string
  assignedTo: string
  dueDate: string
  status: string
}

// ==================== 模拟数据 ====================
const containerTree = ref<ContainerNode[]>([
  {
    id: '1',
    name: 'Project Root',
    type: 'project',
    status: 'Active',
    children: [
      {
        id: '2',
        name: 'WIP (Work in Progress)',
        type: 'container',
        status: 'WIP',
        count: 12,
        children: [
          { id: '3', name: 'Architecture', type: 'folder', status: 'WIP', count: 5 },
          { id: '4', name: 'Structure', type: 'folder', status: 'WIP', count: 3 },
          { id: '5', name: 'MEP', type: 'folder', status: 'WIP', count: 4 }
        ]
      },
      {
        id: '6',
        name: 'Shared',
        type: 'container',
        status: 'Shared',
        count: 8,
        children: [
          { id: '7', name: 'Design Reviews', type: 'folder', status: 'Shared', count: 3 },
          { id: '8', name: 'Coordination Models', type: 'folder', status: 'Shared', count: 5 }
        ]
      },
      {
        id: '9',
        name: 'Published',
        type: 'container',
        status: 'Published',
        count: 6,
        children: [
          { id: '10', name: 'As-Built', type: 'folder', status: 'Published', count: 2 },
          { id: '11', name: 'O&M Manuals', type: 'folder', status: 'Published', count: 4 }
        ]
      },
      {
        id: '12',
        name: 'Archive',
        type: 'container',
        status: 'Archived',
        count: 15
      }
    ]
  }
])

const documents = ref<Document[]>([
  {
    id: 'DOC-001', name: 'Architectural_Model_v2.ifc', type: 'IFC', version: '2.0',
    status: 'WIP', size: '24.5 MB', createdBy: 'John Smith', createdDate: '2024-06-01',
    modifiedBy: 'John Smith', modifiedDate: '2024-06-10', description: 'Architectural model including all building elements',
    revisions: [
      { version: '1.0', date: '2024-05-15', user: 'John Smith', comment: 'Initial version' },
      { version: '2.0', date: '2024-06-10', user: 'John Smith', comment: 'Updated with client feedback' }
    ]
  },
  {
    id: 'DOC-002', name: 'Structural_Frame.rvt', type: 'RVT', version: '1.2',
    status: 'Shared', size: '18.2 MB', createdBy: 'Sarah Lee', createdDate: '2024-05-20',
    modifiedBy: 'Sarah Lee', modifiedDate: '2024-06-08', description: 'Structural steel and concrete model',
    revisions: [
      { version: '1.0', date: '2024-05-20', user: 'Sarah Lee', comment: 'Initial version' },
      { version: '1.1', date: '2024-06-01', user: 'Sarah Lee', comment: 'Updated connections' },
      { version: '1.2', date: '2024-06-08', user: 'Sarah Lee', comment: 'Added foundation details' }
    ]
  },
  {
    id: 'DOC-003', name: 'HVAC_Design.dwg', type: 'DWG', version: '3.0',
    status: 'Under Review', size: '12.8 MB', createdBy: 'Mike Chen', createdDate: '2024-05-10',
    modifiedBy: 'Mike Chen', modifiedDate: '2024-06-12', description: 'HVAC ductwork and equipment layout',
    revisions: [
      { version: '1.0', date: '2024-05-10', user: 'Mike Chen', comment: 'Initial design' },
      { version: '2.0', date: '2024-05-25', user: 'Mike Chen', comment: 'Revised per coordination' },
      { version: '3.0', date: '2024-06-12', user: 'Mike Chen', comment: 'Final for review' }
    ]
  },
  {
    id: 'DOC-004', name: 'Electrical_OneLine.pdf', type: 'PDF', version: '1.0',
    status: 'Published', size: '2.1 MB', createdBy: 'David Kim', createdDate: '2024-06-05',
    modifiedBy: 'David Kim', modifiedDate: '2024-06-05', description: 'Electrical single-line diagram',
    revisions: [
      { version: '1.0', date: '2024-06-05', user: 'David Kim', comment: 'First release' }
    ]
  }
])

const pendingTasks = ref<WorkflowTask[]>([
  { id: 'T1', title: 'Review Architectural Model', document: 'Architectural_Model_v2.ifc', documentId: 'DOC-001', assignedTo: 'Sarah Lee', dueDate: '2024-06-15', status: 'pending' },
  { id: 'T2', title: 'Approve HVAC Design', document: 'HVAC_Design.dwg', documentId: 'DOC-003', assignedTo: 'John Smith', dueDate: '2024-06-18', status: 'pending' },
  { id: 'T3', title: 'Review Coordination Model', document: 'MEP_Coordination.ifc', documentId: 'DOC-005', assignedTo: 'Mike Chen', dueDate: '2024-06-14', status: 'pending' }
])

const stats = reactive({
  totalContainers: 12,
  totalDocuments: 48,
  pendingReviews: 8,
  activeUsers: 24
})

const connectionStatus = ref<'connected' | 'connecting' | 'disconnected'>('connected')
const lastSyncTime = ref('2024-06-12 14:30:00')
const selectedContainer = ref<ContainerNode | null>(null)
const containerSearch = ref('')
const syncProgress = ref(0)
const syncStatus = ref('')
const syncDetails = ref('')

const docDialog = reactive({
  visible: false,
  document: null as Document | null
})

const submitDialog = reactive({
  visible: false,
  document: null as Document | null
})

const approvalDialog = reactive({
  visible: false,
  task: null as WorkflowTask | null
})

const syncDialog = reactive({
  visible: false
})

const submitForm = reactive({
  reviewer: '',
  comments: ''
})

const approvalForm = reactive({
  decision: 'approved',
  comments: ''
})

const containerTreeProps = { children: 'children', label: 'name' }

// ==================== 计算属性 ====================
const filteredContainerTree = computed(() => {
  if (!containerSearch.value) return containerTree.value
  const searchLower = containerSearch.value.toLowerCase()
  const filterNode = (nodes: ContainerNode[]): ContainerNode[] => {
    return nodes.reduce((acc, node) => {
      const matches = node.name.toLowerCase().includes(searchLower)
      const children = node.children ? filterNode(node.children) : []
      if (matches || children.length > 0) {
        acc.push({ ...node, children: children.length > 0 ? children : node.children })
      }
      return acc
    }, [] as ContainerNode[])
  }
  return filterNode(containerTree.value)
})

// ==================== 辅助函数 ====================
const getContainerIcon = (type: string) => {
  const map: Record<string, any> = {
    'project': Folder,
    'container': Folder,
    'folder': Document,
    'WIP': Clock,
    'Shared': Folder,
    'Published': Folder,
    'Archived': Folder
  }
  return map[type] || Folder
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'WIP': 'warning',
    'Shared': 'info',
    'Published': 'success',
    'Archived': 'info',
    'Under Review': 'warning',
    'Active': 'success'
  }
  return map[status] || 'info'
}

const isOverdue = (dueDate: string) => {
  return new Date(dueDate) < new Date()
}

const onContainerSelect = (node: ContainerNode) => {
  selectedContainer.value = node
  // Simulate loading documents for the selected container
  docLoading.value = true
  setTimeout(() => {
    docLoading.value = false
    // Documents would be filtered by container in real implementation
  }, 500)
}

const refreshDocuments = () => {
  docLoading.value = true
  setTimeout(() => {
    docLoading.value = false
    ElMessage.success('Documents refreshed')
  }, 800)
}

const refreshTasks = () => {
  ElMessage.success('Tasks refreshed')
}

const viewDocument = (doc: Document) => {
  docDialog.document = doc
  docDialog.visible = true
}

const downloadDocument = (doc: Document) => {
  ElMessage.success(`Downloading ${doc.name}`)
}

const uploadDocument = () => {
  ElMessage.info('Upload document functionality')
  const input = document.createElement('input')
  input.type = 'file'
  input.onchange = (e: any) => {
    if (e.target.files?.[0]) {
      ElMessage.success(`Uploading ${e.target.files[0].name}`)
    }
  }
  input.click()
}

const submitForReview = (doc: Document) => {
  submitDialog.document = doc
  submitForm.reviewer = ''
  submitForm.comments = ''
  submitDialog.visible = true
}

const confirmSubmit = () => {
  if (!submitForm.reviewer) {
    ElMessage.warning('Please select a reviewer')
    return
  }
  ElMessage.success(`Document submitted for review to ${submitForm.reviewer.split('@')[0]}`)
  submitDialog.visible = false

  // Update document status
  if (submitDialog.document) {
    const doc = documents.value.find(d => d.id === submitDialog.document!.id)
    if (doc) doc.status = 'Under Review'
  }
}

const approveTask = (task: WorkflowTask) => {
  approvalDialog.task = task
  approvalForm.decision = 'approved'
  approvalForm.comments = ''
  approvalDialog.visible = true
}

const rejectTask = (task: WorkflowTask) => {
  approvalDialog.task = task
  approvalForm.decision = 'rejected'
  approvalForm.comments = ''
  approvalDialog.visible = true
}

const confirmApproval = () => {
  if (approvalDialog.task) {
    const decision = approvalForm.decision === 'approved' ? 'Approved' : approvalForm.decision === 'rejected' ? 'Rejected' : 'Rework Required'
    ElMessage.success(`Task ${decision.toLowerCase()}: ${approvalDialog.task.title}`)

    // Remove from pending tasks
    const index = pendingTasks.value.findIndex(t => t.id === approvalDialog.task!.id)
    if (index !== -1) pendingTasks.value.splice(index, 1)

    // Update document status if approved
    if (approvalForm.decision === 'approved') {
      const doc = documents.value.find(d => d.id === approvalDialog.task!.documentId)
      if (doc) doc.status = 'Published'
    } else if (approvalForm.decision === 'rework') {
      const doc = documents.value.find(d => d.id === approvalDialog.task!.documentId)
      if (doc) doc.status = 'WIP'
    }
  }
  approvalDialog.visible = false
}

const syncCDE = async () => {
  isSyncing.value = true
  syncDialog.visible = true
  syncProgress.value = 0
  syncStatus.value = 'Connecting to CDE...'
  syncDetails.value = 'Authenticating'

  await new Promise(resolve => setTimeout(resolve, 1000))
  syncProgress.value = 25
  syncStatus.value = 'Fetching container structure...'
  syncDetails.value = 'Loading project hierarchy'

  await new Promise(resolve => setTimeout(resolve, 1500))
  syncProgress.value = 60
  syncStatus.value = 'Synchronizing documents...'
  syncDetails.value = 'Checking for updates'

  await new Promise(resolve => setTimeout(resolve, 1500))
  syncProgress.value = 90
  syncStatus.value = 'Updating metadata...'
  syncDetails.value = 'Processing changes'

  await new Promise(resolve => setTimeout(resolve, 1000))
  syncProgress.value = 100
  syncStatus.value = 'Sync complete!'
  syncDetails.value = 'All data synchronized'

  lastSyncTime.value = new Date().toLocaleString()

  setTimeout(() => {
    syncDialog.visible = false
    isSyncing.value = false
    ElMessage.success('CDE synchronization completed')
  }, 1000)
}

const configureConnection = () => {
  ElMessage.info('CDE connection settings')
}

const exportMetadata = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    containers: containerTree.value,
    documents: documents.value,
    stats: stats
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `cde-metadata-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Metadata exported')
}

// ==================== 数据加载 ====================
const loadData = () => {
  // Data loaded
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
.cde-link-page {
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

/* Status Card */
.status-card {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.connection-status.connected .status-indicator { background-color: #67c23a; }
.connection-status.connecting .status-indicator { background-color: #e6a23c; animation: pulse 1.5s infinite; }
.connection-status.disconnected .status-indicator { background-color: #f56c6c; }

.status-text {
  font-size: 14px;
}

.status-text span {
  display: block;
  font-size: 12px;
  color: #8c9aab;
}

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

/* Cards */
.containers-card, .documents-card, .tasks-card, .placeholder-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Container Tree */
.container-tree {
  max-height: 500px;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.tree-node .el-icon {
  color: #409eff;
}

.status-tag {
  margin-left: 8px;
  font-size: 10px;
}

.node-count {
  margin-left: auto;
  font-size: 11px;
  color: #8c9aab;
}

/* Placeholder */
.placeholder-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: #8c9aab;
}

.placeholder-card .el-icon {
  font-size: 48px;
}

.no-documents {
  padding: 40px 0;
}

/* Document Detail */
.revision-history {
  max-height: 200px;
  overflow-y: auto;
}

.revision-item {
  padding: 6px 0;
  border-bottom: 1px solid #ebeef5;
  font-size: 12px;
}

.overdue {
  color: #f56c6c;
  font-weight: 500;
}

/* Sync Dialog */
.sync-progress {
  padding: 20px;
  text-align: center;
}

.sync-status {
  margin-top: 16px;
  font-size: 14px;
  font-weight: 500;
  color: #409eff;
}

.sync-details {
  margin-top: 8px;
  font-size: 12px;
  color: #8c9aab;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-tree-node__content) {
  height: 36px;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}
</style>