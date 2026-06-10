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
        <div class="loading-tip">Semantic Model: Event / Fault / Work Order</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="semantic-model-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Semantic Model</el-breadcrumb-item>
            <el-breadcrumb-item>Event / Fault / Work Order</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Event / Fault / Work Order</h1>
        <p class="description">Define relationships between events, faults, and work orders for root cause analysis</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Model
        </el-button>
        <el-button type="primary" @click="handleAddEntity">
          <el-icon><Plus /></el-icon>
          Add Entity
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

    <!-- Relationship Graph -->
    <el-card class="graph-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Entity Relationship Graph</span>
          <div class="graph-controls">
            <el-button size="small" @click="zoomIn">
              <el-icon><ZoomIn /></el-icon>
            </el-button>
            <el-button size="small" @click="zoomOut">
              <el-icon><ZoomOut /></el-icon>
            </el-button>
            <el-button size="small" @click="resetZoom">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
      <div ref="graphChartRef" class="graph-container"></div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by title or description"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.entityType" placeholder="Entity Type" clearable style="width: 140px">
            <el-option label="Event" value="Event" />
            <el-option label="Fault" value="Fault" />
            <el-option label="Work Order" value="Work Order" />
          </el-select>
          <el-select v-model="filters.severity" placeholder="Severity" clearable style="width: 120px">
            <el-option label="Critical" value="Critical" />
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Open" value="Open" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Resolved" value="Resolved" />
            <el-option label="Closed" value="Closed" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Data Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Entity Registry ({{ filteredEntities.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchEntities" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedEntities" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column prop="title" label="Title" min-width="220" show-overflow-tooltip />
        <el-table-column prop="entityType" label="Type" width="110">
          <template #default="{ row }">
            <el-tag :type="getEntityTypeTag(row.entityType)" size="small">{{ row.entityType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="120" />
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="relatedTo" label="Related To" width="140">
          <template #default="{ row }">
            <el-popover placement="top" :width="250" trigger="hover">
              <template #reference>
                <el-tag type="info" size="small" style="cursor: pointer">
                  {{ row.relatedEntities?.length || 0 }} relations
                </el-tag>
              </template>
              <div v-for="rel in row.relatedEntities" :key="rel.id" class="relation-item">
                <strong>{{ rel.type }}:</strong> {{ rel.title }}
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="success" size="small" @click="editEntity(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteEntity(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredEntities.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Add/Edit Entity Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'add' ? 'Add Entity' : 'Edit Entity'" width="600px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Title" prop="title">
              <el-input v-model="formData.title" placeholder="Enter title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Entity Type" prop="entityType">
              <el-select v-model="formData.entityType" placeholder="Select type" style="width: 100%">
                <el-option label="Event" value="Event" />
                <el-option label="Fault" value="Fault" />
                <el-option label="Work Order" value="Work Order" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Severity" prop="severity">
              <el-select v-model="formData.severity" placeholder="Select severity" style="width: 100%">
                <el-option label="Critical" value="Critical" />
                <el-option label="High" value="High" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Low" value="Low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
                <el-option label="Open" value="Open" />
                <el-option label="In Progress" value="In Progress" />
                <el-option label="Resolved" value="Resolved" />
                <el-option label="Closed" value="Closed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Source" prop="source">
              <el-input v-model="formData.source" placeholder="e.g., BMS, SCADA, Manual" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority" prop="priority">
              <el-select v-model="formData.priority" placeholder="Select priority" style="width: 100%">
                <el-option label="P1" value="P1" />
                <el-option label="P2" value="P2" />
                <el-option label="P3" value="P3" />
                <el-option label="P4" value="P4" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Related Entities" prop="relatedIds">
              <el-select
                  v-model="formData.relatedIds"
                  multiple
                  filterable
                  placeholder="Select related entities"
                  style="width: 100%"
              >
                <el-option
                    v-for="entity in availableEntities"
                    :key="entity.id"
                    :label="`${entity.title} (${entity.entityType})`"
                    :value="entity.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save</el-button>
      </template>
    </el-dialog>

    <!-- Entity Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Entity Details - ${currentEntity?.title}`" width="700px" destroy-on-close>
      <div class="entity-details" v-if="currentEntity">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="ID">{{ currentEntity.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">
            <el-tag :type="getEntityTypeTag(currentEntity.entityType)" size="small">{{ currentEntity.entityType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Severity">
            <el-tag :type="getSeverityTag(currentEntity.severity)" size="small">{{ currentEntity.severity }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(currentEntity.status)" size="small">{{ currentEntity.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Priority">{{ currentEntity.priority || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Source">{{ currentEntity.source }}</el-descriptions-item>
          <el-descriptions-item label="Timestamp">{{ currentEntity.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Resolved At">{{ currentEntity.resolvedAt || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ currentEntity.assignedTo || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentEntity.description }}</el-descriptions-item>
          <el-descriptions-item label="Root Cause" :span="2" v-if="currentEntity.rootCause">{{ currentEntity.rootCause }}</el-descriptions-item>
        </el-descriptions>

        <!-- Related Entities -->
        <div class="related-section" v-if="currentEntity.relatedEntities?.length">
          <h4>Related Entities</h4>
          <el-table :data="currentEntity.relatedEntities" size="small" border>
            <el-table-column prop="type" label="Type" width="120">
              <template #default="{ row }">
                <el-tag :type="getEntityTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="Title" min-width="250" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Action" width="80">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="navigateToEntity(row)">View</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Timeline -->
        <div class="timeline-section">
          <h4>Timeline</h4>
          <el-timeline>
            <el-timeline-item
                v-for="event in currentEntity.timeline"
                :key="event.id"
                :timestamp="event.timestamp"
                :type="event.type"
                placement="top"
            >
              {{ event.description }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editEntity(currentEntity)">Edit</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete "{{ deleteTarget?.title }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  ZoomIn, ZoomOut, Connection, Edit, Delete
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading semantic model...',
  'Building relationship graph...',
  'Almost ready...'
]

// ==================== Chart References ====================
const graphChartRef = ref<HTMLElement>()
let graphChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const detailsDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const currentEntity = ref<any>(null)
const deleteTarget = ref<any>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)

const filters = reactive({
  keyword: '',
  entityType: '',
  severity: '',
  status: ''
})

const formData = reactive({
  id: null,
  title: '',
  entityType: 'Event',
  severity: 'Medium',
  status: 'Open',
  source: '',
  priority: 'P3',
  description: '',
  relatedIds: [] as string[]
})

const formRules = {
  title: [{ required: true, message: 'Please enter title', trigger: 'blur' }],
  entityType: [{ required: true, message: 'Please select entity type', trigger: 'change' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Events', value: 1248, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'events' },
  { title: 'Active Faults', value: 36, trend: -8, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'faults' },
  { title: 'Open Work Orders', value: 48, trend: 5, icon: 'Clock', bgColor: '#e6a23c', key: 'workOrders' },
  { title: 'Avg Resolution Time', value: '4.2h', trend: -12, icon: 'Checked', bgColor: '#67c23a', key: 'resolution' }
])

const entities = ref([
  {
    id: 'EVT-001',
    title: 'Chiller-01 High Temperature Alert',
    entityType: 'Event',
    severity: 'High',
    status: 'Resolved',
    source: 'BMS',
    priority: 'P2',
    timestamp: '2024-01-20 08:30:00',
    resolvedAt: '2024-01-20 10:15:00',
    assignedTo: 'John Smith',
    description: 'Chiller-01 supply temperature exceeded threshold of 8°C, reaching 9.2°C.',
    rootCause: 'Condenser fouling causing reduced heat transfer efficiency.',
    relatedEntities: [
      { id: 'FLT-001', type: 'Fault', title: 'Chiller-01 Performance Degradation', status: 'Resolved' },
      { id: 'WO-001', type: 'Work Order', title: 'Chiller-01 Tube Cleaning', status: 'Completed' }
    ],
    timeline: [
      { id: 1, timestamp: '2024-01-20 08:30:00', description: 'Alert triggered by BMS', type: 'danger' },
      { id: 2, timestamp: '2024-01-20 08:35:00', description: 'Alert acknowledged by John Smith', type: 'primary' },
      { id: 3, timestamp: '2024-01-20 09:00:00', description: 'Work order created for tube cleaning', type: 'primary' },
      { id: 4, timestamp: '2024-01-20 10:15:00', description: 'Alert resolved after maintenance', type: 'success' }
    ]
  },
  {
    id: 'FLT-001',
    title: 'Chiller-01 Performance Degradation',
    entityType: 'Fault',
    severity: 'High',
    status: 'Resolved',
    source: 'AI Analytics',
    priority: 'P2',
    timestamp: '2024-01-18 14:00:00',
    resolvedAt: '2024-01-20 10:15:00',
    assignedTo: 'David Wang',
    description: 'Chiller-01 efficiency dropped from 0.85 to 0.72 kW/ton over 7 days.',
    rootCause: 'Condenser fouling due to poor water quality.',
    relatedEntities: [
      { id: 'EVT-001', type: 'Event', title: 'Chiller-01 High Temperature Alert', status: 'Resolved' },
      { id: 'WO-001', type: 'Work Order', title: 'Chiller-01 Tube Cleaning', status: 'Completed' }
    ],
    timeline: [
      { id: 1, timestamp: '2024-01-18 14:00:00', description: 'AI model detected efficiency degradation', type: 'warning' },
      { id: 2, timestamp: '2024-01-18 15:00:00', description: 'Fault investigation started', type: 'primary' },
      { id: 3, timestamp: '2024-01-20 09:00:00', description: 'Root cause identified', type: 'primary' },
      { id: 4, timestamp: '2024-01-20 10:15:00', description: 'Fault resolved after tube cleaning', type: 'success' }
    ]
  },
  {
    id: 'WO-001',
    title: 'Chiller-01 Tube Cleaning',
    entityType: 'Work Order',
    severity: 'Medium',
    status: 'Completed',
    source: 'CMMS',
    priority: 'P2',
    timestamp: '2024-01-20 09:00:00',
    resolvedAt: '2024-01-20 10:00:00',
    assignedTo: 'Mike Johnson',
    description: 'Clean condenser tubes to restore heat transfer efficiency.',
    relatedEntities: [
      { id: 'EVT-001', type: 'Event', title: 'Chiller-01 High Temperature Alert', status: 'Resolved' },
      { id: 'FLT-001', type: 'Fault', title: 'Chiller-01 Performance Degradation', status: 'Resolved' }
    ],
    timeline: [
      { id: 1, timestamp: '2024-01-20 09:00:00', description: 'Work order created', type: 'primary' },
      { id: 2, timestamp: '2024-01-20 09:15:00', description: 'Work order assigned to Mike Johnson', type: 'primary' },
      { id: 3, timestamp: '2024-01-20 09:30:00', description: 'Tube cleaning in progress', type: 'primary' },
      { id: 4, timestamp: '2024-01-20 10:00:00', description: 'Work order completed', type: 'success' }
    ]
  },
  {
    id: 'EVT-002',
    title: 'AHU-01 Filter Clogging Alert',
    entityType: 'Event',
    severity: 'Medium',
    status: 'In Progress',
    source: 'BMS',
    priority: 'P3',
    timestamp: '2024-01-19 11:30:00',
    assignedTo: 'Lisa Zhang',
    description: 'AHU-01 filter pressure drop exceeded 250 Pa threshold.',
    relatedEntities: [
      { id: 'WO-002', type: 'Work Order', title: 'AHU-01 Filter Replacement', status: 'In Progress' }
    ],
    timeline: [
      { id: 1, timestamp: '2024-01-19 11:30:00', description: 'Alert triggered', type: 'warning' },
      { id: 2, timestamp: '2024-01-19 11:45:00', description: 'Alert acknowledged', type: 'primary' },
      { id: 3, timestamp: '2024-01-19 12:00:00', description: 'Work order created', type: 'primary' }
    ]
  },
  {
    id: 'WO-002',
    title: 'AHU-01 Filter Replacement',
    entityType: 'Work Order',
    severity: 'Low',
    status: 'In Progress',
    source: 'CMMS',
    priority: 'P3',
    timestamp: '2024-01-19 12:00:00',
    assignedTo: 'Mike Johnson',
    description: 'Replace clogged air filters in AHU-01.',
    relatedEntities: [
      { id: 'EVT-002', type: 'Event', title: 'AHU-01 Filter Clogging Alert', status: 'In Progress' }
    ],
    timeline: [
      { id: 1, timestamp: '2024-01-19 12:00:00', description: 'Work order created', type: 'primary' },
      { id: 2, timestamp: '2024-01-19 13:00:00', description: 'Parts ordered', type: 'primary' }
    ]
  },
  {
    id: 'EVT-003',
    title: 'UPS-01 Battery Health Warning',
    entityType: 'Event',
    severity: 'Critical',
    status: 'Open',
    source: 'SCADA',
    priority: 'P1',
    timestamp: '2024-01-20 06:00:00',
    assignedTo: 'Tom Harris',
    description: 'UPS-01 battery capacity dropped below 60%. Replacement required.',
    relatedEntities: [
      { id: 'FLT-002', type: 'Fault', title: 'UPS-01 Battery Degradation', status: 'Open' }
    ],
    timeline: [
      { id: 1, timestamp: '2024-01-20 06:00:00', description: 'Battery health warning triggered', type: 'danger' },
      { id: 2, timestamp: '2024-01-20 06:30:00', description: 'Alert acknowledged', type: 'primary' }
    ]
  },
  {
    id: 'FLT-002',
    title: 'UPS-01 Battery Degradation',
    entityType: 'Fault',
    severity: 'Critical',
    status: 'Open',
    source: 'AI Analytics',
    priority: 'P1',
    timestamp: '2024-01-19 00:00:00',
    assignedTo: 'Tom Harris',
    description: 'UPS-01 battery capacity has been declining at 2% per month.',
    relatedEntities: [
      { id: 'EVT-003', type: 'Event', title: 'UPS-01 Battery Health Warning', status: 'Open' },
      { id: 'WO-003', type: 'Work Order', title: 'UPS-01 Battery Replacement', status: 'Pending' }
    ],
    timeline: [
      { id: 1, timestamp: '2024-01-19 00:00:00', description: 'Fault detected by AI model', type: 'warning' },
      { id: 2, timestamp: '2024-01-19 08:00:00', description: 'Fault investigation started', type: 'primary' }
    ]
  },
  {
    id: 'WO-003',
    title: 'UPS-01 Battery Replacement',
    entityType: 'Work Order',
    severity: 'Critical',
    status: 'Pending',
    source: 'CMMS',
    priority: 'P1',
    timestamp: '2024-01-20 07:00:00',
    assignedTo: '',
    description: 'Replace UPS-01 batteries with new lithium-ion units.',
    relatedEntities: [
      { id: 'EVT-003', type: 'Event', title: 'UPS-01 Battery Health Warning', status: 'Open' },
      { id: 'FLT-002', type: 'Fault', title: 'UPS-01 Battery Degradation', status: 'Open' }
    ],
    timeline: [
      { id: 1, timestamp: '2024-01-20 07:00:00', description: 'Work order created', type: 'primary' },
      { id: 2, timestamp: '2024-01-20 07:30:00', description: 'Vendor quote requested', type: 'primary' }
    ]
  }
])

// ==================== Computed ====================
const filteredEntities = computed(() => {
  let filtered = [...entities.value]

  if (filters.keyword) {
    filtered = filtered.filter(e =>
        e.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        e.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.entityType) {
    filtered = filtered.filter(e => e.entityType === filters.entityType)
  }

  if (filters.severity) {
    filtered = filtered.filter(e => e.severity === filters.severity)
  }

  if (filters.status) {
    filtered = filtered.filter(e => e.status === filters.status)
  }

  return filtered
})

const paginatedEntities = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEntities.value.slice(start, end)
})

const availableEntities = computed(() => {
  return entities.value.filter(e => e.id !== formData.id)
})

// ==================== Helper Methods ====================
const getEntityTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Event': 'warning',
    'Fault': 'danger',
    'Work Order': 'success'
  }
  return map[type] || 'info'
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[severity] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'Open': 'danger',
    'In Progress': 'warning',
    'Resolved': 'success',
    'Completed': 'success',
    'Closed': 'info',
    'Pending': 'info'
  }
  return map[status] || 'info'
}

// ==================== Chart Initialization ====================
const initGraphChart = () => {
  if (!graphChartRef.value) return
  if (graphChart) graphChart.dispose()

  graphChart = echarts.init(graphChartRef.value)

  // Build graph data
  const nodes: any[] = []
  const links: any[] = []
  const nodeMap = new Map()

  entities.value.forEach(entity => {
    nodes.push({
      id: entity.id,
      name: entity.title.length > 20 ? entity.title.substring(0, 20) + '...' : entity.title,
      category: entity.entityType,
      symbolSize: entity.entityType === 'Event' ? 30 : entity.entityType === 'Fault' ? 35 : 40,
      itemStyle: {
        color: entity.entityType === 'Event' ? '#e6a23c' : entity.entityType === 'Fault' ? '#f56c6c' : '#67c23a'
      }
    })
    nodeMap.set(entity.id, entity)

    if (entity.relatedEntities) {
      entity.relatedEntities.forEach(rel => {
        links.push({
          source: entity.id,
          target: rel.id,
          lineStyle: { color: '#909399', curveness: 0.3 }
        })
      })
    }
  })

  const categories = [
    { name: 'Event', itemStyle: { color: '#e6a23c' } },
    { name: 'Fault', itemStyle: { color: '#f56c6c' } },
    { name: 'Work Order', itemStyle: { color: '#67c23a' } }
  ]

  const option: echarts.EChartsOption = {
    title: { show: false },
    tooltip: { trigger: 'item', formatter: (params: any) => {
        if (params.dataType === 'node') {
          const entity = nodeMap.get(params.data.id)
          return `<strong>${entity.title}</strong><br/>Type: ${entity.entityType}<br/>Status: ${entity.status}<br/>Severity: ${entity.severity}`
        }
        return ''
      }},
    series: [{
      type: 'graph',
      layout: 'force',
      force: {
        repulsion: 500,
        edgeLength: 150,
        gravity: 0.1,
        friction: 0.1
      },
      data: nodes,
      links: links,
      categories: categories,
      roam: true,
      draggable: true,
      focusNodeAdjacency: true,
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [0, 8],
      lineStyle: { color: '#c0c4cc', width: 2, curveness: 0.3 },
      label: { show: true, position: 'bottom', fontSize: 11 },
      emphasis: { scale: true, label: { show: true } }
    }]
  }

  graphChart.setOption(option)
  window.addEventListener('resize', () => graphChart?.resize())
}

const zoomIn = () => {
  if (graphChart) {
    const option = graphChart.getOption()
    // Zoom functionality handled by echarts built-in
  }
}

const zoomOut = () => {
  if (graphChart) {
    // Zoom functionality handled by echarts built-in
  }
}

const resetZoom = () => {
  if (graphChart) {
    graphChart.dispatchAction({ type: 'restore' })
  }
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.entityType = ''
  filters.severity = ''
  filters.status = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredEntities.value.length} entities...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const handleAddEntity = () => {
  dialogMode.value = 'add'
  Object.assign(formData, {
    id: null,
    title: '',
    entityType: 'Event',
    severity: 'Medium',
    status: 'Open',
    source: '',
    priority: 'P3',
    description: '',
    relatedIds: []
  })
  dialogVisible.value = true
}

const fetchEntities = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const viewDetails = (entity: any) => {
  currentEntity.value = entity
  detailsDialogVisible.value = true
}

const editEntity = (entity: any) => {
  dialogMode.value = 'edit'
  Object.assign(formData, {
    id: entity.id,
    title: entity.title,
    entityType: entity.entityType,
    severity: entity.severity,
    status: entity.status,
    source: entity.source,
    priority: entity.priority,
    description: entity.description,
    relatedIds: entity.relatedEntities?.map((e: any) => e.id) || []
  })
  dialogVisible.value = true
}

const deleteEntity = (entity: any) => {
  deleteTarget.value = entity
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = entities.value.findIndex(e => e.id === deleteTarget.value!.id)
    if (index !== -1) {
      entities.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
      initGraphChart()
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const navigateToEntity = (entity: any) => {
  const found = entities.value.find(e => e.id === entity.id)
  if (found) {
    viewDetails(found)
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'add') {
        const newEntity = {
          id: `ENT-${String(entities.value.length + 1).padStart(3, '0')}`,
          title: formData.title,
          entityType: formData.entityType,
          severity: formData.severity,
          status: formData.status,
          source: formData.source,
          priority: formData.priority,
          timestamp: new Date().toLocaleString(),
          description: formData.description,
          relatedEntities: formData.relatedIds.map(id => {
            const found = entities.value.find(e => e.id === id)
            return found ? { id: found.id, type: found.entityType, title: found.title, status: found.status } : null
          }).filter(Boolean),
          timeline: [{ id: 1, timestamp: new Date().toLocaleString(), description: 'Entity created', type: 'primary' }]
        }
        entities.value.unshift(newEntity)
        ElMessage.success('Entity added successfully')
      } else {
        const index = entities.value.findIndex(e => e.id === formData.id)
        if (index !== -1) {
          entities.value[index] = {
            ...entities.value[index],
            title: formData.title,
            entityType: formData.entityType,
            severity: formData.severity,
            status: formData.status,
            source: formData.source,
            priority: formData.priority,
            description: formData.description,
            relatedEntities: formData.relatedIds.map(id => {
              const found = entities.value.find(e => e.id === id)
              return found ? { id: found.id, type: found.entityType, title: found.title, status: found.status } : null
            }).filter(Boolean)
          }
          ElMessage.success('Entity updated successfully')
        }
      }
      dialogVisible.value = false
      formRef.value?.resetFields()
      initGraphChart()
    }
  })
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initGraphChart()
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
      fetchEntities()
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
.semantic-model-page {
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

.graph-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .graph-controls {
      display: flex;
      gap: 4px;
    }
  }
}

.graph-container {
  width: 100%;
  height: 450px;
  background: #fff;
  border-radius: 8px;
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

.entity-details {
  .related-section, .timeline-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }
}

.relation-item {
  padding: 4px 0;
  font-size: 13px;

  strong {
    color: #303133;
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

:deep(.el-timeline-item__wrapper) {
  padding-left: 28px;
}
</style>