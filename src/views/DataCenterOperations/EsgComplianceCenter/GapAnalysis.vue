<template>
  <div class="gap-analysis-container">
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
            <span class="loading-title">Loading Gap Analysis Dashboard</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">ESG Compliance Gap Analysis</div>
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
            <span class="page-title">ESG Compliance Gap Analysis</span>
            <el-tag type="danger" effect="dark" size="large">Consolidated Dashboard</el-tag>
          </div>
        </template>
      </el-page-header>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><WarningFilled /></el-icon>
                <span>Total Gaps Identified</span>
              </div>
              <div class="card-value">47</div>
              <div class="card-footer">
                <el-progress :percentage="100" :stroke-width="8" :format="() => 'To Address'" />
                <span class="status-text">Across 6 Frameworks</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><CircleCheck /></el-icon>
                <span>High Priority Gaps</span>
              </div>
              <div class="card-value">18</div>
              <div class="card-footer">
                <el-progress :percentage="38" :stroke-width="8" status="exception" />
                <span class="status-text">Requires Immediate Action</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>Avg. Remediation Time</span>
              </div>
              <div class="card-value">6.2 mo</div>
              <div class="card-footer">
                <el-progress :percentage="65" :stroke-width="8" status="warning" />
                <span class="status-text">Medium Complexity</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Remediation Progress</span>
              </div>
              <div class="card-value">34%</div>
              <div class="card-footer">
                <el-progress :percentage="34" :stroke-width="8" status="success" />
                <span class="status-text">Completed</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Framework Filter Tabs -->
      <div class="filter-section">
        <el-card class="filter-card" shadow="never">
          <div class="filter-header">
            <span class="filter-title">Framework Filter</span>
            <el-button type="primary" link @click="clearFilters">Clear All Filters</el-button>
          </div>
          <el-row :gutter="16">
            <el-col :span="4" v-for="framework in frameworks" :key="framework.id">
              <div
                  class="framework-filter"
                  :class="{ active: selectedFrameworks.includes(framework.id) }"
                  @click="toggleFramework(framework.id)"
              >
                <span class="filter-indicator" :style="{ background: framework.color }"></span>
                <span class="filter-name">{{ framework.name }}</span>
                <span class="filter-count">{{ framework.gapCount }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Gap Overview Tab -->
          <el-tab-pane label="Gap Overview" name="overview">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><PieChart /></el-icon>
                <span>Gap Analysis Summary</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="chart-container">
                    <div ref="gapByFrameworkChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="chart-container">
                    <div ref="gapByPriorityChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="chart-container">
                    <div ref="gapByCategoryChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- All Gaps Tab -->
          <el-tab-pane label="All Gaps" name="allGaps">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><List /></el-icon>
                <span>Comprehensive Gap Register</span>
              </div>
              <div class="table-controls">
                <el-input
                    v-model="searchQuery"
                    placeholder="Search gaps..."
                    prefix-icon="Search"
                    style="width: 300px"
                    clearable
                />
                <el-select v-model="priorityFilter" placeholder="Priority" clearable style="width: 150px">
                  <el-option label="High" value="High" />
                  <el-option label="Medium" value="Medium" />
                  <el-option label="Low" value="Low" />
                </el-select>
                <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 150px">
                  <el-option label="Not Started" value="Not Started" />
                  <el-option label="In Progress" value="In Progress" />
                  <el-option label="Completed" value="Completed" />
                </el-select>
              </div>
              <div class="gaps-table">
                <el-table :data="filteredGapData" border style="width: 100%" max-height="500">
                  <el-table-column prop="framework" label="Framework" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getFrameworkTagType(row.framework)" size="small">
                        {{ row.framework }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="category" label="Category" width="120" />
                  <el-table-column prop="gap" label="Gap Description" width="280" />
                  <el-table-column prop="priority" label="Priority" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getPriorityType(row.priority)">
                        {{ row.priority }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="Status" width="120">
                    <template #default="{ row }">
                      <el-tag :type="getStatusType(row.status)">
                        {{ row.status }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="remediation" label="Remediation Plan" />
                  <el-table-column prop="targetDate" label="Target Date" width="110" />
                  <el-table-column label="Actions" width="120" fixed="right">
                    <template #default="{ row }">
                      <el-button type="primary" link size="small" @click="viewGapDetails(row)">Details</el-button>
                      <el-button type="success" link size="small" @click="updateStatus(row)">Update</el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-tab-pane>

          <!-- By Framework Tab -->
          <el-tab-pane label="By Framework" name="byFramework">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><OfficeBuilding /></el-icon>
                <span>Gap Analysis by Framework</span>
              </div>
              <el-collapse v-model="frameworkCollapse" accordion>
                <el-collapse-item v-for="framework in frameworks" :key="framework.id" :name="framework.id">
                  <template #title>
                    <div class="framework-title">
                      <span class="framework-name" :style="{ color: framework.color }">{{ framework.name }}</span>
                      <el-progress
                          :percentage="framework.completionRate"
                          :stroke-width="8"
                          :status="framework.completionRate >= 80 ? 'success' : framework.completionRate >= 50 ? 'warning' : 'exception'"
                          style="width: 200px; margin-left: 20px"
                      />
                      <span class="gap-summary">{{ framework.completedGaps }}/{{ framework.totalGaps }} gaps closed</span>
                    </div>
                  </template>
                  <el-table :data="getFrameworkGaps(framework.id)" border size="small">
                    <el-table-column prop="category" label="Category" width="150" />
                    <el-table-column prop="gap" label="Gap Description" />
                    <el-table-column prop="priority" label="Priority" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getPriorityType(row.priority)" size="small">
                          {{ row.priority }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="status" label="Status" width="120">
                      <template #default="{ row }">
                        <el-tag :type="getStatusType(row.status)" size="small">
                          {{ row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="remediation" label="Remediation Plan" />
                    <el-table-column prop="targetDate" label="Target Date" width="110" />
                    <el-table-column label="Actions" width="100">
                      <template #default="{ row }">
                        <el-button type="primary" link size="small" @click="viewGapDetails(row)">Edit</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-tab-pane>

          <!-- Remediation Roadmap Tab -->
          <el-tab-pane label="Remediation Roadmap" name="roadmap">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                <span>Remediation Roadmap</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="chart-container">
                    <div ref="roadmapChartRef" style="height: 450px"></div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="roadmap-summary">
                    <h4>Key Milestones</h4>
                    <el-timeline>
                      <el-timeline-item
                          v-for="(milestone, index) in milestones"
                          :key="index"
                          :timestamp="milestone.date"
                          :type="milestone.type"
                          :hollow="milestone.completed"
                      >
                        <div class="milestone-content">
                          <strong>{{ milestone.title }}</strong>
                          <p>{{ milestone.description }}</p>
                          <el-progress
                              v-if="milestone.progress"
                              :percentage="milestone.progress"
                              :stroke-width="4"
                              :show-text="false"
                          />
                        </div>
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Resource Planning Tab -->
          <el-tab-pane label="Resource Planning" name="resources">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><User /></el-icon>
                <span>Resource Allocation & Planning</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="resourceChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="resource-table">
                    <el-table :data="resourceData" border>
                      <el-table-column prop="role" label="Role" width="180" />
                      <el-table-column prop="assigned" label="Assigned To" />
                      <el-table-column prop="workload" label="Workload %" width="120">
                        <template #default="{ row }">
                          <el-progress :percentage="row.workload" :stroke-width="8" />
                        </template>
                      </el-table-column>
                      <el-table-column prop="gaps" label="Assigned Gaps" width="120" />
                    </el-table>
                  </div>
                </el-col>
              </el-row>
              <div class="budget-section">
                <h4>Budget Planning</h4>
                <el-row :gutter="20">
                  <el-col :span="8">
                    <el-statistic title="Total Budget" :value="1250000" prefix="$" :precision="0" />
                  </el-col>
                  <el-col :span="8">
                    <el-statistic title="Committed" :value="425000" prefix="$" :precision="0" />
                  </el-col>
                  <el-col :span="8">
                    <el-statistic title="Remaining" :value="825000" prefix="$" :precision="0" />
                  </el-col>
                </el-row>
                <el-progress :percentage="34" :stroke-width="12" :format="() => '34% Utilized'" status="success" />
              </div>
            </div>
          </el-tab-pane>

          <!-- Reports Tab -->
          <el-tab-pane label="Reports" name="reports">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>Gap Analysis Reports</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8" v-for="report in reports" :key="report.id">
                  <div class="report-card" @click="downloadReport(report)">
                    <el-icon :size="40"><component :is="report.icon" /></el-icon>
                    <h4>{{ report.title }}</h4>
                    <p>{{ report.description }}</p>
                    <div class="report-meta">
                      <span>Last updated: {{ report.lastUpdated }}</span>
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
        <el-button type="primary" size="large" @click="generateActionPlan">
          <el-icon><Document /></el-icon>
          Generate Action Plan
        </el-button>
        <el-button size="large" @click="exportGapRegister">
          <el-icon><Download /></el-icon>
          Export Gap Register
        </el-button>
        <el-button size="large" @click="scheduleReview">
          <el-icon><Bell /></el-icon>
          Schedule Review Meeting
        </el-button>
      </div>
    </template>

    <!-- Gap Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" title="Gap Details" width="600px">
      <el-descriptions :column="1" border v-if="selectedGap">
        <el-descriptions-item label="Framework">{{ selectedGap.framework }}</el-descriptions-item>
        <el-descriptions-item label="Category">{{ selectedGap.category }}</el-descriptions-item>
        <el-descriptions-item label="Gap Description">{{ selectedGap.gap }}</el-descriptions-item>
        <el-descriptions-item label="Priority">
          <el-tag :type="getPriorityType(selectedGap.priority)">{{ selectedGap.priority }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-select v-model="selectedGap.status" size="small">
            <el-option label="Not Started" value="Not Started" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Completed" value="Completed" />
          </el-select>
        </el-descriptions-item>
        <el-descriptions-item label="Remediation Plan">
          <el-input v-model="selectedGap.remediation" type="textarea" :rows="2" />
        </el-descriptions-item>
        <el-descriptions-item label="Target Date">
          <el-date-picker v-model="selectedGap.targetDate" type="date" placeholder="Select date" />
        </el-descriptions-item>
        <el-descriptions-item label="Assigned To">
          <el-input v-model="selectedGap.assignedTo" placeholder="Assign to team member" />
        </el-descriptions-item>
        <el-descriptions-item label="Notes">
          <el-input v-model="selectedGap.notes" type="textarea" :rows="3" placeholder="Additional notes" />
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveGapDetails">Save Changes</el-button>
      </template>
    </el-dialog>

    <!-- Update Status Dialog -->
    <el-dialog v-model="statusDialogVisible" title="Update Gap Status" width="400px">
      <el-form :model="statusForm">
        <el-form-item label="Current Status">
          <el-select v-model="statusForm.status" placeholder="Select status">
            <el-option label="Not Started" value="Not Started" />
            <el-option label="In Progress" value="In Progress" />
            <el-option label="Completed" value="Completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="Progress %">
          <el-slider v-model="statusForm.progress" :format-tooltip="(val) => `${val}%`" />
        </el-form-item>
        <el-form-item label="Comments">
          <el-input v-model="statusForm.comments" type="textarea" :rows="2" placeholder="Update comments" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveStatusUpdate">Update Status</el-button>
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
const loadingMessage = ref('Analyzing compliance gaps...')

const loadingMessages = [
  'Analyzing compliance gaps...',
  'Mapping framework requirements...',
  'Identifying priority gaps...',
  'Calculating remediation timelines...',
  'Generating action plans...',
  'Ready to display dashboard...'
]

// Filter state
const selectedFrameworks = ref<string[]>(['IFRS S2', 'ISSB', 'GRI', 'TCFD', 'CSRD', 'SGX/HKEX/MAS'])
const searchQuery = ref('')
const priorityFilter = ref('')
const statusFilter = ref('')
const activeTab = ref('overview')
const frameworkCollapse = ref('')
const detailsDialogVisible = ref(false)
const statusDialogVisible = ref(false)
const selectedGap = ref<any>(null)
const statusForm = ref({ status: '', progress: 0, comments: '' })

// Frameworks data
const frameworks = ref([
  { id: 'IFRS S2', name: 'IFRS S2', color: '#f56c6c', gapCount: 8, totalGaps: 12, completedGaps: 4, completionRate: 33 },
  { id: 'ISSB', name: 'ISSB', color: '#409eff', gapCount: 6, totalGaps: 10, completedGaps: 2, completionRate: 20 },
  { id: 'GRI', name: 'GRI', color: '#67c23a', gapCount: 12, totalGaps: 18, completedGaps: 6, completionRate: 33 },
  { id: 'TCFD', name: 'TCFD', color: '#e6a23c', gapCount: 5, totalGaps: 11, completedGaps: 4, completionRate: 36 },
  { id: 'CSRD', name: 'CSRD', color: '#909399', gapCount: 10, totalGaps: 15, completedGaps: 3, completionRate: 20 },
  { id: 'SGX/HKEX/MAS', name: 'SGX/HKEX/MAS', color: '#9c27b0', gapCount: 6, totalGaps: 10, completedGaps: 2, completionRate: 20 }
])

// Complete gap data
const allGapData = ref([
  // IFRS S2 Gaps
  { id: 1, framework: 'IFRS S2', category: 'Governance', gap: 'Board climate expertise disclosure incomplete', priority: 'High', status: 'In Progress', remediation: 'Document board competencies and training', targetDate: '2025-03-31', assignedTo: 'Legal Team', notes: '' },
  { id: 2, framework: 'IFRS S2', category: 'Strategy', gap: '1.5°C scenario analysis not performed', priority: 'High', status: 'Not Started', remediation: 'Run climate scenario analysis', targetDate: '2025-06-30', assignedTo: 'Risk Team', notes: '' },
  { id: 3, framework: 'IFRS S2', category: 'Metrics', gap: 'Scope 3 emissions data incomplete', priority: 'High', status: 'In Progress', remediation: 'Engage suppliers for data collection', targetDate: '2025-09-30', assignedTo: 'Sustainability', notes: '' },

  // ISSB Gaps
  { id: 4, framework: 'ISSB', category: 'Strategy', gap: 'Transition plan not aligned with SBTi', priority: 'High', status: 'Not Started', remediation: 'Develop transition plan', targetDate: '2025-06-30', assignedTo: 'Strategy', notes: '' },
  { id: 5, framework: 'ISSB', category: 'Metrics', gap: 'Industry-based metrics missing', priority: 'Medium', status: 'In Progress', remediation: 'Implement data collection systems', targetDate: '2025-09-30', assignedTo: 'Data Team', notes: '' },

  // GRI Gaps
  { id: 6, framework: 'GRI', category: 'Governance', gap: 'Stakeholder engagement documentation incomplete', priority: 'Medium', status: 'In Progress', remediation: 'Document engagement process', targetDate: '2025-04-30', assignedTo: 'Communications', notes: '' },
  { id: 7, framework: 'GRI', category: 'Environmental', gap: 'Waste reduction targets not quantified', priority: 'Medium', status: 'Not Started', remediation: 'Set measurable waste targets', targetDate: '2025-06-30', assignedTo: 'Ops', notes: '' },
  { id: 8, framework: 'GRI', category: 'Social', gap: 'Diversity metrics not fully disclosed', priority: 'Low', status: 'Not Started', remediation: 'Expand diversity reporting', targetDate: '2025-12-31', assignedTo: 'HR', notes: '' },

  // TCFD Gaps
  { id: 9, framework: 'TCFD', category: 'Strategy', gap: 'Climate scenario analysis for 2°C only', priority: 'High', status: 'In Progress', remediation: 'Add 1.5°C scenario', targetDate: '2025-06-30', assignedTo: 'Risk Team', notes: '' },
  { id: 10, framework: 'TCFD', category: 'Metrics', gap: 'GHG intensity metrics not disclosed', priority: 'Medium', status: 'Not Started', remediation: 'Calculate intensity metrics', targetDate: '2025-09-30', assignedTo: 'Sustainability', notes: '' },

  // CSRD Gaps
  { id: 11, framework: 'CSRD', category: 'Double Materiality', gap: 'Impact materiality not fully assessed', priority: 'High', status: 'In Progress', remediation: 'Complete double materiality assessment', targetDate: '2025-03-31', assignedTo: 'Sustainability', notes: '' },
  { id: 12, framework: 'CSRD', category: 'Data', gap: 'ESG data management system lacking', priority: 'High', status: 'In Progress', remediation: 'Implement ESG platform', targetDate: '2025-06-30', assignedTo: 'IT', notes: '' },
  { id: 13, framework: 'CSRD', category: 'Assurance', gap: 'Limited assurance not arranged', priority: 'Medium', status: 'Not Started', remediation: 'Engage external auditor', targetDate: '2025-12-31', assignedTo: 'Finance', notes: '' },

  // SGX/HKEX/MAS Gaps
  { id: 14, framework: 'SGX/HKEX/MAS', category: 'Climate', gap: 'Board diversity policy incomplete', priority: 'Medium', status: 'In Progress', remediation: 'Finalize diversity targets', targetDate: '2025-03-31', assignedTo: 'Legal', notes: '' },
  { id: 15, framework: 'SGX/HKEX/MAS', category: 'Taxonomy', gap: 'MAS taxonomy alignment not assessed', priority: 'High', status: 'Not Started', remediation: 'Map activities to taxonomy', targetDate: '2025-06-30', assignedTo: 'Sustainability', notes: '' }
])

// Milestones data
const milestones = ref([
  { date: '2025-03-31', title: 'Double Materiality Assessment', description: 'Complete CSRD double materiality assessment', type: 'primary', completed: false, progress: 65 },
  { date: '2025-06-30', title: 'Climate Scenario Analysis', description: 'Complete 1.5°C scenario analysis for TCFD', type: 'primary', completed: false, progress: 30 },
  { date: '2025-09-30', title: 'Scope 3 Data Collection', description: 'Complete Scope 3 emissions inventory', type: 'warning', completed: false, progress: 45 },
  { date: '2025-12-31', title: 'Limited Assurance', description: 'Obtain limited assurance for key metrics', type: 'warning', completed: false, progress: 10 },
  { date: '2026-03-31', title: 'Full Compliance', description: 'All frameworks fully compliant', type: 'success', completed: false, progress: 0 }
])

// Resource data
const resourceData = ref([
  { role: 'Sustainability Lead', assigned: 'Jane Smith', workload: 85, gaps: 8 },
  { role: 'Data Analyst', assigned: 'John Doe', workload: 70, gaps: 6 },
  { role: 'Risk Manager', assigned: 'Mike Johnson', workload: 60, gaps: 5 },
  { role: 'Legal Counsel', assigned: 'Sarah Lee', workload: 50, gaps: 4 },
  { role: 'External Consultant', assigned: 'ESG Advisors', workload: 40, gaps: 3 }
])

// Reports data
const reports = ref([
  { id: 1, title: 'Gap Analysis Summary', description: 'High-level overview of all identified gaps', icon: 'DataAnalysis', format: 'PDF', lastUpdated: '2024-12-01' },
  { id: 2, title: 'Remediation Action Plan', description: 'Detailed plan with timelines and owners', icon: 'Document', format: 'Excel', lastUpdated: '2024-12-01' },
  { id: 3, title: 'Priority Gaps Report', description: 'Focus on high-priority items', icon: 'WarningFilled', format: 'PDF', lastUpdated: '2024-12-01' },
  { id: 4, title: 'Resource Allocation Plan', description: 'Budget and resource requirements', icon: 'User', format: 'Excel', lastUpdated: '2024-12-01' }
])

// Chart refs
const gapByFrameworkChartRef = ref<HTMLElement | null>(null)
const gapByPriorityChartRef = ref<HTMLElement | null>(null)
const gapByCategoryChartRef = ref<HTMLElement | null>(null)
const roadmapChartRef = ref<HTMLElement | null>(null)
const resourceChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Computed
const filteredGapData = computed(() => {
  let data = allGapData.value.filter(gap => selectedFrameworks.value.includes(gap.framework))

  if (searchQuery.value) {
    data = data.filter(gap =>
        gap.gap.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        gap.remediation.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (priorityFilter.value) {
    data = data.filter(gap => gap.priority === priorityFilter.value)
  }

  if (statusFilter.value) {
    data = data.filter(gap => gap.status === statusFilter.value)
  }

  return data
})

// Methods
const goBack = () => {
  router.back()
}

const toggleFramework = (frameworkId: string) => {
  const index = selectedFrameworks.value.indexOf(frameworkId)
  if (index === -1) {
    selectedFrameworks.value.push(frameworkId)
  } else {
    selectedFrameworks.value.splice(index, 1)
  }
}

const clearFilters = () => {
  selectedFrameworks.value = frameworks.value.map(f => f.id)
  searchQuery.value = ''
  priorityFilter.value = ''
  statusFilter.value = ''
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

const getPriorityType = (priority: string) => {
  const map: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'info'
  }
  return map[priority] || 'info'
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Not Started': 'info',
    'In Progress': 'warning',
    'Completed': 'success'
  }
  return map[status] || 'info'
}

const getFrameworkGaps = (frameworkId: string) => {
  return allGapData.value.filter(gap => gap.framework === frameworkId)
}

const viewGapDetails = (gap: any) => {
  selectedGap.value = { ...gap }
  detailsDialogVisible.value = true
}

const saveGapDetails = () => {
  const index = allGapData.value.findIndex(g => g.id === selectedGap.value.id)
  if (index !== -1) {
    allGapData.value[index] = { ...selectedGap.value }
    ElMessage.success('Gap details updated successfully')
  }
  detailsDialogVisible.value = false
}

const updateStatus = (gap: any) => {
  selectedGap.value = gap
  statusForm.value = {
    status: gap.status,
    progress: gap.status === 'Completed' ? 100 : gap.status === 'In Progress' ? 50 : 0,
    comments: ''
  }
  statusDialogVisible.value = true
}

const saveStatusUpdate = () => {
  if (selectedGap.value) {
    selectedGap.value.status = statusForm.value.status
    ElMessage.success(`Gap status updated to ${statusForm.value.status}`)
  }
  statusDialogVisible.value = false
}

const generateActionPlan = () => {
  ElMessage.success('Action plan generation started. You will receive a notification when ready.')
}

const exportGapRegister = () => {
  ElMessage.success('Gap register export started. File will be downloaded shortly.')
}

const scheduleReview = () => {
  ElMessage.info('Review meeting scheduling interface will open in a new window.')
}

const downloadReport = (report: any) => {
  ElMessage.success(`Downloading ${report.title}...`)
}

// Chart initialization
const initGapByFrameworkChart = () => {
  if (gapByFrameworkChartRef.value) {
    const chart = echarts.init(gapByFrameworkChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        type: 'pie',
        radius: '55%',
        data: frameworks.value.map(f => ({ name: f.name, value: f.gapCount, itemStyle: { color: f.color } })),
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initGapByPriorityChart = () => {
  if (gapByPriorityChartRef.value) {
    const chart = echarts.init(gapByPriorityChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        type: 'pie',
        radius: '55%',
        data: [
          { value: 18, name: 'High Priority', itemStyle: { color: '#f56c6c' } },
          { value: 20, name: 'Medium Priority', itemStyle: { color: '#e6a23c' } },
          { value: 9, name: 'Low Priority', itemStyle: { color: '#67c23a' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initGapByCategoryChart = () => {
  if (gapByCategoryChartRef.value) {
    const chart = echarts.init(gapByCategoryChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        type: 'pie',
        radius: '55%',
        data: [
          { value: 12, name: 'Strategy', itemStyle: { color: '#409eff' } },
          { value: 15, name: 'Metrics', itemStyle: { color: '#67c23a' } },
          { value: 8, name: 'Governance', itemStyle: { color: '#e6a23c' } },
          { value: 7, name: 'Data', itemStyle: { color: '#f56c6c' } },
          { value: 5, name: 'Assurance', itemStyle: { color: '#909399' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initRoadmapChart = () => {
  if (roadmapChartRef.value) {
    const chart = echarts.init(roadmapChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026'] },
      yAxis: { type: 'value', name: 'Gaps to Close' },
      series: [{
        type: 'line',
        data: [20, 35, 50, 65, 47],
        smooth: true,
        lineStyle: { color: '#409eff', width: 3 },
        areaStyle: { opacity: 0.3 },
        label: { show: true, formatter: '{c} gaps' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initResourceChart = () => {
  if (resourceChartRef.value) {
    const chart = echarts.init(resourceChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: resourceData.value.map(r => r.role) },
      yAxis: { type: 'value', name: 'Workload %' },
      series: [{
        type: 'bar',
        data: resourceData.value.map(r => r.workload),
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#409eff' },
              { offset: 1, color: '#67c23a' }
            ]
          }
        },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
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
        initGapByFrameworkChart()
        initGapByPriorityChart()
        initGapByCategoryChart()
        initRoadmapChart()
        initResourceChart()
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
.gap-analysis-container {
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
  border-top-color: #f56c6c;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #409eff;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #67c23a;
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
  background: linear-gradient(90deg, #f56c6c, #409eff, #67c23a);
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
.gap-analysis-container {
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

/* Filter Section */
.filter-section {
  margin-bottom: 24px;
}

.filter-card {
  border-radius: 12px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.framework-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f5f7fa;
}

.framework-filter:hover {
  background: #ecf5ff;
}

.framework-filter.active {
  background: #ecf5ff;
  border: 1px solid #409eff;
}

.filter-indicator {
  width: 12px;
  height: 12px;
  border-radius: 4px;
}

.filter-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
}

.filter-count {
  background: #e4e7ed;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
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

/* Table Controls */
.table-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.gaps-table {
  border-radius: 8px;
  overflow: hidden;
}

/* Framework Title */
.framework-title {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.framework-name {
  font-weight: 600;
  width: 140px;
}

.gap-summary {
  font-size: 12px;
  color: #909399;
}

/* Roadmap */
.roadmap-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  height: 450px;
  overflow-y: auto;
}

.roadmap-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.milestone-content {
  margin-left: 8px;
}

.milestone-content strong {
  display: block;
  margin-bottom: 4px;
}

.milestone-content p {
  margin: 4px 0;
  font-size: 12px;
  color: #909399;
}

/* Resource Section */
.resource-table {
  border-radius: 8px;
  overflow: hidden;
}

.budget-section {
  margin-top: 24px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.budget-section h4 {
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

:deep(.el-collapse-item__header) {
  font-weight: 500;
  height: 56px;
}
</style>