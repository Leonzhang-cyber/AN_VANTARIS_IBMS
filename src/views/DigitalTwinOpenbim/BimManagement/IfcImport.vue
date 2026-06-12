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
        <div class="loading-tip">BIM Management - IFC Import</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ifc-import-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>IFC Import</h1>
        <p>Import Industry Foundation Classes (IFC) files into the digital twin environment</p>
      </div>
    </div>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- Upload Section -->
      <el-col :xs="24" :lg="8">
        <div class="upload-card">
          <div class="card-header">
            <h3>Import IFC File</h3>
          </div>
          <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop" @click="triggerFileInput">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">Drag & drop IFC file here or click to browse</div>
            <div class="upload-hint">Supports IFC2x3, IFC4, IFC4x3 formats (Max 500MB)</div>
            <input ref="fileInputRef" type="file" accept=".ifc,.ifcxml,.ifczip" style="display: none" @change="handleFileSelect" />
          </div>
          <el-button
              type="primary"
              :loading="isImporting"
              :disabled="!selectedFile"
              @click="startImport"
              style="width: 100%; margin-top: 16px"
          >
            <el-icon><Upload /></el-icon>
            {{ isImporting ? 'Importing...' : 'Import File' }}
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
                <div class="history-meta">{{ item.date }} • {{ item.size }}</div>
              </div>
              <el-button link type="primary" size="small" @click.stop="reimport(item)">Reimport</el-button>
            </div>
            <div v-if="importHistory.length === 0" class="no-history">
              <el-empty description="No import history" :image-size="60" />
            </div>
          </div>
        </div>
      </el-col>

      <!-- Model Preview & Validation -->
      <el-col :xs="24" :lg="16">
        <div class="preview-card">
          <div class="card-header">
            <h3>Model Preview</h3>
            <div class="preview-controls" v-if="importedModel">
              <el-button size="small" @click="resetView">
                <el-icon><RefreshRight /></el-icon>
                Reset
              </el-button>
              <el-button size="small" @click="toggleWireframe">
                <el-icon><Grid /></el-icon>
                Wireframe
              </el-button>
            </div>
          </div>
          <div class="preview-container" ref="previewContainerRef">
            <canvas ref="previewCanvasRef" class="preview-canvas"></canvas>
            <div v-if="!importedModel && !isImporting" class="preview-placeholder">
              <el-icon><Files /></el-icon>
              <span>Select an IFC file to preview</span>
            </div>
            <div v-if="isImporting" class="import-progress">
              <el-progress :percentage="importProgress" :stroke-width="8" />
              <div class="progress-status">{{ importStatus }}</div>
            </div>
          </div>
          <div class="model-info" v-if="importedModel">
            <el-descriptions :column="3" size="small" border>
              <el-descriptions-item label="File Name">{{ importedModel.name }}</el-descriptions-item>
              <el-descriptions-item label="Format">{{ importedModel.format }}</el-descriptions-item>
              <el-descriptions-item label="Size">{{ importedModel.size }}</el-descriptions-item>
              <el-descriptions-item label="Elements">{{ importedModel.elementCount }}</el-descriptions-item>
              <el-descriptions-item label="IFC Version">{{ importedModel.ifcVersion }}</el-descriptions-item>
              <el-descriptions-item label="Schema">{{ importedModel.schema }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <!-- Model Structure -->
        <div class="structure-card" v-if="importedModel">
          <div class="card-header">
            <h3>Model Structure</h3>
            <el-input v-model="structureSearch" placeholder="Search..." clearable size="small" style="width: 200px" :prefix-icon="Search" />
          </div>
          <div class="tree-container">
            <el-tree
                :data="filteredTreeData"
                :props="treeProps"
                node-key="id"
                :default-expand-all="false"
                :expand-on-click-node="false"
                @node-click="onNodeClick"
            >
              <template #default="{ node, data }">
                <span class="tree-node">
                  <el-icon><component :is="getNodeIcon(data.type)" /></el-icon>
                  <span>{{ data.name }}</span>
                  <span class="node-count" v-if="data.count">({{ data.count }})</span>
                  <el-tag v-if="data.type" size="small" class="node-type">{{ data.type }}</el-tag>
                </span>
              </template>
            </el-tree>
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

    <!-- Validation Results Dialog -->
    <el-dialog v-model="validationDialog.visible" title="IFC Validation Results" width="600px">
      <div class="validation-summary">
        <div class="validation-stats">
          <div class="stat success">
            <div class="stat-value">{{ validationStats.passed }}</div>
            <div class="stat-label">Passed</div>
          </div>
          <div class="stat warning">
            <div class="stat-value">{{ validationStats.warnings }}</div>
            <div class="stat-label">Warnings</div>
          </div>
          <div class="stat error">
            <div class="stat-value">{{ validationStats.errors }}</div>
            <div class="stat-label">Errors</div>
          </div>
        </div>
        <div class="validation-list">
          <div v-for="(issue, idx) in validationIssues" :key="idx" class="validation-item" :class="issue.level">
            <el-icon><component :is="issue.level === 'error' ? 'CircleClose' : issue.level === 'warning' ? 'Warning' : 'CircleCheck'" /></el-icon>
            <span>{{ issue.message }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="validationDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="proceedWithImport">Proceed Anyway</el-button>
      </template>
    </el-dialog>

    <!-- Element Detail Dialog -->
    <el-dialog v-model="elementDialog.visible" :title="elementDialog.element?.name" width="500px">
      <div v-if="elementDialog.element">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Type">{{ elementDialog.element.type }}</el-descriptions-item>
          <el-descriptions-item label="GUID">{{ elementDialog.element.guid }}</el-descriptions-item>
          <el-descriptions-item label="Global ID" :span="2">{{ elementDialog.element.globalId }}</el-descriptions-item>
          <el-descriptions-item label="Material">{{ elementDialog.element.material || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Layer">{{ elementDialog.element.layer || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Properties" :span="2">
            <pre class="property-preview">{{ JSON.stringify(elementDialog.element.properties, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  UploadFilled,
  Upload,
  CircleCheck,
  CircleClose,
  Clock,
  RefreshRight,
  Grid,
  Files,
  Search,
  House,
  Tools,
  Connection,
  DataLine,
  Warning,
  InfoFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading IFC parser...',
  'Initializing viewer...',
  'Almost ready...'
]

// ==================== 响应式状态 ====================
const fileInputRef = ref<HTMLInputElement | null>(null)
const previewCanvasRef = ref<HTMLCanvasElement | null>(null)
const previewContainerRef = ref<HTMLDivElement | null>(null)

const selectedFile = ref<File | null>(null)
const isImporting = ref(false)
const importProgress = ref(0)
const importStatus = ref('')
const importedModel = ref<any>(null)
const importLog = ref<any[]>([])
const structureSearch = ref('')
const wireframeMode = ref(false)

const importHistory = ref([
  { id: 1, name: 'Building_A_Structural.ifc', date: '2024-06-10', size: '24.5 MB', status: 'success' },
  { id: 2, name: 'MEP_Systems.ifc', date: '2024-06-08', size: '18.2 MB', status: 'success' },
  { id: 3, name: 'Architectural_Model.ifc', date: '2024-06-05', size: '32.1 MB', status: 'error' },
  { id: 4, name: 'Site_Plan.ifc', date: '2024-06-01', size: '8.7 MB', status: 'success' }
])

const treeData = ref<any[]>([])
const treeProps = { children: 'children', label: 'name' }

const validationDialog = reactive({
  visible: false,
  resolvePromise: null as ((value: boolean) => void) | null
})

const validationStats = reactive({
  passed: 0,
  warnings: 0,
  errors: 0
})

const validationIssues = ref<any[]>([])

const elementDialog = reactive({
  visible: false,
  element: null as any
})

let animationFrameId: number | null = null
let rotationAngle = 0

// ==================== 计算属性 ====================
const filteredTreeData = computed(() => {
  if (!structureSearch.value) return treeData.value
  const searchLower = structureSearch.value.toLowerCase()
  const filterNode = (nodes: any[]): any[] => {
    return nodes.reduce((acc, node) => {
      const matches = node.name.toLowerCase().includes(searchLower)
      const children = node.children ? filterNode(node.children) : []
      if (matches || children.length > 0) {
        acc.push({ ...node, children: children.length > 0 ? children : node.children })
      }
      return acc
    }, [])
  }
  return filterNode(treeData.value)
})

// ==================== 辅助函数 ====================
const getNodeIcon = (type: string) => {
  const map: Record<string, any> = {
    'IfcBuilding': House,
    'IfcBuildingStorey': DataLine,
    'IfcSpace': House,
    'IfcWall': Grid,
    'IfcSlab': Grid,
    'IfcColumn': Grid,
    'IfcBeam': Grid,
    'IfcDoor': Grid,
    'IfcWindow': Grid,
    'IfcDistributionSystem': Connection,
    'IfcFlowSegment': Connection,
    'IfcFlowFitting': Tools,
    'IfcDistributionElement': Connection,
    'IfcElementAssembly': Tools
  }
  return map[type] || Grid
}

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

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
    addLog(`File selected: ${selectedFile.value.name} (${(selectedFile.value.size / 1024 / 1024).toFixed(2)} MB)`, 'info')
  }
}

const handleDrop = (e: DragEvent) => {
  const files = e.dataTransfer?.files
  if (files && files[0] && (files[0].name.endsWith('.ifc') || files[0].name.endsWith('.ifcxml') || files[0].name.endsWith('.ifczip'))) {
    selectedFile.value = files[0]
    addLog(`File dropped: ${selectedFile.value.name}`, 'info')
  } else {
    ElMessage.warning('Please drop a valid IFC file (.ifc, .ifcxml, .ifczip)')
  }
}

// ==================== 模拟 IFC 解析 ====================
const validateIFC = (file: File): Promise<{ isValid: boolean; stats: any; issues: any[] }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Simulate validation
      const randomErrors = Math.random() > 0.7 ? Math.floor(Math.random() * 3) : 0
      const randomWarnings = Math.floor(Math.random() * 5)

      const issues: any[] = []
      if (randomErrors > 0) {
        issues.push({ level: 'error', message: 'Missing required IFC header information' })
        if (randomErrors > 1) issues.push({ level: 'error', message: 'Invalid entity reference detected' })
      }
      if (randomWarnings > 0) {
        issues.push({ level: 'warning', message: 'Non-standard property set used' })
        if (randomWarnings > 1) issues.push({ level: 'warning', message: 'Missing optional geometry representation' })
        if (randomWarnings > 2) issues.push({ level: 'warning', message: 'Inconsistent unit definitions' })
      }

      resolve({
        isValid: randomErrors === 0,
        stats: { passed: 10 - randomErrors - randomWarnings, warnings: randomWarnings, errors: randomErrors },
        issues
      })
    }, 1000)
  })
}

const parseIFCContent = (file: File): Promise<any> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Generate mock model structure
      const model = {
        name: file.name,
        format: file.name.split('.').pop()?.toUpperCase(),
        size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
        elementCount: Math.floor(Math.random() * 500) + 200,
        ifcVersion: ['IFC2x3', 'IFC4', 'IFC4x3'][Math.floor(Math.random() * 3)],
        schema: 'IFC2x3'
      }

      // Generate mock tree structure
      const buildings = ['Building A', 'Building B', 'Building C']
      const storeys = ['Ground Floor', 'First Floor', 'Second Floor', 'Third Floor']
      const categories = ['Walls', 'Slabs', 'Columns', 'Beams', 'Doors', 'Windows', 'HVAC', 'Electrical', 'Plumbing']

      const tree: any[] = buildings.map((building, bIdx) => ({
        id: `building-${bIdx}`,
        name: building,
        type: 'IfcBuilding',
        children: storeys.map((storey, sIdx) => ({
          id: `storey-${bIdx}-${sIdx}`,
          name: storey,
          type: 'IfcBuildingStorey',
          children: categories.slice(0, Math.floor(Math.random() * 6) + 3).map((cat, cIdx) => ({
            id: `category-${bIdx}-${sIdx}-${cIdx}`,
            name: cat,
            type: `Ifc${cat}`,
            count: Math.floor(Math.random() * 30) + 5,
            children: Array.from({ length: Math.min(5, Math.floor(Math.random() * 10)) }, (_, i) => ({
              id: `element-${bIdx}-${sIdx}-${cIdx}-${i}`,
              name: `${cat} ${String.fromCharCode(65 + i)}`,
              type: `Ifc${cat.slice(0, -1)}`,
              guid: `3D${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
              globalId: `IFC_${Math.random().toString(36).substring(2, 15).toUpperCase()}`,
              material: ['Concrete', 'Steel', 'Wood', 'Glass', 'Aluminum'][Math.floor(Math.random() * 5)],
              layer: `Layer ${Math.floor(Math.random() * 5) + 1}`,
              properties: {
                'LoadBearing': Math.random() > 0.5,
                'FireRating': `${Math.floor(Math.random() * 120) + 60} min`,
                'ThermalTransmittance': (Math.random() * 0.5 + 0.1).toFixed(2),
                'AcousticRating': ['STC 45', 'STC 50', 'STC 55'][Math.floor(Math.random() * 3)]
              }
            }))
          }))
        }))
      }))

      resolve({ model, tree })
    }, 1500)
  })
}

const drawModelPreview = () => {
  const canvas = previewCanvasRef.value
  const container = previewContainerRef.value
  if (!canvas || !container || !importedModel.value) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = container.clientWidth
  const height = 400
  canvas.width = width
  canvas.height = height

  // Background
  ctx.fillStyle = '#1a1a2e'
  ctx.fillRect(0, 0, width, height)

  const centerX = width / 2
  const centerY = height / 2 + 20

  // Draw isometric building shape
  ctx.save()
  if (wireframeMode.value) {
    ctx.strokeStyle = '#409eff'
    ctx.lineWidth = 1
  } else {
    ctx.fillStyle = 'rgba(64, 158, 255, 0.3)'
    ctx.fillRect(centerX - 120, centerY - 100, 240, 200)
  }

  // Draw floors
  for (let i = 0; i < 5; i++) {
    const y = centerY - 80 + i * 25
    if (wireframeMode.value) {
      ctx.beginPath()
      ctx.moveTo(centerX - 110, y)
      ctx.lineTo(centerX + 110, y)
      ctx.stroke()
    } else {
      ctx.fillStyle = `rgba(64, 158, 255, ${0.2 + i * 0.05})`
      ctx.fillRect(centerX - 110, y, 220, 22)
    }
  }

  // Draw structural elements
  for (let i = 0; i < 6; i++) {
    const x = centerX - 100 + i * 40
    if (wireframeMode.value) {
      ctx.strokeRect(x - 5, centerY - 80, 10, 180)
    } else {
      ctx.fillStyle = '#8c9aab'
      ctx.fillRect(x - 5, centerY - 80, 10, 180)
    }
  }

  // Draw roof
  ctx.beginPath()
  ctx.moveTo(centerX - 130, centerY - 80)
  ctx.lineTo(centerX, centerY - 130)
  ctx.lineTo(centerX + 130, centerY - 80)
  if (wireframeMode.value) {
    ctx.stroke()
  } else {
    ctx.fillStyle = '#e6a23c'
    ctx.fill()
  }

  // Animated rotation effect
  rotationAngle += 0.005
  ctx.restore()
}

const startRenderLoop = () => {
  const render = () => {
    drawModelPreview()
    animationFrameId = requestAnimationFrame(render)
  }
  render()
}

const resetView = () => {
  rotationAngle = 0
  drawModelPreview()
}

const toggleWireframe = () => {
  wireframeMode.value = !wireframeMode.value
  drawModelPreview()
}

const onNodeClick = (data: any) => {
  if (data.properties) {
    elementDialog.element = data
    elementDialog.visible = true
  }
}

// ==================== 导入流程 ====================
const startImport = async () => {
  if (!selectedFile.value) return

  isImporting.value = true
  importProgress.value = 0
  importStatus.value = 'Validating IFC file...'
  addLog(`Starting import of ${selectedFile.value.name}`, 'info')

  // Step 1: Validation
  importProgress.value = 20
  const validation = await validateIFC(selectedFile.value)
  validationStats.passed = validation.stats.passed
  validationStats.warnings = validation.stats.warnings
  validationStats.errors = validation.stats.errors
  validationIssues.value = validation.issues

  if (!validation.isValid) {
    importStatus.value = 'Validation failed'
    addLog(`Validation failed with ${validation.stats.errors} errors`, 'error')
    validationDialog.visible = true

    // Wait for user decision
    const proceed = await new Promise<boolean>((resolve) => {
      validationDialog.resolvePromise = resolve
    })
    validationDialog.resolvePromise = null

    if (!proceed) {
      isImporting.value = false
      importProgress.value = 0
      addLog('Import cancelled due to validation errors', 'warning')
      return
    }
  }

  // Step 2: Parsing
  importProgress.value = 40
  importStatus.value = 'Parsing IFC structure...'
  addLog('Parsing IFC file structure', 'info')

  const parsed = await parseIFCContent(selectedFile.value)
  importProgress.value = 80
  importStatus.value = 'Generating model preview...'

  // Step 3: Model creation
  importedModel.value = parsed.model
  treeData.value = parsed.tree
  importProgress.value = 100
  importStatus.value = 'Import complete!'

  // Add to history
  importHistory.value.unshift({
    id: Date.now(),
    name: selectedFile.value.name,
    date: new Date().toISOString().slice(0, 10),
    size: `${(selectedFile.value.size / 1024 / 1024).toFixed(2)} MB`,
    status: 'success'
  })

  addLog(`Successfully imported ${parsed.model.elementCount} elements`, 'success')

  setTimeout(() => {
    isImporting.value = false
    ElMessage.success('IFC file imported successfully')

    // Start preview animation
    nextTick(() => {
      startRenderLoop()
    })
  }, 500)
}

const proceedWithImport = () => {
  validationDialog.visible = false
  if (validationDialog.resolvePromise) {
    validationDialog.resolvePromise(true)
  }
}

const loadHistoryItem = (item: any) => {
  selectedFile.value = null
  importedModel.value = {
    name: item.name,
    format: 'IFC',
    size: item.size,
    elementCount: Math.floor(Math.random() * 500) + 200,
    ifcVersion: 'IFC4',
    schema: 'IFC2x3'
  }
  treeData.value = [
    { id: '1', name: 'Building A', type: 'IfcBuilding', children: [
        { id: '1-1', name: 'Ground Floor', type: 'IfcBuildingStorey', children: [
            { id: '1-1-1', name: 'Walls', type: 'IfcWall', count: 24 },
            { id: '1-1-2', name: 'Columns', type: 'IfcColumn', count: 16 }
          ]}
      ]}
  ]
  addLog(`Loaded previous import: ${item.name}`, 'info')
  nextTick(() => startRenderLoop())
}

const reimport = (item: any) => {
  selectedFile.value = null
  loadHistoryItem(item)
  ElMessage.success(`Reimporting ${item.name}`)
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
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
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
.ifc-import-page {
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
.upload-card, .history-card, .preview-card, .structure-card, .log-card {
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

/* History List */
.history-list {
  max-height: 300px;
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

/* Preview Container */
.preview-container {
  position: relative;
  background-color: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
  min-height: 400px;
}

.preview-canvas {
  width: 100%;
  height: 400px;
  display: block;
}

.preview-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #8c9aab;
  background: rgba(0, 0, 0, 0.7);
}

.preview-placeholder .el-icon {
  font-size: 48px;
}

.import-progress {
  position: absolute;
  bottom: 20px;
  left: 20px;
  right: 20px;
  background: rgba(0, 0, 0, 0.8);
  padding: 16px;
  border-radius: 8px;
}

.progress-status {
  margin-top: 8px;
  font-size: 12px;
  color: #8c9aab;
  text-align: center;
}

.model-info {
  margin-top: 16px;
}

/* Tree Container */
.tree-container {
  max-height: 400px;
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

.node-count {
  color: #8c9aab;
  font-size: 11px;
}

.node-type {
  font-size: 10px;
  margin-left: 8px;
}

/* Log Container */
.log-container {
  max-height: 200px;
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

/* Validation Dialog */
.validation-summary {
  padding: 8px 0;
}

.validation-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.validation-stats .stat {
  text-align: center;
}

.validation-stats .stat-value {
  font-size: 28px;
  font-weight: 700;
}

.validation-stats .stat.success .stat-value { color: #67c23a; }
.validation-stats .stat.warning .stat-value { color: #e6a23c; }
.validation-stats .stat.error .stat-value { color: #f56c6c; }

.validation-stats .stat-label {
  font-size: 12px;
  color: #8c9aab;
}

.validation-list {
  max-height: 250px;
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

.property-preview {
  background: #f5f7fa;
  padding: 8px;
  border-radius: 4px;
  font-size: 11px;
  overflow-x: auto;
  max-height: 200px;
}

:deep(.el-tree-node__content) {
  height: 32px;
}

:deep(.el-tree-node__content:hover) {
  background-color: #f5f7fa;
}
</style>