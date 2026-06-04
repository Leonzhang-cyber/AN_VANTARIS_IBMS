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
          <span class="loading-title">Spare Parts Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Inventory Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="spare-parts-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Box /></el-icon>
          Spare Parts Management
        </h1>
        <div class="page-subtitle">Manage inventory, track stock levels, and reorder parts</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> Add Part
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
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalParts }}</div>
          <div class="stat-label">Total Parts</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.inStock }}</div>
          <div class="stat-label">In Stock</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.lowStock }}</div>
          <div class="stat-label">Low Stock</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><ShoppingCart /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ formatNumber(stats.inventoryValue) }}</div>
          <div class="stat-label">Inventory Value</div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by part name or code..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option label="All Categories" value="" />
          <el-option label="Electrical" value="Electrical" />
          <el-option label="Mechanical" value="Mechanical" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="UPS" value="UPS" />
          <el-option label="Battery" value="Battery" />
          <el-option label="Filter" value="Filter" />
          <el-option label="Cable" value="Cable" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="All Status" value="" />
          <el-option label="In Stock" value="in-stock" />
          <el-option label="Low Stock" value="low-stock" />
          <el-option label="Out of Stock" value="out-of-stock" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button size="small" @click="checkLowStock">
          <el-icon><Bell /></el-icon> Check Low Stock
        </el-button>
      </div>
    </div>

    <!-- Parts Table -->
    <div class="table-container">
      <el-table
          :data="paginatedParts"
          stripe
          border
          style="width: 100%"
          v-loading="tableLoading"
          @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="code" label="Part Code" width="130" sortable />
        <el-table-column prop="name" label="Part Name" min-width="180" sortable />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="manufacturer" label="Manufacturer" width="140" />
        <el-table-column prop="model" label="Model/Compatibility" width="140" />
        <el-table-column prop="location" label="Location" width="120" />
        <el-table-column prop="quantity" label="Stock" width="100" sortable>
          <template #default="{ row }">
            <span :class="getStockClass(row.quantity, row.minStock)">
              {{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="minStock" label="Min Stock" width="90" />
        <el-table-column prop="unitPrice" label="Unit Price" width="110">
          <template #default="{ row }">${{ formatNumber(row.unitPrice) }}</template>
        </el-table-column>
        <el-table-column prop="totalValue" label="Total Value" width="120">
          <template #default="{ row }">${{ formatNumber(row.quantity * row.unitPrice) }}</template>
        </el-table-column>
        <el-table-column label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStockStatusType(row.quantity, row.minStock)" size="small">
              {{ getStockStatus(row.quantity, row.minStock) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="viewPart(row)">View</el-button>
            <el-button type="primary" link size="small" @click.stop="editPart(row)">Edit</el-button>
            <el-button type="danger" link size="small" @click.stop="deletePart(row)">Delete</el-button>
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

    <!-- Add/Edit Part Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" class="part-dialog">
      <el-form :model="partForm" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Part Code" prop="code">
              <el-input v-model="partForm.code" placeholder="Auto-generated" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Part Name" prop="name">
              <el-input v-model="partForm.name" placeholder="Enter part name" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Category" prop="category">
              <el-select v-model="partForm.category" placeholder="Select category" style="width: 100%">
                <el-option label="Electrical" value="Electrical" />
                <el-option label="Mechanical" value="Mechanical" />
                <el-option label="HVAC" value="HVAC" />
                <el-option label="UPS" value="UPS" />
                <el-option label="Battery" value="Battery" />
                <el-option label="Filter" value="Filter" />
                <el-option label="Cable" value="Cable" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Manufacturer" prop="manufacturer">
              <el-input v-model="partForm.manufacturer" placeholder="Enter manufacturer" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Model/Compatibility" prop="model">
              <el-input v-model="partForm.model" placeholder="Enter model or compatible equipment" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Location" prop="location">
              <el-select v-model="partForm.location" placeholder="Select storage location" style="width: 100%">
                <el-option label="Main Warehouse" value="Main Warehouse" />
                <el-option label="Data Center Storage" value="Data Center Storage" />
                <el-option label="Server Room A" value="Server Room A" />
                <el-option label="Server Room B" value="Server Room B" />
                <el-option label="Maintenance Room" value="Maintenance Room" />
                <el-option label="Offsite Storage" value="Offsite Storage" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Quantity" prop="quantity">
              <el-input-number v-model="partForm.quantity" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Minimum Stock" prop="minStock">
              <el-input-number v-model="partForm.minStock" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Unit Price ($)" prop="unitPrice">
              <el-input-number v-model="partForm.unitPrice" :min="0" :step="10" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Reorder Quantity" prop="reorderQty">
              <el-input-number v-model="partForm.reorderQty" :min="0" :step="5" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Supplier" prop="supplier">
              <el-input v-model="partForm.supplier" placeholder="Enter supplier name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Lead Time (days)" prop="leadTime">
              <el-input-number v-model="partForm.leadTime" :min="1" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description" prop="description">
          <el-input v-model="partForm.description" type="textarea" :rows="2" placeholder="Part description..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="savePart">Save Part</el-button>
      </template>
    </el-dialog>

    <!-- View Part Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="selectedPart?.name" width="750px" class="view-dialog">
      <div v-if="selectedPart" class="part-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Part Code">{{ selectedPart.code }}</el-descriptions-item>
          <el-descriptions-item label="Part Name">{{ selectedPart.name }}</el-descriptions-item>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryTagType(selectedPart.category)" size="small">{{ selectedPart.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedPart.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model/Compatibility">{{ selectedPart.model }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedPart.location }}</el-descriptions-item>
          <el-descriptions-item label="Current Stock">
            <span :class="getStockClass(selectedPart.quantity, selectedPart.minStock)">
              {{ selectedPart.quantity }} units
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="Minimum Stock">{{ selectedPart.minStock }} units</el-descriptions-item>
          <el-descriptions-item label="Unit Price">${{ formatNumber(selectedPart.unitPrice) }}</el-descriptions-item>
          <el-descriptions-item label="Total Value">${{ formatNumber(selectedPart.quantity * selectedPart.unitPrice) }}</el-descriptions-item>
          <el-descriptions-item label="Reorder Quantity">{{ selectedPart.reorderQty }} units</el-descriptions-item>
          <el-descriptions-item label="Supplier">{{ selectedPart.supplier }}</el-descriptions-item>
          <el-descriptions-item label="Lead Time">{{ selectedPart.leadTime }} days</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStockStatusType(selectedPart.quantity, selectedPart.minStock)" size="small">
              {{ getStockStatus(selectedPart.quantity, selectedPart.minStock) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Last Restocked">{{ selectedPart.lastRestocked || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedPart.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="reorderPart(selectedPart)" v-if="selectedPart?.quantity <= selectedPart?.minStock">
          Reorder Now
        </el-button>
      </template>
    </el-dialog>

    <!-- Low Stock Alert Dialog -->
    <el-dialog v-model="lowStockDialogVisible" title="Low Stock Alert" width="600px">
      <div class="low-stock-list">
        <el-table :data="lowStockParts" border stripe>
          <el-table-column prop="code" label="Part Code" width="130" />
          <el-table-column prop="name" label="Part Name" min-width="180" />
          <el-table-column prop="quantity" label="Current Stock" width="100">
            <template #default="{ row }">
              <span class="low-stock-value">{{ row.quantity }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="minStock" label="Min Stock" width="100" />
          <el-table-column label="Action" width="120">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="reorderPart(row)">Reorder</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="lowStockParts.length === 0" class="no-low-stock">
          <el-empty description="No low stock items" :image-size="80" />
        </div>
      </div>
      <template #footer>
        <el-button @click="lowStockDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="reorderAllLowStock">Reorder All</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Box, Plus, Download, Refresh, Search, CircleCheck,
  Warning, ShoppingCart, Bell
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading inventory data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading inventory data...',
  'Loading part details...',
  'Checking stock levels...',
  'Almost ready...'
]

// ==================== Types ====================
interface SparePart {
  id: number
  code: string
  name: string
  category: string
  manufacturer: string
  model: string
  location: string
  quantity: number
  minStock: number
  unitPrice: number
  reorderQty: number
  supplier: string
  leadTime: number
  lastRestocked: string | null
  description: string
}

// ==================== Mock Data (25 parts) ====================
const spareParts = ref<SparePart[]>([
  { id: 1, code: 'SP-001', name: 'UPS Battery - 12V 7AH', category: 'Battery', manufacturer: 'CSB', model: 'UPS-12V7AH', location: 'Main Warehouse', quantity: 45, minStock: 20, unitPrice: 45, reorderQty: 30, supplier: 'Battery Supply Co.', leadTime: 5, lastRestocked: '2024-05-15', description: 'Replacement battery for UPS systems' },
  { id: 2, code: 'SP-002', name: 'CRAC Air Filter - 24x24', category: 'Filter', manufacturer: 'Camfil', model: 'CRAC-FILTER-24', location: 'Main Warehouse', quantity: 12, minStock: 15, unitPrice: 28, reorderQty: 20, supplier: 'HVAC Supplies Inc.', leadTime: 7, lastRestocked: '2024-05-10', description: 'High-efficiency air filter for CRAC units' },
  { id: 3, code: 'SP-003', name: 'PDU Circuit Breaker - 20A', category: 'Electrical', manufacturer: 'Schneider', model: 'PDU-CB-20', location: 'Data Center Storage', quantity: 8, minStock: 10, unitPrice: 35, reorderQty: 15, supplier: 'Electrical Parts Ltd.', leadTime: 4, lastRestocked: '2024-05-20', description: 'Circuit breaker for PDU units' },
  { id: 4, code: 'SP-004', name: 'Fan Motor - 120mm', category: 'Mechanical', manufacturer: 'Delta', model: 'FAN-120-12V', location: 'Main Warehouse', quantity: 25, minStock: 15, unitPrice: 22, reorderQty: 20, supplier: 'FanTech Solutions', leadTime: 6, lastRestocked: '2024-05-05', description: 'Cooling fan for UPS/PDU equipment' },
  { id: 5, code: 'SP-005', name: 'Generator Oil Filter', category: 'Filter', manufacturer: 'Cummins', model: 'GEN-OIL-FILTER', location: 'Maintenance Room', quantity: 6, minStock: 8, unitPrice: 18, reorderQty: 12, supplier: 'Generator Parts Co.', leadTime: 5, lastRestocked: '2024-05-12', description: 'Oil filter for generator maintenance' },
  { id: 6, code: 'SP-006', name: 'Chiller Belt - B54', category: 'Mechanical', manufacturer: 'Gates', model: 'BELT-B54', location: 'Main Warehouse', quantity: 3, minStock: 5, unitPrice: 15, reorderQty: 10, supplier: 'Industrial Belts Inc.', leadTime: 3, lastRestocked: '2024-05-18', description: 'Drive belt for chiller compressor' },
  { id: 7, code: 'SP-007', name: 'HVAC Thermostat', category: 'HVAC', manufacturer: 'Honeywell', model: 'T-STAT-PRO', location: 'Main Warehouse', quantity: 18, minStock: 10, unitPrice: 65, reorderQty: 12, supplier: 'HVAC Supplies Inc.', leadTime: 7, lastRestocked: '2024-05-08', description: 'Digital thermostat for HVAC control' },
  { id: 8, code: 'SP-008', name: 'Power Cable - C13 to C14', category: 'Cable', manufacturer: 'Tripp Lite', model: 'CABLE-C13-C14', location: 'Server Room A', quantity: 150, minStock: 50, unitPrice: 8, reorderQty: 100, supplier: 'Cable Solutions', leadTime: 3, lastRestocked: '2024-05-25', description: 'Power cable for server/PDU connections' },
  { id: 9, code: 'SP-009', name: 'UPS Control Board', category: 'UPS', manufacturer: 'APC', model: 'UPS-CB-1000', location: 'Data Center Storage', quantity: 2, minStock: 3, unitPrice: 185, reorderQty: 5, supplier: 'UPS Parts Direct', leadTime: 10, lastRestocked: '2024-05-01', description: 'Control board for UPS-1000 series' },
  { id: 10, code: 'SP-010', name: 'Transformer Fuse - 100A', category: 'Electrical', manufacturer: 'Bussmann', model: 'FUSE-100A', location: 'Main Warehouse', quantity: 22, minStock: 15, unitPrice: 12, reorderQty: 20, supplier: 'Electrical Parts Ltd.', leadTime: 4, lastRestocked: '2024-05-22', description: 'High-capacity fuse for transformer protection' },
  { id: 11, code: 'SP-011', name: 'CRAC Compressor', category: 'HVAC', manufacturer: 'Copeland', model: 'COMP-CRAC-01', location: 'Main Warehouse', quantity: 1, minStock: 2, unitPrice: 450, reorderQty: 2, supplier: 'HVAC Supplies Inc.', leadTime: 14, lastRestocked: '2024-04-15', description: 'Replacement compressor for CRAC units' },
  { id: 12, code: 'SP-012', name: 'Generator Spark Plug', category: 'Mechanical', manufacturer: 'NGK', model: 'SPARK-BP5ES', location: 'Maintenance Room', quantity: 14, minStock: 10, unitPrice: 6, reorderQty: 15, supplier: 'Generator Parts Co.', leadTime: 5, lastRestocked: '2024-05-14', description: 'Spark plug for generator engine' },
  { id: 13, code: 'SP-013', name: 'PDU Display Module', category: 'Electrical', manufacturer: 'Raritan', model: 'PDU-DISP-01', location: 'Data Center Storage', quantity: 3, minStock: 3, unitPrice: 95, reorderQty: 4, supplier: 'PDU Parts Co.', leadTime: 8, lastRestocked: '2024-05-09', description: 'LCD display module for PDU' },
  { id: 14, code: 'SP-014', name: 'Chiller Refrigerant - R410A', category: 'HVAC', manufacturer: 'DuPont', model: 'REF-R410A', location: 'Main Warehouse', quantity: 5, minStock: 4, unitPrice: 85, reorderQty: 6, supplier: 'Refrigerant Supply', leadTime: 5, lastRestocked: '2024-05-20', description: 'Refrigerant for chiller systems' },
  { id: 15, code: 'SP-015', name: 'UPS Fan - 80mm', category: 'Mechanical', manufacturer: 'Sunon', model: 'FAN-80-12V', location: 'Main Warehouse', quantity: 30, minStock: 20, unitPrice: 12, reorderQty: 25, supplier: 'FanTech Solutions', leadTime: 6, lastRestocked: '2024-05-18', description: 'Cooling fan for UPS units' },
  { id: 16, code: 'SP-016', name: 'HVAC Contactor', category: 'Electrical', manufacturer: 'Siemens', model: 'CONT-3RT', location: 'Main Warehouse', quantity: 9, minStock: 8, unitPrice: 42, reorderQty: 10, supplier: 'Electrical Parts Ltd.', leadTime: 6, lastRestocked: '2024-05-16', description: 'Magnetic contactor for HVAC control' },
  { id: 17, code: 'SP-017', name: 'Generator Air Filter', category: 'Filter', manufacturer: 'Donaldson', model: 'AIR-FILTER-GEN', location: 'Maintenance Room', quantity: 7, minStock: 6, unitPrice: 25, reorderQty: 8, supplier: 'Generator Parts Co.', leadTime: 7, lastRestocked: '2024-05-11', description: 'Air filter for generator' },
  { id: 18, code: 'SP-018', name: 'Network Cable - Cat6', category: 'Cable', manufacturer: 'Belden', model: 'CAT6-3FT', location: 'Server Room B', quantity: 200, minStock: 100, unitPrice: 4, reorderQty: 150, supplier: 'Cable Solutions', leadTime: 3, lastRestocked: '2024-05-28', description: 'Cat6 Ethernet cable' },
  { id: 19, code: 'SP-019', name: 'PDU Outlet - C13', category: 'Electrical', manufacturer: 'APC', model: 'OUTLET-C13', location: 'Data Center Storage', quantity: 11, minStock: 10, unitPrice: 8, reorderQty: 15, supplier: 'PDU Parts Co.', leadTime: 5, lastRestocked: '2024-05-21', description: 'Replacement outlet for PDU' },
  { id: 20, code: 'SP-020', name: 'UPS Battery - 12V 9AH', category: 'Battery', manufacturer: 'Yuasa', model: 'UPS-12V9AH', location: 'Main Warehouse', quantity: 28, minStock: 20, unitPrice: 55, reorderQty: 25, supplier: 'Battery Supply Co.', leadTime: 5, lastRestocked: '2024-05-19', description: 'High-capacity battery for UPS systems' },
  { id: 21, code: 'SP-021', name: 'CRAC Humidity Sensor', category: 'HVAC', manufacturer: 'Sensirion', model: 'HUM-SENSOR', location: 'Main Warehouse', quantity: 4, minStock: 5, unitPrice: 38, reorderQty: 6, supplier: 'HVAC Supplies Inc.', leadTime: 8, lastRestocked: '2024-05-07', description: 'Humidity sensor for CRAC units' },
  { id: 22, code: 'SP-022', name: 'Generator Starter Motor', category: 'Mechanical', manufacturer: 'Delco', model: 'START-MOTOR', location: 'Maintenance Room', quantity: 1, minStock: 2, unitPrice: 320, reorderQty: 2, supplier: 'Generator Parts Co.', leadTime: 10, lastRestocked: '2024-04-25', description: 'Starter motor for generator' },
  { id: 23, code: 'SP-023', name: 'Chiller Pump Seal', category: 'Mechanical', manufacturer: 'John Crane', model: 'PUMP-SEAL', location: 'Main Warehouse', quantity: 6, minStock: 6, unitPrice: 28, reorderQty: 8, supplier: 'Industrial Parts Inc.', leadTime: 7, lastRestocked: '2024-05-13', description: 'Mechanical seal for chiller pump' },
  { id: 24, code: 'SP-024', name: 'UPS Communication Card', category: 'UPS', manufacturer: 'Eaton', model: 'COMM-CARD', location: 'Data Center Storage', quantity: 2, minStock: 3, unitPrice: 155, reorderQty: 3, supplier: 'UPS Parts Direct', leadTime: 9, lastRestocked: '2024-05-03', description: 'Network communication card for UPS' },
  { id: 25, code: 'SP-025', name: 'HVAC Pressure Switch', category: 'Electrical', manufacturer: 'Johnson Controls', model: 'PRESS-SWITCH', location: 'Main Warehouse', quantity: 8, minStock: 5, unitPrice: 32, reorderQty: 8, supplier: 'HVAC Supplies Inc.', leadTime: 5, lastRestocked: '2024-05-17', description: 'Pressure switch for HVAC systems' }
])

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const lowStockDialogVisible = ref(false)
const dialogTitle = ref('Add Part')
const selectedPart = ref<SparePart | null>(null)
const editingPart = ref<SparePart | null>(null)
const formRef = ref()
const selectedRows = ref<SparePart[]>([])

const partForm = ref({
  id: null as number | null,
  code: '',
  name: '',
  category: '',
  manufacturer: '',
  model: '',
  location: '',
  quantity: 0,
  minStock: 0,
  unitPrice: 0,
  reorderQty: 0,
  supplier: '',
  leadTime: 7,
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter part name', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  manufacturer: [{ required: true, message: 'Please enter manufacturer', trigger: 'blur' }],
  quantity: [{ required: true, message: 'Please enter quantity', trigger: 'blur' }],
  unitPrice: [{ required: true, message: 'Please enter unit price', trigger: 'blur' }]
}

// ==================== Computed ====================
const stats = computed(() => {
  const totalParts = spareParts.value.length
  const inStock = spareParts.value.filter(p => p.quantity > p.minStock).length
  const lowStock = spareParts.value.filter(p => p.quantity <= p.minStock && p.quantity > 0).length
  const outOfStock = spareParts.value.filter(p => p.quantity === 0).length
  const inventoryValue = spareParts.value.reduce((sum, p) => sum + (p.quantity * p.unitPrice), 0)

  return {
    totalParts,
    inStock,
    lowStock,
    outOfStock,
    inventoryValue
  }
})

const filteredParts = computed(() => {
  let filtered = [...spareParts.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(search) ||
        p.code.toLowerCase().includes(search) ||
        p.manufacturer.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(p => p.category === categoryFilter.value)
  }

  if (statusFilter.value) {
    if (statusFilter.value === 'in-stock') {
      filtered = filtered.filter(p => p.quantity > p.minStock)
    } else if (statusFilter.value === 'low-stock') {
      filtered = filtered.filter(p => p.quantity <= p.minStock && p.quantity > 0)
    } else if (statusFilter.value === 'out-of-stock') {
      filtered = filtered.filter(p => p.quantity === 0)
    }
  }

  return filtered
})

const totalRecords = computed(() => filteredParts.value.length)

const paginatedParts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredParts.value.slice(start, end)
})

const lowStockParts = computed(() => {
  return spareParts.value.filter(p => p.quantity <= p.minStock && p.quantity > 0)
})

// ==================== Helper Functions ====================
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    Electrical: 'primary', Mechanical: 'warning', HVAC: 'info',
    UPS: 'danger', Battery: 'success', Filter: 'info', Cable: ''
  }
  return map[category] || 'info'
}

const getStockClass = (quantity: number, minStock: number): string => {
  if (quantity === 0) return 'stock-out'
  if (quantity <= minStock) return 'stock-low'
  return 'stock-good'
}

const getStockStatus = (quantity: number, minStock: number): string => {
  if (quantity === 0) return 'Out of Stock'
  if (quantity <= minStock) return 'Low Stock'
  return 'In Stock'
}

const getStockStatusType = (quantity: number, minStock: number): string => {
  if (quantity === 0) return 'danger'
  if (quantity <= minStock) return 'warning'
  return 'success'
}

const generatePartCode = (): string => {
  const count = spareParts.value.length + 1
  return `SP-${String(count).padStart(3, '0')}`
}

const handleSelectionChange = (selection: SparePart[]) => {
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
  dialogTitle.value = 'Add Part'
  editingPart.value = null
  partForm.value = {
    id: null,
    code: generatePartCode(),
    name: '',
    category: '',
    manufacturer: '',
    model: '',
    location: 'Main Warehouse',
    quantity: 0,
    minStock: 0,
    unitPrice: 0,
    reorderQty: 0,
    supplier: '',
    leadTime: 7,
    description: ''
  }
  dialogVisible.value = true
}

const editPart = (part: SparePart) => {
  dialogTitle.value = 'Edit Part'
  editingPart.value = part
  partForm.value = {
    id: part.id,
    code: part.code,
    name: part.name,
    category: part.category,
    manufacturer: part.manufacturer,
    model: part.model,
    location: part.location,
    quantity: part.quantity,
    minStock: part.minStock,
    unitPrice: part.unitPrice,
    reorderQty: part.reorderQty,
    supplier: part.supplier,
    leadTime: part.leadTime,
    description: part.description
  }
  dialogVisible.value = true
}

const viewPart = (part: SparePart) => {
  selectedPart.value = part
  viewDialogVisible.value = true
}

const deletePart = (part: SparePart) => {
  ElMessageBox.confirm(
      `Delete part "${part.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = spareParts.value.findIndex(p => p.id === part.id)
    if (index !== -1) {
      spareParts.value.splice(index, 1)
      ElMessage.success('Part deleted')
    }
  }).catch(() => {})
}

const savePart = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    if (editingPart.value) {
      const index = spareParts.value.findIndex(p => p.id === editingPart.value!.id)
      if (index !== -1) {
        spareParts.value[index] = {
          ...spareParts.value[index],
          name: partForm.value.name,
          category: partForm.value.category,
          manufacturer: partForm.value.manufacturer,
          model: partForm.value.model,
          location: partForm.value.location,
          quantity: partForm.value.quantity,
          minStock: partForm.value.minStock,
          unitPrice: partForm.value.unitPrice,
          reorderQty: partForm.value.reorderQty,
          supplier: partForm.value.supplier,
          leadTime: partForm.value.leadTime,
          description: partForm.value.description,
          lastRestocked: partForm.value.quantity !== spareParts.value[index].quantity ? new Date().toISOString().slice(0, 10) : spareParts.value[index].lastRestocked
        }
        ElMessage.success('Part updated')
      }
    } else {
      const newId = Math.max(...spareParts.value.map(p => p.id), 0) + 1
      spareParts.value.push({
        id: newId,
        code: partForm.value.code,
        name: partForm.value.name,
        category: partForm.value.category,
        manufacturer: partForm.value.manufacturer,
        model: partForm.value.model,
        location: partForm.value.location,
        quantity: partForm.value.quantity,
        minStock: partForm.value.minStock,
        unitPrice: partForm.value.unitPrice,
        reorderQty: partForm.value.reorderQty,
        supplier: partForm.value.supplier,
        leadTime: partForm.value.leadTime,
        lastRestocked: partForm.value.quantity > 0 ? new Date().toISOString().slice(0, 10) : null,
        description: partForm.value.description
      })
      ElMessage.success('Part added')
    }

    dialogVisible.value = false
  })
}

const reorderPart = (part: SparePart | null) => {
  if (!part) return
  ElMessageBox.confirm(
      `Create reorder for ${part.name}? Quantity: ${part.reorderQty} units.`,
      'Confirm Reorder',
      { confirmButtonText: 'Reorder', cancelButtonText: 'Cancel', type: 'info' }
  ).then(() => {
    const index = spareParts.value.findIndex(p => p.id === part.id)
    if (index !== -1) {
      spareParts.value[index].quantity += part.reorderQty
      spareParts.value[index].lastRestocked = new Date().toISOString().slice(0, 10)
      ElMessage.success(`Reorder placed for ${part.name}`)
    }
    lowStockDialogVisible.value = false
    viewDialogVisible.value = false
  }).catch(() => {})
}

const reorderAllLowStock = () => {
  ElMessageBox.confirm(
      `Reorder all ${lowStockParts.value.length} low stock items?`,
      'Confirm Bulk Reorder',
      { confirmButtonText: 'Reorder All', cancelButtonText: 'Cancel', type: 'info' }
  ).then(() => {
    lowStockParts.value.forEach(part => {
      const index = spareParts.value.findIndex(p => p.id === part.id)
      if (index !== -1) {
        spareParts.value[index].quantity += part.reorderQty
        spareParts.value[index].lastRestocked = new Date().toISOString().slice(0, 10)
      }
    })
    ElMessage.success(`Reorder placed for ${lowStockParts.value.length} items`)
    lowStockDialogVisible.value = false
  }).catch(() => {})
}

const checkLowStock = () => {
  if (lowStockParts.value.length === 0) {
    ElMessage.success('No low stock items found')
  } else {
    lowStockDialogVisible.value = true
  }
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('Inventory data exported')
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
.spare-parts-page {
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

.stock-good { color: #22c55e; font-weight: 600; }
.stock-low { color: #f59e0b; font-weight: 600; }
.stock-out { color: #ef4444; font-weight: 600; }

/* Dialog */
.part-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.view-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.part-detail {
  padding: 8px;
}

.low-stock-list {
  max-height: 400px;
  overflow-y: auto;
}

.low-stock-value {
  color: #f59e0b;
  font-weight: 600;
}

.no-low-stock {
  padding: 20px;
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