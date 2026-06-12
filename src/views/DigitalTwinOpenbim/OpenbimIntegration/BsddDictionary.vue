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
        <div class="loading-tip">OpenBIM Integration - bSDD Dictionary</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="bsdd-dictionary-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>bSDD Dictionary</h1>
        <p>buildingSMART Data Dictionary integration for standardized classifications and properties</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="syncDictionary">
          <el-icon><Refresh /></el-icon>
          Sync Dictionary
        </el-button>
        <el-button @click="exportMappings">
          <el-icon><Download /></el-icon>
          Export Mappings
        </el-button>
        <el-button @click="importMappings">
          <el-icon><Upload /></el-icon>
          Import Mappings
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
            <div class="stat-value">{{ stats.totalConcepts }}</div>
            <div class="stat-label">Total Concepts</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.mappedConcepts }}</div>
            <div class="stat-label">Mapped Concepts</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeDomains }}</div>
            <div class="stat-label">Active Domains</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.lastSync }}</div>
            <div class="stat-label">Last Sync</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- Domains & Classification Tree -->
      <el-col :xs="24" :lg="10">
        <div class="browser-card">
          <div class="card-header">
            <h3>Classification Domains</h3>
            <el-input
                v-model="domainSearch"
                placeholder="Search domains..."
                clearable
                size="small"
                style="width: 160px"
                :prefix-icon="Search"
            />
          </div>
          <div class="domain-list">
            <div
                v-for="domain in filteredDomains"
                :key="domain.id"
                class="domain-item"
                :class="{ active: selectedDomain?.id === domain.id }"
                @click="onDomainSelect(domain)"
            >
              <div class="domain-icon">
                <el-icon><Folder /></el-icon>
              </div>
              <div class="domain-info">
                <div class="domain-name">{{ domain.name }}</div>
                <div class="domain-code">{{ domain.code }}</div>
              </div>
              <el-tag size="small" type="info">{{ domain.conceptCount }} concepts</el-tag>
            </div>
          </div>
        </div>

        <div class="concept-card" v-if="selectedDomain">
          <div class="card-header">
            <h3>Concepts - {{ selectedDomain.name }}</h3>
            <el-input
                v-model="conceptSearch"
                placeholder="Search concepts..."
                clearable
                size="small"
                style="width: 160px"
                :prefix-icon="Search"
            />
          </div>
          <div class="concept-list">
            <div
                v-for="concept in filteredConcepts"
                :key="concept.id"
                class="concept-item"
                :class="{ selected: selectedConcept?.id === concept.id }"
                @click="onConceptSelect(concept)"
            >
              <div class="concept-info">
                <div class="concept-name">{{ concept.name }}</div>
                <div class="concept-code">{{ concept.code }}</div>
              </div>
              <el-tag v-if="concept.mapped" size="small" type="success">Mapped</el-tag>
              <el-tag v-else size="small" type="info">Unmapped</el-tag>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Concept Details & Mapping -->
      <el-col :xs="24" :lg="14">
        <div class="detail-card" v-if="selectedConcept">
          <div class="card-header">
            <h3>Concept Details</h3>
            <div class="detail-actions">
              <el-button size="small" @click="openMappingDialog">
                <el-icon><Connection /></el-icon>
                Map to Twin
              </el-button>
              <el-button size="small" @click="viewConceptInBSDD" type="primary" link>
                View in bSDD ↗
              </el-button>
            </div>
          </div>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="Name">{{ selectedConcept.name }}</el-descriptions-item>
            <el-descriptions-item label="Code">{{ selectedConcept.code }}</el-descriptions-item>
            <el-descriptions-item label="Definition" :span="2">{{ selectedConcept.definition }}</el-descriptions-item>
            <el-descriptions-item label="Domain">{{ selectedConcept.domain }}</el-descriptions-item>
            <el-descriptions-item label="Version">{{ selectedConcept.version }}</el-descriptions-item>
            <el-descriptions-item label="Status">{{ selectedConcept.status }}</el-descriptions-item>
            <el-descriptions-item label="Synonyms" :span="2">{{ selectedConcept.synonyms?.join(', ') || 'None' }}</el-descriptions-item>
          </el-descriptions>

          <div class="properties-section" v-if="selectedConcept.properties?.length">
            <div class="section-header">
              <h4>Properties</h4>
            </div>
            <el-table :data="selectedConcept.properties" size="small" stripe>
              <el-table-column prop="name" label="Property Name" width="180" />
              <el-table-column prop="type" label="Data Type" width="100" />
              <el-table-column prop="unit" label="Unit" width="80" />
              <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
            </el-table>
          </div>

          <div class="mapping-section" v-if="selectedConcept.mapping">
            <div class="section-header">
              <h4>Current Mapping</h4>
              <el-button size="small" type="danger" link @click="removeMapping">Remove Mapping</el-button>
            </div>
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="Target Asset Type">{{ selectedConcept.mapping.targetType }}</el-descriptions-item>
              <el-descriptions-item label="Target Property">{{ selectedConcept.mapping.targetProperty }}</el-descriptions-item>
              <el-descriptions-item label="Mapped On">{{ selectedConcept.mapping.mappedOn }}</el-descriptions-item>
              <el-descriptions-item label="Mapped By">{{ selectedConcept.mapping.mappedBy }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <div class="detail-placeholder" v-else>
          <el-icon><InfoFilled /></el-icon>
          <span>Select a concept from the left to view details</span>
        </div>

        <!-- Recent Mappings -->
        <div class="mappings-card">
          <div class="card-header">
            <h3>Recent Mappings</h3>
            <el-button size="small" @click="clearRecentMappings">Clear</el-button>
          </div>
          <el-table :data="recentMappings" stripe size="small">
            <el-table-column prop="conceptCode" label="Concept Code" width="140" />
            <el-table-column prop="conceptName" label="Concept Name" min-width="180" show-overflow-tooltip />
            <el-table-column prop="targetType" label="Target Type" width="120" />
            <el-table-column prop="targetProperty" label="Target Property" width="140" />
            <el-table-column prop="mappedOn" label="Mapped On" width="100" />
            <el-table-column label="Actions" width="70">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewMapping(row)">View</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="recentMappings.length === 0" class="no-mappings">
            <el-empty description="No mappings yet" :image-size="60" />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Mapping Dialog -->
    <el-dialog v-model="mappingDialog.visible" title="Map to Digital Twin" width="500px">
      <el-form :model="mappingForm" label-width="130px">
        <el-form-item label="Concept">
          <el-input :value="selectedConcept?.name" disabled />
        </el-form-item>
        <el-form-item label="Concept Code">
          <el-input :value="selectedConcept?.code" disabled />
        </el-form-item>
        <el-form-item label="Target Asset Type" required>
          <el-select v-model="mappingForm.targetType" placeholder="Select asset type" style="width: 100%">
            <el-option label="HVAC Equipment" value="hvac" />
            <el-option label="Electrical Equipment" value="electrical" />
            <el-option label="Plumbing System" value="plumbing" />
            <el-option label="Structural Element" value="structural" />
            <el-option label="Architectural Element" value="architectural" />
            <el-option label="Fire Protection" value="fire" />
            <el-option label="Security System" value="security" />
            <el-option label="Space" value="space" />
            <el-option label="Zone" value="zone" />
          </el-select>
        </el-form-item>
        <el-form-item label="Target Property" required>
          <el-select v-model="mappingForm.targetProperty" placeholder="Select property" style="width: 100%">
            <el-option label="Name" value="name" />
            <el-option label="Description" value="description" />
            <el-option label="Type" value="type" />
            <el-option label="Category" value="category" />
            <el-option label="Manufacturer" value="manufacturer" />
            <el-option label="Model" value="model" />
            <el-option label="Serial Number" value="serialNumber" />
            <el-option label="Install Date" value="installDate" />
            <el-option label="Status" value="status" />
            <el-option label="Fire Rating" value="fireRating" />
            <el-option label="Thermal Rating" value="thermalRating" />
          </el-select>
        </el-form-item>
        <el-form-item label="Property Mapping">
          <el-table :data="mappingForm.propertyMappings" size="small" style="width: 100%">
            <el-table-column prop="bsddProperty" label="bSDD Property" width="150" />
            <el-table-column prop="targetProperty" label="Target Property" width="150" />
            <el-table-column label="Actions" width="60">
              <template #default="{ $index }">
                <el-button link type="danger" size="small" @click="removePropertyMapping($index)">Remove</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-button size="small" type="primary" link @click="addPropertyMapping" style="margin-top: 8px">
            <el-icon><Plus /></el-icon>
            Add Property Mapping
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="mappingDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmMapping">Save Mapping</el-button>
      </template>
    </el-dialog>

    <!-- Sync Progress Dialog -->
    <el-dialog v-model="syncDialog.visible" title="Syncing with bSDD" width="450px" :close-on-click-modal="false" :show-close="false">
      <div class="sync-progress">
        <el-progress :percentage="syncProgress" :stroke-width="10" />
        <div class="sync-status">{{ syncStatus }}</div>
        <div class="sync-details">{{ syncDetails }}</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Download,
  Upload,
  Grid,
  CircleCheck,
  Document,
  DataAnalysis,
  Search,
  Folder,
  InfoFilled,
  Connection,
  Plus,
  Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Connecting to bSDD API...',
  'Loading classification domains...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface BSDDDomain {
  id: string
  name: string
  code: string
  version: string
  conceptCount: number
}

interface BSDDConcept {
  id: string
  name: string
  code: string
  definition: string
  domain: string
  version: string
  status: string
  synonyms: string[]
  properties: Array<{ name: string; type: string; unit: string; description: string }>
  mapped: boolean
  mapping?: {
    targetType: string
    targetProperty: string
    propertyMappings: Array<{ bsddProperty: string; targetProperty: string }>
    mappedOn: string
    mappedBy: string
  }
}

interface Mapping {
  id: string
  conceptCode: string
  conceptName: string
  targetType: string
  targetProperty: string
  mappedOn: string
  mappedBy: string
}

// ==================== 模拟数据 ====================
const domains = ref<BSDDDomain[]>([
  { id: '1', name: 'Building Elements', code: 'https://identifier.buildingsmart.org/uri/building/element', version: '1.2', conceptCount: 245 },
  { id: '2', name: 'HVAC Systems', code: 'https://identifier.buildingsmart.org/uri/building/hvac', version: '1.1', conceptCount: 128 },
  { id: '3', name: 'Electrical Systems', code: 'https://identifier.buildingsmart.org/uri/building/electrical', version: '1.0', conceptCount: 96 },
  { id: '4', name: 'Plumbing Systems', code: 'https://identifier.buildingsmart.org/uri/building/plumbing', version: '1.0', conceptCount: 78 },
  { id: '5', name: 'Fire Safety', code: 'https://identifier.buildingsmart.org/uri/building/fire', version: '1.1', conceptCount: 52 },
  { id: '6', name: 'Security Systems', code: 'https://identifier.buildingsmart.org/uri/building/security', version: '1.0', conceptCount: 34 }
])

const concepts = ref<BSDDConcept[]>([
  {
    id: '1', name: 'Wall', code: 'IfcWall', definition: 'Vertical construction element that separates or encloses spaces',
    domain: 'Building Elements', version: '1.2', status: 'Active', synonyms: ['Partition', 'Barrier'],
    properties: [
      { name: 'LoadBearing', type: 'Boolean', unit: '', description: 'Indicates if the wall is load-bearing' },
      { name: 'FireRating', type: 'String', unit: 'minutes', description: 'Fire resistance rating' },
      { name: 'ThermalTransmittance', type: 'Real', unit: 'W/m²K', description: 'U-value of the wall' }
    ],
    mapped: true,
    mapping: { targetType: 'architectural', targetProperty: 'type', propertyMappings: [], mappedOn: '2024-06-10', mappedBy: 'admin@ibms.com' }
  },
  {
    id: '2', name: 'Air Handling Unit', code: 'AHU', definition: 'Device used to condition and circulate air as part of HVAC system',
    domain: 'HVAC Systems', version: '1.1', status: 'Active', synonyms: ['Air handler', 'Air conditioner'],
    properties: [
      { name: 'AirFlow', type: 'Real', unit: 'm³/s', description: 'Volume flow rate of air' },
      { name: 'FanSpeed', type: 'Integer', unit: 'RPM', description: 'Rotational speed of the fan' },
      { name: 'HeatingCapacity', type: 'Real', unit: 'kW', description: 'Heating power' },
      { name: 'CoolingCapacity', type: 'Real', unit: 'kW', description: 'Cooling power' }
    ],
    mapped: true,
    mapping: { targetType: 'hvac', targetProperty: 'type', propertyMappings: [], mappedOn: '2024-06-08', mappedBy: 'admin@ibms.com' }
  },
  {
    id: '3', name: 'Chiller', code: 'Chiller', definition: 'Machine that removes heat from a liquid via vapor-compression refrigeration cycle',
    domain: 'HVAC Systems', version: '1.1', status: 'Active', synonyms: ['Cooler', 'Refrigeration unit'],
    properties: [
      { name: 'CoolingCapacity', type: 'Real', unit: 'kW', description: 'Cooling power' },
      { name: 'COP', type: 'Real', unit: '', description: 'Coefficient of performance' },
      { name: 'RefrigerantType', type: 'String', unit: '', description: 'Type of refrigerant used' }
    ],
    mapped: false
  },
  {
    id: '4', name: 'Electrical Panel', code: 'Panel', definition: 'Enclosure that houses electrical components for power distribution',
    domain: 'Electrical Systems', version: '1.0', status: 'Active', synonyms: ['Distribution board', 'Breaker panel'],
    properties: [
      { name: 'Voltage', type: 'Real', unit: 'V', description: 'Operating voltage' },
      { name: 'Amperage', type: 'Real', unit: 'A', description: 'Current rating' },
      { name: 'CircuitCount', type: 'Integer', unit: '', description: 'Number of circuits' }
    ],
    mapped: false
  },
  {
    id: '5', name: 'Pipe', code: 'Pipe', definition: 'Cylindrical conduit for conveying fluids',
    domain: 'Plumbing Systems', version: '1.0', status: 'Active', synonyms: ['Tube', 'Conduit'],
    properties: [
      { name: 'Diameter', type: 'Real', unit: 'mm', description: 'Inner diameter' },
      { name: 'Material', type: 'String', unit: '', description: 'Pipe material (PVC, copper, steel)' },
      { name: 'Length', type: 'Real', unit: 'm', description: 'Pipe length' }
    ],
    mapped: false
  }
])

const recentMappings = ref<Mapping[]>([
  { id: '1', conceptCode: 'IfcWall', conceptName: 'Wall', targetType: 'architectural', targetProperty: 'type', mappedOn: '2024-06-10', mappedBy: 'admin@ibms.com' },
  { id: '2', conceptCode: 'AHU', conceptName: 'Air Handling Unit', targetType: 'hvac', targetProperty: 'type', mappedOn: '2024-06-08', mappedBy: 'admin@ibms.com' },
  { id: '3', conceptCode: 'IfcDoor', conceptName: 'Door', targetType: 'architectural', targetProperty: 'type', mappedOn: '2024-06-05', mappedBy: 'john.doe@ibms.com' }
])

const stats = reactive({
  totalConcepts: 0,
  mappedConcepts: 0,
  activeDomains: 6,
  lastSync: '2024-06-10'
})

const selectedDomain = ref<BSDDDomain | null>(null)
const selectedConcept = ref<BSDDConcept | null>(null)
const domainSearch = ref('')
const conceptSearch = ref('')
const syncProgress = ref(0)
const syncStatus = ref('')
const syncDetails = ref('')

const mappingDialog = reactive({
  visible: false,
  concept: null as BSDDConcept | null
})

const syncDialog = reactive({
  visible: false
})

const mappingForm = reactive({
  targetType: '',
  targetProperty: '',
  propertyMappings: [] as Array<{ bsddProperty: string; targetProperty: string }>
})

// ==================== 计算属性 ====================
const filteredDomains = computed(() => {
  let filtered = [...domains.value]
  if (domainSearch.value) {
    const searchLower = domainSearch.value.toLowerCase()
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchLower) ||
        d.code.toLowerCase().includes(searchLower)
    )
  }
  return filtered
})

const filteredConcepts = computed(() => {
  if (!selectedDomain.value) return []
  let filtered = concepts.value.filter(c => c.domain === selectedDomain.value!.name)
  if (conceptSearch.value) {
    const searchLower = conceptSearch.value.toLowerCase()
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(searchLower) ||
        c.code.toLowerCase().includes(searchLower)
    )
  }
  return filtered
})

// ==================== 辅助函数 ====================
const updateStats = () => {
  stats.totalConcepts = concepts.value.length
  stats.mappedConcepts = concepts.value.filter(c => c.mapped).length
}

const onDomainSelect = (domain: BSDDDomain) => {
  selectedDomain.value = domain
  selectedConcept.value = null
  conceptSearch.value = ''
}

const onConceptSelect = (concept: BSDDConcept) => {
  selectedConcept.value = concept
}

const openMappingDialog = () => {
  if (!selectedConcept.value) return
  mappingForm.targetType = selectedConcept.value.mapping?.targetType || ''
  mappingForm.targetProperty = selectedConcept.value.mapping?.targetProperty || ''
  mappingForm.propertyMappings = selectedConcept.value.mapping?.propertyMappings || []
  mappingDialog.visible = true
  mappingDialog.concept = selectedConcept.value
}

const addPropertyMapping = () => {
  mappingForm.propertyMappings.push({ bsddProperty: '', targetProperty: '' })
}

const removePropertyMapping = (index: number) => {
  mappingForm.propertyMappings.splice(index, 1)
}

const confirmMapping = () => {
  if (!mappingDialog.concept) return
  if (!mappingForm.targetType || !mappingForm.targetProperty) {
    ElMessage.warning('Please select target type and property')
    return
  }

  const concept = concepts.value.find(c => c.id === mappingDialog.concept!.id)
  if (concept) {
    concept.mapped = true
    concept.mapping = {
      targetType: mappingForm.targetType,
      targetProperty: mappingForm.targetProperty,
      propertyMappings: [...mappingForm.propertyMappings],
      mappedOn: new Date().toISOString().slice(0, 10),
      mappedBy: 'admin@ibms.com'
    }

    // Add to recent mappings
    recentMappings.value.unshift({
      id: Date.now().toString(),
      conceptCode: concept.code,
      conceptName: concept.name,
      targetType: mappingForm.targetType,
      targetProperty: mappingForm.targetProperty,
      mappedOn: new Date().toISOString().slice(0, 10),
      mappedBy: 'admin@ibms.com'
    })
    if (recentMappings.value.length > 10) recentMappings.value.pop()

    updateStats()
    ElMessage.success(`Mapping created for ${concept.name}`)
  }
  mappingDialog.visible = false
}

const removeMapping = () => {
  if (!selectedConcept.value) return
  const concept = concepts.value.find(c => c.id === selectedConcept.value!.id)
  if (concept) {
    concept.mapped = false
    concept.mapping = undefined
    updateStats()
    ElMessage.success(`Mapping removed for ${concept.name}`)
  }
}

const viewMapping = (mapping: Mapping) => {
  const concept = concepts.value.find(c => c.code === mapping.conceptCode)
  if (concept) {
    selectedConcept.value = concept
    // Also select the domain
    const domain = domains.value.find(d => d.name === concept.domain)
    if (domain) selectedDomain.value = domain
    ElMessage.info(`Viewing mapping for ${concept.name}`)
  }
}

const clearRecentMappings = () => {
  recentMappings.value = []
  ElMessage.info('Recent mappings cleared')
}

const syncDictionary = async () => {
  syncDialog.visible = true
  syncProgress.value = 0
  syncStatus.value = 'Connecting to bSDD API...'
  syncDetails.value = 'Establishing connection'

  await new Promise(resolve => setTimeout(resolve, 1000))
  syncProgress.value = 20
  syncStatus.value = 'Fetching domains...'
  syncDetails.value = 'Loading classification domains'

  await new Promise(resolve => setTimeout(resolve, 1000))
  syncProgress.value = 50
  syncStatus.value = 'Fetching concepts...'
  syncDetails.value = 'Downloading concept definitions'

  await new Promise(resolve => setTimeout(resolve, 1500))
  syncProgress.value = 80
  syncStatus.value = 'Processing data...'
  syncDetails.value = 'Updating local dictionary'

  await new Promise(resolve => setTimeout(resolve, 1000))
  syncProgress.value = 100
  syncStatus.value = 'Sync complete!'
  syncDetails.value = 'Dictionary updated successfully'

  stats.lastSync = new Date().toISOString().slice(0, 10)

  setTimeout(() => {
    syncDialog.visible = false
    ElMessage.success('bSDD dictionary synchronized successfully')
  }, 1000)
}

const viewConceptInBSDD = () => {
  if (selectedConcept.value) {
    window.open(`https://identifier.buildingsmart.org/uri/search?q=${selectedConcept.value.code}`, '_blank')
  }
}

const exportMappings = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    mappings: recentMappings.value,
    conceptMappings: concepts.value.filter(c => c.mapped).map(c => ({
      conceptCode: c.code,
      conceptName: c.name,
      mapping: c.mapping
    }))
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `bsdd-mappings-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Mappings exported')
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
            recentMappings.value = [...imported.mappings, ...recentMappings.value].slice(0, 10)
            ElMessage.success(`Imported ${imported.mappings.length} mappings`)
          }
          if (imported.conceptMappings) {
            imported.conceptMappings.forEach((imp: any) => {
              const concept = concepts.value.find(c => c.code === imp.conceptCode)
              if (concept) {
                concept.mapped = true
                concept.mapping = imp.mapping
              }
            })
            updateStats()
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
.bsdd-dictionary-page {
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
.browser-card, .concept-card, .detail-card, .mappings-card, .detail-placeholder {
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

/* Domain List */
.domain-list, .concept-list {
  max-height: 300px;
  overflow-y: auto;
}

.domain-item, .concept-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.domain-item:hover, .concept-item:hover {
  background-color: #f5f7fa;
}

.domain-item.active, .concept-item.selected {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.domain-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ecf5ff;
  color: #409eff;
}

.domain-info, .concept-info {
  flex: 1;
}

.domain-name, .concept-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
}

.domain-code, .concept-code {
  font-size: 11px;
  color: #8c9aab;
}

/* Detail Placeholder */
.detail-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: #8c9aab;
}

.detail-placeholder .el-icon {
  font-size: 48px;
}

/* Properties Section */
.properties-section, .mapping-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Mappings Card */
.mappings-card {
  margin-bottom: 0;
}

.no-mappings {
  padding: 20px;
}

/* Sync Dialog */
.sync-progress {
  padding: 20px;
  text-align: center;
}

.sync-status {
  margin-top: 16px;
  font-size: 14px;
  font-weight: 500;
  color: #409eff;
}

.sync-details {
  margin-top: 8px;
  font-size: 12px;
  color: #8c9aab;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-descriptions__label) {
  width: 120px;
}
</style>