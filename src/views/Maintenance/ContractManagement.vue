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
          <span class="loading-title">Contract Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Contract Lifecycle Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="contract-management-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          Contract Management
        </h1>
        <div class="page-subtitle">Manage service contracts, track renewals, and monitor compliance</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> Create Contract
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
          <div class="stat-value">{{ stats.totalContracts }}</div>
          <div class="stat-label">Total Contracts</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.activeContracts }}</div>
          <div class="stat-label">Active Contracts</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.expiringSoon }}</div>
          <div class="stat-label">Expiring Soon (30d)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ formatNumber(stats.totalValue) }}</div>
          <div class="stat-label">Total Contract Value</div>
        </div>
      </div>
    </div>

    <!-- Tab View -->
    <div class="main-tabs">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="All Contracts" name="all">
          <template #label>
            <span><el-icon><List /></el-icon> All Contracts</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Active" name="active">
          <template #label>
            <span><el-icon><CircleCheck /></el-icon> Active</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Expiring Soon" name="expiring">
          <template #label>
            <span><el-icon><Warning /></el-icon> Expiring Soon</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Expired" name="expired">
          <template #label>
            <span><el-icon><CircleClose /></el-icon> Expired</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by contract or vendor..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="typeFilter" placeholder="Contract Type" clearable style="width: 140px">
          <el-option label="Maintenance" value="Maintenance" />
          <el-option label="Service" value="Service" />
          <el-option label="Supply" value="Supply" />
          <el-option label="Lease" value="Lease" />
        </el-select>
        <el-select v-model="vendorFilter" placeholder="Vendor" clearable filterable style="width: 160px">
          <el-option v-for="v in uniqueVendors" :key="v" :label="v" :value="v" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button size="small" @click="checkExpiringContracts">
          <el-icon><Bell /></el-icon> Check Expiring
        </el-button>
      </div>
    </div>

    <!-- Contracts Table -->
    <div class="table-container">
      <el-table
          :data="paginatedContracts"
          stripe
          border
          style="width: 100%"
          v-loading="tableLoading"
          @row-click="viewContract"
      >
        <el-table-column prop="code" label="Contract Code" width="130" sortable />
        <el-table-column prop="name" label="Contract Name" min-width="200" sortable />
        <el-table-column prop="vendor" label="Vendor" width="180" sortable />
        <el-table-column prop="type" label="Type" width="110">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="startDate" label="Start Date" width="110" sortable />
        <el-table-column prop="endDate" label="End Date" width="110" sortable>
          <template #default="{ row }">
            <span :class="getDateClass(row.endDate)">
              {{ row.endDate }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="Contract Value" width="140" sortable>
          <template #default="{ row }">${{ formatNumber(row.value) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="viewContract(row)">View</el-button>
            <el-button type="primary" link size="small" @click.stop="editContract(row)">Edit</el-button>
            <el-button type="danger" link size="small" @click.stop="deleteContract(row)">Delete</el-button>
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

    <!-- Add/Edit Contract Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="750px" class="contract-dialog">
      <el-form :model="contractForm" :rules="formRules" ref="formRef" label-width="130px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Contract Code" prop="code">
              <el-input v-model="contractForm.code" placeholder="Auto-generated" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Contract Name" prop="name">
              <el-input v-model="contractForm.name" placeholder="Enter contract name" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Vendor" prop="vendor">
              <el-select v-model="contractForm.vendor" placeholder="Select vendor" filterable style="width: 100%">
                <el-option v-for="v in vendorOptions" :key="v" :label="v" :value="v" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Contract Type" prop="type">
              <el-select v-model="contractForm.type" placeholder="Select type" style="width: 100%">
                <el-option label="Maintenance" value="Maintenance" />
                <el-option label="Service" value="Service" />
                <el-option label="Supply" value="Supply" />
                <el-option label="Lease" value="Lease" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Start Date" prop="startDate">
              <el-date-picker
                  v-model="contractForm.startDate"
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
                  v-model="contractForm.endDate"
                  type="date"
                  placeholder="Select end date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Contract Value ($)" prop="value">
              <el-input-number v-model="contractForm.value" :min="0" :step="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Payment Terms" prop="paymentTerms">
              <el-select v-model="contractForm.paymentTerms" placeholder="Select terms" style="width: 100%">
                <el-option label="Net 30" value="Net 30" />
                <el-option label="Net 45" value="Net 45" />
                <el-option label="Net 60" value="Net 60" />
                <el-option label="COD" value="COD" />
                <el-option label="Prepaid" value="Prepaid" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="contractForm.status" placeholder="Select status" style="width: 100%">
                <el-option label="Active" value="active" />
                <el-option label="Expired" value="expired" />
                <el-option label="Terminated" value="terminated" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Auto Renew" prop="autoRenew">
              <el-switch v-model="contractForm.autoRenew" active-text="Yes" inactive-text="No" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Scope of Work" prop="scope">
          <el-input v-model="contractForm.scope" type="textarea" :rows="2" placeholder="Describe the scope of work..." />
        </el-form-item>

        <el-form-item label="Terms & Conditions" prop="terms">
          <el-input v-model="contractForm.terms" type="textarea" :rows="2" placeholder="Key terms and conditions..." />
        </el-form-item>

        <el-form-item label="Notes" prop="notes">
          <el-input v-model="contractForm.notes" type="textarea" :rows="2" placeholder="Additional notes..." />
        </el-form-item>

        <!-- Attachments -->
        <div class="attachment-section">
          <div class="section-label">Attachments</div>
          <div class="attachment-list">
            <div v-for="(file, idx) in contractForm.attachments" :key="idx" class="attachment-item">
              <el-icon><Document /></el-icon>
              <span>{{ file.name }}</span>
              <el-button type="danger" link size="small" @click="removeAttachment(idx)">Remove</el-button>
            </div>
            <el-button type="primary" link @click="addAttachment">
              <el-icon><Plus /></el-icon> Add Attachment
            </el-button>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveContract">Save Contract</el-button>
      </template>
    </el-dialog>

    <!-- View Contract Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="selectedContract?.name" width="850px" class="view-dialog">
      <div v-if="selectedContract" class="contract-detail">
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedContract.code }}</div>
            <div class="detail-stat-label">Contract Code</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedContract.vendor }}</div>
            <div class="detail-stat-label">Vendor</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">${{ formatNumber(selectedContract.value) }}</div>
            <div class="detail-stat-label">Contract Value</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value" :class="getDateClass(selectedContract.endDate)">
              {{ getDaysLeft(selectedContract.endDate) }} days
            </div>
            <div class="detail-stat-label">Days Remaining</div>
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Contract Name">{{ selectedContract.name }}</el-descriptions-item>
          <el-descriptions-item label="Contract Type">
            <el-tag :type="getTypeTagType(selectedContract.type)" size="small">{{ selectedContract.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Start Date">{{ selectedContract.startDate }}</el-descriptions-item>
          <el-descriptions-item label="End Date">
            <span :class="getDateClass(selectedContract.endDate)">{{ selectedContract.endDate }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Payment Terms">{{ selectedContract.paymentTerms }}</el-descriptions-item>
          <el-descriptions-item label="Auto Renew">
            <el-tag :type="selectedContract.autoRenew ? 'success' : 'info'" size="small">
              {{ selectedContract.autoRenew ? 'Enabled' : 'Disabled' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedContract.status)" size="small">
              {{ getStatusText(selectedContract.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Last Renewed">{{ selectedContract.lastRenewed || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Scope of Work" :span="2">{{ selectedContract.scope }}</el-descriptions-item>
          <el-descriptions-item label="Terms & Conditions" :span="2">{{ selectedContract.terms }}</el-descriptions-item>
          <el-descriptions-item label="Notes" :span="2">{{ selectedContract.notes || 'No notes' }}</el-descriptions-item>
        </el-descriptions>

        <!-- Attachments -->
        <div class="attachment-section" v-if="selectedContract.attachments?.length">
          <div class="section-title">Attachments</div>
          <div class="attachment-list-view">
            <div v-for="(file, idx) in selectedContract.attachments" :key="idx" class="attachment-view-item">
              <el-icon><Document /></el-icon>
              <span>{{ file.name }}</span>
              <el-button type="primary" link size="small" @click="downloadAttachment(file)">Download</el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editContract(selectedContract)">Edit Contract</el-button>
        <el-button type="warning" @click="renewContract(selectedContract)" v-if="shouldShowRenewButton(selectedContract)">
          Renew Contract
        </el-button>
      </template>
    </el-dialog>

    <!-- Renew Contract Dialog -->
    <el-dialog v-model="renewDialogVisible" title="Renew Contract" width="500px">
      <el-form :model="renewForm" label-width="120px">
        <el-form-item label="Contract Name">
          <el-input :value="renewingContract?.name" disabled />
        </el-form-item>
        <el-form-item label="Current End Date">
          <el-input :value="renewingContract?.endDate" disabled />
        </el-form-item>
        <el-form-item label="New End Date" required>
          <el-date-picker
              v-model="renewForm.newEndDate"
              type="date"
              placeholder="Select new end date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="New Contract Value">
          <el-input-number v-model="renewForm.newValue" :min="0" :step="10000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Renewal Notes">
          <el-input v-model="renewForm.notes" type="textarea" :rows="2" placeholder="Renewal notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renewDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmRenew">Confirm Renewal</el-button>
      </template>
    </el-dialog>

    <!-- Expiring Contracts Dialog -->
    <el-dialog v-model="expiryDialogVisible" title="Contracts Expiring Soon" width="750px">
      <div class="expiring-list">
        <el-table :data="expiringContracts" border stripe>
          <el-table-column prop="code" label="Contract Code" width="130" />
          <el-table-column prop="name" label="Contract Name" min-width="200" />
          <el-table-column prop="vendor" label="Vendor" width="160" />
          <el-table-column prop="endDate" label="End Date" width="120">
            <template #default="{ row }">
              <span class="expiring-date">{{ row.endDate }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="daysLeft" label="Days Left" width="100">
            <template #default="{ row }">
              <el-tag :type="getDaysLeftType(row.daysLeft)" size="small">{{ row.daysLeft }} days</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Action" width="120">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="renewContract(row)">Renew</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="expiringContracts.length === 0" class="no-expiring">
          <el-empty description="No contracts expiring within 30 days" :image-size="80" />
        </div>
      </div>
      <template #footer>
        <el-button @click="expiryDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document, Plus, Download, Refresh, Search, CircleCheck,
  Clock, Warning, CircleClose, Money, List, Bell
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading contract data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading contract data...',
  'Loading vendor information...',
  'Analyzing contract status...',
  'Almost ready...'
]

// ==================== Types ====================
interface Attachment {
  name: string
  url: string
}

interface Contract {
  id: number
  code: string
  name: string
  vendor: string
  type: 'Maintenance' | 'Service' | 'Supply' | 'Lease'
  startDate: string
  endDate: string
  value: number
  paymentTerms: string
  status: 'active' | 'expired' | 'terminated'
  autoRenew: boolean
  lastRenewed: string | null
  scope: string
  terms: string
  notes: string
  attachments: Attachment[]
}

// ==================== Mock Data (20 contracts) ====================
const contracts = ref<Contract[]>([
  { id: 1, code: 'CT-2024-001', name: 'UPS Maintenance Agreement', vendor: 'Schneider Electric', type: 'Maintenance', startDate: '2024-01-01', endDate: '2025-12-31', value: 250000, paymentTerms: 'Net 45', status: 'active', autoRenew: false, lastRenewed: '2024-01-01', scope: 'Comprehensive maintenance for all UPS systems including quarterly inspections and 24/7 emergency support.', terms: 'Standard terms and conditions apply. Service level agreement attached.', notes: 'Includes battery replacement every 3 years.', attachments: [{ name: 'SLA_2024.pdf', url: '# ' }] },
  { id: 2, code: 'CT-2024-002', name: 'CRAC Unit Service Contract', vendor: 'Vertiv Singapore', type: 'Service', startDate: '2023-06-01', endDate: '2025-05-31', value: 180000, paymentTerms: 'Net 30', status: 'active', autoRenew: true, lastRenewed: '2023-06-01', scope: 'Preventive maintenance for all CRAC units including filter replacement and compressor checks.', terms: 'Response time: 4 hours for critical issues.', notes: 'Quarterly maintenance visits included.', attachments: [] },
  { id: 3, code: 'CT-2024-003', name: 'Generator Parts Supply', vendor: 'Caterpillar Singapore', type: 'Supply', startDate: '2023-03-15', endDate: '2025-03-14', value: 350000, paymentTerms: 'Net 60', status: 'active', autoRenew: false, lastRenewed: '2023-03-15', scope: 'Supply of genuine generator parts and consumables.', terms: 'Parts warranty: 12 months.', notes: 'Priority shipping for emergency orders.', attachments: [] },
  { id: 4, code: 'CT-2024-004', name: 'Chiller Maintenance Contract', vendor: 'Trane Singapore', type: 'Maintenance', startDate: '2023-09-01', endDate: '2024-12-31', value: 220000, paymentTerms: 'Net 45', status: 'active', autoRenew: false, lastRenewed: '2023-09-01', scope: 'Comprehensive chiller maintenance including oil analysis and compressor inspections.', terms: 'Annual performance guarantee included.', notes: 'Next renewal due December 2024.', attachments: [] },
  { id: 5, code: 'CT-2024-005', name: 'Electrical Equipment Supply', vendor: 'ABB Singapore', type: 'Supply', startDate: '2024-02-01', endDate: '2026-01-31', value: 300000, paymentTerms: 'Net 30', status: 'active', autoRenew: true, lastRenewed: '2024-02-01', scope: 'Supply of electrical components including transformers and switchgear.', terms: 'Volume discounts apply.', notes: '5% discount for early payment.', attachments: [] },
  { id: 6, code: 'CT-2024-006', name: 'Battery Replacement Program', vendor: 'Battery Supply Co.', type: 'Service', startDate: '2023-01-01', endDate: '2024-12-31', value: 120000, paymentTerms: 'Net 30', status: 'active', autoRenew: false, lastRenewed: '2023-01-01', scope: 'Battery health monitoring and replacement services.', terms: 'Batteries recycled according to environmental standards.', notes: 'Expires December 31, 2024.', attachments: [] },
  { id: 7, code: 'CT-2024-007', name: 'HVAC Spare Parts Supply', vendor: 'HVAC Supplies Inc.', type: 'Supply', startDate: '2023-07-01', endDate: '2025-06-30', value: 95000, paymentTerms: 'Net 30', status: 'active', autoRenew: true, lastRenewed: '2023-07-01', scope: 'Supply of HVAC spare parts including filters, belts, and motors.', terms: 'Minimum order quantity applies.', notes: 'Weekly stock replenishment.', attachments: [] },
  { id: 8, code: 'CT-2024-008', name: 'Electrical Parts Supply', vendor: 'Electrical Parts Ltd.', type: 'Supply', startDate: '2023-11-01', endDate: '2024-10-31', value: 80000, paymentTerms: 'Net 30', status: 'active', autoRenew: false, lastRenewed: '2023-11-01', scope: 'Supply of electrical components and accessories.', terms: '30-day return policy.', notes: 'Expires October 31, 2024.', attachments: [] },
  { id: 9, code: 'CT-2024-009', name: 'UPS Maintenance - Eaton', vendor: 'Eaton Singapore', type: 'Maintenance', startDate: '2024-03-01', endDate: '2026-02-28', value: 280000, paymentTerms: 'Net 45', status: 'active', autoRenew: true, lastRenewed: '2024-03-01', scope: 'UPS maintenance and battery management services.', terms: '24/7 technical support included.', notes: 'Includes annual load bank testing.', attachments: [] },
  { id: 10, code: 'CT-2024-010', name: 'Generator Parts Supply', vendor: 'Generator Parts Co.', type: 'Supply', startDate: '2023-08-01', endDate: '2025-07-31', value: 150000, paymentTerms: 'Net 30', status: 'active', autoRenew: false, lastRenewed: '2023-08-01', scope: 'Genuine generator parts supply.', terms: 'Parts warranty: 6 months.', notes: 'Emergency parts available within 24 hours.', attachments: [] },
  { id: 11, code: 'CT-2024-011', name: 'Cable Supply Agreement', vendor: 'Cable Solutions', type: 'Supply', startDate: '2023-12-01', endDate: '2024-11-30', value: 60000, paymentTerms: 'Net 30', status: 'active', autoRenew: false, lastRenewed: '2023-12-01', scope: 'Supply of power and network cables.', terms: 'Custom lengths available on request.', notes: 'Expires November 30, 2024.', attachments: [] },
  { id: 12, code: 'CT-2024-012', name: 'Building Automation Maintenance', vendor: 'Johnson Controls', type: 'Maintenance', startDate: '2022-10-01', endDate: '2024-09-30', value: 200000, paymentTerms: 'Net 45', status: 'active', autoRenew: false, lastRenewed: '2022-10-01', scope: 'Building automation system maintenance and support.', terms: 'Remote monitoring included.', notes: 'Renewal required before October 2024.', attachments: [] },
  { id: 13, code: 'CT-2024-013', name: 'Electrical Systems Support', vendor: 'Siemens Singapore', type: 'Service', startDate: '2024-04-01', endDate: '2026-03-31', value: 320000, paymentTerms: 'Net 60', status: 'active', autoRenew: true, lastRenewed: '2024-04-01', scope: 'Electrical systems maintenance and support.', terms: 'Annual performance review.', notes: 'New contract effective April 2024.', attachments: [] },
  { id: 14, code: 'CT-2024-014', name: 'Facility Maintenance Services', vendor: 'Maintenance Solutions Pte Ltd', type: 'Maintenance', startDate: '2023-05-01', endDate: '2025-04-30', value: 450000, paymentTerms: 'Net 30', status: 'active', autoRenew: true, lastRenewed: '2023-05-01', scope: 'Comprehensive facility maintenance services.', terms: '24/7 on-call support.', notes: 'Monthly performance reports provided.', attachments: [] },
  { id: 15, code: 'CT-2024-015', name: 'UPS Parts Supply', vendor: 'UPS Parts Direct', type: 'Supply', startDate: '2023-10-01', endDate: '2024-09-30', value: 75000, paymentTerms: 'Net 30', status: 'active', autoRenew: false, lastRenewed: '2023-10-01', scope: 'UPS spare parts and consumables.', terms: 'Express shipping available.', notes: 'Expires September 30, 2024.', attachments: [] },
  { id: 16, code: 'CT-2024-016', name: 'Cooling Tower Maintenance', vendor: 'Cooling Tower Services', type: 'Maintenance', startDate: '2023-04-01', endDate: '2025-03-31', value: 130000, paymentTerms: 'Net 45', status: 'active', autoRenew: false, lastRenewed: '2023-04-01', scope: 'Cooling tower cleaning and maintenance.', terms: 'Water treatment included.', notes: 'Quarterly chemical treatment.', attachments: [] },
  { id: 17, code: 'CT-2024-017', name: 'Transformer Maintenance', vendor: 'Transformer Specialist', type: 'Maintenance', startDate: '2023-02-01', endDate: '2025-01-31', value: 110000, paymentTerms: 'Net 30', status: 'expired', autoRenew: false, lastRenewed: '2023-02-01', scope: 'Transformer oil analysis and maintenance.', terms: 'DGA testing included.', notes: 'Contract expired - renewal pending.', attachments: [] },
  { id: 18, code: 'CT-2024-018', name: 'HVAC Service Agreement', vendor: 'Carrier Singapore', type: 'Service', startDate: '2022-12-01', endDate: '2024-11-30', value: 160000, paymentTerms: 'Net 45', status: 'active', autoRenew: false, lastRenewed: '2022-12-01', scope: 'HVAC system service and maintenance.', terms: 'Seasonal preventive maintenance.', notes: 'Renewal due November 2024.', attachments: [] },
  { id: 19, code: 'CT-2024-019', name: 'Industrial Parts Supply', vendor: 'Industrial Parts Inc.', type: 'Supply', startDate: '2024-01-15', endDate: '2025-01-14', value: 85000, paymentTerms: 'Net 30', status: 'active', autoRenew: true, lastRenewed: '2024-01-15', scope: 'Industrial parts including seals, bearings, and belts.', terms: 'Bulk pricing available.', notes: 'Auto-renewal enabled.', attachments: [] },
  { id: 20, code: 'CT-2024-020', name: 'Generator Service Contract', vendor: 'Generator Solutions', type: 'Service', startDate: '2023-11-15', endDate: '2025-11-14', value: 190000, paymentTerms: 'Net 30', status: 'active', autoRenew: false, lastRenewed: '2023-11-15', scope: 'Generator testing and maintenance services.', terms: 'Monthly load bank testing.', notes: 'Includes 24/7 emergency response.', attachments: [] }
])

// ==================== State ====================
const activeTab = ref('all')
const searchText = ref('')
const typeFilter = ref('')
const vendorFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const renewDialogVisible = ref(false)
const expiryDialogVisible = ref(false)
const dialogTitle = ref('Create Contract')
const selectedContract = ref<Contract | null>(null)
const renewingContract = ref<Contract | null>(null)
const editingContract = ref<Contract | null>(null)
const formRef = ref()

const contractForm = ref({
  id: null as number | null,
  code: '',
  name: '',
  vendor: '',
  type: 'Maintenance' as 'Maintenance' | 'Service' | 'Supply' | 'Lease',
  startDate: '',
  endDate: '',
  value: 0,
  paymentTerms: 'Net 30',
  status: 'active' as 'active' | 'expired' | 'terminated',
  autoRenew: false,
  scope: '',
  terms: '',
  notes: '',
  attachments: [] as Attachment[]
})

const renewForm = ref({
  newEndDate: '',
  newValue: 0,
  notes: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter contract name', trigger: 'blur' }],
  vendor: [{ required: true, message: 'Please select vendor', trigger: 'change' }],
  startDate: [{ required: true, message: 'Please select start date', trigger: 'change' }],
  endDate: [{ required: true, message: 'Please select end date', trigger: 'change' }],
  value: [{ required: true, message: 'Please enter contract value', trigger: 'blur' }]
}

// ==================== Computed ====================
const uniqueVendors = computed(() => {
  return [...new Set(contracts.value.map(c => c.vendor))]
})

const vendorOptions = computed(() => {
  const vendors = [...uniqueVendors.value]
  if (!vendors.includes('New Vendor')) vendors.push('New Vendor')
  return vendors
})

const stats = computed(() => {
  const totalContracts = contracts.value.length
  const activeContracts = contracts.value.filter(c => c.status === 'active').length
  const today = new Date()
  const thirtyDaysFromNow = new Date()
  thirtyDaysFromNow.setDate(today.getDate() + 30)
  const expiringSoon = contracts.value.filter(c => {
    const endDate = new Date(c.endDate)
    return endDate <= thirtyDaysFromNow && endDate >= today && c.status === 'active'
  }).length
  const totalValue = contracts.value.reduce((sum, c) => sum + c.value, 0)

  return { totalContracts, activeContracts, expiringSoon, totalValue }
})

const expiringContracts = computed(() => {
  const today = new Date()
  const thirtyDaysFromNow = new Date()
  thirtyDaysFromNow.setDate(today.getDate() + 30)
  return contracts.value
      .filter(c => {
        const endDate = new Date(c.endDate)
        return endDate <= thirtyDaysFromNow && endDate >= today && c.status === 'active'
      })
      .map(c => ({
        ...c,
        daysLeft: Math.ceil((new Date(c.endDate).getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
      }))
      .sort((a, b) => a.daysLeft - b.daysLeft)
})

const filteredContracts = computed(() => {
  let filtered = [...contracts.value]

  if (activeTab.value === 'active') {
    filtered = filtered.filter(c => c.status === 'active')
  } else if (activeTab.value === 'expiring') {
    const today = new Date()
    const thirtyDaysFromNow = new Date()
    thirtyDaysFromNow.setDate(today.getDate() + 30)
    filtered = filtered.filter(c => {
      const endDate = new Date(c.endDate)
      return endDate <= thirtyDaysFromNow && endDate >= today && c.status === 'active'
    })
  } else if (activeTab.value === 'expired') {
    filtered = filtered.filter(c => c.status === 'expired')
  }

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(search) ||
        c.code.toLowerCase().includes(search) ||
        c.vendor.toLowerCase().includes(search)
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(c => c.type === typeFilter.value)
  }

  if (vendorFilter.value) {
    filtered = filtered.filter(c => c.vendor === vendorFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredContracts.value.length)

const paginatedContracts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredContracts.value.slice(start, end)
})

// ==================== Helper Functions ====================
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const getTypeTagType = (type: string): string => {
  const map: Record<string, string> = {
    Maintenance: 'primary', Service: 'success', Supply: 'warning', Lease: 'info'
  }
  return map[type] || 'info'
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { active: 'success', expired: 'danger', terminated: 'info' }
  return map[status] || 'info'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { active: 'Active', expired: 'Expired', terminated: 'Terminated' }
  return map[status] || status
}

const getDateClass = (date: string): string => {
  const today = new Date()
  const endDate = new Date(date)
  const daysLeft = Math.ceil((endDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  if (daysLeft < 0) return 'date-expired'
  if (daysLeft < 30) return 'date-expiring'
  return 'date-good'
}

const getDaysLeft = (date: string): number => {
  const today = new Date()
  const endDate = new Date(date)
  return Math.ceil((endDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
}

const getDaysLeftType = (days: number): string => {
  if (days < 7) return 'danger'
  if (days < 30) return 'warning'
  return 'success'
}

const shouldShowRenewButton = (contract: Contract | null): boolean => {
  if (!contract) return false
  const daysLeft = getDaysLeft(contract.endDate)
  return daysLeft > 0 && daysLeft <= 60 && contract.status === 'active'
}

const generateContractCode = (): string => {
  const year = new Date().getFullYear()
  const count = contracts.value.length + 1
  return `CT-${year}-${String(count).padStart(3, '0')}`
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

const addAttachment = () => {
  const name = prompt('Enter attachment name:')
  if (name) {
    contractForm.value.attachments.push({ name, url: '# ' })
  }
}

const removeAttachment = (index: number) => {
  contractForm.value.attachments.splice(index, 1)
}

const downloadAttachment = (file: Attachment) => {
  ElMessage.info(`Downloading ${file.name}`)
}

const openAddDialog = () => {
  dialogTitle.value = 'Create Contract'
  editingContract.value = null
  contractForm.value = {
    id: null,
    code: generateContractCode(),
    name: '',
    vendor: '',
    type: 'Maintenance',
    startDate: new Date().toISOString().slice(0, 10),
    endDate: '',
    value: 0,
    paymentTerms: 'Net 30',
    status: 'active',
    autoRenew: false,
    scope: '',
    terms: '',
    notes: '',
    attachments: []
  }
  dialogVisible.value = true
}

const editContract = (contract: Contract | null) => {
  if (!contract) return
  dialogTitle.value = 'Edit Contract'
  editingContract.value = contract
  contractForm.value = {
    id: contract.id,
    code: contract.code,
    name: contract.name,
    vendor: contract.vendor,
    type: contract.type,
    startDate: contract.startDate,
    endDate: contract.endDate,
    value: contract.value,
    paymentTerms: contract.paymentTerms,
    status: contract.status,
    autoRenew: contract.autoRenew,
    scope: contract.scope,
    terms: contract.terms,
    notes: contract.notes,
    attachments: [...contract.attachments]
  }
  dialogVisible.value = true
}

const viewContract = (contract: Contract) => {
  selectedContract.value = contract
  viewDialogVisible.value = true
}

const deleteContract = (contract: Contract) => {
  ElMessageBox.confirm(
      `Delete contract "${contract.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = contracts.value.findIndex(c => c.id === contract.id)
    if (index !== -1) {
      contracts.value.splice(index, 1)
      ElMessage.success('Contract deleted')
    }
  }).catch(() => {})
}

const saveContract = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    if (editingContract.value) {
      const index = contracts.value.findIndex(c => c.id === editingContract.value!.id)
      if (index !== -1) {
        contracts.value[index] = {
          ...contracts.value[index],
          name: contractForm.value.name,
          vendor: contractForm.value.vendor,
          type: contractForm.value.type,
          startDate: contractForm.value.startDate,
          endDate: contractForm.value.endDate,
          value: contractForm.value.value,
          paymentTerms: contractForm.value.paymentTerms,
          status: contractForm.value.status,
          autoRenew: contractForm.value.autoRenew,
          scope: contractForm.value.scope,
          terms: contractForm.value.terms,
          notes: contractForm.value.notes,
          attachments: contractForm.value.attachments
        }
        ElMessage.success('Contract updated')
      }
    } else {
      const newId = Math.max(...contracts.value.map(c => c.id), 0) + 1
      contracts.value.push({
        id: newId,
        code: contractForm.value.code,
        name: contractForm.value.name,
        vendor: contractForm.value.vendor,
        type: contractForm.value.type,
        startDate: contractForm.value.startDate,
        endDate: contractForm.value.endDate,
        value: contractForm.value.value,
        paymentTerms: contractForm.value.paymentTerms,
        status: contractForm.value.status,
        autoRenew: contractForm.value.autoRenew,
        lastRenewed: new Date().toISOString().slice(0, 10),
        scope: contractForm.value.scope,
        terms: contractForm.value.terms,
        notes: contractForm.value.notes,
        attachments: contractForm.value.attachments
      })
      ElMessage.success('Contract created')
    }

    dialogVisible.value = false
  })
}

const renewContract = (contract: Contract | null) => {
  if (!contract) return
  renewingContract.value = contract
  renewForm.value = {
    newEndDate: '',
    newValue: contract.value,
    notes: ''
  }
  renewDialogVisible.value = true
}

const confirmRenew = () => {
  if (!renewingContract.value) return
  if (!renewForm.value.newEndDate) {
    ElMessage.warning('Please select new end date')
    return
  }

  const index = contracts.value.findIndex(c => c.id === renewingContract.value!.id)
  if (index !== -1) {
    contracts.value[index] = {
      ...contracts.value[index],
      endDate: renewForm.value.newEndDate,
      value: renewForm.value.newValue,
      lastRenewed: new Date().toISOString().slice(0, 10),
      status: 'active',
      notes: contracts.value[index].notes + (renewForm.value.notes ? `\nRenewal notes: ${renewForm.value.notes}` : '')
    }
    ElMessage.success(`Contract renewed until ${renewForm.value.newEndDate}`)
  }
  renewDialogVisible.value = false
  expiryDialogVisible.value = false
  viewDialogVisible.value = false
}

const checkExpiringContracts = () => {
  if (expiringContracts.value.length === 0) {
    ElMessage.success('No contracts expiring within 30 days')
  } else {
    expiryDialogVisible.value = true
  }
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Contract data exported')
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
.contract-management-page {
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
  display: flex;
  gap: 12px;
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

/* Date Status */
.date-good { color: #22c55e; }
.date-expiring { color: #f59e0b; font-weight: 600; }
.date-expired { color: #ef4444; font-weight: 600; }

.expiring-date {
  color: #f59e0b;
  font-weight: 600;
}

/* Dialog */
.contract-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.view-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.contract-detail {
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
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.attachment-section {
  margin-top: 20px;
}

.section-label, .section-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 12px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.attachment-list, .attachment-list-view {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.attachment-item, .attachment-view-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-bottom: 1px solid #eef2f8;
}

.attachment-item:last-child, .attachment-view-item:last-child {
  border-bottom: none;
}

.expiring-list {
  max-height: 400px;
  overflow-y: auto;
}

.no-expiring {
  padding: 20px;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
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
</style>