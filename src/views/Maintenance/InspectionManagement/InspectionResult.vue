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
          <span class="loading-title">Inspection Result</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Quality Assurance & Compliance</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="inspection-result-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          Inspection Result
        </h1>
        <div class="page-subtitle">View and analyze inspection execution results</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
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
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalInspections }}</div>
          <div class="stat-label">Total Inspections</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.passed }}</div>
          <div class="stat-label">Passed</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Close /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.failed }}</div>
          <div class="stat-label">Failed</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.passRate }}<span class="unit">%</span></div>
          <div class="stat-label">Pass Rate</div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by equipment or inspector..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 280px"
        />
        <el-select v-model="statusFilter" placeholder="Result" clearable style="width: 120px">
          <el-option label="Passed" value="passed" />
          <el-option label="Failed" value="failed" />
          <el-option label="Pending" value="pending" />
        </el-select>
        <el-select v-model="equipmentFilter" placeholder="Equipment Type" clearable style="width: 140px">
          <el-option label="UPS" value="UPS" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Generator" value="Generator" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="HVAC" value="HVAC" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Last 30 days: {{ stats.last30Days }} inspections</span>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Inspection Trends</span>
          <el-button text size="small" @click="toggleChartView">
            {{ chartView === 'bar' ? 'Switch to Line' : 'Switch to Bar' }}
          </el-button>
        </div>
        <div class="chart-container" ref="chartContainer"></div>
      </div>
      <div class="stats-card-small">
        <div class="stats-small-header">
          <span>Top Issues Found</span>
          <el-tag size="small" type="danger">{{ topIssues.length }} critical</el-tag>
        </div>
        <div class="issues-list">
          <div v-for="issue in topIssues" :key="issue.name" class="issue-item">
            <div class="issue-name">
              <span class="issue-dot" :class="issue.severity"></span>
              {{ issue.name }}
            </div>
            <div class="issue-count">{{ issue.count }} times</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Results Table -->
    <div class="table-container">
      <el-table
          :data="paginatedResults"
          stripe
          border
          style="width: 100%"
          v-loading="tableLoading"
          @sort-change="handleSortChange"
      >
        <el-table-column prop="inspectionCode" label="Inspection Code" width="140" sortable="custom" />
        <el-table-column prop="planName" label="Plan Name" min-width="180" />
        <el-table-column prop="equipment" label="Equipment" width="140" />
        <el-table-column prop="equipmentType" label="Type" width="100" />
        <el-table-column prop="inspector" label="Inspector" width="120" />
        <el-table-column prop="inspectionDate" label="Date" width="110" sortable="custom" />
        <el-table-column prop="result" label="Result" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getResultTagType(row.result)" size="small">
              {{ getResultText(row.result) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="passRate" label="Pass Rate" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.passRate" :stroke-width="6" :color="getProgressColor(row.passRate)" />
          </template>
        </el-table-column>
        <el-table-column prop="issuesFound" label="Issues" width="80" align="center">
          <template #default="{ row }">
            <span :class="{ 'issue-count': row.issuesFound > 0 }">{{ row.issuesFound }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              View
            </el-button>
            <el-button type="primary" link size="small" @click="generateReport(row)">
              Report
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Inspection Result Details" width="800px" class="detail-dialog">
      <div v-if="selectedResult" class="detail-content">
        <!-- Basic Info -->
        <div class="detail-section">
          <div class="detail-section-title">Basic Information</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Inspection Code">{{ selectedResult.inspectionCode }}</el-descriptions-item>
            <el-descriptions-item label="Plan Name">{{ selectedResult.planName }}</el-descriptions-item>
            <el-descriptions-item label="Equipment">{{ selectedResult.equipment }}</el-descriptions-item>
            <el-descriptions-item label="Equipment Type">{{ selectedResult.equipmentType }}</el-descriptions-item>
            <el-descriptions-item label="Inspector">{{ selectedResult.inspector }}</el-descriptions-item>
            <el-descriptions-item label="Inspection Date">{{ selectedResult.inspectionDate }}</el-descriptions-item>
            <el-descriptions-item label="Result">
              <el-tag :type="getResultTagType(selectedResult.result)" size="small">
                {{ getResultText(selectedResult.result) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Pass Rate">{{ selectedResult.passRate }}%</el-descriptions-item>
            <el-descriptions-item label="Duration">{{ selectedResult.duration }} minutes</el-descriptions-item>
            <el-descriptions-item label="Inspector Notes" :span="2">{{ selectedResult.notes || 'No notes' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Checklist Items -->
        <div class="detail-section">
          <div class="detail-section-title">Checklist Items ({{ selectedResult.checklistItems.length }})</div>
          <div class="checklist-detail">
            <div v-for="(item, idx) in selectedResult.checklistItems" :key="idx" class="checklist-item-detail">
              <div class="item-status">
                <el-icon v-if="item.status === 'pass'" class="status-pass"><CircleCheck /></el-icon>
                <el-icon v-else-if="item.status === 'fail'" class="status-fail"><CircleClose /></el-icon>
                <el-icon v-else class="status-pending"><Clock /></el-icon>
              </div>
              <div class="item-info">
                <div class="item-name">{{ item.name }}</div>
                <div class="item-standard" v-if="item.standardValue">
                  Standard: {{ item.standardValue }} {{ item.unit || '' }}
                </div>
              </div>
              <div class="item-measurement" v-if="item.measuredValue">
                Measured: {{ item.measuredValue }} {{ item.unit || '' }}
              </div>
              <div class="item-remark" v-if="item.remark">
                <span class="remark-label">Note:</span> {{ item.remark }}
              </div>
            </div>
          </div>
        </div>

        <!-- Attachments -->
        <div class="detail-section" v-if="selectedResult.attachments?.length">
          <div class="detail-section-title">Attachments</div>
          <div class="attachments-list">
            <div v-for="(file, idx) in selectedResult.attachments" :key="idx" class="attachment-item">
              <el-icon><Paperclip /></el-icon>
              <span>{{ file.name }}</span>
              <el-button type="primary" link size="small">Download</el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="generateReport(selectedResult)">Generate Report</el-button>
      </template>
    </el-dialog>

    <!-- Report Dialog -->
    <el-dialog v-model="reportDialogVisible" title="Generate Report" width="500px">
      <el-form :model="reportForm" label-width="100px">
        <el-form-item label="Report Format">
          <el-radio-group v-model="reportForm.format">
            <el-radio value="pdf">PDF Document</el-radio>
            <el-radio value="excel">Excel Spreadsheet</el-radio>
            <el-radio value="csv">CSV File</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Include Details">
          <el-checkbox-group v-model="reportForm.include">
            <el-checkbox value="checklist">Checklist Items</el-checkbox>
            <el-checkbox value="measurements">Measurements</el-checkbox>
            <el-checkbox value="attachments">Attachments</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Email To">
          <el-input v-model="reportForm.email" placeholder="Enter email address (optional)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reportDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmGenerateReport">Generate</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Document, Download, Refresh, Search, CircleCheck, Close,
  Warning, Clock, CircleClose, Paperclip
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading inspection results...',
  'Analyzing data...',
  'Almost ready...'
]

// ==================== Types ====================
interface ChecklistItemResult {
  id: number
  name: string
  status: 'pass' | 'fail' | 'pending'
  standardValue?: string
  measuredValue?: string
  unit?: string
  remark?: string
}

interface InspectionResult {
  id: number
  inspectionCode: string
  planId: number
  planName: string
  equipment: string
  equipmentType: string
  inspector: string
  inspectionDate: string
  result: 'passed' | 'failed' | 'pending'
  passRate: number
  issuesFound: number
  duration: number
  notes: string
  checklistItems: ChecklistItemResult[]
  attachments?: { name: string; url: string }[]
  createdAt: string
}

// ==================== Mock Data (30+ Results) ====================
const inspectionResults = ref<InspectionResult[]>([
  { id: 1, inspectionCode: 'INS-20240601-001', planId: 1, planName: 'UPS Monthly Inspection', equipment: 'UPS-01', equipmentType: 'UPS', inspector: 'John Chen', inspectionDate: '2024-06-01', result: 'passed', passRate: 100, issuesFound: 0, duration: 45, notes: 'All parameters within normal range', checklistItems: [
      { id: 1, name: 'Check input voltage and current', status: 'pass', standardValue: '±10%', measuredValue: '+5%', unit: 'V' },
      { id: 2, name: 'Check output voltage and current', status: 'pass', standardValue: '±5%', measuredValue: '+2%', unit: 'V' },
      { id: 3, name: 'Inspect battery terminal connections', status: 'pass', standardValue: 'No corrosion', measuredValue: 'Clean' }
    ], createdAt: '2024-06-01' },
  { id: 2, inspectionCode: 'INS-20240601-002', planId: 2, planName: 'CRAC Unit Weekly', equipment: 'CRAC-01', equipmentType: 'CRAC', inspector: 'Sarah Wong', inspectionDate: '2024-06-01', result: 'passed', passRate: 95, issuesFound: 1, duration: 30, notes: 'Minor filter dirt detected, cleaned', checklistItems: [
      { id: 4, name: 'Check supply air temperature', status: 'pass', standardValue: '18-22', measuredValue: '20.5', unit: '°C' },
      { id: 5, name: 'Check return air temperature', status: 'pass', standardValue: '22-26', measuredValue: '24', unit: '°C' },
      { id: 6, name: 'Inspect and clean air filters', status: 'fail', standardValue: 'Clean', measuredValue: 'Dirty', remark: 'Filter replaced' }
    ], createdAt: '2024-06-01' },
  { id: 3, inspectionCode: 'INS-20240531-003', planId: 3, planName: 'Generator Monthly Test', equipment: 'Generator-01', equipmentType: 'Generator', inspector: 'Mike Lim', inspectionDate: '2024-05-31', result: 'failed', passRate: 70, issuesFound: 2, duration: 60, notes: 'Fuel level low, battery voltage below threshold', checklistItems: [
      { id: 7, name: 'Check fuel level', status: 'fail', standardValue: '≥75', measuredValue: '45', unit: '%', remark: 'Need refill' },
      { id: 8, name: 'Start generator and run', status: 'pass', standardValue: 'Normal', measuredValue: 'Normal' },
      { id: 9, name: 'Check oil pressure', status: 'pass', standardValue: '40-60', measuredValue: '52', unit: 'psi' },
      { id: 10, name: 'Inspect battery voltage', status: 'fail', standardValue: '≥12.5', measuredValue: '11.8', unit: 'V', remark: 'Battery needs replacement' }
    ], createdAt: '2024-05-31' },
  { id: 4, inspectionCode: 'INS-20240530-004', planId: 4, planName: 'Chiller Quarterly', equipment: 'Chiller-01', equipmentType: 'Chiller', inspector: 'Sarah Wong', inspectionDate: '2024-05-30', result: 'passed', passRate: 100, issuesFound: 0, duration: 90, notes: 'All systems operational', checklistItems: [
      { id: 11, name: 'Check evaporator pressure', status: 'pass', standardValue: '60-80', measuredValue: '72', unit: 'psi' },
      { id: 12, name: 'Check condenser pressure', status: 'pass', standardValue: '180-220', measuredValue: '195', unit: 'psi' }
    ], createdAt: '2024-05-30' },
  { id: 5, inspectionCode: 'INS-20240530-005', planId: 5, planName: 'PDU Load Distribution', equipment: 'PDU-A01', equipmentType: 'PDU', inspector: 'John Chen', inspectionDate: '2024-05-30', result: 'passed', passRate: 98, issuesFound: 0, duration: 25, notes: 'Load balanced', checklistItems: [
      { id: 13, name: 'Check total load percentage', status: 'pass', standardValue: '≤80', measuredValue: '65', unit: '%' },
      { id: 14, name: 'Verify phase balance', status: 'pass', standardValue: '±10', measuredValue: '+5', unit: '%' }
    ], createdAt: '2024-05-30' },
  { id: 6, inspectionCode: 'INS-20240529-006', planId: 6, planName: 'HVAC AHU Daily', equipment: 'AHU-01', equipmentType: 'HVAC', inspector: 'Ahmad Razak', inspectionDate: '2024-05-29', result: 'passed', passRate: 92, issuesFound: 1, duration: 20, notes: 'Filter needs replacement soon', checklistItems: [
      { id: 15, name: 'Check supply fan operation', status: 'pass', standardValue: 'Normal', measuredValue: 'Normal' },
      { id: 16, name: 'Inspect filter condition', status: 'fail', standardValue: 'Clean', measuredValue: 'Moderate dirt' }
    ], createdAt: '2024-05-29' },
  { id: 7, inspectionCode: 'INS-20240529-007', planId: 7, planName: 'Transformer Oil Check', equipment: 'Transformer-01', equipmentType: 'Transformer', inspector: 'Mike Lim', inspectionDate: '2024-05-29', result: 'passed', passRate: 100, issuesFound: 0, duration: 55, notes: 'Oil sample sent to lab', checklistItems: [
      { id: 17, name: 'Check oil level', status: 'pass', standardValue: 'Normal', measuredValue: 'Normal' },
      { id: 18, name: 'Record top oil temperature', status: 'pass', standardValue: '≤95', measuredValue: '82', unit: '°C' }
    ], createdAt: '2024-05-29' },
  { id: 8, inspectionCode: 'INS-20240528-008', planId: 8, planName: 'Fire Alarm Weekly', equipment: 'FirePanel-01', equipmentType: 'Fire Alarm', inspector: 'David Tan', inspectionDate: '2024-05-28', result: 'passed', passRate: 100, issuesFound: 0, duration: 35, notes: 'All systems functional', checklistItems: [
      { id: 19, name: 'Check control panel status', status: 'pass', standardValue: 'Normal', measuredValue: 'Normal' },
      { id: 20, name: 'Test smoke detector', status: 'pass', standardValue: 'Trigger alarm', measuredValue: 'Triggered' }
    ], createdAt: '2024-05-28' },
  { id: 9, inspectionCode: 'INS-20240528-009', planId: 9, planName: 'Cooling Tower Monthly', equipment: 'Tower-01', equipmentType: 'Cooling Tower', inspector: 'Sarah Wong', inspectionDate: '2024-05-28', result: 'failed', passRate: 75, issuesFound: 2, duration: 50, notes: 'Algae growth detected', checklistItems: [
      { id: 21, name: 'Check water level', status: 'pass', standardValue: 'Normal', measuredValue: 'Normal' },
      { id: 22, name: 'Check for algae growth', status: 'fail', standardValue: 'None', measuredValue: 'Present', remark: 'Chemical treatment required' }
    ], createdAt: '2024-05-28' },
  { id: 10, inspectionCode: 'INS-20240527-010', planId: 10, planName: 'Network Switch Check', equipment: 'Switch-01', equipmentType: 'Network', inspector: 'Lisa Ng', inspectionDate: '2024-05-27', result: 'passed', passRate: 100, issuesFound: 0, duration: 15, notes: 'All ports operational', checklistItems: [
      { id: 23, name: 'Check switch LED status', status: 'pass', standardValue: 'All green', measuredValue: 'All green' },
      { id: 24, name: 'Check for error logs', status: 'pass', standardValue: 'No errors', measuredValue: 'No errors' }
    ], createdAt: '2024-05-27' },
  { id: 11, inspectionCode: 'INS-20240527-011', planId: 11, planName: 'Water Pump Check', equipment: 'Pump-01', equipmentType: 'Plumbing', inspector: 'David Tan', inspectionDate: '2024-05-27', result: 'passed', passRate: 96, issuesFound: 0, duration: 30, notes: 'Normal operation', checklistItems: [
      { id: 25, name: 'Check pump bearing temperature', status: 'pass', standardValue: '≤75', measuredValue: '68', unit: '°C' },
      { id: 26, name: 'Check for water leaks', status: 'pass', standardValue: 'No leaks', measuredValue: 'No leaks' }
    ], createdAt: '2024-05-27' },
  { id: 12, inspectionCode: 'INS-20240526-012', planId: 12, planName: 'Battery Room Safety', equipment: 'BatteryRoom-01', equipmentType: 'Battery', inspector: 'John Chen', inspectionDate: '2024-05-26', result: 'failed', passRate: 80, issuesFound: 1, duration: 40, notes: 'Ventilation fan not operating', checklistItems: [
      { id: 27, name: 'Check hydrogen detector', status: 'pass', standardValue: 'Normal', measuredValue: 'Normal' },
      { id: 28, name: 'Verify ventilation fan', status: 'fail', standardValue: 'Running', measuredValue: 'Stopped', remark: 'Fan motor failed' }
    ], createdAt: '2024-05-26' },
  { id: 13, inspectionCode: 'INS-20240526-013', planId: 1, planName: 'UPS Monthly Inspection', equipment: 'UPS-02', equipmentType: 'UPS', inspector: 'John Chen', inspectionDate: '2024-05-26', result: 'passed', passRate: 100, issuesFound: 0, duration: 50, notes: 'All good', checklistItems: [], createdAt: '2024-05-26' },
  { id: 14, inspectionCode: 'INS-20240525-014', planId: 2, planName: 'CRAC Unit Weekly', equipment: 'CRAC-02', equipmentType: 'CRAC', inspector: 'Sarah Wong', inspectionDate: '2024-05-25', result: 'passed', passRate: 94, issuesFound: 1, duration: 28, notes: 'Filter cleaned', checklistItems: [], createdAt: '2024-05-25' },
  { id: 15, inspectionCode: 'INS-20240525-015', planId: 3, planName: 'Generator Monthly Test', equipment: 'Generator-02', equipmentType: 'Generator', inspector: 'Mike Lim', inspectionDate: '2024-05-25', result: 'passed', passRate: 90, issuesFound: 1, duration: 55, notes: 'Fuel level low', checklistItems: [], createdAt: '2024-05-25' },
  { id: 16, inspectionCode: 'INS-20240524-016', planId: 6, planName: 'HVAC AHU Daily', equipment: 'AHU-02', equipmentType: 'HVAC', inspector: 'Ahmad Razak', inspectionDate: '2024-05-24', result: 'passed', passRate: 100, issuesFound: 0, duration: 18, notes: 'Normal', checklistItems: [], createdAt: '2024-05-24' },
  { id: 17, inspectionCode: 'INS-20240524-017', planId: 8, planName: 'Fire Alarm Weekly', equipment: 'FirePanel-02', equipmentType: 'Fire Alarm', inspector: 'David Tan', inspectionDate: '2024-05-24', result: 'passed', passRate: 100, issuesFound: 0, duration: 30, notes: 'All good', checklistItems: [], createdAt: '2024-05-24' },
  { id: 18, inspectionCode: 'INS-20240523-018', planId: 10, planName: 'Network Switch Check', equipment: 'Switch-02', equipmentType: 'Network', inspector: 'Lisa Ng', inspectionDate: '2024-05-23', result: 'failed', passRate: 60, issuesFound: 2, duration: 20, notes: 'High CPU usage', checklistItems: [], createdAt: '2024-05-23' },
  { id: 19, inspectionCode: 'INS-20240523-019', planId: 5, planName: 'PDU Load Distribution', equipment: 'PDU-B01', equipmentType: 'PDU', inspector: 'John Chen', inspectionDate: '2024-05-23', result: 'passed', passRate: 100, issuesFound: 0, duration: 22, notes: 'Balanced', checklistItems: [], createdAt: '2024-05-23' },
  { id: 20, inspectionCode: 'INS-20240522-020', planId: 9, planName: 'Cooling Tower Monthly', equipment: 'Tower-02', equipmentType: 'Cooling Tower', inspector: 'Sarah Wong', inspectionDate: '2024-05-22', result: 'passed', passRate: 92, issuesFound: 1, duration: 45, notes: 'Chemical dosing adjusted', checklistItems: [], createdAt: '2024-05-22' },
  { id: 21, inspectionCode: 'INS-20240522-021', planId: 4, planName: 'Chiller Quarterly', equipment: 'Chiller-02', equipmentType: 'Chiller', inspector: 'Sarah Wong', inspectionDate: '2024-05-22', result: 'passed', passRate: 100, issuesFound: 0, duration: 85, notes: 'Efficient operation', checklistItems: [], createdAt: '2024-05-22' },
  { id: 22, inspectionCode: 'INS-20240521-022', planId: 7, planName: 'Transformer Oil Check', equipment: 'Transformer-02', equipmentType: 'Transformer', inspector: 'Mike Lim', inspectionDate: '2024-05-21', result: 'failed', passRate: 70, issuesFound: 2, duration: 60, notes: 'Oil leak detected', checklistItems: [], createdAt: '2024-05-21' },
  { id: 23, inspectionCode: 'INS-20240521-023', planId: 11, planName: 'Water Pump Check', equipment: 'Pump-02', equipmentType: 'Plumbing', inspector: 'David Tan', inspectionDate: '2024-05-21', result: 'passed', passRate: 100, issuesFound: 0, duration: 25, notes: 'Normal', checklistItems: [], createdAt: '2024-05-21' },
  { id: 24, inspectionCode: 'INS-20240520-024', planId: 12, planName: 'Battery Room Safety', equipment: 'BatteryRoom-02', equipmentType: 'Battery', inspector: 'John Chen', inspectionDate: '2024-05-20', result: 'passed', passRate: 100, issuesFound: 0, duration: 35, notes: 'All safety equipment functional', checklistItems: [], createdAt: '2024-05-20' }
])

// ==================== State ====================
const searchText = ref('')
const dateRange = ref<string[]>([])
const statusFilter = ref('')
const equipmentFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const reportDialogVisible = ref(false)
const selectedResult = ref<InspectionResult | null>(null)
const chartView = ref('bar')
const sortField = ref('inspectionDate')
const sortOrder = ref('descending')

const chartContainer = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const reportForm = ref({
  format: 'pdf',
  include: ['checklist', 'measurements'],
  email: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

  const passed = inspectionResults.value.filter(r => r.result === 'passed').length
  const failed = inspectionResults.value.filter(r => r.result === 'failed').length
  const last30Days = inspectionResults.value.filter(r => new Date(r.inspectionDate) >= thirtyDaysAgo).length

  return {
    totalInspections: inspectionResults.value.length,
    passed,
    failed,
    passRate: Math.round((passed / inspectionResults.value.length) * 100),
    last30Days
  }
})

const topIssues = computed(() => {
  const issues: Record<string, { count: number; severity: string }> = {}
  inspectionResults.value.forEach(result => {
    result.checklistItems.forEach(item => {
      if (item.status === 'fail' && item.name) {
        if (!issues[item.name]) {
          issues[item.name] = { count: 0, severity: 'medium' }
        }
        issues[item.name].count++
      }
    })
  })
  return Object.entries(issues)
      .map(([name, data]) => ({ name, count: data.count, severity: data.severity }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5)
})

const filteredResults = computed(() => {
  let filtered = [...inspectionResults.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.planName.toLowerCase().includes(search) ||
        r.equipment.toLowerCase().includes(search) ||
        r.inspector.toLowerCase().includes(search) ||
        r.inspectionCode.toLowerCase().includes(search)
    )
  }

  if (dateRange.value && dateRange.value.length === 2) {
    filtered = filtered.filter(r =>
        r.inspectionDate >= dateRange.value[0] &&
        r.inspectionDate <= dateRange.value[1]
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(r => r.result === statusFilter.value)
  }

  if (equipmentFilter.value) {
    filtered = filtered.filter(r => r.equipmentType === equipmentFilter.value)
  }

  // Sort
  filtered.sort((a, b) => {
    let aVal = a[sortField.value as keyof InspectionResult]
    let bVal = b[sortField.value as keyof InspectionResult]
    if (sortOrder.value === 'ascending') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  return filtered
})

const totalRecords = computed(() => filteredResults.value.length)

const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredResults.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getResultText = (result: string) => {
  const map: Record<string, string> = { passed: 'Passed', failed: 'Failed', pending: 'Pending' }
  return map[result] || result
}

const getResultTagType = (result: string) => {
  const map: Record<string, string> = { passed: 'success', failed: 'danger', pending: 'warning' }
  return map[result] || 'info'
}

const getProgressColor = (rate: number) => {
  if (rate >= 90) return '#67c23a'
  if (rate >= 70) return '#e6a23c'
  return '#f56c6c'
}

const handleSortChange = ({ prop, order }: any) => {
  if (prop) {
    sortField.value = prop
    sortOrder.value = order || 'descending'
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const viewDetail = (result: InspectionResult) => {
  selectedResult.value = result
  detailDialogVisible.value = true
}

const generateReport = (result: InspectionResult | null) => {
  selectedResult.value = result
  reportForm.value = {
    format: 'pdf',
    include: ['checklist', 'measurements'],
    email: ''
  }
  reportDialogVisible.value = true
}

const confirmGenerateReport = () => {
  ElMessage.success(`Report generated in ${reportForm.value.format.toUpperCase()} format`)
  reportDialogVisible.value = false
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Report exported successfully')
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

const toggleChartView = () => {
  chartView.value = chartView.value === 'bar' ? 'line' : 'bar'
  initChart()
}

// ==================== Chart ====================
const initChart = () => {
  if (!chartContainer.value) return

  const monthlyData = getMonthlyData()

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartContainer.value)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Passed', 'Failed'], bottom: 0 },
    grid: { top: 40, left: 50, right: 30, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: monthlyData.months,
      axisLabel: { rotate: 0 }
    },
    yAxis: { type: 'value', name: 'Number of Inspections' },
    series: chartView.value === 'bar' ? [
      { name: 'Passed', type: 'bar', data: monthlyData.passed, itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] } },
      { name: 'Failed', type: 'bar', data: monthlyData.failed, itemStyle: { color: '#f56c6c', borderRadius: [4, 4, 0, 0] } }
    ] : [
      { name: 'Passed', type: 'line', data: monthlyData.passed, smooth: true, lineStyle: { color: '#67c23a', width: 3 }, symbol: 'circle', symbolSize: 8 },
      { name: 'Failed', type: 'line', data: monthlyData.failed, smooth: true, lineStyle: { color: '#f56c6c', width: 3 }, symbol: 'circle', symbolSize: 8 }
    ]
  }

  chartInstance.setOption(option)
  window.addEventListener('resize', () => chartInstance?.resize())
}

const getMonthlyData = () => {
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  const passed = [18, 22, 25, 28, 30, 8]
  const failed = [3, 4, 2, 5, 3, 1]
  return { months, passed, failed }
}

// Watch for filter changes
watch([searchText, dateRange, statusFilter, equipmentFilter], () => {
  currentPage.value = 1
})

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
      nextTick(() => {
        initChart()
      })
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
.inspection-result-page {
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
.stat-icon.red { background: #fee2e2; color: #ef4444; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }

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

/* Chart Section */
.chart-section {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 2;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-container {
  height: 280px;
  width: 100%;
}

.stats-card-small {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stats-small-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.issues-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.issue-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eef2f8;
}

.issue-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #475569;
}

.issue-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.issue-dot.high { background: #ef4444; }
.issue-dot.medium { background: #f59e0b; }
.issue-dot.low { background: #22c55e; }

.issue-count {
  font-size: 13px;
  font-weight: 600;
  color: #ef4444;
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

.issue-count {
  color: #ef4444;
  font-weight: 600;
}

/* Detail Dialog */
.detail-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section-title {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #3b82f6;
}

.checklist-detail {
  border: 1px solid #eef2f8;
  border-radius: 12px;
  overflow: hidden;
}

.checklist-item-detail {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #eef2f8;
  background: #fafcff;
}

.checklist-item-detail:last-child {
  border-bottom: none;
}

.item-status {
  flex-shrink: 0;
}

.status-pass { color: #22c55e; font-size: 20px; }
.status-fail { color: #ef4444; font-size: 20px; }
.status-pending { color: #f59e0b; font-size: 20px; }

.item-info {
  flex: 2;
}

.item-name {
  font-weight: 500;
  font-size: 13px;
  color: #1e293b;
}

.item-standard {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.item-measurement {
  flex: 1;
  font-size: 13px;
  color: #3b82f6;
}

.item-remark {
  flex: 1;
  font-size: 12px;
  color: #f59e0b;
}

.remark-label {
  font-weight: 500;
  color: #64748b;
}

.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 10px;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .chart-section {
    flex-direction: column;
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
  .filter-left .el-select,
  .filter-left .el-date-editor {
    width: 100% !important;
  }
}
</style>