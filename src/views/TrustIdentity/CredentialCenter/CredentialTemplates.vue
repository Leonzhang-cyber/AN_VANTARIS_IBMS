<template>
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Trust & Identity - Credential Templates</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="credential-templates-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Credential Templates</h1>
        <p>Create and manage verifiable credential templates with custom schemas and claims</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          Create Template
        </el-button>
        <el-button @click="importTemplate">
          <el-icon><Upload /></el-icon>
          Import Template
        </el-button>
        <el-button @click="exportTemplates">
          <el-icon><Download /></el-icon>
          Export All
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalTemplates }}</div>
            <div class="stat-label">Total Templates</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeTemplates }}</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.draftTemplates }}</div>
            <div class="stat-label">In Draft</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalIssuedFromTemplates }}</div>
            <div class="stat-label">Credentials Issued</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Search and Filter -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search templates by name or schema..."
          clearable
          style="width: 280px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All Status" value="" />
        <el-option label="Active" value="active" />
        <el-option label="Draft" value="draft" />
        <el-option label="Archived" value="archived" />
      </el-select>
      <el-select v-model="filters.category" placeholder="Category" clearable style="width: 160px">
        <el-option label="All Categories" value="" />
        <el-option label="Identity" value="identity" />
        <el-option label="Certification" value="certification" />
        <el-option label="Compliance" value="compliance" />
        <el-option label="Access" value="access" />
      </el-select>
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply Filters
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- Templates Grid -->
    <div class="templates-grid-wrapper">
      <div class="grid-header">
        <span class="grid-title">Credential Templates</span>
        <div class="grid-view-toggle">
          <el-button-group>
            <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" @click="viewMode = 'grid'">
              <el-icon><Grid /></el-icon>
            </el-button>
            <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
              <el-icon><List /></el-icon>
            </el-button>
          </el-button-group>
        </div>
      </div>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="templates-grid">
        <div
            v-for="template in filteredTemplates"
            :key="template.id"
            class="template-card"
            :class="{ 'status-draft': template.status === 'draft', 'status-archived': template.status === 'archived' }"
        >
          <div class="template-header">
            <div class="template-icon" :class="getTemplateIconClass(template.category)">
              <el-icon><component :is="getTemplateIcon(template.category)" /></el-icon>
            </div>
            <div class="template-status">
              <el-tag :type="template.status === 'active' ? 'success' : template.status === 'draft' ? 'warning' : 'info'" size="small">
                {{ template.status === 'active' ? 'Active' : template.status === 'draft' ? 'Draft' : 'Archived' }}
              </el-tag>
            </div>
          </div>
          <div class="template-body">
            <h3 class="template-name">{{ template.name }}</h3>
            <p class="template-description">{{ template.description }}</p>
            <div class="template-meta">
              <div class="meta-item">
                <el-icon><Document /></el-icon>
                <span>{{ template.fields.length }} fields</span>
              </div>
              <div class="meta-item">
                <el-icon><DataAnalysis /></el-icon>
                <span>v{{ template.version }}</span>
              </div>
              <div class="meta-item">
                <el-icon><TrendCharts /></el-icon>
                <span>{{ template.issuedCount }} issued</span>
              </div>
            </div>
            <div class="template-schema">
              <el-tooltip :content="template.schema" placement="top">
                <span class="schema-preview">{{ truncateSchema(template.schema) }}</span>
              </el-tooltip>
            </div>
          </div>
          <div class="template-footer">
            <el-button
                :type="template.status === 'active' ? 'danger' : 'success'"
                size="small"
                @click="toggleTemplateStatus(template)"
            >
              <el-icon><component :is="template.status === 'active' ? 'CircleClose' : 'CircleCheck'" /></el-icon>
              {{ template.status === 'active' ? 'Deactivate' : 'Activate' }}
            </el-button>
            <el-button size="small" @click="editTemplate(template)">
              <el-icon><Edit /></el-icon>
              Edit
            </el-button>
            <el-button size="small" type="primary" @click="useTemplate(template)">
              <el-icon><Plus /></el-icon>
              Use
            </el-button>
            <el-dropdown trigger="click" @command="(cmd) => handleDropdown(cmd, template)">
              <el-button size="small">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="duplicate">
                    <el-icon><CopyDocument /></el-icon>
                    Duplicate
                  </el-dropdown-item>
                  <el-dropdown-item command="export">
                    <el-icon><Download /></el-icon>
                    Export Template
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>
                    <span style="color: #f56c6c">
                      <el-icon><Delete /></el-icon>
                      Delete
                    </span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="templates-list">
        <el-table :data="filteredTemplates" stripe style="width: 100%">
          <el-table-column prop="name" label="Template Name" min-width="200">
            <template #default="{ row }">
              <div class="list-name-cell">
                <div class="list-icon" :class="getTemplateIconClass(row.category)">
                  <el-icon><component :is="getTemplateIcon(row.category)" /></el-icon>
                </div>
                <div>
                  <div class="list-name">{{ row.name }}</div>
                  <div class="list-schema">{{ truncateSchema(row.schema, 50) }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
          <el-table-column prop="category" label="Category" width="120">
            <template #default="{ row }">
              <el-tag size="small">{{ formatCategory(row.category) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="version" label="Version" width="80" />
          <el-table-column prop="fields.length" label="Fields" width="80" />
          <el-table-column prop="issuedCount" label="Issued" width="80" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : row.status === 'draft' ? 'warning' : 'info'" size="small">
                {{ row.status === 'active' ? 'Active' : row.status === 'draft' ? 'Draft' : 'Archived' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updatedAt" label="Updated" width="110" />
          <el-table-column label="Actions" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="editTemplate(row)">
                Edit
              </el-button>
              <el-button
                  link
                  :type="row.status === 'active' ? 'danger' : 'success'"
                  size="small"
                  @click="toggleTemplateStatus(row)"
              >
                {{ row.status === 'active' ? 'Deactivate' : 'Activate' }}
              </el-button>
              <el-button link type="primary" size="small" @click="useTemplate(row)">
                Use
              </el-button>
              <el-dropdown trigger="click" @command="(cmd) => handleDropdown(cmd, row)">
                <el-button link size="small">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="duplicate">Duplicate</el-dropdown-item>
                    <el-dropdown-item command="export">Export</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[12, 24, 48]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Create/Edit Template Dialog -->
    <el-dialog
        v-model="dialog.visible"
        :title="dialog.isEdit ? 'Edit Credential Template' : 'Create Credential Template'"
        width="750px"
        class="template-dialog"
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="130px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Template Name" prop="name">
              <el-input v-model="form.name" placeholder="Enter template name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Category" prop="category">
              <el-select v-model="form.category" placeholder="Select category" style="width: 100%">
                <el-option label="Identity" value="identity" />
                <el-option label="Certification" value="certification" />
                <el-option label="Compliance" value="compliance" />
                <el-option label="Access" value="access" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="Description" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="Describe the purpose of this credential" />
        </el-form-item>

        <el-form-item label="Schema URL" prop="schema">
          <el-input v-model="form.schema" placeholder="https://schema.org/..." />
          <div class="form-hint">W3C-compliant schema URL for this credential type</div>
        </el-form-item>

        <el-form-item label="Version" prop="version">
          <el-input v-model="form.version" placeholder="1.0.0" style="width: 150px" />
        </el-form-item>

        <el-divider content-position="left">Credential Claims / Fields</el-divider>

        <div class="fields-editor">
          <div v-for="(field, index) in form.fields" :key="index" class="field-item">
            <div class="field-header">
              <span class="field-number">Field {{ index + 1 }}</span>
              <el-button link type="danger" @click="removeField(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-row :gutter="12">
              <el-col :span="8">
                <el-input v-model="field.name" placeholder="Field name" size="small" />
              </el-col>
              <el-col :span="6">
                <el-select v-model="field.type" placeholder="Type" size="small" style="width: 100%">
                  <el-option label="String" value="string" />
                  <el-option label="Number" value="number" />
                  <el-option label="Boolean" value="boolean" />
                  <el-option label="Date" value="date" />
                  <el-option label="DateTime" value="datetime" />
                  <el-option label="URL" value="url" />
                  <el-option label="Email" value="email" />
                </el-select>
              </el-col>
              <el-col :span="6">
                <el-checkbox v-model="field.required">Required</el-checkbox>
              </el-col>
              <el-col :span="4">
                <el-input v-if="field.type === 'string'" v-model="field.defaultValue" placeholder="Default" size="small" />
              </el-col>
            </el-row>
            <el-input
                v-if="field.type === 'string' && field.options"
                v-model="field.options"
                placeholder="Options (comma separated)"
                size="small"
                style="margin-top: 8px"
            />
          </div>
          <el-button type="primary" link @click="addField" style="margin-top: 12px">
            <el-icon><Plus /></el-icon>
            Add Field
          </el-button>
        </div>

        <el-divider />

        <el-form-item label="Status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">Active (Ready to use)</el-radio>
            <el-radio value="draft">Draft (Save for later)</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTemplate">Save Template</el-button>
      </template>
    </el-dialog>

    <!-- JSON Schema Preview Dialog -->
    <el-dialog v-model="schemaDialog.visible" title="JSON Schema Preview" width="650px">
      <div class="json-preview">
        <pre>{{ JSON.stringify(schemaDialog.schema, null, 2) }}</pre>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus,
  Upload,
  Download,
  Document,
  CircleCheck,
  Clock,
  DataAnalysis,
  Search,
  RefreshLeft,
  Grid,
  List,
  Edit,
  MoreFilled,
  CopyDocument,
  Delete,
  TrendCharts,
  User,
  Tools,
  Warning,
  Key,
  CircleClose
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading credential templates...',
  'Initializing schema validator...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface TemplateField {
  name: string
  label: string
  type: string
  required: boolean
  defaultValue?: string
  options?: string
}

interface CredentialTemplate {
  id: string
  name: string
  description: string
  category: string
  schema: string
  version: string
  status: 'active' | 'draft' | 'archived'
  fields: TemplateField[]
  issuedCount: number
  createdAt: string
  updatedAt: string
  createdBy: string
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalTemplates: 12,
  activeTemplates: 8,
  draftTemplates: 3,
  totalIssuedFromTemplates: 1248
})

const templates = ref<CredentialTemplate[]>([
  {
    id: 'tmpl_001',
    name: 'Employee Identity',
    description: 'Verifiable credential for employee identity verification with role and department information',
    category: 'identity',
    schema: 'https://schema.org/EmployeeRole',
    version: '1.2.0',
    status: 'active',
    fields: [
      { name: 'employeeId', label: 'Employee ID', type: 'string', required: true },
      { name: 'position', label: 'Position', type: 'string', required: true },
      { name: 'department', label: 'Department', type: 'string', required: true },
      { name: 'hireDate', label: 'Hire Date', type: 'date', required: true },
      { name: 'clearanceLevel', label: 'Clearance Level', type: 'string', required: false }
    ],
    issuedCount: 456,
    createdAt: '2024-01-15',
    updatedAt: '2024-05-20',
    createdBy: 'admin@ibms.com'
  },
  {
    id: 'tmpl_002',
    name: 'Equipment Certification',
    description: 'Credential for equipment safety certification and maintenance compliance',
    category: 'certification',
    schema: 'https://schema.org/Certification',
    version: '1.0.0',
    status: 'active',
    fields: [
      { name: 'equipmentId', label: 'Equipment ID', type: 'string', required: true },
      { name: 'certificationType', label: 'Certification Type', type: 'string', required: true },
      { name: 'inspectorName', label: 'Inspector Name', type: 'string', required: true },
      { name: 'complianceStatus', label: 'Compliance Status', type: 'string', required: true },
      { name: 'remarks', label: 'Remarks', type: 'string', required: false }
    ],
    issuedCount: 234,
    createdAt: '2024-02-10',
    updatedAt: '2024-06-01',
    createdBy: 'admin@ibms.com'
  },
  {
    id: 'tmpl_003',
    name: 'Compliance Attestation',
    description: 'Regulatory compliance and standards attestation credential',
    category: 'compliance',
    schema: 'https://schema.org/Compliance',
    version: '1.1.0',
    status: 'active',
    fields: [
      { name: 'standard', label: 'Standard', type: 'string', required: true },
      { name: 'complianceScore', label: 'Compliance Score', type: 'number', required: true },
      { name: 'auditorName', label: 'Auditor Name', type: 'string', required: true },
      { name: 'auditDate', label: 'Audit Date', type: 'date', required: true },
      { name: 'recommendations', label: 'Recommendations', type: 'string', required: false }
    ],
    issuedCount: 189,
    createdAt: '2024-01-20',
    updatedAt: '2024-05-15',
    createdBy: 'admin@ibms.com'
  },
  {
    id: 'tmpl_004',
    name: 'Access Credential',
    description: 'Access control credential for building zones and restricted areas',
    category: 'access',
    schema: 'https://schema.org/AccessCredential',
    version: '2.0.0',
    status: 'active',
    fields: [
      { name: 'accessLevel', label: 'Access Level', type: 'string', required: true },
      { name: 'zones', label: 'Accessible Zones', type: 'string', required: true },
      { name: 'issuedBy', label: 'Issuing Authority', type: 'string', required: true }
    ],
    issuedCount: 369,
    createdAt: '2024-03-05',
    updatedAt: '2024-06-10',
    createdBy: 'security@ibms.com'
  },
  {
    id: 'tmpl_005',
    name: 'Training Completion',
    description: 'Credential for employee training and course completion',
    category: 'identity',
    schema: 'https://schema.org/EducationalOccupationalCredential',
    version: '1.0.0',
    status: 'draft',
    fields: [
      { name: 'courseName', label: 'Course Name', type: 'string', required: true },
      { name: 'completionDate', label: 'Completion Date', type: 'date', required: true },
      { name: 'score', label: 'Score', type: 'number', required: false },
      { name: 'instructor', label: 'Instructor', type: 'string', required: false }
    ],
    issuedCount: 0,
    createdAt: '2024-06-01',
    updatedAt: '2024-06-01',
    createdBy: 'admin@ibms.com'
  },
  {
    id: 'tmpl_006',
    name: 'Vendor Qualification',
    description: 'Credential for vendor and contractor qualification verification',
    category: 'compliance',
    schema: 'https://schema.org/Qualification',
    version: '1.0.0',
    status: 'active',
    fields: [
      { name: 'vendorId', label: 'Vendor ID', type: 'string', required: true },
      { name: 'qualificationType', label: 'Qualification Type', type: 'string', required: true },
      { name: 'expiryDate', label: 'Expiry Date', type: 'date', required: true },
      { name: 'approvedBy', label: 'Approved By', type: 'string', required: true }
    ],
    issuedCount: 0,
    createdAt: '2024-05-20',
    updatedAt: '2024-05-20',
    createdBy: 'procurement@ibms.com'
  }
])

const viewMode = ref<'grid' | 'list'>('grid')
const formRef = ref<FormInstance>()

const filters = reactive({
  search: '',
  status: '',
  category: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 12,
  total: 0
})

const dialog = reactive({
  visible: false,
  isEdit: false,
  editId: ''
})

const schemaDialog = reactive({
  visible: false,
  schema: null as any
})

const form = reactive({
  name: '',
  description: '',
  category: '',
  schema: '',
  version: '',
  status: 'active' as 'active' | 'draft',
  fields: [] as TemplateField[]
})

const formRules: FormRules = {
  name: [{ required: true, message: 'Template name is required', trigger: 'blur' }],
  description: [{ required: true, message: 'Description is required', trigger: 'blur' }],
  category: [{ required: true, message: 'Category is required', trigger: 'change' }],
  schema: [{ required: true, message: 'Schema URL is required', trigger: 'blur' }],
  version: [{ required: true, message: 'Version is required', trigger: 'blur' }]
}

// ==================== 计算属性 ====================
const filteredTemplates = computed(() => {
  let filtered = [...templates.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(searchLower) ||
        t.description.toLowerCase().includes(searchLower) ||
        t.schema.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(t => t.status === filters.status)
  }

  if (filters.category) {
    filtered = filtered.filter(t => t.category === filters.category)
  }

  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== 辅助函数 ====================
const getTemplateIcon = (category: string) => {
  const map: Record<string, any> = {
    'identity': User,
    'certification': Tools,
    'compliance': Warning,
    'access': Key
  }
  return map[category] || Document
}

const getTemplateIconClass = (category: string) => {
  const map: Record<string, string> = {
    'identity': 'identity',
    'certification': 'certification',
    'compliance': 'compliance',
    'access': 'access'
  }
  return map[category] || 'default'
}

const formatCategory = (category: string) => {
  const map: Record<string, string> = {
    'identity': 'Identity',
    'certification': 'Certification',
    'compliance': 'Compliance',
    'access': 'Access'
  }
  return map[category] || category
}

const truncateSchema = (schema: string, maxLength = 40) => {
  if (schema.length <= maxLength) return schema
  return schema.substring(0, maxLength) + '...'
}

const addField = () => {
  form.fields.push({
    name: '',
    label: '',
    type: 'string',
    required: false,
    defaultValue: '',
    options: ''
  })
}

const removeField = (index: number) => {
  form.fields.splice(index, 1)
}

const resetForm = () => {
  form.name = ''
  form.description = ''
  form.category = ''
  form.schema = ''
  form.version = ''
  form.status = 'active'
  form.fields = []
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.category = ''
  pagination.currentPage = 1
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const openCreateDialog = () => {
  dialog.isEdit = false
  resetForm()
  dialog.visible = true
  nextTick(() => {
    addField()
    addField()
    addField()
  })
}

const editTemplate = (template: CredentialTemplate) => {
  dialog.isEdit = true
  dialog.editId = template.id
  form.name = template.name
  form.description = template.description
  form.category = template.category
  form.schema = template.schema
  form.version = template.version
  form.status = template.status
  form.fields = JSON.parse(JSON.stringify(template.fields))
  dialog.visible = true
}

const saveTemplate = async () => {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      if (dialog.isEdit) {
        const index = templates.value.findIndex(t => t.id === dialog.editId)
        if (index !== -1) {
          templates.value[index] = {
            ...templates.value[index],
            name: form.name,
            description: form.description,
            category: form.category,
            schema: form.schema,
            version: form.version,
            status: form.status,
            fields: form.fields,
            updatedAt: new Date().toISOString().slice(0, 10)
          }
          ElMessage.success('Template updated successfully')
        }
      } else {
        const newTemplate: CredentialTemplate = {
          id: `tmpl_${String(templates.value.length + 1).padStart(3, '0')}`,
          name: form.name,
          description: form.description,
          category: form.category,
          schema: form.schema,
          version: form.version,
          status: form.status,
          fields: form.fields,
          issuedCount: 0,
          createdAt: new Date().toISOString().slice(0, 10),
          updatedAt: new Date().toISOString().slice(0, 10),
          createdBy: 'admin@ibms.com'
        }
        templates.value.unshift(newTemplate)
        stats.totalTemplates++
        if (form.status === 'active') stats.activeTemplates++
        else stats.draftTemplates++
        ElMessage.success('Template created successfully')
      }
      dialog.visible = false
      resetForm()
    }
  })
}

const toggleTemplateStatus = (template: CredentialTemplate) => {
  const newStatus = template.status === 'active' ? 'archived' : 'active'
  template.status = newStatus
  if (newStatus === 'active') {
    stats.activeTemplates++
    stats.draftTemplates--
  } else {
    stats.activeTemplates--
    stats.draftTemplates++
  }
  ElMessage.success(`Template ${newStatus === 'active' ? 'activated' : 'deactivated'}`)
}

const useTemplate = (template: CredentialTemplate) => {
  ElMessage.info(`Using template: ${template.name} - Redirecting to issue credential page`)
  // In a real app, navigate to issue credential page with template pre-filled
}

const duplicateTemplate = (template: CredentialTemplate) => {
  const newTemplate: CredentialTemplate = {
    ...template,
    id: `tmpl_${String(templates.value.length + 1).padStart(3, '0')}`,
    name: `${template.name} (Copy)`,
    issuedCount: 0,
    status: 'draft',
    createdAt: new Date().toISOString().slice(0, 10),
    updatedAt: new Date().toISOString().slice(0, 10)
  }
  templates.value.unshift(newTemplate)
  stats.totalTemplates++
  stats.draftTemplates++
  ElMessage.success('Template duplicated')
}

const exportTemplate = (template: CredentialTemplate) => {
  const data = JSON.stringify(template, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${template.name.replace(/\s/g, '_')}_template.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Template exported')
}

const deleteTemplate = async (template: CredentialTemplate) => {
  try {
    await ElMessageBox.confirm(
        `Are you sure you want to delete "${template.name}"? This action cannot be undone.`,
        'Confirm Delete',
        { confirmButtonText: 'Delete', type: 'warning' }
    )
    const index = templates.value.findIndex(t => t.id === template.id)
    if (index !== -1) {
      templates.value.splice(index, 1)
      stats.totalTemplates--
      if (template.status === 'active') stats.activeTemplates--
      else if (template.status === 'draft') stats.draftTemplates--
      ElMessage.success('Template deleted')
    }
  } catch {
    // User cancelled
  }
}

const handleDropdown = (command: string, template: CredentialTemplate) => {
  switch (command) {
    case 'duplicate':
      duplicateTemplate(template)
      break
    case 'export':
      exportTemplate(template)
      break
    case 'delete':
      deleteTemplate(template)
      break
  }
}

const importTemplate = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e: any) => {
    if (e.target.files?.[0]) {
      const reader = new FileReader()
      reader.onload = (ev) => {
        try {
          const imported = JSON.parse(ev.target?.result as string)
          if (imported.name && imported.schema) {
            const newTemplate: CredentialTemplate = {
              ...imported,
              id: `tmpl_${String(templates.value.length + 1).padStart(3, '0')}`,
              issuedCount: 0,
              createdAt: new Date().toISOString().slice(0, 10),
              updatedAt: new Date().toISOString().slice(0, 10),
              createdBy: 'admin@ibms.com'
            }
            templates.value.unshift(newTemplate)
            stats.totalTemplates++
            if (newTemplate.status === 'active') stats.activeTemplates++
            else stats.draftTemplates++
            ElMessage.success('Template imported successfully')
          } else {
            ElMessage.error('Invalid template file')
          }
        } catch {
          ElMessage.error('Failed to parse template file')
        }
      }
      reader.readAsText(e.target.files[0])
    }
  }
  input.click()
}

const exportTemplates = () => {
  const exportData = {
    exportedAt: new Date().toISOString(),
    totalTemplates: templates.value.length,
    templates: templates.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `credential-templates-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('All templates exported')
}

// ==================== 数据加载 ====================
const loadData = () => {
  // Data already loaded
}

// ==================== 生命周期 ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      loadData()
    }, 400)
  }, 2000)
})
</script>

<style scoped>
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

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

/* ==================== Main Content Styles ==================== */
.credential-templates-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Cards */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Templates Grid */
.templates-grid-wrapper {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.grid-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.template-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  overflow: hidden;
  transition: all 0.2s;
}

.template-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.template-card.status-draft {
  border-left: 3px solid #e6a23c;
}

.template-card.status-archived {
  opacity: 0.7;
  border-left: 3px solid #909399;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 0 16px;
}

.template-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.template-icon.identity { background-color: #ecf5ff; color: #409eff; }
.template-icon.certification { background-color: #f0f9eb; color: #67c23a; }
.template-icon.compliance { background-color: #fff3e0; color: #e6a23c; }
.template-icon.access { background-color: #fef0f0; color: #f56c6c; }

.template-body {
  padding: 16px;
}

.template-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.template-description {
  font-size: 13px;
  color: #5e6e82;
  margin-bottom: 12px;
  line-height: 1.4;
}

.template-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #8c9aab;
}

.meta-item .el-icon {
  font-size: 12px;
}

.template-schema {
  background: #f5f7fa;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-family: monospace;
  color: #409eff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.template-footer {
  display: flex;
  gap: 8px;
  padding: 12px 16px 16px 16px;
  border-top: 1px solid #ebeef5;
  flex-wrap: wrap;
}

/* List View */
.templates-list {
  width: 100%;
}

.list-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.list-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.list-icon.identity { background-color: #ecf5ff; color: #409eff; }
.list-icon.certification { background-color: #f0f9eb; color: #67c23a; }
.list-icon.compliance { background-color: #fff3e0; color: #e6a23c; }
.list-icon.access { background-color: #fef0f0; color: #f56c6c; }

.list-name {
  font-weight: 500;
  font-size: 14px;
}

.list-schema {
  font-size: 11px;
  color: #8c9aab;
  font-family: monospace;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* Dialog */
.template-dialog :deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

.fields-editor {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.field-item {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.field-number {
  font-weight: 500;
  font-size: 12px;
  color: #409eff;
}

.form-hint {
  font-size: 11px;
  color: #8c9aab;
  margin-top: 4px;
}

.json-preview {
  background: #1e1e2e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  max-height: 500px;
}

.json-preview pre {
  margin: 0;
  font-size: 12px;
  font-family: monospace;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}
</style>