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
        <div class="loading-tip">Vendor Templates</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="vendor-templates-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Templates</el-breadcrumb-item>
          <el-breadcrumb-item>Vendor Templates</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="loadTemplates" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
          Import Vendor Template
        </el-button>
      </div>
    </div>

    <!-- 厂商筛选 -->
    <div class="vendor-filter">
      <div class="vendor-list">
        <div
            v-for="vendor in vendors"
            :key="vendor.id"
            class="vendor-item"
            :class="{ active: selectedVendorId === vendor.id }"
            @click="selectVendor(vendor.id)"
        >
          <div class="vendor-avatar" :style="{ backgroundColor: vendor.color }">
            <el-icon><component :is="vendor.icon" /></el-icon>
          </div>
          <div class="vendor-info">
            <span class="vendor-name">{{ vendor.name }}</span>
            <span class="template-count">{{ getVendorTemplateCount(vendor.id) }} templates</span>
          </div>
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
        <el-select v-model="filterSystemType" placeholder="System Type" clearable style="width: 140px" @change="filterTemplates">
          <el-option label="All Systems" value="" />
          <el-option label="HVAC" value="hvac" />
          <el-option label="Lighting" value="lighting" />
          <el-option label="Security" value="sas" />
          <el-option label="Fire Alarm" value="fas" />
          <el-option label="Plumbing" value="plumbing" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 120px" @change="filterTemplates">
          <el-option label="All Status" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Deprecated" value="deprecated" />
        </el-select>
      </div>
      <div class="filter-right">
        <span class="total-count">{{ filteredTemplates.length }} templates found</span>
      </div>
    </div>

    <!-- 模板卡片列表 -->
    <div class="templates-grid">
      <div v-for="template in filteredTemplates" :key="template.id" class="template-card" @click="viewTemplate(template)">
        <div class="card-header">
          <div class="vendor-badge" :style="{ backgroundColor: getVendorColor(template.vendorId) }">
            <span>{{ getVendorName(template.vendorId).charAt(0) }}</span>
          </div>
          <div class="card-badge">
            <el-tag :type="template.status === 'active' ? 'success' : 'danger'" size="small">
              {{ template.status }}
            </el-tag>
          </div>
        </div>
        <div class="card-body">
          <h3 class="template-name">{{ template.name }}</h3>
          <p class="template-desc">{{ template.description || 'No description' }}</p>
          <div class="template-meta">
            <div class="meta-item">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ getVendorName(template.vendorId) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Monitor /></el-icon>
              <span>{{ getSystemLabel(template.systemType) }}</span>
            </div>
            <div class="meta-item">
              <el-icon><List /></el-icon>
              <span>{{ template.modelCount || 0 }} models</span>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <div class="version-info">
            <span class="version">v{{ template.version }}</span>
            <span class="updated">{{ formatDate(template.updatedAt) }}</span>
          </div>
          <div class="card-actions" @click.stop>
            <el-button size="small" text @click="editTemplate(template)">Edit</el-button>
            <el-button size="small" text type="primary" @click="viewModels(template)">Models</el-button>
            <el-dropdown trigger="click" @command="(cmd: string) => handleTemplateCommand(cmd, template)">
              <el-button size="small" text :icon="MoreFilled" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="duplicate">Duplicate</el-dropdown-item>
                  <el-dropdown-item command="export">Export</el-dropdown-item>
                  <el-dropdown-item command="preview">Preview</el-dropdown-item>
                  <el-dropdown-item divided command="deprecate" v-if="template.status === 'active'">Mark as Deprecated</el-dropdown-item>
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
      <el-empty description="No vendor templates found">
        <el-button type="primary" @click="openCreateDialog">Import Vendor Template</el-button>
      </el-empty>
    </div>

    <!-- 导入/编辑模板对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingTemplate ? 'Edit Vendor Template' : 'Import Vendor Template'" width="700px" @closed="resetForm">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Vendor" prop="vendorId">
              <el-select v-model="formData.vendorId" placeholder="Select vendor" style="width: 100%">
                <el-option v-for="vendor in vendors" :key="vendor.id" :label="vendor.name" :value="vendor.id" />
              </el-select>
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
        <el-form-item label="Template Name" prop="name">
          <el-input v-model="formData.name" placeholder="e.g., Carrier AHU Standard Template" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Template description" />
        </el-form-item>
        <el-form-item label="Version" prop="version">
          <el-input v-model="formData.version" placeholder="e.g., 1.0.0" />
        </el-form-item>
        <el-form-item label="Status" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio label="active">Active</el-radio>
            <el-radio label="deprecated">Deprecated</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-divider>Supported Device Models</el-divider>

        <div class="models-editor">
          <div class="models-header">
            <span>Model Name</span>
            <span>Series</span>
            <span>Protocol</span>
            <span>Firmware Min</span>
            <span></span>
          </div>
          <div v-for="(model, index) in formData.models" :key="index" class="model-row">
            <el-input v-model="model.name" placeholder="e.g., 39G" size="small" style="width: 180px" />
            <el-input v-model="model.series" placeholder="e.g., AquaSnap" size="small" style="width: 150px" />
            <el-select v-model="model.protocol" placeholder="Protocol" size="small" style="width: 120px">
              <el-option label="BACnet" value="bacnet" />
              <el-option label="Modbus" value="modbus" />
              <el-option label="OPC UA" value="opcua" />
              <el-option label="MQTT" value="mqtt" />
              <el-option label="SNMP" value="snmp" />
            </el-select>
            <el-input v-model="model.firmwareMin" placeholder="e.g., 2.0" size="small" style="width: 100px" />
            <el-button type="danger" size="small" :icon="Delete" circle @click="removeModel(index)" />
          </div>
          <el-button type="primary" size="small" :icon="Plus" @click="addModel" style="margin-top: 12px">
            Add Model
          </el-button>
        </div>

        <el-divider>Parameter Configuration</el-divider>

        <div class="parameters-editor">
          <div class="parameters-header">
            <span>Parameter Name</span>
            <span>Type</span>
            <span>Unit</span>
            <span>Default</span>
            <span>Required</span>
            <span></span>
          </div>
          <div v-for="(param, index) in formData.parameters" :key="index" class="parameter-row">
            <el-input v-model="param.name" placeholder="e.g., Supply Air Temp" size="small" style="width: 180px" />
            <el-select v-model="param.type" placeholder="Type" size="small" style="width: 100px">
              <el-option label="Number" value="number" />
              <el-option label="String" value="string" />
              <el-option label="Boolean" value="boolean" />
              <el-option label="Enum" value="enum" />
            </el-select>
            <el-input v-model="param.unit" placeholder="e.g., °C" size="small" style="width: 80px" />
            <el-input v-model="param.defaultValue" placeholder="Default" size="small" style="width: 100px" />
            <el-checkbox v-model="param.required" style="width: 60px" />
            <el-button type="danger" size="small" :icon="Delete" circle @click="removeParameter(index)" />
          </div>
          <el-button type="primary" size="small" :icon="Plus" @click="addParameter" style="margin-top: 12px">
            Add Parameter
          </el-button>
        </div>

        <el-divider>Communication Settings</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Default Port">
              <el-input-number v-model="formData.communication.defaultPort" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Timeout (ms)">
              <el-input-number v-model="formData.communication.timeout" :min="1000" :max="60000" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Retry Count">
              <el-input-number v-model="formData.communication.retryCount" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Polling Interval (s)">
              <el-input-number v-model="formData.communication.pollingInterval" :min="5" :max="3600" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTemplate" :loading="saving">Save Template</el-button>
      </template>
    </el-dialog>

    <!-- 设备型号列表对话框 -->
    <el-dialog v-model="modelsDialogVisible" :title="`Device Models - ${selectedTemplate?.name}`" width="600px">
      <el-table :data="selectedTemplate?.models || []" stripe border>
        <el-table-column prop="name" label="Model Name" width="180" />
        <el-table-column prop="series" label="Series" width="150" />
        <el-table-column prop="protocol" label="Protocol" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.protocol?.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="firmwareMin" label="Min Firmware" width="120" />
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'warning'" size="small">{{ row.status || 'active' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="modelsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="applyToDevices">Apply to Devices</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Refresh, Plus, Search, MoreFilled, Monitor, List, Delete,
  OfficeBuilding, Cpu, ColdDrink, Sunny, Lock, Bell, MagicStick, Folder
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading vendor templates...')
const refreshing = ref(false)
const saving = ref(false)
const loadingMessages = ['Initializing...', 'Loading vendors...', 'Loading templates...', 'Almost ready...']

// ==================== Types ====================
interface Vendor {
  id: string
  name: string
  icon: string
  color: string
  description: string
}

interface DeviceModel {
  name: string
  series: string
  protocol: string
  firmwareMin: string
  status?: string
}

interface TemplateParameter {
  name: string
  type: 'number' | 'string' | 'boolean' | 'enum'
  unit: string
  defaultValue: any
  required: boolean
}

interface CommunicationSettings {
  defaultPort: number
  timeout: number
  retryCount: number
  pollingInterval: number
}

interface VendorTemplate {
  id: string
  vendorId: string
  name: string
  description: string
  systemType: 'hvac' | 'lighting' | 'sas' | 'fas' | 'plumbing'
  version: string
  status: 'active' | 'deprecated'
  models: DeviceModel[]
  parameters: TemplateParameter[]
  communication: CommunicationSettings
  modelCount: number
  createdAt: string
  updatedAt: string
}

// ==================== State ====================
const searchKeyword = ref('')
const filterSystemType = ref('')
const filterStatus = ref('')
const selectedVendorId = ref('')
const dialogVisible = ref(false)
const modelsDialogVisible = ref(false)
const editingTemplate = ref<VendorTemplate | null>(null)
const selectedTemplate = ref<VendorTemplate | null>(null)
const formRef = ref<FormInstance>()

// Mock 厂商数据
const vendors = ref<Vendor[]>([
  { id: 'carrier', name: 'Carrier', icon: 'Cpu', color: '#5470c6', description: 'HVAC Systems' },
  { id: 'daikin', name: 'Daikin', icon: 'Cpu', color: '#fac858', description: 'HVAC & Refrigeration' },
  { id: 'honeywell', name: 'Honeywell', icon: 'Cpu', color: '#ee6666', description: 'Building Controls' },
  { id: 'siemens', name: 'Siemens', icon: 'Cpu', color: '#73c0de', description: 'Industrial Automation' },
  { id: 'schneider', name: 'Schneider Electric', icon: 'Cpu', color: '#3ba272', description: 'Energy Management' },
  { id: 'johnson', name: 'Johnson Controls', icon: 'Cpu', color: '#fc8452', description: 'Building Solutions' },
  { id: 'philips', name: 'Philips', icon: 'Sunny', color: '#9a60b4', description: 'Lighting Systems' },
  { id: 'hikvision', name: 'Hikvision', icon: 'Lock', color: '#ea7ccc', description: 'Security & Surveillance' }
])

// Mock 模板数据
const templates = ref<VendorTemplate[]>([])

// 表单数据
const formData = ref({
  vendorId: '',
  name: '',
  description: '',
  systemType: 'hvac',
  version: '1.0.0',
  status: 'active',
  models: [] as DeviceModel[],
  parameters: [] as TemplateParameter[],
  communication: {
    defaultPort: 47808,
    timeout: 5000,
    retryCount: 3,
    pollingInterval: 30
  }
})

const formRules: FormRules = {
  vendorId: [{ required: true, message: 'Please select vendor', trigger: 'change' }],
  name: [{ required: true, message: 'Please enter template name', trigger: 'blur' }],
  systemType: [{ required: true, message: 'Please select system type', trigger: 'change' }],
  version: [{ required: true, message: 'Please enter version', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredTemplates = computed(() => {
  let result = [...templates.value]

  if (selectedVendorId.value) {
    result = result.filter(t => t.vendorId === selectedVendorId.value)
  }

  if (searchKeyword.value) {
    const kw = searchKeyword.value.toLowerCase()
    result = result.filter(t =>
        t.name.toLowerCase().includes(kw) ||
        t.description?.toLowerCase().includes(kw) ||
        t.models.some(m => m.name.toLowerCase().includes(kw))
    )
  }

  if (filterSystemType.value) {
    result = result.filter(t => t.systemType === filterSystemType.value)
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

const getVendorName = (vendorId: string) => {
  const vendor = vendors.value.find(v => v.id === vendorId)
  return vendor?.name || vendorId
}

const getVendorColor = (vendorId: string) => {
  const vendor = vendors.value.find(v => v.id === vendorId)
  return vendor?.color || '#909399'
}

const getVendorTemplateCount = (vendorId: string) => {
  return templates.value.filter(t => t.vendorId === vendorId).length
}

const selectVendor = (vendorId: string) => {
  selectedVendorId.value = selectedVendorId.value === vendorId ? '' : vendorId
}

// 生成模拟数据
const generateMockTemplates = (): VendorTemplate[] => {
  const now = new Date().toISOString()

  return [
    {
      id: '1',
      vendorId: 'carrier',
      name: 'Carrier AHU Standard Template',
      description: 'Standard template for Carrier Air Handling Units',
      systemType: 'hvac',
      version: '2.1.0',
      status: 'active',
      models: [
        { name: '39G', series: 'AquaSnap', protocol: 'bacnet', firmwareMin: '2.0', status: 'active' },
        { name: '39M', series: 'AquaForce', protocol: 'bacnet', firmwareMin: '1.8', status: 'active' },
        { name: '39C', series: 'WeatherMaster', protocol: 'modbus', firmwareMin: '3.0', status: 'beta' }
      ],
      parameters: [
        { name: 'Supply Air Temp', type: 'number', unit: '°C', defaultValue: 22.5, required: true },
        { name: 'Return Air Temp', type: 'number', unit: '°C', defaultValue: 24.0, required: true },
        { name: 'Fan Speed', type: 'number', unit: '%', defaultValue: 70, required: false }
      ],
      communication: { defaultPort: 47808, timeout: 5000, retryCount: 3, pollingInterval: 30 },
      modelCount: 3,
      createdAt: '2024-01-15T00:00:00Z',
      updatedAt: now
    },
    {
      id: '2',
      vendorId: 'daikin',
      name: 'Daikin FCU Configuration',
      description: 'Standard template for Daikin Fan Coil Units',
      systemType: 'hvac',
      version: '1.5.0',
      status: 'active',
      models: [
        { name: 'FXMQ', series: 'SkyAir', protocol: 'bacnet', firmwareMin: '1.2', status: 'active' },
        { name: 'FXDQ', series: 'VRV', protocol: 'modbus', firmwareMin: '2.0', status: 'active' }
      ],
      parameters: [
        { name: 'Fan Speed', type: 'number', unit: '%', defaultValue: 60, required: true },
        { name: 'Mode', type: 'enum', unit: '', defaultValue: 'auto', required: true }
      ],
      communication: { defaultPort: 502, timeout: 3000, retryCount: 3, pollingInterval: 30 },
      modelCount: 2,
      createdAt: '2024-01-20T00:00:00Z',
      updatedAt: now
    },
    {
      id: '3',
      vendorId: 'honeywell',
      name: 'Honeywell Fire Alarm Template',
      description: 'Standard configuration for Honeywell fire alarm systems',
      systemType: 'fas',
      version: '3.0.0',
      status: 'active',
      models: [
        { name: 'XLS', series: 'Notifier', protocol: 'bacnet', firmwareMin: '5.0', status: 'active' },
        { name: 'Gamewell-FCI', series: 'E3', protocol: 'modbus', firmwareMin: '4.2', status: 'active' }
      ],
      parameters: [
        { name: 'Sensitivity', type: 'number', unit: '%', defaultValue: 50, required: true },
        { name: 'Test Mode', type: 'boolean', unit: '', defaultValue: false, required: false }
      ],
      communication: { defaultPort: 47808, timeout: 5000, retryCount: 3, pollingInterval: 60 },
      modelCount: 2,
      createdAt: '2024-02-01T00:00:00Z',
      updatedAt: now
    },
    {
      id: '4',
      vendorId: 'philips',
      name: 'Philips Lighting Controller',
      description: 'Standard template for Philips Dynalite lighting systems',
      systemType: 'lighting',
      version: '2.0.0',
      status: 'active',
      models: [
        { name: 'Dynalite', series: 'DDRC', protocol: 'bacnet', firmwareMin: '1.0', status: 'active' },
        { name: 'Hue', series: 'Bridge', protocol: 'mqtt', firmwareMin: '2.0', status: 'beta' }
      ],
      parameters: [
        { name: 'Brightness', type: 'number', unit: '%', defaultValue: 80, required: true },
        { name: 'Color Temp', type: 'number', unit: 'K', defaultValue: 4000, required: false }
      ],
      communication: { defaultPort: 80, timeout: 3000, retryCount: 3, pollingInterval: 30 },
      modelCount: 2,
      createdAt: '2024-02-10T00:00:00Z',
      updatedAt: now
    },
    {
      id: '5',
      vendorId: 'hikvision',
      name: 'Hikvision Access Control',
      description: 'Standard template for Hikvision access control systems',
      systemType: 'sas',
      version: '1.8.0',
      status: 'active',
      models: [
        { name: 'DS-K2600', series: 'Access Controller', protocol: 'bacnet', firmwareMin: '2.0', status: 'active' },
        { name: 'DS-K1T671', series: 'Face Recognition', protocol: 'mqtt', firmwareMin: '1.5', status: 'active' }
      ],
      parameters: [
        { name: 'Door Timeout', type: 'number', unit: 's', defaultValue: 5, required: true },
        { name: 'Lock Mode', type: 'enum', unit: '', defaultValue: 'auto', required: true }
      ],
      communication: { defaultPort: 8000, timeout: 5000, retryCount: 3, pollingInterval: 15 },
      modelCount: 2,
      createdAt: '2024-02-15T00:00:00Z',
      updatedAt: now
    },
    {
      id: '6',
      vendorId: 'siemens',
      name: 'Siemens PLC Template',
      description: 'Standard configuration for Siemens PLCs',
      systemType: 'hvac',
      version: '4.2.0',
      status: 'deprecated',
      models: [
        { name: 'S7-1200', series: 'SIMATIC', protocol: 'opcua', firmwareMin: '4.0', status: 'deprecated' },
        { name: 'S7-1500', series: 'SIMATIC', protocol: 'opcua', firmwareMin: '2.0', status: 'active' }
      ],
      parameters: [
        { name: 'Cycle Time', type: 'number', unit: 'ms', defaultValue: 100, required: true }
      ],
      communication: { defaultPort: 4840, timeout: 10000, retryCount: 5, pollingInterval: 60 },
      modelCount: 2,
      createdAt: '2023-06-01T00:00:00Z',
      updatedAt: '2024-03-01T00:00:00Z'
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

const openCreateDialog = () => {
  editingTemplate.value = null
  resetForm()
  dialogVisible.value = true
}

const editTemplate = (template: VendorTemplate) => {
  editingTemplate.value = template
  formData.value = {
    vendorId: template.vendorId,
    name: template.name,
    description: template.description,
    systemType: template.systemType,
    version: template.version,
    status: template.status,
    models: JSON.parse(JSON.stringify(template.models)),
    parameters: JSON.parse(JSON.stringify(template.parameters)),
    communication: { ...template.communication }
  }
  dialogVisible.value = true
}

const resetForm = () => {
  formData.value = {
    vendorId: '',
    name: '',
    description: '',
    systemType: 'hvac',
    version: '1.0.0',
    status: 'active',
    models: [],
    parameters: [],
    communication: { defaultPort: 47808, timeout: 5000, retryCount: 3, pollingInterval: 30 }
  }
  if (formRef.value) formRef.value.clearValidate()
}

const addModel = () => {
  formData.value.models.push({
    name: '',
    series: '',
    protocol: 'bacnet',
    firmwareMin: '',
    status: 'active'
  })
}

const removeModel = (index: number) => {
  formData.value.models.splice(index, 1)
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
            modelCount: formData.value.models.length,
            updatedAt: new Date().toISOString()
          }
        }
        ElMessage.success('Template updated successfully')
      } else {
        const newTemplate: VendorTemplate = {
          id: Date.now().toString(),
          ...formData.value,
          modelCount: formData.value.models.length,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        templates.value.push(newTemplate)
        ElMessage.success('Template imported successfully')
      }

      dialogVisible.value = false
      saving.value = false
    }
  })
}

const viewTemplate = (template: VendorTemplate) => {
  ElMessage.info(`Viewing template: ${template.name}`)
}

const viewModels = (template: VendorTemplate) => {
  selectedTemplate.value = template
  modelsDialogVisible.value = true
}

const applyToDevices = () => {
  ElMessage.info(`Applying template to devices...`)
  modelsDialogVisible.value = false
}

const handleTemplateCommand = (command: string, template: VendorTemplate) => {
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
    case 'deprecate':
      deprecateTemplate(template)
      break
    case 'delete':
      deleteTemplate(template)
      break
  }
}

const duplicateTemplate = (template: VendorTemplate) => {
  const newTemplate: VendorTemplate = {
    ...template,
    id: Date.now().toString(),
    name: `${template.name} (Copy)`,
    version: '1.0.0',
    status: 'active',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
  templates.value.push(newTemplate)
  ElMessage.success(`Template duplicated: ${newTemplate.name}`)
}

const exportTemplate = (template: VendorTemplate) => {
  const dataStr = JSON.stringify(template, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${template.vendorId}_${template.name.replace(/\s/g, '_')}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success(`Template exported: ${template.name}`)
}

const previewTemplate = (template: VendorTemplate) => {
  ElMessage.info(`Previewing template: ${template.name}`)
}

const deprecateTemplate = async (template: VendorTemplate) => {
  try {
    await ElMessageBox.confirm(
        `Mark template "${template.name}" as deprecated?`,
        'Confirm Deprecate',
        { confirmButtonText: 'Deprecate', cancelButtonText: 'Cancel', type: 'warning' }
    )
    const index = templates.value.findIndex(t => t.id === template.id)
    if (index !== -1) {
      templates.value[index].status = 'deprecated'
    }
    ElMessage.success('Template marked as deprecated')
  } catch (error) {
    // cancelled
  }
}

const deleteTemplate = async (template: VendorTemplate) => {
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

.vendor-templates-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.vendor-filter { background: white; border-radius: 12px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.vendor-list { display: flex; flex-wrap: wrap; gap: 12px; }
.vendor-item { display: flex; align-items: center; gap: 12px; padding: 10px 16px; border-radius: 12px; cursor: pointer; transition: all 0.3s ease; background: #f8fafc; }
.vendor-item:hover { background: #ecf5ff; }
.vendor-item.active { background: #ecf5ff; border: 1px solid #409eff; }
.vendor-avatar { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.vendor-avatar .el-icon { font-size: 20px; }
.vendor-info { display: flex; flex-direction: column; }
.vendor-name { font-weight: 600; color: #1e293b; font-size: 14px; }
.template-count { font-size: 11px; color: #64748b; }

.filter-bar { display: flex; justify-content: space-between; align-items: center; background: white; padding: 16px 20px; border-radius: 12px; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.filter-left { display: flex; gap: 12px; flex-wrap: wrap; }
.total-count { font-size: 13px; color: #64748b; }

.templates-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 20px; }
.template-card { background: white; border-radius: 16px; overflow: hidden; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.template-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }
.card-header { padding: 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; }
.vendor-badge { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; }
.card-badge .el-tag { font-size: 11px; }
.card-body { padding: 16px; }
.template-name { margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.template-desc { margin: 0 0 12px 0; font-size: 13px; color: #64748b; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.template-meta { display: flex; gap: 16px; }
.meta-item { display: flex; align-items: center; gap: 4px; font-size: 12px; color: #94a3b8; }
.card-footer { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #f8fafc; border-top: 1px solid #e2e8f0; }
.version-info { display: flex; gap: 12px; font-size: 12px; }
.version { font-weight: 500; color: #409eff; }
.updated { color: #94a3b8; }
.card-actions { display: flex; gap: 4px; }

.empty-state { padding: 60px; text-align: center; background: white; border-radius: 16px; }

.models-editor, .parameters-editor { border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }
.models-header, .parameters-header { display: flex; gap: 12px; padding-bottom: 12px; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; font-size: 12px; font-weight: 500; color: #64748b; }
.model-row, .parameter-row { display: flex; gap: 12px; margin-bottom: 12px; align-items: center; }

@media (max-width: 1024px) { .templates-grid { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); } }
@media (max-width: 768px) { .templates-grid { grid-template-columns: 1fr; } .filter-bar { flex-direction: column; } .filter-left { width: 100%; } .vendor-list { flex-direction: column; } }
</style>