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
        <div class="loading-tip">OpenBIM Integration - COBie Mapping</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cobie-mapping-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>COBie Mapping</h1>
        <p>Map COBie spreadsheets to digital twin asset model for facility management integration</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="saveMappings">
          <el-icon><Check /></el-icon>
          Save Mappings
        </el-button>
        <el-button @click="importMappings">
          <el-icon><Upload /></el-icon>
          Import
        </el-button>
        <el-button @click="exportMappings">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button @click="validateMappings">
          <el-icon><VideoPlay /></el-icon>
          Validate
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
            <div class="stat-value">{{ stats.totalMappings }}</div>
            <div class="stat-label">Total Mappings</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeMappings }}</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.issuesDetected }}</div>
            <div class="stat-label">Issues Detected</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.coverage }}%</div>
            <div class="stat-label">Coverage</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- COBie Sheets Browser -->
      <el-col :xs="24" :lg="10">
        <div class="browser-card">
          <div class="card-header">
            <h3>COBie Sheets</h3>
            <el-input
                v-model="sheetSearch"
                placeholder="Search sheets..."
                clearable
                size="small"
                style="width: 160px"
                :prefix-icon="Search"
            />
          </div>
          <div class="sheet-list">
            <div
                v-for="sheet in filteredSheets"
                :key="sheet.name"
                class="sheet-item"
                :class="{ active: selectedSheet?.name === sheet.name }"
                @click="onSheetSelect(sheet)"
            >
              <div class="sheet-icon" :class="sheet.status">
                <el-icon><component :is="getSheetIcon(sheet.name)" /></el-icon>
              </div>
              <div class="sheet-info">
                <div class="sheet-name">{{ sheet.name }}</div>
                <div class="sheet-desc">{{ sheet.description }}</div>
              </div>
              <el-tag v-if="sheet.mapped" size="small" type="success" class="mapped-tag">Mapped</el-tag>
              <el-tag v-else-if="sheet.partial" size="small" type="warning" class="partial-tag">Partial</el-tag>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Mapping Configuration -->
      <el-col :xs="24" :lg="14">
        <div class="mapping-card">
          <div class="card-header">
            <h3>Mapping Configuration</h3>
            <div v-if="selectedSheet" class="selected-info">
              <el-tag type="primary" size="small">{{ selectedSheet.name }}</el-tag>
            </div>
          </div>

          <div v-if="!selectedSheet" class="no-selection">
            <el-icon><Document /></el-icon>
            <span>Select a COBie sheet from the left to configure mapping</span>
          </div>

          <div v-else class="mapping-form">
            <el-form :model="mappingForm" label-width="140px">
              <el-form-item label="COBie Sheet">
                <el-input :value="selectedSheet.name" disabled />
              </el-form-item>

              <el-form-item label="Target Asset Type">
                <el-select v-model="mappingForm.targetType" placeholder="Select asset type" style="width: 100%">
                  <el-option label="Facility" value="facility" />
                  <el-option label="Floor" value="floor" />
                  <el-option label="Space" value="space" />
                  <el-option label="Zone" value="zone" />
                  <el-option label="Equipment" value="equipment" />
                  <el-option label="Component" value="component" />
                  <el-option label="System" value="system" />
                  <el-option label="Contact" value="contact" />
                  <el-option label="Document" value="document" />
                  <el-option label="Job" value="job" />
                </el-select>
              </el-form-item>

              <el-form-item label="Target Class">
                <el-select v-model="mappingForm.targetClass" placeholder="Select class" style="width: 100%">
                  <el-option label="Asset" value="asset" />
                  <el-option label="System" value="system" />
                  <el-option label="Component" value="component" />
                  <el-option label="Space" value="space" />
                  <el-option label="Zone" value="zone" />
                  <el-option label="Document" value="document" />
                  <el-option label="Contact" value="contact" />
                </el-select>
              </el-form-item>

              <el-form-item label="Priority">
                <el-slider v-model="mappingForm.priority" :min="0" :max="100" :step="1" />
                <span class="param-hint">{{ mappingForm.priority }}%</span>
              </el-form-item>

              <el-form-item label="Field Mapping">
                <div class="field-mapping-list">
                  <div v-for="(field, idx) in mappingForm.fieldMappings" :key="idx" class="field-mapping-item">
                    <el-select v-model="field.cobieField" placeholder="COBie Field" size="small" style="width: 180px">
                      <el-option :label="f" :value="f" v-for="f in getAvailableFields(selectedSheet.name)" :key="f" />
                    </el-select>
                    <el-icon><Right /></el-icon>
                    <el-select v-model="field.targetField" placeholder="Target Field" size="small" style="width: 180px">
                      <el-option :label="f" :value="f" v-for="f in targetFields" :key="f" />
                    </el-select>
                    <el-select v-model="field.conversion" placeholder="Conversion" size="small" style="width: 130px" clearable>
                      <el-option label="None" value="" />
                      <el-option label="String → Title Case" value="title_case" />
                      <el-option label="String → Upper Case" value="upper_case" />
                      <el-option label="String → Lower Case" value="lower_case" />
                      <el-option label="Date Format" value="date_format" />
                      <el-option label="Unit Conversion" value="unit_convert" />
                    </el-select>
                    <el-button link type="danger" size="small" @click="removeFieldMapping(idx)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <el-button size="small" type="primary" link @click="addFieldMapping">
                    <el-icon><Plus /></el-icon>
                    Add Field Mapping
                  </el-button>
                </div>
              </el-form-item>

              <el-form-item label="Filter Condition">
                <el-input v-model="mappingForm.filterCondition" placeholder="e.g., Category = 'HVAC'" />
                <div class="form-hint">Optional SQL-like filter for selective mapping</div>
              </el-form-item>

              <el-form-item label="Status">
                <el-radio-group v-model="mappingForm.status">
                  <el-radio value="active">Active</el-radio>
                  <el-radio value="inactive">Inactive</el-radio>
                  <el-radio value="draft">Draft</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="Notes">
                <el-input v-model="mappingForm.notes" type="textarea" :rows="2" placeholder="Additional notes..." />
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="saveMapping">Save Mapping</el-button>
                <el-button @click="testMapping">Test Mapping</el-button>
                <el-button @click="resetMapping">Reset</el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Mappings Table -->
    <div class="mappings-table-wrapper">
      <div class="table-header">
        <h3>Active Mappings</h3>
        <div class="table-filters">
          <el-select v-model="tableFilter.type" placeholder="Filter by type" clearable size="small" style="width: 140px">
            <el-option label="All Types" value="" />
            <el-option label="Space" value="space" />
            <el-option label="Equipment" value="equipment" />
            <el-option label="Component" value="component" />
            <el-option label="Contact" value="contact" />
          </el-select>
          <el-input
              v-model="tableFilter.search"
              placeholder="Search..."
              clearable
              size="small"
              style="width: 180px"
              :prefix-icon="Search"
          />
        </div>
      </div>
      <el-table :data="filteredMappings" stripe>
        <el-table-column prop="sheet" label="COBie Sheet" width="140" />
        <el-table-column prop="targetType" label="Target Type" width="140" />
        <el-table-column prop="targetClass" label="Target Class" width="140" />
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.priority" :stroke-width="6" :show-text="false" />
          </template>
        </el-table-column>
        <el-table-column prop="fieldCount" label="Fields Mapped" width="110" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'draft' ? 'warning' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="editMapping(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteMapping(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Validation Results -->
    <div class="validation-card" v-if="validationResults.length > 0">
      <div class="card-header">
        <h3>Validation Results</h3>
        <el-button size="small" @click="validationResults = []">Clear</el-button>
      </div>
      <div class="validation-list">
        <div v-for="(result, idx) in validationResults" :key="idx" class="validation-item" :class="result.severity">
          <el-icon><component :is="result.severity === 'error' ? 'CircleClose' : result.severity === 'warning' ? 'Warning' : 'CircleCheck'" /></el-icon>
          <span>{{ result.message }}</span>
          <span class="validation-time">{{ result.time }}</span>
        </div>
      </div>
    </div>

    <!-- Test Mapping Dialog -->
    <el-dialog v-model="testDialog.visible" title="Test Mapping Result" width="550px">
      <div v-if="testDialog.result" class="test-result">
        <div class="test-icon" :class="testDialog.result.success ? 'success' : 'error'">
          <el-icon v-if="testDialog.result.success"><CircleCheck /></el-icon>
          <el-icon v-else><CircleClose /></el-icon>
        </div>
        <div class="test-message">{{ testDialog.result.message }}</div>
        <div class="test-details" v-if="testDialog.result.details">
          <div class="detail-row"><strong>Sample COBie Data:</strong></div>
          <pre>{{ JSON.stringify(testDialog.result.details.sample, null, 2) }}</pre>
          <div class="detail-row"><strong>Mapped Output:</strong></div>
          <pre>{{ JSON.stringify(testDialog.result.details.mapped, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Check,
  Upload,
  Download,
  VideoPlay,
  Document,
  CircleCheck,
  Warning,
  DataAnalysis,
  Search,
  Right,
  Delete,
  Plus,
  OfficeBuilding,
  Grid,
  House,
  Tools,
  User,
  Folder
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading COBie schema...',
  'Initializing mapping engine...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface COBieSheet {
  name: string
  description: string
  fields: string[]
  mapped: boolean
  partial: boolean
  status: 'mapped' | 'partial' | 'unmapped'
}

interface Mapping {
  id: string
  sheet: string
  targetType: string
  targetClass: string
  priority: number
  status: 'active' | 'inactive' | 'draft'
  fieldCount: number
  fieldMappings: Array<{ cobieField: string; targetField: string; conversion: string }>
  filterCondition: string
  notes: string
}

// ==================== 模拟数据 ====================
const cobieSheets = ref<COBieSheet[]>([
  { name: 'Contact', description: 'Organization and individual contacts', fields: ['Email', 'Phone', 'Organization', 'Department', 'FullName', 'GivenName', 'FamilyName'], mapped: true, partial: false, status: 'mapped' },
  { name: 'Facility', description: 'Site and building information', fields: ['SiteName', 'ProjectName', 'Location', 'Area', 'FacilityName'], mapped: true, partial: false, status: 'mapped' },
  { name: 'Floor', description: 'Building floor levels', fields: ['Name', 'Elevation', 'Height'], mapped: true, partial: false, status: 'mapped' },
  { name: 'Space', description: 'Room and area definitions', fields: ['Name', 'Floor', 'RoomTag', 'Category', 'Area', 'Height'], mapped: true, partial: false, status: 'mapped' },
  { name: 'Zone', description: 'Grouping of spaces', fields: ['Name', 'Category', 'Description'], mapped: false, partial: true, status: 'partial' },
  { name: 'Type', description: 'Product and equipment types', fields: ['Name', 'Category', 'Description', 'Manufacturer', 'Model'], mapped: true, partial: false, status: 'mapped' },
  { name: 'Component', description: 'Individual asset instances', fields: ['Name', 'TypeName', 'SerialNumber', 'Manufacturer', 'Model', 'Floor', 'Space'], mapped: true, partial: false, status: 'mapped' },
  { name: 'System', description: 'Grouping of components', fields: ['Name', 'Category', 'Description'], mapped: false, partial: true, status: 'partial' },
  { name: 'Assembly', description: 'Pre-assembled items', fields: ['Name', 'TypeName', 'Description'], mapped: false, partial: false, status: 'unmapped' },
  { name: 'Connection', description: 'Connections between components', fields: ['Name', 'Description'], mapped: false, partial: false, status: 'unmapped' },
  { name: 'Document', description: 'Reference documents', fields: ['Name', 'URL', 'Description'], mapped: false, partial: false, status: 'unmapped' },
  { name: 'Attribute', description: 'Extended properties', fields: ['Name', 'Value', 'Unit'], mapped: false, partial: false, status: 'unmapped' }
])

const targetFields = ref([
  'id', 'name', 'description', 'type', 'category', 'location', 'floor',
  'area', 'height', 'manufacturer', 'model', 'serialNumber', 'installDate',
  'status', 'contactEmail', 'contactPhone', 'organization', 'url'
])

const mappings = ref<Mapping[]>([
  { id: 'MAP-001', sheet: 'Contact', targetType: 'contact', targetClass: 'contact', priority: 95, status: 'active', fieldCount: 4, fieldMappings: [], filterCondition: '', notes: 'Contact person mapping' },
  { id: 'MAP-002', sheet: 'Facility', targetType: 'facility', targetClass: 'asset', priority: 100, status: 'active', fieldCount: 3, fieldMappings: [], filterCondition: '', notes: '' },
  { id: 'MAP-003', sheet: 'Space', targetType: 'space', targetClass: 'space', priority: 90, status: 'active', fieldCount: 5, fieldMappings: [], filterCondition: '', notes: '' },
  { id: 'MAP-004', sheet: 'Component', targetType: 'equipment', targetClass: 'asset', priority: 88, status: 'active', fieldCount: 6, fieldMappings: [], filterCondition: '', notes: 'Asset instance mapping' },
  { id: 'MAP-005', sheet: 'Type', targetType: 'component', targetClass: 'component', priority: 85, status: 'draft', fieldCount: 3, fieldMappings: [], filterCondition: '', notes: 'Needs review' }
])

const stats = reactive({
  totalMappings: 0,
  activeMappings: 0,
  issuesDetected: 2,
  coverage: 68
})

const mappingForm = reactive({
  targetType: '',
  targetClass: '',
  priority: 80,
  fieldMappings: [] as Array<{ cobieField: string; targetField: string; conversion: string }>,
  filterCondition: '',
  status: 'active' as 'active' | 'inactive' | 'draft',
  notes: ''
})

const selectedSheet = ref<COBieSheet | null>(null)
const sheetSearch = ref('')
const tableFilter = reactive({ type: '', search: '' })
const validationResults = ref<any[]>([])
const testDialog = reactive({ visible: false, result: null as any })

// ==================== 计算属性 ====================
const filteredSheets = computed(() => {
  let filtered = [...cobieSheets.value]
  if (sheetSearch.value) {
    const searchLower = sheetSearch.value.toLowerCase()
    filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(searchLower) ||
        s.description.toLowerCase().includes(searchLower)
    )
  }
  return filtered
})

const filteredMappings = computed(() => {
  let filtered = [...mappings.value]
  if (tableFilter.type) {
    filtered = filtered.filter(m => m.targetType === tableFilter.type)
  }
  if (tableFilter.search) {
    const searchLower = tableFilter.search.toLowerCase()
    filtered = filtered.filter(m =>
        m.sheet.toLowerCase().includes(searchLower) ||
        m.targetType.toLowerCase().includes(searchLower)
    )
  }
  return filtered
})

// ==================== 辅助函数 ====================
const getSheetIcon = (sheetName: string) => {
  const map: Record<string, any> = {
    'Contact': User,
    'Facility': OfficeBuilding,
    'Floor': Grid,
    'Space': House,
    'Zone': Folder,
    'Type': Tools,
    'Component': Tools,
    'System': DataAnalysis
  }
  return map[sheetName] || Document
}

const getAvailableFields = (sheetName: string) => {
  const sheet = cobieSheets.value.find(s => s.name === sheetName)
  return sheet?.fields || []
}

const updateStats = () => {
  stats.totalMappings = mappings.value.length
  stats.activeMappings = mappings.value.filter(m => m.status === 'active').length
  const mappedSheets = cobieSheets.value.filter(s => s.mapped).length
  stats.coverage = Math.round((mappedSheets / cobieSheets.value.length) * 100)
}

const onSheetSelect = (sheet: COBieSheet) => {
  selectedSheet.value = sheet

  // Find existing mapping
  const existing = mappings.value.find(m => m.sheet === sheet.name)
  if (existing) {
    mappingForm.targetType = existing.targetType
    mappingForm.targetClass = existing.targetClass
    mappingForm.priority = existing.priority
    mappingForm.fieldMappings = [...existing.fieldMappings]
    mappingForm.filterCondition = existing.filterCondition
    mappingForm.status = existing.status
    mappingForm.notes = existing.notes
  } else {
    resetMapping()
  }
}

const addFieldMapping = () => {
  mappingForm.fieldMappings.push({ cobieField: '', targetField: '', conversion: '' })
}

const removeFieldMapping = (index: number) => {
  mappingForm.fieldMappings.splice(index, 1)
}

const resetMapping = () => {
  mappingForm.targetType = ''
  mappingForm.targetClass = ''
  mappingForm.priority = 80
  mappingForm.fieldMappings = []
  mappingForm.filterCondition = ''
  mappingForm.status = 'active'
  mappingForm.notes = ''
}

const saveMapping = () => {
  if (!selectedSheet.value) {
    ElMessage.warning('No sheet selected')
    return
  }

  const existingIndex = mappings.value.findIndex(m => m.sheet === selectedSheet.value!.name)
  const mapping: Mapping = {
    id: existingIndex !== -1 ? mappings.value[existingIndex].id : `MAP-${String(mappings.value.length + 1).padStart(3, '0')}`,
    sheet: selectedSheet.value.name,
    targetType: mappingForm.targetType,
    targetClass: mappingForm.targetClass,
    priority: mappingForm.priority,
    status: mappingForm.status,
    fieldCount: mappingForm.fieldMappings.length,
    fieldMappings: mappingForm.fieldMappings,
    filterCondition: mappingForm.filterCondition,
    notes: mappingForm.notes
  }

  if (existingIndex !== -1) {
    mappings.value[existingIndex] = mapping
    ElMessage.success(`Mapping for ${selectedSheet.value.name} updated`)
  } else {
    mappings.value.push(mapping)
    selectedSheet.value.mapped = mappingForm.fieldMappings.length > 0
    selectedSheet.value.partial = mappingForm.fieldMappings.length > 0 && mappingForm.fieldMappings.length < (getAvailableFields(selectedSheet.value.name).length / 2)
    selectedSheet.value.status = selectedSheet.value.mapped ? 'mapped' : selectedSheet.value.partial ? 'partial' : 'unmapped'
    ElMessage.success(`Mapping for ${selectedSheet.value.name} created`)
  }
  updateStats()
}

const editMapping = (mapping: Mapping) => {
  const sheet = cobieSheets.value.find(s => s.name === mapping.sheet)
  if (sheet) {
    selectedSheet.value = sheet
    mappingForm.targetType = mapping.targetType
    mappingForm.targetClass = mapping.targetClass
    mappingForm.priority = mapping.priority
    mappingForm.fieldMappings = [...mapping.fieldMappings]
    mappingForm.filterCondition = mapping.filterCondition
    mappingForm.status = mapping.status
    mappingForm.notes = mapping.notes
  }
}

const deleteMapping = (mapping: Mapping) => {
  const index = mappings.value.findIndex(m => m.id === mapping.id)
  if (index !== -1) {
    mappings.value.splice(index, 1)
    const sheet = cobieSheets.value.find(s => s.name === mapping.sheet)
    if (sheet) {
      sheet.mapped = false
      sheet.partial = false
      sheet.status = 'unmapped'
    }
    updateStats()
    ElMessage.success(`Mapping for ${mapping.sheet} deleted`)
  }
}

const saveMappings = () => {
  addValidation('Mapping configuration saved successfully', 'success')
  ElMessage.success('All mappings saved')
}

const importMappings = () => {
  ElMessage.info('Import mapping configuration - select JSON file')
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e: any) => {
    if (e.target.files?.[0]) {
      const reader = new FileReader()
      reader.onload = (ev) => {
        try {
          const imported = JSON.parse(ev.target?.result as string)
          if (imported.mappings) {
            mappings.value = imported.mappings
            updateStats()
            ElMessage.success(`Imported ${imported.mappings.length} mappings`)
          }
        } catch {
          ElMessage.error('Invalid mapping file')
        }
      }
      reader.readAsText(e.target.files[0])
    }
  }
  input.click()
}

const exportMappings = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    schema: 'COBie Mapping Configuration v1.0',
    mappings: mappings.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `cobie-mappings-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Mappings exported')
}

const testMapping = () => {
  if (!selectedSheet.value) return

  const sampleData: Record<string, any> = {}
  const fields = getAvailableFields(selectedSheet.value.name)
  fields.forEach(field => {
    if (field === 'Name') sampleData[field] = 'Sample Name'
    else if (field === 'Email') sampleData[field] = 'test@example.com'
    else if (field === 'Phone') sampleData[field] = '+1 555-1234'
    else if (field === 'Area') sampleData[field] = 125.5
    else if (field === 'Height') sampleData[field] = 4.2
    else sampleData[field] = `Sample ${field}`
  })

  const mappedOutput: Record<string, any> = {}
  mappingForm.fieldMappings.forEach(mapping => {
    if (mapping.cobieField && mapping.targetField && sampleData[mapping.cobieField] !== undefined) {
      let value = sampleData[mapping.cobieField]
      if (mapping.conversion === 'upper_case') value = String(value).toUpperCase()
      else if (mapping.conversion === 'lower_case') value = String(value).toLowerCase()
      else if (mapping.conversion === 'title_case') value = String(value).replace(/\b\w/g, l => l.toUpperCase())
      mappedOutput[mapping.targetField] = value
    }
  })

  testDialog.result = {
    success: mappingForm.fieldMappings.length > 0,
    message: mappingForm.fieldMappings.length > 0
        ? `Successfully mapped ${mappingForm.fieldMappings.length} fields from ${selectedSheet.value.name}`
        : 'No field mappings configured',
    details: mappingForm.fieldMappings.length > 0 ? {
      sample: sampleData,
      mapped: mappedOutput
    } : null
  }
  testDialog.visible = true
}

const validateMappings = () => {
  validationResults.value = []

  // Check for unmapped critical sheets
  const criticalSheets = ['Contact', 'Facility', 'Space', 'Component']
  criticalSheets.forEach(sheetName => {
    const exists = mappings.value.some(m => m.sheet === sheetName)
    if (!exists) {
      addValidation(`Critical sheet ${sheetName} has no mapping defined`, 'warning')
    }
  })

  // Check for incomplete mappings
  mappings.value.forEach(m => {
    if (m.fieldCount === 0) {
      addValidation(`Mapping for ${m.sheet} has no field mappings`, 'warning')
    }
  })

  // Check for missing required fields
  mappings.value.forEach(m => {
    const sheet = cobieSheets.value.find(s => s.name === m.sheet)
    if (sheet && m.fieldCount > 0 && m.fieldCount < 3) {
      addValidation(`Mapping for ${m.sheet} has only ${m.fieldCount} fields (may be incomplete)`, 'warning')
    }
  })

  // Check for duplicate mappings
  const duplicates = mappings.value.reduce((acc, m) => {
    acc[m.sheet] = (acc[m.sheet] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  Object.entries(duplicates).forEach(([sheet, count]) => {
    if (count > 1) {
      addValidation(`Duplicate mapping detected for ${sheet}`, 'error')
    }
  })

  if (validationResults.value.length === 0) {
    addValidation('All mappings validated successfully', 'success')
  }

  stats.issuesDetected = validationResults.value.filter(v => v.severity !== 'success').length
}

const addValidation = (message: string, severity: 'success' | 'warning' | 'error') => {
  validationResults.value.unshift({
    message,
    severity,
    time: new Date().toLocaleTimeString()
  })
  if (validationResults.value.length > 20) validationResults.value.pop()
}

// ==================== 数据加载 ====================
const loadData = () => {
  updateStats()
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
.cobie-mapping-page {
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

/* Cards */
.browser-card, .mapping-card, .mappings-table-wrapper, .validation-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Sheet List */
.sheet-list {
  max-height: 500px;
  overflow-y: auto;
}

.sheet-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.sheet-item:hover {
  background-color: #f5f7fa;
}

.sheet-item.active {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.sheet-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.sheet-icon.mapped { background-color: #f0f9eb; color: #67c23a; }
.sheet-icon.partial { background-color: #fff3e0; color: #e6a23c; }
.sheet-icon.unmapped { background-color: #f5f7fa; color: #8c9aab; }

.sheet-info {
  flex: 1;
}

.sheet-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
}

.sheet-desc {
  font-size: 11px;
  color: #8c9aab;
}

.mapped-tag, .partial-tag {
  font-size: 10px;
}

/* Mapping Form */
.no-selection {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: #8c9aab;
  background: #f5f7fa;
  border-radius: 8px;
}

.no-selection .el-icon {
  font-size: 48px;
}

.param-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #8c9aab;
}

.form-hint {
  font-size: 11px;
  color: #8c9aab;
  margin-top: 4px;
}

.field-mapping-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.field-mapping-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* Mappings Table */
.mappings-table-wrapper {
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-filters {
  display: flex;
  gap: 12px;
}

/* Validation */
.validation-list {
  max-height: 200px;
  overflow-y: auto;
}

.validation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.validation-item.error .el-icon { color: #f56c6c; }
.validation-item.warning .el-icon { color: #e6a23c; }
.validation-item.success .el-icon { color: #67c23a; }

.validation-time {
  margin-left: auto;
  font-size: 10px;
  color: #c0c4cc;
}

/* Test Dialog */
.test-result {
  text-align: center;
  padding: 20px;
}

.test-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.test-icon.success { color: #67c23a; }
.test-icon.error { color: #f56c6c; }

.test-message {
  font-size: 16px;
  margin-bottom: 20px;
}

.test-details {
  text-align: left;
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}

.test-details pre {
  margin: 8px 0;
  font-size: 11px;
  white-space: pre-wrap;
}

.detail-row {
  font-weight: 600;
  margin-top: 8px;
  margin-bottom: 4px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}
</style>