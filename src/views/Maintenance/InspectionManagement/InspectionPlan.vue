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
          <span class="loading-title">Inspection Plan</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Inspection Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="inspection-plan-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          Inspection Plan
        </h1>
        <div class="page-subtitle">Manage and track equipment inspection schedules</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> Create Plan
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalPlans }}</div>
          <div class="stat-label">Total Plans</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.activePlans }}</div>
          <div class="stat-label">Active Plans</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pendingToday }}</div>
          <div class="stat-label">Due Today</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Check /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.completionRate }}<span class="unit">%</span></div>
          <div class="stat-label">Completion Rate</div>
        </div>
      </div>
    </div>

    <!-- Tab View -->
    <div class="main-tabs">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="All Plans" name="all">
          <template #label>
            <span><el-icon><List /></el-icon> All Plans</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Due Today" name="today">
          <template #label>
            <span><el-icon><Clock /></el-icon> Due Today</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Overdue" name="overdue">
          <template #label>
            <span><el-icon><WarningFilled /></el-icon> Overdue</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Completed" name="completed">
          <template #label>
            <span><el-icon><CircleCheck /></el-icon> Completed</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by plan name or equipment..."
            style="width: 260px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="priorityFilter" placeholder="Priority" clearable style="width: 120px">
          <el-option label="Critical" value="critical" />
          <el-option label="High" value="high" />
          <el-option label="Medium" value="medium" />
          <el-option label="Low" value="low" />
        </el-select>
        <el-select v-model="typeFilter" placeholder="Type" clearable style="width: 140px">
          <el-option label="Daily" value="daily" />
          <el-option label="Weekly" value="weekly" />
          <el-option label="Monthly" value="monthly" />
          <el-option label="Quarterly" value="quarterly" />
          <el-option label="Yearly" value="yearly" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Today: {{ currentDate }}</span>
      </div>
    </div>

    <!-- Inspection Plans Table -->
    <div class="table-container">
      <el-table :data="filteredPlans" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="planCode" label="Plan Code" width="120" />
        <el-table-column prop="planName" label="Plan Name" min-width="180" />
        <el-table-column prop="equipment" label="Equipment" min-width="150" />
        <el-table-column prop="equipmentType" label="Equipment Type" width="130" />
        <el-table-column prop="frequency" label="Frequency" width="100">
          <template #default="{ row }">
            <el-tag :type="getFrequencyTagType(row.frequency)" size="small">
              {{ getFrequencyText(row.frequency) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ row.priority.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="nextDueDate" label="Next Due Date" width="120" />
        <el-table-column prop="assignedTo" label="Assigned To" width="120" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewPlan(row)">
              View
            </el-button>
            <el-button type="primary" link size="small" @click="editPlan(row)">
              Edit
            </el-button>
            <el-button type="danger" link size="small" @click="deletePlan(row)">
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Create/Edit Plan Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="650px">
      <el-form :model="planForm" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Plan Code" prop="planCode">
              <el-input v-model="planForm.planCode" placeholder="Auto-generated" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Plan Name" prop="planName">
              <el-input v-model="planForm.planName" placeholder="Enter plan name" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Equipment" prop="equipment">
              <el-select v-model="planForm.equipment" placeholder="Select equipment" filterable style="width: 100%">
                <el-option
                    v-for="item in equipmentList"
                    :key="item.id"
                    :label="item.name"
                    :value="item.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Equipment Type" prop="equipmentType">
              <el-select v-model="planForm.equipmentType" placeholder="Select type" style="width: 100%">
                <el-option label="UPS" value="UPS" />
                <el-option label="CRAC" value="CRAC" />
                <el-option label="PDU" value="PDU" />
                <el-option label="Chiller" value="Chiller" />
                <el-option label="Generator" value="Generator" />
                <el-option label="Transformer" value="Transformer" />
                <el-option label="Switchboard" value="Switchboard" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Frequency" prop="frequency">
              <el-select v-model="planForm.frequency" placeholder="Select frequency" style="width: 100%">
                <el-option label="Daily" value="daily" />
                <el-option label="Weekly" value="weekly" />
                <el-option label="Monthly" value="monthly" />
                <el-option label="Quarterly" value="quarterly" />
                <el-option label="Yearly" value="yearly" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority" prop="priority">
              <el-select v-model="planForm.priority" placeholder="Select priority" style="width: 100%">
                <el-option label="Critical" value="critical" />
                <el-option label="High" value="high" />
                <el-option label="Medium" value="medium" />
                <el-option label="Low" value="low" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Start Date" prop="startDate">
              <el-date-picker
                  v-model="planForm.startDate"
                  type="date"
                  placeholder="Select start date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Next Due Date" prop="nextDueDate">
              <el-date-picker
                  v-model="planForm.nextDueDate"
                  type="date"
                  placeholder="Select due date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Assigned To" prop="assignedTo">
              <el-select v-model="planForm.assignedTo" placeholder="Assign to engineer" filterable style="width: 100%">
                <el-option
                    v-for="eng in engineers"
                    :key="eng.id"
                    :label="eng.name"
                    :value="eng.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Estimated Hours" prop="estimatedHours">
              <el-input-number v-model="planForm.estimatedHours" :min="0.5" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Checklist Items" prop="checklist">
          <el-input
              v-model="planForm.checklistInput"
              type="textarea"
              :rows="3"
              placeholder="Enter checklist items (one per line)"
          />
          <div class="checklist-tags" v-if="planForm.checklist.length > 0">
            <el-tag
                v-for="(item, idx) in planForm.checklist"
                :key="idx"
                closable
                @close="removeChecklistItem(idx)"
                class="checklist-tag"
            >
              {{ item }}
            </el-tag>
          </div>
        </el-form-item>

        <el-form-item label="Instructions" prop="instructions">
          <el-input
              v-model="planForm.instructions"
              type="textarea"
              :rows="2"
              placeholder="Special instructions for inspection..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePlan">Save</el-button>
      </template>
    </el-dialog>

    <!-- View Plan Dialog -->
    <el-dialog v-model="viewDialogVisible" title="Inspection Plan Details" width="700px">
      <div class="plan-detail" v-if="selectedPlan">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Plan Code">{{ selectedPlan.planCode }}</el-descriptions-item>
          <el-descriptions-item label="Plan Name">{{ selectedPlan.planName }}</el-descriptions-item>
          <el-descriptions-item label="Equipment">{{ selectedPlan.equipment }}</el-descriptions-item>
          <el-descriptions-item label="Equipment Type">{{ selectedPlan.equipmentType }}</el-descriptions-item>
          <el-descriptions-item label="Frequency">{{ getFrequencyText(selectedPlan.frequency) }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(selectedPlan.priority)" size="small">
              {{ selectedPlan.priority.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Start Date">{{ selectedPlan.startDate }}</el-descriptions-item>
          <el-descriptions-item label="Next Due Date">{{ selectedPlan.nextDueDate }}</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ selectedPlan.assignedTo }}</el-descriptions-item>
          <el-descriptions-item label="Estimated Hours">{{ selectedPlan.estimatedHours }} hours</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedPlan.status)" size="small">
              {{ getStatusText(selectedPlan.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Last Inspection">{{ selectedPlan.lastInspection || 'Not yet' }}</el-descriptions-item>
          <el-descriptions-item label="Checklist" :span="2">
            <ul class="checklist-list">
              <li v-for="(item, idx) in selectedPlan.checklist" :key="idx">✓ {{ item }}</li>
            </ul>
          </el-descriptions-item>
          <el-descriptions-item label="Instructions" :span="2">{{ selectedPlan.instructions || 'No special instructions' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="startInspection(selectedPlan)" v-if="selectedPlan?.status === 'pending'">
          Start Inspection
        </el-button>
      </template>
    </el-dialog>

    <!-- Complete Inspection Dialog -->
    <el-dialog v-model="completeDialogVisible" title="Complete Inspection" width="550px">
      <div class="complete-content">
        <p><strong>Plan:</strong> {{ completingPlan?.planName }}</p>
        <p><strong>Equipment:</strong> {{ completingPlan?.equipment }}</p>
        <el-divider />
        <el-form :model="completeForm" label-width="120px">
          <el-form-item label="Completion Date">
            <el-date-picker
                v-model="completeForm.completionDate"
                type="date"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="Actual Hours">
            <el-input-number v-model="completeForm.actualHours" :min="0.5" :step="0.5" style="width: 100%" />
          </el-form-item>
          <el-form-item label="Notes">
            <el-input v-model="completeForm.notes" type="textarea" :rows="3" placeholder="Inspection notes..." />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="completeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmComplete">Complete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Plus, Download, Refresh, List, Clock, WarningFilled,
  CircleCheck, Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading inspection plans...',
  'Loading equipment data...',
  'Initializing scheduler...',
  'Almost ready...'
]

// ==================== Types ====================
interface InspectionPlan {
  id: number
  planCode: string
  planName: string
  equipment: string
  equipmentType: string
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly'
  priority: 'critical' | 'high' | 'medium' | 'low'
  startDate: string
  nextDueDate: string
  lastInspection: string | null
  assignedTo: string
  assignedToId: number
  status: 'pending' | 'in-progress' | 'completed' | 'overdue'
  estimatedHours: number
  actualHours: number | null
  checklist: string[]
  instructions: string
  createdAt: string
}

interface Equipment {
  id: number
  name: string
  type: string
  location: string
}

interface Engineer {
  id: number
  name: string
  email: string
  role: string
}

// ==================== Mock Data ====================
const equipmentList = ref<Equipment[]>([
  { id: 1, name: 'UPS-01', type: 'UPS', location: 'Server Room A' },
  { id: 2, name: 'UPS-02', type: 'UPS', location: 'Server Room B' },
  { id: 3, name: 'UPS-03', type: 'UPS', location: 'Server Room C' },
  { id: 4, name: 'CRAC-01', type: 'CRAC', location: 'Data Center' },
  { id: 5, name: 'CRAC-02', type: 'CRAC', location: 'Data Center' },
  { id: 6, name: 'PDU-A01', type: 'PDU', location: 'Server Row A' },
  { id: 7, name: 'PDU-B01', type: 'PDU', location: 'Server Row B' },
  { id: 8, name: 'Chiller-01', type: 'Chiller', location: 'Chiller Plant' },
  { id: 9, name: 'Generator-01', type: 'Generator', location: 'Generator Room' },
  { id: 10, name: 'Transformer-01', type: 'Transformer', location: 'Electrical Room' }
])

const engineers = ref<Engineer[]>([
  { id: 1, name: 'John Chen', email: 'john.chen@ibms.com', role: 'Senior Technician' },
  { id: 2, name: 'Sarah Wong', email: 'sarah.wong@ibms.com', role: 'HVAC Specialist' },
  { id: 3, name: 'Mike Lim', email: 'mike.lim@ibms.com', role: 'Electrical Engineer' },
  { id: 4, name: 'David Tan', email: 'david.tan@ibms.com', role: 'General Technician' },
  { id: 5, name: 'Lisa Ng', email: 'lisa.ng@ibms.com', role: 'Network Specialist' }
])

const inspectionPlans = ref<InspectionPlan[]>([
  { id: 1, planCode: 'INSP-001', planName: 'UPS Battery Health Check', equipment: 'UPS-01', equipmentType: 'UPS', frequency: 'monthly', priority: 'critical', startDate: '2024-01-01', nextDueDate: '2024-06-15', lastInspection: '2024-05-15', assignedTo: 'John Chen', assignedToId: 1, status: 'pending', estimatedHours: 2, actualHours: null, checklist: ['Check battery voltage', 'Inspect terminal connections', 'Test battery capacity', 'Record temperature readings'], instructions: 'Use thermal imaging camera for hot spot detection', createdAt: '2024-01-01' },
  { id: 2, planCode: 'INSP-002', planName: 'CRAC Filter Replacement', equipment: 'CRAC-01', equipmentType: 'CRAC', frequency: 'monthly', priority: 'high', startDate: '2024-01-01', nextDueDate: '2024-06-10', lastInspection: '2024-05-10', assignedTo: 'Sarah Wong', assignedToId: 2, status: 'pending', estimatedHours: 1.5, actualHours: null, checklist: ['Check filter condition', 'Replace if dirty', 'Record pressure drop', 'Clean filter housing'], instructions: 'Use genuine filters only', createdAt: '2024-01-01' },
  { id: 3, planCode: 'INSP-003', planName: 'PDU Load Monitoring', equipment: 'PDU-A01', equipmentType: 'PDU', frequency: 'weekly', priority: 'medium', startDate: '2024-01-01', nextDueDate: '2024-06-12', lastInspection: '2024-06-05', assignedTo: 'Mike Lim', assignedToId: 3, status: 'in-progress', estimatedHours: 1, actualHours: null, checklist: ['Check load percentage', 'Verify phase balance', 'Record current readings', 'Check for alerts'], instructions: 'Compare with baseline readings', createdAt: '2024-01-01' },
  { id: 4, planCode: 'INSP-004', planName: 'Chiller Performance Test', equipment: 'Chiller-01', equipmentType: 'Chiller', frequency: 'quarterly', priority: 'critical', startDate: '2024-01-01', nextDueDate: '2024-06-20', lastInspection: '2024-03-20', assignedTo: 'Sarah Wong', assignedToId: 2, status: 'pending', estimatedHours: 3, actualHours: null, checklist: ['Check refrigerant levels', 'Test compressor operation', 'Verify water flow', 'Record temperature differential'], instructions: 'Coordinate with facility team', createdAt: '2024-01-01' },
  { id: 5, planCode: 'INSP-005', planName: 'Generator Weekly Test', equipment: 'Generator-01', equipmentType: 'Generator', frequency: 'weekly', priority: 'high', startDate: '2024-01-01', nextDueDate: '2024-06-11', lastInspection: '2024-06-04', assignedTo: 'Mike Lim', assignedToId: 3, status: 'completed', estimatedHours: 1, actualHours: 0.75, checklist: ['Start generator', 'Check fuel level', 'Monitor voltage output', 'Log runtime'], instructions: 'Test under load for 30 minutes', createdAt: '2024-01-01' },
  { id: 6, planCode: 'INSP-006', planName: 'Transformer Oil Analysis', equipment: 'Transformer-01', equipmentType: 'Transformer', frequency: 'yearly', priority: 'medium', startDate: '2024-01-01', nextDueDate: '2024-07-01', lastInspection: '2023-07-01', assignedTo: 'David Tan', assignedToId: 4, status: 'pending', estimatedHours: 2, actualHours: null, checklist: ['Collect oil sample', 'Check oil level', 'Inspect for leaks', 'Record temperature'], instructions: 'Send sample to lab for DGA', createdAt: '2024-01-01' },
  { id: 7, planCode: 'INSP-007', planName: 'Network Switch Health', equipment: 'Switch-01', equipmentType: 'Network', frequency: 'daily', priority: 'high', startDate: '2024-01-01', nextDueDate: '2024-06-13', lastInspection: '2024-06-06', assignedTo: 'Lisa Ng', assignedToId: 5, status: 'pending', estimatedHours: 0.5, actualHours: null, checklist: ['Check port status', 'Verify power supply', 'Check fan operation', 'Review error logs'], instructions: 'Check for abnormal traffic patterns', createdAt: '2024-01-01' },
  { id: 8, planCode: 'INSP-008', planName: 'Cooling Tower Inspection', equipment: 'CoolingTower-01', equipmentType: 'HVAC', frequency: 'monthly', priority: 'high', startDate: '2024-01-01', nextDueDate: '2024-06-08', lastInspection: '2024-05-08', assignedTo: 'Sarah Wong', assignedToId: 2, status: 'overdue', estimatedHours: 2.5, actualHours: null, checklist: ['Check water level', 'Inspect fan blades', 'Clean strainers', 'Test chemical dosing'], instructions: 'Check for algae growth', createdAt: '2024-01-01' }
])

// ==================== State ====================
const activeTab = ref('all')
const searchText = ref('')
const priorityFilter = ref('')
const typeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const completeDialogVisible = ref(false)
const dialogTitle = ref('Create Inspection Plan')
const selectedPlan = ref<InspectionPlan | null>(null)
const completingPlan = ref<InspectionPlan | null>(null)
const formRef = ref()

const planForm = ref({
  id: null as number | null,
  planCode: '',
  planName: '',
  equipment: '',
  equipmentType: '',
  frequency: 'monthly' as 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly',
  priority: 'medium' as 'critical' | 'high' | 'medium' | 'low',
  startDate: '',
  nextDueDate: '',
  assignedTo: '',
  estimatedHours: 1,
  checklistInput: '',
  checklist: [] as string[],
  instructions: ''
})

const completeForm = ref({
  completionDate: '',
  actualHours: 0,
  notes: ''
})

const formRules = {
  planName: [{ required: true, message: 'Please enter plan name', trigger: 'blur' }],
  equipment: [{ required: true, message: 'Please select equipment', trigger: 'change' }],
  frequency: [{ required: true, message: 'Please select frequency', trigger: 'change' }],
  priority: [{ required: true, message: 'Please select priority', trigger: 'change' }],
  nextDueDate: [{ required: true, message: 'Please select due date', trigger: 'change' }],
  assignedTo: [{ required: true, message: 'Please assign to engineer', trigger: 'change' }]
}

// ==================== Computed ====================
const currentDate = computed(() => {
  return new Date().toLocaleDateString()
})

const stats = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  return {
    totalPlans: inspectionPlans.value.length,
    activePlans: inspectionPlans.value.filter(p => p.status === 'pending' || p.status === 'in-progress').length,
    pendingToday: inspectionPlans.value.filter(p => p.nextDueDate === today && p.status !== 'completed').length,
    completionRate: Math.round((inspectionPlans.value.filter(p => p.status === 'completed').length / inspectionPlans.value.length) * 100)
  }
})

const filteredPlans = computed(() => {
  let filtered = [...inspectionPlans.value]

  // Filter by tab
  if (activeTab.value === 'today') {
    const today = new Date().toISOString().slice(0, 10)
    filtered = filtered.filter(p => p.nextDueDate === today && p.status !== 'completed')
  } else if (activeTab.value === 'overdue') {
    const today = new Date().toISOString().slice(0, 10)
    filtered = filtered.filter(p => p.nextDueDate < today && p.status !== 'completed')
  } else if (activeTab.value === 'completed') {
    filtered = filtered.filter(p => p.status === 'completed')
  }

  // Search filter
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(p =>
        p.planName.toLowerCase().includes(search) ||
        p.equipment.toLowerCase().includes(search) ||
        p.planCode.toLowerCase().includes(search)
    )
  }

  // Priority filter
  if (priorityFilter.value) {
    filtered = filtered.filter(p => p.priority === priorityFilter.value)
  }

  // Type filter
  if (typeFilter.value) {
    filtered = filtered.filter(p => p.frequency === typeFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredPlans.value.length)

const paginatedPlans = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPlans.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getFrequencyText = (frequency: string) => {
  const map: Record<string, string> = {
    daily: 'Daily', weekly: 'Weekly', monthly: 'Monthly', quarterly: 'Quarterly', yearly: 'Yearly'
  }
  return map[frequency] || frequency
}

const getFrequencyTagType = (frequency: string) => {
  const map: Record<string, string> = {
    daily: 'info', weekly: 'success', monthly: 'primary', quarterly: 'warning', yearly: 'danger'
  }
  return map[frequency] || ''
}

const getPriorityTagType = (priority: string) => {
  const map: Record<string, string> = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: 'Pending', 'in-progress': 'In Progress', completed: 'Completed', overdue: 'Overdue'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    pending: 'warning', 'in-progress': 'primary', completed: 'success', overdue: 'danger'
  }
  return map[status] || ''
}

const generatePlanCode = () => {
  const year = new Date().getFullYear()
  const count = inspectionPlans.value.length + 1
  return `INSP-${year}-${String(count).padStart(3, '0')}`
}

const removeChecklistItem = (index: number) => {
  planForm.value.checklist.splice(index, 1)
}

// ==================== CRUD Methods ====================
const openAddDialog = () => {
  dialogTitle.value = 'Create Inspection Plan'
  planForm.value = {
    id: null,
    planCode: generatePlanCode(),
    planName: '',
    equipment: '',
    equipmentType: '',
    frequency: 'monthly',
    priority: 'medium',
    startDate: new Date().toISOString().slice(0, 10),
    nextDueDate: '',
    assignedTo: '',
    estimatedHours: 1,
    checklistInput: '',
    checklist: [],
    instructions: ''
  }
  dialogVisible.value = true
}

const editPlan = (plan: InspectionPlan) => {
  dialogTitle.value = 'Edit Inspection Plan'
  planForm.value = {
    id: plan.id,
    planCode: plan.planCode,
    planName: plan.planName,
    equipment: plan.equipment,
    equipmentType: plan.equipmentType,
    frequency: plan.frequency,
    priority: plan.priority,
    startDate: plan.startDate,
    nextDueDate: plan.nextDueDate,
    assignedTo: plan.assignedTo,
    estimatedHours: plan.estimatedHours,
    checklistInput: '',
    checklist: [...plan.checklist],
    instructions: plan.instructions
  }
  dialogVisible.value = true
}

const viewPlan = (plan: InspectionPlan) => {
  selectedPlan.value = plan
  viewDialogVisible.value = true
}

const deletePlan = (plan: InspectionPlan) => {
  ElMessageBox.confirm(
      `Delete inspection plan "${plan.planName}"?`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = inspectionPlans.value.findIndex(p => p.id === plan.id)
    if (index !== -1) {
      inspectionPlans.value.splice(index, 1)
      ElMessage.success('Plan deleted')
    }
  }).catch(() => {})
}

const savePlan = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    // Process checklist from input
    if (planForm.value.checklistInput) {
      const items = planForm.value.checklistInput.split('\n').filter(item => item.trim())
      planForm.value.checklist = [...planForm.value.checklist, ...items]
    }

    const equipment = equipmentList.value.find(e => e.name === planForm.value.equipment)

    if (planForm.value.id) {
      // Update existing plan
      const index = inspectionPlans.value.findIndex(p => p.id === planForm.value.id)
      if (index !== -1) {
        inspectionPlans.value[index] = {
          ...inspectionPlans.value[index],
          planName: planForm.value.planName,
          equipment: planForm.value.equipment,
          equipmentType: planForm.value.equipmentType,
          frequency: planForm.value.frequency,
          priority: planForm.value.priority,
          startDate: planForm.value.startDate,
          nextDueDate: planForm.value.nextDueDate,
          assignedTo: planForm.value.assignedTo,
          estimatedHours: planForm.value.estimatedHours,
          checklist: planForm.value.checklist,
          instructions: planForm.value.instructions
        }
        ElMessage.success('Plan updated')
      }
    } else {
      // Create new plan
      const newId = Math.max(...inspectionPlans.value.map(p => p.id), 0) + 1
      inspectionPlans.value.push({
        id: newId,
        planCode: planForm.value.planCode,
        planName: planForm.value.planName,
        equipment: planForm.value.equipment,
        equipmentType: planForm.value.equipmentType || equipment?.type || '',
        frequency: planForm.value.frequency,
        priority: planForm.value.priority,
        startDate: planForm.value.startDate,
        nextDueDate: planForm.value.nextDueDate,
        lastInspection: null,
        assignedTo: planForm.value.assignedTo,
        assignedToId: engineers.value.find(e => e.name === planForm.value.assignedTo)?.id || 0,
        status: 'pending',
        estimatedHours: planForm.value.estimatedHours,
        actualHours: null,
        checklist: planForm.value.checklist,
        instructions: planForm.value.instructions,
        createdAt: new Date().toISOString().slice(0, 10)
      })
      ElMessage.success('Plan created')
    }

    dialogVisible.value = false
  })
}

const startInspection = (plan: InspectionPlan | null) => {
  if (!plan) return
  completingPlan.value = plan
  completeForm.value = {
    completionDate: new Date().toISOString().slice(0, 10),
    actualHours: plan.estimatedHours,
    notes: ''
  }
  completeDialogVisible.value = true
}

const confirmComplete = () => {
  if (!completingPlan.value) return

  const index = inspectionPlans.value.findIndex(p => p.id === completingPlan.value!.id)
  if (index !== -1) {
    // Calculate next due date based on frequency
    const nextDate = new Date(completingPlan.value.nextDueDate)
    const frequency = completingPlan.value.frequency
    switch (frequency) {
      case 'daily':
        nextDate.setDate(nextDate.getDate() + 1)
        break
      case 'weekly':
        nextDate.setDate(nextDate.getDate() + 7)
        break
      case 'monthly':
        nextDate.setMonth(nextDate.getMonth() + 1)
        break
      case 'quarterly':
        nextDate.setMonth(nextDate.getMonth() + 3)
        break
      case 'yearly':
        nextDate.setFullYear(nextDate.getFullYear() + 1)
        break
    }

    inspectionPlans.value[index] = {
      ...inspectionPlans.value[index],
      status: 'completed',
      lastInspection: completeForm.value.completionDate,
      actualHours: completeForm.value.actualHours,
      nextDueDate: nextDate.toISOString().slice(0, 10)
    }
    ElMessage.success('Inspection completed')
  }

  completeDialogVisible.value = false
  viewDialogVisible.value = false
}

const handleTabChange = () => {
  currentPage.value = 1
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Lifecycle ====================
onMounted(() => {
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
    }, 500)
  }, 2200)
})
</script>

<style scoped>
* {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
*::-webkit-scrollbar {
  display: none;
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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Page ==================== */
.inspection-plan-page {
  min-height: 100vh;
  background: #f5f7fb;
  padding: 20px;
  overflow-x: hidden;
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
  gap: 10px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 6px 0;
}

.page-subtitle {
  font-size: 13px;
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
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
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

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 2px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

/* Main Tabs */
.main-tabs {
  background: white;
  border-radius: 16px;
  padding: 0 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__item) {
  height: 50px;
  line-height: 50px;
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

/* Checklist Tags */
.checklist-tags {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.checklist-tag {
  margin: 0;
}

.checklist-list {
  margin: 0;
  padding-left: 20px;
}

.checklist-list li {
  margin: 4px 0;
}

/* Plan Detail */
.plan-detail {
  max-height: 500px;
  overflow-y: auto;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
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