<template>
  <!-- ==================== Loading Screen ==================== -->
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
        <div class="loading-tip">Custom Templates</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="custom-templates-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Templates</el-breadcrumb-item>
          <el-breadcrumb-item>Custom Templates</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="loadTemplates" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          Create Custom Template
        </el-button>
      </div>
    </div>

    <!-- 模板统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Folder /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ templates.length }}</span>
          <span class="stat-label">Total Templates</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><SuccessFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ activeCount }}</span>
          <span class="stat-label">Active</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Monitor /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalDeviceUsage }}</span>
          <span class="stat-label">Devices Using</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><StarFilled /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ avgRating.toFixed(1) }}</span>
          <span class="stat-label">Avg Rating</span>
        </div>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchKeyword"
            placeholder="Search templates..."
            clearable
            :prefix-icon="Search"
            style="width: 260px"
            @clear="filterTemplates"
            @keyup.enter="filterTemplates"
        />
        <el-select v-model="filterCategory" placeholder="Category" clearable style="width: 140px" @change="filterTemplates">
          <el-option label="All Categories" value="" />
          <el-option label="HVAC" value="hvac" />
          <el-option label="Lighting" value="lighting" />
          <el-option label="Security" value="sas" />
          <el-option label="Fire Alarm" value="fas" />
          <el-option label="Plumbing" value="plumbing" />
          <el-option label="Electrical" value="electrical" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 120px" @change="filterTemplates">
          <el-option label="All Status" value="" />
          <el-option label="Published" value="published" />
          <el-option label="Draft" value="draft" />
          <el-option label="Archived" value="archived" />
        </el-select>
        <el-select v-model="filterOwner" placeholder="Owner" clearable style="width: 140px" @change="filterTemplates">
          <el-option label="All Templates" value="" />
          <el-option label="My Templates" value="mine" />
          <el-option label="Shared with Me" value="shared" />
          <el-option label="Public" value="public" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button-group>
          <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" :icon="Grid" size="small" @click="viewMode = 'grid'" />
          <el-button :type="viewMode === 'list' ? 'primary' : 'default'" :icon="List" size="small" @click="viewMode = 'list'" />
        </el-button-group>
      </div>
    </div>

    <!-- 网格视图 -->
    <div v-if="viewMode === 'grid'" class="templates-grid">
      <div v-for="template in filteredTemplates" :key="template.id" class="template-card" @click="viewTemplate(template)">
        <div class="card-header" :style="{ backgroundColor: getCategoryColor(template.category) }">
          <div class="card-icon">
            <el-icon><component :is="getCategoryIcon(template.category)" /></el-icon>
          </div>
          <div class="card-badge">
            <el-tag :type="template.status === 'published' ? 'success' : template.status === 'draft' ? 'info' : 'danger'" size="small">
              {{ template.status }}
            </el-tag>
          </div>
        </div>
        <div class="card-body">
          <h3 class="template-name">{{ template.name }}</h3>
          <p class="template-desc">{{ template.description || 'No description' }}</p>
          <div class="template-meta">
            <div class="meta-item">
              <el-icon><User /></el-icon>
              <span>{{ template.author }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDate(template.updatedAt) }}</span>
            </div>
          </div>
          <div class="template-rating">
            <el-rate v-model="template.rating" disabled show-score text-color="#ff9900" score-template="{value}" />
            <span class="usage-count">{{ template.usageCount }} uses</span>
          </div>
        </div>
        <div class="card-footer">
          <div class="tag-list">
            <el-tag v-for="tag in template.tags?.slice(0, 2)" :key="tag" size="small" type="info">{{ tag }}</el-tag>
            <span v-if="template.tags?.length > 2" class="tag-more">+{{ template.tags.length - 2 }}</span>
          </div>
          <div class="card-actions" @click.stop>
            <el-button size="small" text @click="editTemplate(template)">Edit</el-button>
            <el-button size="small" text type="primary" @click="applyTemplate(template)">Apply</el-button>
            <el-dropdown trigger="click" @command="(cmd: string) => handleTemplateCommand(cmd, template)">
              <el-button size="small" text :icon="MoreFilled" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="duplicate">Duplicate</el-dropdown-item>
                  <el-dropdown-item command="export">Export</el-dropdown-item>
                  <el-dropdown-item command="share">Share</el-dropdown-item>
                  <el-dropdown-item divided command="archive" v-if="template.status === 'published'">Archive</el-dropdown-item>
                  <el-dropdown-item divided command="delete" style="color: #f56c6c">Delete</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </div>

    <!-- 列表视图 -->
    <div v-else class="templates-list">
      <el-table :data="filteredTemplates" stripe border style="width: 100%" @row-click="viewTemplate">
        <el-table-column type="index" label="#" width="50" />
        <el-table-column label="Template" min-width="250">
          <template #default="{ row }">
            <div class="template-cell">
              <div class="template-icon" :style="{ backgroundColor: getCategoryColor(row.category) }">
                <el-icon><component :is="getCategoryIcon(row.category)" /></el-icon>
              </div>
              <div class="template-info">
                <span class="template-name">{{ row.name }}</span>
                <span class="template-desc">{{ row.description }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ getCategoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'published' ? 'success' : row.status === 'draft' ? 'info' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Rating" width="150">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled show-score text-color="#ff9900" score-template="{value}" />
          </template>
        </el-table-column>
        <el-table-column prop="usageCount" label="Uses" width="80" />
        <el-table-column prop="author" label="Author" width="120" />
        <el-table-column label="Updated" width="120">
          <template #default="{ row }">{{ formatDate(row.updatedAt) }}</template>
        </el-table-column>
        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text @click.stop="editTemplate(row)">Edit</el-button>
            <el-button size="small" text type="primary" @click.stop="applyTemplate(row)">Apply</el-button>
            <el-dropdown trigger="click" @command="(cmd: string) => handleTemplateCommand(cmd, row)">
              <el-button size="small" text :icon="MoreFilled" />
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredTemplates.length === 0" class="empty-state">
      <el-empty description="No custom templates found">
        <el-button type="primary" @click="openCreateDialog">Create Your First Template</el-button>
      </el-empty>
    </div>

    <!-- 创建/编辑模板对话框 - 基础信息 -->
    <el-dialog v-model="dialogVisible" :title="editingTemplate ? 'Edit Custom Template' : 'Create Custom Template'" width="800px" @closed="resetForm">
      <el-steps :active="step" finish-status="success" simple style="margin-bottom: 24px">
        <el-step title="Basic Info" @click="step = 0" />
        <el-step title="Parameters" @click="step = 1" />
        <el-step title="Scripts & Logic" @click="step = 2" />
        <el-step title="Review" @click="step = 3" />
      </el-steps>

      <!-- Step 1: Basic Info -->
      <div v-show="step === 0">
        <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
          <el-form-item label="Template Name" prop="name">
            <el-input v-model="formData.name" placeholder="Enter template name" />
          </el-form-item>
          <el-form-item label="Description" prop="description">
            <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="Describe what this template does" />
          </el-form-item>
          <el-form-item label="Category" prop="category">
            <el-select v-model="formData.category" placeholder="Select category" style="width: 100%">
              <el-option label="HVAC" value="hvac" />
              <el-option label="Lighting" value="lighting" />
              <el-option label="Security" value="sas" />
              <el-option label="Fire Alarm" value="fas" />
              <el-option label="Plumbing" value="plumbing" />
              <el-option label="Electrical" value="electrical" />
            </el-select>
          </el-form-item>
          <el-form-item label="Status" prop="status">
            <el-radio-group v-model="formData.status">
              <el-radio label="draft">Draft (Only visible to me)</el-radio>
              <el-radio label="published">Published (Share with team)</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="Tags" prop="tags">
            <el-select v-model="formData.tags" multiple filterable allow-create default-first-option placeholder="Add tags" style="width: 100%">
              <el-option v-for="tag in commonTags" :key="tag" :label="tag" :value="tag" />
            </el-select>
          </el-form-item>
          <el-form-item label="Visibility" prop="visibility">
            <el-radio-group v-model="formData.visibility">
              <el-radio label="private">Private (Only me)</el-radio>
              <el-radio label="team">Team (My team)</el-radio>
              <el-radio label="public">Public (Everyone)</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 2: Parameters -->
      <div v-show="step === 1">
        <div class="parameters-editor">
          <div class="parameters-header">
            <span>Parameter Name</span>
            <span>Type</span>
            <span>Unit</span>
            <span>Default Value</span>
            <span>Required</span>
            <span>Validation</span>
            <span></span>
          </div>
          <div v-for="(param, index) in formData.parameters" :key="index" class="parameter-row">
            <el-input v-model="param.name" placeholder="e.g., Temperature" size="small" style="width: 150px" />
            <el-select v-model="param.type" placeholder="Type" size="small" style="width: 100px">
              <el-option label="Number" value="number" />
              <el-option label="String" value="string" />
              <el-option label="Boolean" value="boolean" />
              <el-option label="Enum" value="enum" />
            </el-select>
            <el-input v-model="param.unit" placeholder="°C" size="small" style="width: 80px" />
            <el-input v-model="param.defaultValue" placeholder="Default" size="small" style="width: 100px" />
            <el-checkbox v-model="param.required" style="width: 60px" />
            <el-input v-model="param.validation" placeholder="min:0,max:100" size="small" style="width: 120px" />
            <el-button type="danger" size="small" :icon="Delete" circle @click="removeParameter(index)" />
          </div>
          <el-button type="primary" size="small" :icon="Plus" @click="addParameter" style="margin-top: 12px">
            Add Parameter
          </el-button>
        </div>

        <el-divider>Default Metrics</el-divider>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="Temperature">
              <el-input-number v-model="formData.defaultMetrics.temperature" :min="-10" :max="50" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Humidity">
              <el-input-number v-model="formData.defaultMetrics.humidity" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Power">
              <el-input-number v-model="formData.defaultMetrics.power" :min="0" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- Step 3: Scripts & Logic -->
      <div v-show="step === 2">
        <el-form label-width="120px">
          <el-form-item label="Validation Script">
            <el-input
                v-model="formData.validationScript"
                type="textarea"
                :rows="6"
                placeholder="// JavaScript validation logic
function validate(parameters) {
  if (parameters.temperature < 0 || parameters.temperature > 50) {
    return { valid: false, message: 'Temperature out of range' };
  }
  return { valid: true };
}"
            />
          </el-form-item>
          <el-form-item label="Transformation Script">
            <el-input
                v-model="formData.transformScript"
                type="textarea"
                :rows="6"
                placeholder="// JavaScript transformation logic
function transform(deviceData, parameters) {
  deviceData.name = parameters.name || deviceData.name;
  deviceData.metrics.temperature = parameters.temperature;
  return deviceData;
}"
            />
          </el-form-item>
          <el-form-item label="Pre-apply Hook">
            <el-input
                v-model="formData.preApplyScript"
                type="textarea"
                :rows="4"
                placeholder="// Run before applying template"
            />
          </el-form-item>
          <el-form-item label="Post-apply Hook">
            <el-input
                v-model="formData.postApplyScript"
                type="textarea"
                :rows="4"
                placeholder="// Run after applying template"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- Step 4: Review -->
      <div v-show="step === 3">
        <div class="review-section">
          <h4>Template Summary</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Name">{{ formData.name }}</el-descriptions-item>
            <el-descriptions-item label="Category">{{ getCategoryLabel(formData.category) }}</el-descriptions-item>
            <el-descriptions-item label="Status">{{ formData.status }}</el-descriptions-item>
            <el-descriptions-item label="Visibility">{{ formData.visibility }}</el-descriptions-item>
            <el-descriptions-item label="Tags">{{ formData.tags?.join(', ') || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Parameters">{{ formData.parameters.length }} parameters</el-descriptions-item>
          </el-descriptions>

          <h4 style="margin-top: 20px">Parameters</h4>
          <el-table :data="formData.parameters" size="small" border>
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="type" label="Type" />
            <el-table-column prop="unit" label="Unit" />
            <el-table-column prop="defaultValue" label="Default" />
            <el-table-column prop="required" label="Required" width="80">
              <template #default="{ row }">{{ row.required ? 'Yes' : 'No' }}</template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <div style="display: flex; justify-content: space-between; width: 100%">
          <div>
            <el-button v-if="step > 0" @click="step--">Back</el-button>
          </div>
          <div>
            <el-button @click="dialogVisible = false">Cancel</el-button>
            <el-button v-if="step < 3" type="primary" @click="step++">Next</el-button>
            <el-button v-else type="primary" @click="saveTemplate" :loading="saving">Save Template</el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 应用模板对话框 -->
    <el-dialog v-model="applyDialogVisible" :title="`Apply Template: ${selectedTemplate?.name}`" width="500px">
      <div class="apply-content">
        <p>This template contains <strong>{{ selectedTemplate?.parameters?.length || 0 }}</strong> configurable parameters.</p>
        <el-divider />
        <el-form label-width="140px">
          <el-form-item v-for="param in selectedTemplate?.parameters" :key="param.name" :label="param.name" :required="param.required">
            <el-input v-if="param.type === 'string'" v-model="paramValues[param.name]" :placeholder="param.defaultValue" />
            <el-input-number v-else-if="param.type === 'number'" v-model="paramValues[param.name]" :placeholder="param.defaultValue" style="width: 100%" />
            <el-select v-else-if="param.type === 'enum'" v-model="paramValues[param.name]" placeholder="Select value" style="width: 100%">
              <el-option v-for="opt in param.enumValues" :key="opt" :label="opt" :value="opt" />
            </el-select>
            <el-switch v-else-if="param.type === 'boolean'" v-model="paramValues[param.name]" />
            <div class="param-hint" v-if="param.validation">{{ param.validation }}</div>
          </el-form-item>
        </el-form>
        <el-divider />
        <el-select v-model="targetDevices" multiple placeholder="Select target devices" filterable style="width: 100%">
          <el-option v-for="device in availableDevices" :key="device.id" :label="`${device.name} (${device.model})`" :value="device.id" />
        </el-select>
        <div class="apply-options">
          <el-checkbox v-model="applyOptions.backup">Create backup before applying</el-checkbox>
          <el-checkbox v-model="applyOptions.validate">Validate before apply</el-checkbox>
          <el-checkbox v-model="applyOptions.notify">Send notification on completion</el-checkbox>
        </div>
      </div>
      <template #footer>
        <el-button @click="applyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmApply" :disabled="targetDevices.length === 0">Apply to {{ targetDevices.length }} Device(s)</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Refresh, Plus, Search, MoreFilled, Folder, SuccessFilled, Monitor,
  StarFilled, Grid, List, User, Clock, Delete, Cpu, ColdDrink, Sunny, Lock, Bell, MagicStick
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading custom templates...')
const refreshing = ref(false)
const saving = ref(false)
const loadingMessages = ['Initializing...', 'Loading templates...', 'Loading parameters...', 'Almost ready...']

// ==================== Types ====================
interface TemplateParameter {
  name: string
  type: 'number' | 'string' | 'boolean' | 'enum'
  unit: string
  defaultValue: any
  required: boolean
  validation?: string
  enumValues?: string[]
}

interface DefaultMetrics {
  temperature: number
  humidity: number
  power: number
}

interface CustomTemplate {
  id: string
  name: string
  description: string
  category: 'hvac' | 'lighting' | 'sas' | 'fas' | 'plumbing' | 'electrical'
  status: 'draft' | 'published' | 'archived'
  visibility: 'private' | 'team' | 'public'
  tags: string[]
  parameters: TemplateParameter[]
  defaultMetrics: DefaultMetrics
  validationScript: string
  transformScript: string
  preApplyScript: string
  postApplyScript: string
  rating: number
  usageCount: number
  author: string
  authorId: string
  createdAt: string
  updatedAt: string
}

// ==================== State ====================
const step = ref(0)
const searchKeyword = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const filterOwner = ref('')
const viewMode = ref<'grid' | 'list'>('grid')
const dialogVisible = ref(false)
const applyDialogVisible = ref(false)
const editingTemplate = ref<CustomTemplate | null>(null)
const selectedTemplate = ref<CustomTemplate | null>(null)
const targetDevices = ref<string[]>([])
const paramValues = ref<Record<string, any>>({})
const applyOptions = ref({
  backup: true,
  validate: true,
  notify: true
})
const formRef = ref<FormInstance>()

// Mock 数据
const templates = ref<CustomTemplate[]>([])
const availableDevices = ref([
  { id: '1', name: 'AHU-B2-01', model: 'Carrier 39G' },
  { id: '2', name: 'FCU-B2-01', model: 'Daikin FXMQ' },
  { id: '3', name: 'CH-B2-01', model: 'Carrier AquaEdge' }
])

const commonTags = ['HVAC', 'Energy Saving', 'Standard', 'Premium', 'Legacy', 'Compliance']

// 表单数据
const formData = ref({
  name: '',
  description: '',
  category: 'hvac',
  status: 'draft',
  visibility: 'private',
  tags: [] as string[],
  parameters: [] as TemplateParameter[],
  defaultMetrics: { temperature: 24, humidity: 50, power: 10 },
  validationScript: '',
  transformScript: '',
  preApplyScript: '',
  postApplyScript: ''
})

const formRules: FormRules = {
  name: [{ required: true, message: 'Please enter template name', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }]
}

// ==================== Computed ====================
const activeCount = computed(() => templates.value.filter(t => t.status === 'published').length)
const totalDeviceUsage = computed(() => templates.value.reduce((sum, t) => sum + t.usageCount, 0))
const avgRating = computed(() => {
  const published = templates.value.filter(t => t.status === 'published')
  if (published.length === 0) return 0
  const sum = published.reduce((s, t) => s + t.rating, 0)
  return sum / published.length
})

const filteredTemplates = computed(() => {
  let result = [...templates.value]

  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(t => t.name.toLowerCase().includes(kw) || t.description?.toLowerCase().includes(kw))
  }
  if (filterCategory.value) result = result.filter(t => t.category === filterCategory.value)
  if (filterStatus.value) result = result.filter(t => t.status === filterStatus.value)
  if (filterOwner.value === 'mine') result = result.filter(t => t.authorId === 'current-user')
  else if (filterOwner.value === 'shared') result = result.filter(t => t.visibility === 'team')
  else if (filterOwner.value === 'public') result = result.filter(t => t.visibility === 'public')

  return result
})

// ==================== Helper Functions ====================
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    hvac: 'HVAC', lighting: 'Lighting', sas: 'Security', fas: 'Fire Alarm', plumbing: 'Plumbing', electrical: 'Electrical'
  }
  return labels[category] || category
}

const getCategoryIcon = (category: string) => {
  const icons: Record<string, any> = {
    hvac: ColdDrink, lighting: Sunny, sas: Lock, fas: Bell, plumbing: MagicStick, electrical: Cpu
  }
  return icons[category] || Folder
}

const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    hvac: '#5470c6', lighting: '#fac858', sas: '#73c0de', fas: '#ee6666', plumbing: '#3ba272', electrical: '#fc8452'
  }
  return colors[category] || '#909399'
}

const getCategoryTagType = (category: string) => {
  const types: Record<string, string> = {
    hvac: 'primary', lighting: 'success', sas: 'danger', fas: 'warning', plumbing: 'info', electrical: 'warning'
  }
  return types[category] || 'info'
}

// 生成模拟数据
const generateMockTemplates = (): CustomTemplate[] => {
  const now = new Date().toISOString()

  return [
    {
      id: '1',
      name: 'Smart HVAC Controller',
      description: 'Advanced HVAC control with adaptive algorithms',
      category: 'hvac',
      status: 'published',
      visibility: 'public',
      tags: ['HVAC', 'Energy Saving', 'Smart Building'],
      parameters: [
        { name: 'Setpoint Temp', type: 'number', unit: '°C', defaultValue: 22.5, required: true, validation: 'min:18,max:28' },
        { name: 'Fan Speed', type: 'number', unit: '%', defaultValue: 70, required: false },
        { name: 'Mode', type: 'enum', unit: '', defaultValue: 'auto', required: true }
      ],
      defaultMetrics: { temperature: 23, humidity: 55, power: 15 },
      validationScript: 'function validate(parameters) { if (parameters.temp < 18 || parameters.temp > 28) { return { valid: false, message: "Temperature out of range" }; } return { valid: true }; }',
      transformScript: '',
      preApplyScript: '',
      postApplyScript: '',
      rating: 4.5,
      usageCount: 23,
      author: 'John Smith',
      authorId: 'user-1',
      createdAt: '2024-01-15T00:00:00Z',
      updatedAt: now
    },
    {
      id: '2',
      name: 'Lighting Automation',
      description: 'Intelligent lighting control with occupancy sensing',
      category: 'lighting',
      status: 'published',
      visibility: 'team',
      tags: ['Lighting', 'Automation', 'Energy'],
      parameters: [
        { name: 'Brightness', type: 'number', unit: '%', defaultValue: 80, required: true },
        { name: 'Auto Dim', type: 'boolean', unit: '', defaultValue: true, required: false }
      ],
      defaultMetrics: { temperature: 26, humidity: 45, power: 5 },
      validationScript: '',
      transformScript: '',
      preApplyScript: '',
      postApplyScript: '',
      rating: 4.2,
      usageCount: 15,
      author: 'Sarah Johnson',
      authorId: 'user-2',
      createdAt: '2024-01-20T00:00:00Z',
      updatedAt: now
    },
    {
      id: '3',
      name: 'Security Gateway Config',
      description: 'Standard security system configuration',
      category: 'sas',
      status: 'draft',
      visibility: 'private',
      tags: ['Security', 'Access Control'],
      parameters: [
        { name: 'Door Timeout', type: 'number', unit: 's', defaultValue: 5, required: true },
        { name: 'Alarm Delay', type: 'number', unit: 's', defaultValue: 30, required: false }
      ],
      defaultMetrics: { temperature: 35, humidity: 40, power: 0.5 },
      validationScript: '',
      transformScript: '',
      preApplyScript: '',
      postApplyScript: '',
      rating: 0,
      usageCount: 0,
      author: 'John Smith',
      authorId: 'user-1',
      createdAt: '2024-02-01T00:00:00Z',
      updatedAt: now
    }
  ]
}

// ==================== Actions ====================
const loadTemplates = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 500))
  templates.value = generateMockTemplates()
  refreshing.value = false
}

const filterTemplates = () => {}

const openCreateDialog = () => {
  editingTemplate.value = null
  step.value = 0
  resetForm()
  dialogVisible.value = true
}

const editTemplate = (template: CustomTemplate) => {
  editingTemplate.value = template
  step.value = 0
  formData.value = {
    name: template.name,
    description: template.description,
    category: template.category,
    status: template.status,
    visibility: template.visibility,
    tags: [...template.tags],
    parameters: JSON.parse(JSON.stringify(template.parameters)),
    defaultMetrics: { ...template.defaultMetrics },
    validationScript: template.validationScript,
    transformScript: template.transformScript,
    preApplyScript: template.preApplyScript,
    postApplyScript: template.postApplyScript
  }
  dialogVisible.value = true
}

const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    category: 'hvac',
    status: 'draft',
    visibility: 'private',
    tags: [],
    parameters: [],
    defaultMetrics: { temperature: 24, humidity: 50, power: 10 },
    validationScript: '',
    transformScript: '',
    preApplyScript: '',
    postApplyScript: ''
  }
  if (formRef.value) formRef.value.clearValidate()
}

const addParameter = () => {
  formData.value.parameters.push({
    name: '',
    type: 'number',
    unit: '',
    defaultValue: '',
    required: false,
    validation: ''
  })
}

const removeParameter = (index: number) => {
  formData.value.parameters.splice(index, 1)
}

const saveTemplate = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      await new Promise(resolve => setTimeout(resolve, 800))

      if (editingTemplate.value) {
        const index = templates.value.findIndex(t => t.id === editingTemplate.value!.id)
        if (index !== -1) {
          templates.value[index] = {
            ...templates.value[index],
            ...formData.value,
            updatedAt: new Date().toISOString()
          }
        }
        ElMessage.success('Template updated successfully')
      } else {
        const newTemplate: CustomTemplate = {
          id: Date.now().toString(),
          ...formData.value,
          rating: 0,
          usageCount: 0,
          author: 'Current User',
          authorId: 'current-user',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        templates.value.push(newTemplate)
        ElMessage.success('Template created successfully')
      }

      dialogVisible.value = false
      saving.value = false
    }
  })
}

const viewTemplate = (template: CustomTemplate) => {
  ElMessage.info(`Viewing template: ${template.name}`)
}

const applyTemplate = (template: CustomTemplate) => {
  selectedTemplate.value = template
  paramValues.value = {}
  template.parameters.forEach(p => {
    paramValues.value[p.name] = p.defaultValue
  })
  targetDevices.value = []
  applyDialogVisible.value = true
}

const confirmApply = () => {
  if (targetDevices.value.length === 0) {
    ElMessage.warning('Please select at least one device')
    return
  }
  ElMessage.success(`Template applied to ${targetDevices.value.length} device(s)`)
  applyDialogVisible.value = false
}

const handleTemplateCommand = (command: string, template: CustomTemplate) => {
  switch (command) {
    case 'duplicate':
      duplicateTemplate(template)
      break
    case 'export':
      exportTemplate(template)
      break
    case 'share':
      shareTemplate(template)
      break
    case 'archive':
      archiveTemplate(template)
      break
    case 'delete':
      deleteTemplate(template)
      break
  }
}

const duplicateTemplate = (template: CustomTemplate) => {
  const newTemplate: CustomTemplate = {
    ...template,
    id: Date.now().toString(),
    name: `${template.name} (Copy)`,
    status: 'draft',
    usageCount: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
  templates.value.push(newTemplate)
  ElMessage.success(`Template duplicated: ${newTemplate.name}`)
}

const exportTemplate = (template: CustomTemplate) => {
  const dataStr = JSON.stringify(template, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${template.name.replace(/\s/g, '_')}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success(`Template exported: ${template.name}`)
}

const shareTemplate = (template: CustomTemplate) => {
  ElMessage.info(`Share template: ${template.name}`)
}

const archiveTemplate = async (template: CustomTemplate) => {
  try {
    await ElMessageBox.confirm(`Archive template "${template.name}"?`, 'Confirm Archive', {
      confirmButtonText: 'Archive', cancelButtonText: 'Cancel', type: 'info'
    })
    const index = templates.value.findIndex(t => t.id === template.id)
    if (index !== -1) templates.value[index].status = 'archived'
    ElMessage.success('Template archived')
  } catch (error) {}
}

const deleteTemplate = async (template: CustomTemplate) => {
  try {
    await ElMessageBox.confirm(`Delete template "${template.name}"?`, 'Confirm Delete', {
      confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
    })
    templates.value = templates.value.filter(t => t.id !== template.id)
    ElMessage.success('Template deleted')
  } catch (error) {}
}

// ==================== Lifecycle ====================
onMounted(() => {
  let msgIdx = 0
  const msgInt = setInterval(() => {
    if (msgIdx < loadingMessages.length - 1) {
      msgIdx++
      loadingMessage.value = loadingMessages[msgIdx]
    }
  }, 400)
  const progInt = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInt)
    clearInterval(progInt)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      loadTemplates()
      isLoaded.value = true
    }, 400)
  }, 2000)
})
</script>

<style scoped>
.loading-container { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-overlay { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: fadeInUp 0.6s ease-out; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.custom-templates-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat-icon .el-icon { font-size: 32px; color: #3b82f6; }
.stat-info .stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-info .stat-label { font-size: 13px; color: #64748b; }

.filter-bar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.filter-left { display: flex; gap: 12px; flex-wrap: wrap; }

.templates-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 20px; }
.template-card { background: white; border-radius: 16px; overflow: hidden; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.template-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }
.card-header { height: 100px; position: relative; display: flex; align-items: center; justify-content: center; }
.card-icon .el-icon { font-size: 48px; color: white; }
.card-badge { position: absolute; top: 12px; right: 12px; }
.card-body { padding: 16px; }
.template-name { margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.template-desc { margin: 0 0 12px 0; font-size: 13px; color: #64748b; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.template-meta { display: flex; gap: 16px; margin-bottom: 12px; }
.meta-item { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #94a3b8; }
.template-rating { display: flex; align-items: center; justify-content: space-between; }
.usage-count { font-size: 12px; color: #64748b; }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #f8fafc; border-top: 1px solid #e2e8f0; }
.tag-list { display: flex; gap: 8px; flex-wrap: wrap; }
.tag-more { font-size: 11px; color: #94a3b8; }
.card-actions { display: flex; gap: 4px; }

.templates-list { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.template-cell { display: flex; align-items: center; gap: 12px; }
.template-icon { width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; }
.template-info { display: flex; flex-direction: column; }
.template-name { font-weight: 500; color: #1e293b; }
.template-desc { font-size: 11px; color: #64748b; }

.empty-state { padding: 60px; text-align: center; background: white; border-radius: 16px; }

.parameters-editor { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }
.parameters-header { display: flex; gap: 12px; padding-bottom: 12px; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; font-size: 12px; font-weight: 500; color: #64748b; }
.parameter-row { display: flex; gap: 12px; margin-bottom: 12px; align-items: center; }

.review-section { max-height: 500px; overflow-y: auto; }
.review-section h4 { margin: 0 0 16px 0; }

.apply-content { max-height: 500px; overflow-y: auto; }
.apply-options { margin-top: 16px; display: flex; gap: 16px; flex-wrap: wrap; }
.param-hint { font-size: 11px; color: #94a3b8; margin-top: 4px; }

@media (max-width: 1024px) { .stats-cards { grid-template-columns: repeat(2, 1fr); } .templates-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); } }
@media (max-width: 768px) { .stats-cards { grid-template-columns: 1fr; } .filter-bar { flex-direction: column; } .filter-left { width: 100%; } .templates-grid { grid-template-columns: 1fr; } .parameters-header, .parameter-row { flex-wrap: wrap; } }
</style>