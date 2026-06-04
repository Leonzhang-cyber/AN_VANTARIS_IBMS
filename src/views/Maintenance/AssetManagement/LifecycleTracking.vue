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
          <span class="loading-title">Lifecycle Tracking</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Asset Lifecycle Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="lifecycle-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Connection /></el-icon>
          Lifecycle Tracking
        </h1>
        <div class="page-subtitle">Track asset lifecycle stages from acquisition to retirement</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddAsset">
          <el-icon><Plus /></el-icon> Add Asset
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Lifecycle Overview Cards -->
    <div class="lifecycle-stats">
      <div class="stat-card">
        <div class="stat-icon planning">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ lifecycleStats.planning }}</div>
          <div class="stat-label">Planning</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon acquisition">
          <el-icon><ShoppingCart /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ lifecycleStats.acquisition }}</div>
          <div class="stat-label">Acquisition</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon installation">
          <el-icon><Tools /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ lifecycleStats.installation }}</div>
          <div class="stat-label">Installation</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon operation">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ lifecycleStats.operation }}</div>
          <div class="stat-label">Operation</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon maintenance">
          <el-icon><Tools /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ lifecycleStats.maintenance }}</div>
          <div class="stat-label">Maintenance</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon retirement">
          <el-icon><CircleClose /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ lifecycleStats.retirement }}</div>
          <div class="stat-label">Retirement</div>
        </div>
      </div>
    </div>

    <!-- Lifecycle Funnel Chart -->
    <div class="chart-section">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Asset Lifecycle Funnel</span>
        </div>
        <div class="chart-container" ref="funnelChartEl"></div>
      </div>
      <div class="value-summary-card">
        <div class="summary-header">
          <span>Asset Value Summary</span>
          <el-tag type="primary" size="small">Total: ${{ formatNumber(totalAssetValue) }}</el-tag>
        </div>
        <div class="value-stats">
          <div class="value-item">
            <div class="value-label">Initial Investment</div>
            <div class="value-amount">${{ formatNumber(totalInitialValue) }}</div>
          </div>
          <div class="value-item">
            <div class="value-label">Current Value</div>
            <div class="value-amount">${{ formatNumber(totalCurrentValue) }}</div>
          </div>
          <div class="value-item">
            <div class="value-label">Total Depreciation</div>
            <div class="value-amount depreciation">-${{ formatNumber(totalDepreciation) }}</div>
          </div>
          <div class="value-item">
            <div class="value-label">Avg Depreciation Rate</div>
            <div class="value-amount">{{ avgDepreciationRate }}%</div>
          </div>
        </div>
        <div class="depreciation-chart" ref="depreciationChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by asset name..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="stageFilter" placeholder="Lifecycle Stage" clearable style="width: 140px">
          <el-option label="All Stages" value="" />
          <el-option label="Planning" value="planning" />
          <el-option label="Acquisition" value="acquisition" />
          <el-option label="Installation" value="installation" />
          <el-option label="Operation" value="operation" />
          <el-option label="Maintenance" value="maintenance" />
          <el-option label="Retirement" value="retirement" />
        </el-select>
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 130px">
          <el-option label="All Categories" value="" />
          <el-option label="UPS" value="UPS" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Generator" value="Generator" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="Transformer" value="Transformer" />
          <el-option label="HVAC" value="HVAC" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Showing {{ filteredAssets.length }} assets</span>
      </div>
    </div>

    <!-- Assets Timeline Table -->
    <div class="timeline-container">
      <el-table
          :data="paginatedAssets"
          stripe
          border
          style="width: 100%"
          @row-click="viewAssetDetail"
      >
        <el-table-column prop="code" label="Asset Code" width="140" sortable />
        <el-table-column prop="name" label="Asset Name" min-width="160" sortable />
        <el-table-column prop="category" label="Category" width="110">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="stage" label="Lifecycle Stage" width="140">
          <template #default="{ row }">
            <div class="stage-badge" :class="row.stage">
              {{ getStageText(row.stage) }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="acquisitionDate" label="Acquired" width="110" sortable />
        <el-table-column prop="installationDate" label="Installed" width="110" sortable />
        <el-table-column prop="expectedLife" label="Expected Life" width="110">
          <template #default="{ row }">{{ row.expectedLife }} years</template>
        </el-table-column>
        <el-table-column prop="remainingLife" label="Remaining Life" width="110">
          <template #default="{ row }">
            <span :class="getRemainingLifeClass(row.remainingLife)">
              {{ row.remainingLife }} years
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="currentValue" label="Current Value" width="130">
          <template #default="{ row }">${{ formatNumber(row.currentValue) }}</template>
        </el-table-column>
        <el-table-column label="Lifecycle Progress" width="150">
          <template #default="{ row }">
            <el-progress
                :percentage="row.lifecycleProgress"
                :stroke-width="8"
                :color="getProgressColor(row.lifecycleProgress)"
                :show-text="true"
            />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="viewAssetDetail(row)">View</el-button>
            <el-button type="primary" link size="small" @click.stop="updateStage(row)">Update</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAsset?.name" width="900px" class="lifecycle-dialog">
      <div v-if="selectedAsset" class="asset-lifecycle-detail">
        <!-- Timeline -->
        <div class="detail-section">
          <div class="section-title">Lifecycle Timeline</div>
          <div class="timeline-wrapper">
            <div class="timeline-steps">
              <div
                  v-for="(step, idx) in lifecycleSteps"
                  :key="step.key"
                  class="timeline-step"
                  :class="{ active: isStepActive(step.key, selectedAsset.stage), completed: isStepCompleted(step.key, selectedAsset.stage) }"
              >
                <div class="step-icon">
                  <el-icon><component :is="step.icon" /></el-icon>
                </div>
                <div class="step-label">{{ step.label }}</div>
                <div v-if="idx < lifecycleSteps.length - 1" class="step-line"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Asset Info -->
        <div class="detail-section">
          <div class="section-title">Asset Information</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Asset Code">{{ selectedAsset.code }}</el-descriptions-item>
            <el-descriptions-item label="Asset Name">{{ selectedAsset.name }}</el-descriptions-item>
            <el-descriptions-item label="Category">{{ selectedAsset.category }}</el-descriptions-item>
            <el-descriptions-item label="Manufacturer">{{ selectedAsset.manufacturer }}</el-descriptions-item>
            <el-descriptions-item label="Model">{{ selectedAsset.model }}</el-descriptions-item>
            <el-descriptions-item label="Serial Number">{{ selectedAsset.serialNumber }}</el-descriptions-item>
            <el-descriptions-item label="Location">{{ selectedAsset.location }}</el-descriptions-item>
            <el-descriptions-item label="Current Stage">
              <span class="stage-badge" :class="selectedAsset.stage">{{ getStageText(selectedAsset.stage) }}</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Financial Info -->
        <div class="detail-section">
          <div class="section-title">Financial Information</div>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="Purchase Cost">${{ formatNumber(selectedAsset.purchaseCost) }}</el-descriptions-item>
            <el-descriptions-item label="Current Value">${{ formatNumber(selectedAsset.currentValue) }}</el-descriptions-item>
            <el-descriptions-item label="Depreciation">${{ formatNumber(selectedAsset.depreciationAmount) }}</el-descriptions-item>
            <el-descriptions-item label="Depreciation Rate">{{ selectedAsset.depreciationRate }}%</el-descriptions-item>
            <el-descriptions-item label="Salvage Value">${{ formatNumber(selectedAsset.salvageValue || 0) }}</el-descriptions-item>
            <el-descriptions-item label="ROI">{{ selectedAsset.roi || 'N/A' }}%</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Date Timeline -->
        <div class="detail-section">
          <div class="section-title">Key Dates</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Acquisition Date">{{ selectedAsset.acquisitionDate }}</el-descriptions-item>
            <el-descriptions-item label="Installation Date">{{ selectedAsset.installationDate }}</el-descriptions-item>
            <el-descriptions-item label="Warranty Expiry">{{ selectedAsset.warrantyExpiry || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Expected Retirement">{{ selectedAsset.expectedRetirement || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Last Maintenance">{{ selectedAsset.lastMaintenance || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Next Maintenance">{{ selectedAsset.nextMaintenance || 'N/A' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Maintenance History -->
        <div class="detail-section">
          <div class="section-title">Maintenance History</div>
          <el-table :data="selectedAsset.maintenanceHistory" border stripe size="small">
            <el-table-column prop="date" label="Date" width="110" />
            <el-table-column prop="type" label="Type" width="120">
              <template #default="{ row }">
                <el-tag :type="row.type === 'preventive' ? 'success' : (row.type === 'corrective' ? 'warning' : 'danger')" size="small">
                  {{ row.type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="200" />
            <el-table-column prop="cost" label="Cost" width="120">
              <template #default="{ row }">${{ formatNumber(row.cost) }}</template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Depreciation Chart -->
        <div class="detail-section">
          <div class="section-title">Depreciation Forecast</div>
          <div class="depreciation-forecast" ref="assetDepreciationChartEl"></div>
        </div>
      </div>
    </el-dialog>

    <!-- Update Stage Dialog -->
    <el-dialog v-model="stageDialogVisible" title="Update Lifecycle Stage" width="450px">
      <el-form :model="stageForm" label-width="120px">
        <el-form-item label="Asset">
          <el-input :value="stageAsset?.name" disabled />
        </el-form-item>
        <el-form-item label="Current Stage">
          <el-input :value="getStageText(stageAsset?.stage || '')" disabled />
        </el-form-item>
        <el-form-item label="New Stage" required>
          <el-select v-model="stageForm.newStage" placeholder="Select new stage" style="width: 100%">
            <el-option label="Planning" value="planning" />
            <el-option label="Acquisition" value="acquisition" />
            <el-option label="Installation" value="installation" />
            <el-option label="Operation" value="operation" />
            <el-option label="Maintenance" value="maintenance" />
            <el-option label="Retirement" value="retirement" />
          </el-select>
        </el-form-item>
        <el-form-item label="Effective Date">
          <el-date-picker v-model="stageForm.effectiveDate" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="stageForm.notes" type="textarea" :rows="2" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stageDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmStageUpdate">Update</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Connection, Plus, Download, Refresh, Document, ShoppingCart,
  Tools, Cpu, CircleClose, Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading lifecycle data...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading lifecycle data...',
  'Analyzing asset stages...',
  'Calculating depreciation...',
  'Almost ready...'
]

// ==================== Types ====================
interface MaintenanceRecord {
  date: string
  type: 'preventive' | 'corrective' | 'emergency'
  description: string
  cost: number
}

interface LifecycleAsset {
  id: number
  code: string
  name: string
  category: string
  manufacturer: string
  model: string
  serialNumber: string
  location: string
  stage: 'planning' | 'acquisition' | 'installation' | 'operation' | 'maintenance' | 'retirement'
  acquisitionDate: string
  installationDate: string
  warrantyExpiry: string | null
  expectedLife: number
  remainingLife: number
  purchaseCost: number
  currentValue: number
  depreciationAmount: number
  depreciationRate: number
  salvageValue: number | null
  roi: number | null
  expectedRetirement: string | null
  lastMaintenance: string | null
  nextMaintenance: string | null
  lifecycleProgress: number
  maintenanceHistory: MaintenanceRecord[]
}

// ==================== Mock Data (20 assets) ====================
const assets = ref<LifecycleAsset[]>([
  { id: 1, code: 'AST-001', name: 'UPS-01', category: 'UPS', manufacturer: 'Schneider Electric', model: 'Galaxy VX', serialNumber: 'SN-UPS-001', location: 'Server Room A', stage: 'operation', acquisitionDate: '2022-03-15', installationDate: '2022-04-01', warrantyExpiry: '2027-03-14', expectedLife: 10, remainingLife: 7.5, purchaseCost: 45000, currentValue: 38000, depreciationAmount: 7000, depreciationRate: 15.6, salvageValue: 5000, roi: 25.5, expectedRetirement: '2032-03-15', lastMaintenance: '2024-05-15', nextMaintenance: '2024-08-15', lifecycleProgress: 25,
    maintenanceHistory: [
      { date: '2024-05-15', type: 'preventive', description: 'Quarterly UPS maintenance', cost: 850 },
      { date: '2024-02-10', type: 'preventive', description: 'Battery health check', cost: 450 }
    ] },
  { id: 2, code: 'AST-002', name: 'CRAC-01', category: 'CRAC', manufacturer: 'Vertiv', model: 'Liebert CRV', serialNumber: 'SN-CRAC-001', location: 'Data Center', stage: 'maintenance', acquisitionDate: '2021-11-20', installationDate: '2021-12-10', warrantyExpiry: '2026-11-19', expectedLife: 8, remainingLife: 4.2, purchaseCost: 28000, currentValue: 21000, depreciationAmount: 7000, depreciationRate: 25, salvageValue: 3000, roi: 18.5, expectedRetirement: '2029-12-10', lastMaintenance: '2024-05-20', nextMaintenance: '2024-06-20', lifecycleProgress: 52,
    maintenanceHistory: [
      { date: '2024-05-20', type: 'corrective', description: 'Compressor repair', cost: 1200 },
      { date: '2024-03-10', type: 'preventive', description: 'Filter replacement', cost: 320 }
    ] },
  { id: 3, code: 'AST-003', name: 'Generator-01', category: 'Generator', manufacturer: 'Caterpillar', model: '3516', serialNumber: 'SN-GEN-001', location: 'Generator Room', stage: 'operation', acquisitionDate: '2020-08-10', installationDate: '2020-09-01', warrantyExpiry: '2025-08-09', expectedLife: 15, remainingLife: 10.5, purchaseCost: 120000, currentValue: 85000, depreciationAmount: 35000, depreciationRate: 29.2, salvageValue: 15000, roi: 32.5, expectedRetirement: '2035-09-01', lastMaintenance: '2024-05-25', nextMaintenance: '2024-08-25', lifecycleProgress: 30,
    maintenanceHistory: [
      { date: '2024-05-25', type: 'preventive', description: 'Generator load test', cost: 950 },
      { date: '2024-02-20', type: 'preventive', description: 'Oil change and inspection', cost: 650 }
    ] },
  { id: 4, code: 'AST-004', name: 'PDU-A01', category: 'PDU', manufacturer: 'Raritan', model: 'PX-5000', serialNumber: 'SN-PDU-001', location: 'Server Row A', stage: 'operation', acquisitionDate: '2023-01-10', installationDate: '2023-01-25', warrantyExpiry: '2028-01-09', expectedLife: 7, remainingLife: 5.2, purchaseCost: 8500, currentValue: 7800, depreciationAmount: 700, depreciationRate: 8.2, salvageValue: 1000, roi: 15.2, expectedRetirement: '2030-01-25', lastMaintenance: '2024-05-10', nextMaintenance: '2024-08-10', lifecycleProgress: 21,
    maintenanceHistory: [
      { date: '2024-05-10', type: 'preventive', description: 'PDU firmware update', cost: 300 }
    ] },
  { id: 5, code: 'AST-005', name: 'Chiller-01', category: 'Chiller', manufacturer: 'Trane', model: 'CenTraVac', serialNumber: 'SN-CHL-001', location: 'Chiller Plant', stage: 'maintenance', acquisitionDate: '2019-06-05', installationDate: '2019-07-01', warrantyExpiry: '2024-06-04', expectedLife: 12, remainingLife: 6.5, purchaseCost: 95000, currentValue: 45000, depreciationAmount: 50000, depreciationRate: 52.6, salvageValue: 8000, roi: 28.5, expectedRetirement: '2031-07-01', lastMaintenance: '2024-05-28', nextMaintenance: '2024-06-28', lifecycleProgress: 54,
    maintenanceHistory: [
      { date: '2024-05-28', type: 'emergency', description: 'Chiller compressor failure', cost: 3500 },
      { date: '2024-03-15', type: 'preventive', description: 'Condenser cleaning', cost: 800 }
    ] },
  { id: 6, code: 'AST-006', name: 'Transformer-01', category: 'Transformer', manufacturer: 'ABB', model: 'RESIBLOC', serialNumber: 'SN-TRF-001', location: 'Electrical Room', stage: 'operation', acquisitionDate: '2021-04-12', installationDate: '2021-05-01', warrantyExpiry: '2026-04-11', expectedLife: 20, remainingLife: 16.5, purchaseCost: 32000, currentValue: 26000, depreciationAmount: 6000, depreciationRate: 18.8, salvageValue: 4000, roi: 22.5, expectedRetirement: '2041-05-01', lastMaintenance: '2024-04-12', nextMaintenance: '2024-10-12', lifecycleProgress: 15,
    maintenanceHistory: [
      { date: '2024-04-12', type: 'preventive', description: 'Oil sampling and analysis', cost: 400 }
    ] },
  { id: 7, code: 'AST-007', name: 'HVAC-AHU-01', category: 'HVAC', manufacturer: 'Carrier', model: '39CQ', serialNumber: 'SN-AHU-001', location: 'Mechanical Room', stage: 'maintenance', acquisitionDate: '2020-10-18', installationDate: '2020-11-05', warrantyExpiry: '2025-10-17', expectedLife: 10, remainingLife: 5.8, purchaseCost: 18000, currentValue: 12000, depreciationAmount: 6000, depreciationRate: 33.3, salvageValue: 2000, roi: 16.5, expectedRetirement: '2030-11-05', lastMaintenance: '2024-05-18', nextMaintenance: '2024-07-18', lifecycleProgress: 42,
    maintenanceHistory: [
      { date: '2024-05-18', type: 'corrective', description: 'Belt replacement', cost: 280 },
      { date: '2024-03-10', type: 'preventive', description: 'Filter cleaning', cost: 180 }
    ] },
  { id: 8, code: 'AST-008', name: 'CoolingTower-01', category: 'Cooling Tower', manufacturer: 'Baltimore', model: 'NC8400', serialNumber: 'SN-CT-001', location: 'Roof', stage: 'operation', acquisitionDate: '2021-09-22', installationDate: '2021-10-10', warrantyExpiry: '2026-09-21', expectedLife: 15, remainingLife: 11.5, purchaseCost: 25000, currentValue: 18500, depreciationAmount: 6500, depreciationRate: 26, salvageValue: 3000, roi: 20.5, expectedRetirement: '2036-10-10', lastMaintenance: '2024-05-22', nextMaintenance: '2024-07-22', lifecycleProgress: 23,
    maintenanceHistory: [
      { date: '2024-05-22', type: 'preventive', description: 'Cooling tower cleaning', cost: 450 }
    ] },
  { id: 9, code: 'AST-009', name: 'UPS-02', category: 'UPS', manufacturer: 'Eaton', model: '9395', serialNumber: 'SN-UPS-002', location: 'Server Room B', stage: 'planning', acquisitionDate: '2024-06-01', installationDate: '2024-06-15', warrantyExpiry: '2029-05-31', expectedLife: 10, remainingLife: 9.8, purchaseCost: 52000, currentValue: 52000, depreciationAmount: 0, depreciationRate: 0, salvageValue: 6000, roi: null, expectedRetirement: '2034-06-15', lastMaintenance: null, nextMaintenance: '2024-09-15', lifecycleProgress: 5,
    maintenanceHistory: [] },
  { id: 10, code: 'AST-010', name: 'CRAC-02', category: 'CRAC', manufacturer: 'Stulz', model: 'CyberAir', serialNumber: 'SN-CRAC-002', location: 'Data Center', stage: 'acquisition', acquisitionDate: '2024-05-10', installationDate: '2024-05-25', warrantyExpiry: '2029-05-09', expectedLife: 8, remainingLife: 7.9, purchaseCost: 32000, currentValue: 32000, depreciationAmount: 0, depreciationRate: 0, salvageValue: 4000, roi: null, expectedRetirement: '2032-05-25', lastMaintenance: null, nextMaintenance: '2024-08-25', lifecycleProgress: 10,
    maintenanceHistory: [] },
  { id: 11, code: 'AST-011', name: 'PDU-B01', category: 'PDU', manufacturer: 'Schneider Electric', model: 'APC AP8858', serialNumber: 'SN-PDU-002', location: 'Server Row B', stage: 'operation', acquisitionDate: '2023-03-20', installationDate: '2023-04-05', warrantyExpiry: '2028-03-19', expectedLife: 7, remainingLife: 5.5, purchaseCost: 7200, currentValue: 6700, depreciationAmount: 500, depreciationRate: 6.9, salvageValue: 800, roi: 14.2, expectedRetirement: '2030-04-05', lastMaintenance: '2024-04-20', nextMaintenance: '2024-07-20', lifecycleProgress: 18,
    maintenanceHistory: [
      { date: '2024-04-20', type: 'preventive', description: 'PDU load monitoring', cost: 250 }
    ] },
  { id: 12, code: 'AST-012', name: 'Generator-02', category: 'Generator', manufacturer: 'Cummins', model: 'C2000D5', serialNumber: 'SN-GEN-002', location: 'Generator Room', stage: 'retirement', acquisitionDate: '2018-11-10', installationDate: '2018-12-01', warrantyExpiry: '2023-11-09', expectedLife: 12, remainingLife: 0.5, purchaseCost: 95000, currentValue: 25000, depreciationAmount: 70000, depreciationRate: 73.7, salvageValue: 8000, roi: 12.5, expectedRetirement: '2024-12-01', lastMaintenance: '2024-04-10', nextMaintenance: '2024-07-10', lifecycleProgress: 95,
    maintenanceHistory: [
      { date: '2024-04-10', type: 'emergency', description: 'Major engine repair', cost: 5000 },
      { date: '2024-01-15', type: 'preventive', description: 'Generator test', cost: 600 }
    ] },
  { id: 13, code: 'AST-013', name: 'UPS-03', category: 'UPS', manufacturer: 'Vertiv', model: 'Liebert EXM', serialNumber: 'SN-UPS-003', location: 'Server Room C', stage: 'installation', acquisitionDate: '2023-08-05', installationDate: '2023-08-20', warrantyExpiry: '2028-08-04', expectedLife: 10, remainingLife: 8.8, purchaseCost: 38000, currentValue: 36000, depreciationAmount: 2000, depreciationRate: 5.3, salvageValue: 4500, roi: 18.5, expectedRetirement: '2033-08-20', lastMaintenance: '2024-05-05', nextMaintenance: '2024-08-05', lifecycleProgress: 12,
    maintenanceHistory: [
      { date: '2024-05-05', type: 'preventive', description: 'UPS battery check', cost: 380 }
    ] },
  { id: 14, code: 'AST-014', name: 'Chiller-02', category: 'Chiller', manufacturer: 'York', model: 'YVAA', serialNumber: 'SN-CHL-002', location: 'Chiller Plant', stage: 'operation', acquisitionDate: '2022-04-18', installationDate: '2022-05-05', warrantyExpiry: '2027-04-17', expectedLife: 12, remainingLife: 9.5, purchaseCost: 88000, currentValue: 73000, depreciationAmount: 15000, depreciationRate: 17, salvageValue: 10000, roi: 24.5, expectedRetirement: '2034-05-05', lastMaintenance: '2024-04-18', nextMaintenance: '2024-07-18', lifecycleProgress: 22,
    maintenanceHistory: [
      { date: '2024-04-18', type: 'preventive', description: 'Chiller tune-up', cost: 750 }
    ] },
  { id: 15, code: 'AST-015', name: 'HVAC-AHU-02', category: 'HVAC', manufacturer: 'Daikin', model: 'MPS', serialNumber: 'SN-AHU-002', location: 'Mechanical Room', stage: 'maintenance', acquisitionDate: '2021-12-12', installationDate: '2022-01-01', warrantyExpiry: '2026-12-11', expectedLife: 10, remainingLife: 6.2, purchaseCost: 15000, currentValue: 10500, depreciationAmount: 4500, depreciationRate: 30, salvageValue: 1500, roi: 15.2, expectedRetirement: '2032-01-01', lastMaintenance: '2024-05-12', nextMaintenance: '2024-07-12', lifecycleProgress: 38,
    maintenanceHistory: [
      { date: '2024-05-12', type: 'corrective', description: 'Fan motor repair', cost: 420 }
    ] },
  { id: 16, code: 'AST-016', name: 'Transformer-02', category: 'Transformer', manufacturer: 'Siemens', model: 'GEAFOL', serialNumber: 'SN-TRF-002', location: 'Electrical Room', stage: 'planning', acquisitionDate: '2024-07-15', installationDate: '2024-08-01', warrantyExpiry: '2029-07-14', expectedLife: 20, remainingLife: 19.8, purchaseCost: 35000, currentValue: 35000, depreciationAmount: 0, depreciationRate: 0, salvageValue: 5000, roi: null, expectedRetirement: '2044-08-01', lastMaintenance: null, nextMaintenance: '2024-11-01', lifecycleProgress: 3,
    maintenanceHistory: [] },
  { id: 17, code: 'AST-017', name: 'PDU-C01', category: 'PDU', manufacturer: 'ServerTech', model: 'Sentry', serialNumber: 'SN-PDU-003', location: 'Server Row C', stage: 'operation', acquisitionDate: '2023-06-10', installationDate: '2023-06-25', warrantyExpiry: '2028-06-09', expectedLife: 7, remainingLife: 5.8, purchaseCost: 6800, currentValue: 6300, depreciationAmount: 500, depreciationRate: 7.4, salvageValue: 700, roi: 13.8, expectedRetirement: '2030-06-25', lastMaintenance: '2024-05-10', nextMaintenance: '2024-08-10', lifecycleProgress: 17,
    maintenanceHistory: [
      { date: '2024-05-10', type: 'preventive', description: 'PDU inspection', cost: 200 }
    ] },
  { id: 18, code: 'AST-018', name: 'CRAC-03', category: 'CRAC', manufacturer: 'Schneider Electric', model: 'Uniflair', serialNumber: 'SN-CRAC-003', location: 'Data Center', stage: 'acquisition', acquisitionDate: '2024-06-20', installationDate: '2024-07-05', warrantyExpiry: '2029-06-19', expectedLife: 8, remainingLife: 7.9, purchaseCost: 30000, currentValue: 30000, depreciationAmount: 0, depreciationRate: 0, salvageValue: 3500, roi: null, expectedRetirement: '2032-07-05', lastMaintenance: null, nextMaintenance: '2024-10-05', lifecycleProgress: 8,
    maintenanceHistory: [] },
  { id: 19, code: 'AST-019', name: 'CoolingTower-02', category: 'Cooling Tower', manufacturer: 'EVAPCO', model: 'ATC', serialNumber: 'SN-CT-002', location: 'Roof', stage: 'installation', acquisitionDate: '2024-05-20', installationDate: '2024-06-05', warrantyExpiry: '2029-05-19', expectedLife: 15, remainingLife: 14.8, purchaseCost: 22000, currentValue: 22000, depreciationAmount: 0, depreciationRate: 0, salvageValue: 2500, roi: null, expectedRetirement: '2039-06-05', lastMaintenance: null, nextMaintenance: '2024-09-05', lifecycleProgress: 5,
    maintenanceHistory: [] },
  { id: 20, code: 'AST-020', name: 'Generator-03', category: 'Generator', manufacturer: 'Kohler', model: 'KD2000', serialNumber: 'SN-GEN-003', location: 'Generator Room', stage: 'operation', acquisitionDate: '2023-10-15', installationDate: '2023-11-01', warrantyExpiry: '2028-10-14', expectedLife: 15, remainingLife: 13.8, purchaseCost: 110000, currentValue: 105000, depreciationAmount: 5000, depreciationRate: 4.5, salvageValue: 12000, roi: 28.5, expectedRetirement: '2038-11-01', lastMaintenance: '2024-05-15', nextMaintenance: '2024-08-15', lifecycleProgress: 10,
    maintenanceHistory: [
      { date: '2024-05-15', type: 'preventive', description: 'Generator load test', cost: 850 }
    ] }
])

// ==================== State ====================
const searchText = ref('')
const stageFilter = ref('')
const categoryFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const stageDialogVisible = ref(false)
const selectedAsset = ref<LifecycleAsset | null>(null)
const stageAsset = ref<LifecycleAsset | null>(null)

const stageForm = ref({
  newStage: '',
  effectiveDate: '',
  notes: ''
})

// Chart refs
const funnelChartEl = ref<HTMLElement | null>(null)
const depreciationChartEl = ref<HTMLElement | null>(null)
const assetDepreciationChartEl = ref<HTMLElement | null>(null)

let funnelChart: echarts.ECharts | null = null
let depreciationChart: echarts.ECharts | null = null
let assetDepreciationChart: echarts.ECharts | null = null

// ==================== Computed ====================
const lifecycleStats = computed(() => {
  const stats = {
    planning: 0,
    acquisition: 0,
    installation: 0,
    operation: 0,
    maintenance: 0,
    retirement: 0
  }
  assets.value.forEach(asset => {
    stats[asset.stage]++
  })
  return stats
})

const totalAssetValue = computed(() => {
  return assets.value.reduce((sum, a) => sum + a.currentValue, 0)
})

const totalInitialValue = computed(() => {
  return assets.value.reduce((sum, a) => sum + a.purchaseCost, 0)
})

const totalCurrentValue = computed(() => {
  return assets.value.reduce((sum, a) => sum + a.currentValue, 0)
})

const totalDepreciation = computed(() => {
  return totalInitialValue.value - totalCurrentValue.value
})

const avgDepreciationRate = computed(() => {
  const avg = assets.value.reduce((sum, a) => sum + a.depreciationRate, 0) / assets.value.length
  return avg.toFixed(1)
})

const filteredAssets = computed(() => {
  let filtered = [...assets.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a => a.name.toLowerCase().includes(search))
  }

  if (stageFilter.value) {
    filtered = filtered.filter(a => a.stage === stageFilter.value)
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(a => a.category === categoryFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredAssets.value.length)

const paginatedAssets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAssets.value.slice(start, end)
})

const lifecycleSteps = [
  { key: 'planning', label: 'Planning', icon: 'Document' },
  { key: 'acquisition', label: 'Acquisition', icon: 'ShoppingCart' },
  { key: 'installation', label: 'Installation', icon: 'Tools' },
  { key: 'operation', label: 'Operation', icon: 'Cpu' },
  { key: 'maintenance', label: 'Maintenance', icon: 'Tools' },
  { key: 'retirement', label: 'Retirement', icon: 'CircleClose' }
]

// ==================== Helper Functions ====================
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    UPS: 'primary', CRAC: 'success', PDU: 'warning', Generator: 'danger',
    Chiller: 'info', Transformer: 'primary', HVAC: 'info', 'Cooling Tower': 'warning'
  }
  return map[category] || 'info'
}

const getStageText = (stage: string): string => {
  const map: Record<string, string> = {
    planning: 'Planning', acquisition: 'Acquisition', installation: 'Installation',
    operation: 'Operation', maintenance: 'Maintenance', retirement: 'Retirement'
  }
  return map[stage] || stage
}

const getRemainingLifeClass = (life: number): string => {
  if (life > 5) return 'life-good'
  if (life > 2) return 'life-warning'
  return 'life-critical'
}

const getProgressColor = (progress: number): string => {
  if (progress < 30) return '#3b82f6'
  if (progress < 70) return '#f59e0b'
  return '#ef4444'
}

const isStepActive = (stepKey: string, currentStage: string): boolean => {
  const order = ['planning', 'acquisition', 'installation', 'operation', 'maintenance', 'retirement']
  return stepKey === currentStage
}

const isStepCompleted = (stepKey: string, currentStage: string): boolean => {
  const order = ['planning', 'acquisition', 'installation', 'operation', 'maintenance', 'retirement']
  const currentIndex = order.indexOf(currentStage)
  const stepIndex = order.indexOf(stepKey)
  return stepIndex < currentIndex
}

const viewAssetDetail = (asset: LifecycleAsset): void => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
  nextTick(() => {
    if (assetDepreciationChartEl.value) {
      initAssetDepreciationChart(asset)
    }
  })
}

const updateStage = (asset: LifecycleAsset): void => {
  stageAsset.value = asset
  stageForm.value = {
    newStage: '',
    effectiveDate: new Date().toISOString().slice(0, 10),
    notes: ''
  }
  stageDialogVisible.value = true
}

const confirmStageUpdate = (): void => {
  if (!stageAsset.value || !stageForm.value.newStage) {
    ElMessage.warning('Please select a new stage')
    return
  }

  const index = assets.value.findIndex(a => a.id === stageAsset.value!.id)
  if (index !== -1) {
    assets.value[index].stage = stageForm.value.newStage as any
    ElMessage.success(`Stage updated to ${getStageText(stageForm.value.newStage)}`)
  }
  stageDialogVisible.value = false
}

const openAddAsset = (): void => {
  ElMessage.info('Add asset functionality coming soon')
}

const exportReport = (): void => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Lifecycle report exported')
  }, 1000)
}

const refreshData = async (): Promise<void> => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Charts ====================
const initFunnelChart = (): void => {
  if (!funnelChartEl.value) return
  if (funnelChart) funnelChart.dispose()

  const stats = lifecycleStats.value

  funnelChart = echarts.init(funnelChartEl.value)
  funnelChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} assets ({d}%)' },
    series: [{
      type: 'funnel',
      data: [
        { name: 'Planning', value: stats.planning },
        { name: 'Acquisition', value: stats.acquisition },
        { name: 'Installation', value: stats.installation },
        { name: 'Operation', value: stats.operation },
        { name: 'Maintenance', value: stats.maintenance },
        { name: 'Retirement', value: stats.retirement }
      ],
      gap: 2,
      label: { show: true, position: 'inside' },
      itemStyle: { borderColor: '#fff', borderWidth: 1 }
    }]
  })
}

const initDepreciationChart = (): void => {
  if (!depreciationChartEl.value) return
  if (depreciationChart) depreciationChart.dispose()

  depreciationChart = echarts.init(depreciationChartEl.value)
  depreciationChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 20, left: 50, right: 20, bottom: 20 },
    xAxis: { type: 'category', data: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 'Year 6', 'Year 7', 'Year 8', 'Year 9', 'Year 10'] },
    yAxis: { type: 'value', name: 'Value (%)' },
    series: [{
      type: 'line',
      data: [100, 88, 76, 64, 52, 40, 28, 16, 8, 0],
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#3b82f6', width: 3 },
      name: 'Asset Value (%)'
    }]
  })
}

const initAssetDepreciationChart = (asset: LifecycleAsset): void => {
  if (!assetDepreciationChartEl.value) return
  if (assetDepreciationChart) assetDepreciationChart.dispose()

  const years = Array.from({ length: Math.min(asset.expectedLife, 10) }, (_, i) => `Year ${i + 1}`)
  const yearlyValue = Array.from({ length: Math.min(asset.expectedLife, 10) }, (_, i) => {
    const year = i + 1
    return Math.max(asset.purchaseCost * (1 - asset.depreciationRate / 100 * year), asset.salvageValue || 0)
  })

  assetDepreciationChart = echarts.init(assetDepreciationChartEl.value)
  assetDepreciationChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => {
        return `${params[0].axisValue}<br/>Value: $${params[0].value.toLocaleString()}`
      } },
    grid: { top: 20, left: 60, right: 20, bottom: 20 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Value ($)', axisLabel: { formatter: (v: number) => '$' + (v / 1000).toFixed(0) + 'k' } },
    series: [{
      type: 'line',
      data: yearlyValue,
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#3b82f6', width: 3 }
    }]
  })
}

// ==================== Watch for chart updates ====================
watch([lifecycleStats], () => {
  nextTick(() => initFunnelChart())
})

// ==================== Loading Animation ====================
const startLoading = (): void => {
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
        initFunnelChart()
        initDepreciationChart()
      })
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})
</script>

<style scoped>
/* 样式与之前相同，省略重复代码... */
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

.lifecycle-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

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

.lifecycle-stats {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.stat-icon.planning { background: #eef2ff; color: #3b82f6; }
.stat-icon.acquisition { background: #dcfce7; color: #22c55e; }
.stat-icon.installation { background: #fef3c7; color: #f59e0b; }
.stat-icon.operation { background: #e0e7ff; color: #4f46e5; }
.stat-icon.maintenance { background: #fee2e2; color: #ef4444; }
.stat-icon.retirement { background: #f3e8ff; color: #8b5cf6; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.chart-section {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1;
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

.chart-container {
  height: 280px;
  width: 100%;
}

.value-summary-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  color: #1e293b;
}

.value-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.value-item {
  text-align: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.value-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 6px;
}

.value-amount {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.value-amount.depreciation { color: #ef4444; }

.depreciation-chart {
  height: 180px;
  width: 100%;
}

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

.timeline-container {
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

.stage-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.stage-badge.planning { background: #eef2ff; color: #3b82f6; }
.stage-badge.acquisition { background: #dcfce7; color: #22c55e; }
.stage-badge.installation { background: #fef3c7; color: #f59e0b; }
.stage-badge.operation { background: #e0e7ff; color: #4f46e5; }
.stage-badge.maintenance { background: #fee2e2; color: #ef4444; }
.stage-badge.retirement { background: #f3e8ff; color: #8b5cf6; }

.life-good { color: #22c55e; font-weight: 600; }
.life-warning { color: #f59e0b; font-weight: 600; }
.life-critical { color: #ef4444; font-weight: 600; }

.lifecycle-dialog :deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}

.asset-lifecycle-detail {
  padding: 8px;
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

.timeline-wrapper {
  padding: 20px;
  background: #f8fafc;
  border-radius: 16px;
}

.timeline-steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.timeline-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  flex: 1;
}

.step-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: white;
  border: 2px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #94a3b8;
  margin-bottom: 8px;
  position: relative;
  z-index: 2;
}

.timeline-step.completed .step-icon {
  border-color: #22c55e;
  background: #22c55e;
  color: white;
}

.timeline-step.active .step-icon {
  border-color: #3b82f6;
  background: #3b82f6;
  color: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
}

.step-label {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}

.timeline-step.completed .step-label,
.timeline-step.active .step-label {
  color: #1e293b;
  font-weight: 600;
}

.step-line {
  position: absolute;
  top: 24px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #e2e8f0;
  z-index: 1;
}

.timeline-step:last-child .step-line {
  display: none;
}

.timeline-step.completed + .step-line {
  background: #22c55e;
}

.depreciation-forecast {
  height: 250px;
  width: 100%;
}

@media (max-width: 1200px) {
  .lifecycle-stats {
    grid-template-columns: repeat(3, 1fr);
  }
  .chart-section {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .lifecycle-stats {
    grid-template-columns: repeat(2, 1fr);
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
  .timeline-steps {
    flex-direction: column;
    gap: 16px;
  }
  .step-line {
    display: none;
  }
}
</style>