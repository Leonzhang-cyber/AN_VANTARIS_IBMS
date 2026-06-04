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
          <span class="loading-title">Asset Register</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Asset Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="asset-register-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><OfficeBuilding /></el-icon>
          Asset Register
        </h1>
        <div class="page-subtitle">Manage and track all facility assets</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> Register Asset
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
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalAssets }}</div>
          <div class="stat-label">Total Assets</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.activeAssets }}</div>
          <div class="stat-label">Active</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.maintenanceDue }}</div>
          <div class="stat-label">Maintenance Due</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgAssetAge }}</div>
          <div class="stat-label">Avg Asset Age (years)</div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by name, code or location..."
            style="width: 260px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option label="UPS" value="UPS" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Generator" value="Generator" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="Transformer" value="Transformer" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="Cooling Tower" value="Cooling Tower" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
          <el-option label="Under Maintenance" value="maintenance" />
          <el-option label="Retired" value="retired" />
        </el-select>
        <el-select v-model="locationFilter" placeholder="Location" clearable style="width: 150px">
          <el-option label="Server Room A" value="Server Room A" />
          <el-option label="Server Room B" value="Server Room B" />
          <el-option label="Server Room C" value="Server Room C" />
          <el-option label="Data Center" value="Data Center" />
          <el-option label="Generator Room" value="Generator Room" />
          <el-option label="Chiller Plant" value="Chiller Plant" />
          <el-option label="Electrical Room" value="Electrical Room" />
          <el-option label="Mechanical Room" value="Mechanical Room" />
          <el-option label="Roof" value="Roof" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Total Value: ${{ formatNumber(totalAssetValue) }}</span>
      </div>
    </div>

    <!-- Assets Table -->
    <div class="table-container">
      <el-table
          :data="paginatedAssets"
          stripe
          border
          style="width: 100%"
          v-loading="tableLoading"
          @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="code" label="Asset Code" width="120" sortable />
        <el-table-column prop="name" label="Asset Name" min-width="160" sortable />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="manufacturer" label="Manufacturer" width="130" />
        <el-table-column prop="model" label="Model" width="120" />
        <el-table-column prop="location" label="Location" width="140" />
        <el-table-column prop="installationDate" label="Install Date" width="110" sortable />
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewAsset(row)">View</el-button>
            <el-button type="primary" link size="small" @click="editAsset(row)">Edit</el-button>
            <el-button type="danger" link size="small" @click="deleteAsset(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

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

    <!-- Add/Edit Asset Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" class="asset-dialog">
      <el-form :model="assetForm" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Asset Name" prop="name">
              <el-input v-model="assetForm.name" placeholder="Enter asset name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Asset Code" prop="code">
              <el-input v-model="assetForm.code" placeholder="Auto-generated" disabled />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Category" prop="category">
              <el-select v-model="assetForm.category" placeholder="Select category" style="width: 100%">
                <el-option label="UPS" value="UPS" />
                <el-option label="CRAC" value="CRAC" />
                <el-option label="PDU" value="PDU" />
                <el-option label="Generator" value="Generator" />
                <el-option label="Chiller" value="Chiller" />
                <el-option label="Transformer" value="Transformer" />
                <el-option label="HVAC" value="HVAC" />
                <el-option label="Cooling Tower" value="Cooling Tower" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-select v-model="assetForm.status" placeholder="Select status" style="width: 100%">
                <el-option label="Active" value="active" />
                <el-option label="Inactive" value="inactive" />
                <el-option label="Under Maintenance" value="maintenance" />
                <el-option label="Retired" value="retired" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Manufacturer" prop="manufacturer">
              <el-input v-model="assetForm.manufacturer" placeholder="Enter manufacturer" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Model" prop="model">
              <el-input v-model="assetForm.model" placeholder="Enter model number" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Serial Number" prop="serialNumber">
              <el-input v-model="assetForm.serialNumber" placeholder="Enter serial number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Location" prop="location">
              <el-select v-model="assetForm.location" placeholder="Select location" filterable style="width: 100%">
                <el-option label="Server Room A" value="Server Room A" />
                <el-option label="Server Room B" value="Server Room B" />
                <el-option label="Server Room C" value="Server Room C" />
                <el-option label="Data Center" value="Data Center" />
                <el-option label="Generator Room" value="Generator Room" />
                <el-option label="Chiller Plant" value="Chiller Plant" />
                <el-option label="Electrical Room" value="Electrical Room" />
                <el-option label="Mechanical Room" value="Mechanical Room" />
                <el-option label="Roof" value="Roof" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Installation Date" prop="installationDate">
              <el-date-picker
                  v-model="assetForm.installationDate"
                  type="date"
                  placeholder="Select date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Warranty Expiry" prop="warrantyExpiry">
              <el-date-picker
                  v-model="assetForm.warrantyExpiry"
                  type="date"
                  placeholder="Select date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Purchase Cost ($)" prop="purchaseCost">
              <el-input-number v-model="assetForm.purchaseCost" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Current Value ($)" prop="currentValue">
              <el-input-number v-model="assetForm.currentValue" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description" prop="description">
          <el-input v-model="assetForm.description" type="textarea" :rows="2" placeholder="Asset description..." />
        </el-form-item>

        <el-form-item label="Technical Specifications" prop="specifications">
          <el-input v-model="assetForm.specifications" type="textarea" :rows="2" placeholder="Technical specifications..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveAsset">Save Asset</el-button>
      </template>
    </el-dialog>

    <!-- View Asset Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="selectedAsset?.name" width="800px" class="view-dialog">
      <div v-if="selectedAsset" class="asset-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Asset Code">{{ selectedAsset.code }}</el-descriptions-item>
          <el-descriptions-item label="Asset Name">{{ selectedAsset.name }}</el-descriptions-item>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryTagType(selectedAsset.category)" size="small">{{ selectedAsset.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedAsset.status)" size="small">{{ getStatusText(selectedAsset.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedAsset.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedAsset.model }}</el-descriptions-item>
          <el-descriptions-item label="Serial Number">{{ selectedAsset.serialNumber }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedAsset.location }}</el-descriptions-item>
          <el-descriptions-item label="Installation Date">{{ selectedAsset.installationDate }}</el-descriptions-item>
          <el-descriptions-item label="Warranty Expiry">{{ selectedAsset.warrantyExpiry || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Purchase Cost">${{ formatNumber(selectedAsset.purchaseCost) }}</el-descriptions-item>
          <el-descriptions-item label="Current Value">${{ formatNumber(selectedAsset.currentValue) }}</el-descriptions-item>
          <el-descriptions-item label="Depreciation">{{ selectedAsset.depreciation }}%</el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedAsset.lastMaintenance || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedAsset.nextMaintenance || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedAsset.description || 'No description' }}</el-descriptions-item>
          <el-descriptions-item label="Technical Specs" :span="2">{{ selectedAsset.specifications || 'No specifications' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editAsset(selectedAsset)">Edit Asset</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  OfficeBuilding, Plus, Download, Refresh, Search, CircleCheck,
  Warning, Clock, User
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading asset data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading asset data...',
  'Loading categories...',
  'Initializing asset register...',
  'Almost ready...'
]

// ==================== Types ====================
interface Asset {
  id: number
  code: string
  name: string
  category: string
  manufacturer: string
  model: string
  serialNumber: string
  location: string
  status: 'active' | 'inactive' | 'maintenance' | 'retired'
  installationDate: string
  warrantyExpiry: string | null
  purchaseCost: number
  currentValue: number
  depreciation: number
  lastMaintenance: string | null
  nextMaintenance: string | null
  description: string
  specifications: string
  createdAt: string
}

// ==================== Mock Data ====================
const assets = ref<Asset[]>([
  { id: 1, code: 'AST-2024-001', name: 'UPS-01', category: 'UPS', manufacturer: 'Schneider Electric', model: 'Galaxy VX', serialNumber: 'SN-UPS-001', location: 'Server Room A', status: 'active', installationDate: '2022-03-15', warrantyExpiry: '2027-03-14', purchaseCost: 45000, currentValue: 38000, depreciation: 15.6, lastMaintenance: '2024-05-15', nextMaintenance: '2024-08-15', description: '500kVA UPS system for critical loads', specifications: '500kVA, 480V, Lithium-ion batteries', createdAt: '2022-03-15' },
  { id: 2, code: 'AST-2024-002', name: 'CRAC-01', category: 'CRAC', manufacturer: 'Vertiv', model: 'Liebert CRV', serialNumber: 'SN-CRAC-001', location: 'Data Center', status: 'active', installationDate: '2021-11-20', warrantyExpiry: '2026-11-19', purchaseCost: 28000, currentValue: 21000, depreciation: 25, lastMaintenance: '2024-05-20', nextMaintenance: '2024-06-20', description: '60kW precision cooling unit', specifications: '60kW, R410A refrigerant', createdAt: '2021-11-20' },
  { id: 3, code: 'AST-2024-003', name: 'Generator-01', category: 'Generator', manufacturer: 'Caterpillar', model: '3516', serialNumber: 'SN-GEN-001', location: 'Generator Room', status: 'active', installationDate: '2020-08-10', warrantyExpiry: '2025-08-09', purchaseCost: 120000, currentValue: 85000, depreciation: 29.2, lastMaintenance: '2024-05-25', nextMaintenance: '2024-06-25', description: '2MW diesel generator', specifications: '2MW, 480V, 1500L fuel tank', createdAt: '2020-08-10' },
  { id: 4, code: 'AST-2024-004', name: 'PDU-A01', category: 'PDU', manufacturer: 'Raritan', model: 'PX-5000', serialNumber: 'SN-PDU-001', location: 'Server Row A', status: 'active', installationDate: '2023-01-10', warrantyExpiry: '2028-01-09', purchaseCost: 8500, currentValue: 7800, depreciation: 8.2, lastMaintenance: '2024-05-10', nextMaintenance: '2024-08-10', description: '50kVA power distribution unit', specifications: '50kVA, 48 outlets, 3-phase', createdAt: '2023-01-10' },
  { id: 5, code: 'AST-2024-005', name: 'Chiller-01', category: 'Chiller', manufacturer: 'Trane', model: 'CenTraVac', serialNumber: 'SN-CHL-001', location: 'Chiller Plant', status: 'maintenance', installationDate: '2019-06-05', warrantyExpiry: '2024-06-04', purchaseCost: 95000, currentValue: 45000, depreciation: 52.6, lastMaintenance: '2024-05-28', nextMaintenance: '2024-06-28', description: '500 ton centrifugal chiller', specifications: '500 tons, 800kW, R-134a', createdAt: '2019-06-05' },
  { id: 6, code: 'AST-2024-006', name: 'Transformer-01', category: 'Transformer', manufacturer: 'ABB', model: 'RESIBLOC', serialNumber: 'SN-TRF-001', location: 'Electrical Room', status: 'active', installationDate: '2021-04-12', warrantyExpiry: '2026-04-11', purchaseCost: 32000, currentValue: 26000, depreciation: 18.8, lastMaintenance: '2024-04-12', nextMaintenance: '2024-10-12', description: '2.5MVA dry-type transformer', specifications: '2.5MVA, 13.8kV/480V', createdAt: '2021-04-12' },
  { id: 7, code: 'AST-2024-007', name: 'HVAC-AHU-01', category: 'HVAC', manufacturer: 'Carrier', model: '39CQ', serialNumber: 'SN-AHU-001', location: 'Mechanical Room', status: 'active', installationDate: '2020-10-18', warrantyExpiry: '2025-10-17', purchaseCost: 18000, currentValue: 12000, depreciation: 33.3, lastMaintenance: '2024-05-18', nextMaintenance: '2024-07-18', description: 'Air Handling Unit', specifications: '30000 CFM, 50HP motor', createdAt: '2020-10-18' },
  { id: 8, code: 'AST-2024-008', name: 'CoolingTower-01', category: 'Cooling Tower', manufacturer: 'Baltimore', model: 'NC8400', serialNumber: 'SN-CT-001', location: 'Roof', status: 'active', installationDate: '2021-09-22', warrantyExpiry: '2026-09-21', purchaseCost: 25000, currentValue: 18500, depreciation: 26, lastMaintenance: '2024-05-22', nextMaintenance: '2024-07-22', description: 'Cooling tower for chiller system', specifications: '500 tons, 100HP fan', createdAt: '2021-09-22' },
  { id: 9, code: 'AST-2024-009', name: 'UPS-02', category: 'UPS', manufacturer: 'Eaton', model: '9395', serialNumber: 'SN-UPS-002', location: 'Server Room B', status: 'active', installationDate: '2022-12-01', warrantyExpiry: '2027-11-30', purchaseCost: 52000, currentValue: 47000, depreciation: 9.6, lastMaintenance: '2024-05-01', nextMaintenance: '2024-08-01', description: '300kVA UPS system', specifications: '300kVA, 480V, VRLA batteries', createdAt: '2022-12-01' },
  { id: 10, code: 'AST-2024-010', name: 'CRAC-02', category: 'CRAC', manufacturer: 'Stulz', model: 'CyberAir', serialNumber: 'SN-CRAC-002', location: 'Data Center', status: 'maintenance', installationDate: '2022-06-15', warrantyExpiry: '2027-06-14', purchaseCost: 32000, currentValue: 27000, depreciation: 15.6, lastMaintenance: '2024-06-01', nextMaintenance: '2024-07-01', description: '80kW precision cooling', specifications: '80kW, EC fans', createdAt: '2022-06-15' },
  { id: 11, code: 'AST-2024-011', name: 'PDU-B01', category: 'PDU', manufacturer: 'Schneider Electric', model: 'APC AP8858', serialNumber: 'SN-PDU-002', location: 'Server Row B', status: 'active', installationDate: '2023-03-20', warrantyExpiry: '2028-03-19', purchaseCost: 7200, currentValue: 6700, depreciation: 6.9, lastMaintenance: '2024-04-20', nextMaintenance: '2024-07-20', description: '30kVA PDU', specifications: '30kVA, 36 outlets', createdAt: '2023-03-20' },
  { id: 12, code: 'AST-2024-012', name: 'Generator-02', category: 'Generator', manufacturer: 'Cummins', model: 'C2000D5', serialNumber: 'SN-GEN-002', location: 'Generator Room', status: 'inactive', installationDate: '2018-11-10', warrantyExpiry: '2023-11-09', purchaseCost: 95000, currentValue: 25000, depreciation: 73.7, lastMaintenance: '2024-04-10', nextMaintenance: '2024-07-10', description: '1.5MW diesel generator (standby)', specifications: '1.5MW, 480V', createdAt: '2018-11-10' },
  { id: 13, code: 'AST-2024-013', name: 'UPS-03', category: 'UPS', manufacturer: 'Vertiv', model: 'Liebert EXM', serialNumber: 'SN-UPS-003', location: 'Server Room C', status: 'active', installationDate: '2023-08-05', warrantyExpiry: '2028-08-04', purchaseCost: 38000, currentValue: 36000, depreciation: 5.3, lastMaintenance: '2024-05-05', nextMaintenance: '2024-08-05', description: '200kVA UPS system', specifications: '200kVA, 480V', createdAt: '2023-08-05' },
  { id: 14, code: 'AST-2024-014', name: 'Chiller-02', category: 'Chiller', manufacturer: 'York', model: 'YVAA', serialNumber: 'SN-CHL-002', location: 'Chiller Plant', status: 'active', installationDate: '2022-04-18', warrantyExpiry: '2027-04-17', purchaseCost: 88000, currentValue: 73000, depreciation: 17, lastMaintenance: '2024-04-18', nextMaintenance: '2024-07-18', description: '400 ton scroll chiller', specifications: '400 tons, 650kW', createdAt: '2022-04-18' },
  { id: 15, code: 'AST-2024-015', name: 'HVAC-AHU-02', category: 'HVAC', manufacturer: 'Daikin', model: 'MPS', serialNumber: 'SN-AHU-002', location: 'Mechanical Room', status: 'active', installationDate: '2021-12-12', warrantyExpiry: '2026-12-11', purchaseCost: 15000, currentValue: 10500, depreciation: 30, lastMaintenance: '2024-05-12', nextMaintenance: '2024-07-12', description: 'Air Handling Unit', specifications: '25000 CFM, 40HP motor', createdAt: '2021-12-12' },
  { id: 16, code: 'AST-2024-016', name: 'Transformer-02', category: 'Transformer', manufacturer: 'Siemens', model: 'GEAFOL', serialNumber: 'SN-TRF-002', location: 'Electrical Room', status: 'active', installationDate: '2023-01-25', warrantyExpiry: '2028-01-24', purchaseCost: 35000, currentValue: 32000, depreciation: 8.6, lastMaintenance: '2024-03-25', nextMaintenance: '2024-09-25', description: '2MVA cast resin transformer', specifications: '2MVA, 13.8kV/480V', createdAt: '2023-01-25' },
  { id: 17, code: 'AST-2024-017', name: 'PDU-C01', category: 'PDU', manufacturer: 'ServerTech', model: 'Sentry', serialNumber: 'SN-PDU-003', location: 'Server Row C', status: 'active', installationDate: '2023-06-10', warrantyExpiry: '2028-06-09', purchaseCost: 6800, currentValue: 6300, depreciation: 7.4, lastMaintenance: '2024-05-10', nextMaintenance: '2024-08-10', description: '22kVA PDU', specifications: '22kVA, 24 outlets', createdAt: '2023-06-10' },
  { id: 18, code: 'AST-2024-018', name: 'CRAC-03', category: 'CRAC', manufacturer: 'Schneider Electric', model: 'Uniflair', serialNumber: 'SN-CRAC-003', location: 'Data Center', status: 'active', installationDate: '2023-03-01', warrantyExpiry: '2028-02-28', purchaseCost: 30000, currentValue: 27000, depreciation: 10, lastMaintenance: '2024-04-01', nextMaintenance: '2024-07-01', description: '70kW precision cooling', specifications: '70kW, R410A', createdAt: '2023-03-01' },
  { id: 19, code: 'AST-2024-019', name: 'CoolingTower-02', category: 'Cooling Tower', manufacturer: 'EVAPCO', model: 'ATC', serialNumber: 'SN-CT-002', location: 'Roof', status: 'maintenance', installationDate: '2022-07-20', warrantyExpiry: '2027-07-19', purchaseCost: 22000, currentValue: 16500, depreciation: 25, lastMaintenance: '2024-06-01', nextMaintenance: '2024-07-01', description: 'Cooling tower for HVAC', specifications: '400 tons, 75HP fan', createdAt: '2022-07-20' },
  { id: 20, code: 'AST-2024-020', name: 'Generator-03', category: 'Generator', manufacturer: 'Kohler', model: 'KD2000', serialNumber: 'SN-GEN-003', location: 'Generator Room', status: 'active', installationDate: '2023-10-15', warrantyExpiry: '2028-10-14', purchaseCost: 110000, currentValue: 105000, depreciation: 4.5, lastMaintenance: '2024-05-15', nextMaintenance: '2024-08-15', description: '2MW natural gas generator', specifications: '2MW, 480V, natural gas', createdAt: '2023-10-15' }
])

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const locationFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('Register Asset')
const selectedAsset = ref<Asset | null>(null)
const editingAsset = ref<Asset | null>(null)
const formRef = ref()
const selectedRows = ref<Asset[]>([])

const assetForm = ref({
  id: null as number | null,
  code: '',
  name: '',
  category: '',
  manufacturer: '',
  model: '',
  serialNumber: '',
  location: '',
  status: 'active' as 'active' | 'inactive' | 'maintenance' | 'retired',
  installationDate: '',
  warrantyExpiry: '',
  purchaseCost: 0,
  currentValue: 0,
  description: '',
  specifications: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter asset name', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  manufacturer: [{ required: true, message: 'Please enter manufacturer', trigger: 'blur' }],
  location: [{ required: true, message: 'Please select location', trigger: 'change' }],
  installationDate: [{ required: true, message: 'Please select installation date', trigger: 'change' }]
}

// ==================== Computed ====================
const totalAssetValue = computed(() => {
  return assets.value.reduce((sum, asset) => sum + asset.currentValue, 0)
})

const stats = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  const maintenanceDue = assets.value.filter(a => a.nextMaintenance && a.nextMaintenance <= today).length
  const totalAge = assets.value.reduce((sum, a) => {
    const installDate = new Date(a.installationDate)
    const age = (new Date().getTime() - installDate.getTime()) / (1000 * 60 * 60 * 24 * 365)
    return sum + age
  }, 0)

  return {
    totalAssets: assets.value.length,
    activeAssets: assets.value.filter(a => a.status === 'active').length,
    maintenanceDue: maintenanceDue,
    avgAssetAge: (totalAge / assets.value.length).toFixed(1)
  }
})

const filteredAssets = computed(() => {
  let filtered = [...assets.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a =>
        a.name.toLowerCase().includes(search) ||
        a.code.toLowerCase().includes(search) ||
        a.location.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(a => a.category === categoryFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(a => a.status === statusFilter.value)
  }

  if (locationFilter.value) {
    filtered = filtered.filter(a => a.location === locationFilter.value)
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
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getCategoryTagType = (category: string) => {
  const map: Record<string, string> = {
    UPS: 'primary', CRAC: 'success', PDU: 'warning',
    Generator: 'danger', Chiller: 'info', Transformer: 'primary',
    'Cooling Tower': 'warning', HVAC: 'info'
  }
  return map[category] || 'info'
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    active: 'success', inactive: 'info', maintenance: 'warning', retired: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: 'Active', inactive: 'Inactive', maintenance: 'Under Maintenance', retired: 'Retired'
  }
  return map[status] || status
}

const generateAssetCode = () => {
  const year = new Date().getFullYear()
  const count = assets.value.length + 1
  return `AST-${year}-${String(count).padStart(3, '0')}`
}

const handleSelectionChange = (selection: Asset[]) => {
  selectedRows.value = selection
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const openAddDialog = () => {
  dialogTitle.value = 'Register Asset'
  editingAsset.value = null
  assetForm.value = {
    id: null,
    code: generateAssetCode(),
    name: '',
    category: '',
    manufacturer: '',
    model: '',
    serialNumber: '',
    location: '',
    status: 'active',
    installationDate: new Date().toISOString().slice(0, 10),
    warrantyExpiry: '',
    purchaseCost: 0,
    currentValue: 0,
    description: '',
    specifications: ''
  }
  dialogVisible.value = true
}

const editAsset = (asset: Asset | null) => {
  if (!asset) return
  dialogTitle.value = 'Edit Asset'
  editingAsset.value = asset
  assetForm.value = {
    id: asset.id,
    code: asset.code,
    name: asset.name,
    category: asset.category,
    manufacturer: asset.manufacturer,
    model: asset.model,
    serialNumber: asset.serialNumber,
    location: asset.location,
    status: asset.status,
    installationDate: asset.installationDate,
    warrantyExpiry: asset.warrantyExpiry || '',
    purchaseCost: asset.purchaseCost,
    currentValue: asset.currentValue,
    description: asset.description,
    specifications: asset.specifications
  }
  dialogVisible.value = true
}

const viewAsset = (asset: Asset) => {
  selectedAsset.value = asset
  viewDialogVisible.value = true
}

const deleteAsset = (asset: Asset) => {
  ElMessageBox.confirm(
      `Delete asset "${asset.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = assets.value.findIndex(a => a.id === asset.id)
    if (index !== -1) {
      assets.value.splice(index, 1)
      ElMessage.success('Asset deleted')
    }
  }).catch(() => {})
}

const saveAsset = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    const depreciation = ((assetForm.value.purchaseCost - assetForm.value.currentValue) / assetForm.value.purchaseCost) * 100

    if (editingAsset.value) {
      const index = assets.value.findIndex(a => a.id === editingAsset.value!.id)
      if (index !== -1) {
        assets.value[index] = {
          ...assets.value[index],
          name: assetForm.value.name,
          category: assetForm.value.category,
          manufacturer: assetForm.value.manufacturer,
          model: assetForm.value.model,
          serialNumber: assetForm.value.serialNumber,
          location: assetForm.value.location,
          status: assetForm.value.status,
          installationDate: assetForm.value.installationDate,
          warrantyExpiry: assetForm.value.warrantyExpiry || null,
          purchaseCost: assetForm.value.purchaseCost,
          currentValue: assetForm.value.currentValue,
          depreciation: depreciation,
          description: assetForm.value.description,
          specifications: assetForm.value.specifications
        }
        ElMessage.success('Asset updated')
      }
    } else {
      const newId = Math.max(...assets.value.map(a => a.id), 0) + 1
      assets.value.push({
        id: newId,
        code: assetForm.value.code,
        name: assetForm.value.name,
        category: assetForm.value.category,
        manufacturer: assetForm.value.manufacturer,
        model: assetForm.value.model,
        serialNumber: assetForm.value.serialNumber,
        location: assetForm.value.location,
        status: assetForm.value.status,
        installationDate: assetForm.value.installationDate,
        warrantyExpiry: assetForm.value.warrantyExpiry || null,
        purchaseCost: assetForm.value.purchaseCost,
        currentValue: assetForm.value.currentValue,
        depreciation: depreciation,
        lastMaintenance: null,
        nextMaintenance: null,
        description: assetForm.value.description,
        specifications: assetForm.value.specifications,
        createdAt: new Date().toISOString().slice(0, 10)
      })
      ElMessage.success('Asset registered')
    }

    dialogVisible.value = false
  })
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Asset data exported successfully')
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
.asset-register-page {
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

/* Asset Dialog */
.asset-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.view-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
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
}
</style>