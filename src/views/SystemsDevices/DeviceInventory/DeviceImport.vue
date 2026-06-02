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
        <div class="loading-tip">Device Import</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="device-import-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Device Inventory
          </el-breadcrumb-item>
          <el-breadcrumb-item>Import Devices</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>

    <!-- 导入步骤 -->
    <div class="import-steps">
      <el-steps :active="currentStep" align-center finish-status="success">
        <el-step title="Select Method" description="Choose import method" />
        <el-step title="Configure" description="Fill in device details" />
        <el-step title="Preview" description="Review imported devices" />
        <el-step title="Complete" description="Import finished" />
      </el-steps>
    </div>

    <!-- Step 1: 选择导入方式 -->
    <div v-if="currentStep === 1" class="step-content">
      <div class="method-cards">
        <div class="method-card" :class="{ selected: importMethod === 'single' }" @click="importMethod = 'single'">
          <div class="method-icon"><el-icon><Plus /></el-icon></div>
          <h3>Single Device</h3>
          <p>Add one device manually</p>
        </div>
        <div class="method-card" :class="{ selected: importMethod === 'batch' }" @click="importMethod = 'batch'">
          <div class="method-icon"><el-icon><DocumentAdd /></el-icon></div>
          <h3>Batch Import</h3>
          <p>Import multiple devices at once</p>
        </div>
        <div class="method-card" :class="{ selected: importMethod === 'template' }" @click="importMethod = 'template'">
          <div class="method-icon"><el-icon><Download /></el-icon></div>
          <h3>Excel Template</h3>
          <p>Upload from Excel file</p>
        </div>
      </div>

      <div class="step-actions">
        <el-button type="primary" size="large" @click="goToNextStep" :disabled="!importMethod">
          Next
        </el-button>
      </div>
    </div>

    <!-- Step 2: 配置设备信息 -->
    <div v-if="currentStep === 2" class="step-content">
      <!-- 单台设备导入表单 -->
      <div v-if="importMethod === 'single'" class="single-device-form">
        <div class="form-section">
          <h3><el-icon><InfoFilled /></el-icon> Basic Information</h3>
          <el-form :model="singleDevice" :rules="deviceRules" ref="singleDeviceFormRef" label-width="140px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Device Name *" prop="name">
                  <el-input v-model="singleDevice.name" placeholder="e.g., AHU-01" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Model" prop="model">
                  <el-input v-model="singleDevice.model" placeholder="e.g., Carrier 39G" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Manufacturer" prop="manufacturer">
                  <el-input v-model="singleDevice.manufacturer" placeholder="e.g., Carrier" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Serial Number" prop="serialNumber">
                  <el-input v-model="singleDevice.serialNumber" placeholder="Unique serial number" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="System Type *" prop="systemType">
                  <el-select v-model="singleDevice.systemType" placeholder="Select system type" style="width: 100%">
                    <el-option label="HVAC" value="hvac" />
                    <el-option label="Lighting" value="lighting" />
                    <el-option label="Security" value="sas" />
                    <el-option label="Fire Alarm" value="fas" />
                    <el-option label="Plumbing" value="plumbing" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Status" prop="status">
                  <el-select v-model="singleDevice.status" placeholder="Select status" style="width: 100%">
                    <el-option label="Online" value="online" />
                    <el-option label="Offline" value="offline" />
                    <el-option label="Warning" value="warning" />
                    <el-option label="Error" value="error" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Area *" prop="area">
                  <el-select v-model="singleDevice.area" placeholder="Select area" style="width: 100%">
                    <el-option label="Basement B2" value="Basement B2" />
                    <el-option label="Parking B1" value="Parking B1" />
                    <el-option label="Lobby 1F" value="Lobby 1F" />
                    <el-option label="Office 2F" value="Office 2F" />
                    <el-option label="Executive 3F" value="Executive 3F" />
                    <el-option label="Roof Mechanical" value="Roof Mechanical" />
                    <el-option label="Create New Area" value="__new__" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12" v-if="singleDevice.area === '__new__'">
                <el-form-item label="New Area Name" prop="newAreaName">
                  <el-input v-model="singleDevice.newAreaName" placeholder="Enter new area name" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <div class="form-section">
          <h3><el-icon><Odometer /></el-icon> Initial Metrics</h3>
          <el-form label-width="140px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Temperature">
                  <el-input-number v-model="singleDevice.temperature" :min="-10" :max="50" :step="0.5" style="width: 100%" />
                  <span class="unit-suffix">°C</span>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Humidity">
                  <el-input-number v-model="singleDevice.humidity" :min="0" :max="100" style="width: 100%" />
                  <span class="unit-suffix">%</span>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Power">
                  <el-input-number v-model="singleDevice.power" :min="0" :step="0.5" style="width: 100%" />
                  <span class="unit-suffix">kW</span>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Efficiency">
                  <el-input-number v-model="singleDevice.efficiency" :min="0" :max="100" style="width: 100%" />
                  <span class="unit-suffix">%</span>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <div class="form-section">
          <h3><el-icon><Calendar /></el-icon> Maintenance Schedule</h3>
          <el-form label-width="140px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Installation Date">
                  <el-date-picker v-model="singleDevice.installationDate" type="date" placeholder="Select date" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Next Maintenance">
                  <el-date-picker v-model="singleDevice.nextMaintenance" type="date" placeholder="Select date" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </div>

      <!-- 批量导入表单 -->
      <div v-if="importMethod === 'batch'" class="batch-import-form">
        <div class="batch-input-area">
          <div class="batch-header">
            <h3><el-icon><Edit /></el-icon> Batch Device Input</h3>
            <el-button type="primary" size="small" @click="addBatchRow">Add Row</el-button>
          </div>
          <el-table :data="batchDevices" border stripe style="width: 100%" max-height="500">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column label="Device Name *" min-width="150">
              <template #default="{ row, $index }">
                <el-input v-model="row.name" placeholder="Device name" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="Model" min-width="120">
              <template #default="{ row }">
                <el-input v-model="row.model" placeholder="Model" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="Manufacturer" min-width="120">
              <template #default="{ row }">
                <el-input v-model="row.manufacturer" placeholder="Manufacturer" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="System Type *" width="130">
              <template #default="{ row }">
                <el-select v-model="row.systemType" placeholder="Select" size="small" style="width: 100%">
                  <el-option label="HVAC" value="hvac" />
                  <el-option label="Lighting" value="lighting" />
                  <el-option label="Security" value="sas" />
                  <el-option label="Fire Alarm" value="fas" />
                  <el-option label="Plumbing" value="plumbing" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="Area *" width="140">
              <template #default="{ row }">
                <el-select v-model="row.area" placeholder="Select area" size="small" style="width: 100%">
                  <el-option label="Basement B2" value="Basement B2" />
                  <el-option label="Parking B1" value="Parking B1" />
                  <el-option label="Lobby 1F" value="Lobby 1F" />
                  <el-option label="Office 2F" value="Office 2F" />
                  <el-option label="Executive 3F" value="Executive 3F" />
                  <el-option label="Roof Mechanical" value="Roof Mechanical" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="Status" width="100">
              <template #default="{ row }">
                <el-select v-model="row.status" size="small" style="width: 100%">
                  <el-option label="Online" value="online" />
                  <el-option label="Offline" value="offline" />
                  <el-option label="Warning" value="warning" />
                  <el-option label="Error" value="error" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="60">
              <template #default="{ $index }">
                <el-button type="danger" size="small" text @click="removeBatchRow($index)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="batch-actions">
            <el-button type="primary" plain @click="fillSampleData">Load Sample Data</el-button>
            <el-button type="danger" plain @click="clearBatchData">Clear All</el-button>
          </div>
        </div>

        <div class="batch-defaults">
          <h4>Default Values (applied to empty fields)</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="Default Status">
                <el-select v-model="batchDefaults.status" size="small">
                  <el-option label="Online" value="online" />
                  <el-option label="Offline" value="offline" />
                  <el-option label="Warning" value="warning" />
                  <el-option label="Error" value="error" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="Default Area">
                <el-select v-model="batchDefaults.area" size="small">
                  <el-option label="Basement B2" value="Basement B2" />
                  <el-option label="Lobby 1F" value="Lobby 1F" />
                  <el-option label="Office 2F" value="Office 2F" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- Excel 模板导入 -->
      <div v-if="importMethod === 'template'" class="template-import-form">
        <div class="upload-card">
          <div class="upload-area" :class="{ 'drag-over': isDragOver }"
               @dragover.prevent="isDragOver = true"
               @dragleave.prevent="isDragOver = false"
               @drop.prevent="handleDrop">
            <el-icon class="upload-icon"><Upload /></el-icon>
            <h3>Drag & Drop your Excel file here</h3>
            <p>or</p>
            <el-button type="primary" @click="triggerFileInput">
              <el-icon><FolderOpened /></el-icon>
              Browse Files
            </el-button>
            <input ref="fileInputRef" type="file" accept=".csv,.xlsx,.xls" style="display: none" @change="handleFileSelect" />
            <p class="upload-hint">Supported formats: CSV, Excel (.xlsx, .xls) | Max size: 10MB</p>
          </div>

          <div v-if="selectedFile" class="selected-file">
            <div class="file-info">
              <el-icon><Document /></el-icon>
              <span>{{ selectedFile.name }}</span>
              <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
            </div>
            <div class="file-actions">
              <el-button type="primary" size="small" @click="parseFile" :loading="parsing">Parse File</el-button>
              <el-button type="danger" size="small" text @click="clearFile">Remove</el-button>
            </div>
          </div>
        </div>

        <div class="template-tip">
          <el-alert title="Template Guide" type="info" :closable="false">
            <template #default>
              <p>Download the template file and fill in device information following these required columns:</p>
              <ul>
                <li><strong>Device Name</strong> - Required, unique device identifier</li>
                <li><strong>System Type</strong> - Required, values: hvac, lighting, sas, fas, plumbing</li>
                <li><strong>Area</strong> - Required, existing area name</li>
                <li><strong>Model, Manufacturer, Serial Number</strong> - Optional but recommended</li>
              </ul>
              <el-button type="primary" link @click="downloadTemplate">
                <el-icon><Download /></el-icon> Download Template
              </el-button>
            </template>
          </el-alert>
        </div>
      </div>

      <div class="step-actions">
        <el-button size="large" @click="currentStep = 1">Back</el-button>
        <el-button type="primary" size="large" @click="goToPreview" :loading="previewLoading">
          Next: Preview
        </el-button>
      </div>
    </div>

    <!-- Step 3: 预览导入设备 -->
    <div v-if="currentStep === 3" class="step-content">
      <div class="preview-card">
        <div class="preview-header">
          <h3><el-icon><View /></el-icon> Preview Imported Devices</h3>
          <div class="preview-stats">
            <el-tag type="success">{{ previewDevices.length }} devices to import</el-tag>
            <el-tag v-if="validationErrors.length === 0" type="success">All valid</el-tag>
            <el-tag v-else type="danger">{{ validationErrors.length }} issues</el-tag>
          </div>
        </div>

        <el-table :data="previewDevices" stripe border max-height="400" style="width: 100%">
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="name" label="Device Name" min-width="180" />
          <el-table-column prop="model" label="Model" min-width="150" />
          <el-table-column prop="manufacturer" label="Manufacturer" min-width="150" />
          <el-table-column prop="systemType" label="System Type" width="120">
            <template #default="{ row }">
              <el-tag :type="getSystemTagType(row.systemType)" size="small">{{ getSystemLabel(row.systemType) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="area" label="Area" width="120" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Valid" width="80">
            <template #default="{ row }">
              <el-icon v-if="row._valid" class="success-icon"><CircleCheckFilled /></el-icon>
              <el-icon v-else class="error-icon"><CircleCloseFilled /></el-icon>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="validationErrors.length > 0" class="validation-summary">
          <h4><el-icon><WarningFilled /></el-icon> Validation Issues</h4>
          <div class="validation-list">
            <div v-for="(err, idx) in validationErrors.slice(0, 10)" :key="idx" class="validation-item">
              <span class="validation-msg">{{ err }}</span>
            </div>
          </div>
        </div>

        <div class="step-actions">
          <el-button size="large" @click="currentStep = 2">Back</el-button>
          <el-button type="primary" size="large" @click="confirmImport" :loading="importing">
            Import {{ validCount }} Devices
          </el-button>
        </div>
      </div>
    </div>

    <!-- Step 4: 导入完成 -->
    <div v-if="currentStep === 4" class="step-content">
      <div class="complete-card" :class="{ 'has-error': importErrors.length > 0 }">
        <div class="complete-icon" :class="{ success: importErrors.length === 0, error: importErrors.length > 0 }">
          <el-icon v-if="importErrors.length === 0"><CircleCheckFilled /></el-icon>
          <el-icon v-else><CircleCloseFilled /></el-icon>
        </div>
        <h3>{{ importErrors.length === 0 ? 'Import Completed Successfully!' : 'Import Completed with Errors' }}</h3>
        <div class="complete-stats">
          <div class="stat-item">
            <span class="stat-label">Total processed:</span>
            <span class="stat-value">{{ importResult.total }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Successfully imported:</span>
            <span class="stat-value success">{{ importResult.success }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Failed:</span>
            <span class="stat-value danger">{{ importResult.failed }}</span>
          </div>
        </div>
        <div class="complete-actions">
          <el-button type="primary" @click="goToInventory">View Device List</el-button>
          <el-button @click="resetImport">Import More Devices</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import * as XLSX from 'xlsx'
import {
  Plus, DocumentAdd, Download, Upload, FolderOpened, Document, View,
  CircleCheckFilled, CircleCloseFilled, WarningFilled, InfoFilled,
  Odometer, Calendar, Edit, Delete, Setting
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing import module...')
const router = useRouter()
const loadingMessages = ['Initializing...', 'Loading import module...', 'Preparing...', 'Almost ready...']

// ==================== State ====================
const currentStep = ref(1)
const importMethod = ref('')
const previewLoading = ref(false)
const importing = ref(false)
const parsing = ref(false)
const isDragOver = ref(false)
const selectedFile = ref<File | null>(null)
const fileInputRef = ref<HTMLInputElement>()
const singleDeviceFormRef = ref<FormInstance>()

// 单台设备
const singleDevice = ref({
  name: '', model: '', manufacturer: '', serialNumber: '',
  systemType: '', status: 'online', area: '', newAreaName: '',
  temperature: 24, humidity: 50, power: 10, efficiency: 90,
  installationDate: new Date(), nextMaintenance: new Date(Date.now() + 90 * 24 * 3600000)
})

// 批量导入设备列表
const batchDevices = ref([
  { name: '', model: '', manufacturer: '', systemType: '', area: '', status: 'online' }
])

const batchDefaults = ref({
  status: 'online',
  area: 'Basement B2'
})

// 预览设备列表
const previewDevices = ref<any[]>([])
const validationErrors = ref<string[]>([])
const importResult = ref({ total: 0, success: 0, failed: 0 })
const importErrors = ref<string[]>([])

// ==================== Computed ====================
const validCount = computed(() => previewDevices.value.filter(d => d._valid).length)

// ==================== Validation Rules ====================
const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  systemType: [{ required: true, message: 'Please select system type', trigger: 'change' }],
  area: [{ required: true, message: 'Please select area', trigger: 'change' }]
}

// ==================== Helper Functions ====================
const getSystemLabel = (type: string) => {
  const labels: Record<string, string> = {
    hvac: 'HVAC', lighting: 'Lighting', sas: 'Security', fas: 'Fire Alarm', plumbing: 'Plumbing'
  }
  return labels[type] || type
}

const getSystemTagType = (type: string) => {
  const types: Record<string, string> = {
    hvac: 'primary', lighting: 'success', sas: 'danger', fas: 'warning', plumbing: 'info'
  }
  return types[type] || 'info'
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    online: 'success', offline: 'info', warning: 'warning', error: 'danger'
  }
  return types[status] || 'info'
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const goToInventory = () => router.push('/systems-devices/device-inventory/device-list')

// ==================== Step Navigation ====================
const goToNextStep = () => {
  if (importMethod.value) {
    currentStep.value = 2
    if (importMethod.value === 'batch' && batchDevices.value.length === 0) {
      addBatchRow()
    }
  }
}

const goToPreview = async () => {
  if (importMethod.value === 'single') {
    if (!singleDeviceFormRef.value) return
    await singleDeviceFormRef.value.validate(async (valid) => {
      if (valid) {
        previewLoading.value = true
        await buildPreviewDevices()
        previewLoading.value = false
        currentStep.value = 3
      }
    })
  } else if (importMethod.value === 'batch') {
    previewLoading.value = true
    await buildBatchPreview()
    previewLoading.value = false
    currentStep.value = 3
  } else if (importMethod.value === 'template') {
    if (!selectedFile.value) {
      ElMessage.warning('Please select a file first')
      return
    }
    previewLoading.value = true
    await parseFile()
    previewLoading.value = false
    currentStep.value = 3
  }
}

// ==================== Build Preview ====================
const buildPreviewDevices = async () => {
  const area = singleDevice.value.area === '__new__' ? singleDevice.value.newAreaName : singleDevice.value.area
  const device = {
    name: singleDevice.value.name,
    model: singleDevice.value.model || 'Unknown',
    manufacturer: singleDevice.value.manufacturer || 'Unknown',
    serialNumber: singleDevice.value.serialNumber || `SN-${Date.now()}`,
    systemType: singleDevice.value.systemType,
    area: area,
    status: singleDevice.value.status,
    temperature: singleDevice.value.temperature,
    humidity: singleDevice.value.humidity,
    power: singleDevice.value.power,
    efficiency: singleDevice.value.efficiency,
    installationDate: singleDevice.value.installationDate?.toISOString().split('T')[0] || new Date().toISOString().split('T')[0],
    nextMaintenance: singleDevice.value.nextMaintenance?.toISOString().split('T')[0] || new Date(Date.now() + 90 * 24 * 3600000).toISOString().split('T')[0],
    _valid: !!(singleDevice.value.name && singleDevice.value.systemType && area)
  }
  previewDevices.value = [device]
  validatePreview()
}

const buildBatchPreview = async () => {
  previewDevices.value = batchDevices.value.map(device => {
    const area = device.area || batchDefaults.value.area
    const status = device.status || batchDefaults.value.status
    const valid = !!(device.name && device.systemType && area)
    return {
      ...device,
      model: device.model || 'Unknown',
      manufacturer: device.manufacturer || 'Unknown',
      serialNumber: device.serialNumber || `SN-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`,
      area,
      status,
      temperature: 24,
      humidity: 50,
      power: 10,
      efficiency: 90,
      installationDate: new Date().toISOString().split('T')[0],
      nextMaintenance: new Date(Date.now() + 90 * 24 * 3600000).toISOString().split('T')[0],
      _valid: valid
    }
  })
  validatePreview()
}

const validatePreview = () => {
  validationErrors.value = []
  previewDevices.value.forEach((device, idx) => {
    if (!device._valid) {
      validationErrors.value.push(`Row ${idx + 1}: Missing required fields (Name, System Type, Area)`)
    }
  })
}

// ==================== Batch Operations ====================
const addBatchRow = () => {
  batchDevices.value.push({ name: '', model: '', manufacturer: '', systemType: '', area: '', status: 'online' })
}

const removeBatchRow = (index: number) => {
  batchDevices.value.splice(index, 1)
}

const fillSampleData = () => {
  batchDevices.value = [
    { name: 'AHU-B2-01', model: 'Carrier 39G', manufacturer: 'Carrier', systemType: 'hvac', area: 'Basement B2', status: 'online' },
    { name: 'FCU-B2-01', model: 'Daikin FXMQ', manufacturer: 'Daikin', systemType: 'hvac', area: 'Basement B2', status: 'online' },
    { name: 'CH-B2-01', model: 'Carrier AquaEdge', manufacturer: 'Carrier', systemType: 'hvac', area: 'Basement B2', status: 'online' },
    { name: 'Lighting Controller', model: 'Philips Dynalite', manufacturer: 'Philips', systemType: 'lighting', area: 'Lobby 1F', status: 'online' },
    { name: 'Access Controller', model: 'HID VertX', manufacturer: 'HID', systemType: 'sas', area: 'Lobby 1F', status: 'online' }
  ]
  ElMessage.success('Sample data loaded')
}

const clearBatchData = () => {
  batchDevices.value = [{ name: '', model: '', manufacturer: '', systemType: '', area: '', status: 'online' }]
  ElMessage.info('Batch data cleared')
}

// ==================== File Operations ====================
const triggerFileInput = () => fileInputRef.value?.click()

const clearFile = () => {
  selectedFile.value = null
  if (fileInputRef.value) fileInputRef.value.value = ''
  previewDevices.value = []
}

const handleDrop = (e: DragEvent) => {
  isDragOver.value = false
  const files = e.dataTransfer?.files
  if (files && files.length > 0) handleFile(files[0])
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files.length > 0) handleFile(input.files[0])
}

const handleFile = (file: File) => {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['csv', 'xlsx', 'xls'].includes(ext || '')) {
    ElMessage.error('Please upload CSV or Excel file')
    return
  }
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('File size must be less than 10MB')
    return
  }
  selectedFile.value = file
}

const parseFile = async () => {
  if (!selectedFile.value) return
  parsing.value = true

  try {
    const data = await readFile(selectedFile.value)
    if (data.length > 0) {
      previewDevices.value = data.map((row: any, idx: number) => {
        const systemTypeMap: Record<string, string> = {
          'HVAC': 'hvac', 'Lighting': 'lighting', 'Security': 'sas', 'FireAlarm': 'fas', 'Plumbing': 'plumbing'
        }
        const systemType = systemTypeMap[row['System Type']] || row['systemType']?.toLowerCase() || ''
        const area = row['Area'] || row['area'] || ''
        const name = row['Device Name'] || row['name'] || ''
        const valid = !!(name && systemType && area)

        return {
          name,
          model: row['Model'] || row['model'] || 'Unknown',
          manufacturer: row['Manufacturer'] || row['manufacturer'] || 'Unknown',
          serialNumber: row['Serial Number'] || row['serialNumber'] || `SN-${Date.now()}-${idx}`,
          systemType,
          area,
          status: row['Status'] || row['status'] || 'online',
          temperature: parseFloat(row['Temperature']) || 24,
          humidity: parseFloat(row['Humidity']) || 50,
          power: parseFloat(row['Power']) || 10,
          efficiency: parseFloat(row['Efficiency']) || 90,
          installationDate: row['Installation Date'] || new Date().toISOString().split('T')[0],
          _valid: valid
        }
      })
      validatePreview()
      ElMessage.success(`Parsed ${previewDevices.value.length} devices from file`)
    } else {
      ElMessage.error('No data found in file')
    }
  } catch (error) {
    ElMessage.error('Failed to parse file')
  } finally {
    parsing.value = false
  }
}

const readFile = (file: File): Promise<any[]> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = e.target?.result
        let jsonData: any[] = []

        if (file.name.endsWith('.csv')) {
          const text = data as string
          const lines = text.split(/\r?\n/)
          const headers = lines[0].split(',').map(h => h.trim())
          jsonData = lines.slice(1).filter(line => line.trim()).map(line => {
            const values = line.split(',').map(v => v.trim())
            const row: any = {}
            headers.forEach((h, i) => { row[h] = values[i] || '' })
            return row
          })
        } else {
          const workbook = XLSX.read(data, { type: 'binary' })
          const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
          jsonData = XLSX.utils.sheet_to_json(firstSheet)
        }
        resolve(jsonData)
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = () => reject(reader.error)

    if (file.name.endsWith('.csv')) {
      reader.readAsText(file, 'UTF-8')
    } else {
      reader.readAsBinaryString(file)
    }
  })
}

const downloadTemplate = () => {
  const templateData = [
    { 'Device Name': 'AHU-01', 'Model': 'Carrier 39G', 'Manufacturer': 'Carrier', 'System Type': 'HVAC', 'Area': 'Basement B2', 'Status': 'online', 'Temperature': 23.5, 'Humidity': 55, 'Power': 18.5, 'Efficiency': 94, 'Serial Number': 'SN-001' },
    { 'Device Name': 'FCU-01', 'Model': 'Daikin FXMQ', 'Manufacturer': 'Daikin', 'System Type': 'HVAC', 'Area': 'Office 2F', 'Status': 'online', 'Temperature': 22.5, 'Humidity': 48, 'Power': 6.8, 'Efficiency': 91, 'Serial Number': 'SN-002' }
  ]
  const ws = XLSX.utils.json_to_sheet(templateData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Device Template')
  XLSX.writeFile(wb, `device_import_template_${new Date().toISOString().split('T')[0]}.xlsx`)
  ElMessage.success('Template downloaded')
}

// ==================== Import ====================
const confirmImport = async () => {
  const validDevices = previewDevices.value.filter(d => d._valid)
  if (validDevices.length === 0) {
    ElMessage.warning('No valid devices to import')
    return
  }

  importing.value = true
  importResult.value = { total: validDevices.length, success: 0, failed: 0 }
  importErrors.value = []

  for (let i = 0; i < validDevices.length; i++) {
    const device = validDevices[i]
    await new Promise(resolve => setTimeout(resolve, 200))

    try {
      const newDevice = {
        id: `dev-${Date.now()}-${i}-${Math.random().toString(36).substr(2, 4)}`,
        name: device.name,
        type: 'device',
        status: device.status,
        model: device.model,
        manufacturer: device.manufacturer,
        serialNumber: device.serialNumber,
        systemType: device.systemType,
        area: device.area,
        floor: device.area.substring(0, 2),
        imageUrl: 'https://aegisnx.com/wp-content/uploads/2026/05/1779084477643.png',
        metrics: {
          temperature: device.temperature,
          humidity: device.humidity,
          power: device.power,
          energy: 0,
          uptime: 0,
          efficiency: device.efficiency
        },
        lastMaintenance: new Date().toISOString().split('T')[0],
        nextMaintenance: device.nextMaintenance,
        installationDate: device.installationDate
      }
      console.log('Imported device:', newDevice)
      importResult.value.success++
    } catch (error) {
      importResult.value.failed++
      importErrors.value.push(`${device.name}: Import failed`)
    }
  }

  importing.value = false
  currentStep.value = 4
}

const resetImport = () => {
  currentStep.value = 1
  importMethod.value = ''
  selectedFile.value = null
  previewDevices.value = []
  validationErrors.value = []
  singleDevice.value = {
    name: '', model: '', manufacturer: '', serialNumber: '',
    systemType: '', status: 'online', area: '', newAreaName: '',
    temperature: 24, humidity: 50, power: 10, efficiency: 90,
    installationDate: new Date(), nextMaintenance: new Date(Date.now() + 90 * 24 * 3600000)
  }
  batchDevices.value = [{ name: '', model: '', manufacturer: '', systemType: '', area: '', status: 'online' }]
  if (fileInputRef.value) fileInputRef.value.value = ''
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
    setTimeout(() => { isLoaded.value = true }, 400)
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

.device-import-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { margin-bottom: 24px; }
.import-steps { background: white; padding: 24px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.step-content { animation: fadeIn 0.3s ease; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.method-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 32px; }
.method-card { background: white; border-radius: 16px; padding: 32px; text-align: center; cursor: pointer; border: 2px solid #e4e7ed; transition: all 0.3s ease; }
.method-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1); }
.method-card.selected { border-color: #409eff; background: #ecf5ff; }
.method-icon .el-icon { font-size: 48px; color: #409eff; margin-bottom: 16px; }
.method-card h3 { margin: 0 0 8px 0; font-size: 18px; }
.method-card p { margin: 0; color: #64748b; font-size: 13px; }

.step-actions { display: flex; justify-content: center; gap: 16px; margin-top: 32px; }

.form-section { background: white; border-radius: 16px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.form-section h3 { display: flex; align-items: center; gap: 8px; margin: 0 0 20px 0; font-size: 16px; }
.unit-suffix { margin-left: 8px; color: #64748b; font-size: 13px; }

.batch-input-area { background: white; border-radius: 16px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.batch-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.batch-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; }
.batch-actions { display: flex; justify-content: center; gap: 16px; margin-top: 20px; }
.batch-defaults { background: #f8fafc; border-radius: 12px; padding: 20px; }
.batch-defaults h4 { margin: 0 0 16px 0; font-size: 14px; color: #1e293b; }

.upload-card { background: white; border-radius: 16px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.upload-area { border: 2px dashed #d9d9d9; border-radius: 16px; padding: 48px; text-align: center; cursor: pointer; transition: all 0.3s ease; }
.upload-area:hover, .upload-area.drag-over { border-color: #409eff; background: #ecf5ff; }
.upload-icon { font-size: 48px; color: #409eff; margin-bottom: 16px; }
.upload-area h3 { margin: 0 0 8px 0; }
.upload-area p { color: #64748b; margin: 8px 0; }
.upload-hint { font-size: 12px; color: #94a3b8; margin-top: 16px; }
.selected-file { margin-top: 24px; padding: 16px 20px; background: #f8fafc; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.file-info { display: flex; align-items: center; gap: 12px; }
.file-size { color: #94a3b8; font-size: 12px; }
.file-actions { display: flex; gap: 8px; }
.template-tip { margin-top: 24px; }

.preview-card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.preview-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.preview-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; }
.preview-stats { display: flex; gap: 12px; }
.success-icon { color: #67c23a; font-size: 18px; }
.error-icon { color: #f56c6c; font-size: 18px; }
.validation-summary { margin-top: 20px; padding: 16px; background: #fef0f0; border-radius: 12px; border-left: 4px solid #e6a23c; }
.validation-summary h4 { display: flex; align-items: center; gap: 8px; margin: 0 0 12px 0; color: #e6a23c; }
.validation-list { max-height: 150px; overflow-y: auto; }
.validation-item { font-size: 13px; padding: 4px 0; }

.complete-card { text-align: center; background: white; border-radius: 16px; padding: 48px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.complete-icon { font-size: 64px; margin-bottom: 16px; }
.complete-icon.success { color: #67c23a; }
.complete-icon.error { color: #f56c6c; }
.complete-stats { display: flex; justify-content: center; gap: 48px; margin: 32px 0; }
.complete-stats .stat-item { text-align: center; }
.complete-stats .stat-label { display: block; font-size: 13px; color: #64748b; }
.complete-stats .stat-value { display: block; font-size: 28px; font-weight: 700; }
.complete-stats .stat-value.success { color: #67c23a; }
.complete-stats .stat-value.danger { color: #f56c6c; }
.complete-actions { display: flex; justify-content: center; gap: 16px; }

@media (max-width: 768px) {
  .device-import-page { padding: 12px; }
  .method-cards { grid-template-columns: 1fr; }
  .preview-header { flex-direction: column; align-items: flex-start; }
}
</style>