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
          <span class="loading-title">Inspection Checklist</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Quality & Compliance Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="inspection-checklist-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Checked /></el-icon>
          Inspection Checklist
        </h1>
        <div class="page-subtitle">Standardized inspection templates for equipment maintenance</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon> Create Checklist
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
          <div class="stat-value">{{ stats.totalTemplates }}</div>
          <div class="stat-label">Total Templates</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.activeTemplates }}</div>
          <div class="stat-label">Active</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Checked /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalItems }}</div>
          <div class="stat-label">Total Checklist Items</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.complianceRate }}<span class="unit">%</span></div>
          <div class="stat-label">Compliance Rate</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by name or equipment type..."
            style="width: 280px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="equipmentTypeFilter" placeholder="Equipment Type" clearable style="width: 150px">
          <el-option label="UPS" value="UPS" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Chiller" value="Chiller" />
          <el-option label="Generator" value="Generator" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="Transformer" value="Transformer" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="filter-label">Last updated: {{ lastUpdated }}</span>
      </div>
    </div>

    <!-- Checklist Cards Grid -->
    <div class="checklist-grid">
      <div
          v-for="template in filteredTemplates"
          :key="template.id"
          class="checklist-card"
          :class="{ inactive: template.status === 'inactive' }"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="header-left">
            <div class="template-icon" :class="getEquipmentTypeColor(template.equipmentType)">
              <el-icon><Checked /></el-icon>
            </div>
            <div class="template-info">
              <div class="template-name">{{ template.name }}</div>
              <div class="template-meta">
                <span class="equipment-type">{{ template.equipmentType }}</span>
                <span class="version">v{{ template.version }}</span>
              </div>
            </div>
          </div>
          <el-dropdown trigger="click" @command="(cmd) => handleMenuCommand(cmd, template)">
            <el-button text circle>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="view">View Details</el-dropdown-item>
                <el-dropdown-item command="edit">Edit</el-dropdown-item>
                <el-dropdown-item command="duplicate">Duplicate</el-dropdown-item>
                <el-dropdown-item command="export">Export</el-dropdown-item>
                <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- Card Stats -->
        <div class="card-stats">
          <div class="stat-row">
            <div class="stat">
              <span class="stat-label-sm">Total Items</span>
              <span class="stat-value-sm">{{ template.items.length }}</span>
            </div>
            <div class="stat">
              <span class="stat-label-sm">Critical Items</span>
              <span class="stat-value-sm critical">{{ template.criticalCount }}</span>
            </div>
            <div class="stat">
              <span class="stat-label-sm">Used Count</span>
              <span class="stat-value-sm">{{ template.usedCount }}</span>
            </div>
          </div>
          <div class="progress-row">
            <div class="progress-label">Compliance Rate</div>
            <el-progress :percentage="template.complianceRate" :stroke-width="6" :color="getProgressColor(template.complianceRate)" />
          </div>
        </div>

        <!-- Card Preview -->
        <div class="card-preview">
          <div class="preview-header">
            <span>Sample Checklist Items</span>
            <el-button text size="small" @click="viewTemplate(template)">View All →</el-button>
          </div>
          <div class="preview-items">
            <div v-for="item in template.items.slice(0, 3)" :key="item.id" class="preview-item">
              <el-icon :class="item.isRequired ? 'required' : 'optional'">
                <CircleCheck v-if="item.isRequired" /><Check v-else />
              </el-icon>
              <span>{{ item.name.length > 40 ? item.name.substring(0, 40) + '...' : item.name }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-info">
            <span><el-icon><Calendar /></el-icon> Updated: {{ template.updatedAt }}</span>
            <span><el-icon><User /></el-icon> {{ template.createdBy }}</span>
          </div>
          <el-tag :type="template.status === 'active' ? 'success' : 'info'" size="small">
            {{ template.status === 'active' ? 'Active' : 'Inactive' }}
          </el-tag>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredTemplates.length === 0" class="empty-state">
        <el-empty description="No checklist templates found">
          <el-button type="primary" @click="openCreateDialog">Create First Checklist</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Create/Edit Checklist Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="750px" class="checklist-dialog">
      <el-form :model="checklistForm" :rules="formRules" ref="formRef" label-width="120px">
        <!-- Basic Info -->
        <div class="form-section">
          <div class="section-title">Basic Information</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Template Name" prop="name">
                <el-input v-model="checklistForm.name" placeholder="e.g., UPS Monthly Inspection" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Equipment Type" prop="equipmentType">
                <el-select v-model="checklistForm.equipmentType" placeholder="Select equipment type" style="width: 100%">
                  <el-option label="UPS" value="UPS" />
                  <el-option label="CRAC" value="CRAC" />
                  <el-option label="PDU" value="PDU" />
                  <el-option label="Chiller" value="Chiller" />
                  <el-option label="Generator" value="Generator" />
                  <el-option label="HVAC" value="HVAC" />
                  <el-option label="Transformer" value="Transformer" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="Frequency" prop="frequency">
                <el-select v-model="checklistForm.frequency" placeholder="Select frequency" style="width: 100%">
                  <el-option label="Daily" value="daily" />
                  <el-option label="Weekly" value="weekly" />
                  <el-option label="Monthly" value="monthly" />
                  <el-option label="Quarterly" value="quarterly" />
                  <el-option label="Yearly" value="yearly" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="Status" prop="status">
                <el-radio-group v-model="checklistForm.status">
                  <el-radio value="active">Active</el-radio>
                  <el-radio value="inactive">Inactive</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="Description" prop="description">
            <el-input v-model="checklistForm.description" type="textarea" :rows="2" placeholder="Describe the purpose of this checklist..." />
          </el-form-item>
        </div>

        <!-- Checklist Items -->
        <div class="form-section">
          <div class="section-title">
            <span>Checklist Items</span>
            <el-button type="primary" link @click="addChecklistItem">
              <el-icon><Plus /></el-icon> Add Item
            </el-button>
          </div>

          <div class="items-table">
            <div v-for="(item, idx) in checklistForm.items" :key="idx" class="item-row">
              <div class="item-order">{{ idx + 1 }}</div>
              <div class="item-name">
                <el-input
                    v-model="item.name"
                    placeholder="Inspection item description"
                    size="small"
                />
              </div>
              <div class="item-type">
                <el-select v-model="item.type" placeholder="Type" size="small" style="width: 100px">
                  <el-option label="Check" value="check" />
                  <el-option label="Measure" value="measure" />
                  <el-option label="Visual" value="visual" />
                  <el-option label="Test" value="test" />
                </el-select>
              </div>
              <div class="item-required">
                <el-checkbox v-model="item.isRequired">Required</el-checkbox>
              </div>
              <div class="item-standard">
                <el-input
                    v-model="item.standardValue"
                    placeholder="Standard value (optional)"
                    size="small"
                    style="width: 120px"
                />
              </div>
              <div class="item-unit">
                <el-input
                    v-model="item.unit"
                    placeholder="Unit"
                    size="small"
                    style="width: 60px"
                />
              </div>
              <div class="item-actions">
                <el-button type="danger" link size="small" @click="removeChecklistItem(idx)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>

            <div v-if="checklistForm.items.length === 0" class="empty-items">
              <el-empty description="No checklist items added" :image-size="60" />
            </div>
          </div>
        </div>

        <!-- Reference Documents -->
        <div class="form-section">
          <div class="section-title">
            <span>Reference Documents</span>
            <el-button type="primary" link @click="addReference">
              <el-icon><Plus /></el-icon> Add Reference
            </el-button>
          </div>
          <div class="references-list">
            <div v-for="(ref, idx) in checklistForm.references" :key="idx" class="reference-row">
              <el-input v-model="ref.name" placeholder="Document name" size="small" style="flex: 2" />
              <el-input v-model="ref.link" placeholder="Link or file path" size="small" style="flex: 3" />
              <el-button type="danger" link size="small" @click="removeReference(idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveChecklist">Save Template</el-button>
      </template>
    </el-dialog>

    <!-- View Template Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="viewTemplateData?.name" width="800px" class="view-dialog">
      <div v-if="viewTemplateData" class="view-content">
        <!-- Basic Info -->
        <div class="view-section">
          <div class="view-section-title">Basic Information</div>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Template Name">{{ viewTemplateData.name }}</el-descriptions-item>
            <el-descriptions-item label="Equipment Type">{{ viewTemplateData.equipmentType }}</el-descriptions-item>
            <el-descriptions-item label="Frequency">{{ getFrequencyText(viewTemplateData.frequency) }}</el-descriptions-item>
            <el-descriptions-item label="Version">v{{ viewTemplateData.version }}</el-descriptions-item>
            <el-descriptions-item label="Created By">{{ viewTemplateData.createdBy }}</el-descriptions-item>
            <el-descriptions-item label="Last Updated">{{ viewTemplateData.updatedAt }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ viewTemplateData.description || 'No description' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Checklist Items -->
        <div class="view-section">
          <div class="view-section-title">Checklist Items ({{ viewTemplateData.items.length }})</div>
          <div class="view-items-table">
            <div class="view-items-header">
              <div class="col-order">#</div>
              <div class="col-name">Inspection Item</div>
              <div class="col-type">Type</div>
              <div class="col-standard">Standard Value</div>
              <div class="col-required">Required</div>
            </div>
            <div v-for="(item, idx) in viewTemplateData.items" :key="idx" class="view-items-row">
              <div class="col-order">{{ idx + 1 }}</div>
              <div class="col-name">{{ item.name }}</div>
              <div class="col-type">
                <el-tag :type="getItemTypeTag(item.type)" size="small">{{ getItemTypeText(item.type) }}</el-tag>
              </div>
              <div class="col-standard">{{ item.standardValue || '-' }} {{ item.unit || '' }}</div>
              <div class="col-required">
                <el-tag :type="item.isRequired ? 'danger' : 'info'" size="small">
                  {{ item.isRequired ? 'Required' : 'Optional' }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- Reference Documents -->
        <div class="view-section" v-if="viewTemplateData.references?.length">
          <div class="view-section-title">Reference Documents</div>
          <div class="view-references">
            <div v-for="(ref, idx) in viewTemplateData.references" :key="idx" class="reference-link">
              <el-icon><Link /></el-icon>
              <span>{{ ref.name }}</span>
              <el-link :href="ref.link" target="_blank" type="primary">View</el-link>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="viewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editFromView">Edit Template</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Checked, Plus, Download, Refresh, Search, MoreFilled,
  CircleCheck, Check, Calendar, User, Delete, Link, TrendCharts
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading checklist templates...',
  'Loading inspection items...',
  'Almost ready...'
]

// ==================== Types ====================
interface ChecklistItem {
  id: number
  name: string
  type: 'check' | 'measure' | 'visual' | 'test'
  isRequired: boolean
  standardValue?: string
  unit?: string
}

interface Reference {
  name: string
  link: string
}

interface ChecklistTemplate {
  id: number
  name: string
  equipmentType: string
  frequency: string
  version: number
  description: string
  items: ChecklistItem[]
  references: Reference[]
  status: 'active' | 'inactive'
  createdBy: string
  createdAt: string
  updatedAt: string
  usedCount: number
  criticalCount: number
  complianceRate: number
}

// ==================== Mock Data ====================
// ==================== Mock Data (12 Templates) ====================
const checklistTemplates = ref<ChecklistTemplate[]>([
  {
    id: 1,
    name: 'UPS Monthly Inspection Checklist',
    equipmentType: 'UPS',
    frequency: 'monthly',
    version: 2,
    description: 'Comprehensive inspection checklist for UPS systems including battery health, input/output parameters, and environmental conditions.',
    items: [
      { id: 1, name: 'Check input voltage and current', type: 'measure', isRequired: true, standardValue: '±10%', unit: 'V' },
      { id: 2, name: 'Check output voltage and current', type: 'measure', isRequired: true, standardValue: '±5%', unit: 'V' },
      { id: 3, name: 'Inspect battery terminal connections', type: 'visual', isRequired: true, standardValue: 'No corrosion', unit: '' },
      { id: 4, name: 'Measure battery string voltage', type: 'measure', isRequired: true, standardValue: '≥400', unit: 'V' },
      { id: 5, name: 'Check fan operation and noise', type: 'check', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 6, name: 'Record ambient temperature', type: 'measure', isRequired: true, standardValue: '20-25', unit: '°C' },
      { id: 7, name: 'Check for alarms on display', type: 'check', isRequired: true, standardValue: 'No alarms', unit: '' }
    ],
    references: [
      { name: 'UPS Maintenance Manual', link: '/docs/ups-manual.pdf' },
      { name: 'Battery Safety Guidelines', link: '/docs/battery-safety.pdf' }
    ],
    status: 'active',
    createdBy: 'John Chen',
    createdAt: '2024-01-15',
    updatedAt: '2024-05-20',
    usedCount: 24,
    criticalCount: 5,
    complianceRate: 96
  },
  {
    id: 2,
    name: 'CRAC Unit Weekly Checklist',
    equipmentType: 'CRAC',
    frequency: 'weekly',
    version: 3,
    description: 'Weekly inspection checklist for CRAC units covering cooling performance, filters, and refrigerant levels.',
    items: [
      { id: 8, name: 'Check supply air temperature', type: 'measure', isRequired: true, standardValue: '18-22', unit: '°C' },
      { id: 9, name: 'Check return air temperature', type: 'measure', isRequired: true, standardValue: '22-26', unit: '°C' },
      { id: 10, name: 'Inspect and clean air filters', type: 'visual', isRequired: true, standardValue: 'Clean', unit: '' },
      { id: 11, name: 'Check refrigerant pressure', type: 'measure', isRequired: true, standardValue: '60-80', unit: 'psi' },
      { id: 12, name: 'Check condensate drain', type: 'check', isRequired: true, standardValue: 'Clear', unit: '' },
      { id: 13, name: 'Record humidity level', type: 'measure', isRequired: true, standardValue: '40-60', unit: '%' }
    ],
    references: [
      { name: 'CRAC Maintenance Schedule', link: '/docs/crac-schedule.pdf' }
    ],
    status: 'active',
    createdBy: 'Sarah Wong',
    createdAt: '2024-01-10',
    updatedAt: '2024-05-18',
    usedCount: 42,
    criticalCount: 4,
    complianceRate: 98
  },
  {
    id: 3,
    name: 'Generator Monthly Test Checklist',
    equipmentType: 'Generator',
    frequency: 'monthly',
    version: 1,
    description: 'Monthly generator testing and inspection checklist for backup power systems.',
    items: [
      { id: 14, name: 'Check fuel level', type: 'measure', isRequired: true, standardValue: '≥75', unit: '%' },
      { id: 15, name: 'Start generator and run for 30 min', type: 'test', isRequired: true, standardValue: 'Normal operation', unit: '' },
      { id: 16, name: 'Check oil pressure', type: 'measure', isRequired: true, standardValue: '40-60', unit: 'psi' },
      { id: 17, name: 'Check coolant temperature', type: 'measure', isRequired: true, standardValue: '80-95', unit: '°C' },
      { id: 18, name: 'Inspect battery voltage', type: 'measure', isRequired: true, standardValue: '≥12.5', unit: 'V' },
      { id: 19, name: 'Check for leaks (fuel, oil, coolant)', type: 'visual', isRequired: true, standardValue: 'No leaks', unit: '' }
    ],
    references: [],
    status: 'active',
    createdBy: 'Mike Lim',
    createdAt: '2024-02-01',
    updatedAt: '2024-05-25',
    usedCount: 18,
    criticalCount: 4,
    complianceRate: 94
  },
  {
    id: 4,
    name: 'Chiller Quarterly Inspection',
    equipmentType: 'Chiller',
    frequency: 'quarterly',
    version: 2,
    description: 'Quarterly comprehensive inspection for chiller systems.',
    items: [
      { id: 20, name: 'Check evaporator pressure', type: 'measure', isRequired: true, standardValue: '60-80', unit: 'psi' },
      { id: 21, name: 'Check condenser pressure', type: 'measure', isRequired: true, standardValue: '180-220', unit: 'psi' },
      { id: 22, name: 'Inspect for refrigerant leaks', type: 'visual', isRequired: true, standardValue: 'No leaks', unit: '' },
      { id: 23, name: 'Check oil level and condition', type: 'visual', isRequired: true, standardValue: 'Normal', unit: '' }
    ],
    references: [],
    status: 'inactive',
    createdBy: 'Sarah Wong',
    createdAt: '2024-01-20',
    updatedAt: '2024-04-15',
    usedCount: 8,
    criticalCount: 2,
    complianceRate: 88
  },
  {
    id: 5,
    name: 'PDU Load Distribution Check',
    equipmentType: 'PDU',
    frequency: 'weekly',
    version: 1,
    description: 'Weekly PDU load monitoring and phase balance inspection.',
    items: [
      { id: 24, name: 'Check total load percentage', type: 'measure', isRequired: true, standardValue: '≤80', unit: '%' },
      { id: 25, name: 'Verify phase balance', type: 'measure', isRequired: true, standardValue: '±10', unit: '%' },
      { id: 26, name: 'Check for overload alarms', type: 'check', isRequired: true, standardValue: 'No alarms', unit: '' },
      { id: 27, name: 'Inspect circuit breakers', type: 'visual', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 28, name: 'Record voltage readings per phase', type: 'measure', isRequired: true, standardValue: '220-240', unit: 'V' }
    ],
    references: [
      { name: 'PDU User Manual', link: '/docs/pdu-manual.pdf' }
    ],
    status: 'active',
    createdBy: 'John Chen',
    createdAt: '2024-02-10',
    updatedAt: '2024-05-22',
    usedCount: 35,
    criticalCount: 3,
    complianceRate: 95
  },
  {
    id: 6,
    name: 'HVAC AHU Daily Checklist',
    equipmentType: 'HVAC',
    frequency: 'daily',
    version: 2,
    description: 'Daily Air Handling Unit inspection for optimal air quality and energy efficiency.',
    items: [
      { id: 29, name: 'Check supply fan operation', type: 'check', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 30, name: 'Check return fan operation', type: 'check', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 31, name: 'Inspect filter condition', type: 'visual', isRequired: true, standardValue: 'Clean', unit: '' },
      { id: 32, name: 'Check mixed air temperature', type: 'measure', isRequired: true, standardValue: '15-25', unit: '°C' },
      { id: 33, name: 'Check discharge air temperature', type: 'measure', isRequired: true, standardValue: '12-18', unit: '°C' },
      { id: 34, name: 'Record CO2 levels', type: 'measure', isRequired: false, standardValue: '≤1000', unit: 'ppm' },
      { id: 35, name: 'Check for unusual noise/vibration', type: 'check', isRequired: true, standardValue: 'None', unit: '' }
    ],
    references: [],
    status: 'active',
    createdBy: 'Ahmad Razak',
    createdAt: '2024-01-05',
    updatedAt: '2024-05-28',
    usedCount: 156,
    criticalCount: 5,
    complianceRate: 97
  },
  {
    id: 7,
    name: 'Transformer Oil & Temperature Check',
    equipmentType: 'Transformer',
    frequency: 'quarterly',
    version: 1,
    description: 'Quarterly transformer inspection focusing on oil quality and thermal performance.',
    items: [
      { id: 36, name: 'Check oil level in conservator', type: 'measure', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 37, name: 'Record top oil temperature', type: 'measure', isRequired: true, standardValue: '≤95', unit: '°C' },
      { id: 38, name: 'Record winding temperature', type: 'measure', isRequired: true, standardValue: '≤105', unit: '°C' },
      { id: 39, name: 'Check for oil leaks', type: 'visual', isRequired: true, standardValue: 'No leaks', unit: '' },
      { id: 40, name: 'Inspect bushings for cracks', type: 'visual', isRequired: true, standardValue: 'No cracks', unit: '' },
      { id: 41, name: 'Check cooling fans operation', type: 'check', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 42, name: 'Take oil sample for DGA', type: 'test', isRequired: true, standardValue: 'Lab analysis', unit: '' }
    ],
    references: [
      { name: 'Transformer Oil Testing Standard', link: '/docs/oil-testing.pdf' }
    ],
    status: 'active',
    createdBy: 'Mike Lim',
    createdAt: '2024-02-15',
    updatedAt: '2024-05-10',
    usedCount: 12,
    criticalCount: 5,
    complianceRate: 92
  },
  {
    id: 8,
    name: 'Fire Alarm System Weekly Test',
    equipmentType: 'Fire Alarm',
    frequency: 'weekly',
    version: 2,
    description: 'Weekly fire alarm system testing to ensure operational readiness.',
    items: [
      { id: 43, name: 'Check control panel status', type: 'check', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 44, name: 'Test smoke detector (random zone)', type: 'test', isRequired: true, standardValue: 'Trigger alarm', unit: '' },
      { id: 45, name: 'Test manual call point', type: 'test', isRequired: true, standardValue: 'Trigger alarm', unit: '' },
      { id: 46, name: 'Verify alarm bell/strobe operation', type: 'check', isRequired: true, standardValue: 'Working', unit: '' },
      { id: 47, name: 'Check battery backup', type: 'test', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 48, name: 'Record any fault signals', type: 'check', isRequired: true, standardValue: 'No faults', unit: '' }
    ],
    references: [
      { name: 'Fire Safety Regulations', link: '/docs/fire-safety.pdf' }
    ],
    status: 'active',
    createdBy: 'David Tan',
    createdAt: '2024-01-20',
    updatedAt: '2024-05-25',
    usedCount: 28,
    criticalCount: 5,
    complianceRate: 100
  },
  {
    id: 9,
    name: 'Cooling Tower Monthly Inspection',
    equipmentType: 'Cooling Tower',
    frequency: 'monthly',
    version: 1,
    description: 'Monthly cooling tower inspection for water treatment and mechanical integrity.',
    items: [
      { id: 49, name: 'Check water level in basin', type: 'measure', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 50, name: 'Inspect fan blades for damage', type: 'visual', isRequired: true, standardValue: 'No damage', unit: '' },
      { id: 51, name: 'Check motor bearing temperature', type: 'measure', isRequired: true, standardValue: '≤70', unit: '°C' },
      { id: 52, name: 'Inspect drift eliminators', type: 'visual', isRequired: true, standardValue: 'Clean', unit: '' },
      { id: 53, name: 'Check chemical dosing system', type: 'check', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 54, name: 'Measure conductivity of water', type: 'measure', isRequired: true, standardValue: '≤3000', unit: 'µS/cm' },
      { id: 55, name: 'Check for algae/slime growth', type: 'visual', isRequired: true, standardValue: 'None', unit: '' }
    ],
    references: [],
    status: 'active',
    createdBy: 'Sarah Wong',
    createdAt: '2024-03-01',
    updatedAt: '2024-05-20',
    usedCount: 9,
    criticalCount: 4,
    complianceRate: 93
  },
  {
    id: 10,
    name: 'Network Switch & Server Room Check',
    equipmentType: 'Network',
    frequency: 'daily',
    version: 3,
    description: 'Daily network equipment inspection for optimal data center operations.',
    items: [
      { id: 56, name: 'Check switch LED status', type: 'check', isRequired: true, standardValue: 'All green', unit: '' },
      { id: 57, name: 'Verify port link status', type: 'check', isRequired: true, standardValue: 'No errors', unit: '' },
      { id: 58, name: 'Check CPU utilization', type: 'measure', isRequired: true, standardValue: '≤70', unit: '%' },
      { id: 59, name: 'Check memory utilization', type: 'measure', isRequired: true, standardValue: '≤80', unit: '%' },
      { id: 60, name: 'Inspect cable management', type: 'visual', isRequired: false, standardValue: 'Organized', unit: '' },
      { id: 61, name: 'Check for error logs', type: 'check', isRequired: true, standardValue: 'No errors', unit: '' },
      { id: 62, name: 'Record ambient temperature', type: 'measure', isRequired: true, standardValue: '20-25', unit: '°C' }
    ],
    references: [],
    status: 'active',
    createdBy: 'Lisa Ng',
    createdAt: '2024-01-01',
    updatedAt: '2024-05-29',
    usedCount: 210,
    criticalCount: 5,
    complianceRate: 99
  },
  {
    id: 11,
    name: 'Water Pump & Valve Operational Check',
    equipmentType: 'Plumbing',
    frequency: 'weekly',
    version: 1,
    description: 'Weekly inspection of water pumps, valves, and piping systems.',
    items: [
      { id: 63, name: 'Check pump bearing temperature', type: 'measure', isRequired: true, standardValue: '≤75', unit: '°C' },
      { id: 64, name: 'Check pump vibration levels', type: 'check', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 65, name: 'Inspect for water leaks', type: 'visual', isRequired: true, standardValue: 'No leaks', unit: '' },
      { id: 66, name: 'Check valve position (open/close)', type: 'check', isRequired: true, standardValue: 'Correct', unit: '' },
      { id: 67, name: 'Record discharge pressure', type: 'measure', isRequired: true, standardValue: '4-6', unit: 'bar' },
      { id: 68, name: 'Check suction pressure', type: 'measure', isRequired: true, standardValue: '≥1', unit: 'bar' },
      { id: 69, name: 'Inspect coupling alignment', type: 'visual', isRequired: true, standardValue: 'Aligned', unit: '' }
    ],
    references: [],
    status: 'inactive',
    createdBy: 'David Tan',
    createdAt: '2024-02-20',
    updatedAt: '2024-04-01',
    usedCount: 5,
    criticalCount: 4,
    complianceRate: 85
  },
  {
    id: 12,
    name: 'Battery Room Safety & Ventilation',
    equipmentType: 'Battery',
    frequency: 'weekly',
    version: 2,
    description: 'Weekly safety inspection of battery room including ventilation and emergency equipment.',
    items: [
      { id: 70, name: 'Check hydrogen gas detector', type: 'check', isRequired: true, standardValue: 'Normal', unit: '' },
      { id: 71, name: 'Verify ventilation fan operation', type: 'check', isRequired: true, standardValue: 'Running', unit: '' },
      { id: 72, name: 'Check emergency eyewash station', type: 'check', isRequired: true, standardValue: 'Functional', unit: '' },
      { id: 73, name: 'Inspect for acid spills', type: 'visual', isRequired: true, standardValue: 'None', unit: '' },
      { id: 74, name: 'Check battery terminal corrosion', type: 'visual', isRequired: true, standardValue: 'None', unit: '' },
      { id: 75, name: 'Record room temperature', type: 'measure', isRequired: true, standardValue: '20-25', unit: '°C' },
      { id: 76, name: 'Check PPE availability', type: 'check', isRequired: true, standardValue: 'Available', unit: '' },
      { id: 77, name: 'Inspect fire extinguisher', type: 'check', isRequired: true, standardValue: 'Green tag', unit: '' }
    ],
    references: [
      { name: 'Battery Safety Handbook', link: '/docs/battery-safety.pdf' },
      { name: 'OSHA Battery Room Standards', link: '/docs/osha-battery.pdf' }
    ],
    status: 'active',
    createdBy: 'John Chen',
    createdAt: '2024-03-10',
    updatedAt: '2024-05-15',
    usedCount: 16,
    criticalCount: 7,
    complianceRate: 96
  }
])

// ==================== State ====================
const searchText = ref('')
const equipmentTypeFilter = ref('')
const statusFilter = ref('')
const dialogVisible = ref(false)
const viewDialogVisible = ref(false)
const dialogTitle = ref('Create Checklist Template')
const viewTemplateData = ref<ChecklistTemplate | null>(null)
const editingTemplate = ref<ChecklistTemplate | null>(null)
const formRef = ref()

const checklistForm = ref({
  id: null as number | null,
  name: '',
  equipmentType: '',
  frequency: 'monthly',
  description: '',
  status: 'active' as 'active' | 'inactive',
  items: [] as ChecklistItem[],
  references: [] as Reference[]
})

const formRules = {
  name: [{ required: true, message: 'Please enter template name', trigger: 'blur' }],
  equipmentType: [{ required: true, message: 'Please select equipment type', trigger: 'change' }]
}

// ==================== Computed ====================
const lastUpdated = computed(() => {
  const dates = checklistTemplates.value.map(t => new Date(t.updatedAt))
  const latest = new Date(Math.max(...dates.map(d => d.getTime())))
  return latest.toLocaleDateString()
})

const stats = computed(() => ({
  totalTemplates: checklistTemplates.value.length,
  activeTemplates: checklistTemplates.value.filter(t => t.status === 'active').length,
  totalItems: checklistTemplates.value.reduce((sum, t) => sum + t.items.length, 0),
  complianceRate: Math.round(checklistTemplates.value.reduce((sum, t) => sum + t.complianceRate, 0) / checklistTemplates.value.length)
}))

const filteredTemplates = computed(() => {
  let filtered = [...checklistTemplates.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(search) ||
        t.equipmentType.toLowerCase().includes(search)
    )
  }

  if (equipmentTypeFilter.value) {
    filtered = filtered.filter(t => t.equipmentType === equipmentTypeFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(t => t.status === statusFilter.value)
  }

  return filtered
})

// ==================== Helper Functions ====================
const getEquipmentTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    UPS: 'ups', CRAC: 'crac', PDU: 'pdu',
    Chiller: 'chiller', Generator: 'generator', HVAC: 'hvac', Transformer: 'transformer'
  }
  return colors[type] || 'default'
}

const getProgressColor = (rate: number) => {
  if (rate >= 95) return '#67c23a'
  if (rate >= 85) return '#e6a23c'
  return '#f56c6c'
}

const getFrequencyText = (frequency: string) => {
  const map: Record<string, string> = {
    daily: 'Daily', weekly: 'Weekly', monthly: 'Monthly', quarterly: 'Quarterly', yearly: 'Yearly'
  }
  return map[frequency] || frequency
}

const getItemTypeText = (type: string) => {
  const map: Record<string, string> = {
    check: 'Check', measure: 'Measure', visual: 'Visual', test: 'Test'
  }
  return map[type] || type
}

const getItemTypeTag = (type: string) => {
  const map: Record<string, string> = {
    check: 'success', measure: 'primary', visual: 'info', test: 'warning'
  }
  return map[type] || ''
}

// ==================== CRUD Methods ====================
const openCreateDialog = () => {
  dialogTitle.value = 'Create Checklist Template'
  editingTemplate.value = null
  checklistForm.value = {
    id: null,
    name: '',
    equipmentType: '',
    frequency: 'monthly',
    description: '',
    status: 'active',
    items: [],
    references: []
  }
  dialogVisible.value = true
}

const editTemplate = (template: ChecklistTemplate) => {
  dialogTitle.value = 'Edit Checklist Template'
  editingTemplate.value = template
  checklistForm.value = {
    id: template.id,
    name: template.name,
    equipmentType: template.equipmentType,
    frequency: template.frequency,
    description: template.description,
    status: template.status,
    items: JSON.parse(JSON.stringify(template.items)),
    references: JSON.parse(JSON.stringify(template.references || []))
  }
  dialogVisible.value = true
}

const viewTemplate = (template: ChecklistTemplate) => {
  viewTemplateData.value = template
  viewDialogVisible.value = true
}

const editFromView = () => {
  if (viewTemplateData.value) {
    viewDialogVisible.value = false
    editTemplate(viewTemplateData.value)
  }
}

const duplicateTemplate = (template: ChecklistTemplate) => {
  const newTemplate = {
    ...JSON.parse(JSON.stringify(template)),
    id: Math.max(...checklistTemplates.value.map(t => t.id), 0) + 1,
    name: `${template.name} (Copy)`,
    version: 1,
    createdBy: 'Current User',
    createdAt: new Date().toISOString().slice(0, 10),
    updatedAt: new Date().toISOString().slice(0, 10),
    usedCount: 0
  }
  checklistTemplates.value.push(newTemplate)
  ElMessage.success('Template duplicated')
}

const deleteTemplate = (template: ChecklistTemplate) => {
  ElMessageBox.confirm(
      `Delete checklist "${template.name}"? This action cannot be undone.`,
      'Confirm Delete',
      { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    const index = checklistTemplates.value.findIndex(t => t.id === template.id)
    if (index !== -1) {
      checklistTemplates.value.splice(index, 1)
      ElMessage.success('Template deleted')
    }
  }).catch(() => {})
}

const exportTemplate = (template: ChecklistTemplate) => {
  ElMessage.success(`Exporting ${template.name}...`)
  setTimeout(() => {
    ElMessage.success('Export completed')
  }, 1000)
}

const handleMenuCommand = (command: string, template: ChecklistTemplate) => {
  switch (command) {
    case 'view': viewTemplate(template); break
    case 'edit': editTemplate(template); break
    case 'duplicate': duplicateTemplate(template); break
    case 'export': exportTemplate(template); break
    case 'delete': deleteTemplate(template); break
  }
}

const addChecklistItem = () => {
  checklistForm.value.items.push({
    id: Date.now(),
    name: '',
    type: 'check',
    isRequired: true,
    standardValue: '',
    unit: ''
  })
}

const removeChecklistItem = (index: number) => {
  checklistForm.value.items.splice(index, 1)
}

const addReference = () => {
  checklistForm.value.references.push({ name: '', link: '' })
}

const removeReference = (index: number) => {
  checklistForm.value.references.splice(index, 1)
}

const saveChecklist = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    if (editingTemplate.value) {
      // Update existing
      const index = checklistTemplates.value.findIndex(t => t.id === editingTemplate.value!.id)
      if (index !== -1) {
        checklistTemplates.value[index] = {
          ...checklistTemplates.value[index],
          name: checklistForm.value.name,
          equipmentType: checklistForm.value.equipmentType,
          frequency: checklistForm.value.frequency,
          description: checklistForm.value.description,
          status: checklistForm.value.status,
          items: checklistForm.value.items,
          references: checklistForm.value.references,
          updatedAt: new Date().toISOString().slice(0, 10)
        }
        ElMessage.success('Template updated')
      }
    } else {
      // Create new
      const criticalCount = checklistForm.value.items.filter(i => i.isRequired).length
      const newId = Math.max(...checklistTemplates.value.map(t => t.id), 0) + 1
      checklistTemplates.value.push({
        id: newId,
        name: checklistForm.value.name,
        equipmentType: checklistForm.value.equipmentType,
        frequency: checklistForm.value.frequency,
        version: 1,
        description: checklistForm.value.description,
        items: checklistForm.value.items,
        references: checklistForm.value.references,
        status: checklistForm.value.status,
        createdBy: 'Current User',
        createdAt: new Date().toISOString().slice(0, 10),
        updatedAt: new Date().toISOString().slice(0, 10),
        usedCount: 0,
        criticalCount: criticalCount,
        complianceRate: 100
      })
      ElMessage.success('Template created')
    }

    dialogVisible.value = false
  })
}

const exportData = () => {
  ElMessage.success('Export started')
  setTimeout(() => {
    ElMessage.success('All checklist templates exported')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

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
.inspection-checklist-page {
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

/* Checklist Grid */
.checklist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
}

.checklist-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.checklist-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.1);
}

.checklist-card.inactive {
  opacity: 0.7;
  background: #fafcff;
}

/* Card Header */
.card-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid #eef2f8;
}

.header-left {
  display: flex;
  gap: 14px;
}

.template-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.template-icon.ups { background: #eef2ff; color: #3b82f6; }
.template-icon.crac { background: #dcfce7; color: #22c55e; }
.template-icon.pdu { background: #fef3c7; color: #f59e0b; }
.template-icon.chiller { background: #e0e7ff; color: #4f46e5; }
.template-icon.generator { background: #fee2e2; color: #ef4444; }
.template-icon.hvac { background: #f3e8ff; color: #8b5cf6; }
.template-icon.transformer { background: #fef3c7; color: #d97706; }
.template-icon.default { background: #f1f5f9; color: #64748b; }

.template-name {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 4px;
}

.template-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
}

.equipment-type {
  color: #3b82f6;
  background: #eef2ff;
  padding: 2px 8px;
  border-radius: 12px;
}

.version {
  color: #64748b;
}

/* Card Stats */
.card-stats {
  padding: 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #eef2f8;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.stat {
  text-align: center;
  flex: 1;
}

.stat-label-sm {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.stat-value-sm {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.stat-value-sm.critical {
  color: #ef4444;
}

.progress-row {
  margin-top: 8px;
}

.progress-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 6px;
}

/* Card Preview */
.card-preview {
  padding: 16px 20px;
  border-bottom: 1px solid #eef2f8;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.preview-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #475569;
}

.preview-item .required {
  color: #ef4444;
}

.preview-item .optional {
  color: #94a3b8;
}

/* Card Footer */
.card-footer {
  padding: 14px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
}

.footer-info {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #64748b;
}

.footer-info span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  padding: 60px;
  background: white;
  border-radius: 20px;
  text-align: center;
}

/* Dialog Styles */
.checklist-dialog :deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 28px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #eef2f8;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Items Table */
.items-table {
  border: 1px solid #eef2f8;
  border-radius: 12px;
  overflow: hidden;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-bottom: 1px solid #eef2f8;
  background: #fafcff;
}

.item-row:last-child {
  border-bottom: none;
}

.item-order {
  width: 32px;
  font-weight: 600;
  color: #64748b;
}

.item-name {
  flex: 2;
}

.item-type {
  width: 100px;
}

.item-required {
  width: 80px;
}

.item-standard {
  width: 130px;
}

.item-unit {
  width: 70px;
}

.item-actions {
  width: 40px;
}

.empty-items {
  padding: 20px;
  text-align: center;
}

/* References List */
.references-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reference-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* View Dialog */
.view-dialog :deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}

.view-section {
  margin-bottom: 24px;
}

.view-section-title {
  font-weight: 600;
  font-size: 15px;
  color: #1e293b;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #3b82f6;
}

.view-items-table {
  border: 1px solid #eef2f8;
  border-radius: 12px;
  overflow: hidden;
}

.view-items-header,
.view-items-row {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #eef2f8;
}

.view-items-header {
  background: #f8fafc;
  font-weight: 600;
  font-size: 12px;
  color: #1e293b;
}

.view-items-row {
  background: white;
}

.col-order { width: 50px; }
.col-name { flex: 2; }
.col-type { width: 100px; }
.col-standard { width: 150px; }
.col-required { width: 90px; }

.view-references {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reference-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 10px;
}

/* Responsive */
@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .checklist-grid {
    grid-template-columns: 1fr;
  }

  .item-row {
    flex-wrap: wrap;
  }

  .item-order, .item-name, .item-type, .item-required, .item-standard, .item-unit {
    width: auto;
    flex: auto;
  }
}

@media (max-width: 600px) {
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