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
        <div class="loading-tip">Device Templates</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="device-templates-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Templates</el-breadcrumb-item>
          <el-breadcrumb-item>Standard Templates</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="loadTemplates" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          Create Template
        </el-button>
      </div>
    </div>

    <!-- 模板类型标签 -->
    <div class="tabs-container">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="All Templates" name="all" />
        <el-tab-pane label="HVAC Templates" name="hvac" />
        <el-tab-pane label="Lighting Templates" name="lighting" />
        <el-tab-pane label="Security Templates" name="sas" />
        <el-tab-pane label="Fire Alarm Templates" name="fas" />
        <el-tab-pane label="Plumbing Templates" name="plumbing" />
      </el-tabs>
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
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px" @change="filterTemplates">
          <el-option label="All Status" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Draft" value="draft" />
          <el-option label="Archived" value="archived" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="total-count">{{ filteredTemplates.length }} templates found</span>
      </div>
    </div>

    <!-- 模板卡片列表 -->
    <div class="templates-grid">
      <div v-for="template in filteredTemplates" :key="template.id" class="template-card" @click="viewTemplate(template)">
        <div class="card-header" :style="{ backgroundColor: getSystemColor(template.systemType) }">
          <div class="card-icon">
            <el-icon><component :is="getSystemIcon(template.systemType)" /></el-icon>
          </div>
          <div class="card-badge">
            <el-tag :type="template.status === 'active' ? 'success' : template.status === 'draft' ? 'info' : 'danger'" size="small">
              {{ template.status }}
            </el-tag>
          </div>
        </div>
        <div class="card-body">
          <h3 class="template-name">{{ template.name }}</h3>
          <p class="template-desc">{{ template.description || 'No description' }}</p>
          <div class="template-meta">
            <div class="meta-item">
              <el-icon><Monitor /></el-icon>
              <span>{{ getSystemLabel(template.systemType) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><List /></el-icon>
              <span>{{ template.parameters?.length || 0 }} parameters</span>
            </div>
            <div class="meta-item">
              <el-icon><Clock /></el-icon>
              <span>{{ formatDate(template.updatedAt) }}</span>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <div class="usage-stats">
            <span class="usage-count">{{ template.usageCount || 0 }} devices using</span>
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
                  <el-dropdown-item command="preview">Preview</el-dropdown-item>
                  <el-dropdown-item divided command="archive" v-if="template.status === 'active'">Archive</el-dropdown-item>
                  <el-dropdown-item divided command="delete" style="color: #f56c6c">Delete</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredTemplates.length === 0" class="empty-state">
      <el-empty description="No templates found">
        <el-button type="primary" @click="openCreateDialog">Create Template</el-button>
      </el-empty>
    </div>

    <!-- 创建/编辑模板对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingTemplate ? 'Edit Template' : 'Create Template'" width="700px" @closed="resetForm">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Template Name" prop="name">
              <el-input v-model="formData.name" placeholder="Enter template name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="System Type" prop="systemType">
              <el-select v-model="formData.systemType" placeholder="Select system type" style="width: 100%">
                <el-option label="HVAC" value="hvac" />
                <el-option label="Lighting" value="lighting" />
                <el-option label="Security" value="sas" />
                <el-option label="Fire Alarm" value="fas" />
                <el-option label="Plumbing" value="plumbing" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Template description" />
        </el-form-item>
        <el-form-item label="Status" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">Active</el-radio>
            <el-radio label="draft">Draft</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-divider>Parameter Configuration</el-divider>

        <div class="parameters-editor">
          <div class="parameters-header">
            <span class="param-name">Parameter Name</span>
            <span class="param-type">Type</span>
            <span class="param-unit">Unit</span>
            <span class="param-default">Default Value</span>
            <span class="param-required">Required</span>
            <span class="param-actions"></span>
          </div>
          <div v-for="(param, index) in formData.parameters" :key="index" class="parameter-row">
            <el-input v-model="param.name" placeholder="e.g., Temperature" size="small" class="param-name-input" />
            <el-select v-model="param.type" placeholder="Type" size="small" class="param-type-select">
              <el-option label="Number" value="number" />
              <el-option label="String" value="string" />
              <el-option label="Boolean" value="boolean" />
              <el-option label="Enum" value="enum" />
            </el-select>
            <el-input v-model="param.unit" placeholder="e.g., °C" size="small" class="param-unit-input" />
            <el-input v-model="param.defaultValue" placeholder="Default" size="small" class="param-default-input" />
            <el-checkbox v-model="param.required" class="param-required-checkbox" />
            <el-button type="danger" size="small" :icon="Delete" circle @click="removeParameter(index)" />
          </div>
          <el-button type="primary" size="small" :icon="Plus" @click="addParameter" style="margin-top: 12px">
            Add Parameter
          </el-button>
        </div>

        <el-divider>Threshold Configuration</el-divider>

        <div class="thresholds-editor">
          <div class="thresholds-header">
            <span>Parameter</span>
            <span>Warning Min</span>
            <span>Warning Max</span>
            <span>Critical Min</span>
            <span>Critical Max</span>
            <span></span>
          </div>
          <div v-for="(threshold, index) in formData.thresholds" :key="index" class="threshold-row">
            <el-select v-model="threshold.parameter" placeholder="Select parameter" size="small" style="width: 140px">
              <el-option v-for="param in formData.parameters" :key="param.name" :label="param.name" :value="param.name" />
            </el-select>
            <el-input-number v-model="threshold.warningMin" :step="0.5" size="small" style="width: 100px" placeholder="Min" />
            <el-input-number v-model="threshold.warningMax" :step="0.5" size="small" style="width: 100px" placeholder="Max" />
            <el-input-number v-model="threshold.criticalMin" :step="0.5" size="small" style="width: 100px" placeholder="Min" />
            <el-input-number v-model="threshold.criticalMax" :step="0.5" size="small" style="width: 100px" placeholder="Max" />
            <el-button type="danger" size="small" :icon="Delete" circle @click="removeThreshold(index)" />
          </div>
          <el-button type="primary" size="small" :icon="Plus" @click="addThreshold" style="margin-top: 12px">
            Add Threshold
          </el-button>
        </div>

        <el-divider>Default Metrics</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Default Temperature">
              <el-input-number v-model="formData.defaultMetrics.temperature" :min="-10" :max="50" :step="0.5" style="width: 100%" />
              <span class="unit-suffix">°C</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Default Humidity">
              <el-input-number v-model="formData.defaultMetrics.humidity" :min="0" :max="100" style="width: 100%" />
              <span class="unit-suffix">%</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Default Power">
              <el-input-number v-model="formData.defaultMetrics.power" :min="0" :step="0.5" style="width: 100%" />
              <span class="unit-suffix">kW</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Expected Life">
              <el-input-number v-model="formData.expectedLife" :min="1" :max="30" style="width: 100%" />
              <span class="unit-suffix">years</span>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTemplate" :loading="saving">Save Template</el-button>
      </template>
    </el-dialog>

    <!-- 应用模板对话框 -->
    <el-dialog v-model="applyDialogVisible" title="Apply Template to Devices" width="500px">
      <div class="apply-content">
        <p>Applying template: <strong>{{ selectedTemplate?.name }}</strong></p>
        <p class="apply-info">This will configure the selected devices with the template settings.</p>
        <el-select
            v-model="selectedDevicesForApply"
            multiple
            placeholder="Select devices to apply template"
            filterable
            style="width: 100%"
        >
          <el-option
              v-for="device in availableDevices"
              :key="device.id"
              :label="`${device.name} (${device.model})`"
              :value="device.id"
          />
        </el-select>
        <div class="apply-options">
          <el-checkbox v-model="applyOptions.overwriteExisting">Overwrite existing configuration</el-checkbox>
          <el-checkbox v-model="applyOptions.createBackup">Create backup before applying</el-checkbox>
        </div>
      </div>
      <template #footer>
        <el-button @click="applyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmApply" :disabled="selectedDevicesForApply.length === 0">Apply to {{ selectedDevicesForApply.length }} Device(s)</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Refresh, Plus, Search, MoreFilled, Monitor, List, Clock, Delete,
  Cpu, ColdDrink, Sunny, Lock, Bell, MagicStick, Folder
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading templates...')
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
}

interface Threshold {
  parameter: string
  warningMin: number
  warningMax: number
  criticalMin: number
  criticalMax: number
}

interface DefaultMetrics {
  temperature: number
  humidity: number
  power: number
}

interface DeviceTemplate {
  id: string
  name: string
  description: string
  systemType: 'hvac' | 'lighting' | 'sas' | 'fas' | 'plumbing'
  status: 'active' | 'draft' | 'archived'
  parameters: TemplateParameter[]
  thresholds: Threshold[]
  defaultMetrics: DefaultMetrics
  expectedLife: number
  usageCount: number
  createdAt: string
  updatedAt: string
}

interface Device {
  id: string
  name: string
  model: string
  systemType: string
}

// ==================== State ====================
const activeTab = ref('all')
const searchKeyword = ref('')
const filterStatus = ref('')
const dialogVisible = ref(false)
const applyDialogVisible = ref(false)
const editingTemplate = ref<DeviceTemplate | null>(null)
const selectedTemplate = ref<DeviceTemplate | null>(null)
const selectedDevicesForApply = ref<string[]>([])
const formRef = ref<FormInstance>()

// 表单数据
const formData = ref({
  name: '',
  description: '',
  systemType: 'hvac',
  status: 'draft',
  parameters: [] as TemplateParameter[],
  thresholds: [] as Threshold[],
  defaultMetrics: {
    temperature: 24,
    humidity: 50,
    power: 10
  },
  expectedLife: 10
})

const applyOptions = ref({
  overwriteExisting: true,
  createBackup: true
})

const formRules: FormRules = {
  name: [{ required: true, message: 'Please enter template name', trigger: 'blur' }],
  systemType: [{ required: true, message: 'Please select system type', trigger: 'change' }]
}

// Mock 模板数据
const templates = ref<DeviceTemplate[]>([])

// Mock 设备数据
const availableDevices = ref<Device[]>([
  { id: '1', name: 'AHU-B2-01 Air Handler', model: 'Carrier 39G', systemType: 'hvac' },
  { id: '2', name: 'FCU-B2-01 Fan Coil', model: 'Daikin FXMQ', systemType: 'hvac' },
  { id: '3', name: 'CH-B2-01 Chiller', model: 'Carrier AquaEdge', systemType: 'hvac' },
  { id: '4', name: 'LIGHT-B2-01 Controller', model: 'Philips Dynalite', systemType: 'lighting' },
  { id: '5', name: 'ACS-1F-01 Entrance', model: 'HID VertX', systemType: 'sas' }
])

// ==================== Computed ====================
const filteredTemplates = computed(() => {
  let result = [...templates.value]

  if (activeTab.value !== 'all') {
    result = result.filter(t => t.systemType === activeTab.value)
  }

  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(t =>
        t.name.toLowerCase().includes(kw) ||
        t.description?.toLowerCase().includes(kw)
    )
  }

  if (filterStatus.value) {
    result = result.filter(t => t.status === filterStatus.value)
  }

  return result
})

// ==================== Helper Functions ====================
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

const getSystemLabel = (type: string) => {
  const labels: Record<string, string> = {
    hvac: 'HVAC', lighting: 'Lighting', sas: 'Security', fas: 'Fire Alarm', plumbing: 'Plumbing'
  }
  return labels[type] || type
}

const getSystemIcon = (type: string) => {
  const icons: Record<string, any> = {
    hvac: ColdDrink, lighting: Sunny, sas: Lock, fas: Bell, plumbing: MagicStick
  }
  return icons[type] || Cpu
}

const getSystemColor = (type: string) => {
  const colors: Record<string, string> = {
    hvac: '#5470c6', lighting: '#fac858', sas: '#73c0de', fas: '#ee6666', plumbing: '#3ba272'
  }
  return colors[type] || '#909399'
}

// 生成模拟数据
const generateMockTemplates = (): DeviceTemplate[] => {
  const now = new Date().toISOString()

  return [
    {
      id: '1',
      name: 'Standard HVAC AHU Template',
      description: 'Standard configuration for Air Handling Units',
      systemType: 'hvac',
      status: 'active',
      parameters: [
        { name: 'Supply Air Temp', type: 'number', unit: '°C', defaultValue: 22.5, required: true },
        { name: 'Return Air Temp', type: 'number', unit: '°C', defaultValue: 24.0, required: true },
        { name: 'Fan Speed', type: 'number', unit: '%', defaultValue: 70, required: false },
        { name: 'Operation Mode', type: 'enum', unit: '', defaultValue: 'auto', required: true }
      ],
      thresholds: [
        { parameter: 'Supply Air Temp', warningMin: 18, warningMax: 26, criticalMin: 15, criticalMax: 30 },
        { parameter: 'Return Air Temp', warningMin: 20, warningMax: 28, criticalMin: 18, criticalMax: 32 }
      ],
      defaultMetrics: { temperature: 23, humidity: 55, power: 15 },
      expectedLife: 15,
      usageCount: 12,
      createdAt: '2024-01-15T00:00:00Z',
      updatedAt: now
    },
    {
      id: '2',
      name: 'Standard Lighting Controller',
      description: 'Standard configuration for lighting control systems',
      systemType: 'lighting',
      status: 'active',
      parameters: [
        { name: 'Brightness', type: 'number', unit: '%', defaultValue: 80, required: true },
        { name: 'Color Temperature', type: 'number', unit: 'K', defaultValue: 4000, required: false },
        { name: 'Dimming Speed', type: 'number', unit: 's', defaultValue: 2, required: false }
      ],
      thresholds: [
        { parameter: 'Brightness', warningMin: 10, warningMax: 100, criticalMin: 0, criticalMax: 100 }
      ],
      defaultMetrics: { temperature: 26, humidity: 45, power: 5 },
      expectedLife: 10,
      usageCount: 8,
      createdAt: '2024-01-20T00:00:00Z',
      updatedAt: now
    },
    {
      id: '3',
      name: 'Chiller Standard Config',
      description: 'Standard configuration for chiller units',
      systemType: 'hvac',
      status: 'active',
      parameters: [
        { name: 'Chilled Water Setpoint', type: 'number', unit: '°C', defaultValue: 7, required: true },
        { name: 'Condenser Water Temp', type: 'number', unit: '°C', defaultValue: 32, required: true },
        { name: 'Load Percentage', type: 'number', unit: '%', defaultValue: 60, required: false }
      ],
      thresholds: [
        { parameter: 'Chilled Water Setpoint', warningMin: 5, warningMax: 10, criticalMin: 3, criticalMax: 12 },
        { parameter: 'Condenser Water Temp', warningMin: 28, warningMax: 35, criticalMin: 25, criticalMax: 40 }
      ],
      defaultMetrics: { temperature: 28, humidity: 65, power: 85 },
      expectedLife: 20,
      usageCount: 5,
      createdAt: '2024-02-01T00:00:00Z',
      updatedAt: now
    },
    {
      id: '4',
      name: 'Access Control Standard',
      description: 'Standard configuration for access control systems',
      systemType: 'sas',
      status: 'draft',
      parameters: [
        { name: 'Door Timeout', type: 'number', unit: 's', defaultValue: 5, required: true },
        { name: 'Lock Mode', type: 'enum', unit: '', defaultValue: 'auto', required: true }
      ],
      thresholds: [],
      defaultMetrics: { temperature: 35, humidity: 40, power: 0.5 },
      expectedLife: 8,
      usageCount: 0,
      createdAt: '2024-02-10T00:00:00Z',
      updatedAt: now
    },
    {
      id: '5',
      name: 'Fire Alarm Standard',
      description: 'Standard configuration for fire alarm systems',
      systemType: 'fas',
      status: 'active',
      parameters: [
        { name: 'Sensitivity', type: 'number', unit: '%', defaultValue: 50, required: true },
        { name: 'Test Mode', type: 'boolean', unit: '', defaultValue: false, required: false }
      ],
      thresholds: [
        { parameter: 'Sensitivity', warningMin: 30, warningMax: 80, criticalMin: 20, criticalMax: 90 }
      ],
      defaultMetrics: { temperature: 22, humidity: 55, power: 0.3 },
      expectedLife: 10,
      usageCount: 3,
      createdAt: '2024-02-15T00:00:00Z',
      updatedAt: now
    },
    {
      id: '6',
      name: 'Pump Standard Configuration',
      description: 'Standard configuration for pump systems',
      systemType: 'plumbing',
      status: 'active',
      parameters: [
        { name: 'Flow Rate Setpoint', type: 'number', unit: 'm³/h', defaultValue: 100, required: true },
        { name: 'Pressure Setpoint', type: 'number', unit: 'kPa', defaultValue: 300, required: true }
      ],
      thresholds: [
        { parameter: 'Flow Rate Setpoint', warningMin: 50, warningMax: 150, criticalMin: 30, criticalMax: 200 },
        { parameter: 'Pressure Setpoint', warningMin: 200, warningMax: 400, criticalMin: 150, criticalMax: 500 }
      ],
      defaultMetrics: { temperature: 30, humidity: 60, power: 7.5 },
      expectedLife: 12,
      usageCount: 2,
      createdAt: '2024-02-20T00:00:00Z',
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

const filterTemplates = () => {
  // Computed property handles filtering
}

const handleTabChange = () => {
  filterTemplates()
}

const openCreateDialog = () => {
  editingTemplate.value = null
  resetForm()
  dialogVisible.value = true
}

const editTemplate = (template: DeviceTemplate) => {
  editingTemplate.value = template
  formData.value = {
    name: template.name,
    description: template.description,
    systemType: template.systemType,
    status: template.status,
    parameters: JSON.parse(JSON.stringify(template.parameters)),
    thresholds: JSON.parse(JSON.stringify(template.thresholds)),
    defaultMetrics: { ...template.defaultMetrics },
    expectedLife: template.expectedLife
  }
  dialogVisible.value = true
}

const resetForm = () => {
  formData.value = {
    name: '',
    description: '',
    systemType: 'hvac',
    status: 'draft',
    parameters: [],
    thresholds: [],
    defaultMetrics: { temperature: 24, humidity: 50, power: 10 },
    expectedLife: 10
  }
  if (formRef.value) formRef.value.clearValidate()
}

const addParameter = () => {
  formData.value.parameters.push({
    name: '',
    type: 'number',
    unit: '',
    defaultValue: '',
    required: false
  })
}

const removeParameter = (index: number) => {
  formData.value.parameters.splice(index, 1)
}

const addThreshold = () => {
  formData.value.thresholds.push({
    parameter: '',
    warningMin: 0,
    warningMax: 0,
    criticalMin: 0,
    criticalMax: 0
  })
}

const removeThreshold = (index: number) => {
  formData.value.thresholds.splice(index, 1)
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
        const newTemplate: DeviceTemplate = {
          id: Date.now().toString(),
          ...formData.value,
          usageCount: 0,
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

const viewTemplate = (template: DeviceTemplate) => {
  ElMessage.info(`Viewing template: ${template.name}`)
}

const applyTemplate = (template: DeviceTemplate) => {
  selectedTemplate.value = template
  selectedDevicesForApply.value = []
  applyOptions.value = { overwriteExisting: true, createBackup: true }
  applyDialogVisible.value = true
}

const confirmApply = () => {
  if (selectedDevicesForApply.value.length === 0) {
    ElMessage.warning('Please select at least one device')
    return
  }

  ElMessage.success(`Template "${selectedTemplate.value?.name}" applied to ${selectedDevicesForApply.value.length} device(s)`)
  applyDialogVisible.value = false
}

const handleTemplateCommand = (command: string, template: DeviceTemplate) => {
  switch (command) {
    case 'duplicate':
      duplicateTemplate(template)
      break
    case 'export':
      exportTemplate(template)
      break
    case 'preview':
      previewTemplate(template)
      break
    case 'archive':
      archiveTemplate(template)
      break
    case 'delete':
      deleteTemplate(template)
      break
  }
}

const duplicateTemplate = (template: DeviceTemplate) => {
  const newTemplate: DeviceTemplate = {
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

const exportTemplate = (template: DeviceTemplate) => {
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

const previewTemplate = (template: DeviceTemplate) => {
  ElMessage.info(`Previewing template: ${template.name}`)
}

const archiveTemplate = async (template: DeviceTemplate) => {
  try {
    await ElMessageBox.confirm(
        `Archive template "${template.name}"? Archived templates can be restored later.`,
        'Confirm Archive',
        { confirmButtonText: 'Archive', cancelButtonText: 'Cancel', type: 'info' }
    )
    const index = templates.value.findIndex(t => t.id === template.id)
    if (index !== -1) {
      templates.value[index].status = 'archived'
    }
    ElMessage.success('Template archived')
  } catch (error) {
    // cancelled
  }
}

const deleteTemplate = async (template: DeviceTemplate) => {
  try {
    await ElMessageBox.confirm(
        `Delete template "${template.name}"? This action cannot be undone.`,
        'Confirm Delete',
        { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
    templates.value = templates.value.filter(t => t.id !== template.id)
    ElMessage.success('Template deleted')
  } catch (error) {
    // cancelled
  }
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

.device-templates-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.tabs-container { background: white; border-radius: 12px; padding: 0 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }

.filter-bar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.filter-left { display: flex; gap: 12px; flex-wrap: wrap; }
.total-count { font-size: 13px; color: #64748b; }

.templates-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 20px; }
.template-card { background: white; border-radius: 16px; overflow: hidden; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.template-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }
.card-header { height: 100px; position: relative; display: flex; align-items: center; justify-content: center; }
.card-icon .el-icon { font-size: 48px; color: white; }
.card-badge { position: absolute; top: 12px; right: 12px; }
.card-body { padding: 16px; }
.template-name { margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.template-desc { margin: 0 0 12px 0; font-size: 13px; color: #64748b; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.template-meta { display: flex; gap: 16px; }
.meta-item { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #94a3b8; }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #f8fafc; border-top: 1px solid #e2e8f0; }
.usage-count { font-size: 12px; color: #64748b; }
.card-actions { display: flex; gap: 4px; }

.empty-state { padding: 60px; text-align: center; background: white; border-radius: 16px; }

.parameters-editor, .thresholds-editor { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }
.parameters-header, .thresholds-header { display: flex; gap: 12px; padding-bottom: 12px; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; font-size: 12px; font-weight: 500; color: #64748b; }
.parameter-row, .threshold-row { display: flex; gap: 12px; margin-bottom: 12px; align-items: center; }
.param-name-input { flex: 2; }
.param-type-select { width: 100px; }
.param-unit-input { width: 80px; }
.param-default-input { flex: 1; }
.param-required-checkbox { width: 60px; }
.unit-suffix { margin-left: 8px; color: #64748b; }

.apply-content { display: flex; flex-direction: column; gap: 16px; }
.apply-info { color: #64748b; font-size: 13px; }
.apply-options { display: flex; gap: 16px; margin-top: 8px; }

@media (max-width: 1024px) { .templates-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); } }
@media (max-width: 768px) { .templates-grid { grid-template-columns: 1fr; } .filter-bar { flex-direction: column; } .filter-left { width: 100%; } }
</style>