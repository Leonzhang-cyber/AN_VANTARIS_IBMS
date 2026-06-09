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
        <div class="loading-tip">Lessons Learned</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="lessons-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Lessons Learned</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Lessons Learned</h1>
        <p class="description">Capture, share, and apply insights from decision outcomes to improve future decision-making</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleCreateLesson">
          <el-icon><Plus /></el-icon>
          Add Lesson
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

    <!-- Lessons by Category Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="16">
        <el-card class="trend-chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Lessons by Category</span>
              <el-radio-group v-model="chartPeriod" size="small">
                <el-radio-button value="monthly">Monthly</el-radio-button>
                <el-radio-button value="quarterly">Quarterly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="distribution-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Impact Distribution</span>
            </div>
          </template>
          <div ref="impactChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Quick Filters -->
    <el-card class="quick-filters-card" shadow="hover">
      <div class="quick-filters">
        <span class="filter-label">Quick Filters:</span>
        <el-radio-group v-model="quickFilter" @change="handleQuickFilter">
          <el-radio-button value="all">All Lessons</el-radio-button>
          <el-radio-button value="high">High Impact</el-radio-button>
          <el-radio-button value="recent">Last 30 Days</el-radio-button>
          <el-radio-button value="unread">Unread</el-radio-button>
          <el-radio-button value="actionable">Actionable</el-radio-button>
        </el-radio-group>
      </div>
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
          <el-select v-model="filters.category" placeholder="Category" clearable style="width: 140px">
            <el-option label="Process Improvement" value="Process Improvement" />
            <el-option label="Technical Issue" value="Technical Issue" />
            <el-option label="Communication" value="Communication" />
            <el-option label="Resource Management" value="Resource Management" />
            <el-option label="Risk Management" value="Risk Management" />
            <el-option label="Compliance" value="Compliance" />
          </el-select>
          <el-select v-model="filters.impact" placeholder="Impact Level" clearable style="width: 130px">
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
            <el-option label="Active" value="Active" />
            <el-option label="Implemented" value="Implemented" />
            <el-option label="Under Review" value="Under Review" />
            <el-option label="Archived" value="Archived" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 260px"
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
          <span>Lessons Learned ({{ filteredLessons.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchLessons" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedLessons" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="Lesson Title" min-width="220" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="150">
          <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="impact" label="Impact" width="100">
          <template #default="{ row }">
            <el-tag :type="getImpactTag(row.impact)" size="small">{{ row.impact }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="Created By" width="130" />
        <el-table-column prop="createdAt" label="Created Date" width="110" />
        <el-table-column prop="views" label="Views" width="80" align="center" />
        <el-table-column prop="likes" label="Likes" width="80" align="center" />
        <el-table-column label="Actions" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewLesson(row)">View</el-button>
            <el-button link type="success" size="small" @click="implementLesson(row)">Implement</el-button>
            <el-button link type="info" size="small" @click="shareLesson(row)">Share</el-button>
            <el-button link type="danger" size="small" @click="deleteLesson(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredLessons.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Create/Edit Lesson Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Add Lesson Learned' : (dialogMode === 'edit' ? 'Edit Lesson' : 'Lesson Details')" width="700px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px" :disabled="dialogMode === 'view'">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Title" prop="title">
              <el-input v-model="formData.title" placeholder="Enter lesson title" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Category" prop="category">
              <el-select v-model="formData.category" placeholder="Select category" style="width: 100%">
                <el-option label="Process Improvement" value="Process Improvement" />
                <el-option label="Technical Issue" value="Technical Issue" />
                <el-option label="Communication" value="Communication" />
                <el-option label="Resource Management" value="Resource Management" />
                <el-option label="Risk Management" value="Risk Management" />
                <el-option label="Compliance" value="Compliance" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Impact Level" prop="impact">
              <el-select v-model="formData.impact" placeholder="Select impact" style="width: 100%">
                <el-option label="High" value="High" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Low" value="Low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
                <el-option label="Active" value="Active" />
                <el-option label="Under Review" value="Under Review" />
                <el-option label="Implemented" value="Implemented" />
                <el-option label="Archived" value="Archived" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Related Decision" prop="relatedDecision">
              <el-select v-model="formData.relatedDecision" placeholder="Select related decision" clearable style="width: 100%">
                <el-option label="Chiller Overhaul Decision" value="Chiller Overhaul Decision" />
                <el-option label="LED Lighting Retrofit" value="LED Lighting Retrofit" />
                <el-option label="UPS Battery Replacement" value="UPS Battery Replacement" />
                <el-option label="HVAC Optimization" value="HVAC Optimization" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="What Happened?" prop="whatHappened">
              <el-input v-model="formData.whatHappened" type="textarea" :rows="2" placeholder="Describe what happened" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Root Cause" prop="rootCause">
              <el-input v-model="formData.rootCause" type="textarea" :rows="2" placeholder="Identify the root cause" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Lesson Learned" prop="lesson">
              <el-input v-model="formData.lesson" type="textarea" :rows="2" placeholder="What did we learn?" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Recommendations" prop="recommendations">
              <el-input v-model="formData.recommendations" type="textarea" :rows="2" placeholder="What should we do moving forward?" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Tags" prop="tags">
              <el-select v-model="formData.tags" multiple filterable allow-create default-first-option placeholder="Enter tags" style="width: 100%">
                <el-option label="Efficiency" value="Efficiency" />
                <el-option label="Cost Saving" value="Cost Saving" />
                <el-option label="Safety" value="Safety" />
                <el-option label="Quality" value="Quality" />
                <el-option label="Process" value="Process" />
                <el-option label="Training" value="Training" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button v-if="dialogMode !== 'view'" type="primary" @click="submitForm">Save Lesson</el-button>
      </template>
    </el-dialog>

    <!-- Lesson Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="currentLesson?.title" width="800px" destroy-on-close>
      <div class="lesson-detail">
        <div class="detail-header">
          <div class="lesson-meta">
            <el-tag :type="getCategoryTag(currentLesson?.category || '')" size="default">{{ currentLesson?.category }}</el-tag>
            <el-tag :type="getImpactTag(currentLesson?.impact || '')" size="default">{{ currentLesson?.impact }} Impact</el-tag>
            <el-tag :type="getStatusTag(currentLesson?.status || '')" size="default">{{ currentLesson?.status }}</el-tag>
          </div>
          <div class="lesson-stats">
            <span><el-icon><View /></el-icon> {{ currentLesson?.views }} views</span>
            <span><el-icon><Star /></el-icon> {{ currentLesson?.likes }} likes</span>
          </div>
        </div>

        <div class="detail-section">
          <h4>What Happened?</h4>
          <p>{{ currentLesson?.whatHappened }}</p>
        </div>

        <div class="detail-section">
          <h4>Root Cause Analysis</h4>
          <p>{{ currentLesson?.rootCause }}</p>
        </div>

        <div class="detail-section">
          <h4>Lesson Learned</h4>
          <div class="lesson-box">{{ currentLesson?.lesson }}</div>
        </div>

        <div class="detail-section">
          <h4>Recommendations</h4>
          <ul>
            <li v-for="(rec, idx) in currentLesson?.recommendations.split('\n')" :key="idx">{{ rec }}</li>
          </ul>
        </div>

        <div class="detail-section">
          <h4>Action Items</h4>
          <el-table :data="currentLesson?.actionItems || []" size="small" border>
            <el-table-column prop="task" label="Task" />
            <el-table-column prop="assignee" label="Assignee" width="120" />
            <el-table-column prop="dueDate" label="Due Date" width="100" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Completed' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="detail-section" v-if="currentLesson?.relatedDecision">
          <h4>Related Decision</h4>
          <el-link type="primary" @click="viewRelatedDecision">{{ currentLesson.relatedDecision }}</el-link>
        </div>

        <div class="detail-section">
          <h4>Tags</h4>
          <div>
            <el-tag v-for="tag in currentLesson?.tags" :key="tag" size="small" style="margin-right: 8px">{{ tag }}</el-tag>
          </div>
        </div>

        <div class="detail-section">
          <h4>Metadata</h4>
          <el-descriptions :column="2" size="small">
            <el-descriptions-item label="Created By">{{ currentLesson?.createdBy }}</el-descriptions-item>
            <el-descriptions-item label="Created At">{{ currentLesson?.createdAt }}</el-descriptions-item>
            <el-descriptions-item label="Last Updated">{{ currentLesson?.updatedAt }}</el-descriptions-item>
            <el-descriptions-item label="Last Reviewed">{{ currentLesson?.lastReviewed }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="success" @click="likeLesson">Like ({{ currentLesson?.likes }})</el-button>
        <el-button type="primary" @click="shareLesson(currentLesson)">Share</el-button>
      </template>
    </el-dialog>

    <!-- Implement Dialog -->
    <el-dialog v-model="implementDialogVisible" title="Implement Lesson" width="500px">
      <p>Mark lesson as implemented:</p>
      <p><strong>{{ implementTarget?.title }}</strong></p>
      <el-input
          v-model="implementationNotes"
          type="textarea"
          :rows="3"
          placeholder="Enter implementation notes"
          style="margin-top: 16px"
      />
      <template #footer>
        <el-button @click="implementDialogVisible = false">Cancel</el-button>
        <el-button type="success" @click="confirmImplement">Mark as Implemented</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete lesson "{{ deleteTarget?.title }}"?</p>
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
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, View, Star
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading lessons learned...',
  'Organizing knowledge base...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface Lesson {
  id: number
  title: string
  category: string
  impact: string
  status: string
  whatHappened: string
  rootCause: string
  lesson: string
  recommendations: string
  relatedDecision: string
  relatedDecisionId: number
  createdBy: string
  createdAt: string
  updatedAt: string
  lastReviewed: string
  views: number
  likes: number
  tags: string[]
  actionItems: Array<{ task: string; assignee: string; dueDate: string; status: string }>
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
const trendChartRef = ref<HTMLElement>()
const impactChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let impactChart: echarts.ECharts | null = null

const chartPeriod = ref<'monthly' | 'quarterly'>('monthly')
const quickFilter = ref('all')

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Lessons', value: 86, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Implemented', value: 34, trend: 18, icon: 'Checked', bgColor: '#67c23a', key: 'implemented' },
  { title: 'High Impact', value: 28, trend: 8, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'high' },
  { title: 'Active Lessons', value: 42, trend: -5, icon: 'Clock', bgColor: '#f56c6c', key: 'active' }
])

const lessons = ref<Lesson[]>([
  {
    id: 1,
    title: 'Early Risk Assessment Saves Time and Money',
    category: 'Risk Management',
    impact: 'High',
    status: 'Implemented',
    whatHappened: 'During the chiller overhaul project, we discovered mid-project that critical spare parts had 6-week lead times, causing a 3-week delay.',
    rootCause: 'Risk assessment was conducted at a high level without detailed supply chain analysis.',
    lesson: 'Conduct detailed risk assessments including supply chain lead times before project kickoff.',
    recommendations: 'Implement mandatory detailed risk assessment checklist for all major projects.',
    relatedDecision: 'Chiller Overhaul Decision',
    relatedDecisionId: 101,
    createdBy: 'John Smith',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-20',
    lastReviewed: '2024-02-01',
    views: 245,
    likes: 32,
    tags: ['Risk', 'Planning', 'Supply Chain'],
    actionItems: [
      { task: 'Create risk assessment template', assignee: 'John Smith', dueDate: '2024-02-15', status: 'In Progress' },
      { task: 'Train team on risk assessment', assignee: 'Sarah Chen', dueDate: '2024-02-28', status: 'Pending' }
    ]
  },
  {
    id: 2,
    title: 'Communication Breakdown During Emergency Response',
    category: 'Communication',
    impact: 'High',
    status: 'Implemented',
    whatHappened: 'During the UPS battery failure incident, critical information was delayed because stakeholders were not on the correct communication channels.',
    rootCause: 'Emergency contact list was outdated and communication protocol was unclear.',
    lesson: 'Maintain and regularly test emergency communication protocols and contact lists.',
    recommendations: 'Quarterly testing of emergency communication system and monthly contact list reviews.',
    relatedDecision: 'UPS Battery Replacement',
    relatedDecisionId: 103,
    createdBy: 'Tom Harris',
    createdAt: '2024-01-15',
    updatedAt: '2024-01-25',
    lastReviewed: '2024-02-05',
    views: 189,
    likes: 28,
    tags: ['Communication', 'Emergency', 'Process'],
    actionItems: [
      { task: 'Update emergency contact list', assignee: 'Tom Harris', dueDate: '2024-02-10', status: 'Completed' },
      { task: 'Conduct communication drill', assignee: 'Sarah Chen', dueDate: '2024-02-28', status: 'Pending' }
    ]
  },
  {
    id: 3,
    title: 'Vendor Qualification Process Gaps',
    category: 'Process Improvement',
    impact: 'Medium',
    status: 'Under Review',
    whatHappened: 'Selected LED vendor failed to meet delivery timeline, causing cascading delays in the retrofit project.',
    rootCause: 'Vendor qualification process focused only on price without assessing delivery track record.',
    lesson: 'Include delivery performance metrics in vendor selection criteria.',
    recommendations: 'Expand vendor scorecard to include delivery reliability and past performance.',
    relatedDecision: 'LED Lighting Retrofit',
    relatedDecisionId: 102,
    createdBy: 'Lisa Zhang',
    createdAt: '2024-01-08',
    updatedAt: '2024-01-18',
    lastReviewed: '2024-01-28',
    views: 134,
    likes: 18,
    tags: ['Procurement', 'Vendor', 'Quality'],
    actionItems: [
      { task: 'Update vendor selection criteria', assignee: 'Lisa Zhang', dueDate: '2024-02-20', status: 'In Progress' }
    ]
  },
  {
    id: 4,
    title: 'Resource Overallocation Causes Burnout',
    category: 'Resource Management',
    impact: 'Medium',
    status: 'Implemented',
    whatHappened: 'Key technical staff were assigned to multiple concurrent high-priority projects, leading to fatigue and reduced quality.',
    rootCause: 'No centralized resource capacity tracking system.',
    lesson: 'Implement resource capacity planning and workload balancing.',
    recommendations: 'Adopt resource management tool and establish capacity review process.',
    relatedDecision: '',
    relatedDecisionId: 0,
    createdBy: 'Sarah Chen',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-15',
    lastReviewed: '2024-01-25',
    views: 98,
    likes: 22,
    tags: ['Resources', 'Workload', 'Wellness'],
    actionItems: [
      { task: 'Select resource management tool', assignee: 'Sarah Chen', dueDate: '2024-02-14', status: 'Completed' },
      { task: 'Implement capacity tracking', assignee: 'David Wang', dueDate: '2024-02-28', status: 'In Progress' }
    ]
  },
  {
    id: 5,
    title: 'Data Validation Before AI Implementation',
    category: 'Technical Issue',
    impact: 'High',
    status: 'Active',
    whatHappened: 'HVAC optimization AI model produced inaccurate recommendations due to poor quality input data.',
    rootCause: 'Sensors were not calibrated and historical data had gaps.',
    lesson: 'Validate data quality before deploying any AI or analytics solution.',
    recommendations: 'Implement data quality checks and sensor calibration schedules.',
    relatedDecision: 'HVAC Optimization Algorithm',
    relatedDecisionId: 105,
    createdBy: 'David Wang',
    createdAt: '2024-01-12',
    updatedAt: '2024-01-22',
    lastReviewed: '2024-02-02',
    views: 267,
    likes: 45,
    tags: ['Data', 'AI', 'Quality'],
    actionItems: [
      { task: 'Create data validation framework', assignee: 'David Wang', dueDate: '2024-02-28', status: 'In Progress' },
      { task: 'Schedule sensor calibration', assignee: 'Mike Johnson', dueDate: '2024-03-15', status: 'Pending' }
    ]
  },
  {
    id: 6,
    title: 'Insufficient Stakeholder Engagement',
    category: 'Communication',
    impact: 'Medium',
    status: 'Active',
    whatHappened: 'ESG initiative faced resistance because key stakeholders were not consulted early in the planning process.',
    rootCause: 'Stakeholder mapping was incomplete and engagement plan was not executed.',
    lesson: 'Identify and engage all stakeholders before project initiation.',
    recommendations: 'Create stakeholder engagement matrix and communication plan templates.',
    relatedDecision: 'Solar Panel Installation',
    relatedDecisionId: 104,
    createdBy: 'Emily Zhao',
    createdAt: '2024-01-18',
    updatedAt: '2024-01-28',
    lastReviewed: '2024-02-07',
    views: 76,
    likes: 15,
    tags: ['Stakeholder', 'Engagement', 'Communication'],
    actionItems: [
      { task: 'Create stakeholder template', assignee: 'Emily Zhao', dueDate: '2024-02-28', status: 'In Progress' }
    ]
  },
  {
    id: 7,
    title: 'Budget Contingency Underestimation',
    category: 'Risk Management',
    impact: 'High',
    status: 'Under Review',
    whatHappened: 'Multiple projects exceeded budget due to unforeseen cost increases in materials.',
    rootCause: 'Budget contingency was set at 10% while market volatility suggested 20-25%.',
    lesson: 'Review market conditions when setting budget contingency levels.',
    recommendations: 'Implement quarterly market review process for budget planning.',
    relatedDecision: '',
    relatedDecisionId: 0,
    createdBy: 'Anna Kim',
    createdAt: '2024-01-20',
    updatedAt: '2024-01-30',
    lastReviewed: '2024-02-09',
    views: 112,
    likes: 20,
    tags: ['Budget', 'Risk', 'Planning'],
    actionItems: [
      { task: 'Develop market analysis process', assignee: 'Anna Kim', dueDate: '2024-03-01', status: 'Pending' }
    ]
  },
  {
    id: 8,
    title: 'Documentation Standardization Saves Time',
    category: 'Process Improvement',
    impact: 'Low',
    status: 'Implemented',
    whatHappened: 'Engineers spent hours searching for information across different document formats and locations.',
    rootCause: 'No standardized documentation format or central repository.',
    lesson: 'Standardize documentation templates and maintain a central repository.',
    recommendations: 'Adopt document management system with standard templates.',
    relatedDecision: '',
    relatedDecisionId: 0,
    createdBy: 'John Smith',
    createdAt: '2024-01-22',
    updatedAt: '2024-02-01',
    lastReviewed: '2024-02-12',
    views: 54,
    likes: 12,
    tags: ['Documentation', 'Process', 'Efficiency'],
    actionItems: [
      { task: 'Create document templates', assignee: 'John Smith', dueDate: '2024-02-15', status: 'Completed' }
    ]
  }
])

// ==================== Reactive Variables ====================
const loading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const implementDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit' | 'view'>('create')
const currentLesson = ref<Lesson | null>(null)
const implementTarget = ref<Lesson | null>(null)
const deleteTarget = ref<Lesson | null>(null)
const implementationNotes = ref('')
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)

const filters = reactive({
  keyword: '',
  category: '',
  impact: '',
  status: '',
  dateRange: null as [Date, Date] | null
})

const formData = reactive<Lesson>({
  id: 0,
  title: '',
  category: '',
  impact: 'Medium',
  status: 'Active',
  whatHappened: '',
  rootCause: '',
  lesson: '',
  recommendations: '',
  relatedDecision: '',
  relatedDecisionId: 0,
  createdBy: '',
  createdAt: '',
  updatedAt: '',
  lastReviewed: '',
  views: 0,
  likes: 0,
  tags: [],
  actionItems: []
})

const formRules = {
  title: [{ required: true, message: 'Please enter title', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  whatHappened: [{ required: true, message: 'Please describe what happened', trigger: 'blur' }],
  lesson: [{ required: true, message: 'Please state the lesson learned', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredLessons = computed(() => {
  let filtered = [...lessons.value]

  // Apply quick filter
  if (quickFilter.value === 'high') {
    filtered = filtered.filter(l => l.impact === 'High')
  } else if (quickFilter.value === 'recent') {
    const thirtyDaysAgo = new Date()
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
    filtered = filtered.filter(l => new Date(l.createdAt) >= thirtyDaysAgo)
  } else if (quickFilter.value === 'actionable') {
    filtered = filtered.filter(l => l.status === 'Active' || l.status === 'Under Review')
  }

  // Apply search filters
  if (filters.keyword) {
    filtered = filtered.filter(l =>
        l.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        l.lesson.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.category) {
    filtered = filtered.filter(l => l.category === filters.category)
  }

  if (filters.impact) {
    filtered = filtered.filter(l => l.impact === filters.impact)
  }

  if (filters.status) {
    filtered = filtered.filter(l => l.status === filters.status)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(l => {
      const date = new Date(l.createdAt)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedLessons = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLessons.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getCategoryTag = (category: string): string => {
  const map: Record<string, string> = {
    'Process Improvement': 'primary',
    'Technical Issue': 'danger',
    'Communication': 'warning',
    'Resource Management': 'info',
    'Risk Management': 'warning',
    'Compliance': 'success'
  }
  return map[category] || 'info'
}

const getImpactTag = (impact: string): string => {
  const map: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'info'
  }
  return map[impact] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Active': 'success',
    'Implemented': 'success',
    'Under Review': 'warning',
    'Archived': 'info'
  }
  return map[status] || 'info'
}

// ==================== Chart Initialization ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const monthlyData = [6, 8, 5, 7, 9, 6, 8, 7, 9, 10, 8, 11]
  const quarterlyData = [19, 21, 24, 29]
  const data = chartPeriod.value === 'monthly' ? monthlyData : quarterlyData
  const xAxisData = chartPeriod.value === 'monthly'
      ? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      : ['Q1', 'Q2', 'Q3', 'Q4']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Process Improvement', 'Technical Issue', 'Communication', 'Risk Management', 'Other'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Number of Lessons' },
    series: [
      { name: 'Process Improvement', type: 'bar', data: [2, 3, 1, 2, 3, 2, 2, 3, 2, 3, 2, 3], stack: 'total' },
      { name: 'Technical Issue', type: 'bar', data: [1, 1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2], stack: 'total' },
      { name: 'Communication', type: 'bar', data: [1, 2, 1, 2, 1, 1, 2, 1, 2, 2, 2, 2], stack: 'total' },
      { name: 'Risk Management', type: 'bar', data: [1, 1, 1, 1, 2, 1, 1, 2, 2, 2, 2, 3], stack: 'total' },
      { name: 'Other', type: 'bar', data: [1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1], stack: 'total' }
    ]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initImpactChart = () => {
  if (!impactChartRef.value) return
  if (impactChart) impactChart.dispose()

  impactChart = echarts.init(impactChartRef.value)

  const highCount = lessons.value.filter(l => l.impact === 'High').length
  const mediumCount = lessons.value.filter(l => l.impact === 'Medium').length
  const lowCount = lessons.value.filter(l => l.impact === 'Low').length

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} lessons)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: highCount, name: 'High Impact', itemStyle: { color: '#f56c6c' } },
        { value: mediumCount, name: 'Medium Impact', itemStyle: { color: '#e6a23c' } },
        { value: lowCount, name: 'Low Impact', itemStyle: { color: '#67c23a' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  impactChart.setOption(option)
  window.addEventListener('resize', () => impactChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleQuickFilter = () => {
  currentPage.value = 1
  initTrendChart()
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.category = ''
  filters.impact = ''
  filters.status = ''
  filters.dateRange = null
  quickFilter.value = 'all'
  currentPage.value = 1
  ElMessage.success('Filters reset')
  initTrendChart()
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredLessons.value.length} lessons...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchLessons = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleCreateLesson = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    id: 0,
    title: '',
    category: '',
    impact: 'Medium',
    status: 'Active',
    whatHappened: '',
    rootCause: '',
    lesson: '',
    recommendations: '',
    relatedDecision: '',
    relatedDecisionId: 0,
    createdBy: 'Current User',
    createdAt: new Date().toISOString().split('T')[0],
    updatedAt: new Date().toISOString().split('T')[0],
    lastReviewed: new Date().toISOString().split('T')[0],
    views: 0,
    likes: 0,
    tags: [],
    actionItems: []
  })
  dialogVisible.value = true
}

const viewLesson = (lesson: Lesson) => {
  const index = lessons.value.findIndex(l => l.id === lesson.id)
  if (index !== -1) {
    lessons.value[index].views++
  }
  currentLesson.value = lesson
  detailDialogVisible.value = true
}

const implementLesson = (lesson: Lesson) => {
  implementTarget.value = lesson
  implementationNotes.value = ''
  implementDialogVisible.value = true
}

const confirmImplement = () => {
  if (implementTarget.value) {
    const index = lessons.value.findIndex(l => l.id === implementTarget.value!.id)
    if (index !== -1) {
      lessons.value[index].status = 'Implemented'
      lessons.value[index].updatedAt = new Date().toISOString().split('T')[0]
      ElMessage.success(`Lesson "${implementTarget.value.title}" marked as implemented`)
    }
  }
  implementDialogVisible.value = false
  implementTarget.value = null
  implementationNotes.value = ''
  initImpactChart()
}

const shareLesson = (lesson: Lesson | null) => {
  if (lesson) {
    ElMessage.success(`Share link for "${lesson.title}" copied to clipboard`)
  }
}

const likeLesson = () => {
  if (currentLesson.value) {
    const index = lessons.value.findIndex(l => l.id === currentLesson.value!.id)
    if (index !== -1) {
      lessons.value[index].likes++
      currentLesson.value.likes++
      ElMessage.success('Thanks for your feedback!')
    }
  }
}

const deleteLesson = (lesson: Lesson) => {
  deleteTarget.value = lesson
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = lessons.value.findIndex(l => l.id === deleteTarget.value!.id)
    if (index !== -1) {
      lessons.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
      initImpactChart()
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'create') {
        const newLesson: Lesson = {
          ...formData,
          id: Date.now(),
          createdAt: new Date().toISOString().split('T')[0],
          updatedAt: new Date().toISOString().split('T')[0],
          lastReviewed: new Date().toISOString().split('T')[0],
          views: 0,
          likes: 0,
          actionItems: []
        }
        lessons.value.unshift(newLesson)
        ElMessage.success('Lesson created successfully')
      } else if (dialogMode.value === 'edit') {
        const index = lessons.value.findIndex(l => l.id === formData.id)
        if (index !== -1) {
          lessons.value[index] = { ...formData, updatedAt: new Date().toISOString().split('T')[0] }
          ElMessage.success('Lesson updated successfully')
        }
      }
      dialogVisible.value = false
      initImpactChart()
      currentPage.value = 1
    }
  })
}

const viewRelatedDecision = () => {
  ElMessage.info(`Viewing related decision: ${currentLesson.value?.relatedDecision}`)
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
    initImpactChart()
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
      fetchLessons()
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
.lessons-page {
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

.trend-chart-card, .distribution-card {
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

.quick-filters-card {
  margin-bottom: 20px;

  .quick-filters {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;

    .filter-label {
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

.lesson-detail {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #ebeef5;

    .lesson-meta {
      display: flex;
      gap: 8px;
    }

    .lesson-stats {
      display: flex;
      gap: 16px;
      color: #909399;
      font-size: 13px;

      span {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  .detail-section {
    margin-bottom: 24px;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 2px solid #409eff;
      display: inline-block;
    }

    p {
      color: #606266;
      line-height: 1.6;
      margin: 0;
    }

    ul {
      margin: 0;
      padding-left: 20px;

      li {
        color: #606266;
        line-height: 1.8;
      }
    }

    .lesson-box {
      background: #f5f7fa;
      padding: 16px;
      border-radius: 8px;
      border-left: 4px solid #409eff;
      font-style: italic;
      color: #303133;
    }
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