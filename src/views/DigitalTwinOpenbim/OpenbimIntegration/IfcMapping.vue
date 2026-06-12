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
        <div class="loading-tip">OpenBIM Integration - IFC Mapping</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ifc-mapping-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>IFC Mapping</h1>
        <p>Map IFC entities to internal digital twin data model for seamless integration</p>
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
            <el-icon><Grid /></el-icon>
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
      <!-- IFC Entity Browser -->
      <el-col :xs="24" :lg="10">
        <div class="browser-card">
          <div class="card-header">
            <h3>IFC Entities</h3>
            <el-input
                v-model="entitySearch"
                placeholder="Search entities..."
                clearable
                size="small"
                style="width: 180px"
                :prefix-icon="Search"
            />
          </div>
          <div class="entity-tree">
            <el-tree
                :data="filteredEntityTree"
                :props="entityTreeProps"
                node-key="id"
                :expand-on-click-node="false"
                @node-click="onEntitySelect"
                highlight-current
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <el-icon><component :is="getEntityIcon(data.type)" /></el-icon>
                  <span>{{ data.name }}</span>
                  <el-tag v-if="data.mapped" size="small" type="success" class="mapped-tag">Mapped</el-tag>
                  <el-tag v-else-if="data.partial" size="small" type="warning" class="partial-tag">Partial</el-tag>
                </span>
              </template>
            </el-tree>
          </div>
        </div>
      </el-col>

      <!-- Mapping Configuration -->
      <el-col :xs="24" :lg="14">
        <div class="mapping-card">
          <div class="card-header">
            <h3>Mapping Configuration</h3>
            <div v-if="selectedEntity" class="selected-info">
              <el-tag type="primary" size="small">{{ selectedEntity.name }}</el-tag>
            </div>
          </div>

          <div v-if="!selectedEntity" class="no-selection">
            <el-icon><Grid /></el-icon>
            <span>Select an IFC entity from the left to configure mapping</span>
          </div>

          <div v-else class="mapping-form">
            <el-form :model="mappingForm" label-width="140px">
              <el-form-item label="IFC Entity">
                <el-input :value="selectedEntity.name" disabled />
              </el-form-item>

              <el-form-item label="Target Asset Type">
                <el-select v-model="mappingForm.targetType" placeholder="Select asset type" style="width: 100%">
                  <el-option label="HVAC Equipment" value="hvac" />
                  <el-option label="Electrical Equipment" value="electrical" />
                  <el-option label="Plumbing System" value="plumbing" />
                  <el-option label="Structural Element" value="structural" />
                  <el-option label="Architectural Element" value="architectural" />
                  <el-option label="Fire Protection" value="fire" />
                  <el-option label="Security System" value="security" />
                </el-select>
              </el-form-item>

              <el-form-item label="Target Class">
                <el-select v-model="mappingForm.targetClass" placeholder="Select class" style="width: 100%">
                  <el-option label="Asset" value="asset" />
                  <el-option label="System" value="system" />
                  <el-option label="Component" value="component" />
                  <el-option label="Space" value="space" />
                  <el-option label="Zone" value="zone" />
                </el-select>
              </el-form-item>

              <el-form-item label="Priority">
                <el-slider v-model="mappingForm.priority" :min="0" :max="100" :step="1" />
                <span class="param-hint">{{ mappingForm.priority }}%</span>
              </el-form-item>

              <el-form-item label="Property Mapping">
                <div class="property-mapping-list">
                  <div v-for="(prop, idx) in mappingForm.propertyMappings" :key="idx" class="property-mapping-item">
                    <el-select v-model="prop.ifcProperty" placeholder="IFC Property" size="small" style="width: 200px">
                      <el-option :label="p" :value="p" v-for="p in availableIfcProperties" :key="p" />
                    </el-select>
                    <el-icon><Right /></el-icon>
                    <el-select v-model="prop.targetProperty" placeholder="Target Property" size="small" style="width: 200px">
                      <el-option :label="p" :value="p" v-for="p in availableTargetProperties" :key="p" />
                    </el-select>
                    <el-button link type="danger" size="small" @click="removePropertyMapping(idx)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </div>
                  <el-button size="small" type="primary" link @click="addPropertyMapping">
                    <el-icon><Plus /></el-icon>
                    Add Property Mapping
                  </el-button>
                </div>
              </el-form-item>

              <el-form-item label="Transformation Rules">
                <el-select v-model="mappingForm.transformations" multiple placeholder="Select transformations" style="width: 100%">
                  <el-option label="Unit Conversion (SI to US)" value="unit_convert" />
                  <el-option label="String Normalization" value="normalize" />
                  <el-option label="Date Format Conversion" value="date_convert" />
                  <el-option label="IfcGuid to UUID" value="guid_to_uuid" />
                </el-select>
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

    <!-- Mapping Tables -->
    <div class="mappings-table-wrapper">
      <div class="table-header">
        <h3>Active Mappings</h3>
        <div class="table-filters">
          <el-select v-model="tableFilter.type" placeholder="Filter by type" clearable size="small" style="width: 140px">
            <el-option label="All Types" value="" />
            <el-option label="HVAC" value="hvac" />
            <el-option label="Electrical" value="electrical" />
            <el-option label="Plumbing" value="plumbing" />
            <el-option label="Structural" value="structural" />
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
        <el-table-column prop="ifcEntity" label="IFC Entity" width="180" />
        <el-table-column prop="targetType" label="Target Type" width="140" />
        <el-table-column prop="targetClass" label="Target Class" width="140" />
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.priority" :stroke-width="6" :show-text="false" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : row.status === 'draft' ? 'warning' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="propertyCount" label="Properties" width="100" />
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
          <pre>{{ JSON.stringify(testDialog.result.details, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Check,
  Upload,
  Download,
  VideoPlay,
  Grid,
  CircleCheck,
  Warning,
  DataAnalysis,
  Search,
  Right,
  Delete,
  Plus,
  House,
  Tools,
  Connection,
  Lock
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading IFC schema...',
  'Initializing mapping engine...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface IFCEntity {
  id: string
  name: string
  type: string
  children?: IFCEntity[]
  mapped: boolean
  partial: boolean
}

interface Mapping {
  id: string
  ifcEntity: string
  targetType: string
  targetClass: string
  priority: number
  status: 'active' | 'inactive' | 'draft'
  propertyCount: number
  propertyMappings: any[]
  transformations: string[]
  notes: string
}

// ==================== 模拟数据 ====================
const entityTree = ref<IFCEntity[]>([
  {
    id: 'root',
    name: 'IFC Schema',
    type: 'schema',
    mapped: false,
    partial: false,
    children: [
      {
        id: 'ifcproduct',
        name: 'IfcProduct',
        type: 'abstract',
        mapped: false,
        partial: false,
        children: [
          { id: 'ifcelement', name: 'IfcElement', type: 'abstract', mapped: false, partial: false,
            children: [
              { id: 'ifcwall', name: 'IfcWall', type: 'entity', mapped: true, partial: false },
              { id: 'ifcslab', name: 'IfcSlab', type: 'entity', mapped: true, partial: false },
              { id: 'ifccolumn', name: 'IfcColumn', type: 'entity', mapped: true, partial: false },
              { id: 'ifcbeam', name: 'IfcBeam', type: 'entity', mapped: true, partial: false },
              { id: 'ifcdoor', name: 'IfcDoor', type: 'entity', mapped: true, partial: false },
              { id: 'ifcwindow', name: 'IfcWindow', type: 'entity', mapped: true, partial: false }
            ]
          },
          { id: 'ifcdistributionelement', name: 'IfcDistributionElement', type: 'abstract', mapped: false, partial: false,
            children: [
              { id: 'ifcflowterminal', name: 'IfcFlowTerminal', type: 'entity', mapped: true, partial: false },
              { id: 'ifcflowcontroller', name: 'IfcFlowController', type: 'entity', mapped: false, partial: true },
              { id: 'ifcflowfitting', name: 'IfcFlowFitting', type: 'entity', mapped: false, partial: true },
              { id: 'ifcflowmovingdevice', name: 'IfcFlowMovingDevice', type: 'entity', mapped: true, partial: false },
              { id: 'ifcenergyconversiondevice', name: 'IfcEnergyConversionDevice', type: 'entity', mapped: false, partial: false }
            ]
          }
        ]
      },
      {
        id: 'ifcspatialelement',
        name: 'IfcSpatialElement',
        type: 'abstract',
        mapped: false,
        partial: false,
        children: [
          { id: 'ifcbuilding', name: 'IfcBuilding', type: 'entity', mapped: true, partial: false },
          { id: 'ifcbuildingstorey', name: 'IfcBuildingStorey', type: 'entity', mapped: true, partial: false },
          { id: 'ifcspace', name: 'IfcSpace', type: 'entity', mapped: true, partial: false }
        ]
      }
    ]
  }
])

const availableIfcProperties = ref([
  'Name', 'Description', 'GlobalId', 'Tag', 'PredefinedType',
  'NominalHeight', 'NominalWidth', 'LoadBearing', 'FireRating',
  'ThermalTransmittance', 'AcousticRating', 'Color', 'Material',
  'Manufacturer', 'Model', 'SerialNumber', 'PowerRating'
])

const availableTargetProperties = ref([
  'assetName', 'assetDescription', 'assetId', 'assetTag', 'assetType',
  'height', 'width', 'loadBearing', 'fireRating',
  'thermalRating', 'acousticRating', 'color', 'material',
  'manufacturer', 'model', 'serialNumber', 'powerRating'
])

const mappings = ref<Mapping[]>([
  { id: 'MAP-001', ifcEntity: 'IfcWall', targetType: 'architectural', targetClass: 'component', priority: 95, status: 'active', propertyCount: 6, propertyMappings: [], transformations: [], notes: 'Wall element mapping' },
  { id: 'MAP-002', ifcEntity: 'IfcSlab', targetType: 'structural', targetClass: 'component', priority: 90, status: 'active', propertyCount: 5, propertyMappings: [], transformations: [], notes: '' },
  { id: 'MAP-003', ifcEntity: 'IfcFlowMovingDevice', targetType: 'hvac', targetClass: 'asset', priority: 85, status: 'active', propertyCount: 8, propertyMappings: [], transformations: [], notes: 'HVAC equipment mapping' },
  { id: 'MAP-004', ifcEntity: 'IfcBuilding', targetType: 'architectural', targetClass: 'system', priority: 100, status: 'active', propertyCount: 4, propertyMappings: [], transformations: [], notes: '' },
  { id: 'MAP-005', ifcEntity: 'IfcDoor', targetType: 'architectural', targetClass: 'component', priority: 88, status: 'draft', propertyCount: 3, propertyMappings: [], transformations: [], notes: 'Needs review' }
])

const stats = reactive({
  totalMappings: 0,
  activeMappings: 0,
  issuesDetected: 2,
  coverage: 78
})

const mappingForm = reactive({
  targetType: '',
  targetClass: '',
  priority: 80,
  propertyMappings: [] as Array<{ ifcProperty: string; targetProperty: string }>,
  transformations: [] as string[],
  status: 'active' as 'active' | 'inactive' | 'draft',
  notes: ''
})

const selectedEntity = ref<IFCEntity | null>(null)
const entitySearch = ref('')
const tableFilter = reactive({ type: '', search: '' })
const validationResults = ref<any[]>([])
const testDialog = reactive({ visible: false, result: null as any })

const entityTreeProps = { children: 'children', label: 'name' }

// ==================== 计算属性 ====================
const filteredEntityTree = computed(() => {
  if (!entitySearch.value) return entityTree.value
  const searchLower = entitySearch.value.toLowerCase()
  const filterNode = (nodes: IFCEntity[]): IFCEntity[] => {
    return nodes.reduce((acc, node) => {
      const matches = node.name.toLowerCase().includes(searchLower)
      const children = node.children ? filterNode(node.children) : []
      if (matches || children.length > 0) {
        acc.push({ ...node, children: children.length > 0 ? children : node.children })
      }
      return acc
    }, [] as IFCEntity[])
  }
  return filterNode(entityTree.value)
})

const filteredMappings = computed(() => {
  let filtered = [...mappings.value]
  if (tableFilter.type) {
    filtered = filtered.filter(m => m.targetType === tableFilter.type)
  }
  if (tableFilter.search) {
    const searchLower = tableFilter.search.toLowerCase()
    filtered = filtered.filter(m =>
        m.ifcEntity.toLowerCase().includes(searchLower) ||
        m.targetType.toLowerCase().includes(searchLower)
    )
  }
  return filtered
})

// ==================== 辅助函数 ====================
const getEntityIcon = (type: string) => {
  const map: Record<string, any> = {
    'entity': Grid,
    'abstract': DataAnalysis,
    'schema': House,
    'hvac': Tools,
    'electrical': Connection,
    'plumbing': Tools,
    'security': Lock
  }
  return map[type] || Grid
}

const updateStats = () => {
  stats.totalMappings = mappings.value.length
  stats.activeMappings = mappings.value.filter(m => m.status === 'active').length
}

const onEntitySelect = (entity: IFCEntity) => {
  if (entity.type !== 'entity') return
  selectedEntity.value = entity

  // Find existing mapping
  const existing = mappings.value.find(m => m.ifcEntity === entity.name)
  if (existing) {
    mappingForm.targetType = existing.targetType
    mappingForm.targetClass = existing.targetClass
    mappingForm.priority = existing.priority
    mappingForm.propertyMappings = [...existing.propertyMappings]
    mappingForm.transformations = [...existing.transformations]
    mappingForm.status = existing.status
    mappingForm.notes = existing.notes
  } else {
    resetMapping()
  }
}

const addPropertyMapping = () => {
  mappingForm.propertyMappings.push({ ifcProperty: '', targetProperty: '' })
}

const removePropertyMapping = (index: number) => {
  mappingForm.propertyMappings.splice(index, 1)
}

const resetMapping = () => {
  mappingForm.targetType = ''
  mappingForm.targetClass = ''
  mappingForm.priority = 80
  mappingForm.propertyMappings = []
  mappingForm.transformations = []
  mappingForm.status = 'active'
  mappingForm.notes = ''
}

const saveMapping = () => {
  if (!selectedEntity.value) {
    ElMessage.warning('No entity selected')
    return
  }

  const existingIndex = mappings.value.findIndex(m => m.ifcEntity === selectedEntity.value!.name)
  const mapping: Mapping = {
    id: existingIndex !== -1 ? mappings.value[existingIndex].id : `MAP-${String(mappings.value.length + 1).padStart(3, '0')}`,
    ifcEntity: selectedEntity.value.name,
    targetType: mappingForm.targetType,
    targetClass: mappingForm.targetClass,
    priority: mappingForm.priority,
    status: mappingForm.status,
    propertyCount: mappingForm.propertyMappings.length,
    propertyMappings: mappingForm.propertyMappings,
    transformations: mappingForm.transformations,
    notes: mappingForm.notes
  }

  if (existingIndex !== -1) {
    mappings.value[existingIndex] = mapping
    ElMessage.success(`Mapping for ${selectedEntity.value.name} updated`)
  } else {
    mappings.value.push(mapping)
    selectedEntity.value.mapped = true
    ElMessage.success(`Mapping for ${selectedEntity.value.name} created`)
  }
  updateStats()
}

const editMapping = (mapping: Mapping) => {
  const entity = findEntityByName(mapping.ifcEntity)
  if (entity) {
    selectedEntity.value = entity
    mappingForm.targetType = mapping.targetType
    mappingForm.targetClass = mapping.targetClass
    mappingForm.priority = mapping.priority
    mappingForm.propertyMappings = [...mapping.propertyMappings]
    mappingForm.transformations = [...mapping.transformations]
    mappingForm.status = mapping.status
    mappingForm.notes = mapping.notes
  }
}

const deleteMapping = (mapping: Mapping) => {
  const index = mappings.value.findIndex(m => m.id === mapping.id)
  if (index !== -1) {
    mappings.value.splice(index, 1)
    const entity = findEntityByName(mapping.ifcEntity)
    if (entity) entity.mapped = false
    updateStats()
    ElMessage.success(`Mapping for ${mapping.ifcEntity} deleted`)
  }
}

const findEntityByName = (name: string): IFCEntity | null => {
  const search = (nodes: IFCEntity[]): IFCEntity | null => {
    for (const node of nodes) {
      if (node.name === name) return node
      if (node.children) {
        const found = search(node.children)
        if (found) return found
      }
    }
    return null
  }
  return search(entityTree.value)
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
    schema: 'IFC Mapping Configuration v1.0',
    mappings: mappings.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ifc-mappings-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Mappings exported')
}

const testMapping = () => {
  if (!selectedEntity.value) return

  const sampleData = {
    ifcEntity: selectedEntity.value.name,
    sampleProperties: {
      Name: 'Sample Element',
      GlobalId: '3D_' + Math.random().toString(36).substring(2, 10),
      PredefinedType: 'WALL_STANDARD',
      LoadBearing: true,
      FireRating: '60 min'
    }
  }

  testDialog.result = {
    success: mappingForm.targetType !== '',
    message: mappingForm.targetType
        ? `Successfully mapped ${selectedEntity.value.name} to ${mappingForm.targetType.toUpperCase()}`
        : 'Mapping incomplete - target type not selected',
    details: mappingForm.targetType ? {
      transformed: {
        assetName: sampleData.sampleProperties.Name,
        assetId: sampleData.sampleProperties.GlobalId,
        assetType: sampleData.sampleProperties.PredefinedType,
        loadBearing: sampleData.sampleProperties.LoadBearing,
        fireRating: sampleData.sampleProperties.FireRating
      }
    } : null
  }
  testDialog.visible = true
}

const validateMappings = () => {
  validationResults.value = []

  // Check for unmapped critical entities
  const criticalEntities = ['IfcWall', 'IfcSlab', 'IfcSpace']
  criticalEntities.forEach(entity => {
    const exists = mappings.value.some(m => m.ifcEntity === entity)
    if (!exists) {
      addValidation(`Critical entity ${entity} has no mapping defined`, 'warning')
    }
  })

  // Check for incomplete mappings
  mappings.value.forEach(m => {
    if (m.propertyCount === 0) {
      addValidation(`Mapping for ${m.ifcEntity} has no property mappings`, 'warning')
    }
  })

  // Check for duplicate mappings
  const duplicates = mappings.value.reduce((acc, m) => {
    acc[m.ifcEntity] = (acc[m.ifcEntity] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  Object.entries(duplicates).forEach(([entity, count]) => {
    if (count > 1) {
      addValidation(`Duplicate mapping detected for ${entity}`, 'error')
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
.ifc-mapping-page {
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

/* Entity Tree */
.entity-tree {
  max-height: 500px;
  overflow-y: auto;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.tree-node .el-icon {
  color: #409eff;
}

.mapped-tag, .partial-tag {
  margin-left: 8px;
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

.property-mapping-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.property-mapping-item {
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
  margin: 0;
  font-size: 11px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-tree-node__content) {
  height: 32px;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}
</style>