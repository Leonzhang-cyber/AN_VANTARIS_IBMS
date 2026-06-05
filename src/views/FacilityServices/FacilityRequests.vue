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
          <span class="loading-title">Facility Requests</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Service Request Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="facility-requests-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Tickets /></el-icon>
          Facility Requests
        </h1>
        <div class="page-subtitle">Manage and track facility service requests</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> New Request
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
          <div class="stat-value">{{ stats.totalRequests }}</div>
          <div class="stat-label">Total Requests</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pendingRequests }}</div>
          <div class="stat-label">Pending</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.completedRequests }}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgResponseTime }}<span class="unit">hrs</span></div>
          <div class="stat-label">Avg Response Time</div>
        </div>
      </div>
    </div>

    <!-- Tab View -->
    <div class="main-tabs">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="All Requests" name="all">
          <template #label>
            <span><el-icon><List /></el-icon> All Requests</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Pending" name="pending">
          <template #label>
            <span><el-icon><Clock /></el-icon> Pending</span>
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
            placeholder="Search by title or requester..."
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
        <el-select v-model="typeFilter" placeholder="Request Type" clearable style="width: 140px">
          <el-option label="Maintenance" value="Maintenance" />
          <el-option label="Cleaning" value="Cleaning" />
          <el-option label="Repair" value="Repair" />
          <el-option label="Installation" value="Installation" />
          <el-option label="Inspection" value="Inspection" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Showing {{ filteredRequests.length }} requests</span>
      </div>
    </div>

    <!-- Requests Table -->
    <div class="table-container">
      <el-table
          :data="paginatedRequests"
          stripe
          border
          style="width: 100%"
          v-loading="tableLoading"
          @row-click="viewRequest"
      >
        <el-table-column prop="id" label="ID" width="80" sortable />
        <el-table-column prop="title" label="Title" min-width="200" sortable />
        <el-table-column prop="requester" label="Requester" width="140" sortable />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ row.priority.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="Location" width="140" />
        <el-table-column prop="submittedDate" label="Submitted" width="110" sortable />
        <el-table-column prop="assignedTo" label="Assigned To" width="130" />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="viewRequest(row)">View</el-button>
            <el-button type="primary" link size="small" @click.stop="editRequest(row)">Edit</el-button>
            <el-button type="danger" link size="small" @click.stop="deleteRequest(row)">Delete</el-button>
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

    <!-- Create/Edit Request Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="650px" class="request-dialog" destroy-on-close>
      <el-form :model="requestForm" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Title" prop="title">
              <el-input v-model="requestForm.title" placeholder="Enter request title" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Request Type" prop="type">
              <el-select v-model="requestForm.type" placeholder="Select type" style="width: 100%">
                <el-option label="Maintenance" value="Maintenance" />
                <el-option label="Cleaning" value="Cleaning" />
                <el-option label="Repair" value="Repair" />
                <el-option label="Installation" value="Installation" />
                <el-option label="Inspection" value="Inspection" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority" prop="priority">
              <el-select v-model="requestForm.priority" placeholder="Select priority" style="width: 100%">
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
            <el-form-item label="Location" prop="location">
              <el-input v-model="requestForm.location" placeholder="Enter location" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Requester" prop="requester">
              <el-input v-model="requestForm.requester" placeholder="Enter requester name" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Contact Email" prop="contactEmail">
              <el-input v-model="requestForm.contactEmail" placeholder="Enter email address" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Contact Phone" prop="contactPhone">
              <el-input v-model="requestForm.contactPhone" placeholder="Enter phone number" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Assigned To" prop="assignedTo">
              <el-select v-model="requestForm.assignedTo" placeholder="Assign to staff" clearable style="width: 100%">
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
              <el-select v-model="requestForm.status" placeholder="Select status" style="width: 100%">
                <el-option label="Pending" value="pending" />
                <el-option label="In Progress" value="in-progress" />
                <el-option label="Completed" value="completed" />
                <el-option label="Cancelled" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description" prop="description">
          <el-input v-model="requestForm.description" type="textarea" :rows="3" placeholder="Detailed description of the request..." />
        </el-form-item>

        <el-form-item label="Resolution Notes" prop="resolutionNotes" v-if="requestForm.status === 'completed'">
          <el-input v-model="requestForm.resolutionNotes" type="textarea" :rows="2" placeholder="Notes about resolution..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRequest">Save Request</el-button>
      </template>
    </el-dialog>

    <!-- View Request Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="selectedRequest?.title" width="700px" class="view-dialog">
      <div v-if="selectedRequest" class="request-detail">
        <div class="detail-header" :class="selectedRequest.priority">
          <div class="detail-icon">
            <el-icon><Tickets /></el-icon>
          </div>
          <div class="detail-info">
            <div class="detail-id">Request #{{ selectedRequest.id }}</div>
            <div class="detail-title">{{ selectedRequest.title }}</div>
          </div>
          <div class="detail-status">
            <el-tag :type="getStatusTagType(selectedRequest.status)" size="large">
              {{ getStatusText(selectedRequest.status) }}
            </el-tag>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Request Type">
            <el-tag :type="getTypeTagType(selectedRequest.type)" size="small">{{ selectedRequest.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(selectedRequest.priority)" size="small">
              {{ selectedRequest.priority.toUpperCase() }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Requester">{{ selectedRequest.requester }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedRequest.location }}</el-descriptions-item>
          <el-descriptions-item label="Contact Email">{{ selectedRequest.contactEmail }}</el-descriptions-item>
          <el-descriptions-item label="Contact Phone">{{ selectedRequest.contactPhone }}</el-descriptions-item>
          <el-descriptions-item label="Submitted Date">{{ selectedRequest.submittedDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Updated">{{ selectedRequest.lastUpdated }}</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ selectedRequest.assignedTo || 'Unassigned' }}</el-descriptions-item>
          <el-descriptions-item label="Completed Date">{{ selectedRequest.completedDate || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedRequest.description }}</el-descriptions-item>
          <el-descriptions-item label="Resolution Notes" :span="2" v-if="selectedRequest.resolutionNotes">{{ selectedRequest.resolutionNotes }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editRequest(selectedRequest)">Edit Request</el-button>
        <el-button type="success" @click="updateStatus(selectedRequest, 'in-progress')" v-if="selectedRequest?.status === 'pending'">
          Start Progress
        </el-button>
        <el-button type="success" @click="updateStatus(selectedRequest, 'completed')" v-if="selectedRequest?.status === 'in-progress'">
          Mark Complete
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Tickets, Plus, Download, Refresh, Search, List, Clock,
  CircleCheck, Loading, Document
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading facility requests...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading facility requests...',
  'Loading request data...',
  'Processing queue...',
  'Almost ready...'
]

// ==================== Types ====================
interface FacilityRequest {
  id: number
  title: string
  type: 'Maintenance' | 'Cleaning' | 'Repair' | 'Installation' | 'Inspection'
  priority: 'critical' | 'high' | 'medium' | 'low'
  location: string
  requester: string
  contactEmail: string
  contactPhone: string
  description: string
  resolutionNotes: string | null
  assignedTo: string | null
  status: 'pending' | 'in-progress' | 'completed' | 'cancelled'
  submittedDate: string
  lastUpdated: string
  completedDate: string | null
}

// ==================== Mock Data (25 requests) ====================
const facilityRequests = ref<FacilityRequest[]>([
  { id: 1001, title: 'AC not cooling properly', type: 'Maintenance', priority: 'high', location: 'Server Room A', requester: 'John Smith', contactEmail: 'john.smith@ibms.com', contactPhone: '+65 9123 4567', description: 'The air conditioning unit is blowing warm air. Room temperature is rising.', resolutionNotes: null, assignedTo: 'John Chen', status: 'pending', submittedDate: '2024-06-10', lastUpdated: '2024-06-10', completedDate: null },
  { id: 1002, title: 'Light bulb replacement', type: 'Maintenance', priority: 'low', location: 'Conference Room B', requester: 'Sarah Lee', contactEmail: 'sarah.lee@ibms.com', contactPhone: '+65 9234 5678', description: 'Several light bulbs are not working in Conference Room B.', resolutionNotes: 'All bulbs replaced', assignedTo: 'David Tan', status: 'completed', submittedDate: '2024-06-09', lastUpdated: '2024-06-10', completedDate: '2024-06-10' },
  { id: 1003, title: 'Water leak in restroom', type: 'Repair', priority: 'critical', location: '2nd Floor Restroom', requester: 'Mike Wong', contactEmail: 'mike.wong@ibms.com', contactPhone: '+65 9345 6789', description: 'Water leaking from the sink pipe. Urgent attention needed.', resolutionNotes: 'Pipe replaced, leak fixed', assignedTo: 'Mike Lim', status: 'completed', submittedDate: '2024-06-08', lastUpdated: '2024-06-09', completedDate: '2024-06-09' },
  { id: 1004, title: 'Carpet cleaning requested', type: 'Cleaning', priority: 'medium', location: 'Executive Office', requester: 'Lisa Tan', contactEmail: 'lisa.tan@ibms.com', contactPhone: '+65 9456 7890', description: 'Carpet needs deep cleaning due to stain.', resolutionNotes: null, assignedTo: 'Sarah Wong', status: 'in-progress', submittedDate: '2024-06-10', lastUpdated: '2024-06-10', completedDate: null },
  { id: 1005, title: 'New monitor installation', type: 'Installation', priority: 'medium', location: 'IT Department', requester: 'Tom Chen', contactEmail: 'tom.chen@ibms.com', contactPhone: '+65 9567 8901', description: 'Need to install 3 new monitors for the IT team.', resolutionNotes: null, assignedTo: 'Lisa Ng', status: 'pending', submittedDate: '2024-06-11', lastUpdated: '2024-06-11', completedDate: null },
  { id: 1006, title: 'Elevator malfunction', type: 'Repair', priority: 'critical', location: 'Main Lobby', requester: 'Security Team', contactEmail: 'security@ibms.com', contactPhone: '+65 9678 9012', description: 'Elevator making strange noise and not responding to calls.', resolutionNotes: 'Technician dispatched, motor replaced', assignedTo: 'Mike Lim', status: 'completed', submittedDate: '2024-06-07', lastUpdated: '2024-06-08', completedDate: '2024-06-08' },
  { id: 1007, title: 'HVAC annual inspection', type: 'Inspection', priority: 'high', location: 'Mechanical Room', requester: 'Facility Manager', contactEmail: 'facility@ibms.com', contactPhone: '+65 9789 0123', description: 'Annual HVAC system inspection and certification.', resolutionNotes: null, assignedTo: 'John Chen', status: 'pending', submittedDate: '2024-06-11', lastUpdated: '2024-06-11', completedDate: null },
  { id: 1008, title: 'Window cleaning service', type: 'Cleaning', priority: 'low', location: 'All Floors', requester: 'Office Admin', contactEmail: 'admin@ibms.com', contactPhone: '+65 9890 1234', description: 'Monthly window cleaning for all office windows.', resolutionNotes: 'Service completed', assignedTo: 'Sarah Wong', status: 'completed', submittedDate: '2024-06-05', lastUpdated: '2024-06-06', completedDate: '2024-06-06' },
  { id: 1009, title: 'UPS battery replacement', type: 'Maintenance', priority: 'critical', location: 'Server Room', requester: 'IT Manager', contactEmail: 'itmanager@ibms.com', contactPhone: '+65 9901 2345', description: 'UPS batteries need replacement due to age and reduced capacity.', resolutionNotes: null, assignedTo: 'John Chen', status: 'in-progress', submittedDate: '2024-06-09', lastUpdated: '2024-06-10', completedDate: null },
  { id: 1010, title: 'Door lock repair', type: 'Repair', priority: 'high', location: 'Main Entrance', requester: 'Security', contactEmail: 'security@ibms.com', contactPhone: '+65 9012 3456', description: 'Main entrance door lock is jammed and not closing properly.', resolutionNotes: null, assignedTo: 'David Tan', status: 'pending', submittedDate: '2024-06-11', lastUpdated: '2024-06-11', completedDate: null },
  { id: 1011, title: 'Fire alarm testing', type: 'Inspection', priority: 'high', location: 'Entire Building', requester: 'Safety Officer', contactEmail: 'safety@ibms.com', contactPhone: '+65 9123 4567', description: 'Quarterly fire alarm system testing and inspection.', resolutionNotes: 'All systems operational', assignedTo: 'Mike Lim', status: 'completed', submittedDate: '2024-06-04', lastUpdated: '2024-06-05', completedDate: '2024-06-05' },
  { id: 1012, title: 'Printer toner replacement', type: 'Maintenance', priority: 'low', location: 'Office Area', requester: 'Staff', contactEmail: 'staff@ibms.com', contactPhone: '+65 9234 5678', description: 'Main printer is out of toner.', resolutionNotes: 'Toner replaced', assignedTo: 'David Tan', status: 'completed', submittedDate: '2024-06-10', lastUpdated: '2024-06-10', completedDate: '2024-06-10' },
  { id: 1013, title: 'Parking gate repair', type: 'Repair', priority: 'medium', location: 'Parking Garage', requester: 'Security', contactEmail: 'security@ibms.com', contactPhone: '+65 9345 6789', description: 'Parking gate arm not lifting properly.', resolutionNotes: null, assignedTo: 'Mike Lim', status: 'in-progress', submittedDate: '2024-06-10', lastUpdated: '2024-06-11', completedDate: null },
  { id: 1014, title: 'Conference room AV setup', type: 'Installation', priority: 'medium', location: 'Conference Room A', requester: 'Events Team', contactEmail: 'events@ibms.com', contactPhone: '+65 9456 7890', description: 'New audio-visual equipment needs installation.', resolutionNotes: null, assignedTo: 'Lisa Ng', status: 'pending', submittedDate: '2024-06-11', lastUpdated: '2024-06-11', completedDate: null },
  { id: 1015, title: 'Pest control service', type: 'Cleaning', priority: 'medium', location: 'Cafeteria', requester: 'Cafeteria Manager', contactEmail: 'cafe@ibms.com', contactPhone: '+65 9567 8901', description: 'Pest control treatment needed in cafeteria area.', resolutionNotes: 'Treatment completed', assignedTo: 'Sarah Wong', status: 'completed', submittedDate: '2024-06-06', lastUpdated: '2024-06-07', completedDate: '2024-06-07' },
  { id: 1016, title: 'Server room cooling', type: 'Maintenance', priority: 'critical', location: 'Server Room B', requester: 'IT Manager', contactEmail: 'itmanager@ibms.com', contactPhone: '+65 9678 9012', description: 'Server room temperature rising, AC not cooling sufficiently.', resolutionNotes: null, assignedTo: 'John Chen', status: 'pending', submittedDate: '2024-06-11', lastUpdated: '2024-06-11', completedDate: null },
  { id: 1017, title: 'Window blinds repair', type: 'Repair', priority: 'low', location: 'Office Area', requester: 'Staff', contactEmail: 'staff@ibms.com', contactPhone: '+65 9789 0123', description: 'Window blinds are broken and need repair.', resolutionNotes: 'Blinds replaced', assignedTo: 'David Tan', status: 'completed', submittedDate: '2024-06-08', lastUpdated: '2024-06-09', completedDate: '2024-06-09' },
  { id: 1018, title: 'Electrical outlet inspection', type: 'Inspection', priority: 'medium', location: 'All Floors', requester: 'Safety Officer', contactEmail: 'safety@ibms.com', contactPhone: '+65 9890 1234', description: 'Annual electrical outlet safety inspection.', resolutionNotes: null, assignedTo: 'Mike Lim', status: 'pending', submittedDate: '2024-06-10', lastUpdated: '2024-06-10', completedDate: null },
  { id: 1019, title: 'Office furniture assembly', type: 'Installation', priority: 'low', location: 'New Office', requester: 'HR Department', contactEmail: 'hr@ibms.com', contactPhone: '+65 9901 2345', description: 'Need assistance assembling new office desks and chairs.', resolutionNotes: null, assignedTo: 'David Tan', status: 'pending', submittedDate: '2024-06-11', lastUpdated: '2024-06-11', completedDate: null },
  { id: 1020, title: 'Ceiling leak repair', type: 'Repair', priority: 'high', location: '3rd Floor Hallway', requester: 'Facility Manager', contactEmail: 'facility@ibms.com', contactPhone: '+65 9012 3456', description: 'Water stain on ceiling, possible leak from above floor.', resolutionNotes: null, assignedTo: 'Mike Lim', status: 'in-progress', submittedDate: '2024-06-09', lastUpdated: '2024-06-10', completedDate: null },
  { id: 1021, title: 'Restroom supplies restock', type: 'Maintenance', priority: 'low', location: 'All Restrooms', requester: 'Janitorial', contactEmail: 'janitorial@ibms.com', contactPhone: '+65 9123 4567', description: 'Need restroom supplies replenishment.', resolutionNotes: 'Supplies restocked', assignedTo: 'Sarah Wong', status: 'completed', submittedDate: '2024-06-07', lastUpdated: '2024-06-07', completedDate: '2024-06-07' },
  { id: 1022, title: 'Security camera installation', type: 'Installation', priority: 'high', location: 'Parking Area', requester: 'Security', contactEmail: 'security@ibms.com', contactPhone: '+65 9234 5678', description: 'Install new security cameras in parking area.', resolutionNotes: null, assignedTo: 'Lisa Ng', status: 'pending', submittedDate: '2024-06-10', lastUpdated: '2024-06-10', completedDate: null },
  { id: 1023, title: 'Building facade cleaning', type: 'Cleaning', priority: 'low', location: 'Exterior', requester: 'Management', contactEmail: 'mgmt@ibms.com', contactPhone: '+65 9345 6789', description: 'Annual building exterior cleaning service.', resolutionNotes: 'Cleaning scheduled', assignedTo: 'Sarah Wong', status: 'in-progress', submittedDate: '2024-06-05', lastUpdated: '2024-06-06', completedDate: null },
  { id: 1024, title: 'Generator maintenance', type: 'Maintenance', priority: 'critical', location: 'Generator Room', requester: 'Facility Manager', contactEmail: 'facility@ibms.com', contactPhone: '+65 9456 7890', description: 'Emergency generator needs routine maintenance and testing.', resolutionNotes: null, assignedTo: 'John Chen', status: 'pending', submittedDate: '2024-06-11', lastUpdated: '2024-06-11', completedDate: null },
  { id: 1025, title: 'Chair casters replacement', type: 'Repair', priority: 'low', location: 'Conference Room', requester: 'Staff', contactEmail: 'staff@ibms.com', contactPhone: '+65 9567 8901', description: 'Several office chairs need caster replacement.', resolutionNotes: null, assignedTo: 'David Tan', status: 'pending', submittedDate: '2024-06-10', lastUpdated: '2024-06-10', completedDate: null }
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
const dialogTitle = ref('New Request')
const selectedRequest = ref<FacilityRequest | null>(null)
const editingRequest = ref<FacilityRequest | null>(null)
const formRef = ref()

const requestForm = ref({
  id: null as number | null,
  title: '',
  type: 'Maintenance' as 'Maintenance' | 'Cleaning' | 'Repair' | 'Installation' | 'Inspection',
  priority: 'medium' as 'critical' | 'high' | 'medium' | 'low',
  location: '',
  requester: '',
  contactEmail: '',
  contactPhone: '',
  description: '',
  resolutionNotes: '',
  assignedTo: '',
  status: 'pending' as 'pending' | 'in-progress' | 'completed' | 'cancelled'
})

const formRules = {
  title: [{ required: true, message: 'Please enter request title', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select request type', trigger: 'change' }],
  location: [{ required: true, message: 'Please enter location', trigger: 'blur' }],
  requester: [{ required: true, message: 'Please enter requester name', trigger: 'blur' }],
  description: [{ required: true, message: 'Please enter description', trigger: 'blur' }]
}

// ==================== Computed ====================
const stats = computed(() => {
  const totalRequests = facilityRequests.value.length
  const pendingRequests = facilityRequests.value.filter(r => r.status === 'pending').length
  const inProgressRequests = facilityRequests.value.filter(r => r.status === 'in-progress').length
  const completedRequests = facilityRequests.value.filter(r => r.status === 'completed').length

  // Calculate avg response time (mock)
  const avgResponseTime = 4.2

  return {
    totalRequests,
    pendingRequests,
    inProgressRequests,
    completedRequests,
    avgResponseTime
  }
})

const filteredRequests = computed(() => {
  let filtered = [...facilityRequests.value]

  if (activeTab.value !== 'all') {
    filtered = filtered.filter(r => r.status === activeTab.value)
  }

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(search) ||
        r.requester.toLowerCase().includes(search) ||
        r.location.toLowerCase().includes(search)
    )
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(r => r.priority === priorityFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(r => r.type === typeFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredRequests.value.length)

const paginatedRequests = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRequests.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getTypeTagType = (type: string): string => {
  const map: Record<string, string> = {
    Maintenance: 'primary', Cleaning: 'success', Repair: 'warning',
    Installation: 'info', Inspection: 'danger'
  }
  return map[type] || 'info'
}

const getPriorityTagType = (priority: string): string => {
  const map: Record<string, string> = { critical: 'danger', high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { pending: 'warning', 'in-progress': 'primary', completed: 'success', cancelled: 'info' }
  return map[status] || 'info'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { pending: 'Pending', 'in-progress': 'In Progress', completed: 'Completed', cancelled: 'Cancelled' }
  return map[status] || status
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

const openCreateDialog = () => {
  dialogTitle.value = 'New Request'
  editingRequest.value = null
  requestForm.value = {
    id: null,
    title: '',
    type: 'Maintenance',
    priority: 'medium',
    location: '',
    requester: '',
    contactEmail: '',
    contactPhone: '',
    description: '',
    resolutionNotes: '',
    assignedTo: '',
    status: 'pending'
  }
  dialogVisible.value = true
}

const editRequest = (request: FacilityRequest | null) => {
  if (!request) return
  dialogTitle.value = 'Edit Request'
  editingRequest.value = request
  requestForm.value = {
    id: request.id,
    title: request.title,
    type: request.type,
    priority: request.priority,
    location: request.location,
    requester: request.requester,
    contactEmail: request.contactEmail,
    contactPhone: request.contactPhone,
    description: request.description,
    resolutionNotes: request.resolutionNotes || '',
    assignedTo: request.assignedTo || '',
    status: request.status
  }
  dialogVisible.value = true
}

const viewRequest = (request: FacilityRequest) => {
  selectedRequest.value = request
  viewDialogVisible.value = true
}

const deleteRequest = (request: FacilityRequest) => {
  ElMessageBox.confirm(
      `Delete request "${request.title}"? This action cannot be undone.`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = facilityRequests.value.findIndex(r => r.id === request.id)
    if (index !== -1) {
      facilityRequests.value.splice(index, 1)
      ElMessage.success('Request deleted')
    }
  }).catch(() => {})
}

const saveRequest = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    const now = new Date().toISOString().slice(0, 10)

    if (editingRequest.value) {
      const index = facilityRequests.value.findIndex(r => r.id === editingRequest.value!.id)
      if (index !== -1) {
        facilityRequests.value[index] = {
          ...facilityRequests.value[index],
          title: requestForm.value.title,
          type: requestForm.value.type,
          priority: requestForm.value.priority,
          location: requestForm.value.location,
          requester: requestForm.value.requester,
          contactEmail: requestForm.value.contactEmail,
          contactPhone: requestForm.value.contactPhone,
          description: requestForm.value.description,
          resolutionNotes: requestForm.value.resolutionNotes || null,
          assignedTo: requestForm.value.assignedTo || null,
          status: requestForm.value.status,
          lastUpdated: now,
          completedDate: requestForm.value.status === 'completed' ? now : facilityRequests.value[index].completedDate
        }
        ElMessage.success('Request updated')
      }
    } else {
      const newId = Math.max(...facilityRequests.value.map(r => r.id), 0) + 1
      facilityRequests.value.push({
        id: newId,
        title: requestForm.value.title,
        type: requestForm.value.type,
        priority: requestForm.value.priority,
        location: requestForm.value.location,
        requester: requestForm.value.requester,
        contactEmail: requestForm.value.contactEmail,
        contactPhone: requestForm.value.contactPhone,
        description: requestForm.value.description,
        resolutionNotes: null,
        assignedTo: requestForm.value.assignedTo || null,
        status: 'pending',
        submittedDate: now,
        lastUpdated: now,
        completedDate: null
      })
      ElMessage.success('Request created')
    }

    dialogVisible.value = false
  })
}

const updateStatus = (request: FacilityRequest | null, newStatus: string) => {
  if (!request) return

  const index = facilityRequests.value.findIndex(r => r.id === request.id)
  if (index !== -1) {
    const now = new Date().toISOString().slice(0, 10)
    facilityRequests.value[index] = {
      ...facilityRequests.value[index],
      status: newStatus as any,
      lastUpdated: now,
      completedDate: newStatus === 'completed' ? now : facilityRequests.value[index].completedDate
    }
    ElMessage.success(`Request status updated to ${getStatusText(newStatus)}`)
    viewDialogVisible.value = false
    selectedRequest.value = facilityRequests.value[index]
  }
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Request data exported')
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
.facility-requests-page {
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
.request-dialog :deep(.el-dialog__body) {
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

.detail-id {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.detail-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
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
}
</style>