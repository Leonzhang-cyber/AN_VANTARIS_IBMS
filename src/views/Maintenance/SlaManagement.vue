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
          <span class="loading-title">SLA Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Service Level Agreement Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="sla-management-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><DataBoard /></el-icon>
          SLA Management
        </h1>
        <div class="page-subtitle">Monitor service level agreements and compliance metrics</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> Create SLA
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
          <div class="stat-value">{{ stats.totalSLA }}</div>
          <div class="stat-label">Total SLAs</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.compliantSLA }}</div>
          <div class="stat-label">Compliant</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.atRiskSLA }}</div>
          <div class="stat-label">At Risk</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.violatedSLA }}</div>
          <div class="stat-label">Violated</div>
        </div>
      </div>
    </div>

    <!-- SLA Overview Chart -->
    <div class="chart-section">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">SLA Compliance Overview</span>
<!--          <span class="chart-subtitle">Current month performance</span>-->
        </div>
        <div class="chart-container" ref="complianceChartEl"></div>
      </div>
      <div class="metrics-card">
        <div class="metrics-header">
          <span>Key Performance Metrics</span>
          <el-tag type="primary" size="small">Monthly Average</el-tag>
        </div>
        <div class="metrics-list">
          <div class="metric-item">
            <div class="metric-info">
              <span class="metric-label">Average Response Time</span>
              <span class="metric-value">{{ metrics.avgResponseTime }} min</span>
            </div>
            <div class="metric-target">Target: ≤{{ metrics.responseTarget }} min</div>
          </div>
          <div class="metric-item">
            <div class="metric-info">
              <span class="metric-label">Average Resolution Time</span>
              <span class="metric-value">{{ metrics.avgResolutionTime }} hrs</span>
            </div>
            <div class="metric-target">Target: ≤{{ metrics.resolutionTarget }} hrs</div>
          </div>
          <div class="metric-item">
            <div class="metric-info">
              <span class="metric-label">Uptime</span>
              <span class="metric-value">{{ metrics.uptime }}%</span>
            </div>
            <div class="metric-target">Target: ≥{{ metrics.uptimeTarget }}%</div>
          </div>
          <div class="metric-item">
            <div class="metric-info">
              <span class="metric-label">First-Time Fix Rate</span>
              <span class="metric-value">{{ metrics.firstTimeFix }}%</span>
            </div>
            <div class="metric-target">Target: ≥{{ metrics.firstTimeFixTarget }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by SLA name or vendor..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="vendorFilter" placeholder="Vendor" clearable filterable style="width: 180px">
          <el-option v-for="v in uniqueVendors" :key="v" :label="v" :value="v" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Compliant" value="compliant" />
          <el-option label="At Risk" value="at-risk" />
          <el-option label="Violated" value="violated" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Overall Compliance: {{ overallCompliance }}%</span>
      </div>
    </div>

    <!-- SLA Cards Grid -->
    <div class="sla-grid">
      <div
          v-for="sla in paginatedSLAs"
          :key="sla.id"
          class="sla-card"
          :class="sla.status"
          @click="viewSLA(sla)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="sla-icon" :class="sla.status">
            <el-icon><DocumentChecked /></el-icon>
          </div>
          <div class="sla-info">
            <div class="sla-name">{{ sla.name }}</div>
            <div class="sla-vendor">{{ sla.vendor }}</div>
          </div>
          <div class="status-badge" :class="sla.status">
            {{ getStatusText(sla.status) }}
          </div>
        </div>

        <!-- Compliance Gauge -->
        <div class="compliance-gauge">
          <div class="gauge-ring">
            <svg width="80" height="80" viewBox="0 0 80 80">
              <circle cx="40" cy="40" r="32" fill="none" stroke="#e2e8f0" stroke-width="6"/>
              <circle cx="40" cy="40" r="32" fill="none"
                      :stroke="getComplianceColor(sla.compliance)"
                      stroke-width="6"
                      :stroke-dasharray="`${sla.compliance * 2.01}, 201`"
                      stroke-linecap="round"
                      transform="rotate(-90 40 40)"/>
            </svg>
            <div class="gauge-value">{{ sla.compliance }}<span class="gauge-percent">%</span></div>
          </div>
          <div class="compliance-stats">
            <div class="stat-row">
              <span>Response:</span>
              <span :class="getMetricClass(sla.avgResponseTime, sla.responseTarget)">
                {{ sla.avgResponseTime }} / {{ sla.responseTarget }} min
              </span>
            </div>
            <div class="stat-row">
              <span>Resolution:</span>
              <span :class="getMetricClass(sla.avgResolutionTime, sla.resolutionTarget)">
                {{ sla.avgResolutionTime }} / {{ sla.resolutionTarget }} hrs
              </span>
            </div>
            <div class="stat-row">
              <span>Uptime:</span>
              <span :class="getMetricClass(sla.uptime, sla.uptimeTarget, true)">
                {{ sla.uptime }} / {{ sla.uptimeTarget }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Contract Info -->
        <div class="contract-info">
          <div class="info-item">
            <el-icon><Calendar /></el-icon>
            <span>Contract: {{ sla.contractCode }}</span>
          </div>
          <div class="info-item">
            <el-icon><Clock /></el-icon>
            <span>Expires: {{ sla.endDate }}</span>
          </div>
        </div>

        <!-- Recent Violations -->
        <div class="violations" v-if="sla.recentViolations.length > 0">
          <div class="violations-header">
            <el-icon><Warning /></el-icon>
            Recent Violations ({{ sla.recentViolations.length }})
          </div>
          <div class="violations-list">
            <div v-for="v in sla.recentViolations.slice(0, 2)" :key="v.id" class="violation-item">
              {{ v.description }}
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-stats">
            <span><el-icon><SuccessFilled /></el-icon> {{ sla.monthlyCompliant }}/{{ sla.monthlyTotal }} compliant</span>
          </div>
          <el-button type="primary" size="small" @click.stop="viewDetails(sla)">
            View Details →
          </el-button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredSLAs.length === 0" class="empty-state">
        <el-empty description="No SLA records found">
          <el-button type="primary" @click="openAddDialog">Create SLA</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="filteredSLAs.length > 0">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[6, 12, 18]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next"
          background
      />
    </div>

    <!-- SLA Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedSLA?.name" width="900px" class="sla-dialog">
      <div v-if="selectedSLA" class="sla-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getComplianceColor(selectedSLA.compliance) }">
              {{ selectedSLA.compliance }}%
            </div>
            <div class="detail-stat-label">Overall Compliance</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedSLA.monthlyCompliant }}/{{ selectedSLA.monthlyTotal }}</div>
            <div class="detail-stat-label">Monthly Performance</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedSLA.avgResponseTime }} min</div>
            <div class="detail-stat-label">Avg Response Time</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedSLA.avgResolutionTime }} hrs</div>
            <div class="detail-stat-label">Avg Resolution Time</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="SLA Name">{{ selectedSLA.name }}</el-descriptions-item>
          <el-descriptions-item label="Vendor">{{ selectedSLA.vendor }}</el-descriptions-item>
          <el-descriptions-item label="Contract Code">{{ selectedSLA.contractCode }}</el-descriptions-item>
          <el-descriptions-item label="Contract Period">{{ selectedSLA.startDate }} - {{ selectedSLA.endDate }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedSLA.status)" size="small">
              {{ getStatusText(selectedSLA.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Last Review Date">{{ selectedSLA.lastReviewDate }}</el-descriptions-item>
        </el-descriptions>

        <!-- SLA Metrics -->
        <div class="detail-section">
          <div class="section-title">SLA Metrics & Targets</div>
          <el-table :data="selectedSLA.metrics" border stripe>
            <el-table-column prop="metric" label="Metric" width="200" />
            <el-table-column prop="target" label="Target" width="120" />
            <el-table-column prop="actual" label="Actual Performance" width="140">
              <template #default="{ row }">
                <span :class="getMetricClass(row.actual, row.target, row.inverse)">
                  {{ row.actual }} {{ row.unit }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="compliance" label="Compliance" width="120">
              <template #default="{ row }">
                <el-progress
                    :percentage="row.compliance"
                    :stroke-width="6"
                    :color="getComplianceColor(row.compliance)"
                    :show-text="true"
                />
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.compliance >= 95 ? 'success' : (row.compliance >= 85 ? 'warning' : 'danger')" size="small">
                  {{ row.compliance >= 95 ? 'Compliant' : (row.compliance >= 85 ? 'At Risk' : 'Violated') }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Monthly Performance Chart -->
        <div class="detail-section">
          <div class="section-title">Monthly Performance Trend</div>
          <div class="trend-chart" ref="trendChartEl"></div>
        </div>

        <!-- Recent Violations -->
        <div class="detail-section" v-if="selectedSLA.recentViolations.length > 0">
          <div class="section-title">Recent Violations</div>
          <el-table :data="selectedSLA.recentViolations" border stripe>
            <el-table-column prop="date" label="Date" width="120" />
            <el-table-column prop="metric" label="Metric" width="150" />
            <el-table-column prop="description" label="Description" min-width="250" />
            <el-table-column prop="resolution" label="Resolution" width="150">
              <template #default="{ row }">
                <el-tag :type="row.resolved ? 'success' : 'warning'" size="small">
                  {{ row.resolved ? 'Resolved' : 'Pending' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editSLA(selectedSLA)">Edit SLA</el-button>
        <el-button type="warning" @click="generateReport(selectedSLA)">Generate Report</el-button>
      </template>
    </el-dialog>

    <!-- Create/Edit SLA Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" class="sla-dialog">
      <el-form :model="slaForm" :rules="formRules" ref="formRef" label-width="130px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="SLA Name" prop="name">
              <el-input v-model="slaForm.name" placeholder="Enter SLA name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Vendor" prop="vendor">
              <el-select v-model="slaForm.vendor" placeholder="Select vendor" filterable style="width: 100%">
                <el-option v-for="v in vendorOptions" :key="v" :label="v" :value="v" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Contract Code" prop="contractCode">
              <el-input v-model="slaForm.contractCode" placeholder="Enter contract code" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="slaForm.status" placeholder="Select status" style="width: 100%">
                <el-option label="Compliant" value="compliant" />
                <el-option label="At Risk" value="at-risk" />
                <el-option label="Violated" value="violated" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Start Date" prop="startDate">
              <el-date-picker
                  v-model="slaForm.startDate"
                  type="date"
                  placeholder="Select start date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="End Date" prop="endDate">
              <el-date-picker
                  v-model="slaForm.endDate"
                  type="date"
                  placeholder="Select end date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">SLA Metrics</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Response Time Target (min)" prop="responseTarget">
              <el-input-number v-model="slaForm.responseTarget" :min="15" :step="15" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Resolution Time Target (hrs)" prop="resolutionTarget">
              <el-input-number v-model="slaForm.resolutionTarget" :min="4" :step="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Uptime Target (%)" prop="uptimeTarget">
              <el-input-number v-model="slaForm.uptimeTarget" :min="95" :max="100" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="First-Time Fix Target (%)" prop="firstTimeFixTarget">
              <el-input-number v-model="slaForm.firstTimeFixTarget" :min="70" :max="100" :step="5" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description" prop="description">
          <el-input v-model="slaForm.description" type="textarea" :rows="2" placeholder="SLA description..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveSLA">Save SLA</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataBoard, Plus, Download, Refresh, Search, CircleCheck,
  Warning, CircleClose, Document, Calendar, Clock, SuccessFilled,
  DocumentChecked
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading SLA data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading SLA data...',
  'Loading vendor information...',
  'Calculating compliance metrics...',
  'Almost ready...'
]

// ==================== Types ====================
interface SLAMetric {
  metric: string
  target: number
  actual: number
  unit: string
  compliance: number
  inverse?: boolean
}

interface SLAViolation {
  id: number
  date: string
  metric: string
  description: string
  resolved: boolean
  resolution?: string
}

interface SLA {
  id: number
  name: string
  vendor: string
  contractCode: string
  startDate: string
  endDate: string
  status: 'compliant' | 'at-risk' | 'violated'
  compliance: number
  avgResponseTime: number
  responseTarget: number
  avgResolutionTime: number
  resolutionTarget: number
  uptime: number
  uptimeTarget: number
  firstTimeFix: number
  firstTimeFixTarget: number
  monthlyCompliant: number
  monthlyTotal: number
  lastReviewDate: string
  metrics: SLAMetric[]
  recentViolations: SLAViolation[]
  description: string
}

// ==================== Mock Data (15 SLAs) ====================
const slas = ref<SLA[]>([
  { id: 1, name: 'UPS Maintenance SLA', vendor: 'Schneider Electric', contractCode: 'CT-2024-001', startDate: '2024-01-01', endDate: '2025-12-31', status: 'compliant', compliance: 98, avgResponseTime: 25, responseTarget: 30, avgResolutionTime: 3.5, resolutionTarget: 4, uptime: 99.98, uptimeTarget: 99.9, firstTimeFix: 92, firstTimeFixTarget: 90, monthlyCompliant: 28, monthlyTotal: 30, lastReviewDate: '2024-05-15',
    metrics: [
      { metric: 'Response Time', target: 30, actual: 25, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 4, actual: 3.5, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.98, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 90, actual: 92, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'Comprehensive UPS maintenance and support services' },
  { id: 2, name: 'CRAC Unit Service SLA', vendor: 'Vertiv Singapore', contractCode: 'CT-2024-002', startDate: '2023-06-01', endDate: '2025-05-31', status: 'compliant', compliance: 95, avgResponseTime: 35, responseTarget: 45, avgResolutionTime: 5, resolutionTarget: 6, uptime: 99.95, uptimeTarget: 99.9, firstTimeFix: 88, firstTimeFixTarget: 85, monthlyCompliant: 26, monthlyTotal: 30, lastReviewDate: '2024-05-10',
    metrics: [
      { metric: 'Response Time', target: 45, actual: 35, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 6, actual: 5, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.95, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 85, actual: 88, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'CRAC unit preventive maintenance and repair services' },
  { id: 3, name: 'Generator Maintenance SLA', vendor: 'Caterpillar Singapore', contractCode: 'CT-2024-003', startDate: '2023-03-15', endDate: '2025-03-14', status: 'at-risk', compliance: 88, avgResponseTime: 50, responseTarget: 45, avgResolutionTime: 8, resolutionTarget: 6, uptime: 99.92, uptimeTarget: 99.95, firstTimeFix: 82, firstTimeFixTarget: 85, monthlyCompliant: 22, monthlyTotal: 30, lastReviewDate: '2024-05-20',
    metrics: [
      { metric: 'Response Time', target: 45, actual: 50, unit: 'min', compliance: 89, inverse: true },
      { metric: 'Resolution Time', target: 6, actual: 8, unit: 'hrs', compliance: 75, inverse: true },
      { metric: 'Uptime', target: 99.95, actual: 99.92, unit: '%', compliance: 94 },
      { metric: 'First-Time Fix', target: 85, actual: 82, unit: '%', compliance: 96 }
    ],
    recentViolations: [
      { id: 1, date: '2024-05-18', metric: 'Resolution Time', description: 'Generator repair took 9.5 hours exceeding 6-hour target', resolved: true, resolution: 'Parts delay - expedited shipping arranged' }
    ],
    description: 'Generator testing and maintenance services' },
  { id: 4, name: 'Chiller Maintenance SLA', vendor: 'Trane Singapore', contractCode: 'CT-2024-004', startDate: '2023-09-01', endDate: '2024-12-31', status: 'compliant', compliance: 96, avgResponseTime: 55, responseTarget: 60, avgResolutionTime: 7, resolutionTarget: 8, uptime: 99.93, uptimeTarget: 99.9, firstTimeFix: 86, firstTimeFixTarget: 85, monthlyCompliant: 27, monthlyTotal: 30, lastReviewDate: '2024-05-12',
    metrics: [
      { metric: 'Response Time', target: 60, actual: 55, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 8, actual: 7, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.93, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 85, actual: 86, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'Chiller system maintenance and repairs' },
  { id: 5, name: 'Electrical Equipment SLA', vendor: 'ABB Singapore', contractCode: 'CT-2024-005', startDate: '2024-02-01', endDate: '2026-01-31', status: 'compliant', compliance: 99, avgResponseTime: 28, responseTarget: 30, avgResolutionTime: 3, resolutionTarget: 4, uptime: 99.99, uptimeTarget: 99.9, firstTimeFix: 94, firstTimeFixTarget: 90, monthlyCompliant: 29, monthlyTotal: 30, lastReviewDate: '2024-05-18',
    metrics: [
      { metric: 'Response Time', target: 30, actual: 28, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 4, actual: 3, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.99, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 90, actual: 94, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'Electrical equipment supply and support' },
  { id: 6, name: 'Battery Replacement SLA', vendor: 'Battery Supply Co.', contractCode: 'CT-2024-006', startDate: '2023-01-01', endDate: '2024-12-31', status: 'at-risk', compliance: 85, avgResponseTime: 28, responseTarget: 24, avgResolutionTime: 4.5, resolutionTarget: 4, uptime: 99.88, uptimeTarget: 99.95, firstTimeFix: 88, firstTimeFixTarget: 90, monthlyCompliant: 20, monthlyTotal: 30, lastReviewDate: '2024-05-05',
    metrics: [
      { metric: 'Response Time', target: 24, actual: 28, unit: 'min', compliance: 83, inverse: true },
      { metric: 'Resolution Time', target: 4, actual: 4.5, unit: 'hrs', compliance: 88, inverse: true },
      { metric: 'Uptime', target: 99.95, actual: 99.88, unit: '%', compliance: 86 },
      { metric: 'First-Time Fix', target: 90, actual: 88, unit: '%', compliance: 98 }
    ],
    recentViolations: [
      { id: 2, date: '2024-05-22', metric: 'Response Time', description: 'Response to battery alert exceeded 24-min target', resolved: false },
      { id: 3, date: '2024-05-15', metric: 'Uptime', description: 'UPS downtime due to delayed battery replacement', resolved: true, resolution: 'Battery replaced within 48 hours' }
    ],
    description: 'Battery health monitoring and replacement' },
  { id: 7, name: 'HVAC Parts Supply SLA', vendor: 'HVAC Supplies Inc.', contractCode: 'CT-2024-007', startDate: '2023-07-01', endDate: '2025-06-30', status: 'compliant', compliance: 97, avgResponseTime: 12, responseTarget: 24, avgResolutionTime: 2, resolutionTarget: 4, uptime: 99.96, uptimeTarget: 99.9, firstTimeFix: 93, firstTimeFixTarget: 85, monthlyCompliant: 28, monthlyTotal: 30, lastReviewDate: '2024-05-08',
    metrics: [
      { metric: 'Response Time', target: 24, actual: 12, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 4, actual: 2, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.96, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 85, actual: 93, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'HVAC spare parts supply' },
  { id: 8, name: 'Electrical Parts SLA', vendor: 'Electrical Parts Ltd.', contractCode: 'CT-2024-008', startDate: '2023-11-01', endDate: '2024-10-31', status: 'compliant', compliance: 94, avgResponseTime: 18, responseTarget: 24, avgResolutionTime: 3.5, resolutionTarget: 4, uptime: 99.92, uptimeTarget: 99.9, firstTimeFix: 89, firstTimeFixTarget: 85, monthlyCompliant: 25, monthlyTotal: 30, lastReviewDate: '2024-05-14',
    metrics: [
      { metric: 'Response Time', target: 24, actual: 18, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 4, actual: 3.5, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.92, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 85, actual: 89, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'Electrical components supply' },
  { id: 9, name: 'Eaton UPS SLA', vendor: 'Eaton Singapore', contractCode: 'CT-2024-009', startDate: '2024-03-01', endDate: '2026-02-28', status: 'compliant', compliance: 98, avgResponseTime: 22, responseTarget: 30, avgResolutionTime: 3.2, resolutionTarget: 4, uptime: 99.97, uptimeTarget: 99.9, firstTimeFix: 91, firstTimeFixTarget: 90, monthlyCompliant: 28, monthlyTotal: 30, lastReviewDate: '2024-05-16',
    metrics: [
      { metric: 'Response Time', target: 30, actual: 22, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 4, actual: 3.2, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.97, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 90, actual: 91, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'UPS maintenance and support' },
  { id: 10, name: 'Generator Parts SLA', vendor: 'Generator Parts Co.', contractCode: 'CT-2024-010', startDate: '2023-08-01', endDate: '2025-07-31', status: 'compliant', compliance: 95, avgResponseTime: 32, responseTarget: 45, avgResolutionTime: 5.5, resolutionTarget: 6, uptime: 99.94, uptimeTarget: 99.9, firstTimeFix: 87, firstTimeFixTarget: 85, monthlyCompliant: 26, monthlyTotal: 30, lastReviewDate: '2024-05-09',
    metrics: [
      { metric: 'Response Time', target: 45, actual: 32, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 6, actual: 5.5, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.94, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 85, actual: 87, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'Generator parts supply' },
  { id: 11, name: 'Cable Supply SLA', vendor: 'Cable Solutions', contractCode: 'CT-2024-011', startDate: '2023-12-01', endDate: '2024-11-30', status: 'violated', compliance: 78, avgResponseTime: 35, responseTarget: 24, avgResolutionTime: 5, resolutionTarget: 4, uptime: 99.85, uptimeTarget: 99.95, firstTimeFix: 80, firstTimeFixTarget: 85, monthlyCompliant: 18, monthlyTotal: 30, lastReviewDate: '2024-05-22',
    metrics: [
      { metric: 'Response Time', target: 24, actual: 35, unit: 'min', compliance: 54, inverse: true },
      { metric: 'Resolution Time', target: 4, actual: 5, unit: 'hrs', compliance: 75, inverse: true },
      { metric: 'Uptime', target: 99.95, actual: 99.85, unit: '%', compliance: 80 },
      { metric: 'First-Time Fix', target: 85, actual: 80, unit: '%', compliance: 94 }
    ],
    recentViolations: [
      { id: 4, date: '2024-05-20', metric: 'Response Time', description: 'Delayed response to urgent cable request', resolved: false },
      { id: 5, date: '2024-05-15', metric: 'Uptime', description: 'Network downtime due to cable quality issue', resolved: true, resolution: 'Replaced defective cables' }
    ],
    description: 'Cable and connectivity solutions' },
  { id: 12, name: 'Building Automation SLA', vendor: 'Johnson Controls', contractCode: 'CT-2024-012', startDate: '2022-10-01', endDate: '2024-09-30', status: 'compliant', compliance: 96, avgResponseTime: 25, responseTarget: 30, avgResolutionTime: 4.2, resolutionTarget: 5, uptime: 99.96, uptimeTarget: 99.9, firstTimeFix: 90, firstTimeFixTarget: 88, monthlyCompliant: 27, monthlyTotal: 30, lastReviewDate: '2024-05-11',
    metrics: [
      { metric: 'Response Time', target: 30, actual: 25, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 5, actual: 4.2, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.96, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 88, actual: 90, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'Building automation system maintenance' },
  { id: 13, name: 'Electrical Systems SLA', vendor: 'Siemens Singapore', contractCode: 'CT-2024-013', startDate: '2024-04-01', endDate: '2026-03-31', status: 'compliant', compliance: 99, avgResponseTime: 20, responseTarget: 30, avgResolutionTime: 2.8, resolutionTarget: 4, uptime: 99.99, uptimeTarget: 99.9, firstTimeFix: 95, firstTimeFixTarget: 90, monthlyCompliant: 29, monthlyTotal: 30, lastReviewDate: '2024-05-17',
    metrics: [
      { metric: 'Response Time', target: 30, actual: 20, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 4, actual: 2.8, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.99, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 90, actual: 95, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'Electrical systems support' },
  { id: 14, name: 'Facility Maintenance SLA', vendor: 'Maintenance Solutions Pte Ltd', contractCode: 'CT-2024-014', startDate: '2023-05-01', endDate: '2025-04-30', status: 'compliant', compliance: 97, avgResponseTime: 30, responseTarget: 45, avgResolutionTime: 5.5, resolutionTarget: 6, uptime: 99.95, uptimeTarget: 99.9, firstTimeFix: 89, firstTimeFixTarget: 85, monthlyCompliant: 28, monthlyTotal: 30, lastReviewDate: '2024-05-13',
    metrics: [
      { metric: 'Response Time', target: 45, actual: 30, unit: 'min', compliance: 100, inverse: true },
      { metric: 'Resolution Time', target: 6, actual: 5.5, unit: 'hrs', compliance: 100, inverse: true },
      { metric: 'Uptime', target: 99.9, actual: 99.95, unit: '%', compliance: 100 },
      { metric: 'First-Time Fix', target: 85, actual: 89, unit: '%', compliance: 100 }
    ],
    recentViolations: [],
    description: 'Comprehensive facility maintenance' },
  { id: 15, name: 'UPS Parts SLA', vendor: 'UPS Parts Direct', contractCode: 'CT-2024-015', startDate: '2023-10-01', endDate: '2024-09-30', status: 'at-risk', compliance: 84, avgResponseTime: 28, responseTarget: 24, avgResolutionTime: 3.2, resolutionTarget: 3, uptime: 99.90, uptimeTarget: 99.95, firstTimeFix: 86, firstTimeFixTarget: 88, monthlyCompliant: 21, monthlyTotal: 30, lastReviewDate: '2024-05-19',
    metrics: [
      { metric: 'Response Time', target: 24, actual: 28, unit: 'min', compliance: 83, inverse: true },
      { metric: 'Resolution Time', target: 3, actual: 3.2, unit: 'hrs', compliance: 93, inverse: true },
      { metric: 'Uptime', target: 99.95, actual: 99.90, unit: '%', compliance: 90 },
      { metric: 'First-Time Fix', target: 88, actual: 86, unit: '%', compliance: 98 }
    ],
    recentViolations: [
      { id: 6, date: '2024-05-21', metric: 'Response Time', description: 'Slow response to urgent part request', resolved: true, resolution: 'Expedited shipping arranged' }
    ],
    description: 'UPS parts and consumables supply' }
])

// ==================== State ====================
const searchText = ref('')
const vendorFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(6)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('Create SLA')
const selectedSLA = ref<SLA | null>(null)
const editingSLA = ref<SLA | null>(null)
const formRef = ref()

let complianceChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
const complianceChartEl = ref<HTMLElement | null>(null)
const trendChartEl = ref<HTMLElement | null>(null)

const slaForm = ref({
  id: null as number | null,
  name: '',
  vendor: '',
  contractCode: '',
  startDate: '',
  endDate: '',
  status: 'compliant' as 'compliant' | 'at-risk' | 'violated',
  responseTarget: 30,
  resolutionTarget: 4,
  uptimeTarget: 99.9,
  firstTimeFixTarget: 85,
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter SLA name', trigger: 'blur' }],
  vendor: [{ required: true, message: 'Please select vendor', trigger: 'change' }],
  startDate: [{ required: true, message: 'Please select start date', trigger: 'change' }],
  endDate: [{ required: true, message: 'Please select end date', trigger: 'change' }]
}

// ==================== Computed ====================
const uniqueVendors = computed(() => {
  return [...new Set(slas.value.map(s => s.vendor))]
})

const vendorOptions = computed(() => {
  return [...uniqueVendors.value]
})

const stats = computed(() => {
  const totalSLA = slas.value.length
  const compliantSLA = slas.value.filter(s => s.status === 'compliant').length
  const atRiskSLA = slas.value.filter(s => s.status === 'at-risk').length
  const violatedSLA = slas.value.filter(s => s.status === 'violated').length
  return { totalSLA, compliantSLA, atRiskSLA, violatedSLA }
})

const metrics = computed(() => {
  const avgResponseTime = Math.round(slas.value.reduce((sum, s) => sum + s.avgResponseTime, 0) / slas.value.length)
  const avgResolutionTime = (slas.value.reduce((sum, s) => sum + s.avgResolutionTime, 0) / slas.value.length).toFixed(1)
  const uptime = (slas.value.reduce((sum, s) => sum + s.uptime, 0) / slas.value.length).toFixed(2)
  const firstTimeFix = Math.round(slas.value.reduce((sum, s) => sum + s.firstTimeFix, 0) / slas.value.length)

  return {
    avgResponseTime,
    avgResolutionTime: parseFloat(avgResolutionTime),
    uptime: parseFloat(uptime),
    firstTimeFix,
    responseTarget: 30,
    resolutionTarget: 4,
    uptimeTarget: 99.9,
    firstTimeFixTarget: 85
  }
})

const overallCompliance = computed(() => {
  return Math.round(slas.value.reduce((sum, s) => sum + s.compliance, 0) / slas.value.length)
})

const filteredSLAs = computed(() => {
  let filtered = [...slas.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(search) ||
        s.vendor.toLowerCase().includes(search) ||
        s.contractCode.toLowerCase().includes(search)
    )
  }

  if (vendorFilter.value) {
    filtered = filtered.filter(s => s.vendor === vendorFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(s => s.status === statusFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredSLAs.value.length)

const paginatedSLAs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSLAs.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getStatusText = (status: string): string => {
  const map: Record<string, string> = { compliant: 'Compliant', 'at-risk': 'At Risk', violated: 'Violated' }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { compliant: 'success', 'at-risk': 'warning', violated: 'danger' }
  return map[status] || 'info'
}

const getComplianceColor = (compliance: number): string => {
  if (compliance >= 95) return '#22c55e'
  if (compliance >= 85) return '#f59e0b'
  return '#ef4444'
}

const getMetricClass = (actual: number, target: number, inverse: boolean = false): string => {
  if (inverse) {
    if (actual <= target) return 'metric-good'
    if (actual <= target * 1.2) return 'metric-warning'
    return 'metric-bad'
  } else {
    if (actual >= target) return 'metric-good'
    if (actual >= target * 0.9) return 'metric-warning'
    return 'metric-bad'
  }
}

const openAddDialog = () => {
  dialogTitle.value = 'Create SLA'
  editingSLA.value = null
  slaForm.value = {
    id: null,
    name: '',
    vendor: '',
    contractCode: '',
    startDate: new Date().toISOString().slice(0, 10),
    endDate: '',
    status: 'compliant',
    responseTarget: 30,
    resolutionTarget: 4,
    uptimeTarget: 99.9,
    firstTimeFixTarget: 85,
    description: ''
  }
  dialogVisible.value = true
}

const editSLA = (sla: SLA | null) => {
  if (!sla) return
  dialogTitle.value = 'Edit SLA'
  editingSLA.value = sla
  slaForm.value = {
    id: sla.id,
    name: sla.name,
    vendor: sla.vendor,
    contractCode: sla.contractCode,
    startDate: sla.startDate,
    endDate: sla.endDate,
    status: sla.status,
    responseTarget: sla.responseTarget,
    resolutionTarget: sla.resolutionTarget,
    uptimeTarget: sla.uptimeTarget,
    firstTimeFixTarget: sla.firstTimeFixTarget,
    description: sla.description
  }
  dialogVisible.value = true
}

const viewSLA = (sla: SLA) => {
  selectedSLA.value = sla
  detailDialogVisible.value = true
  nextTick(() => initTrendChart(sla))
}

const viewDetails = (sla: SLA) => {
  viewSLA(sla)
}

const saveSLA = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    if (editingSLA.value) {
      const index = slas.value.findIndex(s => s.id === editingSLA.value!.id)
      if (index !== -1) {
        slas.value[index] = {
          ...slas.value[index],
          name: slaForm.value.name,
          vendor: slaForm.value.vendor,
          contractCode: slaForm.value.contractCode,
          startDate: slaForm.value.startDate,
          endDate: slaForm.value.endDate,
          status: slaForm.value.status,
          responseTarget: slaForm.value.responseTarget,
          resolutionTarget: slaForm.value.resolutionTarget,
          uptimeTarget: slaForm.value.uptimeTarget,
          firstTimeFixTarget: slaForm.value.firstTimeFixTarget,
          description: slaForm.value.description
        }
        ElMessage.success('SLA updated')
      }
    } else {
      const newId = Math.max(...slas.value.map(s => s.id), 0) + 1
      slas.value.push({
        id: newId,
        name: slaForm.value.name,
        vendor: slaForm.value.vendor,
        contractCode: slaForm.value.contractCode,
        startDate: slaForm.value.startDate,
        endDate: slaForm.value.endDate,
        status: slaForm.value.status,
        compliance: 100,
        avgResponseTime: 0,
        responseTarget: slaForm.value.responseTarget,
        avgResolutionTime: 0,
        resolutionTarget: slaForm.value.resolutionTarget,
        uptime: 100,
        uptimeTarget: slaForm.value.uptimeTarget,
        firstTimeFix: 100,
        firstTimeFixTarget: slaForm.value.firstTimeFixTarget,
        monthlyCompliant: 0,
        monthlyTotal: 0,
        lastReviewDate: new Date().toISOString().slice(0, 10),
        metrics: [],
        recentViolations: [],
        description: slaForm.value.description
      })
      ElMessage.success('SLA created')
    }

    dialogVisible.value = false
  })
}

const generateReport = (sla: SLA | null) => {
  if (!sla) return
  ElMessage.success(`Generating report for ${sla.name}`)
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('SLA data exported')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Charts ====================
const initComplianceChart = () => {
  if (!complianceChartEl.value) return
  if (complianceChart) complianceChart.dispose()

  // 使用真实的 SLA 数据
  const topSLAs = slas.value.slice(0, 8)
  const categories = topSLAs.map(s => s.name.length > 12 ? s.name.slice(0, 12) + '...' : s.name)
  const complianceData = topSLAs.map(s => s.compliance)

  complianceChart = echarts.init(complianceChartEl.value)
  complianceChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Compliance: {c}%' },
    grid: { top: 30, left: 50, right: 20, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { rotate: 30, fontSize: 11, interval: 0, margin: 10 }
    },
    yAxis: { type: 'value', name: 'Compliance (%)', min: 60, max: 100, nameLocation: 'middle', nameGap: 35 },
    series: [{
      type: 'bar',
      data: complianceData,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 95) return '#22c55e'
          if (value >= 85) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%', fontSize: 11 }
    }]
  })
}

const initTrendChart = (sla: SLA) => {
  if (!trendChartEl.value) return
  if (trendChart) trendChart.dispose()

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  // 模拟过去6个月的数据趋势
  const baseCompliance = sla.compliance
  const complianceData = [
    Math.max(60, baseCompliance - 8 + Math.random() * 4),
    Math.max(60, baseCompliance - 5 + Math.random() * 4),
    Math.max(60, baseCompliance - 3 + Math.random() * 4),
    Math.max(60, baseCompliance - 1 + Math.random() * 4),
    Math.max(60, baseCompliance - 2 + Math.random() * 4),
    baseCompliance
  ].map(v => Math.min(100, Math.round(v)))

  const targetData = [sla.compliance >= 95 ? 95 : sla.compliance >= 85 ? 90 : 85, 95, 95, 95, 95, 95]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Actual Compliance', 'Target'], bottom: 0, left: 'center' },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: months, axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', name: 'Compliance (%)', min: 60, max: 100 },
    series: [
      {
        name: 'Actual Compliance',
        type: 'line',
        data: complianceData,
        smooth: true,
        lineStyle: { color: '#3b82f6', width: 3 },
        symbol: 'circle',
        symbolSize: 8,
        areaStyle: { opacity: 0.1, color: '#3b82f6' },
        itemStyle: { color: '#3b82f6' }
      },
      {
        name: 'Target',
        type: 'line',
        data: targetData,
        lineStyle: { color: '#ef4444', width: 2, type: 'dashed' },
        symbol: 'none'
      }
    ]
  })
}

// ==================== Watch for chart updates ====================
watch(filteredSLAs, () => {
  nextTick(() => {
    initComplianceChart()
  })
})

// 监听 isLoaded，页面加载完成后初始化图表
watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initComplianceChart()
    })
  }
})

// 窗口缩放时重绘图表
const handleResize = () => {
  if (complianceChart) complianceChart.resize()
  if (trendChart) trendChart.resize()
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
  window.addEventListener('resize', handleResize)
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
.sla-management-page {
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
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

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

/* Chart Section */
.chart-section {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1.5;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-header {
  margin-bottom: 16px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 260px;
  width: 100%;
  min-height: 220px;
}

.metrics-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.metrics-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  color: #1e293b;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.metric-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.metric-label {
  font-size: 13px;
  color: #64748b;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.metric-target {
  font-size: 11px;
  color: #64748b;
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

/* SLA Grid */
.sla-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.sla-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.sla-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.sla-card.compliant { border-left: 4px solid #22c55e; }
.sla-card.at-risk { border-left: 4px solid #f59e0b; }
.sla-card.violated { border-left: 4px solid #ef4444; }

.card-header {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid #eef2f8;
}

.sla-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.sla-icon.compliant { background: #dcfce7; color: #22c55e; }
.sla-icon.at-risk { background: #fef3c7; color: #f59e0b; }
.sla-icon.violated { background: #fee2e2; color: #ef4444; }

.sla-info {
  flex: 1;
}

.sla-name {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 4px;
}

.sla-vendor {
  font-size: 12px;
  color: #64748b;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.compliant { background: #dcfce7; color: #16a34a; }
.status-badge.at-risk { background: #fef3c7; color: #d97706; }
.status-badge.violated { background: #fee2e2; color: #dc2626; }

/* Compliance Gauge */
.compliance-gauge {
  padding: 16px 20px;
  display: flex;
  gap: 20px;
  border-bottom: 1px solid #eef2f8;
  background: #f8fafc;
}

.gauge-ring {
  position: relative;
  width: 80px;
  height: 80px;
}

.gauge-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 20px;
  font-weight: 700;
}

.gauge-percent {
  font-size: 10px;
}

.compliance-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.stat-row span:first-child {
  color: #64748b;
}

.metric-good { color: #22c55e; font-weight: 600; }
.metric-warning { color: #f59e0b; font-weight: 600; }
.metric-bad { color: #ef4444; font-weight: 600; }

/* Contract Info */
.contract-info {
  padding: 12px 20px;
  display: flex;
  gap: 20px;
  border-bottom: 1px solid #eef2f8;
  font-size: 12px;
  color: #64748b;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Violations */
.violations {
  padding: 12px 20px;
  border-bottom: 1px solid #eef2f8;
  background: #fef2f2;
}

.violations-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 8px;
}

.violations-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.violation-item {
  font-size: 11px;
  color: #dc2626;
}

/* Card Footer */
.card-footer {
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #64748b;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: flex-end;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 60px;
  background: white;
  border-radius: 20px;
  text-align: center;
}

/* Dialog */
.sla-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.sla-detail {
  padding: 8px;
}

.detail-header-stats {
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
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
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

.trend-chart {
  height: 280px;
  width: 100%;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-section {
    flex-direction: column;
  }

  .sla-grid {
    grid-template-columns: 1fr;
  }

  .detail-header-stats {
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

/* 补充缺失全局样式 & Element深度样式 */
:deep(.el-tag--success) {
  background-color: #dcfce7;
  border-color: #22c55e;
  color: #16a34a;
}
:deep(.el-tag--warning) {
  background-color: #fef3c7;
  border-color: #f59e0b;
  color: #d97706;
}
:deep(.el-tag--danger) {
  background-color: #fee2e2;
  border-color: #ef4444;
  color: #dc2626;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-input__inner) {
  border-radius: 8px;
}
:deep(.el-input-number__inner) {
  border-radius: 8px;
}
:deep(.el-select .el-input__inner) {
  border-radius: 8px;
}
:deep(.el-date-editor .el-input__inner) {
  border-radius: 8px;
}
:deep(.el-divider__text) {
  color: #475569;
  font-weight: 500;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-pagination.is-background .el-pager li:not(.is-active):hover) {
  color: #3b82f6;
}
:deep(.el-empty__description) {
  color: #64748b;
}
:deep(.el-dialog__header) {
  padding: 18px 24px;
}
:deep(.el-dialog__footer) {
  padding: 12px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}
:deep(.el-descriptions__label) {
  background-color: #f8fafc !important;
  font-weight: 500;
  color: #334155;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--warning) {
  background: #f59e0b;
  border-color: #f59e0b;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
</style>