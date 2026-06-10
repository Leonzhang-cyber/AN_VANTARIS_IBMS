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
        <div class="loading-tip">Semantic Model: Site / Building / Space</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="semantic-model-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Semantic Model</el-breadcrumb-item>
            <el-breadcrumb-item>Site / Building / Space</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Site / Building / Space Hierarchy</h1>
        <p class="description">Define and manage the semantic hierarchy of physical locations and spaces</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Model
        </el-button>
        <el-button type="primary" @click="handleAddEntity">
          <el-icon><Plus /></el-icon>
          Add Entity
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Hierarchy Tree & Details -->
    <el-row :gutter="20" class="main-row">
      <!-- Left: Hierarchy Tree -->
      <el-col :xs="24" :lg="8">
        <el-card class="tree-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Location Hierarchy</span>
              <el-button link type="primary" size="small" @click="expandAll">
                Expand All
              </el-button>
            </div>
          </template>
          <el-tree
              ref="treeRef"
              :data="treeData"
              :props="treeProps"
              node-key="id"
              default-expand-all
              highlight-current
              @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon :color="getNodeIconColor(data.type)">
                  <component :is="getNodeIcon(data.type)" />
                </el-icon>
                <span>{{ node.label }}</span>
                <el-tag v-if="data.status" :type="data.status === 'Active' ? 'success' : 'info'" size="small" class="tree-tag">
                  {{ data.status }}
                </el-tag>
                <span class="tree-meta">{{ data.totalDevices || 0 }} devices</span>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- Right: Entity Details -->
      <el-col :xs="24" :lg="16">
        <el-card class="detail-card" shadow="hover" v-if="selectedEntity">
          <template #header>
            <div class="card-header">
              <div class="entity-title">
                <el-icon :size="20" :color="getNodeIconColor(selectedEntity.type)">
                  <component :is="getNodeIcon(selectedEntity.type)" />
                </el-icon>
                <span>{{ selectedEntity.name }}</span>
                <el-tag :type="selectedEntity.status === 'Active' ? 'success' : 'info'" size="small">
                  {{ selectedEntity.status }}
                </el-tag>
              </div>
              <div class="entity-actions">
                <el-button link type="primary" size="small" @click="editEntity(selectedEntity)">Edit</el-button>
                <el-button link type="danger" size="small" @click="deleteEntity(selectedEntity)">Delete</el-button>
              </div>
            </div>
          </template>

          <!-- Basic Info -->
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Entity ID">{{ selectedEntity.id }}</el-descriptions-item>
            <el-descriptions-item label="Type">
              <el-tag :type="getTypeTag(selectedEntity.type)" size="small">{{ selectedEntity.type }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="selectedEntity.status === 'Active' ? 'success' : 'info'" size="small">{{ selectedEntity.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Parent">{{ selectedEntity.parent || 'Root' }}</el-descriptions-item>
            <el-descriptions-item label="Total Area">{{ selectedEntity.area || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Total Devices">{{ selectedEntity.totalDevices || 0 }}</el-descriptions-item>
            <el-descriptions-item label="Address" :span="2">{{ selectedEntity.address || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ selectedEntity.description || 'No description' }}</el-descriptions-item>
          </el-descriptions>

          <!-- Key Metrics -->
          <div class="metrics-section">
            <h4>Key Metrics</h4>
            <el-row :gutter="16">
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ selectedEntity.energyConsumption || 'N/A' }}</div>
                  <div class="metric-label">Energy (kWh)</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ selectedEntity.carbonEmissions || 'N/A' }}</div>
                  <div class="metric-label">CO₂ (t)</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ selectedEntity.occupancyRate || 'N/A' }}%</div>
                  <div class="metric-label">Occupancy Rate</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ selectedEntity.efficiencyScore || 'N/A' }}%</div>
                  <div class="metric-label">Efficiency Score</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- Child Entities -->
          <div class="children-section" v-if="selectedEntity.children?.length">
            <h4>Child Entities</h4>
            <el-table :data="selectedEntity.children" size="small" border>
              <el-table-column prop="name" label="Name" min-width="180" />
              <el-table-column prop="type" label="Type" width="120">
                <template #default="{ row }">
                  <el-tag :type="getTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="Status" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="totalDevices" label="Devices" width="80" align="center" />
              <el-table-column label="Action" width="80">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="navigateToEntity(row)">View</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Associated Devices -->
          <div class="devices-section" v-if="selectedEntity.devices?.length">
            <h4>Associated Devices</h4>
            <el-table :data="selectedEntity.devices" size="small" border>
              <el-table-column prop="id" label="Device ID" width="120" />
              <el-table-column prop="name" label="Device Name" min-width="180" />
              <el-table-column prop="type" label="Type" width="120" />
              <el-table-column prop="status" label="Status" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'Online' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- Empty State -->
        <el-card class="detail-card" shadow="hover" v-else>
          <div class="empty-state">
            <el-empty description="Select a location from the hierarchy to view details" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Add/Edit Entity Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'add' ? 'Add Entity' : 'Edit Entity'" width="550px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter entity name" />
        </el-form-item>
        <el-form-item label="Type" prop="type">
          <el-select v-model="formData.type" placeholder="Select type" style="width: 100%">
            <el-option label="Site" value="Site" />
            <el-option label="Building" value="Building" />
            <el-option label="Floor" value="Floor" />
            <el-option label="Zone" value="Zone" />
            <el-option label="Room" value="Room" />
          </el-select>
        </el-form-item>
        <el-form-item label="Parent" prop="parentId">
          <el-tree-select
              v-model="formData.parentId"
              :data="treeData"
              :props="{ label: 'name', value: 'id' }"
              placeholder="Select parent (optional)"
              clearable
              check-strictly
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Status" prop="status">
          <el-radio-group v-model="formData.status">
            <el-radio value="Active">Active</el-radio>
            <el-radio value="Inactive">Inactive</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Address" prop="address">
          <el-input v-model="formData.address" placeholder="Enter address" />
        </el-form-item>
        <el-form-item label="Area (sq ft)" prop="area">
          <el-input-number v-model="formData.area" :min="0" :step="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete "{{ deleteTarget?.name }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This will also delete all child entities and associated metadata.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  OfficeBuilding, Location, Grid, Edit, Delete
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading semantic model...',
  'Building hierarchy...',
  'Almost ready...'
]

// ==================== State ====================
const treeRef = ref()
const selectedEntity = ref<any>(null)
const dialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const deleteTarget = ref<any>(null)
const formRef = ref()

const formData = reactive({
  id: null,
  name: '',
  type: 'Building',
  parentId: null,
  status: 'Active',
  address: '',
  area: 0,
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select type', trigger: 'change' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Sites', value: 12, trend: 0, icon: 'OfficeBuilding', bgColor: '#409eff', key: 'sites' },
  { title: 'Total Buildings', value: 34, trend: 5, icon: 'OfficeBuilding', bgColor: '#67c23a', key: 'buildings' },
  { title: 'Total Spaces', value: 156, trend: 12, icon: 'Grid', bgColor: '#e6a23c', key: 'spaces' },
  { title: 'Associated Devices', value: 1248, trend: 8, icon: 'Document', bgColor: '#f56c6c', key: 'devices' }
])

const treeData = ref([
  {
    id: 'site_1',
    name: 'North America Headquarters',
    type: 'Site',
    status: 'Active',
    address: '123 Corporate Drive, New York, NY 10001',
    area: 250000,
    description: 'Main corporate headquarters for North American operations',
    energyConsumption: '2.45M',
    carbonEmissions: '1,250',
    occupancyRate: 87,
    efficiencyScore: 92,
    totalDevices: 456,
    children: [
      {
        id: 'building_1',
        name: 'Tower A',
        type: 'Building',
        status: 'Active',
        parent: 'North America Headquarters',
        address: '123 Corporate Drive, New York, NY 10001',
        area: 150000,
        description: 'Main office tower',
        energyConsumption: '1.45M',
        carbonEmissions: '750',
        occupancyRate: 92,
        efficiencyScore: 94,
        totalDevices: 256,
        children: [
          {
            id: 'floor_1',
            name: 'Floor 1',
            type: 'Floor',
            status: 'Active',
            parent: 'Tower A',
            area: 15000,
            description: 'Lobby and reception',
            totalDevices: 45,
            children: [
              { id: 'zone_1', name: 'Lobby Zone', type: 'Zone', status: 'Active', parent: 'Floor 1', area: 5000, totalDevices: 15, children: [] },
              { id: 'zone_2', name: 'Conference Area', type: 'Zone', status: 'Active', parent: 'Floor 1', area: 3000, totalDevices: 12, children: [] },
              { id: 'zone_3', name: 'Retail Space', type: 'Zone', status: 'Active', parent: 'Floor 1', area: 7000, totalDevices: 18, children: [] }
            ]
          },
          {
            id: 'floor_2',
            name: 'Floor 2',
            type: 'Floor',
            status: 'Active',
            parent: 'Tower A',
            area: 15000,
            description: 'Office spaces',
            totalDevices: 68,
            children: [
              { id: 'room_101', name: 'Meeting Room 101', type: 'Room', status: 'Active', parent: 'Floor 2', area: 500, totalDevices: 5, children: [] },
              { id: 'room_102', name: 'Meeting Room 102', type: 'Room', status: 'Active', parent: 'Floor 2', area: 500, totalDevices: 5, children: [] },
              { id: 'zone_4', name: 'Open Office', type: 'Zone', status: 'Active', parent: 'Floor 2', area: 14000, totalDevices: 58, children: [] }
            ]
          },
          {
            id: 'floor_3',
            name: 'Floor 3',
            type: 'Floor',
            status: 'Active',
            parent: 'Tower A',
            area: 15000,
            description: 'Executive offices',
            totalDevices: 52,
            children: [
              { id: 'room_201', name: 'CEO Office', type: 'Room', status: 'Active', parent: 'Floor 3', area: 800, totalDevices: 8, children: [] },
              { id: 'room_202', name: 'Board Room', type: 'Room', status: 'Active', parent: 'Floor 3', area: 1200, totalDevices: 12, children: [] }
            ]
          }
        ]
      },
      {
        id: 'building_2',
        name: 'Data Center',
        type: 'Building',
        status: 'Active',
        parent: 'North America Headquarters',
        address: '123 Corporate Drive, New York, NY 10001',
        area: 60000,
        description: 'Primary data center facility',
        energyConsumption: '1.0M',
        carbonEmissions: '500',
        occupancyRate: 95,
        efficiencyScore: 96,
        totalDevices: 200,
        children: [
          {
            id: 'dc_floor_1',
            name: 'Data Hall 1',
            type: 'Zone',
            status: 'Active',
            parent: 'Data Center',
            area: 20000,
            totalDevices: 100,
            children: [
              { id: 'rack_1', name: 'Rack A01', type: 'Zone', status: 'Active', parent: 'Data Hall 1', area: 0, totalDevices: 20, children: [] },
              { id: 'rack_2', name: 'Rack A02', type: 'Zone', status: 'Active', parent: 'Data Hall 1', area: 0, totalDevices: 20, children: [] }
            ]
          }
        ]
      }
    ]
  },
  {
    id: 'site_2',
    name: 'Europe Regional Office',
    type: 'Site',
    status: 'Active',
    address: '45 Regent Street, London, UK',
    area: 80000,
    description: 'European regional headquarters',
    energyConsumption: '890K',
    carbonEmissions: '450',
    occupancyRate: 82,
    efficiencyScore: 88,
    totalDevices: 234,
    children: [
      {
        id: 'building_3',
        name: 'London Tower',
        type: 'Building',
        status: 'Active',
        parent: 'Europe Regional Office',
        address: '45 Regent Street, London, UK',
        area: 80000,
        description: 'Main office building',
        totalDevices: 234,
        children: [
          { id: 'floor_4', name: 'Ground Floor', type: 'Floor', status: 'Active', parent: 'London Tower', area: 20000, totalDevices: 78, children: [] },
          { id: 'floor_5', name: 'First Floor', type: 'Floor', status: 'Active', parent: 'London Tower', area: 20000, totalDevices: 82, children: [] },
          { id: 'floor_6', name: 'Second Floor', type: 'Floor', status: 'Active', parent: 'London Tower', area: 20000, totalDevices: 74, children: [] }
        ]
      }
    ]
  }
])

const treeProps = {
  children: 'children',
  label: 'name'
}

// ==================== Helper Methods ====================
const getNodeIcon = (type: string) => {
  const map: Record<string, string> = {
    'Site': 'OfficeBuilding',
    'Building': 'OfficeBuilding',
    'Floor': 'Grid',
    'Zone': 'Location',
    'Room': 'Edit'
  }
  return map[type] || 'Document'
}

const getNodeIconColor = (type: string) => {
  const map: Record<string, string> = {
    'Site': '#409eff',
    'Building': '#67c23a',
    'Floor': '#e6a23c',
    'Zone': '#909399',
    'Room': '#f56c6c'
  }
  return map[type] || '#909399'
}

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Site': 'primary',
    'Building': 'success',
    'Floor': 'warning',
    'Zone': 'info',
    'Room': 'danger'
  }
  return map[type] || 'info'
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting semantic model...')
}

const handleAddEntity = () => {
  dialogMode.value = 'add'
  Object.assign(formData, {
    id: null,
    name: '',
    type: 'Building',
    parentId: selectedEntity.value?.id || null,
    status: 'Active',
    address: '',
    area: 0,
    description: ''
  })
  dialogVisible.value = true
}

const editEntity = (entity: any) => {
  dialogMode.value = 'edit'
  Object.assign(formData, {
    id: entity.id,
    name: entity.name,
    type: entity.type,
    parentId: null,
    status: entity.status,
    address: entity.address || '',
    area: entity.area || 0,
    description: entity.description || ''
  })
  dialogVisible.value = true
}

const deleteEntity = (entity: any) => {
  deleteTarget.value = entity
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    ElMessage.success(`Deleted: ${deleteTarget.value.name}`)
    // In real app, would remove from tree
    deleteDialogVisible.value = false
    deleteTarget.value = null
    selectedEntity.value = null
  }
}

const handleNodeClick = (data: any) => {
  selectedEntity.value = data
  // Add mock devices for demonstration
  if (!data.devices && data.type === 'Building') {
    data.devices = [
      { id: 'DEV-001', name: 'Main RTU', type: 'HVAC Controller', status: 'Online' },
      { id: 'DEV-002', name: 'Lighting Panel LP1', type: 'Lighting Controller', status: 'Online' },
      { id: 'DEV-003', name: 'Power Meter PM-01', type: 'Power Meter', status: 'Online' }
    ]
  }
}

const navigateToEntity = (entity: any) => {
  // Find and select the entity in tree
  const findNode = (nodes: any[], targetId: string): any => {
    for (const node of nodes) {
      if (node.id === targetId) return node
      if (node.children) {
        const found = findNode(node.children, targetId)
        if (found) return found
      }
    }
    return null
  }
  const node = findNode(treeData.value, entity.id)
  if (node) {
    selectedEntity.value = node
    treeRef.value?.setCurrentKey(entity.id)
  }
}

const expandAll = () => {
  for (let i = 0; i < treeRef.value?.store.nodesMap.length; i++) {
    const node = treeRef.value?.store.nodesMap[Object.keys(treeRef.value?.store.nodesMap)[i]]
    if (node) node.expand()
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Entity added successfully' : 'Entity updated successfully')
      dialogVisible.value = false
      formRef.value?.resetFields()
    }
  })
}

// ==================== Loading Simulation ====================
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
      // Auto-select first site
      selectedEntity.value = treeData.value[0]
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.semantic-model-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.main-row {
  .tree-card, .detail-card {
    height: calc(100vh - 280px);
    overflow-y: auto;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
    }
  }
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;

  .el-icon {
    flex-shrink: 0;
  }

  .tree-tag {
    margin-left: auto;
  }

  .tree-meta {
    font-size: 11px;
    color: #909399;
    margin-left: 8px;
  }
}

.detail-card {
  .entity-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    font-size: 16px;
  }

  .entity-actions {
    display: flex;
    gap: 8px;
  }

  .metrics-section, .children-section, .devices-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
      font-size: 15px;
    }
  }

  .metric-card {
    text-align: center;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;

    .metric-value {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }

    .metric-label {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }

  .empty-state {
    height: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

:deep(.el-tree-node__content) {
  height: 36px;
}

:deep(.el-descriptions) {
  margin-top: 0;
}

:deep(.el-table) {
  font-size: 13px;
}
</style>