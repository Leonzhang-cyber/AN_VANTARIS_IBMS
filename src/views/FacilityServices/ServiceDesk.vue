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
          <span class="loading-title">Service Desk</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">IT Service Management Platform</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="service-desk-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Headset /></el-icon>
          Service Desk
        </h1>
        <div class="page-subtitle">IT service management and support ticket system</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateTicket">
          <el-icon><Plus /></el-icon> New Ticket
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
          <el-icon><Tickets /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalTickets }}</div>
          <div class="stat-label">Total Tickets</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.openTickets }}</div>
          <div class="stat-label">Open Tickets</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.resolvedTickets }}</div>
          <div class="stat-label">Resolved (30d)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.slaCompliance }}<span class="unit">%</span></div>
          <div class="stat-label">SLA Compliance</div>
        </div>
      </div>
    </div>

    <!-- Tab View -->
    <div class="main-tabs">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="My Tickets" name="my-tickets">
          <template #label>
            <span><el-icon><User /></el-icon> My Tickets</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Unassigned" name="unassigned">
          <template #label>
            <span><el-icon><UserFilled /></el-icon> Unassigned</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="In Progress" name="in-progress">
          <template #label>
            <span><el-icon><Loading /></el-icon> In Progress</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Resolved" name="resolved">
          <template #label>
            <span><el-icon><CircleCheck /></el-icon> Resolved</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="All Tickets" name="all">
          <template #label>
            <span><el-icon><List /></el-icon> All Tickets</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by subject or requester..."
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
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option label="Hardware" value="Hardware" />
          <el-option label="Software" value="Software" />
          <el-option label="Network" value="Network" />
          <el-option label="Access" value="Access" />
          <el-option label="Facility" value="Facility" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Showing {{ filteredTickets.length }} tickets</span>
      </div>
    </div>

    <!-- Tickets Table -->
    <div class="table-container">
      <el-table
          :data="paginatedTickets"
          stripe
          border
          style="width: 100%"
          v-loading="tableLoading"
          @row-click="viewTicket"
      >
        <el-table-column prop="id" label="ID" width="80" sortable />
        <el-table-column prop="subject" label="Subject" min-width="220" sortable />
        <el-table-column prop="requester" label="Requester" width="140" sortable />
        <el-table-column prop="category" label="Category" width="110">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ row.priority.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="assignedTo" label="Assigned To" width="130" />
        <el-table-column prop="createdDate" label="Created" width="110" sortable />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="SLA" width="80">
          <template #default="{ row }">
            <el-progress
                :percentage="row.slaProgress"
                :stroke-width="6"
                :color="getSlaColor(row.slaProgress)"
                :show-text="true"
                :format="() => `${row.slaProgress}%`"
            />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="viewTicket(row)">View</el-button>
            <el-button type="primary" link size="small" @click.stop="editTicket(row)">Edit</el-button>
            <el-button type="danger" link size="small" @click.stop="deleteTicket(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Create/Edit Ticket Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" class="ticket-dialog" destroy-on-close>
      <el-form :model="ticketForm" :rules="formRules" ref="formRef" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Subject" prop="subject">
              <el-input v-model="ticketForm.subject" placeholder="Enter ticket subject" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Category" prop="category">
              <el-select v-model="ticketForm.category" placeholder="Select category" style="width: 100%">
                <el-option label="Hardware" value="Hardware" />
                <el-option label="Software" value="Software" />
                <el-option label="Network" value="Network" />
                <el-option label="Access" value="Access" />
                <el-option label="Facility" value="Facility" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority" prop="priority">
              <el-select v-model="ticketForm.priority" placeholder="Select priority" style="width: 100%">
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
            <el-form-item label="Requester" prop="requester">
              <el-input v-model="ticketForm.requester" placeholder="Enter requester name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Contact Email" prop="contactEmail">
              <el-input v-model="ticketForm.contactEmail" placeholder="Enter email address" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Assigned To" prop="assignedTo">
              <el-select v-model="ticketForm.assignedTo" placeholder="Assign to agent" clearable style="width: 100%">
                <el-option label="John Chen" value="John Chen" />
                <el-option label="Sarah Wong" value="Sarah Wong" />
                <el-option label="Mike Lim" value="Mike Lim" />
                <el-option label="David Tan" value="David Tan" />
                <el-option label="Lisa Ng" value="Lisa Ng" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="ticketForm.status" placeholder="Select status" style="width: 100%">
                <el-option label="Open" value="open" />
                <el-option label="In Progress" value="in-progress" />
                <el-option label="Resolved" value="resolved" />
                <el-option label="Closed" value="closed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description" prop="description">
          <el-input v-model="ticketForm.description" type="textarea" :rows="3" placeholder="Detailed description of the issue..." />
        </el-form-item>

        <el-form-item label="Resolution Notes" prop="resolution" v-if="ticketForm.status === 'resolved' || ticketForm.status === 'closed'">
          <el-input v-model="ticketForm.resolution" type="textarea" :rows="2" placeholder="How was this issue resolved?" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTicket">Save Ticket</el-button>
      </template>
    </el-dialog>

    <!-- View Ticket Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="`Ticket #${selectedTicket?.id}`" width="750px" class="view-dialog">
      <div v-if="selectedTicket" class="ticket-detail">
        <div class="detail-header" :class="selectedTicket.priority">
          <div class="detail-icon">
            <el-icon><Tickets /></el-icon>
          </div>
          <div class="detail-info">
            <div class="detail-subject">{{ selectedTicket.subject }}</div>
            <div class="detail-meta">
              <span><el-icon><User /></el-icon> {{ selectedTicket.requester }}</span>
              <span><el-icon><Clock /></el-icon> Created: {{ selectedTicket.createdDate }}</span>
            </div>
          </div>
          <div class="detail-status">
            <el-tag :type="getStatusTagType(selectedTicket.status)" size="large">
              {{ getStatusText(selectedTicket.status) }}
            </el-tag>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Ticket ID">#{{ selectedTicket.id }}</el-descriptions-item>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryTagType(selectedTicket.category)" size="small">{{ selectedTicket.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(selectedTicket.priority)" size="small">
              {{ selectedTicket.priority.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="SLA Status">
            <el-progress
                :percentage="selectedTicket.slaProgress"
                :stroke-width="8"
                :color="getSlaColor(selectedTicket.slaProgress)"
                :show-text="true"
                style="width: 150px"
            />
          </el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ selectedTicket.assignedTo || 'Unassigned' }}</el-descriptions-item>
          <el-descriptions-item label="Contact Email">{{ selectedTicket.contactEmail }}</el-descriptions-item>
          <el-descriptions-item label="Created Date">{{ selectedTicket.createdDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Updated">{{ selectedTicket.lastUpdated }}</el-descriptions-item>
          <el-descriptions-item label="Resolved Date">{{ selectedTicket.resolvedDate || 'Not yet' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedTicket.description }}</el-descriptions-item>
          <el-descriptions-item label="Resolution Notes" :span="2" v-if="selectedTicket.resolution">{{ selectedTicket.resolution }}</el-descriptions-item>
        </el-descriptions>

        <!-- Activity Timeline -->
        <div class="activity-section">
          <div class="section-title">Activity Timeline</div>
          <div class="timeline">
            <div v-for="(activity, idx) in selectedTicket.activities" :key="idx" class="timeline-item">
              <div class="timeline-dot" :class="activity.type"></div>
              <div class="timeline-content">
                <div class="timeline-title">{{ activity.title }}</div>
                <div class="timeline-desc">{{ activity.description }}</div>
                <div class="timeline-time">{{ activity.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editTicket(selectedTicket)">Edit Ticket</el-button>
        <el-button type="success" @click="updateStatus(selectedTicket, 'in-progress')" v-if="selectedTicket?.status === 'open'">
          Start Progress
        </el-button>
        <el-button type="success" @click="updateStatus(selectedTicket, 'resolved')" v-if="selectedTicket?.status === 'in-progress'">
          Mark Resolved
        </el-button>
        <el-button type="info" @click="updateStatus(selectedTicket, 'closed')" v-if="selectedTicket?.status === 'resolved'">
          Close Ticket
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Headset, Plus, Download, Refresh, Search, List, Clock,
  CircleCheck, Loading, User, UserFilled, Tickets, DataLine
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading service desk data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading service desk data...',
  'Loading ticket queue...',
  'Analyzing SLA metrics...',
  'Almost ready...'
]

// ==================== Types ====================
interface TicketActivity {
  title: string
  description: string
  time: string
  type: 'created' | 'assigned' | 'updated' | 'resolved' | 'comment'
}

interface ServiceTicket {
  id: number
  subject: string
  category: 'Hardware' | 'Software' | 'Network' | 'Access' | 'Facility'
  priority: 'critical' | 'high' | 'medium' | 'low'
  requester: string
  contactEmail: string
  description: string
  resolution: string | null
  assignedTo: string | null
  status: 'open' | 'in-progress' | 'resolved' | 'closed'
  createdDate: string
  lastUpdated: string
  resolvedDate: string | null
  slaDeadline: string
  slaProgress: number
  activities: TicketActivity[]
}

// ==================== Mock Data (25 tickets) ====================
const serviceTickets = ref<ServiceTicket[]>([
  { id: 1001, subject: 'Unable to access network drive', category: 'Network', priority: 'high', requester: 'John Smith', contactEmail: 'john.smith@ibms.com', description: 'Cannot access shared network drive G: drive after recent update.', resolution: null, assignedTo: 'Lisa Ng', status: 'in-progress', createdDate: '2024-06-10', lastUpdated: '2024-06-10', resolvedDate: null, slaDeadline: '2024-06-12', slaProgress: 50, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by John Smith', time: '2024-06-10 09:30', type: 'created' },
      { title: 'Assigned', description: 'Assigned to Lisa Ng', time: '2024-06-10 10:00', type: 'assigned' },
      { title: 'In Progress', description: 'Investigating network permissions', time: '2024-06-10 10:30', type: 'updated' }
    ] },
  { id: 1002, subject: 'Printer not working', category: 'Hardware', priority: 'medium', requester: 'Sarah Lee', contactEmail: 'sarah.lee@ibms.com', description: 'Office printer HP LaserJet is not printing. Shows error code E2.', resolution: null, assignedTo: 'David Tan', status: 'open', createdDate: '2024-06-11', lastUpdated: '2024-06-11', resolvedDate: null, slaDeadline: '2024-06-13', slaProgress: 25, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Sarah Lee', time: '2024-06-11 08:45', type: 'created' }
    ] },
  { id: 1003, subject: 'Software license request - Adobe', category: 'Software', priority: 'low', requester: 'Mike Wong', contactEmail: 'mike.wong@ibms.com', description: 'Need Adobe Creative Cloud license for graphic design team.', resolution: 'License purchased and assigned', assignedTo: 'Lisa Ng', status: 'resolved', createdDate: '2024-06-05', lastUpdated: '2024-06-06', resolvedDate: '2024-06-06', slaDeadline: '2024-06-10', slaProgress: 100, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Mike Wong', time: '2024-06-05 11:20', type: 'created' },
      { title: 'Assigned', description: 'Assigned to Lisa Ng', time: '2024-06-05 13:00', type: 'assigned' },
      { title: 'Resolved', description: 'License purchased and assigned', time: '2024-06-06 09:15', type: 'resolved' }
    ] },
  { id: 1004, subject: 'VPN connection dropping', category: 'Network', priority: 'critical', requester: 'IT Manager', contactEmail: 'itmanager@ibms.com', description: 'VPN connection drops every 30 minutes. Affecting remote work.', resolution: null, assignedTo: 'Mike Lim', status: 'in-progress', createdDate: '2024-06-10', lastUpdated: '2024-06-11', resolvedDate: null, slaDeadline: '2024-06-11', slaProgress: 75, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by IT Manager', time: '2024-06-10 14:30', type: 'created' },
      { title: 'Assigned', description: 'Assigned to Mike Lim', time: '2024-06-10 15:00', type: 'assigned' },
      { title: 'In Progress', description: 'Analyzing VPN logs', time: '2024-06-11 09:00', type: 'updated' }
    ] },
  { id: 1005, subject: 'Email password reset', category: 'Access', priority: 'high', requester: 'Lisa Tan', contactEmail: 'lisa.tan@ibms.com', description: 'Forgot email password, need reset.', resolution: 'Password reset and instructions sent', assignedTo: 'John Chen', status: 'resolved', createdDate: '2024-06-09', lastUpdated: '2024-06-09', resolvedDate: '2024-06-09', slaDeadline: '2024-06-10', slaProgress: 100, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Lisa Tan', time: '2024-06-09 16:20', type: 'created' },
      { title: 'Resolved', description: 'Password reset', time: '2024-06-09 16:45', type: 'resolved' }
    ] },
  { id: 1006, subject: 'Slow computer performance', category: 'Hardware', priority: 'medium', requester: 'Tom Chen', contactEmail: 'tom.chen@ibms.com', description: 'Computer running very slow, takes minutes to open applications.', resolution: null, assignedTo: 'David Tan', status: 'open', createdDate: '2024-06-11', lastUpdated: '2024-06-11', resolvedDate: null, slaDeadline: '2024-06-13', slaProgress: 10, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Tom Chen', time: '2024-06-11 10:15', type: 'created' }
    ] },
  { id: 1007, subject: 'Zoom audio issues', category: 'Software', priority: 'high', requester: 'HR Team', contactEmail: 'hr@ibms.com', description: 'Audio not working during Zoom meetings.', resolution: null, assignedTo: 'Lisa Ng', status: 'in-progress', createdDate: '2024-06-10', lastUpdated: '2024-06-10', resolvedDate: null, slaDeadline: '2024-06-12', slaProgress: 40, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by HR Team', time: '2024-06-10 08:00', type: 'created' },
      { title: 'Assigned', description: 'Assigned to Lisa Ng', time: '2024-06-10 08:30', type: 'assigned' }
    ] },
  { id: 1008, subject: 'New employee onboarding', category: 'Access', priority: 'medium', requester: 'HR Dept', contactEmail: 'hr@ibms.com', description: 'Need accounts created for 3 new hires starting next week.', resolution: 'Accounts created and credentials sent', assignedTo: 'John Chen', status: 'resolved', createdDate: '2024-06-03', lastUpdated: '2024-06-04', resolvedDate: '2024-06-04', slaDeadline: '2024-06-07', slaProgress: 100, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by HR Dept', time: '2024-06-03 13:30', type: 'created' },
      { title: 'Resolved', description: 'Accounts created', time: '2024-06-04 11:00', type: 'resolved' }
    ] },
  { id: 1009, subject: 'Server room temperature alert', category: 'Facility', priority: 'critical', requester: 'IT Ops', contactEmail: 'itops@ibms.com', description: 'Server room temperature is above threshold. Alert triggered.', resolution: null, assignedTo: 'John Chen', status: 'open', createdDate: '2024-06-11', lastUpdated: '2024-06-11', resolvedDate: null, slaDeadline: '2024-06-11', slaProgress: 80, activities: [
      { title: 'Ticket Created', description: 'Alert triggered - high temperature', time: '2024-06-11 11:00', type: 'created' }
    ] },
  { id: 1010, subject: 'WiFi connectivity issues', category: 'Network', priority: 'high', requester: 'Sales Team', contactEmail: 'sales@ibms.com', description: 'Intermittent WiFi connectivity in conference rooms.', resolution: null, assignedTo: 'Mike Lim', status: 'in-progress', createdDate: '2024-06-09', lastUpdated: '2024-06-10', resolvedDate: null, slaDeadline: '2024-06-11', slaProgress: 70, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Sales Team', time: '2024-06-09 09:00', type: 'created' },
      { title: 'Assigned', description: 'Assigned to Mike Lim', time: '2024-06-09 10:00', type: 'assigned' }
    ] },
  { id: 1011, subject: 'Laptop battery replacement', category: 'Hardware', priority: 'low', requester: 'Finance Team', contactEmail: 'finance@ibms.com', description: 'Laptop battery not holding charge.', resolution: 'Battery replaced', assignedTo: 'David Tan', status: 'resolved', createdDate: '2024-06-07', lastUpdated: '2024-06-08', resolvedDate: '2024-06-08', slaDeadline: '2024-06-14', slaProgress: 100, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Finance Team', time: '2024-06-07 11:00', type: 'created' },
      { title: 'Resolved', description: 'Battery replaced', time: '2024-06-08 14:00', type: 'resolved' }
    ] },
  { id: 1012, subject: 'Software installation - Office 365', category: 'Software', priority: 'medium', requester: 'Marketing', contactEmail: 'marketing@ibms.com', description: 'Need Office 365 installed on new laptop.', resolution: null, assignedTo: 'Lisa Ng', status: 'open', createdDate: '2024-06-11', lastUpdated: '2024-06-11', resolvedDate: null, slaDeadline: '2024-06-13', slaProgress: 15, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Marketing', time: '2024-06-11 13:00', type: 'created' }
    ] },
  { id: 1013, subject: 'Access card not working', category: 'Access', priority: 'high', requester: 'Security', contactEmail: 'security@ibms.com', description: 'Several employees reporting access card issues at main entrance.', resolution: null, assignedTo: 'John Chen', status: 'in-progress', createdDate: '2024-06-10', lastUpdated: '2024-06-10', resolvedDate: null, slaDeadline: '2024-06-12', slaProgress: 45, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Security', time: '2024-06-10 15:00', type: 'created' },
      { title: 'Assigned', description: 'Assigned to John Chen', time: '2024-06-10 15:30', type: 'assigned' }
    ] },
  { id: 1014, subject: 'Data backup request', category: 'Network', priority: 'medium', requester: 'IT Ops', contactEmail: 'itops@ibms.com', description: 'Need to configure automated backup for critical servers.', resolution: null, assignedTo: 'Mike Lim', status: 'open', createdDate: '2024-06-11', lastUpdated: '2024-06-11', resolvedDate: null, slaDeadline: '2024-06-14', slaProgress: 5, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by IT Ops', time: '2024-06-11 14:30', type: 'created' }
    ] },
  { id: 1015, subject: 'Monitor flickering', category: 'Hardware', priority: 'low', requester: 'Design Team', contactEmail: 'design@ibms.com', description: 'Monitor display flickering intermittently.', resolution: 'Monitor replaced under warranty', assignedTo: 'David Tan', status: 'resolved', createdDate: '2024-06-06', lastUpdated: '2024-06-07', resolvedDate: '2024-06-07', slaDeadline: '2024-06-13', slaProgress: 100, activities: [
      { title: 'Ticket Created', description: 'Ticket submitted by Design Team', time: '2024-06-06 10:00', type: 'created' },
      { title: 'Resolved', description: 'Monitor replaced', time: '2024-06-07 09:00', type: 'resolved' }
    ] }
])

// ==================== State ====================
const activeTab = ref('my-tickets')
const searchText = ref('')
const priorityFilter = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('New Ticket')
const selectedTicket = ref<ServiceTicket | null>(null)
const editingTicket = ref<ServiceTicket | null>(null)
const formRef = ref()

const ticketForm = ref({
  id: null as number | null,
  subject: '',
  category: 'Hardware' as 'Hardware' | 'Software' | 'Network' | 'Access' | 'Facility',
  priority: 'medium' as 'critical' | 'high' | 'medium' | 'low',
  requester: '',
  contactEmail: '',
  description: '',
  resolution: '',
  assignedTo: '',
  status: 'open' as 'open' | 'in-progress' | 'resolved' | 'closed'
})

const formRules = {
  subject: [{ required: true, message: 'Please enter ticket subject', trigger: 'blur' }],
  requester: [{ required: true, message: 'Please enter requester name', trigger: 'blur' }],
  description: [{ required: true, message: 'Please enter description', trigger: 'blur' }]
}

// ==================== Computed ====================
const currentUser = ref('John Chen') // Mock current user

const stats = computed(() => {
  const totalTickets = serviceTickets.value.length
  const openTickets = serviceTickets.value.filter(t => t.status === 'open' || t.status === 'in-progress').length
  const resolvedTickets = serviceTickets.value.filter(t => t.status === 'resolved').length
  const slaCompliance = 94

  return { totalTickets, openTickets, resolvedTickets, slaCompliance }
})

const filteredTickets = computed(() => {
  let filtered = [...serviceTickets.value]

  if (activeTab.value === 'my-tickets') {
    filtered = filtered.filter(t => t.assignedTo === currentUser.value)
  } else if (activeTab.value === 'unassigned') {
    filtered = filtered.filter(t => !t.assignedTo && t.status !== 'closed')
  } else if (activeTab.value === 'in-progress') {
    filtered = filtered.filter(t => t.status === 'in-progress')
  } else if (activeTab.value === 'resolved') {
    filtered = filtered.filter(t => t.status === 'resolved')
  }

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(t =>
        t.subject.toLowerCase().includes(search) ||
        t.requester.toLowerCase().includes(search)
    )
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(t => t.priority === priorityFilter.value)
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(t => t.category === categoryFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredTickets.value.length)

const paginatedTickets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredTickets.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    Hardware: 'primary', Software: 'success', Network: 'warning',
    Access: 'info', Facility: 'danger'
  }
  return map[category] || 'info'
}

const getPriorityTagType = (priority: string): string => {
  const map: Record<string, string> = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { open: 'warning', 'in-progress': 'primary', resolved: 'success', closed: 'info' }
  return map[status] || 'info'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { open: 'Open', 'in-progress': 'In Progress', resolved: 'Resolved', closed: 'Closed' }
  return map[status] || status
}

const getSlaColor = (progress: number): string => {
  if (progress >= 80) return '#ef4444'
  if (progress >= 50) return '#f59e0b'
  return '#22c55e'
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

const openCreateTicket = () => {
  dialogTitle.value = 'New Ticket'
  editingTicket.value = null
  ticketForm.value = {
    id: null,
    subject: '',
    category: 'Hardware',
    priority: 'medium',
    requester: '',
    contactEmail: '',
    description: '',
    resolution: '',
    assignedTo: '',
    status: 'open'
  }
  dialogVisible.value = true
}

const editTicket = (ticket: ServiceTicket | null) => {
  if (!ticket) return
  dialogTitle.value = 'Edit Ticket'
  editingTicket.value = ticket
  ticketForm.value = {
    id: ticket.id,
    subject: ticket.subject,
    category: ticket.category,
    priority: ticket.priority,
    requester: ticket.requester,
    contactEmail: ticket.contactEmail,
    description: ticket.description,
    resolution: ticket.resolution || '',
    assignedTo: ticket.assignedTo || '',
    status: ticket.status
  }
  dialogVisible.value = true
}

const viewTicket = (ticket: ServiceTicket) => {
  selectedTicket.value = ticket
  viewDialogVisible.value = true
}

const deleteTicket = (ticket: ServiceTicket) => {
  ElMessageBox.confirm(
      `Delete ticket #${ticket.id}? This action cannot be undone.`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = serviceTickets.value.findIndex(t => t.id === ticket.id)
    if (index !== -1) {
      serviceTickets.value.splice(index, 1)
      ElMessage.success('Ticket deleted')
    }
  }).catch(() => {})
}

const saveTicket = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    const now = new Date().toISOString().slice(0, 10)
    const currentTime = new Date().toLocaleString()

    if (editingTicket.value) {
      const index = serviceTickets.value.findIndex(t => t.id === editingTicket.value!.id)
      if (index !== -1) {
        const newStatus = ticketForm.value.status
        const newActivity: TicketActivity = {
          title: newStatus === 'resolved' ? 'Resolved' : 'Updated',
          description: newStatus === 'resolved' ? 'Ticket marked as resolved' : 'Ticket information updated',
          time: currentTime,
          type: newStatus === 'resolved' ? 'resolved' : 'updated'
        }

        serviceTickets.value[index] = {
          ...serviceTickets.value[index],
          subject: ticketForm.value.subject,
          category: ticketForm.value.category,
          priority: ticketForm.value.priority,
          requester: ticketForm.value.requester,
          contactEmail: ticketForm.value.contactEmail,
          description: ticketForm.value.description,
          resolution: ticketForm.value.resolution || null,
          assignedTo: ticketForm.value.assignedTo || null,
          status: ticketForm.value.status,
          lastUpdated: now,
          resolvedDate: ticketForm.value.status === 'resolved' ? now : serviceTickets.value[index].resolvedDate,
          activities: [...serviceTickets.value[index].activities, newActivity]
        }
        ElMessage.success('Ticket updated')
      }
    } else {
      const newId = Math.max(...serviceTickets.value.map(t => t.id), 0) + 1
      const slaDeadline = new Date()
      slaDeadline.setDate(slaDeadline.getDate() + 2)

      const newTicket: ServiceTicket = {
        id: newId,
        subject: ticketForm.value.subject,
        category: ticketForm.value.category,
        priority: ticketForm.value.priority,
        requester: ticketForm.value.requester,
        contactEmail: ticketForm.value.contactEmail,
        description: ticketForm.value.description,
        resolution: null,
        assignedTo: ticketForm.value.assignedTo || null,
        status: 'open',
        createdDate: now,
        lastUpdated: now,
        resolvedDate: null,
        slaDeadline: slaDeadline.toISOString().slice(0, 10),
        slaProgress: 0,
        activities: [{ title: 'Ticket Created', description: 'Ticket submitted', time: new Date().toLocaleString(), type: 'created' }]
      }
      serviceTickets.value.unshift(newTicket)
      ElMessage.success('Ticket created')
    }

    dialogVisible.value = false
  })
}

const updateStatus = (ticket: ServiceTicket | null, newStatus: string) => {
  if (!ticket) return

  const index = serviceTickets.value.findIndex(t => t.id === ticket.id)
  if (index !== -1) {
    const now = new Date().toISOString().slice(0, 10)
    const currentTime = new Date().toLocaleString()

    let statusText = ''
    let activityType: 'updated' | 'resolved' = 'updated'
    if (newStatus === 'in-progress') statusText = 'In Progress'
    else if (newStatus === 'resolved') {
      statusText = 'Resolved'
      activityType = 'resolved'
    }
    else if (newStatus === 'closed') statusText = 'Closed'

    const newActivity: TicketActivity = {
      title: `Status changed to ${statusText}`,
      description: `Ticket status updated to ${statusText}`,
      time: currentTime,
      type: activityType
    }

    serviceTickets.value[index] = {
      ...serviceTickets.value[index],
      status: newStatus as any,
      lastUpdated: now,
      resolvedDate: newStatus === 'resolved' ? now : serviceTickets.value[index].resolvedDate,
      activities: [...serviceTickets.value[index].activities, newActivity]
    }
    ElMessage.success(`Ticket status updated to ${statusText}`)
    viewDialogVisible.value = false
    selectedTicket.value = serviceTickets.value[index]
  }
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Ticket data exported')
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
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
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
*::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* ==================== Main Page ==================== */
.service-desk-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
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
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
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
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
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

/* Dialog */
.ticket-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.view-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-radius: 16px;
  margin-bottom: 20px;
}

.detail-header.critical { background: #fee2e2; }
.detail-header.high { background: #fff3e3; }
.detail-header.medium { background: #fef9c3; }
.detail-header.low { background: #dcfce7; }

.detail-icon {
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #3b82f6;
}

.detail-info {
  flex: 1;
}

.detail-subject {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 6px;
}

.detail-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #64748b;
}

.detail-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Activity Timeline */
.activity-section {
  margin-top: 20px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline:before {
  content: '';
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e2e8f0;
}

.timeline-item {
  position: relative;
  margin-bottom: 20px;
}

.timeline-dot {
  position: absolute;
  left: -22px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.timeline-dot.created { background: #3b82f6; }
.timeline-dot.assigned { background: #f59e0b; }
.timeline-dot.updated { background: #8b5cf6; }
.timeline-dot.resolved { background: #22c55e; }
.timeline-dot.comment { background: #64748b; }

.timeline-content {
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 12px;
}

.timeline-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
}

.timeline-desc {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.timeline-time {
  font-size: 11px;
  color: #94a3b8;
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

  .detail-header {
    flex-direction: column;
    text-align: center;
  }

  .detail-meta {
    justify-content: center;
  }
}
</style>