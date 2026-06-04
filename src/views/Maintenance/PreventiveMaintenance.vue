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
          <span class="loading-title">Preventive Maintenance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Proactive Asset Care</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="preventive-maintenance-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Tools /></el-icon>
          Preventive Maintenance
        </h1>
        <div class="page-subtitle">Schedule and track proactive maintenance activities</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">
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
          <div class="stat-value">{{ stats.dueThisWeek }}</div>
          <div class="stat-label">Due This Week</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><TrendCharts /></el-icon>
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
        <el-tab-pane label="Due This Week" name="due-week">
          <template #label>
            <span><el-icon><Clock /></el-icon> Due This Week</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Overdue" name="overdue">
          <template #label>
            <span><el-icon><WarningFilled /></el-icon> Overdue</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="In Progress" name="in-progress">
          <template #label>
            <span><el-icon><Loading /></el-icon> In Progress</span>
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
            placeholder="Search by plan or equipment..."
            style="width: 240px"
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
          <el-option label="Time-Based" value="time" />
          <el-option label="Usage-Based" value="usage" />
          <el-option label="Condition-Based" value="condition" />
        </el-select>
        <el-select v-model="equipmentFilter" placeholder="Equipment Type" clearable style="width: 140px">
          <el-option label="UPS" value="UPS" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Generator" value="Generator" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="Transformer" value="Transformer" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Last updated: {{ lastUpdated }}</span>
      </div>
    </div>

    <!-- PM Plans Grid -->
    <div class="pm-grid">
      <div
          v-for="plan in paginatedPlans"
          :key="plan.id"
          class="pm-card"
          :class="[plan.priority, { overdue: isOverdue(plan) }]"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="header-left">
            <div class="plan-icon" :class="getEquipmentTypeColor(plan.equipmentType)">
              <el-icon><Tools /></el-icon>
            </div>
            <div class="plan-info">
              <div class="plan-name">{{ plan.name }}</div>
              <div class="plan-meta">
                <span class="plan-code">{{ plan.code }}</span>
                <span class="plan-type">{{ getTypeText(plan.type) }}</span>
              </div>
            </div>
          </div>
          <el-dropdown trigger="click" @command="(cmd) => handleMenuCommand(cmd, plan)">
            <el-button text circle>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="view">View Details</el-dropdown-item>
                <el-dropdown-item command="edit">Edit</el-dropdown-item>
                <el-dropdown-item command="start">Start Maintenance</el-dropdown-item>
                <el-dropdown-item command="complete">Mark Complete</el-dropdown-item>
                <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- Equipment Info -->
        <div class="equipment-info">
          <div class="equipment-name">
            <el-icon><Cpu /></el-icon>
            {{ plan.equipment }}
          </div>
          <div class="equipment-location">
            <el-icon><Location /></el-icon>
            {{ plan.location }}
          </div>
        </div>

        <!-- Schedule Info -->
        <div class="schedule-info">
          <div class="schedule-item">
            <span class="label">Frequency:</span>
            <span class="value">{{ getFrequencyText(plan.frequency) }}</span>
          </div>
          <div class="schedule-item">
            <span class="label">Next Due:</span>
            <span class="value" :class="{ 'overdue-text': isOverdue(plan) }">
              {{ plan.nextDueDate }}
            </span>
          </div>
          <div class="schedule-item">
            <span class="label">Last Done:</span>
            <span class="value">{{ plan.lastCompletion || 'Never' }}</span>
          </div>
        </div>

        <!-- Priority Badge -->
        <div class="priority-badge" :class="plan.priority">
          {{ getPriorityText(plan.priority) }}
        </div>

        <!-- Progress -->
        <div class="progress-section">
          <div class="progress-label">
            <span>Completion Progress</span>
            <span>{{ plan.completionRate }}%</span>
          </div>
          <el-progress :percentage="plan.completionRate" :stroke-width="6" :color="getProgressColor(plan.completionRate)" />
        </div>

        <!-- Assigned To -->
        <div class="assigned-info">
          <el-icon><User /></el-icon>
          <span>{{ plan.assignedTo }}</span>
          <el-tag :type="getStatusTagType(plan.status)" size="small" class="status-tag">
            {{ getStatusText(plan.status) }}
          </el-tag>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-stats">
            <span><el-icon><Document /></el-icon> {{ plan.completedTasks }}/{{ plan.totalTasks }} tasks</span>
            <span><el-icon><Clock /></el-icon> {{ plan.estimatedHours }}h est.</span>
          </div>
          <el-button type="primary" size="small" @click.stop="startMaintenance(plan)" v-if="plan.status === 'pending'">
            Start
          </el-button>
          <el-button type="success" size="small" @click.stop="completeMaintenance(plan)" v-else-if="plan.status === 'in-progress'">
            Complete
          </el-button>
          <el-tag v-else-if="plan.status === 'completed'" type="success" size="small">Completed</el-tag>
          <el-tag v-else type="danger" size="small">Overdue</el-tag>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredPlans.length === 0" class="empty-state">
        <el-empty description="No preventive maintenance plans found">
          <el-button type="primary" @click="openCreateDialog">Create First Plan</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="filteredPlans.length > 0">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[6, 12, 18, 24]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" class="pm-dialog">
      <el-form :model="planForm" :rules="formRules" ref="formRef" label-width="130px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Plan Name" prop="name">
              <el-input v-model="planForm.name" placeholder="Enter plan name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Plan Type" prop="type">
              <el-select v-model="planForm.type" placeholder="Select type" style="width: 100%">
                <el-option label="Time-Based" value="time" />
                <el-option label="Usage-Based" value="usage" />
                <el-option label="Condition-Based" value="condition" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Equipment" prop="equipment">
              <el-select v-model="planForm.equipment" placeholder="Select equipment" filterable style="width: 100%">
                <el-option
                    v-for="item in equipmentOptions"
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
                <el-option label="Generator" value="Generator" />
                <el-option label="Chiller" value="Chiller" />
                <el-option label="HVAC" value="HVAC" />
                <el-option label="Transformer" value="Transformer" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Location" prop="location">
              <el-input v-model="planForm.location" placeholder="Equipment location" />
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
            <el-form-item label="Frequency" prop="frequency">
              <el-select v-model="planForm.frequency" placeholder="Select frequency" style="width: 100%">
                <el-option label="Daily" value="daily" />
                <el-option label="Weekly" value="weekly" />
                <el-option label="Monthly" value="monthly" />
                <el-option label="Quarterly" value="quarterly" />
                <el-option label="Semi-Annual" value="semi-annual" />
                <el-option label="Annual" value="annual" />
              </el-select>
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
            <el-form-item label="Estimated Hours" prop="estimatedHours">
              <el-input-number v-model="planForm.estimatedHours" :min="0.5" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Assigned To" prop="assignedTo">
              <el-select v-model="planForm.assignedTo" placeholder="Select engineer" filterable style="width: 100%">
                <el-option
                    v-for="eng in engineers"
                    :key="eng.id"
                    :label="eng.name"
                    :value="eng.name"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description" prop="description">
          <el-input v-model="planForm.description" type="textarea" :rows="2" placeholder="Maintenance description..." />
        </el-form-item>

        <el-form-item label="Tasks">
          <div class="tasks-list">
            <div v-for="(task, idx) in planForm.tasks" :key="idx" class="task-row">
              <el-input v-model="task.name" placeholder="Task description" size="small" style="flex: 3" />
              <el-input-number v-model="task.estimatedMinutes" :min="5" :step="5" placeholder="Min" size="small" style="width: 100px" />
              <el-select v-model="task.type" placeholder="Type" size="small" style="width: 100px">
                <el-option label="Check" value="check" />
                <el-option label="Clean" value="clean" />
                <el-option label="Replace" value="replace" />
                <el-option label="Test" value="test" />
                <el-option label="Calibrate" value="calibrate" />
              </el-select>
              <el-button type="danger" link size="small" @click="removeTask(idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button type="primary" link @click="addTask" style="margin-top: 10px">
              <el-icon><Plus /></el-icon> Add Task
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePlan">Save Plan</el-button>
      </template>
    </el-dialog>

    <!-- View Detail Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="viewPlan?.name" width="750px" class="view-dialog">
      <div v-if="viewPlan" class="view-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Plan Code">{{ viewPlan.code }}</el-descriptions-item>
          <el-descriptions-item label="Plan Type">{{ getTypeText(viewPlan.type) }}</el-descriptions-item>
          <el-descriptions-item label="Equipment">{{ viewPlan.equipment }}</el-descriptions-item>
          <el-descriptions-item label="Equipment Type">{{ viewPlan.equipmentType }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ viewPlan.location }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(viewPlan.priority)" size="small">
              {{ getPriorityText(viewPlan.priority) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Frequency">{{ getFrequencyText(viewPlan.frequency) }}</el-descriptions-item>
          <el-descriptions-item label="Next Due Date">{{ viewPlan.nextDueDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Completion">{{ viewPlan.lastCompletion || 'Never' }}</el-descriptions-item>
          <el-descriptions-item label="Estimated Hours">{{ viewPlan.estimatedHours }} hours</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ viewPlan.assignedTo }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(viewPlan.status)" size="small">
              {{ getStatusText(viewPlan.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Completion Rate" :span="2">
            <el-progress :percentage="viewPlan.completionRate" :stroke-width="8" />
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ viewPlan.description || 'No description' }}</el-descriptions-item>
          <el-descriptions-item label="Tasks" :span="2">
            <ul class="task-list">
              <li v-for="(task, idx) in viewPlan.tasks" :key="idx">
                {{ task.name }} - {{ task.estimatedMinutes }} min ({{ getTaskTypeText(task.type) }})
              </li>
            </ul>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="startMaintenance(viewPlan)" v-if="viewPlan?.status === 'pending'">
          Start Maintenance
        </el-button>
        <el-button type="success" @click="completeMaintenance(viewPlan)" v-else-if="viewPlan?.status === 'in-progress'">
          Complete Maintenance
        </el-button>
      </template>
    </el-dialog>

    <!-- Complete Maintenance Dialog -->
    <el-dialog v-model="completeDialogVisible" title="Complete Maintenance" width="550px">
      <div class="complete-content" v-if="completingPlan">
        <p><strong>Plan:</strong> {{ completingPlan.name }}</p>
        <p><strong>Equipment:</strong> {{ completingPlan.equipment }}</p>
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
          <el-form-item label="Task Status">
            <div class="task-status-list">
              <div v-for="(task, idx) in completingPlan.tasks" :key="idx" class="task-status-item">
                <el-checkbox v-model="task.completed">{{ task.name }}</el-checkbox>
                <span class="task-time">({{ task.estimatedMinutes }} min)</span>
              </div>
            </div>
          </el-form-item>
          <el-form-item label="Notes">
            <el-input v-model="completeForm.notes" type="textarea" :rows="3" placeholder="Maintenance notes..." />
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Tools, Plus, Download, Refresh, List, Clock, WarningFilled,
  CircleCheck, Search, MoreFilled, Cpu, Location, User,
  Delete, Loading, TrendCharts
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading maintenance plans...',
  'Loading equipment data...',
  'Initializing scheduler...',
  'Almost ready...'
]

// ==================== Types ====================
interface PMTask {
  name: string
  estimatedMinutes: number
  type: string
  completed?: boolean
}

interface PMPlan {
  id: number
  code: string
  name: string
  type: 'time' | 'usage' | 'condition'
  equipment: string
  equipmentType: string
  location: string
  priority: 'critical' | 'high' | 'medium' | 'low'
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'semi-annual' | 'annual'
  nextDueDate: string
  lastCompletion: string | null
  estimatedHours: number
  actualHours: number | null
  assignedTo: string
  status: 'pending' | 'in-progress' | 'completed' | 'overdue'
  completionRate: number
  completedTasks: number
  totalTasks: number
  description: string
  tasks: PMTask[]
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
  role: string
}

// ==================== Mock Data ====================
const equipmentOptions = ref<Equipment[]>([
  { id: 1, name: 'UPS-01', type: 'UPS', location: 'Server Room A' },
  { id: 2, name: 'UPS-02', type: 'UPS', location: 'Server Room B' },
  { id: 3, name: 'CRAC-01', type: 'CRAC', location: 'Data Center' },
  { id: 4, name: 'CRAC-02', type: 'CRAC', location: 'Data Center' },
  { id: 5, name: 'PDU-A01', type: 'PDU', location: 'Server Row A' },
  { id: 6, name: 'Generator-01', type: 'Generator', location: 'Generator Room' },
  { id: 7, name: 'Chiller-01', type: 'Chiller', location: 'Chiller Plant' },
  { id: 8, name: 'Transformer-01', type: 'Transformer', location: 'Electrical Room' }
])

const engineers = ref<Engineer[]>([
  { id: 1, name: 'John Chen', role: 'Senior Technician' },
  { id: 2, name: 'Sarah Wong', role: 'HVAC Specialist' },
  { id: 3, name: 'Mike Lim', role: 'Electrical Engineer' },
  { id: 4, name: 'David Tan', role: 'General Technician' },
  { id: 5, name: 'Lisa Ng', role: 'Network Specialist' },
  { id: 6, name: 'Ahmad Razak', role: 'HVAC Technician' },
  { id: 7, name: 'Kevin Lim', role: 'UPS Specialist' }
])

const pmPlans = ref<PMPlan[]>([
  {
    id: 1, code: 'PM-001', name: 'UPS Battery Health Check', type: 'time', equipment: 'UPS-01', equipmentType: 'UPS',
    location: 'Server Room A', priority: 'critical', frequency: 'monthly', nextDueDate: '2024-06-15',
    lastCompletion: '2024-05-15', estimatedHours: 2, actualHours: null, assignedTo: 'John Chen',
    status: 'pending', completionRate: 0, completedTasks: 0, totalTasks: 6,
    description: 'Monthly UPS battery health check including voltage testing and thermal imaging.',
    tasks: [
      { name: 'Check battery terminal connections', estimatedMinutes: 15, type: 'check' },
      { name: 'Measure individual battery voltages', estimatedMinutes: 30, type: 'measure' },
      { name: 'Perform battery capacity test', estimatedMinutes: 45, type: 'test' },
      { name: 'Inspect for corrosion or leakage', estimatedMinutes: 15, type: 'visual' },
      { name: 'Check ambient temperature', estimatedMinutes: 5, type: 'measure' },
      { name: 'Record all readings in log', estimatedMinutes: 10, type: 'check' }
    ]
  },
  {
    id: 2, code: 'PM-002', name: 'CRAC Filter Replacement', type: 'time', equipment: 'CRAC-01', equipmentType: 'CRAC',
    location: 'Data Center', priority: 'high', frequency: 'monthly', nextDueDate: '2024-06-10',
    lastCompletion: '2024-05-10', estimatedHours: 1.5, actualHours: null, assignedTo: 'Sarah Wong',
    status: 'in-progress', completionRate: 40, completedTasks: 2, totalTasks: 5,
    description: 'Monthly CRAC unit filter inspection and replacement.',
    tasks: [
      { name: 'Check filter condition', estimatedMinutes: 10, type: 'visual' },
      { name: 'Replace dirty filters', estimatedMinutes: 30, type: 'replace' },
      { name: 'Clean filter housing', estimatedMinutes: 20, type: 'clean' },
      { name: 'Check airflow pressure', estimatedMinutes: 15, type: 'measure' },
      { name: 'Record filter change date', estimatedMinutes: 5, type: 'check' }
    ]
  },
  {
    id: 3, code: 'PM-003', name: 'Generator Weekly Test', type: 'usage', equipment: 'Generator-01', equipmentType: 'Generator',
    location: 'Generator Room', priority: 'critical', frequency: 'weekly', nextDueDate: '2024-06-07',
    lastCompletion: '2024-05-31', estimatedHours: 1, actualHours: null, assignedTo: 'Mike Lim',
    status: 'pending', completionRate: 0, completedTasks: 0, totalTasks: 4,
    description: 'Weekly generator test run under load.',
    tasks: [
      { name: 'Check fuel level', estimatedMinutes: 5, type: 'check' },
      { name: 'Start generator and run for 30 min', estimatedMinutes: 30, type: 'test' },
      { name: 'Monitor voltage and frequency', estimatedMinutes: 15, type: 'measure' },
      { name: 'Check for unusual noise/vibration', estimatedMinutes: 10, type: 'check' }
    ]
  },
  {
    id: 4, code: 'PM-004', name: 'PDU Load Balancing', type: 'condition', equipment: 'PDU-A01', equipmentType: 'PDU',
    location: 'Server Row A', priority: 'high', frequency: 'quarterly', nextDueDate: '2024-06-20',
    lastCompletion: '2024-03-20', estimatedHours: 2.5, actualHours: 2.2, assignedTo: 'John Chen',
    status: 'pending', completionRate: 0, completedTasks: 0, totalTasks: 5,
    description: 'Quarterly PDU load balancing and phase monitoring.',
    tasks: [
      { name: 'Measure phase currents', estimatedMinutes: 20, type: 'measure' },
      { name: 'Check for phase imbalance', estimatedMinutes: 15, type: 'check' },
      { name: 'Adjust load distribution', estimatedMinutes: 60, type: 'adjust' },
      { name: 'Verify after adjustment', estimatedMinutes: 30, type: 'test' },
      { name: 'Update load records', estimatedMinutes: 10, type: 'check' }
    ]
  },
  {
    id: 5, code: 'PM-005', name: 'Chiller Oil Analysis', type: 'time', equipment: 'Chiller-01', equipmentType: 'Chiller',
    location: 'Chiller Plant', priority: 'medium', frequency: 'quarterly', nextDueDate: '2024-06-25',
    lastCompletion: '2024-03-25', estimatedHours: 2, actualHours: null, assignedTo: 'Sarah Wong',
    status: 'pending', completionRate: 0, completedTasks: 0, totalTasks: 4,
    description: 'Quarterly chiller oil sampling and analysis.',
    tasks: [
      { name: 'Take oil sample', estimatedMinutes: 30, type: 'sample' },
      { name: 'Check oil level and condition', estimatedMinutes: 15, type: 'visual' },
      { name: 'Send sample to lab', estimatedMinutes: 20, type: 'admin' },
      { name: 'Review lab results', estimatedMinutes: 30, type: 'review' }
    ]
  },
  {
    id: 6, code: 'PM-006', name: 'Transformer Thermal Imaging', type: 'condition', equipment: 'Transformer-01', equipmentType: 'Transformer',
    location: 'Electrical Room', priority: 'critical', frequency: 'semi-annual', nextDueDate: '2024-06-18',
    lastCompletion: '2023-12-18', estimatedHours: 3, actualHours: null, assignedTo: 'Mike Lim',
    status: 'pending', completionRate: 0, completedTasks: 0, totalTasks: 6,
    description: 'Semi-annual thermal imaging inspection of transformer.',
    tasks: [
      { name: 'Setup thermal camera', estimatedMinutes: 15, type: 'setup' },
      { name: 'Scan all bushing connections', estimatedMinutes: 30, type: 'scan' },
      { name: 'Scan core and windings', estimatedMinutes: 30, type: 'scan' },
      { name: 'Scan cooling system', estimatedMinutes: 30, type: 'scan' },
      { name: 'Analyze thermal images', estimatedMinutes: 45, type: 'analysis' },
      { name: 'Generate report', estimatedMinutes: 30, type: 'report' }
    ]
  },
  {
    id: 7, code: 'PM-007', name: 'HVAC AHU Belt Replacement', type: 'time', equipment: 'AHU-01', equipmentType: 'HVAC',
    location: 'Mechanical Room', priority: 'medium', frequency: 'semi-annual', nextDueDate: '2024-06-05',
    lastCompletion: '2023-12-05', estimatedHours: 2, actualHours: null, assignedTo: 'Ahmad Razak',
    status: 'overdue', completionRate: 0, completedTasks: 0, totalTasks: 5,
    description: 'Semi-annual AHU belt inspection and replacement.',
    tasks: [
      { name: 'Inspect belt condition', estimatedMinutes: 15, type: 'visual' },
      { name: 'Check belt tension', estimatedMinutes: 10, type: 'check' },
      { name: 'Replace if worn', estimatedMinutes: 45, type: 'replace' },
      { name: 'Align pulleys', estimatedMinutes: 30, type: 'align' },
      { name: 'Test run and verify', estimatedMinutes: 20, type: 'test' }
    ]
  },
  {
    id: 8, code: 'PM-008', name: 'Cooling Tower Cleaning', type: 'time', equipment: 'Tower-01', equipmentType: 'HVAC',
    location: 'Roof', priority: 'high', frequency: 'quarterly', nextDueDate: '2024-06-12',
    lastCompletion: '2024-03-12', estimatedHours: 4, actualHours: null, assignedTo: 'Sarah Wong',
    status: 'pending', completionRate: 0, completedTasks: 0, totalTasks: 6,
    description: 'Quarterly cooling tower cleaning and maintenance.',
    tasks: [
      { name: 'Inspect basin for debris', estimatedMinutes: 20, type: 'visual' },
      { name: 'Clean basin and screens', estimatedMinutes: 60, type: 'clean' },
      { name: 'Check water treatment levels', estimatedMinutes: 15, type: 'check' },
      { name: 'Inspect fan and motor', estimatedMinutes: 30, type: 'visual' },
      { name: 'Check belt condition', estimatedMinutes: 15, type: 'check' },
      { name: 'Record maintenance activities', estimatedMinutes: 10, type: 'admin' }
    ]
  },
  {
    id: 9, code: 'PM-009', name: 'Network Switch Firmware Update', type: 'time', equipment: 'Switch-01', equipmentType: 'Network',
    location: 'Network Room', priority: 'medium', frequency: 'quarterly', nextDueDate: '2024-06-22',
    lastCompletion: '2024-03-22', estimatedHours: 1.5, actualHours: 1.2, assignedTo: 'Lisa Ng',
    status: 'pending', completionRate: 0, completedTasks: 0, totalTasks: 4,
    description: 'Quarterly network switch firmware updates.',
    tasks: [
      { name: 'Backup current configuration', estimatedMinutes: 15, type: 'backup' },
      { name: 'Download latest firmware', estimatedMinutes: 15, type: 'download' },
      { name: 'Schedule maintenance window', estimatedMinutes: 10, type: 'plan' },
      { name: 'Perform firmware update', estimatedMinutes: 30, type: 'update' }
    ]
  }
])

// ==================== State ====================
const activeTab = ref('all')
const searchText = ref('')
const priorityFilter = ref('')
const typeFilter = ref('')
const equipmentFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(6)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const completeDialogVisible = ref(false)
const dialogTitle = ref('Create PM Plan')
const viewPlan = ref<PMPlan | null>(null)
const completingPlan = ref<PMPlan | null>(null)
const formRef = ref()

const planForm = ref({
  id: null as number | null,
  name: '',
  type: 'time' as 'time' | 'usage' | 'condition',
  equipment: '',
  equipmentType: '',
  location: '',
  priority: 'medium' as 'critical' | 'high' | 'medium' | 'low',
  frequency: 'monthly' as 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'semi-annual' | 'annual',
  nextDueDate: '',
  estimatedHours: 1,
  assignedTo: '',
  description: '',
  tasks: [] as PMTask[]
})

const completeForm = ref({
  completionDate: '',
  actualHours: 0,
  notes: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter plan name', trigger: 'blur' }],
  equipment: [{ required: true, message: 'Please select equipment', trigger: 'change' }],
  frequency: [{ required: true, message: 'Please select frequency', trigger: 'change' }],
  nextDueDate: [{ required: true, message: 'Please select due date', trigger: 'change' }]
}

// ==================== Computed ====================
const lastUpdated = computed(() => {
  return new Date().toLocaleDateString()
})

const stats = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  const weekLater = new Date()
  weekLater.setDate(weekLater.getDate() + 7)
  const weekLaterStr = weekLater.toISOString().slice(0, 10)

  const dueThisWeek = pmPlans.value.filter(p =>
      p.nextDueDate >= today && p.nextDueDate <= weekLaterStr && p.status !== 'completed'
  ).length

  return {
    totalPlans: pmPlans.value.length,
    activePlans: pmPlans.value.filter(p => p.status === 'pending' || p.status === 'in-progress').length,
    dueThisWeek,
    completionRate: Math.round((pmPlans.value.filter(p => p.status === 'completed').length / pmPlans.value.length) * 100)
  }
})

const filteredPlans = computed(() => {
  let filtered = [...pmPlans.value]

  if (activeTab.value === 'due-week') {
    const today = new Date().toISOString().slice(0, 10)
    const weekLater = new Date()
    weekLater.setDate(weekLater.getDate() + 7)
    const weekLaterStr = weekLater.toISOString().slice(0, 10)
    filtered = filtered.filter(p => p.nextDueDate >= today && p.nextDueDate <= weekLaterStr && p.status !== 'completed')
  } else if (activeTab.value === 'overdue') {
    const today = new Date().toISOString().slice(0, 10)
    filtered = filtered.filter(p => p.nextDueDate < today && p.status !== 'completed')
  } else if (activeTab.value === 'in-progress') {
    filtered = filtered.filter(p => p.status === 'in-progress')
  } else if (activeTab.value === 'completed') {
    filtered = filtered.filter(p => p.status === 'completed')
  }

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(search) ||
        p.equipment.toLowerCase().includes(search) ||
        p.code.toLowerCase().includes(search)
    )
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(p => p.priority === priorityFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(p => p.type === typeFilter.value)
  }

  if (equipmentFilter.value) {
    filtered = filtered.filter(p => p.equipmentType === equipmentFilter.value)
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
const getTypeText = (type: string) => {
  const map: Record<string, string> = { time: 'Time-Based', usage: 'Usage-Based', condition: 'Condition-Based' }
  return map[type] || type
}

const getFrequencyText = (frequency: string) => {
  const map: Record<string, string> = {
    daily: 'Daily', weekly: 'Weekly', monthly: 'Monthly', quarterly: 'Quarterly',
    'semi-annual': 'Semi-Annual', annual: 'Annual'
  }
  return map[frequency] || frequency
}

const getPriorityText = (priority: string) => {
  const map: Record<string, string> = { critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low' }
  return map[priority] || priority
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
  return map[status] || 'info'
}

const getTaskTypeText = (type: string) => {
  const map: Record<string, string> = {
    check: 'Check', clean: 'Clean', replace: 'Replace', test: 'Test',
    measure: 'Measure', calibrate: 'Calibrate', visual: 'Visual', sample: 'Sample',
    adjust: 'Adjust', backup: 'Backup', update: 'Update', scan: 'Scan',
    analysis: 'Analysis', report: 'Report', setup: 'Setup', align: 'Align',
    admin: 'Admin', plan: 'Plan', download: 'Download', review: 'Review'
  }
  return map[type] || type
}

const getEquipmentTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    UPS: 'ups', CRAC: 'crac', PDU: 'pdu', Generator: 'generator',
    Chiller: 'chiller', HVAC: 'hvac', Transformer: 'transformer', Network: 'network'
  }
  return colors[type] || 'default'
}

const getProgressColor = (rate: number) => {
  if (rate >= 90) return '#67c23a'
  if (rate >= 60) return '#e6a23c'
  return '#f56c6c'
}

const isOverdue = (plan: PMPlan) => {
  const today = new Date().toISOString().slice(0, 10)
  return plan.nextDueDate < today && plan.status !== 'completed'
}

const addTask = () => {
  planForm.value.tasks.push({ name: '', estimatedMinutes: 30, type: 'check' })
}

const removeTask = (index: number) => {
  planForm.value.tasks.splice(index, 1)
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

const handleMenuCommand = (command: string, plan: PMPlan) => {
  switch (command) {
    case 'view': viewPlanDetails(plan); break
    case 'edit': editPlan(plan); break
    case 'start': startMaintenance(plan); break
    case 'complete': completeMaintenance(plan); break
    case 'delete': deletePlan(plan); break
  }
}

const openCreateDialog = () => {
  dialogTitle.value = 'Create PM Plan'
  planForm.value = {
    id: null,
    name: '',
    type: 'time',
    equipment: '',
    equipmentType: '',
    location: '',
    priority: 'medium',
    frequency: 'monthly',
    nextDueDate: new Date().toISOString().slice(0, 10),
    estimatedHours: 1,
    assignedTo: '',
    description: '',
    tasks: []
  }
  dialogVisible.value = true
}

const editPlan = (plan: PMPlan) => {
  dialogTitle.value = 'Edit PM Plan'
  planForm.value = {
    id: plan.id,
    name: plan.name,
    type: plan.type,
    equipment: plan.equipment,
    equipmentType: plan.equipmentType,
    location: plan.location,
    priority: plan.priority,
    frequency: plan.frequency,
    nextDueDate: plan.nextDueDate,
    estimatedHours: plan.estimatedHours,
    assignedTo: plan.assignedTo,
    description: plan.description,
    tasks: JSON.parse(JSON.stringify(plan.tasks))
  }
  dialogVisible.value = true
}

const viewPlanDetails = (plan: PMPlan) => {
  viewPlan.value = plan
  viewDialogVisible.value = true
}

const deletePlan = (plan: PMPlan) => {
  ElMessageBox.confirm(
      `Delete PM plan "${plan.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = pmPlans.value.findIndex(p => p.id === plan.id)
    if (index !== -1) {
      pmPlans.value.splice(index, 1)
      ElMessage.success('Plan deleted')
    }
  }).catch(() => {})
}

const savePlan = () => {
  if (!formRef.value) return
  formRef.value.validate((valid: boolean) => {
    if (!valid) return

    if (planForm.value.id) {
      const index = pmPlans.value.findIndex(p => p.id === planForm.value.id)
      if (index !== -1) {
        pmPlans.value[index] = {
          ...pmPlans.value[index],
          name: planForm.value.name,
          type: planForm.value.type,
          equipment: planForm.value.equipment,
          equipmentType: planForm.value.equipmentType,
          location: planForm.value.location,
          priority: planForm.value.priority,
          frequency: planForm.value.frequency,
          nextDueDate: planForm.value.nextDueDate,
          estimatedHours: planForm.value.estimatedHours,
          assignedTo: planForm.value.assignedTo,
          description: planForm.value.description,
          tasks: planForm.value.tasks,
          totalTasks: planForm.value.tasks.length
        }
        ElMessage.success('Plan updated')
      }
    } else {
      const newId = Math.max(...pmPlans.value.map(p => p.id), 0) + 1
      const equipment = equipmentOptions.value.find(e => e.name === planForm.value.equipment)
      pmPlans.value.push({
        id: newId,
        code: `PM-${String(newId).padStart(3, '0')}`,
        name: planForm.value.name,
        type: planForm.value.type,
        equipment: planForm.value.equipment,
        equipmentType: planForm.value.equipmentType || equipment?.type || '',
        location: planForm.value.location,
        priority: planForm.value.priority,
        frequency: planForm.value.frequency,
        nextDueDate: planForm.value.nextDueDate,
        lastCompletion: null,
        estimatedHours: planForm.value.estimatedHours,
        actualHours: null,
        assignedTo: planForm.value.assignedTo,
        status: 'pending',
        completionRate: 0,
        completedTasks: 0,
        totalTasks: planForm.value.tasks.length,
        description: planForm.value.description,
        tasks: planForm.value.tasks
      })
      ElMessage.success('Plan created')
    }
    dialogVisible.value = false
  })
}

const startMaintenance = (plan: PMPlan | null) => {
  if (!plan) return
  const index = pmPlans.value.findIndex(p => p.id === plan.id)
  if (index !== -1) {
    pmPlans.value[index].status = 'in-progress'
    ElMessage.success(`Started maintenance for ${plan.name}`)
  }
  viewDialogVisible.value = false
}

const completeMaintenance = (plan: PMPlan | null) => {
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

  const index = pmPlans.value.findIndex(p => p.id === completingPlan.value!.id)
  if (index !== -1) {
    const completedTasks = completingPlan.value.tasks.filter(t => t.completed).length
    const completionRate = Math.round((completedTasks / completingPlan.value.totalTasks) * 100)

    // Calculate next due date based on frequency
    const nextDate = new Date(completingPlan.value.nextDueDate)
    switch (completingPlan.value.frequency) {
      case 'daily': nextDate.setDate(nextDate.getDate() + 1); break
      case 'weekly': nextDate.setDate(nextDate.getDate() + 7); break
      case 'monthly': nextDate.setMonth(nextDate.getMonth() + 1); break
      case 'quarterly': nextDate.setMonth(nextDate.getMonth() + 3); break
      case 'semi-annual': nextDate.setMonth(nextDate.getMonth() + 6); break
      case 'annual': nextDate.setFullYear(nextDate.getFullYear() + 1); break
    }

    pmPlans.value[index] = {
      ...pmPlans.value[index],
      status: 'completed',
      lastCompletion: completeForm.value.completionDate,
      actualHours: completeForm.value.actualHours,
      nextDueDate: nextDate.toISOString().slice(0, 10),
      completionRate: completionRate,
      completedTasks: completedTasks
    }
    ElMessage.success(`Maintenance completed for ${completingPlan.value.name}`)
  }
  completeDialogVisible.value = false
  viewDialogVisible.value = false
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('PM plans exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
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
.preventive-maintenance-page {
  min-height: 100vh;
  background: #f0f2f6;
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
  margin-bottom: 24px;
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

/* PM Grid */
.pm-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.pm-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: relative;
}

.pm-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.1);
}

.pm-card.critical { border-top: 4px solid #ef4444; }
.pm-card.high { border-top: 4px solid #f97316; }
.pm-card.medium { border-top: 4px solid #eab308; }
.pm-card.low { border-top: 4px solid #22c55e; }
.pm-card.overdue { background: #fef2f2; }

/* Card Header */
.card-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #eef2f8;
}

.header-left {
  display: flex;
  gap: 14px;
}

.plan-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.plan-icon.ups { background: #eef2ff; color: #3b82f6; }
.plan-icon.crac { background: #dcfce7; color: #22c55e; }
.plan-icon.pdu { background: #fef3c7; color: #f59e0b; }
.plan-icon.generator { background: #fee2e2; color: #ef4444; }
.plan-icon.chiller { background: #e0e7ff; color: #4f46e5; }
.plan-icon.hvac { background: #f3e8ff; color: #8b5cf6; }
.plan-icon.transformer { background: #fef3c7; color: #d97706; }
.plan-icon.network { background: #d1fae5; color: #059669; }
.plan-icon.default { background: #f1f5f9; color: #64748b; }

.plan-name {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 4px;
}

.plan-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
}

.plan-code {
  color: #3b82f6;
  background: #eef2ff;
  padding: 2px 8px;
  border-radius: 12px;
}

.plan-type {
  color: #64748b;
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 12px;
}

/* Equipment Info */
.equipment-info {
  padding: 12px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #eef2f8;
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.equipment-name, .equipment-location {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #475569;
}

/* Schedule Info */
.schedule-info {
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid #eef2f8;
  font-size: 12px;
}

.schedule-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.schedule-item .label {
  color: #64748b;
  font-size: 10px;
}

.schedule-item .value {
  font-weight: 600;
  color: #1e293b;
}

.schedule-item .value.overdue-text {
  color: #ef4444;
}

/* Priority Badge */
.priority-badge {
  position: absolute;
  top: 16px;
  right: 20px;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 20px;
}

.priority-badge.critical { background: #fee2e2; color: #dc2626; }
.priority-badge.high { background: #fff3e3; color: #ea580c; }
.priority-badge.medium { background: #fef9c3; color: #ca8a04; }
.priority-badge.low { background: #dcfce7; color: #16a34a; }

/* Progress Section */
.progress-section {
  padding: 14px 20px;
  border-bottom: 1px solid #eef2f8;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 8px;
}

/* Assigned Info */
.assigned-info {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #475569;
  border-bottom: 1px solid #eef2f8;
}

.status-tag {
  margin-left: auto;
}

/* Card Footer */
.card-footer {
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.footer-stats {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #64748b;
}

.footer-stats span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  padding: 60px;
  background: white;
  border-radius: 20px;
  text-align: center;
}

/* Dialog Styles */
.pm-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.tasks-list {
  border: 1px solid #eef2f8;
  border-radius: 12px;
  padding: 12px;
}

.task-row {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.task-row:last-child {
  margin-bottom: 0;
}

.view-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.task-list {
  margin: 0;
  padding-left: 20px;
}

.task-list li {
  margin: 6px 0;
}

.task-status-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-status-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-time {
  font-size: 11px;
  color: #64748b;
}

/* Responsive */
@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .pm-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
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

  .schedule-info {
    flex-direction: column;
    gap: 10px;
  }

  .schedule-item {
    flex-direction: row;
    justify-content: space-between;
  }
}
</style>