<template>
  <div class="recommendation-center-container">
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
            <span class="loading-title">Loading Recommendation Center</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">AI-Powered Optimization Recommendations</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="recommendation-center-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Recommendation Center</h1>
          <p class="page-subtitle">AI-powered insights and optimization recommendations for your data center</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="runAIAnalysis">
            <el-icon><Cpu /></el-icon>
            Run AI Analysis
          </el-button>
          <el-button @click="exportAllRecommendations">
            <el-icon><Download /></el-icon>
            Export All
          </el-button>
          <el-button @click="configurePreferences">
            <el-icon><Setting /></el-icon>
            Preferences
          </el-button>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="summary-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon blue">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Total Recommendations</span>
                <span class="summary-value">{{ totalRecommendations }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon green">
                <el-icon><DataLine /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Potential Savings</span>
                <span class="summary-value">{{ formatNumber(totalSavings) }} kWh/year</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon orange">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Cost Reduction</span>
                <span class="summary-value">${{ formatNumber(totalCostReduction) }}/year</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-card">
              <div class="summary-icon purple">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="summary-info">
                <span class="summary-label">Carbon Reduction</span>
                <span class="summary-value">{{ formatNumber(totalCarbonReduction) }} tCO₂e/year</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Filter Bar -->
      <div class="filter-section">
        <el-card class="filter-card" shadow="never">
          <div class="filter-row">
            <el-input v-model="searchQuery" placeholder="Search recommendations..." prefix-icon="Search" style="width: 250px" clearable />
            <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
              <el-option label="Cooling" value="cooling" />
              <el-option label="Power" value="power" />
              <el-option label="Space" value="space" />
              <el-option label="Energy" value="energy" />
              <el-option label="Maintenance" value="maintenance" />
            </el-select>
            <el-select v-model="priorityFilter" placeholder="Priority" clearable style="width: 120px">
              <el-option label="High" value="high" />
              <el-option label="Medium" value="medium" />
              <el-option label="Low" value="low" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Pending" value="pending" />
              <el-option label="In Progress" value="in_progress" />
              <el-option label="Implemented" value="implemented" />
              <el-option label="Dismissed" value="dismissed" />
            </el-select>
            <el-button type="primary" @click="clearFilters">Clear Filters</el-button>
          </div>
        </el-card>
      </div>

      <!-- Recommendations Tabs -->
      <el-tabs v-model="activeTab" class="recommendation-tabs">
        <el-tab-pane label="All Recommendations" name="all">
          <div class="recommendations-list">
            <div v-for="rec in filteredRecommendations" :key="rec.id" class="recommendation-card" :class="rec.priority">
              <div class="recommendation-header">
                <div class="rec-type">
                  <el-icon><component :is="getCategoryIcon(rec.category)" /></el-icon>
                  <span class="rec-category">{{ getCategoryName(rec.category) }}</span>
                  <el-tag :type="getPriorityType(rec.priority)" size="small">{{ rec.priority.toUpperCase() }}</el-tag>
                </div>
                <div class="rec-status">
                  <el-tag :type="getStatusType(rec.status)" size="small">{{ getStatusName(rec.status) }}</el-tag>
                </div>
              </div>
              <div class="recommendation-body">
                <h3 class="rec-title">{{ rec.title }}</h3>
                <p class="rec-description">{{ rec.description }}</p>
                <div class="rec-metrics">
                  <div class="metric">
                    <span class="metric-label">Energy Savings</span>
                    <span class="metric-value">{{ formatNumber(rec.energySavings) }} kWh/year</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Cost Savings</span>
                    <span class="metric-value">${{ formatNumber(rec.costSavings) }}/year</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Carbon Reduction</span>
                    <span class="metric-value">{{ formatNumber(rec.carbonReduction) }} tCO₂e</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Investment</span>
                    <span class="metric-value">${{ formatNumber(rec.investment) }}</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Payback</span>
                    <span class="metric-value">{{ rec.payback }} months</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">ROI</span>
                    <span class="metric-value">{{ rec.roi }}%</span>
                  </div>
                </div>
                <div class="rec-actions">
                  <el-button type="primary" size="small" @click="applyRecommendation(rec)">Apply</el-button>
                  <el-button size="small" @click="viewDetails(rec)">Details</el-button>
                  <el-button size="small" @click="dismissRecommendation(rec)">Dismiss</el-button>
                  <el-button size="small" @click="scheduleReminder(rec)">Remind Later</el-button>
                </div>
              </div>
            </div>
            <div v-if="filteredRecommendations.length === 0" class="empty-state">
              <el-empty description="No recommendations found" />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="High Priority" name="high">
          <div class="recommendations-list">
            <div v-for="rec in highPriorityRecommendations" :key="rec.id" class="recommendation-card high">
              <!-- Same structure as above -->
              <div class="recommendation-header">
                <div class="rec-type">
                  <el-icon><component :is="getCategoryIcon(rec.category)" /></el-icon>
                  <span class="rec-category">{{ getCategoryName(rec.category) }}</span>
                  <el-tag type="danger" size="small">HIGH</el-tag>
                </div>
                <div class="rec-status">
                  <el-tag :type="getStatusType(rec.status)" size="small">{{ getStatusName(rec.status) }}</el-tag>
                </div>
              </div>
              <div class="recommendation-body">
                <h3 class="rec-title">{{ rec.title }}</h3>
                <p class="rec-description">{{ rec.description }}</p>
                <div class="rec-metrics">
                  <div class="metric">
                    <span class="metric-label">Energy Savings</span>
                    <span class="metric-value">{{ formatNumber(rec.energySavings) }} kWh/year</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Cost Savings</span>
                    <span class="metric-value">${{ formatNumber(rec.costSavings) }}/year</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Carbon Reduction</span>
                    <span class="metric-value">{{ formatNumber(rec.carbonReduction) }} tCO₂e</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Investment</span>
                    <span class="metric-value">${{ formatNumber(rec.investment) }}</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Payback</span>
                    <span class="metric-value">{{ rec.payback }} months</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">ROI</span>
                    <span class="metric-value">{{ rec.roi }}%</span>
                  </div>
                </div>
                <div class="rec-actions">
                  <el-button type="primary" size="small" @click="applyRecommendation(rec)">Apply</el-button>
                  <el-button size="small" @click="viewDetails(rec)">Details</el-button>
                  <el-button size="small" @click="dismissRecommendation(rec)">Dismiss</el-button>
                  <el-button size="small" @click="scheduleReminder(rec)">Remind Later</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="In Progress" name="inProgress">
          <div class="recommendations-list">
            <div v-for="rec in inProgressRecommendations" :key="rec.id" class="recommendation-card medium">
              <!-- Same structure -->
              <div class="recommendation-header">
                <div class="rec-type">
                  <el-icon><component :is="getCategoryIcon(rec.category)" /></el-icon>
                  <span class="rec-category">{{ getCategoryName(rec.category) }}</span>
                  <el-tag :type="getPriorityType(rec.priority)" size="small">{{ rec.priority.toUpperCase() }}</el-tag>
                </div>
                <div class="rec-status">
                  <el-tag type="warning" size="small">In Progress</el-tag>
                </div>
              </div>
              <div class="recommendation-body">
                <h3 class="rec-title">{{ rec.title }}</h3>
                <p class="rec-description">{{ rec.description }}</p>
                <div class="rec-metrics">
                  <div class="metric">
                    <span class="metric-label">Energy Savings</span>
                    <span class="metric-value">{{ formatNumber(rec.energySavings) }} kWh/year</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Cost Savings</span>
                    <span class="metric-value">${{ formatNumber(rec.costSavings) }}/year</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Carbon Reduction</span>
                    <span class="metric-value">{{ formatNumber(rec.carbonReduction) }} tCO₂e</span>
                  </div>
                </div>
                <div class="rec-progress">
                  <el-progress :percentage="rec.progress || 50" :stroke-width="8" />
                </div>
                <div class="rec-actions">
                  <el-button type="primary" size="small" @click="updateProgress(rec)">Update Progress</el-button>
                  <el-button size="small" @click="viewDetails(rec)">Details</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Implemented" name="implemented">
          <div class="recommendations-list">
            <div v-for="rec in implementedRecommendations" :key="rec.id" class="recommendation-card implemented">
              <div class="recommendation-header">
                <div class="rec-type">
                  <el-icon><component :is="getCategoryIcon(rec.category)" /></el-icon>
                  <span class="rec-category">{{ getCategoryName(rec.category) }}</span>
                </div>
                <div class="rec-status">
                  <el-tag type="success" size="small">Implemented</el-tag>
                </div>
              </div>
              <div class="recommendation-body">
                <h3 class="rec-title">{{ rec.title }}</h3>
                <p class="rec-description">{{ rec.description }}</p>
                <div class="rec-metrics">
                  <div class="metric">
                    <span class="metric-label">Actual Savings</span>
                    <span class="metric-value">{{ formatNumber(rec.actualSavings || rec.energySavings) }} kWh/year</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">Implementation Date</span>
                    <span class="metric-value">{{ rec.implementationDate }}</span>
                  </div>
                </div>
                <div class="rec-actions">
                  <el-button size="small" @click="viewSavingsReport(rec)">View Savings Report</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- Recommendation Detail Dialog -->
      <el-dialog v-model="detailDialogVisible" :title="selectedRecommendation?.title" width="700px">
        <div class="detail-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Category">{{ getCategoryName(selectedRecommendation?.category) }}</el-descriptions-item>
            <el-descriptions-item label="Priority">
              <el-tag :type="getPriorityType(selectedRecommendation?.priority)" size="small">{{ selectedRecommendation?.priority?.toUpperCase() }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="getStatusType(selectedRecommendation?.status)" size="small">{{ getStatusName(selectedRecommendation?.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Created">2024-01-15</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ selectedRecommendation?.description }}</el-descriptions-item>
            <el-descriptions-item label="Energy Savings">{{ formatNumber(selectedRecommendation?.energySavings) }} kWh/year</el-descriptions-item>
            <el-descriptions-item label="Cost Savings">${{ formatNumber(selectedRecommendation?.costSavings) }}/year</el-descriptions-item>
            <el-descriptions-item label="Carbon Reduction">{{ formatNumber(selectedRecommendation?.carbonReduction) }} tCO₂e/year</el-descriptions-item>
            <el-descriptions-item label="Investment">${{ formatNumber(selectedRecommendation?.investment) }}</el-descriptions-item>
            <el-descriptions-item label="Payback Period">{{ selectedRecommendation?.payback }} months</el-descriptions-item>
            <el-descriptions-item label="ROI">{{ selectedRecommendation?.roi }}%</el-descriptions-item>
            <el-descriptions-item label="Implementation Steps" :span="2">
              <ol class="steps-list">
                <li>Review current configuration</li>
                <li>Plan implementation timeline</li>
                <li>Allocate resources</li>
                <li>Execute changes</li>
                <li>Monitor and verify savings</li>
              </ol>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <template #footer>
          <el-button @click="detailDialogVisible = false">Close</el-button>
          <el-button type="primary" @click="applyRecommendation(selectedRecommendation)">Apply Now</el-button>
        </template>
      </el-dialog>

      <!-- Update Progress Dialog -->
      <el-dialog v-model="progressDialogVisible" title="Update Progress" width="450px">
        <el-form>
          <el-form-item label="Progress">
            <el-slider v-model="progressValue" :min="0" :max="100" :step="10" />
          </el-form-item>
          <el-form-item label="Comments">
            <el-input type="textarea" :rows="3" placeholder="Add comments about progress..." v-model="progressComment" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="progressDialogVisible = false">Cancel</el-button>
          <el-button type="primary" @click="saveProgress">Update</el-button>
        </template>
      </el-dialog>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="batchApply">
          <el-icon><Select /></el-icon>
          Batch Apply Selected
        </el-button>
        <el-button size="large" @click="generateActionPlan">
          <el-icon><Document /></el-icon>
          Generate Action Plan
        </el-button>
        <el-button size="large" @click="scheduleReviewMeeting">
          <el-icon><Calendar /></el-icon>
          Schedule Review Meeting
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Cpu, Download, Setting, TrendCharts, DataLine, Coin,
  Search, Document, Calendar, Select, WarningFilled, Check,
  Sunny, WindPower, Grid, Monitor, Tools, Clock
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading recommendations...')

// ==================== Reactive Data ====================
const activeTab = ref('all')
const searchQuery = ref('')
const categoryFilter = ref('')
const priorityFilter = ref('')
const statusFilter = ref('')
const detailDialogVisible = ref(false)
const progressDialogVisible = ref(false)
const selectedRecommendation = ref<any>(null)
const progressValue = ref(50)
const progressComment = ref('')

// Recommendations data
const recommendations = ref([
  {
    id: 1, title: 'Increase Supply Air Temperature',
    description: 'Raise supply air temperature from 22°C to 24°C to reduce cooling energy consumption while maintaining ASHRAE compliance.',
    category: 'cooling', priority: 'high', status: 'pending',
    energySavings: 185000, costSavings: 22200, carbonReduction: 74, investment: 0, payback: 0, roi: 0,
    aiConfidence: 94
  },
  {
    id: 2, title: 'Install Hot Aisle Containment',
    description: 'Implement hot aisle containment to improve cooling efficiency and reduce hot air recirculation.',
    category: 'cooling', priority: 'high', status: 'in_progress',
    energySavings: 320000, costSavings: 38400, carbonReduction: 128, investment: 75000, payback: 23, roi: 51,
    aiConfidence: 89, progress: 45
  },
  {
    id: 3, title: 'Upgrade to LED Lighting',
    description: 'Replace traditional lighting with energy-efficient LED fixtures with motion sensors.',
    category: 'energy', priority: 'medium', status: 'pending',
    energySavings: 85000, costSavings: 10200, carbonReduction: 34, investment: 25000, payback: 29, roi: 41,
    aiConfidence: 96
  },
  {
    id: 4, title: 'Implement Free Cooling',
    description: 'Use outside air for cooling when ambient conditions permit, reducing chiller operation.',
    category: 'cooling', priority: 'high', status: 'pending',
    energySavings: 450000, costSavings: 54000, carbonReduction: 180, investment: 120000, payback: 27, roi: 45,
    aiConfidence: 87
  },
  {
    id: 5, title: 'Optimize UPS Load',
    description: 'Balance UPS load across units to improve efficiency and reduce losses.',
    category: 'power', priority: 'medium', status: 'in_progress',
    energySavings: 65000, costSavings: 7800, carbonReduction: 26, investment: 5000, payback: 8, roi: 156,
    aiConfidence: 92, progress: 70
  },
  {
    id: 6, title: 'Install Blanking Panels',
    description: 'Fill empty rack spaces with blanking panels to prevent airflow bypass.',
    category: 'space', priority: 'low', status: 'implemented',
    energySavings: 28000, costSavings: 3360, carbonReduction: 11, investment: 3000, payback: 11, roi: 112,
    aiConfidence: 98, actualSavings: 29500, implementationDate: '2024-01-10'
  },
  {
    id: 7, title: 'VFD Installation on Fans',
    description: 'Install variable frequency drives on CRAC fan motors for speed control.',
    category: 'cooling', priority: 'high', status: 'pending',
    energySavings: 120000, costSavings: 14400, carbonReduction: 48, investment: 35000, payback: 29, roi: 41,
    aiConfidence: 91
  },
  {
    id: 8, title: 'Predictive Maintenance Program',
    description: 'Implement AI-based predictive maintenance for critical cooling equipment.',
    category: 'maintenance', priority: 'medium', status: 'pending',
    energySavings: 95000, costSavings: 11400, carbonReduction: 38, investment: 45000, payback: 47, roi: 25,
    aiConfidence: 85
  }
])

// Computed totals
const totalRecommendations = computed(() => recommendations.value.length)
const totalSavings = computed(() => recommendations.value.reduce((sum, r) => sum + r.energySavings, 0))
const totalCostReduction = computed(() => recommendations.value.reduce((sum, r) => sum + r.costSavings, 0))
const totalCarbonReduction = computed(() => recommendations.value.reduce((sum, r) => sum + r.carbonReduction, 0))

// Filtered recommendations
const filteredRecommendations = computed(() => {
  let result = recommendations.value

  if (searchQuery.value) {
    result = result.filter(r =>
        r.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
        r.description.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (categoryFilter.value) {
    result = result.filter(r => r.category === categoryFilter.value)
  }

  if (priorityFilter.value) {
    result = result.filter(r => r.priority === priorityFilter.value)
  }

  if (statusFilter.value) {
    result = result.filter(r => r.status === statusFilter.value)
  }

  return result
})

const highPriorityRecommendations = computed(() => {
  return recommendations.value.filter(r => r.priority === 'high' && r.status !== 'implemented')
})

const inProgressRecommendations = computed(() => {
  return recommendations.value.filter(r => r.status === 'in_progress')
})

const implementedRecommendations = computed(() => {
  return recommendations.value.filter(r => r.status === 'implemented')
})

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const getCategoryIcon = (category: string) => {
  const icons: Record<string, any> = {
    cooling: 'WindPower',
    power: 'Monitor',
    space: 'Grid',
    energy: 'DataLine',
    maintenance: 'Tools'
  }
  return icons[category] || 'Setting'
}

const getCategoryName = (category: string) => {
  const names: Record<string, string> = {
    cooling: 'Cooling',
    power: 'Power',
    space: 'Space',
    energy: 'Energy',
    maintenance: 'Maintenance'
  }
  return names[category] || category
}

const getPriorityType = (priority: string) => {
  const types: Record<string, string> = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[priority] || 'info'
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'info',
    in_progress: 'warning',
    implemented: 'success',
    dismissed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusName = (status: string) => {
  const names: Record<string, string> = {
    pending: 'Pending',
    in_progress: 'In Progress',
    implemented: 'Implemented',
    dismissed: 'Dismissed'
  }
  return names[status] || status
}

const clearFilters = () => {
  searchQuery.value = ''
  categoryFilter.value = ''
  priorityFilter.value = ''
  statusFilter.value = ''
}

const runAIAnalysis = () => {
  ElMessage.success('AI analysis started. New recommendations will appear shortly.')
}

const exportAllRecommendations = () => {
  ElMessage.success('Recommendations exported to CSV')
}

const configurePreferences = () => {
  ElMessage.info('Preferences configuration will open')
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applying: ${rec.title}`)
  rec.status = 'in_progress'
  detailDialogVisible.value = false
}

const viewDetails = (rec: any) => {
  selectedRecommendation.value = rec
  detailDialogVisible.value = true
}

const dismissRecommendation = (rec: any) => {
  ElMessage.info(`Recommendation dismissed: ${rec.title}`)
  rec.status = 'dismissed'
}

const scheduleReminder = (rec: any) => {
  ElMessage.info(`Reminder set for ${rec.title}`)
}

const updateProgress = (rec: any) => {
  selectedRecommendation.value = rec
  progressValue.value = rec.progress || 50
  progressDialogVisible.value = true
}

const saveProgress = () => {
  if (selectedRecommendation.value) {
    selectedRecommendation.value.progress = progressValue.value
    if (progressValue.value >= 100) {
      selectedRecommendation.value.status = 'implemented'
      selectedRecommendation.value.implementationDate = new Date().toISOString().split('T')[0]
    }
    ElMessage.success('Progress updated')
  }
  progressDialogVisible.value = false
}

const viewSavingsReport = (rec: any) => {
  ElMessage.info(`Viewing savings report for ${rec.title}`)
}

const batchApply = () => {
  ElMessage.success('Batch apply initiated')
}

const generateActionPlan = () => {
  ElMessage.success('Action plan generated')
}

const scheduleReviewMeeting = () => {
  ElMessage.info('Meeting scheduling interface will open')
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
    }, 400)
  }, 2800)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.recommendation-center-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
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

/* ==================== Main Content ==================== */
.recommendation-center-main {
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
  gap: 12px;
}

/* Summary Section */
.summary-section {
  margin-bottom: 24px;
}

.summary-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.summary-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.summary-icon.blue { background: #eff6ff; color: #3b82f6; }
.summary-icon.green { background: #ecfdf5; color: #10b981; }
.summary-icon.orange { background: #fffbeb; color: #f59e0b; }
.summary-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.summary-info {
  flex: 1;
}

.summary-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.summary-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

/* Filter Section */
.filter-section {
  margin-bottom: 24px;
}

.filter-card {
  border-radius: 16px;
  background: white;
  padding: 16px 20px;
}

.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

/* Recommendation Tabs */
.recommendation-tabs {
  margin-bottom: 24px;
}

.recommendation-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
  background: transparent;
}

.recommendation-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.recommendation-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  padding: 0 20px;
}

.recommendation-tabs :deep(.el-tabs__item.is-active) {
  color: #3b82f6;
}

.recommendation-tabs :deep(.el-tabs__active-bar) {
  background: #3b82f6;
  height: 3px;
}

/* Recommendations List */
.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.recommendation-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
  border-left: 4px solid;
}

.recommendation-card:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.recommendation-card.high {
  border-left-color: #ef4444;
}

.recommendation-card.medium {
  border-left-color: #f59e0b;
}

.recommendation-card.low {
  border-left-color: #10b981;
}

.recommendation-card.implemented {
  border-left-color: #909399;
  opacity: 0.8;
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rec-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rec-category {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}

.rec-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.rec-description {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.rec-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-bottom: 16px;
}

.metric {
  text-align: center;
  min-width: 100px;
}

.metric-label {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.rec-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.rec-progress {
  margin: 12px 0;
}

.empty-state {
  padding: 60px;
  text-align: center;
}

/* Steps List */
.steps-list {
  margin: 0;
  padding-left: 20px;
}

.steps-list li {
  margin: 4px 0;
  font-size: 13px;
  color: #606266;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .recommendation-center-main { padding: 16px; }
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .filter-row { flex-direction: column; align-items: stretch; }
  .filter-row .el-input,
  .filter-row .el-select { width: 100% !important; }
  .rec-metrics { flex-direction: column; gap: 12px; }
  .rec-actions { flex-direction: column; }
  .rec-actions .el-button { width: 100%; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>