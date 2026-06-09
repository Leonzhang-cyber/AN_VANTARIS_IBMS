<template>
  <div class="compliance-roadmap-container">
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
            <span class="loading-title">Loading Compliance Roadmap</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Strategic ESG Compliance Planning</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <el-page-header @back="goBack" content="Back">
        <template #content>
          <div class="page-header-content">
            <span class="page-title">ESG Compliance Roadmap</span>
            <el-tag type="primary" effect="dark" size="large">Strategic Plan 2024-2026</el-tag>
          </div>
        </template>
      </el-page-header>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Flag /></el-icon>
                <span>Overall Progress</span>
              </div>
              <div class="card-value">34%</div>
              <div class="card-footer">
                <el-progress :percentage="34" :stroke-width="8" status="success" />
                <span class="status-text">On Track</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Calendar /></el-icon>
                <span>Milestones Achieved</span>
              </div>
              <div class="card-value">8</div>
              <div class="card-footer">
                <el-progress :percentage="40" :stroke-width="8" />
                <span class="status-text">of 20 Total</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>Next Deadline</span>
              </div>
              <div class="card-value">45 d</div>
              <div class="card-footer">
                <el-progress :percentage="65" :stroke-width="8" status="warning" />
                <span class="status-text">Q1 2025 Reporting</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Risk Score</span>
              </div>
              <div class="card-value">Medium</div>
              <div class="card-footer">
                <el-progress :percentage="55" :stroke-width="8" status="warning" />
                <span class="status-text">Mitigation Active</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Timeline Gantt Chart -->
      <div class="gantt-section">
        <el-card class="gantt-card" shadow="hover">
          <div class="gantt-header">
            <div class="gantt-title">
              <el-icon><TrendCharts /></el-icon>
              <span>Compliance Timeline (Gantt View)</span>
            </div>
            <div class="gantt-controls">
              <el-button-group>
                <el-button :type="viewMode === 'quarter' ? 'primary' : 'default'" size="small" @click="viewMode = 'quarter'">Quarter</el-button>
                <el-button :type="viewMode === 'month' ? 'primary' : 'default'" size="small" @click="viewMode = 'month'">Month</el-button>
              </el-button-group>
            </div>
          </div>
          <div class="chart-container">
            <div ref="ganttChartRef" style="height: 500px"></div>
          </div>
        </el-card>
      </div>

      <!-- Framework Progress Cards -->
      <div class="framework-progress-section">
        <div class="section-header">
          <h3>Framework Compliance Progress</h3>
          <el-button type="primary" link @click="showAllFrameworks">View All Details →</el-button>
        </div>
        <el-row :gutter="20">
          <el-col :span="8" v-for="framework in frameworkProgress" :key="framework.id">
            <el-card class="framework-progress-card" shadow="hover">
              <div class="framework-header">
                <span class="framework-name" :style="{ color: framework.color }">{{ framework.name }}</span>
                <el-tag :type="getProgressTagType(framework.progress)" size="small">
                  {{ framework.progress }}%
                </el-tag>
              </div>
              <div class="framework-progress-bar">
                <el-progress :percentage="framework.progress" :stroke-width="10" :color="framework.color" />
              </div>
              <div class="framework-stats">
                <div class="stat">
                  <span class="stat-label">Target Date</span>
                  <span class="stat-value">{{ framework.targetDate }}</span>
                </div>
                <div class="stat">
                  <span class="stat-label">Status</span>
                  <span class="stat-value">{{ framework.status }}</span>
                </div>
              </div>
              <div class="framework-milestones">
                <div v-for="milestone in framework.milestones" :key="milestone.name" class="milestone-indicator">
                  <el-icon :color="milestone.completed ? '#67c23a' : '#e6a23c'">
                    <CircleCheck v-if="milestone.completed" />
                    <Clock v-else />
                  </el-icon>
                  <span>{{ milestone.name }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Detailed Timeline Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Milestones Tab -->
          <el-tab-pane label="Milestones" name="milestones">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Flag /></el-icon>
                <span>Key Compliance Milestones</span>
              </div>
              <el-timeline>
                <el-timeline-item
                    v-for="milestone in milestones"
                    :key="milestone.id"
                    :timestamp="milestone.date"
                    :type="milestone.completed ? 'success' : 'primary'"
                    :hollow="!milestone.completed"
                    placement="top"
                >
                  <el-card>
                    <div class="milestone-card">
                      <div class="milestone-header">
                        <h4>{{ milestone.title }}</h4>
                        <el-tag :type="milestone.completed ? 'success' : 'warning'" size="small">
                          {{ milestone.completed ? 'Completed' : 'Pending' }}
                        </el-tag>
                      </div>
                      <p>{{ milestone.description }}</p>
                      <div class="milestone-footer">
                        <span><el-icon><OfficeBuilding /></el-icon> {{ milestone.framework }}</span>
                        <span><el-icon><User /></el-icon> {{ milestone.owner }}</span>
                        <el-progress v-if="milestone.progress" :percentage="milestone.progress" :stroke-width="6" style="width: 200px" />
                      </div>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-tab-pane>

          <!-- Action Items Tab -->
          <el-tab-pane label="Action Items" name="actions">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><List /></el-icon>
                <span>Action Items & Tasks</span>
              </div>
              <div class="action-controls">
                <el-input
                    v-model="actionSearch"
                    placeholder="Search actions..."
                    prefix-icon="Search"
                    style="width: 300px"
                    clearable
                />
                <el-select v-model="actionStatusFilter" placeholder="Status" clearable style="width: 150px">
                  <el-option label="Not Started" value="Not Started" />
                  <el-option label="In Progress" value="In Progress" />
                  <el-option label="Completed" value="Completed" />
                </el-select>
                <el-select v-model="actionFrameworkFilter" placeholder="Framework" clearable style="width: 150px">
                  <el-option v-for="fw in frameworks" :key="fw" :label="fw" :value="fw" />
                </el-select>
              </div>
              <el-table :data="filteredActions" border style="width: 100%">
                <el-table-column prop="task" label="Action Item" width="300" />
                <el-table-column prop="framework" label="Framework" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getFrameworkTagType(row.framework)" size="small">{{ row.framework }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="owner" label="Owner" width="120" />
                <el-table-column prop="dueDate" label="Due Date" width="110" />
                <el-table-column prop="status" label="Status" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getActionStatusType(row.status)">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="priority" label="Priority" width="100">
                  <template #default="{ row }">
                    <el-tag :type="getPriorityType(row.priority)" size="small">
                      {{ row.priority }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Actions" width="120">
                  <template #default="{ row }">
                    <el-button type="primary" link size="small" @click="updateActionStatus(row)">Update</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- Dependencies Tab -->
          <el-tab-pane label="Dependencies" name="dependencies">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Connection /></el-icon>
                <span>Task Dependencies & Critical Path</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="chart-container">
                    <div ref="dependencyChartRef" style="height: 500px"></div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="dependency-summary">
                    <h4>Critical Path Analysis</h4>
                    <el-table :data="criticalPathItems" border size="small">
                      <el-table-column prop="task" label="Critical Task" />
                      <el-table-column prop="duration" label="Duration" width="80" />
                    </el-table>
                    <div class="risk-warning">
                      <el-alert
                          title="Critical Path Risk"
                          description="Scope 3 data collection is on critical path and behind schedule"
                          type="warning"
                          show-icon
                          :closable="false"
                      />
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Risk Register Tab -->
          <el-tab-pane label="Risk Register" name="risks">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>Roadmap Risks & Mitigation</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="riskRegister" border style="width: 100%">
                    <el-table-column prop="risk" label="Risk Description" width="250" />
                    <el-table-column prop="likelihood" label="Likelihood" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getRiskLevelType(row.likelihood)">{{ row.likelihood }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="impact" label="Impact" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getRiskLevelType(row.impact)">{{ row.impact }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="mitigation" label="Mitigation Plan" />
                    <el-table-column prop="owner" label="Owner" width="120" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="chart-container">
                    <div ref="riskMatrixChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Resources & Budget Tab -->
          <el-tab-pane label="Resources & Budget" name="resources">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Money /></el-icon>
                <span>Resource Allocation & Budget Tracking</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="budgetChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="budget-details">
                    <h4>Budget Breakdown by Framework</h4>
                    <el-table :data="budgetBreakdown" border size="small">
                      <el-table-column prop="framework" label="Framework" />
                      <el-table-column prop="allocated" label="Allocated ($)" width="120">
                        <template #default="{ row }">
                          {{ formatCurrency(row.allocated) }}
                        </template>
                      </el-table-column>
                      <el-table-column prop="spent" label="Spent ($)" width="120">
                        <template #default="{ row }">
                          {{ formatCurrency(row.spent) }}
                        </template>
                      </el-table-column>
                      <el-table-column prop="remaining" label="Remaining ($)" width="120">
                        <template #default="{ row }">
                          {{ formatCurrency(row.remaining) }}
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Reports Tab -->
          <el-tab-pane label="Reports" name="reports">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>Roadmap Reports</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8" v-for="report in roadmapReports" :key="report.id">
                  <div class="report-card" @click="downloadReport(report)">
                    <el-icon :size="40"><component :is="report.icon" /></el-icon>
                    <h4>{{ report.title }}</h4>
                    <p>{{ report.description }}</p>
                    <div class="report-meta">
                      <span>{{ report.date }}</span>
                      <el-tag size="small">{{ report.format }}</el-tag>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="exportRoadmap">
          <el-icon><Download /></el-icon>
          Export Roadmap
        </el-button>
        <el-button size="large" @click="shareRoadmap">
          <el-icon><Share /></el-icon>
          Share with Stakeholders
        </el-button>
        <el-button size="large" @click="scheduleReview">
          <el-icon><Calendar /></el-icon>
          Schedule Review Meeting
        </el-button>
      </div>
    </template>

    <!-- Update Action Dialog -->
    <el-dialog v-model="actionDialogVisible" title="Update Action Item" width="500px">
      <el-form :model="actionForm">
        <el-form-item label="Task">
          <span>{{ actionForm.task }}</span>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="actionForm.status" placeholder="Select status">
            <el-option label="Not Started" value="Not Started" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Completed" value="Completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="Progress %">
          <el-slider v-model="actionForm.progress" :format-tooltip="(val) => `${val}%`" />
        </el-form-item>
        <el-form-item label="Comments">
          <el-input v-model="actionForm.comments" type="textarea" :rows="3" placeholder="Update comments" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="actionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveActionUpdate">Save Changes</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading compliance roadmap...')

const loadingMessages = [
  'Loading compliance roadmap...',
  'Mapping timeline milestones...',
  'Analyzing dependencies...',
  'Calculating progress metrics...',
  'Generating Gantt chart...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('milestones')
const viewMode = ref('quarter')
const actionSearch = ref('')
const actionStatusFilter = ref('')
const actionFrameworkFilter = ref('')
const actionDialogVisible = ref(false)
const actionForm = ref({ task: '', status: '', progress: 0, comments: '' })

// Frameworks list
const frameworks = ['IFRS S2', 'ISSB', 'GRI', 'TCFD', 'CSRD', 'SGX/HKEX/MAS']

// Framework progress data
const frameworkProgress = ref([
  {
    id: 1, name: 'IFRS S2', color: '#f56c6c', progress: 33, targetDate: '2025-12-31', status: 'On Track',
    milestones: [
      { name: 'Governance', completed: true },
      { name: 'Strategy', completed: false },
      { name: 'Metrics', completed: false }
    ]
  },
  {
    id: 2, name: 'ISSB', color: '#409eff', progress: 20, targetDate: '2026-03-31', status: 'Behind',
    milestones: [
      { name: 'General Requirements', completed: true },
      { name: 'Climate', completed: false },
      { name: 'Implementation', completed: false }
    ]
  },
  {
    id: 3, name: 'GRI', color: '#67c23a', progress: 45, targetDate: '2025-06-30', status: 'On Track',
    milestones: [
      { name: 'Universal', completed: true },
      { name: 'Sector', completed: false },
      { name: 'Topic', completed: false }
    ]
  },
  {
    id: 4, name: 'TCFD', color: '#e6a23c', progress: 55, targetDate: '2025-03-31', status: 'On Track',
    milestones: [
      { name: 'Governance', completed: true },
      { name: 'Strategy', completed: true },
      { name: 'Risk Mgmt', completed: false }
    ]
  },
  {
    id: 5, name: 'CSRD', color: '#909399', progress: 25, targetDate: '2026-06-30', status: 'At Risk',
    milestones: [
      { name: 'ESRS 1-2', completed: true },
      { name: 'ESRS E1', completed: false },
      { name: 'Double Materiality', completed: false }
    ]
  },
  {
    id: 6, name: 'SGX/HKEX/MAS', color: '#9c27b0', progress: 30, targetDate: '2025-09-30', status: 'On Track',
    milestones: [
      { name: 'SGX', completed: true },
      { name: 'HKEX', completed: false },
      { name: 'MAS', completed: false }
    ]
  }
])

// Milestones data
const milestones = ref([
  { id: 1, title: 'TCFD Governance Disclosures Complete', date: '2024-12-15', description: 'Board oversight and governance structure documented', framework: 'TCFD', owner: 'Legal Team', completed: true, progress: 100 },
  { id: 2, title: 'GRI Universal Standards Implementation', date: '2024-12-31', description: 'GRI 1, 2, 3 fully implemented', framework: 'GRI', owner: 'Sustainability', completed: true, progress: 100 },
  { id: 3, title: 'IFRS S2 Governance Phase Complete', date: '2025-01-15', description: 'Board climate competencies documented', framework: 'IFRS S2', owner: 'Legal Team', completed: true, progress: 100 },
  { id: 4, title: 'Double Materiality Assessment', date: '2025-03-31', description: 'CSRD double materiality assessment complete', framework: 'CSRD', owner: 'Sustainability', completed: false, progress: 65 },
  { id: 5, title: 'TCFD Climate Scenario Analysis', date: '2025-03-31', description: '1.5°C and 2°C scenarios completed', framework: 'TCFD', owner: 'Risk Team', completed: false, progress: 40 },
  { id: 6, title: 'GRI Sector Standards Implementation', date: '2025-06-30', description: 'Data center sector standards applied', framework: 'GRI', owner: 'Ops', completed: false, progress: 25 },
  { id: 7, title: 'Scope 3 Emissions Inventory Complete', date: '2025-09-30', description: 'Full Scope 3 data collected and verified', framework: 'IFRS S2', owner: 'Sustainability', completed: false, progress: 30 },
  { id: 8, title: 'HKEX TCFD-aligned Reporting', date: '2025-12-31', description: 'First full TCFD report for HKEX', framework: 'SGX/HKEX/MAS', owner: 'Finance', completed: false, progress: 15 }
])

// Action items data
const actionItems = ref([
  { id: 1, task: 'Complete board climate competency assessment', framework: 'IFRS S2', owner: 'Legal Team', dueDate: '2025-01-31', status: 'Completed', priority: 'High' },
  { id: 2, task: 'Run 1.5°C climate scenario analysis', framework: 'TCFD', owner: 'Risk Team', dueDate: '2025-03-31', status: 'In Progress', priority: 'High' },
  { id: 3, task: 'Document stakeholder engagement process', framework: 'GRI', owner: 'Communications', dueDate: '2025-02-28', status: 'In Progress', priority: 'Medium' },
  { id: 4, task: 'Implement ESG data management platform', framework: 'CSRD', owner: 'IT', dueDate: '2025-06-30', status: 'Not Started', priority: 'High' },
  { id: 5, task: 'Collect Scope 3 supplier data', framework: 'IFRS S2', owner: 'Sustainability', dueDate: '2025-09-30', status: 'In Progress', priority: 'High' },
  { id: 6, task: 'Set waste reduction targets', framework: 'GRI', owner: 'Ops', dueDate: '2025-06-30', status: 'Not Started', priority: 'Medium' },
  { id: 7, task: 'Map activities to MAS taxonomy', framework: 'SGX/HKEX/MAS', owner: 'Sustainability', dueDate: '2025-06-30', status: 'Not Started', priority: 'High' },
  { id: 8, task: 'Engage external assurance provider', framework: 'CSRD', owner: 'Finance', dueDate: '2025-12-31', status: 'Not Started', priority: 'Medium' }
])

// Critical path items
const criticalPathItems = ref([
  { task: 'Double Materiality Assessment', duration: '3 months' },
  { task: 'Climate Scenario Analysis', duration: '2 months' },
  { task: 'Scope 3 Data Collection', duration: '6 months' },
  { task: 'ESG Platform Implementation', duration: '4 months' }
])

// Risk register
const riskRegister = ref([
  { risk: 'Scope 3 data collection delays', likelihood: 'High', impact: 'High', mitigation: 'Engage suppliers early; use estimates where needed', owner: 'Sustainability' },
  { risk: 'Regulatory changes during implementation', likelihood: 'Medium', impact: 'High', mitigation: 'Regular regulatory monitoring; flexible roadmap', owner: 'Legal' },
  { risk: 'Resource constraints', likelihood: 'Medium', impact: 'Medium', mitigation: 'Cross-training; external consultants', owner: 'HR' },
  { risk: 'Data quality issues', likelihood: 'High', impact: 'Medium', mitigation: 'Data validation processes; automated checks', owner: 'IT' },
  { risk: 'Stakeholder buy-in', likelihood: 'Low', impact: 'High', mitigation: 'Regular communication; executive sponsorship', owner: 'Leadership' }
])

// Budget breakdown
const budgetBreakdown = ref([
  { framework: 'IFRS S2', allocated: 250000, spent: 85000, remaining: 165000 },
  { framework: 'ISSB', allocated: 200000, spent: 40000, remaining: 160000 },
  { framework: 'GRI', allocated: 180000, spent: 80000, remaining: 100000 },
  { framework: 'TCFD', allocated: 150000, spent: 90000, remaining: 60000 },
  { framework: 'CSRD', allocated: 300000, spent: 75000, remaining: 225000 },
  { framework: 'SGX/HKEX/MAS', allocated: 170000, spent: 55000, remaining: 115000 }
])

// Roadmap reports
const roadmapReports = ref([
  { id: 1, title: 'Roadmap Summary Report', description: 'Executive summary of compliance roadmap', icon: 'DataAnalysis', format: 'PDF', date: '2024-12-01' },
  { id: 2, title: 'Milestone Tracker', description: 'Detailed milestone progress report', icon: 'Flag', format: 'Excel', date: '2024-12-01' },
  { id: 3, title: 'Risk Assessment Report', description: 'Roadmap risks and mitigation status', icon: 'Warning', format: 'PDF', date: '2024-12-01' },
  { id: 4, title: 'Budget Forecast', description: 'Quarterly budget projections', icon: 'Money', format: 'Excel', date: '2024-12-01' }
])

// Chart refs
const ganttChartRef = ref<HTMLElement | null>(null)
const dependencyChartRef = ref<HTMLElement | null>(null)
const riskMatrixChartRef = ref<HTMLElement | null>(null)
const budgetChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Computed
const filteredActions = computed(() => {
  let data = actionItems.value
  if (actionSearch.value) {
    data = data.filter(a => a.task.toLowerCase().includes(actionSearch.value.toLowerCase()))
  }
  if (actionStatusFilter.value) {
    data = data.filter(a => a.status === actionStatusFilter.value)
  }
  if (actionFrameworkFilter.value) {
    data = data.filter(a => a.framework === actionFrameworkFilter.value)
  }
  return data
})

// Methods
const goBack = () => {
  router.back()
}

const getProgressTagType = (progress: number) => {
  if (progress >= 75) return 'success'
  if (progress >= 50) return 'warning'
  return 'info'
}

const getFrameworkTagType = (framework: string) => {
  const map: Record<string, string> = {
    'IFRS S2': 'danger',
    'ISSB': 'primary',
    'GRI': 'success',
    'TCFD': 'warning',
    'CSRD': 'info',
    'SGX/HKEX/MAS': 'danger'
  }
  return map[framework] || 'info'
}

const getActionStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Not Started': 'info',
    'In Progress': 'warning',
    'Completed': 'success'
  }
  return map[status] || 'info'
}

const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'info'
  }
  return map[priority] || 'info'
}

const getRiskLevelType = (level: string) => {
  const map: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'success'
  }
  return map[level] || 'info'
}

const formatCurrency = (value: number) => {
  return value.toLocaleString()
}

const showAllFrameworks = () => {
  ElMessage.info('Full framework details will be available in the detailed report')
}

const updateActionStatus = (action: any) => {
  actionForm.value = { ...action, progress: action.status === 'Completed' ? 100 : action.status === 'In Progress' ? 50 : 0, comments: '' }
  actionDialogVisible.value = true
}

const saveActionUpdate = () => {
  const index = actionItems.value.findIndex(a => a.task === actionForm.value.task)
  if (index !== -1) {
    actionItems.value[index].status = actionForm.value.status
    ElMessage.success(`Action status updated to ${actionForm.value.status}`)
  }
  actionDialogVisible.value = false
}

const exportRoadmap = () => {
  ElMessage.success('Roadmap export started. File will be downloaded shortly.')
}

const shareRoadmap = () => {
  ElMessage.success('Roadmap shared with stakeholders')
}

const scheduleReview = () => {
  ElMessage.info('Review meeting scheduling interface will open in a new window.')
}

const downloadReport = (report: any) => {
  ElMessage.success(`Downloading ${report.title}...`)
}

// Chart initialization
const initGanttChart = () => {
  if (ganttChartRef.value) {
    const chart = echarts.init(ganttChartRef.value)
    // Simplified Gantt representation using custom series
    chart.setOption({
      title: { show: false },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'time', name: 'Timeline' },
      yAxis: { type: 'category', data: ['IFRS S2', 'ISSB', 'GRI', 'TCFD', 'CSRD', 'SGX/HKEX/MAS'], name: 'Framework' },
      series: [
        { type: 'scatter', name: 'Start', data: [[new Date('2024-10-01').getTime(), 0], [new Date('2024-10-15').getTime(), 1]], symbolSize: 10, itemStyle: { color: '#67c23a' } },
        { type: 'scatter', name: 'Milestone', data: [[new Date('2025-03-31').getTime(), 3], [new Date('2025-06-30').getTime(), 2], [new Date('2025-12-31').getTime(), 0], [new Date('2026-03-31').getTime(), 1]], symbolSize: 15, itemStyle: { color: '#e6a23c' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initDependencyChart = () => {
  if (dependencyChartRef.value) {
    const chart = echarts.init(dependencyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'graph',
        layout: 'force',
        symbolSize: 50,
        roam: true,
        label: { show: true, position: 'bottom' },
        edgeSymbol: ['none', 'arrow'],
        edgeLabel: { show: true, formatter: '{c}' },
        categories: [{ name: 'Task' }],
        data: [
          { name: 'Materiality', category: 0, symbolSize: 40 },
          { name: 'Scenario', category: 0, symbolSize: 40 },
          { name: 'Scope 3', category: 0, symbolSize: 40 },
          { name: 'ESG Platform', category: 0, symbolSize: 40 },
          { name: 'Report', category: 0, symbolSize: 40 }
        ],
        links: [
          { source: 'Materiality', target: 'Scenario' },
          { source: 'Materiality', target: 'ESG Platform' },
          { source: 'Scenario', target: 'Report' },
          { source: 'Scope 3', target: 'Report' },
          { source: 'ESG Platform', target: 'Report' }
        ],
        lineStyle: { color: '#409eff', width: 2, curveness: 0.3 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initRiskMatrixChart = () => {
  if (riskMatrixChartRef.value) {
    const chart = echarts.init(riskMatrixChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', name: 'Impact', data: ['Low', 'Medium', 'High'] },
      yAxis: { type: 'category', name: 'Likelihood', data: ['High', 'Medium', 'Low'] },
      series: [{
        type: 'scatter',
        data: [[1, 0, 2], [2, 1, 1], [0, 2, 1]],
        symbolSize: 30,
        label: { show: true, formatter: (params: any) => ['Regulatory', 'Data', 'Resource'][params.data[2]] }
      }]
    })
    chartInstances.push(chart)
  }
}

const initBudgetChart = () => {
  if (budgetChartRef.value) {
    const chart = echarts.init(budgetChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Allocated', 'Spent', 'Remaining'] },
      xAxis: { type: 'category', data: budgetBreakdown.value.map(b => b.framework) },
      yAxis: { type: 'value', name: 'Budget ($)' },
      series: [
        { name: 'Allocated', type: 'bar', data: budgetBreakdown.value.map(b => b.allocated), itemStyle: { color: '#409eff' } },
        { name: 'Spent', type: 'bar', data: budgetBreakdown.value.map(b => b.spent), itemStyle: { color: '#67c23a' } },
        { name: 'Remaining', type: 'bar', data: budgetBreakdown.value.map(b => b.remaining), itemStyle: { color: '#e6a23c' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}

onMounted(() => {
  let messageIndex = 0
  let progressInterval: ReturnType<typeof setInterval>
  let messageInterval: ReturnType<typeof setInterval>

  messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      const increment = Math.random() * 12 + 3
      loadingProgress.value = Math.min(loadingProgress.value + increment, 100)
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      setTimeout(() => {
        initGanttChart()
        initDependencyChart()
        initRiskMatrixChart()
        initBudgetChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  chartInstances.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.compliance-roadmap-container {
  min-height: 100vh;
  background-color: #f5f7fa;
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
  border: 1px solid rgba(64, 158, 255, 0.3);
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
  border-top-color: #409eff;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #67c23a;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #e6a23c;
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
  font-size: 24px;
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
  width: 320px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 16px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #409eff, #67c23a, #e6a23c);
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
.compliance-roadmap-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.overview-section {
  margin: 24px 0;
}

.overview-card {
  border-radius: 12px;
  transition: transform 0.2s;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
}

.card-header .el-icon {
  font-size: 18px;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16px;
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-text {
  font-size: 12px;
  color: #909399;
}

/* Gantt Section */
.gantt-section {
  margin-bottom: 24px;
}

.gantt-card {
  border-radius: 12px;
}

.gantt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.gantt-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

/* Framework Progress Section */
.framework-progress-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.framework-progress-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.framework-progress-card:hover {
  transform: translateY(-2px);
}

.framework-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.framework-name {
  font-size: 16px;
  font-weight: 600;
}

.framework-progress-bar {
  margin: 16px 0;
}

.framework-stats {
  display: flex;
  gap: 16px;
  margin: 12px 0;
  padding: 8px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.stat {
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #909399;
}

.stat-value {
  font-size: 13px;
  font-weight: 500;
}

.framework-milestones {
  margin-top: 12px;
}

.milestone-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  padding: 4px 0;
  color: #606266;
}

/* Main Content */
.main-content-card {
  margin-top: 20px;
  border-radius: 12px;
}

.tab-content {
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e4e7ed;
}

.section-title .el-icon {
  font-size: 22px;
  color: #409eff;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

/* Milestone Card */
.milestone-card {
  padding: 8px;
}

.milestone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.milestone-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.milestone-footer {
  display: flex;
  gap: 20px;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: #909399;
}

.milestone-footer .el-icon {
  margin-right: 4px;
}

/* Action Controls */
.action-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

/* Dependency Summary */
.dependency-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  height: 500px;
  overflow-y: auto;
}

.dependency-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.risk-warning {
  margin-top: 20px;
}

/* Budget Details */
.budget-details {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  height: 350px;
  overflow-y: auto;
}

.budget-details h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

/* Report Cards */
.report-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.report-card .el-icon {
  color: #409eff;
  margin-bottom: 12px;
}

.report-card h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.report-card p {
  margin: 0 0 12px 0;
  font-size: 12px;
  color: #909399;
}

.report-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #c0c4cc;
}

/* Action Buttons */
.action-buttons {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.action-buttons .el-button {
  border-radius: 8px;
}

/* Deep Selectors */
:deep(.el-tabs--border-card) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-progress__text) {
  font-size: 12px;
}

:deep(.el-timeline-item__timestamp) {
  font-weight: 500;
}
</style>