<template>
  <div class="incident-center-container">
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
            <span class="loading-title">Loading Incident Center</span>
            <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Incident Management & Response Center</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="incident-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Incident Center</h1>
          <p class="page-subtitle">Centralized incident management, tracking, and response coordination</p>
        </div>
        <div class="header-actions">
          <div class="time-display">
            <el-icon><Clock /></el-icon>
            <span>{{ currentTime }}</span>
          </div>
          <el-button type="primary" @click="createIncident">
            <el-icon><Plus /></el-icon>
            Create Incident
          </el-button>
          <el-button @click="exportIncidentReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
          <el-button @click="openIncidentSettings">
            <el-icon><Setting /></el-icon>
            Settings
          </el-button>
        </div>
      </div>

      <!-- Incident Summary Stats -->
      <div class="incident-stats">
        <div class="stat-card" v-for="stat in incidentStats" :key="stat.label">
          <div class="stat-value" :style="{ color: stat.color }">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-trend" :class="stat.trend">
            {{ stat.change }} from last week
          </div>
        </div>
      </div>

      <!-- Main Tabs -->
      <el-tabs v-model="activeTab" class="incident-tabs">
        <!-- Active Incidents Tab -->
        <el-tab-pane label="Active Incidents" name="active">
          <div class="tab-content">
            <div class="section-header">
              <div class="filter-group">
                <el-input v-model="searchQuery" placeholder="Search incidents..." prefix-icon="Search" style="width: 240px" clearable />
                <el-select v-model="severityFilter" placeholder="Severity" clearable style="width: 120px">
                  <el-option label="Critical" value="critical" />
                  <el-option label="High" value="high" />
                  <el-option label="Medium" value="medium" />
                  <el-option label="Low" value="low" />
                </el-select>
                <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
                  <el-option label="New" value="new" />
                  <el-option label="Investigating" value="investigating" />
                  <el-option label="In Progress" value="in-progress" />
                  <el-option label="Resolved" value="resolved" />
                  <el-option label="Closed" value="closed" />
                </el-select>
                <el-select v-model="typeFilter" placeholder="Type" clearable style="width: 120px">
                  <el-option label="Technical" value="technical" />
                  <el-option label="Security" value="security" />
                  <el-option label="Safety" value="safety" />
                  <el-option label="Operational" value="operational" />
                </el-select>
                <el-date-picker v-model="dateRange" type="daterange" range-separator="To" start-placeholder="Start" end-placeholder="End" style="width: 240px" />
              </div>
              <el-button type="primary" @click="applyFilters">Apply Filters</el-button>
            </div>

            <el-table :data="filteredIncidents" stripe class="incident-table" @row-click="viewIncidentDetail">
              <el-table-column type="index" width="50" />
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="Title" min-width="200" />
              <el-table-column prop="severity" label="Severity" width="100">
                <template #default="{ row }">
                  <el-tag :type="getSeverityTagType(row.severity)" size="small">{{ row.severity.toUpperCase() }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="Type" width="100">
                <template #default="{ row }">
                  <el-tag type="info" size="small">{{ row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="Status" width="120">
                <template #default="{ row }">
                  <el-tag :type="getStatusTagType(row.status)" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="location" label="Location" width="150" />
              <el-table-column prop="assignee" label="Assignee" width="120" />
              <el-table-column prop="reportedTime" label="Reported" width="160" />
              <el-table-column label="Actions" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" link size="small" @click.stop="viewIncidentDetail(row)">View</el-button>
                  <el-button type="success" link size="small" @click.stop="assignIncident(row)">Assign</el-button>
                  <el-button type="warning" link size="small" @click.stop="updateStatusmap(row)">Update</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination-container">
              <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50, 100]" :total="totalIncidents" layout="total, sizes, prev, pager, next, jumper" @size-change="handleSizeChange" @current-change="handleCurrentChange" />
            </div>
          </div>
        </el-tab-pane>

        <!-- Incident Details Panel -->
        <el-tab-pane label="Incident Details" name="details" :disabled="!selectedIncident">
          <div v-if="selectedIncident" class="incident-details-panel">
            <div class="details-header">
              <div class="header-left">
                <h2>{{ selectedIncident.title }}</h2>
                <div class="header-badges">
                  <el-tag :type="getSeverityTagType(selectedIncident.severity)" size="large">{{ selectedIncident.severity.toUpperCase() }}</el-tag>
                  <el-tag :type="getStatusTagType(selectedIncident.status)" size="large">{{ selectedIncident.status }}</el-tag>
                  <el-tag type="info" size="large">ID: {{ selectedIncident.id }}</el-tag>
                </div>
              </div>
              <div class="header-actions">
                <el-button type="primary" @click="editIncident(selectedIncident)">Edit</el-button>
                <el-button type="danger" @click="escalateIncident(selectedIncident)">Escalate</el-button>
                <el-button @click="shareIncident(selectedIncident)">Share</el-button>
              </div>
            </div>

            <el-row :gutter="20">
              <el-col :span="16">
                <!-- Incident Description -->
                <el-card class="detail-card">
                  <template #header>
                    <span class="card-title">Description</span>
                  </template>
                  <p>{{ selectedIncident.description }}</p>
                </el-card>

                <!-- Timeline -->
                <el-card class="detail-card">
                  <template #header>
                    <span class="card-title">Incident Timeline</span>
                  </template>
                  <div class="timeline">
                    <div v-for="event in selectedIncident.timeline" :key="event.id" class="timeline-event">
                      <div class="event-dot" :class="event.type"></div>
                      <div class="event-content">
                        <div class="event-header">
                          <span class="event-title">{{ event.title }}</span>
                          <span class="event-time">{{ event.time }}</span>
                        </div>
                        <div class="event-description">{{ event.description }}</div>
                        <div class="event-user">{{ event.user }}</div>
                      </div>
                    </div>
                  </div>
                </el-card>

                <!-- Attachments -->
                <el-card class="detail-card">
                  <template #header>
                    <span class="card-title">Attachments & Evidence</span>
                    <el-button link @click="addAttachment">+ Add</el-button>
                  </template>
                  <div class="attachment-list">
                    <div v-for="file in selectedIncident.attachments" :key="file.name" class="attachment-item">
                      <el-icon><Document /></el-icon>
                      <span>{{ file.name }}</span>
                      <span class="file-size">{{ file.size }}</span>
                      <el-button link @click="downloadAttachment(file)">Download</el-button>
                    </div>
                  </div>
                </el-card>
              </el-col>

              <el-col :span="8">
                <!-- Incident Metadata -->
                <el-card class="detail-card">
                  <template #header>
                    <span class="card-title">Incident Information</span>
                  </template>
                  <el-descriptions :column="1" border>
                    <el-descriptions-item label="Reported By">{{ selectedIncident.reportedBy }}</el-descriptions-item>
                    <el-descriptions-item label="Reported Time">{{ selectedIncident.reportedTime }}</el-descriptions-item>
                    <el-descriptions-item label="Location">{{ selectedIncident.location }}</el-descriptions-item>
                    <el-descriptions-item label="Category">{{ selectedIncident.type }}</el-descriptions-item>
                    <el-descriptions-item label="Assignee">{{ selectedIncident.assignee }}</el-descriptions-item>
                    <el-descriptions-item label="Response Team">{{ selectedIncident.responseTeam }}</el-descriptions-item>
                    <el-descriptions-item label="SLA Deadline">{{ selectedIncident.slaDeadline }}</el-descriptions-item>
                    <el-descriptions-item label="Time to Resolve">{{ selectedIncident.timeToResolve }}</el-descriptions-item>
                  </el-descriptions>
                </el-card>

                <!-- Affected Assets -->
                <el-card class="detail-card">
                  <template #header>
                    <span class="card-title">Affected Assets</span>
                  </template>
                  <div class="asset-list">
                    <div v-for="asset in selectedIncident.affectedAssets" :key="asset.id" class="asset-item">
                      <el-icon><Cpu /></el-icon>
                      <span>{{ asset.name }}</span>
                      <el-tag :type="getAssetStatusTag(asset.status)" size="small">{{ asset.status }}</el-tag>
                    </div>
                  </div>
                </el-card>

                <!-- Related Incidents -->
                <el-card class="detail-card">
                  <template #header>
                    <span class="card-title">Related Incidents</span>
                  </template>
                  <div class="related-list">
                    <div v-for="related in selectedIncident.relatedIncidents" :key="related.id" class="related-item" @click="viewRelatedIncident(related)">
                      <span>{{ related.id }} - {{ related.title }}</span>
                      <el-icon><ArrowRight /></el-icon>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
          <div v-else class="no-selection">
            <el-icon><Warning /></el-icon>
            <p>Select an incident from the Active Incidents tab to view details</p>
          </div>
        </el-tab-pane>

        <!-- Incident Analytics Tab -->
        <el-tab-pane label="Analytics" name="analytics">
          <div class="analytics-content">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <span class="card-title">Incident Trend</span>
                    <el-select v-model="trendPeriod" size="small" style="width: 100px">
                      <el-option label="Weekly" value="week" />
                      <el-option label="Monthly" value="month" />
                      <el-option label="Yearly" value="year" />
                    </el-select>
                  </template>
                  <div ref="trendChartRef" class="chart-container"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <span class="card-title">Incident by Severity</span>
                  </template>
                  <div ref="severityChartRef" class="chart-container"></div>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <span class="card-title">Incident by Type</span>
                  </template>
                  <div ref="typeChartRef" class="chart-container"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="chart-card">
                  <template #header>
                    <span class="card-title">MTTR by Severity</span>
                  </template>
                  <div ref="mttrChartRef" class="chart-container"></div>
                </el-card>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="24">
                <el-card class="chart-card">
                  <template #header>
                    <span class="card-title">Top Incident Locations</span>
                  </template>
                  <div ref="locationChartRef" class="chart-container" style="height: 300px"></div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- Knowledge Base Tab -->
        <el-tab-pane label="Knowledge Base" name="knowledge">
          <div class="knowledge-content">
            <div class="section-header">
              <el-input v-model="kbSearch" placeholder="Search knowledge base..." prefix-icon="Search" style="width: 300px" />
              <el-button type="primary" @click="addKnowledgeArticle">
                <el-icon><Plus /></el-icon>
                Add Article
              </el-button>
            </div>
            <el-row :gutter="20">
              <el-col :span="8" v-for="article in knowledgeArticles" :key="article.id">
                <el-card class="knowledge-card" shadow="hover" @click="viewArticle(article)">
                  <div class="article-icon" :style="{ background: article.color }">
                    <el-icon><component :is="article.icon" /></el-icon>
                  </div>
                  <div class="article-info">
                    <h4>{{ article.title }}</h4>
                    <p>{{ article.summary }}</p>
                    <div class="article-meta">
                      <span><el-icon><Folder /></el-icon> {{ article.category }}</span>
                      <span><el-icon><View /></el-icon> {{ article.views }} views</span>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="runIncidentAnalysis">
          <el-icon><DataAnalysis /></el-icon>
          Run Incident Analysis
        </el-button>
        <el-button size="large" @click="generatePostMortem">
          <el-icon><Document /></el-icon>
          Generate Post-Mortem
        </el-button>
        <el-button size="large" @click="scheduleReview">
          <el-icon><Calendar /></el-icon>
          Schedule Review Meeting
        </el-button>
      </div>
    </div>

    <!-- Create/Edit Incident Dialog -->
    <el-dialog v-model="incidentDialogVisible" :title="dialogMode === 'create' ? 'Create New Incident' : 'Edit Incident'" width="700px">
      <el-form :model="incidentForm" label-width="120px">
        <el-form-item label="Title" required>
          <el-input v-model="incidentForm.title" placeholder="Enter incident title" />
        </el-form-item>
        <el-form-item label="Description" required>
          <el-input type="textarea" v-model="incidentForm.description" :rows="4" placeholder="Describe the incident" />
        </el-form-item>
        <el-form-item label="Severity" required>
          <el-select v-model="incidentForm.severity" style="width: 100%">
            <el-option label="Critical" value="critical" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="incidentForm.type" style="width: 100%">
            <el-option label="Technical" value="technical" />
            <el-option label="Security" value="security" />
            <el-option label="Safety" value="safety" />
            <el-option label="Operational" value="operational" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location">
          <el-input v-model="incidentForm.location" placeholder="Incident location" />
        </el-form-item>
        <el-form-item label="Assignee">
          <el-select v-model="incidentForm.assignee" style="width: 100%">
            <el-option label="John Smith" value="John Smith" />
            <el-option label="Sarah Chen" value="Sarah Chen" />
            <el-option label="Mike Johnson" value="Mike Johnson" />
            <el-option label="Lisa Wong" value="Lisa Wong" />
          </el-select>
        </el-form-item>
        <el-form-item label="Response Team">
          <el-select v-model="incidentForm.responseTeam" style="width: 100%">
            <el-option label="ERT - Emergency Response" value="ERT" />
            <el-option label="SRT - Security Response" value="SRT" />
            <el-option label="TRT - Technical Response" value="TRT" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="incidentDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveIncident">{{ dialogMode === 'create' ? 'Create' : 'Save' }}</el-button>
      </template>
    </el-dialog>

    <!-- Assign Incident Dialog -->
    <el-dialog v-model="assignDialogVisible" title="Assign Incident" width="450px">
      <el-form>
        <el-form-item label="Incident">
          <span>{{ selectedIncident?.title }}</span>
        </el-form-item>
        <el-form-item label="Assign To">
          <el-select v-model="assignTo" placeholder="Select assignee" style="width: 100%">
            <el-option label="John Smith - Lead Engineer" value="John Smith" />
            <el-option label="Sarah Chen - HVAC Specialist" value="Sarah Chen" />
            <el-option label="Mike Johnson - Electrical" value="Mike Johnson" />
            <el-option label="Lisa Wong - Security" value="Lisa Wong" />
          </el-select>
        </el-form-item>
        <el-form-item label="Response Team">
          <el-select v-model="assignTeam" placeholder="Select team" style="width: 100%">
            <el-option label="Emergency Response Team" value="ERT" />
            <el-option label="Security Response Team" value="SRT" />
            <el-option label="Technical Response Team" value="TRT" />
          </el-select>
        </el-form-item>
        <el-form-item label="Due Date">
          <el-date-picker v-model="assignDueDate" type="datetime" placeholder="Select due date" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAssign">Assign</el-button>
      </template>
    </el-dialog>

    <!-- Update Status Dialog -->
    <el-dialog v-model="statusDialogVisible" title="Update Incident Status" width="450px">
      <el-form>
        <el-form-item label="Incident">
          <span>{{ selectedIncident?.title }}</span>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="updateStatus" placeholder="Select status" style="width: 100%">
            <el-option label="New" value="new" />
            <el-option label="Investigating" value="investigating" />
            <el-option label="In Progress" value="in-progress" />
            <el-option label="Resolved" value="resolved" />
            <el-option label="Closed" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="Resolution Notes">
          <el-input type="textarea" v-model="resolutionNotes" :rows="3" placeholder="Add resolution notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmUpdateStatus">Update</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import * as echarts from 'echarts'
import {
  Clock, Refresh, Download, Setting, Plus, Search, Document, Cpu,
  Warning, ArrowRight, DataAnalysis, Calendar, Folder, View,
  InfoFilled, CircleCheck, CircleClose, User, Location, Timer
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading incident center...')

// ==================== Time ====================
const currentTime = ref('')
let timeInterval: ReturnType<typeof setInterval> | null = null

// ==================== Tab State ====================
const activeTab = ref('active')
const searchQuery = ref('')
const severityFilter = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const dateRange = ref<[Date, Date] | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedIncident = ref<any>(null)
const trendPeriod = ref('week')
const kbSearch = ref('')

// Dialog States
const incidentDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const dialogMode = ref('create')
const assignTo = ref('')
const assignTeam = ref('')
const assignDueDate = ref('')
const updateStatus = ref('')
const resolutionNotes = ref('')

// Incident Stats
const incidentStats = ref([
  { label: 'Active Incidents', value: 8, color: '#ef4444', change: '+2', trend: 'up' },
  { label: 'Critical', value: 3, color: '#dc2626', change: '+1', trend: 'up' },
  { label: 'Resolved (This Month)', value: 24, color: '#10b981', change: '+8', trend: 'up' },
  { label: 'Avg Response Time', value: '4.2m', color: '#3b82f6', change: '-0.8m', trend: 'down' },
  { label: 'MTTR', value: '18m', color: '#8b5cf6', change: '-3m', trend: 'down' },
  { label: 'SLA Compliance', value: '94%', color: '#f59e0b', change: '+2%', trend: 'up' }
])

// Incident Form
const incidentForm = ref({
  title: '',
  description: '',
  severity: 'medium',
  type: 'technical',
  location: '',
  assignee: '',
  responseTeam: ''
})

// ==================== Incidents Data ====================
const incidents = ref([
  { id: 'INC-001', title: 'Cooling System Failure - DC East', severity: 'critical', type: 'technical', status: 'investigating', location: 'Singapore DC East', assignee: 'John Smith', reportedTime: '2024-01-15 08:23:45', responseTeam: 'ERT', slaDeadline: '2024-01-15 10:23:45', timeToResolve: '2h', reportedBy: 'System Monitor', description: 'Temperature spike detected in Data Center East. Chiller unit appears to be malfunctioning. Current temperature is 32°C and rising.', affectedAssets: [{ id: 1, name: 'Chiller-01', status: 'critical' }, { id: 2, name: 'CRAC-01', status: 'warning' }], relatedIncidents: [{ id: 'INC-002', title: 'Power Fluctuation' }], attachments: [{ name: 'temperature_log.csv', size: '2.3 MB' }], timeline: [
      { id: 1, type: 'alert', title: 'Alert Triggered', description: 'Temperature exceeded threshold 28°C', time: '08:23:45', user: 'System' },
      { id: 2, type: 'response', title: 'Team Assigned', description: 'ERT dispatched to location', time: '08:25:12', user: 'Command Center' },
      { id: 3, type: 'update', title: 'Investigation Started', description: 'Initial assessment in progress', time: '08:30:00', user: 'John Smith' }
    ] },
  { id: 'INC-002', title: 'Power Fluctuation - UPS Input', severity: 'critical', type: 'technical', status: 'in-progress', location: 'Cooling Plant', assignee: 'Sarah Chen', reportedTime: '2024-01-15 08:15:22', responseTeam: 'ERT', slaDeadline: '2024-01-15 10:15:22', timeToResolve: '2h', reportedBy: 'Power Monitor', description: 'Voltage fluctuation detected at UPS input. Possible grid instability.', affectedAssets: [{ id: 3, name: 'UPS-01', status: 'warning' }], relatedIncidents: [{ id: 'INC-001', title: 'Cooling System Failure' }], attachments: [], timeline: [] },
  { id: 'INC-003', title: 'Unauthorized Access Attempt', severity: 'high', type: 'security', status: 'resolved', location: 'Office Tower - Floor 3', assignee: 'Lisa Wong', reportedTime: '2024-01-15 07:42:10', responseTeam: 'SRT', slaDeadline: '2024-01-15 09:42:10', timeToResolve: '1.5h', reportedBy: 'Security System', description: 'Multiple failed access attempts at secure door. Access badge revoked and incident contained.', affectedAssets: [], relatedIncidents: [], attachments: [], timeline: [] },
  { id: 'INC-004', title: 'Network Latency Spike', severity: 'medium', type: 'technical', status: 'monitoring', location: 'Network Room', assignee: 'Mike Johnson', reportedTime: '2024-01-15 06:05:33', responseTeam: 'TRT', slaDeadline: '2024-01-15 10:05:33', timeToResolve: '4h', reportedBy: 'Network Monitor', description: 'Unexpected latency increase on backbone network. Under investigation.', affectedAssets: [{ id: 4, name: 'Core Switch', status: 'warning' }], relatedIncidents: [], attachments: [], timeline: [] },
  { id: 'INC-005', title: 'Fire Alarm - False Positive', severity: 'low', type: 'safety', status: 'closed', location: 'Warehouse', assignee: 'David Kim', reportedTime: '2024-01-14 15:30:00', responseTeam: 'SRT', slaDeadline: '2024-01-14 17:30:00', timeToResolve: '2h', reportedBy: 'Fire System', description: 'Fire alarm triggered but determined to be false positive. Sensor sensitivity adjusted.', affectedAssets: [], relatedIncidents: [], attachments: [], timeline: [] },
  { id: 'INC-006', title: 'HVAC Efficiency Drop', severity: 'medium', type: 'technical', status: 'investigating', location: 'DC West', assignee: 'Sarah Chen', reportedTime: '2024-01-14 14:20:00', responseTeam: 'TRT', slaDeadline: '2024-01-15 14:20:00', timeToResolve: '24h', reportedBy: 'System Monitor', description: 'Cooling efficiency dropped by 15%. Investigating potential refrigerant leak.', affectedAssets: [{ id: 5, name: 'Chiller-02', status: 'warning' }], relatedIncidents: [], attachments: [], timeline: [] },
  { id: 'INC-007', title: 'Security Camera Offline', severity: 'low', type: 'security', status: 'resolved', location: 'Parking Lot B', assignee: 'Lisa Wong', reportedTime: '2024-01-14 09:00:00', responseTeam: 'SRT', slaDeadline: '2024-01-14 17:00:00', timeToResolve: '8h', reportedBy: 'VMS System', description: 'Camera offline due to network issue. Restored after switch reboot.', affectedAssets: [], relatedIncidents: [], attachments: [], timeline: [] },
  { id: 'INC-008', title: 'Battery Health Degradation', severity: 'high', type: 'technical', status: 'in-progress', location: 'UPS Room', assignee: 'Mike Johnson', reportedTime: '2024-01-14 08:30:00', responseTeam: 'ERT', slaDeadline: '2024-01-15 08:30:00', timeToResolve: '24h', reportedBy: 'BMS System', description: 'UPS battery health below 70%. Replacement scheduled.', affectedAssets: [{ id: 6, name: 'UPS-02', status: 'critical' }], relatedIncidents: [], attachments: [], timeline: [] }
])

// Knowledge Articles
const knowledgeArticles = ref([
  { id: 1, title: 'Cooling System Troubleshooting', summary: 'Step-by-step guide for diagnosing cooling system issues', category: 'Technical', views: 234, icon: 'Cpu', color: '#3b82f6' },
  { id: 2, title: 'Security Incident Response', summary: 'Standard operating procedures for security breaches', category: 'Security', views: 156, icon: 'Lock', color: '#ef4444' },
  { id: 3, title: 'Power Quality Analysis', summary: 'Understanding and resolving power quality issues', category: 'Technical', views: 98, icon: 'Lightning', color: '#f59e0b' },
  { id: 4, title: 'Emergency Communication Protocol', summary: 'How to communicate during emergencies', category: 'Operational', views: 187, icon: 'Bell', color: '#10b981' },
  { id: 5, title: 'Post-Incident Review Process', summary: 'Conducting effective post-mortem analysis', category: 'Process', views: 67, icon: 'Document', color: '#8b5cf6' },
  { id: 6, title: 'SLA Management Guidelines', summary: 'Managing service level agreements for incidents', category: 'Process', views: 45, icon: 'Timer', color: '#06b6d4' }
])

// Computed
const totalIncidents = computed(() => filteredIncidents.value.length)
const filteredIncidents = computed(() => {
  let result = incidents.value
  if (searchQuery.value) {
    result = result.filter(i => i.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || i.id.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  if (severityFilter.value) {
    result = result.filter(i => i.severity === severityFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter(i => i.status === statusFilter.value)
  }
  if (typeFilter.value) {
    result = result.filter(i => i.type === typeFilter.value)
  }
  return result
})

// Helper Functions
const getSeverityTagType = (severity: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[severity] || 'info'
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    new: 'info',
    investigating: 'warning',
    'in-progress': 'primary',
    resolved: 'success',
    monitoring: 'info',
    closed: 'success'
  }
  return types[status] || 'info'
}

const getAssetStatusTag = (status: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    warning: 'warning',
    healthy: 'success'
  }
  return types[status] || 'info'
}

// Actions
const createIncident = () => {
  dialogMode.value = 'create'
  incidentForm.value = { title: '', description: '', severity: 'medium', type: 'technical', location: '', assignee: '', responseTeam: '' }
  incidentDialogVisible.value = true
}

const exportIncidentReport = () => {
  ElMessage.success('Incident report export started')
}

const openIncidentSettings = () => {
  ElMessage.info('Incident settings will open')
}

const applyFilters = () => {
  ElMessage.success('Filters applied')
}

const viewIncidentDetail = (incident: any) => {
  selectedIncident.value = incident
  activeTab.value = 'details'
}

const assignIncident = (incident: any) => {
  selectedIncident.value = incident
  assignTo.value = incident.assignee
  assignTeam.value = incident.responseTeam
  assignDialogVisible.value = true
}

const updateStatusmap = (incident: any) => {
  selectedIncident.value = incident
  updateStatus.value = incident.status
  resolutionNotes.value = ''
  statusDialogVisible.value = true
}

const editIncident = (incident: any) => {
  dialogMode.value = 'edit'
  incidentForm.value = { ...incident }
  incidentDialogVisible.value = true
}

const escalateIncident = (incident: any) => {
  ElMessage.warning(`Incident ${incident.id} escalated to higher command`)
}

const shareIncident = (incident: any) => {
  ElMessage.info(`Share link for ${incident.id} copied`)
}

const addAttachment = () => {
  ElMessage.info('Add attachment dialog will open')
}

const downloadAttachment = (file: any) => {
  ElMessage.success(`Downloading ${file.name}`)
}

const viewRelatedIncident = (incident: any) => {
  const found = incidents.value.find(i => i.id === incident.id)
  if (found) viewIncidentDetail(found)
}

const runIncidentAnalysis = () => {
  ElMessage.success('Incident analysis started')
  activeTab.value = 'analytics'
}

const generatePostMortem = () => {
  ElMessage.success('Post-mortem report generation started')
}

const scheduleReview = () => {
  ElMessage.info('Review meeting scheduling will open')
}

const addKnowledgeArticle = () => {
  ElMessage.info('Add knowledge article dialog will open')
}

const viewArticle = (article: any) => {
  ElMessage.info(`Viewing: ${article.title}`)
}

const saveIncident = () => {
  if (dialogMode.value === 'create') {
    const newId = `INC-${String(incidents.value.length + 1).padStart(3, '0')}`
    incidents.value.unshift({
      id: newId,
      ...incidentForm.value,
      status: 'new',
      reportedTime: new Date().toLocaleString(),
      reportedBy: 'Current User',
      affectedAssets: [],
      relatedIncidents: [],
      attachments: [],
      timeline: [{ id: 1, type: 'create', title: 'Incident Created', description: 'Incident reported and logged', time: new Date().toLocaleTimeString(), user: 'Current User' }]
    })
    ElMessage.success(`Incident ${newId} created successfully`)
  } else {
    ElMessage.success('Incident updated successfully')
  }
  incidentDialogVisible.value = false
}

const confirmAssign = () => {
  if (selectedIncident.value) {
    selectedIncident.value.assignee = assignTo.value
    selectedIncident.value.responseTeam = assignTeam.value
    ElMessage.success(`Incident assigned to ${assignTo.value}`)
  }
  assignDialogVisible.value = false
}

const confirmUpdateStatus = () => {
  if (selectedIncident.value) {
    selectedIncident.value.status = updateStatus.value
    if (updateStatus.value === 'resolved' || updateStatus.value === 'closed') {
      ElNotification({
        title: 'Incident Resolved',
        message: `Incident ${selectedIncident.value.id} has been ${updateStatus.value}`,
        type: 'success'
      })
    }
    ElMessage.success(`Status updated to ${updateStatus.value}`)
  }
  statusDialogVisible.value = false
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

// Chart instances
let trendChart: echarts.ECharts | null = null
let severityChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null
let mttrChart: echarts.ECharts | null = null
let locationChart: echarts.ECharts | null = null

// Chart refs
const trendChartRef = ref<HTMLElement | null>(null)
const severityChartRef = ref<HTMLElement | null>(null)
const typeChartRef = ref<HTMLElement | null>(null)
const mttrChartRef = ref<HTMLElement | null>(null)
const locationChartRef = ref<HTMLElement | null>(null)

// Chart initialization
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()
  trendChart = echarts.init(trendChartRef.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: { type: 'value', name: 'Incident Count' },
    series: [
      { name: 'Critical', type: 'line', data: [2, 1, 3, 2, 4, 1, 0], lineStyle: { color: '#ef4444', width: 2 }, smooth: true },
      { name: 'High', type: 'line', data: [3, 2, 4, 3, 2, 1, 1], lineStyle: { color: '#f59e0b', width: 2 }, smooth: true },
      { name: 'Medium', type: 'line', data: [5, 4, 6, 5, 4, 3, 2], lineStyle: { color: '#3b82f6', width: 2 }, smooth: true },
      { name: 'Low', type: 'line', data: [2, 3, 1, 2, 1, 1, 0], lineStyle: { color: '#10b981', width: 2 }, smooth: true }
    ]
  })
}

const initSeverityChart = () => {
  if (!severityChartRef.value) return
  if (severityChart) severityChart.dispose()
  severityChart = echarts.init(severityChartRef.value)
  severityChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie', radius: '55%', data: [
        { name: 'Critical', value: 3, itemStyle: { color: '#ef4444' } },
        { name: 'High', value: 2, itemStyle: { color: '#f59e0b' } },
        { name: 'Medium', value: 2, itemStyle: { color: '#3b82f6' } },
        { name: 'Low', value: 1, itemStyle: { color: '#10b981' } }
      ], label: { show: true, formatter: '{b}: {d}%' }, emphasis: { scale: true }
    }]
  })
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  if (typeChart) typeChart.dispose()
  typeChart = echarts.init(typeChartRef.value)
  typeChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: ['Technical', 'Security', 'Safety', 'Operational'] },
    yAxis: { type: 'value', name: 'Count' },
    series: [{
      type: 'bar', data: [5, 2, 1, 0], itemStyle: { borderRadius: [8, 8, 0, 0], color: '#3b82f6' }, label: { show: true, position: 'top' }
    }]
  })
}

const initMTTRChart = () => {
  if (!mttrChartRef.value) return
  if (mttrChart) mttrChart.dispose()
  mttrChart = echarts.init(mttrChartRef.value)
  mttrChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: ['Critical', 'High', 'Medium', 'Low'] },
    yAxis: { type: 'value', name: 'Minutes' },
    series: [{
      type: 'bar', data: [45, 32, 25, 18], itemStyle: { borderRadius: [8, 8, 0, 0], color: (params: any) => {
          const colors = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981']
          return colors[params.dataIndex]
        } }, label: { show: true, position: 'top', formatter: '{c}m' }
    }]
  })
}

const initLocationChart = () => {
  if (!locationChartRef.value) return
  if (locationChart) locationChart.dispose()
  locationChart = echarts.init(locationChartRef.value)
  locationChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: ['DC East', 'Cooling Plant', 'Office Tower', 'DC West', 'Network Room'], axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Incident Count' },
    series: [{
      type: 'bar', data: [3, 2, 1, 1, 1], itemStyle: { borderRadius: [8, 8, 0, 0], color: '#8b5cf6' }, label: { show: true, position: 'top' }
    }]
  })
}

// Watch for period changes
watch(trendPeriod, () => initTrendChart())

// Update time
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('en-US', {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

// Resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [trendChart, severityChart, typeChart, mttrChart, locationChart]
    charts.forEach(chart => chart?.resize())
  }, 200)
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initTrendChart()
          initSeverityChart()
          initTypeChart()
          initMTTRChart()
          initLocationChart()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  const charts = [trendChart, severityChart, typeChart, mttrChart, locationChart]
  charts.forEach(chart => chart?.dispose())
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.incident-center-container {
  min-height: 100vh;
  background: #f0f2f6;
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

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
}

.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-progress {
  width: 320px;
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
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
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

/* ==================== Main Content ==================== */
.incident-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 12px;
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

/* Incident Stats */
.incident-stats {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-trend {
  font-size: 11px;
}

.stat-trend.up { color: #ef4444; }
.stat-trend.down { color: #10b981; }

/* Tabs */
.incident-tabs {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.incident-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Incident Table */
.incident-table {
  cursor: pointer;
}

.incident-table :deep(.el-table__row:hover) {
  background: #f8fafc;
  cursor: pointer;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* Incident Details Panel */
.incident-details-panel {
  padding: 0 4px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.details-header h2 {
  margin: 0 0 12px 0;
  font-size: 22px;
  color: #1e293b;
}

.header-badges {
  display: flex;
  gap: 12px;
}

.detail-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.detail-card :deep(.el-card__header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  font-weight: 600;
  color: #1e293b;
}

/* Timeline */
.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline-event {
  position: relative;
  margin-bottom: 20px;
}

.event-dot {
  position: absolute;
  left: -18px;
  top: 4px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.event-dot.alert { background: #ef4444; box-shadow: 0 0 0 3px #fee2e2; }
.event-dot.response { background: #3b82f6; box-shadow: 0 0 0 3px #dbeafe; }
.event-dot.update { background: #10b981; box-shadow: 0 0 0 3px #d1fae5; }
.event-dot.create { background: #8b5cf6; box-shadow: 0 0 0 3px #ede9fe; }

.event-content {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
}

.event-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.event-title {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
}

.event-time {
  font-size: 10px;
  color: #94a3b8;
}

.event-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.event-user {
  font-size: 10px;
  color: #94a3b8;
}

/* Attachments */
.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8fafc;
  border-radius: 8px;
}

.attachment-item .file-size {
  flex: 1;
  font-size: 11px;
  color: #94a3b8;
}

/* Asset List */
.asset-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.asset-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8fafc;
  border-radius: 8px;
}

.asset-item .el-icon {
  color: #3b82f6;
}

/* Related List */
.related-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.related-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.related-item:hover {
  background: #f1f5f9;
}

/* No Selection */
.no-selection {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.no-selection .el-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

/* Analytics Content */
.analytics-content {
  padding: 4px;
}

.chart-card {
  border-radius: 16px;
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* Knowledge Content */
.knowledge-content {
  padding: 4px;
}

.knowledge-card {
  border-radius: 16px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: transform 0.2s;
}

.knowledge-card:hover {
  transform: translateY(-4px);
}

.article-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  font-size: 24px;
  color: white;
}

.article-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #1e293b;
}

.article-info p {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.article-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #94a3b8;
}

.article-meta .el-icon {
  margin-right: 4px;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 8px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 24px;
}

/* Responsive */
@media (max-width: 1200px) {
  .incident-main { padding: 16px; }
  .incident-stats { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .incident-stats { grid-template-columns: repeat(2, 1fr); }
  .section-header { flex-direction: column; align-items: stretch; }
  .filter-group { flex-direction: column; }
  .details-header { flex-direction: column; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>