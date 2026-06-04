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
          <span class="loading-title">Predictive Maintenance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">AI-Powered Asset Intelligence Platform</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="predictive-maintenance-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Cpu /></el-icon>
          Predictive Maintenance
        </h1>
        <div class="page-subtitle">AI-driven failure prediction and proactive maintenance recommendations</div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="runPrediction" :loading="predicting">
          <el-icon><MagicStick /></el-icon> Run Prediction
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export Report
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
          <el-icon><DataBoard /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.monitoredAssets }}</div>
          <div class="stat-label">Monitored Assets</div>
          <div class="stat-trend up">+8% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.atRiskAssets }}</div>
          <div class="stat-label">At Risk Assets</div>
          <div class="stat-trend down">-2% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgHealthScore }}<span class="unit">%</span></div>
          <div class="stat-label">Avg Health Score</div>
          <div class="stat-trend up">+5.2% improvement</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.predictionsThisMonth }}</div>
          <div class="stat-label">AI Predictions</div>
          <div class="stat-trend up">+18% vs last month</div>
        </div>
      </div>
    </div>

    <!-- Main Content: Two Column Layout -->
    <div class="main-layout">
      <!-- Left: Assets Table -->
      <div class="assets-card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><Grid /></el-icon>
            Asset Health Matrix
            <el-tag size="small" type="success" effect="plain">LIVE</el-tag>
          </div>
          <div class="card-filters">
            <el-input
                v-model="searchText"
                placeholder="Search assets..."
                style="width: 200px"
                clearable
                :prefix-icon="Search"
                size="small"
            />
            <el-select v-model="assetTypeFilter" placeholder="Asset Type" clearable size="small" style="width: 120px">
              <el-option label="All Types" value="" />
              <el-option label="UPS" value="UPS" />
              <el-option label="CRAC" value="CRAC" />
              <el-option label="Generator" value="Generator" />
              <el-option label="PDU" value="PDU" />
              <el-option label="Chiller" value="Chiller" />
            </el-select>
          </div>
        </div>
        <div class="table-wrapper">
          <el-table
              :data="paginatedAssets"
              stripe
              @row-click="viewAssetDetail"
              style="width: 100%"
              height="700"
          >
            <el-table-column prop="name" label="Asset" width="140">
              <template #default="{ row }">
                <div class="asset-name-cell">
                  <span class="asset-type-dot" :class="row.type.toLowerCase()"></span>
                  {{ row.name }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="healthScore" label="Health" width="120">
              <template #default="{ row }">
                <div class="health-progress">
                  <el-progress
                      :percentage="row.healthScore"
                      :stroke-width="8"
                      :color="getHealthColor(row.healthScore)"
                      :show-text="false"
                  />
                  <span class="health-percent">{{ row.healthScore }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="failureProbability" label="Failure Risk" width="130">
              <template #default="{ row }">
                <div class="risk-progress">
                  <el-progress
                      :percentage="row.failureProbability"
                      :stroke-width="8"
                      :color="getRiskColor(row.failureProbability)"
                      :show-text="false"
                  />
                  <span class="risk-percent" :class="getRiskClass(row.failureProbability)">{{ row.failureProbability }}%</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="predictedDate" label="Predicted Failure" width="150">
              <template #default="{ row }">
                <div class="date-cell" :class="{ urgent: getDaysUntilFailure(row.predictedDate) <= 7 }">
                  <el-icon><Calendar /></el-icon>
                  {{ formatDate(row.predictedDate) }}
                  <span class="days-badge">{{ getDaysUntilFailure(row.predictedDate) }} days</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Key Metrics" min-width="200">
              <template #default="{ row }">
                <div class="metrics">
                  <span class="metric" :class="getMetricClass(row.temperature, row.temperatureThreshold)">
                    🌡️ {{ row.temperature }}°C
                  </span>
                  <span class="metric" :class="getMetricClass(row.vibration, row.vibrationThreshold)">
                    📳 {{ row.vibration }} mm/s
                  </span>
                  <span class="metric" :class="getMetricClass(row.load, row.loadThreshold)">
                    ⚡ {{ row.load }}%
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.riskLevel)" size="small">
                  {{ getRiskText(row.riskLevel) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrapper">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[14, 24, 48]"
                :total="totalRecords"
                layout="total, sizes, prev, pager, next"
                background
                small
            />
          </div>
        </div>
      </div>

      <!-- Right: Prediction Workflow -->
      <div class="workflow-card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><Share /></el-icon>
            Prediction Workflow
            <el-tag size="small" type="primary" effect="plain">AI MODEL: RANDOM FOREST</el-tag>
          </div>
        </div>
        <div class="workflow-steps">
          <div class="step completed">
            <div class="step-icon">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="step-content">
              <div class="step-title">Data Collection</div>
              <div class="step-desc">12,847 sensor readings</div>
            </div>
          </div>
          <div class="step-line completed"></div>
          <div class="step completed">
            <div class="step-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="step-content">
              <div class="step-title">Feature Engineering</div>
              <div class="step-desc">128 features extracted</div>
            </div>
          </div>
          <div class="step-line active"></div>
          <div class="step active">
            <div class="step-icon">
              <el-icon><MagicStick /></el-icon>
            </div>
            <div class="step-content">
              <div class="step-title">AI Prediction</div>
              <div class="step-desc">Running inference...</div>
            </div>
            <div class="step-pulse"></div>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-icon">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="step-content">
              <div class="step-title">Risk Assessment</div>
              <div class="step-desc">Pending</div>
            </div>
          </div>
          <div class="step-line"></div>
          <div class="step">
            <div class="step-icon">
              <el-icon><Tools /></el-icon>
            </div>
            <div class="step-content">
              <div class="step-title">Action Required</div>
              <div class="step-desc">Pending</div>
            </div>
          </div>
        </div>
        <div class="model-stats">
          <div class="model-stat">
            <span class="label">Model Accuracy</span>
            <span class="value">94.2%</span>
          </div>
          <div class="model-stat">
            <span class="label">Precision</span>
            <span class="value">93.8%</span>
          </div>
          <div class="model-stat">
            <span class="label">Recall</span>
            <span class="value">92.5%</span>
          </div>
          <div class="model-stat">
            <span class="label">F1 Score</span>
            <span class="value">93.1%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- AI Insights Section -->
    <div class="insights-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><MagicStick /></el-icon>
          AI-Powered Insights
        </div>
        <el-button type="primary" link>View All →</el-button>
      </div>
      <div class="insights-grid">
        <div class="insight-item critical">
          <div class="insight-icon">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="insight-content">
            <div class="insight-title">Generator-01 at critical risk</div>
            <div class="insight-desc">Failure probability 78% - predicted failure in 7 days</div>
          </div>
          <el-button type="danger" size="small" plain>Create Work Order</el-button>
        </div>
        <div class="insight-item warning">
          <div class="insight-icon">
            <el-icon><Bell /></el-icon>
          </div>
          <div class="insight-content">
            <div class="insight-title">CRAC-01 efficiency dropped 15%</div>
            <div class="insight-desc">Compressor inspection recommended within 2 weeks</div>
          </div>
          <el-button type="warning" size="small" plain>Schedule Inspection</el-button>
        </div>
        <div class="insight-item success">
          <div class="insight-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="insight-content">
            <div class="insight-title">5 assets optimized</div>
            <div class="insight-desc">Predicted 23% energy savings through load balancing</div>
          </div>
          <el-button type="success" size="small" plain>View Report</el-button>
        </div>
      </div>
    </div>

    <!-- Asset Detail Modal -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAsset?.name" width="800px" class="detail-dialog">
      <div v-if="selectedAsset" class="asset-detail">
        <!-- Header Stats -->
        <div class="detail-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedAsset.healthScore) }">{{ selectedAsset.healthScore }}%</div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value" :class="getRiskClass(selectedAsset.failureProbability)">{{ selectedAsset.failureProbability }}%</div>
            <div class="detail-stat-label">Failure Probability</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ formatDate(selectedAsset.predictedDate) }}</div>
            <div class="detail-stat-label">Predicted Failure</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ getDaysUntilFailure(selectedAsset.predictedDate) }} days</div>
            <div class="detail-stat-label">Days Until Failure</div>
          </div>
        </div>

        <!-- Sensor Data Table -->
        <div class="detail-section">
          <div class="section-title">Sensor Data</div>
          <el-table :data="selectedAsset.sensors" border stripe size="small">
            <el-table-column prop="name" label="Sensor" width="160" />
            <el-table-column prop="currentValue" label="Current Value" width="140">
              <template #default="{ row }">
                <span :class="getMetricClass(row.currentValue, row.threshold)">
                  {{ row.currentValue }} {{ row.unit }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="threshold" label="Threshold" width="120">
              <template #default="{ row }">{{ row.threshold }} {{ row.unit }}</template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'normal' ? 'success' : (row.status === 'warning' ? 'warning' : 'danger')" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="trend" label="Trend" width="80">
              <template #default="{ row }">
                <span :class="row.trend === 'up' ? 'trend-up' : (row.trend === 'down' ? 'trend-down' : 'trend-stable')">
                  {{ row.trend === 'up' ? '↑' : (row.trend === 'down' ? '↓' : '→') }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Recommendations -->
        <div class="detail-section">
          <div class="section-title">AI Recommendations</div>
          <div class="recommendations">
            <div v-for="(rec, idx) in selectedAsset.recommendations" :key="idx" class="recommendation" :class="rec.severity">
              <div class="rec-status">
                <span class="status-dot"></span>
              </div>
              <div class="rec-content">
                <div class="rec-title">{{ rec.title }}</div>
                <div class="rec-desc">{{ rec.description }}</div>
                <div class="rec-deadline">Recommended by: {{ rec.deadline }}</div>
              </div>
              <el-button type="primary" size="small" @click="createWorkOrder(selectedAsset, rec)">Create Work Order</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Work Order Dialog -->
    <el-dialog v-model="workOrderDialogVisible" title="Create Work Order" width="500px">
      <el-form :model="workOrderForm" label-width="100px">
        <el-form-item label="Title">
          <el-input v-model="workOrderForm.title" />
        </el-form-item>
        <el-form-item label="Priority">
          <el-select v-model="workOrderForm.priority" style="width: 100%">
            <el-option label="Critical" value="critical" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Assigned To">
          <el-select v-model="workOrderForm.assignedTo" style="width: 100%">
            <el-option v-for="eng in engineers" :key="eng.id" :label="eng.name" :value="eng.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="Due Date">
          <el-date-picker v-model="workOrderForm.dueDate" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="workOrderForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="workOrderDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmWorkOrder">Create</el-button>
      </template>
    </el-dialog>

    <!-- Toast -->
    <div v-if="showToast" class="toast-notification" :class="toastType">
      <el-icon><SuccessFilled /></el-icon>
      <span>{{ toastMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Cpu, MagicStick, Download, Refresh, DataBoard, Warning, TrendCharts,
  Calendar, Grid, WarningFilled, Search, Bell, Tools, DataAnalysis,
  Share, SuccessFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing AI models...')
const refreshing = ref(false)
const predicting = ref(false)

const loadingMessages = [
  'Initializing AI models...',
  'Loading asset data...',
  'Training prediction algorithms...',
  'Analyzing sensor telemetry...',
  'Generating insights...'
]

// ==================== Types ====================
interface SensorData {
  name: string
  currentValue: number
  threshold: number
  unit: string
  status: 'normal' | 'warning' | 'critical'
  trend: 'up' | 'down' | 'stable'
}

interface Recommendation {
  title: string
  description: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  deadline: string
}

interface Asset {
  id: number
  name: string
  type: string
  location: string
  healthScore: number
  failureProbability: number
  predictedDate: string
  confidence: number
  riskLevel: 'critical' | 'high' | 'medium' | 'low'
  temperature: number
  temperatureThreshold: number
  vibration: number
  vibrationThreshold: number
  load: number
  loadThreshold: number
  lastMaintenance: string
  sensors: SensorData[]
  recommendations: Recommendation[]
}

interface Engineer {
  id: number
  name: string
  role: string
}

// ==================== Data ====================
const engineers = ref<Engineer[]>([
  { id: 1, name: 'John Chen', role: 'Senior Technician' },
  { id: 2, name: 'Sarah Wong', role: 'HVAC Specialist' },
  { id: 3, name: 'Mike Lim', role: 'Electrical Engineer' },
  { id: 4, name: 'David Tan', role: 'General Technician' },
  { id: 5, name: 'Lisa Ng', role: 'Network Specialist' }
])

const assets = ref<Asset[]>([
  {
    id: 1, name: 'UPS-01', type: 'UPS', location: 'Server Room A',
    healthScore: 92, failureProbability: 8, predictedDate: '2024-08-15', confidence: 87,
    riskLevel: 'low', temperature: 24.5, temperatureThreshold: 30, vibration: 1.2, vibrationThreshold: 3.5, load: 65, loadThreshold: 80,
    lastMaintenance: '2024-05-15',
    sensors: [
      { name: 'Input Voltage', currentValue: 220, threshold: 240, unit: 'V', status: 'normal', trend: 'stable' },
      { name: 'Output Voltage', currentValue: 218, threshold: 230, unit: 'V', status: 'normal', trend: 'stable' },
      { name: 'Battery Temperature', currentValue: 26, threshold: 35, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Fan Speed', currentValue: 2850, threshold: 3000, unit: 'RPM', status: 'normal', trend: 'down' }
    ],
    recommendations: [
      { title: 'Battery Capacity Test', description: 'Battery health has decreased by 5% in last 3 months.', severity: 'medium', deadline: '2024-07-01' },
      { title: 'Fan Bearing Inspection', description: 'Fan RPM showing gradual decline. Inspect bearings.', severity: 'low', deadline: '2024-07-15' }
    ]
  },
  {
    id: 2, name: 'CRAC-01', type: 'CRAC', location: 'Data Center',
    healthScore: 78, failureProbability: 35, predictedDate: '2024-06-25', confidence: 82,
    riskLevel: 'high', temperature: 28.5, temperatureThreshold: 26, vibration: 4.2, vibrationThreshold: 3.5, load: 85, loadThreshold: 80,
    lastMaintenance: '2024-04-10',
    sensors: [
      { name: 'Supply Air Temp', currentValue: 22, threshold: 24, unit: '°C', status: 'warning', trend: 'up' },
      { name: 'Return Air Temp', currentValue: 28, threshold: 26, unit: '°C', status: 'critical', trend: 'up' },
      { name: 'Compressor Pressure', currentValue: 85, threshold: 80, unit: 'psi', status: 'warning', trend: 'up' },
      { name: 'Fan Vibration', currentValue: 4.2, threshold: 3.5, unit: 'mm/s', status: 'critical', trend: 'up' }
    ],
    recommendations: [
      { title: 'Compressor Inspection', description: 'Compressor pressure exceeding threshold. Immediate inspection required.', severity: 'critical', deadline: '2024-06-10' },
      { title: 'Filter Replacement', description: 'Air filters showing 80% loading. Schedule replacement.', severity: 'high', deadline: '2024-06-15' }
    ]
  },
  {
    id: 3, name: 'Generator-01', type: 'Generator', location: 'Generator Room',
    healthScore: 45, failureProbability: 78, predictedDate: '2024-06-05', confidence: 91,
    riskLevel: 'critical', temperature: 95, temperatureThreshold: 90, vibration: 6.5, vibrationThreshold: 4.5, load: 45, loadThreshold: 70,
    lastMaintenance: '2024-03-20',
    sensors: [
      { name: 'Engine Temp', currentValue: 95, threshold: 90, unit: '°C', status: 'critical', trend: 'up' },
      { name: 'Oil Pressure', currentValue: 28, threshold: 35, unit: 'psi', status: 'critical', trend: 'down' },
      { name: 'Battery Voltage', currentValue: 11.8, threshold: 12.5, unit: 'V', status: 'critical', trend: 'down' }
    ],
    recommendations: [
      { title: 'Overheating Issue', description: 'Engine temperature above threshold. Check cooling system.', severity: 'critical', deadline: '2024-06-06' },
      { title: 'Battery Replacement', description: 'Battery voltage dropping. Replace battery immediately.', severity: 'critical', deadline: '2024-06-05' }
    ]
  },
  {
    id: 4, name: 'PDU-A01', type: 'PDU', location: 'Server Row A',
    healthScore: 88, failureProbability: 15, predictedDate: '2024-07-20', confidence: 76,
    riskLevel: 'medium', temperature: 32, temperatureThreshold: 35, vibration: 1.8, vibrationThreshold: 3.0, load: 72, loadThreshold: 80,
    lastMaintenance: '2024-05-01',
    sensors: [
      { name: 'Phase A Current', currentValue: 185, threshold: 200, unit: 'A', status: 'normal', trend: 'up' },
      { name: 'Phase B Current', currentValue: 178, threshold: 200, unit: 'A', status: 'normal', trend: 'stable' },
      { name: 'Phase C Current', currentValue: 192, threshold: 200, unit: 'A', status: 'normal', trend: 'up' }
    ],
    recommendations: [
      { title: 'Load Balancing', description: 'Phase C current 8% higher than average. Rebalance load.', severity: 'medium', deadline: '2024-06-30' },
      { title: 'Thermal Imaging', description: 'Schedule thermal scan to identify hot spots.', severity: 'low', deadline: '2024-07-15' }
    ]
  },
  {
    id: 5, name: 'Chiller-01', type: 'Chiller', location: 'Chiller Plant',
    healthScore: 82, failureProbability: 22, predictedDate: '2024-07-10', confidence: 79,
    riskLevel: 'medium', temperature: 28, temperatureThreshold: 32, vibration: 3.2, vibrationThreshold: 4.0, load: 68, loadThreshold: 85,
    lastMaintenance: '2024-04-25',
    sensors: [
      { name: 'Evaporator Pressure', currentValue: 72, threshold: 80, unit: 'psi', status: 'normal', trend: 'stable' },
      { name: 'Condenser Pressure', currentValue: 195, threshold: 220, unit: 'psi', status: 'normal', trend: 'up' },
      { name: 'Refrigerant Level', currentValue: 45, threshold: 40, unit: '%', status: 'warning', trend: 'down' }
    ],
    recommendations: [
      { title: 'Refrigerant Recharge', description: 'Refrigerant level below threshold. Check for leaks.', severity: 'high', deadline: '2024-06-20' }
    ]
  },
  {
    id: 6, name: 'Transformer-01', type: 'Transformer', location: 'Electrical Room',
    healthScore: 95, failureProbability: 5, predictedDate: '2024-09-15', confidence: 88,
    riskLevel: 'low', temperature: 65, temperatureThreshold: 85, vibration: 1.5, vibrationThreshold: 3.0, load: 55, loadThreshold: 90,
    lastMaintenance: '2024-05-20',
    sensors: [
      { name: 'Oil Temperature', currentValue: 65, threshold: 85, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Winding Temperature', currentValue: 72, threshold: 95, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Oil Level', currentValue: 85, threshold: 80, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { title: 'Oil Analysis', description: 'Schedule DGA oil analysis for preventive maintenance.', severity: 'low', deadline: '2024-07-30' }
    ]
  },
  {
    id: 7, name: 'HVAC-AHU-01', type: 'HVAC', location: 'Mechanical Room',
    healthScore: 72, failureProbability: 42, predictedDate: '2024-06-18', confidence: 84,
    riskLevel: 'high', temperature: 35, temperatureThreshold: 32, vibration: 5.5, vibrationThreshold: 4.0, load: 88, loadThreshold: 85,
    lastMaintenance: '2024-04-05',
    sensors: [
      { name: 'Motor Temp', currentValue: 78, threshold: 75, unit: '°C', status: 'warning', trend: 'up' },
      { name: 'Belt Tension', currentValue: 82, threshold: 90, unit: '%', status: 'warning', trend: 'down' },
      { name: 'Air Flow', currentValue: 2800, threshold: 3000, unit: 'CFM', status: 'warning', trend: 'down' }
    ],
    recommendations: [
      { title: 'Belt Replacement', description: 'Belt tension decreasing. Replace drive belt.', severity: 'high', deadline: '2024-06-15' },
      { title: 'Motor Bearing Check', description: 'Vibration increasing. Inspect motor bearings.', severity: 'high', deadline: '2024-06-12' }
    ]
  },
  {
    id: 8, name: 'CoolingTower-01', type: 'Cooling Tower', location: 'Roof',
    healthScore: 68, failureProbability: 48, predictedDate: '2024-06-22', confidence: 81,
    riskLevel: 'high', temperature: 32, temperatureThreshold: 30, vibration: 4.8, vibrationThreshold: 4.0, load: 75, loadThreshold: 80,
    lastMaintenance: '2024-04-18',
    sensors: [
      { name: 'Water Temp', currentValue: 32, threshold: 30, unit: '°C', status: 'warning', trend: 'up' },
      { name: 'Fan Vibration', currentValue: 4.8, threshold: 4.0, unit: 'mm/s', status: 'critical', trend: 'up' },
      { name: 'Water Level', currentValue: 65, threshold: 60, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { title: 'Fan Balancing', description: 'Vibration levels critical. Balance fan blades.', severity: 'critical', deadline: '2024-06-18' },
      { title: 'Water Treatment', description: 'Temperature rising. Check chemical treatment system.', severity: 'high', deadline: '2024-06-20' }
    ]
  },
  {
    id: 9, name: 'UPS-02', type: 'UPS', location: 'Server Room B',
    healthScore: 85, failureProbability: 18, predictedDate: '2024-07-28', confidence: 83,
    riskLevel: 'medium', temperature: 26.2, temperatureThreshold: 30, vibration: 1.5, vibrationThreshold: 3.5, load: 70, loadThreshold: 80,
    lastMaintenance: '2024-05-10',
    sensors: [
      { name: 'Input Voltage', currentValue: 222, threshold: 240, unit: 'V', status: 'normal', trend: 'stable' },
      { name: 'Output Voltage', currentValue: 220, threshold: 230, unit: 'V', status: 'normal', trend: 'up' },
      { name: 'Battery Temperature', currentValue: 27, threshold: 35, unit: '°C', status: 'normal', trend: 'up' },
      { name: 'Fan Speed', currentValue: 2900, threshold: 3000, unit: 'RPM', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { title: 'Battery Health Check', description: 'Battery temperature rising. Schedule inspection.', severity: 'medium', deadline: '2024-07-15' }
    ]
  },
  {
    id: 10, name: 'CRAC-02', type: 'CRAC', location: 'Data Center',
    healthScore: 81, failureProbability: 28, predictedDate: '2024-07-05', confidence: 80,
    riskLevel: 'high', temperature: 27.5, temperatureThreshold: 26, vibration: 3.8, vibrationThreshold: 3.5, load: 78, loadThreshold: 80,
    lastMaintenance: '2024-04-20',
    sensors: [
      { name: 'Supply Air Temp', currentValue: 23, threshold: 24, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Return Air Temp', currentValue: 27, threshold: 26, unit: '°C', status: 'warning', trend: 'up' },
      { name: 'Compressor Pressure', currentValue: 82, threshold: 80, unit: 'psi', status: 'warning', trend: 'up' },
      { name: 'Fan Vibration', currentValue: 3.8, threshold: 3.5, unit: 'mm/s', status: 'warning', trend: 'up' }
    ],
    recommendations: [
      { title: 'Filter Replacement', description: 'Air filters need replacement.', severity: 'high', deadline: '2024-06-25' },
      { title: 'Vibration Analysis', description: 'Fan vibration increasing. Schedule inspection.', severity: 'medium', deadline: '2024-07-01' }
    ]
  },
  {
    id: 11, name: 'Generator-02', type: 'Generator', location: 'Generator Room',
    healthScore: 82, failureProbability: 25, predictedDate: '2024-07-12', confidence: 85,
    riskLevel: 'medium', temperature: 88, temperatureThreshold: 90, vibration: 4.2, vibrationThreshold: 4.5, load: 50, loadThreshold: 70,
    lastMaintenance: '2024-04-15',
    sensors: [
      { name: 'Engine Temp', currentValue: 88, threshold: 90, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Oil Pressure', currentValue: 32, threshold: 35, unit: 'psi', status: 'warning', trend: 'down' },
      { name: 'Battery Voltage', currentValue: 12.2, threshold: 12.5, unit: 'V', status: 'warning', trend: 'down' },
      { name: 'Fuel Level', currentValue: 65, threshold: 25, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { title: 'Oil Change', description: 'Oil pressure dropping. Schedule oil and filter change.', severity: 'medium', deadline: '2024-07-01' },
      { title: 'Battery Check', description: 'Battery voltage low. Inspect charging system.', severity: 'medium', deadline: '2024-06-28' }
    ]
  },
  {
    id: 12, name: 'PDU-B01', type: 'PDU', location: 'Server Row B',
    healthScore: 91, failureProbability: 12, predictedDate: '2024-08-05', confidence: 82,
    riskLevel: 'low', temperature: 30, temperatureThreshold: 35, vibration: 1.3, vibrationThreshold: 3.0, load: 60, loadThreshold: 80,
    lastMaintenance: '2024-05-25',
    sensors: [
      { name: 'Phase A Current', currentValue: 175, threshold: 200, unit: 'A', status: 'normal', trend: 'stable' },
      { name: 'Phase B Current', currentValue: 172, threshold: 200, unit: 'A', status: 'normal', trend: 'stable' },
      { name: 'Phase C Current', currentValue: 178, threshold: 200, unit: 'A', status: 'normal', trend: 'up' }
    ],
    recommendations: [
      { title: 'Load Monitoring', description: 'Monitor load trends for future capacity planning.', severity: 'low', deadline: '2024-08-01' }
    ]
  },
  {
    id: 13, name: 'Chiller-02', type: 'Chiller', location: 'Chiller Plant',
    healthScore: 75, failureProbability: 32, predictedDate: '2024-07-18', confidence: 78,
    riskLevel: 'high', temperature: 30, temperatureThreshold: 32, vibration: 3.5, vibrationThreshold: 4.0, load: 75, loadThreshold: 85,
    lastMaintenance: '2024-04-08',
    sensors: [
      { name: 'Evaporator Pressure', currentValue: 78, threshold: 80, unit: 'psi', status: 'warning', trend: 'up' },
      { name: 'Condenser Pressure', currentValue: 210, threshold: 220, unit: 'psi', status: 'normal', trend: 'up' },
      { name: 'Refrigerant Level', currentValue: 42, threshold: 40, unit: '%', status: 'warning', trend: 'down' }
    ],
    recommendations: [
      { title: 'Refrigerant Check', description: 'Refrigerant level low. Check for leaks.', severity: 'high', deadline: '2024-07-05' },
      { title: 'Condenser Cleaning', description: 'Schedule condenser coil cleaning.', severity: 'medium', deadline: '2024-07-10' }
    ]
  },
  {
    id: 14, name: 'Transformer-02', type: 'Transformer', location: 'Electrical Room',
    healthScore: 88, failureProbability: 14, predictedDate: '2024-08-20', confidence: 86,
    riskLevel: 'low', temperature: 70, temperatureThreshold: 85, vibration: 1.8, vibrationThreshold: 3.0, load: 60, loadThreshold: 90,
    lastMaintenance: '2024-05-18',
    sensors: [
      { name: 'Oil Temperature', currentValue: 70, threshold: 85, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Winding Temperature', currentValue: 78, threshold: 95, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Oil Level', currentValue: 82, threshold: 80, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { title: 'Oil Sampling', description: 'Schedule routine oil analysis.', severity: 'low', deadline: '2024-08-01' }
    ]
  },
  {
    id: 15, name: 'HVAC-AHU-02', type: 'HVAC', location: 'Mechanical Room',
    healthScore: 70, failureProbability: 45, predictedDate: '2024-06-28', confidence: 79,
    riskLevel: 'critical', temperature: 36, temperatureThreshold: 32, vibration: 5.2, vibrationThreshold: 4.0, load: 85, loadThreshold: 85,
    lastMaintenance: '2024-03-28',
    sensors: [
      { name: 'Motor Temp', currentValue: 82, threshold: 75, unit: '°C', status: 'critical', trend: 'up' },
      { name: 'Belt Tension', currentValue: 78, threshold: 90, unit: '%', status: 'critical', trend: 'down' },
      { name: 'Air Flow', currentValue: 2600, threshold: 3000, unit: 'CFM', status: 'critical', trend: 'down' }
    ],
    recommendations: [
      { title: 'Motor Replacement', description: 'Motor overheating. Immediate replacement recommended.', severity: 'critical', deadline: '2024-06-22' },
      { title: 'Belt Replacement', description: 'Replace drive belt and inspect pulleys.', severity: 'high', deadline: '2024-06-25' }
    ]
  },
  {
    id: 16, name: 'CoolingTower-02', type: 'Cooling Tower', location: 'Roof',
    healthScore: 73, failureProbability: 38, predictedDate: '2024-07-08', confidence: 77,
    riskLevel: 'high', temperature: 31, temperatureThreshold: 30, vibration: 4.5, vibrationThreshold: 4.0, load: 70, loadThreshold: 80,
    lastMaintenance: '2024-04-12',
    sensors: [
      { name: 'Water Temp', currentValue: 31, threshold: 30, unit: '°C', status: 'warning', trend: 'up' },
      { name: 'Fan Vibration', currentValue: 4.5, threshold: 4.0, unit: 'mm/s', status: 'warning', trend: 'up' },
      { name: 'Water Level', currentValue: 70, threshold: 60, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { name: 'Fan Inspection', description: 'Fan vibration increasing. Schedule inspection.', severity: 'high', deadline: '2024-06-30' },
      { name: 'Water Treatment', description: 'Check chemical dosing system.', severity: 'medium', deadline: '2024-07-05' }
    ]
  },
  {
    id: 17, name: 'UPS-03', type: 'UPS', location: 'Server Room C',
    healthScore: 94, failureProbability: 6, predictedDate: '2024-09-01', confidence: 89,
    riskLevel: 'low', temperature: 23.5, temperatureThreshold: 30, vibration: 1.0, vibrationThreshold: 3.5, load: 55, loadThreshold: 80,
    lastMaintenance: '2024-05-28',
    sensors: [
      { name: 'Input Voltage', currentValue: 221, threshold: 240, unit: 'V', status: 'normal', trend: 'stable' },
      { name: 'Output Voltage', currentValue: 219, threshold: 230, unit: 'V', status: 'normal', trend: 'stable' },
      { name: 'Battery Temperature', currentValue: 25, threshold: 35, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Fan Speed', currentValue: 2950, threshold: 3000, unit: 'RPM', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { name: 'Routine Check', description: 'All systems normal. Schedule next routine inspection.', severity: 'low', deadline: '2024-08-15' }
    ]
  },
  {
    id: 18, name: 'CRAC-03', type: 'CRAC', location: 'Data Center',
    healthScore: 84, failureProbability: 20, predictedDate: '2024-07-25', confidence: 81,
    riskLevel: 'medium', temperature: 26.5, temperatureThreshold: 26, vibration: 3.2, vibrationThreshold: 3.5, load: 70, loadThreshold: 80,
    lastMaintenance: '2024-05-05',
    sensors: [
      { name: 'Supply Air Temp', currentValue: 21.5, threshold: 24, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Return Air Temp', currentValue: 26.5, threshold: 26, unit: '°C', status: 'warning', trend: 'up' },
      { name: 'Compressor Pressure', currentValue: 78, threshold: 80, unit: 'psi', status: 'normal', trend: 'stable' },
      { name: 'Fan Vibration', currentValue: 3.2, threshold: 3.5, unit: 'mm/s', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { name: 'Temperature Monitoring', description: 'Return air temperature near threshold. Monitor closely.', severity: 'medium', deadline: '2024-07-10' }
    ]
  },
  {
    id: 19, name: 'Generator-03', type: 'Generator', location: 'Generator Room',
    healthScore: 87, failureProbability: 18, predictedDate: '2024-07-30', confidence: 83,
    riskLevel: 'medium', temperature: 86, temperatureThreshold: 90, vibration: 3.8, vibrationThreshold: 4.5, load: 48, loadThreshold: 70,
    lastMaintenance: '2024-05-12',
    sensors: [
      { name: 'Engine Temp', currentValue: 86, threshold: 90, unit: '°C', status: 'normal', trend: 'stable' },
      { name: 'Oil Pressure', currentValue: 34, threshold: 35, unit: 'psi', status: 'normal', trend: 'stable' },
      { name: 'Battery Voltage', currentValue: 12.4, threshold: 12.5, unit: 'V', status: 'normal', trend: 'stable' },
      { name: 'Fuel Level', currentValue: 70, threshold: 25, unit: '%', status: 'normal', trend: 'stable' }
    ],
    recommendations: [
      { name: 'Monthly Test', description: 'Schedule monthly generator test run.', severity: 'low', deadline: '2024-07-20' }
    ]
  },
  {
    id: 20, name: 'PDU-C01', type: 'PDU', location: 'Server Row C',
    healthScore: 90, failureProbability: 10, predictedDate: '2024-08-25', confidence: 84,
    riskLevel: 'low', temperature: 31, temperatureThreshold: 35, vibration: 1.4, vibrationThreshold: 3.0, load: 62, loadThreshold: 80,
    lastMaintenance: '2024-05-22',
    sensors: [
      { name: 'Phase A Current', currentValue: 180, threshold: 200, unit: 'A', status: 'normal', trend: 'stable' },
      { name: 'Phase B Current', currentValue: 178, threshold: 200, unit: 'A', status: 'normal', trend: 'stable' },
      { name: 'Phase C Current', currentValue: 182, threshold: 200, unit: 'A', status: 'normal', trend: 'up' }
    ],
    recommendations: [
      { name: 'Capacity Planning', description: 'Monitor load growth for future expansion.', severity: 'low', deadline: '2024-08-01' }
    ]
  }
])

// ==================== State ====================
const searchText = ref('')
const assetTypeFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(8)
const detailDialogVisible = ref(false)
const workOrderDialogVisible = ref(false)
const selectedAsset = ref<Asset | null>(null)
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')
let toastTimer: NodeJS.Timeout

const workOrderForm = ref({
  title: '',
  priority: 'high',
  assignedTo: '',
  dueDate: '',
  description: ''
})

// ==================== Computed ====================
const stats = computed(() => ({
  monitoredAssets: assets.value.length,
  atRiskAssets: assets.value.filter(a => a.riskLevel === 'critical' || a.riskLevel === 'high').length,
  avgHealthScore: Math.round(assets.value.reduce((sum, a) => sum + a.healthScore, 0) / assets.value.length),
  predictionsThisMonth: 42
}))

const filteredAssets = computed(() => {
  let filtered = [...assets.value]
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a => a.name.toLowerCase().includes(search))
  }
  if (assetTypeFilter.value) {
    filtered = filtered.filter(a => a.type === assetTypeFilter.value)
  }
  return filtered
})

const totalRecords = computed(() => filteredAssets.value.length)

const paginatedAssets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAssets.value.slice(start, end)
})

// ==================== Helper Functions ====================
const formatDate = (date: string) => {
  const d = new Date(date)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const getRiskText = (risk: string) => {
  const map: Record<string, string> = { critical: 'Critical', high: 'High Risk', medium: 'Medium', low: 'Low Risk' }
  return map[risk] || risk
}

const getStatusTagType = (risk: string) => {
  const map: Record<string, string> = { critical: 'danger', high: 'danger', medium: 'warning', low: 'success' }
  return map[risk] || 'info'
}

const getHealthColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getRiskColor = (prob: number) => {
  if (prob >= 70) return '#f56c6c'
  if (prob >= 40) return '#e6a23c'
  return '#67c23a'
}

const getRiskClass = (prob: number) => {
  if (prob >= 70) return 'critical'
  if (prob >= 40) return 'high'
  return 'low'
}

const getMetricClass = (value: number, threshold: number) => {
  if (value >= threshold * 1.1) return 'critical'
  if (value >= threshold) return 'warning'
  return 'normal'
}

const getDaysUntilFailure = (date: string) => {
  const today = new Date()
  const failureDate = new Date(date)
  const diffTime = failureDate.getTime() - today.getTime()
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

const viewAssetDetail = (asset: Asset) => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
}

const createWorkOrder = (asset: Asset | null, rec: Recommendation) => {
  if (!asset) return
  workOrderForm.value = {
    title: `${asset.name} - ${rec.title}`,
    priority: rec.severity === 'critical' ? 'critical' : (rec.severity === 'high' ? 'high' : 'medium'),
    assignedTo: '',
    dueDate: rec.deadline,
    description: rec.description
  }
  workOrderDialogVisible.value = true
}

const confirmWorkOrder = () => {
  ElMessage.success('Work order created successfully')
  workOrderDialogVisible.value = false
  showToastMessage('Work order created', 'success')
}

const runPrediction = async () => {
  predicting.value = true
  showToastMessage('AI model analyzing sensor data...', 'info')
  await new Promise(resolve => setTimeout(resolve, 1500))
  predicting.value = false
  showToastMessage('Prediction complete - New insights available', 'success')
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Report exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  showToastMessage('Data refreshed', 'success')
}

const showToastMessage = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
  if (toastTimer) clearTimeout(toastTimer)
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  toastTimer = setTimeout(() => {
    showToast.value = false
  }, 3000)
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
.predictive-maintenance-page {
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

.header-right {
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

.stat-trend {
  font-size: 11px;
  margin-top: 6px;
}

.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }

/* Main Layout */
.main-layout {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.assets-card {
  flex: 1.5;
  background: white;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.workflow-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eef2f8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #1e293b;
}

.card-filters {
  display: flex;
  gap: 12px;
}

/* Table */
.table-wrapper {
  padding: 0 20px 20px;
}

.asset-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.asset-type-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.asset-type-dot.ups { background: #3b82f6; }
.asset-type-dot.crac { background: #22c55e; }
.asset-type-dot.generator { background: #ef4444; }
.asset-type-dot.pdu { background: #f59e0b; }
.asset-type-dot.chiller { background: #8b5cf6; }
.asset-type-dot.hvac { background: #ec489a; }

.health-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.health-percent {
  font-size: 13px;
  font-weight: 500;
  min-width: 40px;
}

.risk-progress {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-percent {
  font-size: 13px;
  font-weight: 500;
  min-width: 40px;
}

.risk-percent.critical { color: #ef4444; }
.risk-percent.high { color: #f97316; }
.risk-percent.low { color: #22c55e; }

.date-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.date-cell.urgent { color: #ef4444; font-weight: 600; }

.days-badge {
  font-size: 11px;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 12px;
  color: #64748b;
}

.metrics {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.metric {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
}

.metric.normal { background: #dcfce7; color: #16a34a; }
.metric.warning { background: #fef3c7; color: #d97706; }
.metric.critical { background: #fee2e2; color: #dc2626; }

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* Workflow Steps */
.workflow-steps {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  position: relative;
}

.step.completed {
  background: #f0fdf4;
}

.step.active {
  background: #eff6ff;
  border: 1px solid #3b82f6;
}

.step-icon {
  width: 40px;
  height: 40px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #3b82f6;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.step.completed .step-icon { color: #22c55e; }
.step.active .step-icon { color: #3b82f6; }

.step-content {
  flex: 1;
}

.step-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.step-desc {
  font-size: 12px;
  color: #64748b;
  margin-top: 2px;
}

.step-line {
  width: 2px;
  height: 20px;
  background: #e2e8f0;
  margin-left: 28px;
}

.step-line.completed { background: #22c55e; }
.step-line.active { background: #3b82f6; }

.step-pulse {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

/* Model Stats */
.model-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px 20px;
  background: #f8fafc;
  border-top: 1px solid #eef2f8;
}

.model-stat {
  text-align: center;
}

.model-stat .label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.model-stat .value {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

/* Insights Card */
.insights-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 0 20px 20px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px;
  border-radius: 16px;
  background: #f8fafc;
  transition: all 0.3s;
}

.insight-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.insight-item.critical { border-left: 3px solid #ef4444; }
.insight-item.warning { border-left: 3px solid #f59e0b; }
.insight-item.success { border-left: 3px solid #22c55e; }

.insight-icon {
  font-size: 20px;
}

.insight-item.critical .insight-icon { color: #ef4444; }
.insight-item.warning .insight-icon { color: #f59e0b; }
.insight-item.success .insight-icon { color: #22c55e; }

.insight-content {
  flex: 1;
}

.insight-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
}

.insight-desc {
  font-size: 12px;
  color: #64748b;
}

/* Detail Dialog */
.detail-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.asset-detail {
  padding: 8px;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.detail-stat {
  text-align: center;
}

.detail-stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.detail-stat-value.critical { color: #ef4444; }
.detail-stat-value.high { color: #f97316; }

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: #f8fafc;
  border-radius: 12px;
}

.recommendation.critical { border-left: 3px solid #ef4444; }
.recommendation.high { border-left: 3px solid #f97316; }
.recommendation.medium { border-left: 3px solid #eab308; }

.status-dot {
  display: block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
}

.recommendation.critical .status-dot { background: #ef4444; }
.recommendation.high .status-dot { background: #f97316; }
.recommendation.medium .status-dot { background: #eab308; }

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 4px;
}

.rec-desc {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.rec-deadline {
  font-size: 11px;
  color: #8b5cf6;
}

.trend-up { color: #ef4444; }
.trend-down { color: #22c55e; }
.trend-stable { color: #3b82f6; }

/* Toast */
.toast-notification {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 24px;
  background: white;
  border-radius: 40px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  animation: slideUp 0.3s ease-out;
}

.toast-notification.success { background: #10b981; color: white; }
.toast-notification.error { background: #ef4444; color: white; }
.toast-notification.info { background: #3b82f6; color: white; }

@keyframes slideUp {
  from { opacity: 0; transform: translateX(-50%) translateY(20px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-layout {
    flex-direction: column;
  }

  .insights-grid {
    grid-template-columns: 1fr;
  }

  .detail-stats {
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

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-filters {
    flex-direction: column;
    width: 100%;
  }

  .card-filters .el-input,
  .card-filters .el-select {
    width: 100% !important;
  }
}
</style>