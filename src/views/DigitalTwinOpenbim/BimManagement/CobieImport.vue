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
        <div class="loading-tip">BIM Management - COBie Import</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cobie-import-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>COBie Import</h1>
        <p>Import Construction Operations Building Information Exchange (COBie) data for facility management</p>
      </div>
    </div>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- Upload Section -->
      <el-col :xs="24" :lg="8">
        <div class="upload-card">
          <div class="card-header">
            <h3>Import COBie File</h3>
          </div>
          <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop" @click="triggerFileInput">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">Drag & drop COBie file here or click to browse</div>
            <div class="upload-hint">Supports .xlsx, .xls, .csv, .xml formats (Max 100MB)</div>
            <input ref="fileInputRef" type="file" accept=".xlsx,.xls,.csv,.xml" style="display: none" @change="handleFileSelect" />
          </div>

          <div class="file-info" v-if="selectedFile">
            <el-icon><Document /></el-icon>
            <span>{{ selectedFile.name }}</span>
            <span class="file-size">{{ (selectedFile.size / 1024).toFixed(1) }} KB</span>
            <el-button link type="danger" @click="selectedFile = null">Remove</el-button>
          </div>

          <el-button
              type="primary"
              :loading="isImporting"
              :disabled="!selectedFile"
              @click="startImport"
              style="width: 100%; margin-top: 16px"
          >
            <el-icon><Upload /></el-icon>
            {{ isImporting ? 'Importing...' : 'Import COBie Data' }}
          </el-button>
        </div>

        <!-- Import History -->
        <div class="history-card">
          <div class="card-header">
            <h3>Recent Imports</h3>
            <el-button size="small" @click="clearHistory">Clear</el-button>
          </div>
          <div class="history-list">
            <div v-for="item in importHistory" :key="item.id" class="history-item" @click="loadHistoryItem(item)">
              <div class="history-icon" :class="item.status">
                <el-icon v-if="item.status === 'success'"><CircleCheck /></el-icon>
                <el-icon v-else-if="item.status === 'error'"><CircleClose /></el-icon>
                <el-icon v-else><Clock /></el-icon>
              </div>
              <div class="history-info">
                <div class="history-name">{{ item.name }}</div>
                <div class="history-meta">{{ item.date }} • {{ item.recordCount }} records</div>
              </div>
              <el-button link type="primary" size="small" @click.stop="reimport(item)">Reimport</el-button>
            </div>
            <div v-if="importHistory.length === 0" class="no-history">
              <el-empty description="No import history" :image-size="60" />
            </div>
          </div>
        </div>

        <!-- COBie Schema Info -->
        <div class="schema-card">
          <div class="card-header">
            <h3>COBie Schema</h3>
          </div>
          <div class="schema-tables">
            <div class="schema-table" v-for="table in schemaTables" :key="table.name">
              <div class="schema-header">
                <span class="schema-name">{{ table.name }}</span>
                <span class="schema-count">{{ table.count }} records</span>
              </div>
              <div class="schema-fields">{{ table.fields.join(', ') }}</div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Data Preview & Mapping -->
      <el-col :xs="24" :lg="16">
        <!-- Data Preview Tabs -->
        <div class="preview-card">
          <div class="card-header">
            <h3>Data Preview</h3>
            <div class="preview-controls" v-if="importedData">
              <el-select v-model="activeTable" size="small" style="width: 140px">
                <el-option v-for="table in availableTables" :key="table" :label="table" :value="table" />
              </el-select>
              <el-input v-model="tableSearch" placeholder="Search..." clearable size="small" style="width: 160px" :prefix-icon="Search" />
            </div>
          </div>

          <div v-if="!importedData && !isImporting" class="preview-placeholder">
            <el-icon><Document /></el-icon>
            <span>Select a COBie file to preview data</span>
          </div>

          <div v-if="isImporting" class="import-progress">
            <el-progress :percentage="importProgress" :stroke-width="8" />
            <div class="progress-status">{{ importStatus }}</div>
          </div>

          <div v-if="importedData && activeTableData" class="data-table-wrapper">
            <el-table :data="filteredTableData" stripe height="350" style="width: 100%">
              <el-table-column
                  v-for="col in activeTableColumns"
                  :key="col"
                  :prop="col"
                  :label="col"
                  :width="col.length > 15 ? 180 : 120"
                  show-overflow-tooltip
              />
            </el-table>
            <div class="table-footer">
              <span>{{ filteredTableData.length }} of {{ activeTableData.length }} records</span>
              <el-pagination
                  v-model:current-page="tablePage"
                  :page-size="20"
                  :total="activeTableData.length"
                  size="small"
                  layout="prev, pager, next"
                  @current-change="handleTablePageChange"
              />
            </div>
          </div>
        </div>

        <!-- Asset Mapping -->
        <div class="mapping-card" v-if="importedData">
          <div class="card-header">
            <h3>Asset Mapping</h3>
            <el-button size="small" type="primary" @click="applyMapping">Apply Mapping</el-button>
          </div>
          <el-table :data="mappingPreview" stripe>
            <el-table-column prop="cobieType" label="COBie Type" width="150" />
            <el-table-column prop="cobieId" label="COBie ID" width="150" />
            <el-table-column prop="name" label="Name" min-width="180" />
            <el-table-column prop="systemType" label="System Type" width="140" />
            <el-table-column prop="twinAsset" label="Twin Asset" width="180">
              <template #default="{ row }">
                <el-tag v-if="row.twinAsset" type="success" size="small">Linked</el-tag>
                <el-button v-else link type="primary" size="small" @click="linkAsset(row)">Link Asset</el-button>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'mapped' ? 'success' : 'warning'" size="small">
                  {{ row.status === 'mapped' ? 'Mapped' : 'Pending' }}
                </el-tag>
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
            </div>
          </div>
        </div>

        <!-- Import Log -->
        <div class="log-card" v-if="importLog.length > 0">
          <div class="card-header">
            <h3>Import Log</h3>
            <el-button size="small" @click="clearLog">Clear</el-button>
          </div>
          <div class="log-container">
            <div v-for="(log, idx) in importLog" :key="idx" class="log-entry" :class="log.level">
              <el-icon><component :is="getLogIcon(log.level)" /></el-icon>
              <span>{{ log.message }}</span>
              <span class="log-time">{{ log.time }}</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Link Asset Dialog -->
    <el-dialog v-model="linkDialog.visible" title="Link to Twin Asset" width="500px">
      <el-select v-model="linkDialog.selectedAsset" placeholder="Select twin asset" style="width: 100%">
        <el-option
            v-for="asset in availableAssets"
            :key="asset.id"
            :label="`${asset.name} (${asset.type})`"
            :value="asset.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="linkDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmLink">Link</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  Upload,
  CircleCheck,
  CircleClose,
  Clock,
  Document,
  Search,
  Warning,
  InfoFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading COBie parser...',
  'Initializing data mapping...',
  'Almost ready...'
]

// ==================== 响应式状态 ====================
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const isImporting = ref(false)
const importProgress = ref(0)
const importStatus = ref('')
const importedData = ref<any>(null)
const activeTable = ref('Contact')
const tableSearch = ref('')
const tablePage = ref(1)
const importLog = ref<any[]>([])
const validationResults = ref<any[]>([])
const mappingPreview = ref<any[]>([])

const importHistory = ref([
  { id: 1, name: 'Building_Operations_COBie.xlsx', date: '2024-06-10', recordCount: 245, status: 'success' },
  { id: 2, name: 'MEP_Assets.xlsx', date: '2024-06-08', recordCount: 128, status: 'success' },
  { id: 3, name: 'Facility_Data.csv', date: '2024-06-05', recordCount: 89, status: 'error' }
])

const schemaTables = ref([
  { name: 'Contact', count: 24, fields: ['Email', 'Phone', 'Organization', 'Department'] },
  { name: 'Facility', count: 1, fields: ['SiteName', 'ProjectName', 'Location', 'Area'] },
  { name: 'Floor', count: 5, fields: ['Name', 'Elevation', 'Height'] },
  { name: 'Space', count: 48, fields: ['Name', 'Floor', 'RoomTag', 'Category'] },
  { name: 'Zone', count: 12, fields: ['Name', 'Category', 'Description'] },
  { name: 'Type', count: 36, fields: ['Name', 'Category', 'Description'] },
  { name: 'Component', count: 156, fields: ['Name', 'TypeName', 'SerialNumber', 'Manufacturer', 'Model'] },
  { name: 'System', count: 18, fields: ['Name', 'Category', 'Description'] },
  { name: 'Assembly', count: 8, fields: ['Name', 'TypeName', 'Description'] },
  { name: 'Connection', count: 42, fields: ['Name', 'Description'] },
  { name: 'Spare', count: 0, fields: ['Name', 'Description'] },
  { name: 'Resource', count: 0, fields: ['Name', 'Description'] },
  { name: 'Job', count: 0, fields: ['Name', 'Description'] },
  { name: 'Impact', count: 0, fields: ['Name', 'Description'] },
  { name: 'Document', count: 12, fields: ['Name', 'URL', 'Description'] },
  { name: 'Attribute', count: 89, fields: ['Name', 'Value', 'Unit'] }
])

const linkDialog = reactive({
  visible: false,
  currentRow: null as any,
  selectedAsset: ''
})

const availableAssets = ref([
  { id: 'AST-1001', name: 'Chiller C-101', type: 'HVAC' },
  { id: 'AST-1002', name: 'AHU-05', type: 'HVAC' },
  { id: 'AST-1003', name: 'UPS Unit B', type: 'Electrical' },
  { id: 'AST-1004', name: 'Generator G-01', type: 'Electrical' },
  { id: 'AST-1005', name: 'Pump P-203', type: 'Plumbing' }
])

// ==================== 计算属性 ====================
const availableTables = computed(() => {
  if (!importedData.value) return []
  return Object.keys(importedData.value)
})

const activeTableData = computed(() => {
  if (!importedData.value || !activeTable.value) return null
  return importedData.value[activeTable.value] || []
})

const activeTableColumns = computed(() => {
  if (!activeTableData.value || activeTableData.value.length === 0) return []
  return Object.keys(activeTableData.value[0])
})

const filteredTableData = computed(() => {
  if (!activeTableData.value) return []
  let data = [...activeTableData.value]
  if (tableSearch.value) {
    const searchLower = tableSearch.value.toLowerCase()
    data = data.filter(row =>
        Object.values(row).some(val =>
            String(val).toLowerCase().includes(searchLower)
        )
    )
  }
  const start = (tablePage.value - 1) * 20
  return data.slice(start, start + 20)
})

// ==================== 辅助函数 ====================
const getLogIcon = (level: string) => {
  const map: Record<string, any> = {
    'info': InfoFilled,
    'warning': Warning,
    'error': CircleClose,
    'success': CircleCheck
  }
  return map[level] || InfoFilled
}

const addLog = (message: string, level: 'info' | 'warning' | 'error' | 'success' = 'info') => {
  importLog.value.unshift({
    message,
    level,
    time: new Date().toLocaleTimeString()
  })
  if (importLog.value.length > 50) importLog.value.pop()
}

const addValidation = (message: string, severity: 'info' | 'warning' | 'error' = 'info') => {
  validationResults.value.unshift({ message, severity })
  if (validationResults.value.length > 30) validationResults.value.pop()
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
    addLog(`File selected: ${selectedFile.value.name}`, 'info')
  }
}

const handleDrop = (e: DragEvent) => {
  const files = e.dataTransfer?.files
  if (files && files[0] && (files[0].name.endsWith('.xlsx') || files[0].name.endsWith('.xls') || files[0].name.endsWith('.csv') || files[0].name.endsWith('.xml'))) {
    selectedFile.value = files[0]
    addLog(`File dropped: ${selectedFile.value.name}`, 'info')
  } else {
    ElMessage.warning('Please drop a valid COBie file (.xlsx, .xls, .csv, .xml)')
  }
}

const handleTablePageChange = () => {
  // Handled by computed property
}

// ==================== 模拟 COBie 解析 ====================
const parseCOBieFile = (file: File): Promise<any> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Generate mock COBie data based on schema
      const cobieData: any = {}

      // Contact data
      cobieData.Contact = [
        { Email: 'john.smith@owner.com', Phone: '+1 555-0101', Organization: 'Building Owner', Department: 'Facility Management', FullName: 'John Smith', GivenName: 'John', FamilyName: 'Smith', Street: '123 Main St', City: 'New York', State: 'NY', PostalCode: '10001', Country: 'USA' },
        { Email: 'sarah.johnson@architect.com', Phone: '+1 555-0102', Organization: 'Architect Firm', Department: 'Design', FullName: 'Sarah Johnson', GivenName: 'Sarah', FamilyName: 'Johnson', Street: '456 Oak Ave', City: 'New York', State: 'NY', PostalCode: '10002', Country: 'USA' }
      ]

      // Facility data
      cobieData.Facility = [
        { SiteName: 'Headquarters', ProjectName: 'HQ Building', Location: 'New York', Area: '45000 m²', FacilityName: 'Main Building', Description: 'Corporate headquarters' }
      ]

      // Floor data
      cobieData.Floor = [
        { Name: 'Ground Floor', Elevation: '0.00 m', Height: '4.5 m' },
        { Name: 'First Floor', Elevation: '4.50 m', Height: '4.5 m' },
        { Name: 'Second Floor', Elevation: '9.00 m', Height: '4.5 m' },
        { Name: 'Third Floor', Elevation: '13.50 m', Height: '4.5 m' },
        { Name: 'Basement', Elevation: '-3.00 m', Height: '4.0 m' }
      ]

      // Space data
      cobieData.Space = [
        { Name: 'Lobby', Floor: 'Ground Floor', RoomTag: 'G-101', Category: 'Public', Area: '150 m²', Height: '4.5 m', Department: 'Front Office' },
        { Name: 'Server Room', Floor: 'First Floor', RoomTag: '1-205', Category: 'Technical', Area: '80 m²', Height: '4.5 m', Department: 'IT' },
        { Name: 'Office A', Floor: 'Second Floor', RoomTag: '2-301', Category: 'Office', Area: '45 m²', Height: '4.5 m', Department: 'Admin' },
        { Name: 'Conference Room', Floor: 'Second Floor', RoomTag: '2-310', Category: 'Meeting', Area: '60 m²', Height: '4.5 m', Department: 'Admin' }
      ]

      // Component data (assets)
      cobieData.Component = Array.from({ length: 45 }, (_, i) => ({
        Name: `Asset ${i + 1}`,
        TypeName: ['Chiller', 'AHU', 'Pump', 'Fan', 'Controller', 'UPS', 'Generator', 'Lighting Panel', 'VAV Box'][i % 9],
        SerialNumber: `SN-${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
        Manufacturer: ['Trane', 'Carrier', 'Daikin', 'Siemens', 'Schneider', 'ABB', 'Honeywell'][i % 7],
        Model: `M-${Math.floor(Math.random() * 1000)}`,
        Floor: ['Ground Floor', 'First Floor', 'Second Floor', 'Third Floor', 'Basement'][Math.floor(Math.random() * 5)],
        Space: ['Server Room', 'HVAC Room', 'Electrical Room'][Math.floor(Math.random() * 3)],
        Tag: `TAG-${String(i + 1).padStart(4, '0')}`,
        InstallDate: '2024-01-15',
        WarrantyStartDate: '2024-01-15',
        WarrantyEndDate: '2029-01-14',
        ExpectedLife: '10 years',
        Status: 'Operational'
      }))

      cobieData.Type = [
        { Name: 'Chiller', Category: 'HVAC', Description: 'Water-cooled chiller', 'SheetType': 'HVAC' },
        { Name: 'AHU', Category: 'HVAC', Description: 'Air handling unit', 'SheetType': 'HVAC' },
        { Name: 'Pump', Category: 'Plumbing', Description: 'Centrifugal pump', 'SheetType': 'Plumbing' },
        { Name: 'UPS', Category: 'Electrical', Description: 'Uninterruptible power supply', 'SheetType': 'Electrical' }
      ]

      cobieData.System = [
        { Name: 'Chilled Water System', Category: 'HVAC', Description: 'Main cooling distribution' },
        { Name: 'Electrical Distribution', Category: 'Electrical', Description: 'Primary power distribution' }
      ]

      cobieData.Document = [
        { Name: 'As-Built Drawings', URL: '/docs/as-built.pdf', Description: 'Final construction drawings' },
        { Name: 'O&M Manuals', URL: '/docs/om-manual.pdf', Description: 'Operations and maintenance' }
      ]

      resolve(cobieData)
    }, 2000)
  })
}

const generateMappingPreview = (data: any) => {
  const components = data.Component || []
  return components.slice(0, 15).map((comp: any, idx: number) => ({
    id: idx,
    cobieType: comp.TypeName,
    cobieId: `COB-${String(idx + 1).padStart(4, '0')}`,
    name: comp.Name,
    systemType: comp.TypeName,
    twinAsset: Math.random() > 0.6 ? `AST-${Math.floor(Math.random() * 1000) + 1000}` : null,
    status: Math.random() > 0.6 ? 'mapped' : 'pending'
  }))
}

// ==================== 导入流程 ====================
const startImport = async () => {
  if (!selectedFile.value) return

  isImporting.value = true
  importProgress.value = 0
  importStatus.value = 'Validating COBie file...'
  addLog(`Starting COBie import of ${selectedFile.value.name}`, 'info')

  importProgress.value = 30
  importStatus.value = 'Parsing COBie data...'

  const data = await parseCOBieFile(selectedFile.value)
  importProgress.value = 70
  importStatus.value = 'Processing data...'

  // Validate data
  let errorCount = 0
  let warningCount = 0

  if (!data.Contact || data.Contact.length === 0) {
    addValidation('Missing Contact data - facility management contacts required', 'warning')
    warningCount++
  }
  if (!data.Facility || data.Facility.length === 0) {
    addValidation('Missing Facility data', 'error')
    errorCount++
  }
  if (!data.Component || data.Component.length === 0) {
    addValidation('No Component data found - no assets to import', 'error')
    errorCount++
  } else {
    addLog(`Found ${data.Component.length} components (assets)`, 'info')
  }

  importedData.value = data
  mappingPreview.value = generateMappingPreview(data)

  importProgress.value = 100
  importStatus.value = 'Import complete!'

  // Add to history
  importHistory.value.unshift({
    id: Date.now(),
    name: selectedFile.value.name,
    date: new Date().toISOString().slice(0, 10),
    recordCount: (data.Component?.length || 0) + (data.Space?.length || 0) + (data.Contact?.length || 0),
    status: errorCount > 0 ? 'error' : 'success'
  })

  addLog(`Successfully imported COBie data with ${data.Component?.length || 0} assets`, 'success')

  setTimeout(() => {
    isImporting.value = false
    ElMessage.success('COBie file imported successfully')
  }, 500)
}

const loadHistoryItem = (item: any) => {
  selectedFile.value = null
  importedData.value = {
    Contact: [{ Email: 'contact@example.com', Phone: '555-0000', Organization: 'Test Org', Department: 'Facilities' }],
    Facility: [{ SiteName: 'Test Facility', ProjectName: 'Test Project', Location: 'Test Location', Area: '10000 m²' }],
    Floor: [{ Name: 'Ground Floor', Elevation: '0 m', Height: '4 m' }],
    Space: [{ Name: 'Main Hall', Floor: 'Ground Floor', RoomTag: '101', Category: 'Public' }],
    Component: Array.from({ length: Math.floor(Math.random() * 50) + 20 }, (_, i) => ({
      Name: `Asset ${i + 1}`,
      TypeName: ['Chiller', 'AHU', 'Pump'][i % 3],
      SerialNumber: `SN-${i}`,
      Manufacturer: 'Test Manufacturer',
      Model: `M-${i}`,
      Floor: 'Ground Floor',
      Space: 'Main Hall'
    }))
  }
  mappingPreview.value = generateMappingPreview(importedData.value)
  addLog(`Loaded previous import: ${item.name}`, 'info')
}

const reimport = (item: any) => {
  loadHistoryItem(item)
  ElMessage.success(`Reimporting ${item.name}`)
}

const applyMapping = () => {
  ElMessage.success('Asset mapping applied to digital twin')
  mappingPreview.value = mappingPreview.value.map(m => ({ ...m, status: 'mapped', twinAsset: `AST-${Math.floor(Math.random() * 1000) + 1000}` }))
}

const linkAsset = (row: any) => {
  linkDialog.currentRow = row
  linkDialog.selectedAsset = ''
  linkDialog.visible = true
}

const confirmLink = () => {
  if (linkDialog.selectedAsset && linkDialog.currentRow) {
    const asset = availableAssets.value.find(a => a.id === linkDialog.selectedAsset)
    linkDialog.currentRow.twinAsset = asset?.name
    linkDialog.currentRow.status = 'mapped'
    ElMessage.success(`Linked ${linkDialog.currentRow.name} to ${asset?.name}`)
  }
  linkDialog.visible = false
}

const clearHistory = () => {
  importHistory.value = []
  addLog('Import history cleared', 'info')
}

const clearLog = () => {
  importLog.value = []
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
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  // Cleanup
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
.cobie-import-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
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

/* Cards */
.upload-card, .history-card, .schema-card, .preview-card, .mapping-card, .validation-card, .log-card {
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

/* Upload Area */
.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.upload-icon {
  font-size: 48px;
  color: #8c9aab;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 14px;
  color: #5e6e82;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 11px;
  color: #c0c4cc;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 13px;
}

.file-size {
  margin-left: auto;
  color: #8c9aab;
  font-size: 11px;
}

/* History List */
.history-list, .schema-tables {
  max-height: 280px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background-color: #f5f7fa;
}

.history-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-icon.success { background-color: #f0f9eb; color: #67c23a; }
.history-icon.error { background-color: #fef0f0; color: #f56c6c; }
.history-icon.pending { background-color: #fff3e0; color: #e6a23c; }

.history-info {
  flex: 1;
}

.history-name {
  font-weight: 500;
  font-size: 13px;
  color: #1f2f3d;
}

.history-meta {
  font-size: 10px;
  color: #8c9aab;
}

.no-history {
  padding: 20px;
}

/* Schema Tables */
.schema-table {
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
}

.schema-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.schema-name {
  font-weight: 600;
  font-size: 13px;
  color: #409eff;
}

.schema-count {
  font-size: 11px;
  color: #8c9aab;
}

.schema-fields {
  font-size: 11px;
  color: #5e6e82;
  white-space: nowrap;
  overflow-x: auto;
}

/* Preview */
.preview-placeholder {
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

.preview-placeholder .el-icon {
  font-size: 48px;
}

.import-progress {
  padding: 20px;
}

.progress-status {
  margin-top: 8px;
  font-size: 12px;
  color: #8c9aab;
  text-align: center;
}

.data-table-wrapper {
  overflow-x: auto;
}

.table-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
  color: #8c9aab;
}

/* Mapping Card */
.mapping-card .el-table {
  font-size: 12px;
}

/* Validation List */
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
.validation-item.info .el-icon { color: #409eff; }

/* Log Container */
.log-container {
  max-height: 150px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 12px;
}

.log-entry {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #ebeef5;
}

.log-entry.info .el-icon { color: #409eff; }
.log-entry.warning .el-icon { color: #e6a23c; }
.log-entry.error .el-icon { color: #f56c6c; }
.log-entry.success .el-icon { color: #67c23a; }

.log-time {
  margin-left: auto;
  font-size: 10px;
  color: #c0c4cc;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}
</style>