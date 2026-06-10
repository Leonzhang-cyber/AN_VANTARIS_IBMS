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
        <div class="loading-tip">Semantic Model: Asset / Device / Point</div>
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
            <el-breadcrumb-item>Asset / Device / Point</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Asset / Device / Point Hierarchy</h1>
        <p class="description">Define and manage the semantic hierarchy of assets, devices, and data points</p>
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
              <span>Asset Hierarchy</span>
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
                <span class="tree-meta">{{ data.dataPoints || data.children?.length || 0 }} {{ data.type === 'Point' ? 'points' : 'items' }}</span>
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
            <el-descriptions-item label="Location">{{ selectedEntity.location || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Manufacturer">{{ selectedEntity.manufacturer || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Model">{{ selectedEntity.model || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Serial Number">{{ selectedEntity.serialNumber || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Install Date">{{ selectedEntity.installDate || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Warranty Expiry">{{ selectedEntity.warrantyExpiry || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ selectedEntity.description || 'No description' }}</el-descriptions-item>
          </el-descriptions>

          <!-- Equipment Metrics -->
          <div class="metrics-section" v-if="selectedEntity.type !== 'Point'">
            <h4>Equipment Metrics</h4>
            <el-row :gutter="16">
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ selectedEntity.uptime || 'N/A' }}%</div>
                  <div class="metric-label">Uptime</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ selectedEntity.efficiency || 'N/A' }}%</div>
                  <div class="metric-label">Efficiency</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ selectedEntity.powerConsumption || 'N/A' }}</div>
                  <div class="metric-label">Power (kW)</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-card">
                  <div class="metric-value">{{ selectedEntity.temperature || 'N/A' }}°C</div>
                  <div class="metric-label">Temperature</div>
                </div>
              </el-col>
            </el-row>
          </div>

          <!-- Data Points (for Device/Asset) -->
          <div class="points-section" v-if="selectedEntity.dataPointsList?.length">
            <h4>Data Points</h4>
            <el-table :data="selectedEntity.dataPointsList" size="small" border>
              <el-table-column prop="name" label="Point Name" min-width="180" />
              <el-table-column prop="pointType" label="Type" width="120">
                <template #default="{ row }">
                  <el-tag :type="getPointTypeTag(row.pointType)" size="small">{{ row.pointType }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="unit" label="Unit" width="80" />
              <el-table-column prop="currentValue" label="Current Value" width="120" align="right" />
              <el-table-column prop="status" label="Status" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'Good' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Action" width="80">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="viewPointDetails(row)">Details</el-button>
                </template>
              </el-table-column>
            </el-table>
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
              <el-table-column label="Action" width="80">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="navigateToEntity(row)">View</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- Empty State -->
        <el-card class="detail-card" shadow="hover" v-else>
          <div class="empty-state">
            <el-empty description="Select an asset from the hierarchy to view details" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Add/Edit Entity Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'add' ? 'Add Entity' : 'Edit Entity'" width="600px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Name" prop="name">
              <el-input v-model="formData.name" placeholder="Enter name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Type" prop="type">
              <el-select v-model="formData.type" placeholder="Select type" style="width: 100%">
                <el-option label="Asset" value="Asset" />
                <el-option label="Device" value="Device" />
                <el-option label="Point" value="Point" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="formData.type !== 'Point'">
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
          </el-col>
          <el-col :span="24" v-if="formData.type === 'Point'">
            <el-form-item label="Parent Device" prop="parentId">
              <el-tree-select
                  v-model="formData.parentId"
                  :data="treeData"
                  :props="{ label: 'name', value: 'id' }"
                  placeholder="Select parent device"
                  clearable
                  check-strictly
                  style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status" prop="status">
              <el-radio-group v-model="formData.status">
                <el-radio value="Active">Active</el-radio>
                <el-radio value="Inactive">Inactive</el-radio>
                <el-radio value="Maintenance">Maintenance</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="formData.type !== 'Point'">
            <el-form-item label="Location" prop="location">
              <el-input v-model="formData.location" placeholder="Location" />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="formData.type !== 'Point'">
            <el-form-item label="Manufacturer" prop="manufacturer">
              <el-input v-model="formData.manufacturer" placeholder="Manufacturer" />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="formData.type !== 'Point'">
            <el-form-item label="Model" prop="model">
              <el-input v-model="formData.model" placeholder="Model" />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="formData.type === 'Point'">
            <el-form-item label="Point Type" prop="pointType">
              <el-select v-model="formData.pointType" placeholder="Select point type" style="width: 100%">
                <el-option label="Analog Input" value="Analog Input" />
                <el-option label="Digital Input" value="Digital Input" />
                <el-option label="Analog Output" value="Analog Output" />
                <el-option label="Digital Output" value="Digital Output" />
                <el-option label="Calculated" value="Calculated" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="formData.type === 'Point'">
            <el-form-item label="Unit" prop="unit">
              <el-input v-model="formData.unit" placeholder="e.g., °C, kW, %" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save</el-button>
      </template>
    </el-dialog>

    <!-- Point Details Dialog -->
    <el-dialog v-model="pointDialogVisible" title="Point Details" width="500px" destroy-on-close>
      <div class="point-details" v-if="selectedPoint">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Point ID">{{ selectedPoint.id }}</el-descriptions-item>
          <el-descriptions-item label="Name">{{ selectedPoint.name }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedPoint.pointType }}</el-descriptions-item>
          <el-descriptions-item label="Unit">{{ selectedPoint.unit }}</el-descriptions-item>
          <el-descriptions-item label="Current Value">{{ selectedPoint.currentValue }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedPoint.status === 'Good' ? 'success' : 'warning'" size="small">{{ selectedPoint.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Min Range">{{ selectedPoint.minRange || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Max Range">{{ selectedPoint.maxRange || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Last Updated">{{ selectedPoint.lastUpdated || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedPoint.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="pointDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete "{{ deleteTarget?.name }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This will also delete all child entities and associated data.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Cpu, Monitor, Connection, Edit, Delete
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading semantic model...',
  'Building asset hierarchy...',
  'Almost ready...'
]

// ==================== State ====================
const treeRef = ref()
const selectedEntity = ref<any>(null)
const selectedPoint = ref<any>(null)
const dialogVisible = ref(false)
const pointDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const deleteTarget = ref<any>(null)
const formRef = ref()

const formData = reactive({
  id: null,
  name: '',
  type: 'Device',
  parentId: null,
  status: 'Active',
  location: '',
  manufacturer: '',
  model: '',
  pointType: '',
  unit: '',
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select type', trigger: 'change' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Assets', value: 48, trend: 8, icon: 'Document', bgColor: '#409eff', key: 'assets' },
  { title: 'Total Devices', value: 156, trend: 12, icon: 'Cpu', bgColor: '#67c23a', key: 'devices' },
  { title: 'Active Points', value: '2,456', trend: 18, icon: 'Connection', bgColor: '#e6a23c', key: 'points' },
  { title: 'Data Quality', value: '98.5%', trend: 2, icon: 'Checked', bgColor: '#f56c6c', key: 'quality' }
])

const treeData = ref([
  {
    id: 'asset_1',
    name: 'Chiller Plant',
    type: 'Asset',
    status: 'Active',
    parent: 'Root',
    location: 'Building A, Basement',
    description: 'Main chiller plant serving Building A',
    uptime: 99.8,
    efficiency: 92,
    powerConsumption: 245,
    temperature: 22.5,
    dataPoints: 0,
    children: [
      {
        id: 'device_1',
        name: 'Chiller-01',
        type: 'Device',
        status: 'Active',
        parent: 'Chiller Plant',
        location: 'Chiller Room 1',
        manufacturer: 'Trane',
        model: 'CVHF-570',
        serialNumber: 'TR-CVHF-001',
        installDate: '2022-06-15',
        warrantyExpiry: '2027-06-15',
        description: 'Centrifugal chiller for Building A cooling',
        uptime: 99.5,
        efficiency: 94,
        powerConsumption: 180,
        temperature: 22.3,
        dataPoints: 8,
        dataPointsList: [
          { id: 'point_1', name: 'Supply Temperature', pointType: 'Analog Input', unit: '°C', currentValue: 6.5, status: 'Good', minRange: 4, maxRange: 10, lastUpdated: '2024-01-20 10:30:00', description: 'Chilled water supply temperature' },
          { id: 'point_2', name: 'Return Temperature', pointType: 'Analog Input', unit: '°C', currentValue: 12.8, status: 'Good', minRange: 8, maxRange: 16, lastUpdated: '2024-01-20 10:30:00', description: 'Chilled water return temperature' },
          { id: 'point_3', name: 'Power Consumption', pointType: 'Analog Input', unit: 'kW', currentValue: 180.5, status: 'Good', minRange: 0, maxRange: 500, lastUpdated: '2024-01-20 10:30:00', description: 'Real-time power draw' },
          { id: 'point_4', name: 'Running Status', pointType: 'Digital Input', unit: '', currentValue: 'On', status: 'Good', lastUpdated: '2024-01-20 10:30:00', description: 'Chiller on/off status' },
          { id: 'point_5', name: 'Setpoint', pointType: 'Analog Output', unit: '°C', currentValue: 6.0, status: 'Good', minRange: 4, maxRange: 10, lastUpdated: '2024-01-20 10:30:00', description: 'Temperature setpoint' }
        ],
        children: []
      },
      {
        id: 'device_2',
        name: 'Chiller-02',
        type: 'Device',
        status: 'Active',
        parent: 'Chiller Plant',
        location: 'Chiller Room 1',
        manufacturer: 'Trane',
        model: 'CVHF-570',
        serialNumber: 'TR-CVHF-002',
        installDate: '2022-06-15',
        warrantyExpiry: '2027-06-15',
        uptime: 99.2,
        efficiency: 91,
        powerConsumption: 165,
        temperature: 22.8,
        dataPoints: 8,
        dataPointsList: [
          { id: 'point_6', name: 'Supply Temperature', pointType: 'Analog Input', unit: '°C', currentValue: 6.8, status: 'Good' },
          { id: 'point_7', name: 'Return Temperature', pointType: 'Analog Input', unit: '°C', currentValue: 13.2, status: 'Good' },
          { id: 'point_8', name: 'Power Consumption', pointType: 'Analog Input', unit: 'kW', currentValue: 165.2, status: 'Good' }
        ],
        children: []
      }
    ]
  },
  {
    id: 'asset_2',
    name: 'Air Handling System',
    type: 'Asset',
    status: 'Active',
    parent: 'Root',
    location: 'Building A, Mechanical Rooms',
    description: 'Air handling units for building ventilation',
    uptime: 99.5,
    efficiency: 88,
    powerConsumption: 320,
    temperature: 23.0,
    dataPoints: 0,
    children: [
      {
        id: 'device_3',
        name: 'AHU-01',
        type: 'Device',
        status: 'Active',
        parent: 'Air Handling System',
        location: 'Floor 1 Mechanical Room',
        manufacturer: 'Carrier',
        model: '39C-06',
        serialNumber: 'CR-39C-001',
        installDate: '2021-03-10',
        warrantyExpiry: '2026-03-10',
        uptime: 99.7,
        efficiency: 89,
        powerConsumption: 95,
        temperature: 22.5,
        dataPoints: 12,
        dataPointsList: [
          { id: 'point_9', name: 'Supply Air Temp', pointType: 'Analog Input', unit: '°C', currentValue: 14.2, status: 'Good' },
          { id: 'point_10', name: 'Return Air Temp', pointType: 'Analog Input', unit: '°C', currentValue: 23.5, status: 'Good' },
          { id: 'point_11', name: 'Fan Speed', pointType: 'Analog Input', unit: '%', currentValue: 65, status: 'Good' },
          { id: 'point_12', name: 'Filter Pressure Drop', pointType: 'Analog Input', unit: 'Pa', currentValue: 125, status: 'Warning' }
        ],
        children: []
      },
      {
        id: 'device_4',
        name: 'AHU-02',
        type: 'Device',
        status: 'Active',
        parent: 'Air Handling System',
        location: 'Floor 2 Mechanical Room',
        manufacturer: 'Carrier',
        model: '39C-08',
        serialNumber: 'CR-39C-002',
        installDate: '2021-03-10',
        warrantyExpiry: '2026-03-10',
        uptime: 99.4,
        efficiency: 87,
        powerConsumption: 110,
        temperature: 22.8,
        dataPoints: 12,
        dataPointsList: [
          { id: 'point_13', name: 'Supply Air Temp', pointType: 'Analog Input', unit: '°C', currentValue: 14.5, status: 'Good' },
          { id: 'point_14', name: 'Return Air Temp', pointType: 'Analog Input', unit: '°C', currentValue: 24.0, status: 'Good' },
          { id: 'point_15', name: 'Fan Speed', pointType: 'Analog Input', unit: '%', currentValue: 70, status: 'Good' }
        ],
        children: []
      }
    ]
  },
  {
    id: 'asset_3',
    name: 'Power Distribution',
    type: 'Asset',
    status: 'Active',
    parent: 'Root',
    location: 'Building A, Electrical Room',
    description: 'Main electrical distribution equipment',
    uptime: 99.9,
    efficiency: 96,
    powerConsumption: 0,
    temperature: 24.0,
    dataPoints: 0,
    children: [
      {
        id: 'device_5',
        name: 'UPS-01',
        type: 'Device',
        status: 'Active',
        parent: 'Power Distribution',
        location: 'Server Room',
        manufacturer: 'Schneider',
        model: 'Galaxy VX',
        serialNumber: 'SHD-GVX-001',
        installDate: '2023-01-20',
        warrantyExpiry: '2028-01-20',
        uptime: 99.99,
        efficiency: 95,
        powerConsumption: 45,
        temperature: 25.0,
        dataPoints: 10,
        dataPointsList: [
          { id: 'point_16', name: 'Input Voltage', pointType: 'Analog Input', unit: 'V', currentValue: 480, status: 'Good' },
          { id: 'point_17', name: 'Output Voltage', pointType: 'Analog Input', unit: 'V', currentValue: 480, status: 'Good' },
          { id: 'point_18', name: 'Load Percentage', pointType: 'Analog Input', unit: '%', currentValue: 35, status: 'Good' },
          { id: 'point_19', name: 'Battery Health', pointType: 'Analog Input', unit: '%', currentValue: 98, status: 'Good' }
        ],
        children: []
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
    'Asset': 'Document',
    'Device': 'Cpu',
    'Point': 'Connection'
  }
  return map[type] || 'Document'
}

const getNodeIconColor = (type: string) => {
  const map: Record<string, string> = {
    'Asset': '#409eff',
    'Device': '#67c23a',
    'Point': '#e6a23c'
  }
  return map[type] || '#909399'
}

const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Asset': 'primary',
    'Device': 'success',
    'Point': 'warning'
  }
  return map[type] || 'info'
}

const getPointTypeTag = (pointType: string) => {
  const map: Record<string, string> = {
    'Analog Input': 'primary',
    'Digital Input': 'success',
    'Analog Output': 'warning',
    'Digital Output': 'danger',
    'Calculated': 'info'
  }
  return map[pointType] || 'info'
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
    type: 'Device',
    parentId: selectedEntity.value?.id || null,
    status: 'Active',
    location: '',
    manufacturer: '',
    model: '',
    pointType: '',
    unit: '',
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
    location: entity.location || '',
    manufacturer: entity.manufacturer || '',
    model: entity.model || '',
    pointType: entity.pointType || '',
    unit: entity.unit || '',
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
    deleteDialogVisible.value = false
    deleteTarget.value = null
    selectedEntity.value = null
  }
}

const handleNodeClick = (data: any) => {
  selectedEntity.value = data
}

const navigateToEntity = (entity: any) => {
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

const viewPointDetails = (point: any) => {
  selectedPoint.value = point
  pointDialogVisible.value = true
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

  .metrics-section, .points-section, .children-section {
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

.point-details {
  // Styles for point details
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