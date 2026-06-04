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
          <span class="loading-title">Vendor Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Supplier Relationship Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="vendor-management-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><OfficeBuilding /></el-icon>
          Vendor Management
        </h1>
        <div class="page-subtitle">Manage suppliers, contracts, and vendor performance</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon> Add Vendor
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
          <div class="stat-value">{{ stats.totalVendors }}</div>
          <div class="stat-label">Total Vendors</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.activeVendors }}</div>
          <div class="stat-label">Active Vendors</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.contractsExpiring }}</div>
          <div class="stat-label">Contracts Expiring Soon</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgRating }}<span class="unit">★</span></div>
          <div class="stat-label">Average Rating</div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by name or category..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option label="All Categories" value="" />
          <el-option label="UPS" value="UPS" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="Electrical" value="Electrical" />
          <el-option label="Generator" value="Generator" />
          <el-option label="Battery" value="Battery" />
          <el-option label="Maintenance" value="Maintenance" />
          <el-option label="Parts" value="Parts" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="All Status" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button size="small" @click="checkExpiringContracts">
          <el-icon><Bell /></el-icon> Check Expiring Contracts
        </el-button>
      </div>
    </div>

    <!-- Vendors Table -->
    <div class="table-container">
      <el-table
          :data="paginatedVendors"
          stripe
          border
          style="width: 100%"
          v-loading="tableLoading"
          @row-click="viewVendor"
      >
        <el-table-column prop="code" label="Vendor Code" width="120" sortable />
        <el-table-column prop="name" label="Vendor Name" min-width="180" sortable />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="contactPerson" label="Contact Person" width="140" />
        <el-table-column prop="phone" label="Phone" width="130" />
        <el-table-column prop="email" label="Email" min-width="180" />
        <el-table-column prop="contractStart" label="Contract Start" width="110" sortable />
        <el-table-column prop="contractEnd" label="Contract End" width="110" sortable>
          <template #default="{ row }">
            <span :class="getContractClass(row.contractEnd)">
              {{ row.contractEnd }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="Rating" width="100">
          <template #default="{ row }">
            <div class="rating-stars">
              <span v-for="i in 5" :key="i" class="star" :class="{ filled: i <= (row.rating || 0) }">★</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">
              {{ row.status === 'active' ? 'Active' : 'Inactive' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click.stop="editVendor(row)">Edit</el-button>
            <el-button type="primary" link size="small" @click.stop="viewVendor(row)">View</el-button>
            <el-button type="danger" link size="small" @click.stop="deleteVendor(row)">Delete</el-button>
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

    <!-- Add/Edit Vendor Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" class="vendor-dialog">
      <el-form :model="vendorForm" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Vendor Code" prop="code">
              <el-input v-model="vendorForm.code" placeholder="Auto-generated" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Vendor Name" prop="name">
              <el-input v-model="vendorForm.name" placeholder="Enter vendor name" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Category" prop="category">
              <el-select v-model="vendorForm.category" placeholder="Select category" style="width: 100%">
                <el-option label="UPS" value="UPS" />
                <el-option label="HVAC" value="HVAC" />
                <el-option label="Electrical" value="Electrical" />
                <el-option label="Generator" value="Generator" />
                <el-option label="Battery" value="Battery" />
                <el-option label="Maintenance" value="Maintenance" />
                <el-option label="Parts" value="Parts" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-radio-group v-model="vendorForm.status">
                <el-radio value="active">Active</el-radio>
                <el-radio value="inactive">Inactive</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Contact Person" prop="contactPerson">
              <el-input v-model="vendorForm.contactPerson" placeholder="Enter contact name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Position" prop="contactPosition">
              <el-input v-model="vendorForm.contactPosition" placeholder="Enter position" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Phone" prop="phone">
              <el-input v-model="vendorForm.phone" placeholder="Enter phone number" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Email" prop="email">
              <el-input v-model="vendorForm.email" placeholder="Enter email address" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Address" prop="address">
              <el-input v-model="vendorForm.address" placeholder="Enter full address" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Contract Start" prop="contractStart">
              <el-date-picker
                  v-model="vendorForm.contractStart"
                  type="date"
                  placeholder="Select start date"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Contract End" prop="contractEnd">
              <el-date-picker
                  v-model="vendorForm.contractEnd"
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
            <el-form-item label="Contract Value" prop="contractValue">
              <el-input-number v-model="vendorForm.contractValue" :min="0" :step="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Payment Terms" prop="paymentTerms">
              <el-select v-model="vendorForm.paymentTerms" placeholder="Select payment terms" style="width: 100%">
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
            <el-form-item label="Rating" prop="rating">
              <el-rate v-model="vendorForm.rating" :max="5" allow-half show-score />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Website" prop="website">
              <el-input v-model="vendorForm.website" placeholder="Enter website URL" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description" prop="description">
          <el-input v-model="vendorForm.description" type="textarea" :rows="2" placeholder="Vendor description..." />
        </el-form-item>

        <el-form-item label="Services Provided" prop="services">
          <el-input v-model="vendorForm.services" type="textarea" :rows="2" placeholder="List of services provided..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveVendor">Save Vendor</el-button>
      </template>
    </el-dialog>

    <!-- View Vendor Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="selectedVendor?.name" width="800px" class="view-dialog">
      <div v-if="selectedVendor" class="vendor-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Vendor Code">{{ selectedVendor.code }}</el-descriptions-item>
          <el-descriptions-item label="Vendor Name">{{ selectedVendor.name }}</el-descriptions-item>
          <el-descriptions-item label="Category">
            <el-tag :type="getCategoryTagType(selectedVendor.category)" size="small">{{ selectedVendor.category }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedVendor.status === 'active' ? 'success' : 'info'" size="small">
              {{ selectedVendor.status === 'active' ? 'Active' : 'Inactive' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Contact Person">{{ selectedVendor.contactPerson }}</el-descriptions-item>
          <el-descriptions-item label="Position">{{ selectedVendor.contactPosition }}</el-descriptions-item>
          <el-descriptions-item label="Phone">{{ selectedVendor.phone }}</el-descriptions-item>
          <el-descriptions-item label="Email">{{ selectedVendor.email }}</el-descriptions-item>
          <el-descriptions-item label="Address" :span="2">{{ selectedVendor.address }}</el-descriptions-item>
          <el-descriptions-item label="Contract Start">{{ selectedVendor.contractStart }}</el-descriptions-item>
          <el-descriptions-item label="Contract End">
            <span :class="getContractClass(selectedVendor.contractEnd)">{{ selectedVendor.contractEnd }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Contract Value">${{ formatNumber(selectedVendor.contractValue) }}</el-descriptions-item>
          <el-descriptions-item label="Payment Terms">{{ selectedVendor.paymentTerms }}</el-descriptions-item>
          <el-descriptions-item label="Rating">
            <el-rate v-model="selectedVendor.rating" disabled :max="5" allow-half show-score />
          </el-descriptions-item>
          <el-descriptions-item label="Website">
            <a :href="selectedVendor.website" target="_blank">{{ selectedVendor.website }}</a>
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedVendor.description || 'No description' }}</el-descriptions-item>
          <el-descriptions-item label="Services Provided" :span="2">{{ selectedVendor.services || 'No services listed' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editVendor(selectedVendor)">Edit Vendor</el-button>
        <el-button type="warning" @click="renewContract(selectedVendor)" v-if="isContractExpiringSoon(selectedVendor?.contractEnd)">
          Renew Contract
        </el-button>
      </template>
    </el-dialog>

    <!-- Expiring Contracts Dialog -->
    <el-dialog v-model="expiryDialogVisible" title="Contracts Expiring Soon" width="700px">
      <div class="expiring-list">
        <el-table :data="expiringContracts" border stripe>
          <el-table-column prop="code" label="Vendor Code" width="120" />
          <el-table-column prop="name" label="Vendor Name" min-width="180" />
          <el-table-column prop="contractEnd" label="Contract End Date" width="120">
            <template #default="{ row }">
              <span class="expiring-date">{{ row.contractEnd }}</span>
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
          <el-empty description="No contracts expiring soon" :image-size="80" />
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
  OfficeBuilding, Plus, Download, Refresh, Search, CircleCheck,
  Clock, Star, Bell
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading vendor data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading vendor data...',
  'Loading contracts...',
  'Analyzing vendor performance...',
  'Almost ready...'
]

// ==================== Types ====================
interface Vendor {
  id: number
  code: string
  name: string
  category: string
  contactPerson: string
  contactPosition: string
  phone: string
  email: string
  address: string
  contractStart: string
  contractEnd: string
  contractValue: number
  paymentTerms: string
  rating: number
  website: string
  status: 'active' | 'inactive'
  description: string
  services: string
}

// ==================== Mock Data (20 vendors) ====================
const vendors = ref<Vendor[]>([
  { id: 1, code: 'VEN-001', name: 'Schneider Electric', category: 'UPS', contactPerson: 'John Smith', contactPosition: 'Account Manager', phone: '+65 6123 4567', email: 'sales.sg@schneider-electric.com', address: '1 International Business Park, Singapore 609933', contractStart: '2024-01-01', contractEnd: '2025-12-31', contractValue: 250000, paymentTerms: 'Net 45', rating: 4.8, website: 'www.se.com', status: 'active', description: 'Global leader in energy management and automation', services: 'UPS systems, PDUs, power distribution equipment' },
  { id: 2, code: 'VEN-002', name: 'Vertiv Singapore', category: 'HVAC', contactPerson: 'Mary Tan', contactPosition: 'Regional Manager', phone: '+65 6789 0123', email: 'mary.tan@vertiv.com', address: '8 Temasek Boulevard, Singapore 038988', contractStart: '2023-06-01', contractEnd: '2025-05-31', contractValue: 180000, paymentTerms: 'Net 30', rating: 4.6, website: 'www.vertiv.com', status: 'active', description: 'Critical infrastructure and solutions provider', services: 'CRAC units, cooling systems, thermal management' },
  { id: 3, code: 'VEN-003', name: 'Caterpillar Singapore', category: 'Generator', contactPerson: 'Robert Lee', contactPosition: 'Sales Director', phone: '+65 6234 5678', email: 'robert.lee@cat.com', address: '7 Tampines Industrial Ave, Singapore 528800', contractStart: '2023-03-15', contractEnd: '2025-03-14', contractValue: 350000, paymentTerms: 'Net 60', rating: 4.9, website: 'www.caterpillar.com', status: 'active', description: 'Leading manufacturer of construction and mining equipment', services: 'Generator systems, engines, power solutions' },
  { id: 4, code: 'VEN-004', name: 'Trane Singapore', category: 'HVAC', contactPerson: 'David Wong', contactPosition: 'Technical Manager', phone: '+65 6345 6789', email: 'david.wong@trane.com', address: '12 Kallang Way, Singapore 349033', contractStart: '2023-09-01', contractEnd: '2024-12-31', contractValue: 220000, paymentTerms: 'Net 45', rating: 4.5, website: 'www.trane.com', status: 'active', description: 'Indoor comfort solutions and services', services: 'Chiller systems, HVAC maintenance, cooling solutions' },
  { id: 5, code: 'VEN-005', name: 'ABB Singapore', category: 'Electrical', contactPerson: 'Susan Lim', contactPosition: 'Key Account Manager', phone: '+65 6456 7890', email: 'susan.lim@abb.com', address: '2 Ayer Rajah Crescent, Singapore 139935', contractStart: '2024-02-01', contractEnd: '2026-01-31', contractValue: 300000, paymentTerms: 'Net 30', rating: 4.7, website: 'www.abb.com', status: 'active', description: 'Pioneer in electrical equipment and automation', services: 'Transformers, switchgear, electrical components' },
  { id: 6, code: 'VEN-006', name: 'Battery Supply Co.', category: 'Battery', contactPerson: 'James Koh', contactPosition: 'Sales Manager', phone: '+65 6567 8901', email: 'james@batterysupply.com', address: '15 Ubi Road 4, Singapore 408602', contractStart: '2023-01-01', contractEnd: '2024-12-31', contractValue: 120000, paymentTerms: 'Net 30', rating: 4.3, website: 'www.batterysupply.com', status: 'active', description: 'Specialized battery supplier', services: 'UPS batteries, replacement batteries, battery maintenance' },
  { id: 7, code: 'VEN-007', name: 'HVAC Supplies Inc.', category: 'HVAC', contactPerson: 'William Tan', contactPosition: 'Operations Manager', phone: '+65 6678 9012', email: 'william@hvacsupplies.com', address: '28 Woodlands Loop, Singapore 738283', contractStart: '2023-07-01', contractEnd: '2025-06-30', contractValue: 95000, paymentTerms: 'Net 30', rating: 4.4, website: 'www.hvacsupplies.com', status: 'active', description: 'HVAC parts and equipment supplier', services: 'Filters, compressors, thermostats, HVAC accessories' },
  { id: 8, code: 'VEN-008', name: 'Electrical Parts Ltd.', category: 'Parts', contactPerson: 'Angela Chua', contactPosition: 'Procurement Manager', phone: '+65 6789 0123', email: 'angela@electricalparts.com', address: '6 Kaki Bukit Crescent, Singapore 416083', contractStart: '2023-11-01', contractEnd: '2024-10-31', contractValue: 80000, paymentTerms: 'Net 30', rating: 4.2, website: 'www.electricalparts.com', status: 'active', description: 'Electrical components distributor', services: 'Circuit breakers, fuses, wiring accessories' },
  { id: 9, code: 'VEN-009', name: 'Eaton Singapore', category: 'UPS', contactPerson: 'Richard Goh', contactPosition: 'Sales Director', phone: '+65 6890 1234', email: 'richard.goh@eaton.com', address: '1 Changi Business Park, Singapore 486025', contractStart: '2024-03-01', contractEnd: '2026-02-28', contractValue: 280000, paymentTerms: 'Net 45', rating: 4.8, website: 'www.eaton.com', status: 'active', description: 'Power management company', services: 'UPS systems, PDUs, power management solutions' },
  { id: 10, code: 'VEN-010', name: 'Generator Parts Co.', category: 'Generator', contactPerson: 'Patrick Low', contactPosition: 'Technical Sales', phone: '+65 6901 2345', email: 'patrick@genparts.com', address: '22 Pioneer Road, Singapore 639505', contractStart: '2023-08-01', contractEnd: '2025-07-31', contractValue: 150000, paymentTerms: 'Net 30', rating: 4.5, website: 'www.genparts.com', status: 'active', description: 'Generator parts and maintenance services', services: 'Generator parts, oil filters, spark plugs, maintenance kits' },
  { id: 11, code: 'VEN-011', name: 'Cable Solutions', category: 'Parts', contactPerson: 'Helen Ng', contactPosition: 'Account Manager', phone: '+65 7012 3456', email: 'helen@cablesolutions.com', address: '10 Toh Guan Road, Singapore 608789', contractStart: '2023-12-01', contractEnd: '2024-11-30', contractValue: 60000, paymentTerms: 'Net 30', rating: 4.1, website: 'www.cablesolutions.com', status: 'active', description: 'Cable and connectivity solutions', services: 'Power cables, network cables, patch panels' },
  { id: 12, code: 'VEN-012', name: 'Johnson Controls', category: 'HVAC', contactPerson: 'Marcus Teo', contactPosition: 'Service Manager', phone: '+65 7123 4567', email: 'marcus.teo@jci.com', address: '5 Clementi Loop, Singapore 129816', contractStart: '2022-10-01', contractEnd: '2024-09-30', contractValue: 200000, paymentTerms: 'Net 45', rating: 4.6, website: 'www.johnsoncontrols.com', status: 'active', description: 'Building efficiency solutions', services: 'HVAC control systems, building automation' },
  { id: 13, code: 'VEN-013', name: 'Siemens Singapore', category: 'Electrical', contactPerson: 'Christina Lim', contactPosition: 'Business Development', phone: '+65 7234 5678', email: 'christina.lim@siemens.com', address: '60 MacPherson Road, Singapore 348615', contractStart: '2024-04-01', contractEnd: '2026-03-31', contractValue: 320000, paymentTerms: 'Net 60', rating: 4.9, website: 'www.siemens.com', status: 'active', description: 'Global technology company', services: 'Electrical systems, automation, digitalization' },
  { id: 14, code: 'VEN-014', name: 'Maintenance Solutions Pte Ltd', category: 'Maintenance', contactPerson: 'Kenny Foo', contactPosition: 'Operations Director', phone: '+65 7345 6789', email: 'kenny@maintenancesolutions.com', address: '18 Penjuru Lane, Singapore 609195', contractStart: '2023-05-01', contractEnd: '2025-04-30', contractValue: 450000, paymentTerms: 'Net 30', rating: 4.7, website: 'www.maintenancesolutions.com', status: 'active', description: 'Integrated facility maintenance services', services: 'Preventive maintenance, corrective maintenance, 24/7 support' },
  { id: 15, code: 'VEN-015', name: 'UPS Parts Direct', category: 'UPS', contactPerson: 'Bryan Tan', contactPosition: 'Sales Manager', phone: '+65 7456 7890', email: 'bryan@upsparts.com', address: '33 Loyang Drive, Singapore 508910', contractStart: '2023-10-01', contractEnd: '2024-09-30', contractValue: 75000, paymentTerms: 'Net 30', rating: 4.3, website: 'www.upsparts.com', status: 'active', description: 'UPS parts and accessories supplier', services: 'UPS batteries, control boards, fans, capacitors' },
  { id: 16, code: 'VEN-016', name: 'Cooling Tower Services', category: 'HVAC', contactPerson: 'Raymond Chan', contactPosition: 'Technical Manager', phone: '+65 7567 8901', email: 'raymond@coolingtowers.com', address: '9 Tuas Avenue 12, Singapore 639045', contractStart: '2023-04-01', contractEnd: '2025-03-31', contractValue: 130000, paymentTerms: 'Net 45', rating: 4.4, website: 'www.coolingtowers.com', status: 'active', description: 'Cooling tower specialist', services: 'Cooling tower maintenance, repairs, spare parts' },
  { id: 17, code: 'VEN-017', name: 'Transformer Specialist', category: 'Electrical', contactPerson: 'Albert Koh', contactPosition: 'Technical Director', phone: '+65 7678 9012', email: 'albert@transformerspec.com', address: '25 Gul Circle, Singapore 629632', contractStart: '2023-02-01', contractEnd: '2025-01-31', contractValue: 110000, paymentTerms: 'Net 30', rating: 4.5, website: 'www.transformerspec.com', status: 'active', description: 'Transformer maintenance and repair', services: 'Transformer oil analysis, maintenance, repairs' },
  { id: 18, code: 'VEN-018', name: 'Carrier Singapore', category: 'HVAC', contactPerson: 'Vivian Tay', contactPosition: 'Service Manager', phone: '+65 7789 0123', email: 'vivian.tay@carrier.com', address: '3 Ang Mo Kio Street 62, Singapore 569140', contractStart: '2022-12-01', contractEnd: '2024-11-30', contractValue: 160000, paymentTerms: 'Net 45', rating: 4.6, website: 'www.carrier.com', status: 'active', description: 'Heating, ventilation, and air conditioning', services: 'HVAC systems, air handling units, maintenance' },
  { id: 19, code: 'VEN-019', name: 'Industrial Parts Inc.', category: 'Parts', contactPerson: 'Steven Goh', contactPosition: 'Sales Manager', phone: '+65 7890 1234', email: 'steven@industrialparts.com', address: '16 Kian Teck Drive, Singapore 628831', contractStart: '2024-01-15', contractEnd: '2025-01-14', contractValue: 85000, paymentTerms: 'Net 30', rating: 4.2, website: 'www.industrialparts.com', status: 'active', description: 'Industrial parts distributor', services: 'Mechanical seals, bearings, belts, gaskets' },
  { id: 20, code: 'VEN-020', name: 'Generator Solutions', category: 'Generator', contactPerson: 'Derek Lim', contactPosition: 'Operations Manager', phone: '+65 7901 2345', email: 'derek@generatorsolutions.com', address: '42 Sungei Kadut Loop, Singapore 729492', contractStart: '2023-11-15', contractEnd: '2025-11-14', contractValue: 190000, paymentTerms: 'Net 30', rating: 4.5, website: 'www.generatorsolutions.com', status: 'active', description: 'Generator maintenance and repair services', services: 'Generator servicing, repairs, load testing, spare parts' }
])

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const expiryDialogVisible = ref(false)
const dialogTitle = ref('Add Vendor')
const selectedVendor = ref<Vendor | null>(null)
const editingVendor = ref<Vendor | null>(null)
const formRef = ref()

const vendorForm = ref({
  id: null as number | null,
  code: '',
  name: '',
  category: '',
  contactPerson: '',
  contactPosition: '',
  phone: '',
  email: '',
  address: '',
  contractStart: '',
  contractEnd: '',
  contractValue: 0,
  paymentTerms: 'Net 30',
  rating: 4,
  website: '',
  status: 'active' as 'active' | 'inactive',
  description: '',
  services: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter vendor name', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  contactPerson: [{ required: true, message: 'Please enter contact person', trigger: 'blur' }],
  phone: [{ required: true, message: 'Please enter phone number', trigger: 'blur' }],
  email: [{ required: true, message: 'Please enter email address', trigger: 'blur' }, { type: 'email', message: 'Please enter valid email', trigger: 'blur' }]
}

// ==================== Computed ====================
const stats = computed(() => {
  const totalVendors = vendors.value.length
  const activeVendors = vendors.value.filter(v => v.status === 'active').length
  const today = new Date()
  const thirtyDaysFromNow = new Date()
  thirtyDaysFromNow.setDate(today.getDate() + 30)
  const contractsExpiring = vendors.value.filter(v => {
    const endDate = new Date(v.contractEnd)
    return endDate <= thirtyDaysFromNow && endDate >= today && v.status === 'active'
  }).length
  const avgRating = (vendors.value.reduce((sum, v) => sum + v.rating, 0) / vendors.value.length).toFixed(1)

  return { totalVendors, activeVendors, contractsExpiring, avgRating }
})

const expiringContracts = computed(() => {
  const today = new Date()
  const thirtyDaysFromNow = new Date()
  thirtyDaysFromNow.setDate(today.getDate() + 30)
  return vendors.value
      .filter(v => {
        const endDate = new Date(v.contractEnd)
        return endDate <= thirtyDaysFromNow && endDate >= today && v.status === 'active'
      })
      .map(v => ({
        ...v,
        daysLeft: Math.ceil((new Date(v.contractEnd).getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
      }))
      .sort((a, b) => a.daysLeft - b.daysLeft)
})

const filteredVendors = computed(() => {
  let filtered = [...vendors.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(v =>
        v.name.toLowerCase().includes(search) ||
        v.code.toLowerCase().includes(search) ||
        v.category.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(v => v.category === categoryFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(v => v.status === statusFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredVendors.value.length)

const paginatedVendors = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredVendors.value.slice(start, end)
})

// ==================== Helper Functions ====================
const formatNumber = (num: number): string => {
  return num.toLocaleString()
}

const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    UPS: 'primary', HVAC: 'info', Electrical: 'warning', Generator: 'danger',
    Battery: 'success', Maintenance: '', Parts: 'info'
  }
  return map[category] || 'info'
}

const getContractClass = (endDate: string): string => {
  const today = new Date()
  const end = new Date(endDate)
  const daysLeft = Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  if (daysLeft < 0) return 'contract-expired'
  if (daysLeft < 30) return 'contract-expiring'
  return 'contract-good'
}

const getDaysLeftType = (days: number): string => {
  if (days < 7) return 'danger'
  if (days < 30) return 'warning'
  return 'success'
}

const isContractExpiringSoon = (endDate?: string): boolean => {
  if (!endDate) return false
  const today = new Date()
  const end = new Date(endDate)
  const daysLeft = Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
  return daysLeft > 0 && daysLeft <= 30
}

const generateVendorCode = (): string => {
  const count = vendors.value.length + 1
  return `VEN-${String(count).padStart(3, '0')}`
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const openAddDialog = () => {
  dialogTitle.value = 'Add Vendor'
  editingVendor.value = null
  vendorForm.value = {
    id: null,
    code: generateVendorCode(),
    name: '',
    category: '',
    contactPerson: '',
    contactPosition: '',
    phone: '',
    email: '',
    address: '',
    contractStart: new Date().toISOString().slice(0, 10),
    contractEnd: '',
    contractValue: 0,
    paymentTerms: 'Net 30',
    rating: 4,
    website: '',
    status: 'active',
    description: '',
    services: ''
  }
  dialogVisible.value = true
}

const editVendor = (vendor: Vendor | null) => {
  if (!vendor) return
  dialogTitle.value = 'Edit Vendor'
  editingVendor.value = vendor
  vendorForm.value = {
    id: vendor.id,
    code: vendor.code,
    name: vendor.name,
    category: vendor.category,
    contactPerson: vendor.contactPerson,
    contactPosition: vendor.contactPosition,
    phone: vendor.phone,
    email: vendor.email,
    address: vendor.address,
    contractStart: vendor.contractStart,
    contractEnd: vendor.contractEnd,
    contractValue: vendor.contractValue,
    paymentTerms: vendor.paymentTerms,
    rating: vendor.rating,
    website: vendor.website,
    status: vendor.status,
    description: vendor.description,
    services: vendor.services
  }
  dialogVisible.value = true
}

const viewVendor = (vendor: Vendor) => {
  selectedVendor.value = vendor
  viewDialogVisible.value = true
}

const deleteVendor = (vendor: Vendor) => {
  ElMessageBox.confirm(
      `Delete vendor "${vendor.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = vendors.value.findIndex(v => v.id === vendor.id)
    if (index !== -1) {
      vendors.value.splice(index, 1)
      ElMessage.success('Vendor deleted')
    }
  }).catch(() => {})
}

const saveVendor = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    if (editingVendor.value) {
      const index = vendors.value.findIndex(v => v.id === editingVendor.value!.id)
      if (index !== -1) {
        vendors.value[index] = {
          ...vendors.value[index],
          name: vendorForm.value.name,
          category: vendorForm.value.category,
          contactPerson: vendorForm.value.contactPerson,
          contactPosition: vendorForm.value.contactPosition,
          phone: vendorForm.value.phone,
          email: vendorForm.value.email,
          address: vendorForm.value.address,
          contractStart: vendorForm.value.contractStart,
          contractEnd: vendorForm.value.contractEnd,
          contractValue: vendorForm.value.contractValue,
          paymentTerms: vendorForm.value.paymentTerms,
          rating: vendorForm.value.rating,
          website: vendorForm.value.website,
          status: vendorForm.value.status,
          description: vendorForm.value.description,
          services: vendorForm.value.services
        }
        ElMessage.success('Vendor updated')
      }
    } else {
      const newId = Math.max(...vendors.value.map(v => v.id), 0) + 1
      vendors.value.push({
        id: newId,
        code: vendorForm.value.code,
        name: vendorForm.value.name,
        category: vendorForm.value.category,
        contactPerson: vendorForm.value.contactPerson,
        contactPosition: vendorForm.value.contactPosition,
        phone: vendorForm.value.phone,
        email: vendorForm.value.email,
        address: vendorForm.value.address,
        contractStart: vendorForm.value.contractStart,
        contractEnd: vendorForm.value.contractEnd,
        contractValue: vendorForm.value.contractValue,
        paymentTerms: vendorForm.value.paymentTerms,
        rating: vendorForm.value.rating,
        website: vendorForm.value.website,
        status: vendorForm.value.status,
        description: vendorForm.value.description,
        services: vendorForm.value.services
      })
      ElMessage.success('Vendor added')
    }

    dialogVisible.value = false
  })
}

const renewContract = (vendor: Vendor | null) => {
  if (!vendor) return
  ElMessageBox.prompt('Enter new contract end date', 'Renew Contract', {
    confirmButtonText: 'Renew',
    cancelButtonText: 'Cancel',
    inputType: 'date',
    inputValue: new Date(vendor.contractEnd)
  }).then(({ value }) => {
    const index = vendors.value.findIndex(v => v.id === vendor.id)
    if (index !== -1 && value) {
      vendors.value[index].contractEnd = value as string
      ElMessage.success(`Contract renewed for ${vendor.name}`)
      expiryDialogVisible.value = false
      viewDialogVisible.value = false
    }
  }).catch(() => {})
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
    ElMessage.success('Vendor data exported')
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
.vendor-management-page {
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
  justify-align: space-between;
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

/* Rating Stars */
.rating-stars {
  display: inline-flex;
  gap: 2px;
}

.star {
  font-size: 14px;
  color: #e2e8f0;
}

.star.filled {
  color: #fbbf24;
}

/* Contract Status */
.contract-good { color: #22c55e; }
.contract-expiring { color: #f59e0b; font-weight: 600; }
.contract-expired { color: #ef4444; font-weight: 600; }

.expiring-date {
  color: #f59e0b;
  font-weight: 600;
}

/* Dialog */
.vendor-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.view-dialog :deep(.el-dialog__body) {
  max-height: 550px;
  overflow-y: auto;
}

.vendor-detail {
  padding: 8px;
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