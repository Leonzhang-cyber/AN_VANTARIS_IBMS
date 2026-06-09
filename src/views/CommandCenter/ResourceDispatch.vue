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
        <div class="loading-tip">Resource Dispatch Center</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="resource-dispatch-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Command Center</el-breadcrumb-item>
            <el-breadcrumb-item>Resource Dispatch</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Resource Dispatch Center</h1>
        <p class="description">Real-time resource management, personnel tracking, and emergency dispatch coordination</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="primary" @click="handleCreateDispatch">
          <el-icon><Plus /></el-icon>
          New Dispatch
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
                <span class="trend-label">vs last week</span>
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

    <!-- Map & Resource Status -->
    <el-row :gutter="20" class="map-row">
      <el-col :xs="24" :lg="16">
        <el-card class="map-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Resource Location Map</span>
              <div class="map-controls">
                <el-radio-group v-model="mapLayer" size="small">
                  <el-radio-button value="resources">Resources</el-radio-button>
                  <el-radio-button value="incidents">Incidents</el-radio-button>
                  <el-radio-button value="both">Both</el-radio-button>
                </el-radio-group>
                <el-button size="small" @click="refreshMap">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
          <div ref="mapChartRef" class="map-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="status-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Resource Status</span>
              <el-tag type="success" size="small">{{ availableResources }} Available</el-tag>
            </div>
          </template>
          <div class="resource-status-list">
            <div v-for="resource in resourceStatus" :key="resource.name" class="resource-status-item">
              <div class="resource-info">
                <div class="resource-name">{{ resource.name }}</div>
                <div class="resource-count">{{ resource.available }}/{{ resource.total }}</div>
              </div>
              <el-progress
                  :percentage="(resource.available / resource.total) * 100"
                  :color="resource.available / resource.total > 0.5 ? '#67c23a' : '#e6a23c'"
                  :stroke-width="8"
              />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Active Dispatches -->
    <el-card class="dispatch-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Active Dispatches</span>
          <el-button size="small" @click="refreshDispatches">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>

      <el-table :data="activeDispatches" stripe style="width: 100%" v-loading="dispatchLoading">
        <el-table-column prop="id" label="ID"  />
        <el-table-column prop="incident" label="Incident" min-width="180" show-overflow-tooltip />
        <el-table-column prop="location" label="Location"  />
        <el-table-column prop="priority" label="Priority" >
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resources" label="Resources" width="200">
          <template #default="{ row }">
            <el-popover placement="top" :width="250" trigger="hover">
              <template #reference>
                <el-tag type="info" size="small" style="cursor: pointer">
                  {{ row.resources.length }} items
                </el-tag>
              </template>
              <div v-for="r in row.resources" :key="r.id" class="resource-popover-item">
                {{ r.name }} - {{ r.type }}
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getDispatchStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="eta" label="ETA"  />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDispatch(row)">Track</el-button>
            <el-button link type="success" size="small" @click="updateStatus(row)">Update</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Personnel & Equipment -->
    <el-row :gutter="20" class="personnel-row">
      <el-col :xs="24" :lg="12">
        <el-card class="personnel-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Available Personnel</span>
              <el-button link type="primary" size="small" @click="viewAllPersonnel">View All</el-button>
            </div>
          </template>
          <el-table :data="availablePersonnel" stripe style="width: 100%" size="small">
            <el-table-column prop="name" label="Name"  />
            <el-table-column prop="role" label="Role"  />
            <el-table-column prop="location" label="Location"  />
            <el-table-column prop="status" label="Status" >
              <template #default="{ row }">
                <el-tag :type="row.status === 'Available' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Action" >
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="assignPersonnel(row)">Assign</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="equipment-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Available Equipment</span>
              <el-button link type="primary" size="small" @click="viewAllEquipment">View All</el-button>
            </div>
          </template>
          <el-table :data="availableEquipment" stripe style="width: 100%" size="small">
            <el-table-column prop="name" label="Equipment"  />
            <el-table-column prop="type" label="Type"  />
            <el-table-column prop="location" label="Location"  />
            <el-table-column prop="status" label="Status" >
              <template #default="{ row }">
                <el-tag :type="row.status === 'Available' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Action" >
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="assignEquipment(row)">Assign</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <!-- Dispatch History -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Recent Dispatch History</span>
          <el-button size="small" @click="toggleHistoryFilter">
            <el-icon><Search /></el-icon>
            Filter
          </el-button>
        </div>
      </template>

      <el-table :data="filteredHistory" stripe style="width: 100%" size="small">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="date" label="Date"  />
        <el-table-column prop="incident" label="Incident" min-width="180" show-overflow-tooltip />
        <el-table-column prop="resources" label="Resources Dispatched"  />
        <el-table-column prop="responseTime" label="Response Time"  />
        <el-table-column prop="resolutionTime" label="Resolution Time"  />
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="row.status === 'Completed' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="historyPage"
            v-model:page-size="historyPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="filteredHistory.length"
            @size-change="historyPage = 1"
        />
      </div>
    </el-card>

    <!-- New Dispatch Dialog -->
    <el-dialog v-model="dispatchDialogVisible" title="Create New Dispatch" width="600px" destroy-on-close>
      <el-form :model="dispatchForm" :rules="dispatchRules" ref="dispatchFormRef" label-width="120px">
        <el-form-item label="Incident Type" prop="incidentType">
          <el-select v-model="dispatchForm.incidentType" placeholder="Select incident type" style="width: 100%">
            <el-option label="Fire Emergency" value="Fire Emergency" />
            <el-option label="Medical Emergency" value="Medical Emergency" />
            <el-option label="Power Outage" value="Power Outage" />
            <el-option label="Equipment Failure" value="Equipment Failure" />
            <el-option label="Security Incident" value="Security Incident" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location" prop="location">
          <el-input v-model="dispatchForm.location" placeholder="Enter incident location" />
        </el-form-item>
        <el-form-item label="Priority" prop="priority">
          <el-radio-group v-model="dispatchForm.priority">
            <el-radio value="Critical">Critical</el-radio>
            <el-radio value="High">High</el-radio>
            <el-radio value="Medium">Medium</el-radio>
            <el-radio value="Low">Low</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Personnel Required" prop="personnelIds">
          <el-select v-model="dispatchForm.personnelIds" multiple placeholder="Select personnel" style="width: 100%">
            <el-option v-for="p in availablePersonnel" :key="p.id" :label="`${p.name} - ${p.role}`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Equipment Required" prop="equipmentIds">
          <el-select v-model="dispatchForm.equipmentIds" multiple placeholder="Select equipment" style="width: 100%">
            <el-option v-for="e in availableEquipment" :key="e.id" :label="`${e.name} (${e.type})`" :value="e.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="dispatchForm.description" type="textarea" :rows="2" placeholder="Enter incident description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dispatchDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitDispatch">Create Dispatch</el-button>
      </template>
    </el-dialog>

    <!-- Track Dispatch Dialog -->
    <el-dialog v-model="trackDialogVisible" :title="`Tracking: ${trackingDispatch?.incident}`" width="700px" destroy-on-close>
      <div class="tracking-container" v-if="trackingDispatch">
        <div class="tracking-timeline">
          <el-timeline>
            <el-timeline-item
                v-for="event in trackingDispatch.timeline"
                :key="event.id"
                :timestamp="event.time"
                :type="event.type"
            >
              {{ event.description }}
            </el-timeline-item>
          </el-timeline>
        </div>
        <div class="tracking-resources">
          <h4>Assigned Resources</h4>
          <el-table :data="trackingDispatch.resources" size="small" border>
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="type" label="Type" />
            <el-table-column prop="status" label="Status">
              <template #default="{ row }">
                <el-tag :type="row.status === 'En Route' ? 'warning' : (row.status === 'On Site' ? 'success' : 'info')" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="eta" label="ETA" />
          </el-table>
        </div>
        <div class="tracking-actions">
          <el-button type="primary" @click="updateResourceStatus">Update Status</el-button>
          <el-button @click="sendNotification">Send Notification</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="trackDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Location, User, Tools, Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading resource data...',
  'Loading dispatch records...',
  'Almost ready...'
]

// ==================== Chart References ====================
const mapChartRef = ref<HTMLElement>()
let mapChart: echarts.ECharts | null = null

// ==================== State ====================
const mapLayer = ref('both')
const dispatchLoading = ref(false)
const dispatchDialogVisible = ref(false)
const trackDialogVisible = ref(false)
const trackingDispatch = ref<any>(null)
const dispatchFormRef = ref()
const historyPage = ref(1)
const historyPageSize = ref(10)
const availableResources = ref(24)

// Mock Data
const statsCards = ref([
  { title: 'Active Dispatches', value: 8, trend: -12, icon: 'Warning', bgColor: '#f56c6c', key: 'active' },
  { title: 'Available Personnel', value: 32, trend: 8, icon: 'User', bgColor: '#67c23a', key: 'personnel' },
  { title: 'Available Equipment', value: 45, trend: 5, icon: 'Tools', bgColor: '#409eff', key: 'equipment' },
  { title: 'Avg Response Time', value: '8.2 min', trend: -15, icon: 'Clock', bgColor: '#e6a23c', key: 'response' }
])

const resourceStatus = ref([
  { name: 'Fire & Rescue', available: 12, total: 15 },
  { name: 'Medical Team', available: 8, total: 10 },
  { name: 'Technical Support', available: 15, total: 20 },
  { name: 'Security Personnel', available: 10, total: 12 },
  { name: 'Maintenance Crew', available: 18, total: 25 }
])

const activeDispatches = ref([
  {
    id: 'D-001',
    incident: 'Fire Alarm - Building A, Floor 3',
    location: 'Building A',
    priority: 'Critical',
    resources: [
      { id: 1, name: 'John Smith', type: 'Fire Captain', status: 'En Route', eta: '5 min' },
      { id: 2, name: 'Fire Truck F01', type: 'Vehicle', status: 'En Route', eta: '8 min' }
    ],
    status: 'In Progress',
    eta: '8 min',
    timeline: [
      { id: 1, time: '14:30', description: 'Alert received', type: 'primary' },
      { id: 2, time: '14:32', description: 'Resources dispatched', type: 'primary' },
      { id: 3, time: '14:35', description: 'En route to location', type: 'warning' }
    ]
  },
  {
    id: 'D-002',
    incident: 'Medical Emergency - Main Lobby',
    location: 'Main Lobby',
    priority: 'High',
    resources: [
      { id: 3, name: 'Sarah Chen', type: 'Paramedic', status: 'On Site', eta: 'On Site' }
    ],
    status: 'On Scene',
    eta: 'On Site',
    timeline: [
      { id: 1, time: '14:45', description: 'Alert received', type: 'primary' },
      { id: 2, time: '14:47', description: 'Resources dispatched', type: 'primary' },
      { id: 3, time: '14:52', description: 'Arrived on scene', type: 'success' }
    ]
  },
  {
    id: 'D-003',
    incident: 'Power Outage - Data Center',
    location: 'Data Center',
    priority: 'Critical',
    resources: [
      { id: 4, name: 'David Wang', type: 'Electrical Engineer', status: 'En Route', eta: '12 min' },
      { id: 5, name: 'Mike Johnson', type: 'Technician', status: 'En Route', eta: '10 min' },
      { id: 6, name: 'Generator G01', type: 'Equipment', status: 'Dispatched', eta: '20 min' }
    ],
    status: 'In Progress',
    eta: '10 min',
    timeline: [
      { id: 1, time: '15:00', description: 'Alert received', type: 'primary' },
      { id: 2, time: '15:02', description: 'Resources dispatched', type: 'primary' }
    ]
  }
])

const availablePersonnel = ref([
  { id: 1, name: 'John Smith', role: 'Fire Captain', location: 'Station A', status: 'Available' },
  { id: 2, name: 'Sarah Chen', role: 'Paramedic', location: 'Station B', status: 'On Call' },
  { id: 3, name: 'David Wang', role: 'Electrical Engineer', location: 'Workshop', status: 'Available' },
  { id: 4, name: 'Mike Johnson', role: 'HVAC Technician', location: 'Maintenance', status: 'Available' },
  { id: 5, name: 'Lisa Zhang', role: 'Safety Officer', location: 'Office', status: 'Available' },
  { id: 6, name: 'Tom Harris', role: 'IT Specialist', location: 'Data Center', status: 'On Call' }
])

const availableEquipment = ref([
  { id: 1, name: 'Fire Truck F01', type: 'Vehicle', location: 'Station A', status: 'Available' },
  { id: 2, name: 'Ambulance M01', type: 'Vehicle', location: 'Station B', status: 'In Use' },
  { id: 3, name: 'Generator G01', type: 'Power', location: 'Warehouse', status: 'Available' },
  { id: 4, name: 'Portable Pump P01', type: 'Pump', location: 'Warehouse', status: 'Available' },
  { id: 5, name: 'Rescue Kit R01', type: 'Kit', location: 'Station A', status: 'Available' },
  { id: 6, name: 'Mobile Command Unit', type: 'Vehicle', location: 'Parking', status: 'Available' }
])

const dispatchHistory = ref([
  { id: 1, date: '2024-01-18', incident: 'Small Fire - Cafeteria', resources: '2 Personnel, 1 Truck', responseTime: '6 min', resolutionTime: '25 min', status: 'Completed' },
  { id: 2, date: '2024-01-15', incident: 'Elevator Entrapment', resources: '3 Personnel', responseTime: '8 min', resolutionTime: '32 min', status: 'Completed' },
  { id: 3, date: '2024-01-12', incident: 'Water Leak - Basement', resources: '2 Personnel, 1 Pump', responseTime: '12 min', resolutionTime: '55 min', status: 'Completed' },
  { id: 4, date: '2024-01-10', incident: 'Security Breach - Gate', resources: '4 Security', responseTime: '4 min', resolutionTime: '18 min', status: 'Completed' }
])

const dispatchForm = reactive({
  incidentType: '',
  location: '',
  priority: 'Medium',
  personnelIds: [] as number[],
  equipmentIds: [] as number[],
  description: ''
})

const dispatchRules = {
  incidentType: [{ required: true, message: 'Please select incident type', trigger: 'change' }],
  location: [{ required: true, message: 'Please enter location', trigger: 'blur' }],
  priority: [{ required: true, message: 'Please select priority', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredHistory = computed(() => {
  return dispatchHistory.value
})

// ==================== Helper Methods ====================
const getPriorityTag = (priority: string): string => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[priority] || 'info'
}

const getDispatchStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'In Progress': 'warning',
    'On Scene': 'success',
    'Completed': 'success',
    'Cancelled': 'danger'
  }
  return map[status] || 'info'
}

// ==================== Map Initialization ====================
const initMapChart = () => {
  if (!mapChartRef.value) return
  if (mapChart) mapChart.dispose()

  mapChart = echarts.init(mapChartRef.value)

  const resourcesData = [
    { name: 'Station A', value: [116.40, 39.90], category: 'resource' },
    { name: 'Station B', value: [116.42, 39.92], category: 'resource' },
    { name: 'Warehouse', value: [116.38, 39.88], category: 'resource' }
  ]

  const incidentsData = [
    { name: 'Fire Alarm', value: [116.41, 39.91], category: 'incident' }
  ]

  const series: any[] = []

  if (mapLayer.value === 'resources' || mapLayer.value === 'both') {
    series.push({
      type: 'scatter',
      name: 'Resources',
      data: resourcesData.map(d => d.value),
      symbolSize: 20,
      itemStyle: { color: '#409eff' },
      label: { show: true, formatter: (p: any) => resourcesData[p.dataIndex]?.name, position: 'bottom' }
    })
  }

  if (mapLayer.value === 'incidents' || mapLayer.value === 'both') {
    series.push({
      type: 'scatter',
      name: 'Incidents',
      data: incidentsData.map(d => d.value),
      symbolSize: 25,
      itemStyle: { color: '#f56c6c' },
      label: { show: true, formatter: (p: any) => incidentsData[p.dataIndex]?.name, position: 'bottom' }
    })
  }

  const option: echarts.EChartsOption = {
    title: { show: false },
    tooltip: { trigger: 'item' },
    xAxis: { show: false, min: 116.35, max: 116.45 },
    yAxis: { show: false, min: 39.85, max: 39.95 },
    series: series,
    backgroundColor: '#f0f2f5'
  }

  mapChart.setOption(option)
  window.addEventListener('resize', () => mapChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting dispatch report...')
}

const handleCreateDispatch = () => {
  dispatchDialogVisible.value = true
}

const refreshMap = () => {
  initMapChart()
  ElMessage.success('Map refreshed')
}

const refreshDispatches = () => {
  dispatchLoading.value = true
  setTimeout(() => {
    dispatchLoading.value = false
    ElMessage.success('Dispatches refreshed')
  }, 500)
}

const viewDispatch = (dispatch: any) => {
  trackingDispatch.value = dispatch
  trackDialogVisible.value = true
}

const updateStatus = (dispatch: any) => {
  ElMessage.info(`Updating status for dispatch ${dispatch.id}`)
}

const assignPersonnel = (personnel: any) => {
  ElMessage.success(`${personnel.name} assigned to new dispatch`)
}

const assignEquipment = (equipment: any) => {
  ElMessage.success(`${equipment.name} assigned to new dispatch`)
}

const viewAllPersonnel = () => {
  ElMessage.info('Viewing all personnel')
}

const viewAllEquipment = () => {
  ElMessage.info('Viewing all equipment')
}

const toggleHistoryFilter = () => {
  ElMessage.info('Filter options would open here')
}

const submitDispatch = async () => {
  if (!dispatchFormRef.value) return
  await dispatchFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Dispatch created successfully')
      dispatchDialogVisible.value = false
      dispatchFormRef.value?.resetFields()
    }
  })
}

const updateResourceStatus = () => {
  ElMessage.success('Resource status updated')
}

const sendNotification = () => {
  ElMessage.success('Notification sent to all assigned resources')
}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initMapChart()
  }, 100)
}

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
      initCharts()
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
.resource-dispatch-page {
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

.map-row {
  margin-bottom: 20px;
}

.map-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .map-controls {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.map-container {
  width: 100%;
  height: 400px;
  background: #f0f2f5;
  border-radius: 8px;
}

.status-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.resource-status-list {
  .resource-status-item {
    margin-bottom: 16px;

    .resource-info {
      display: flex;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 14px;

      .resource-name {
        font-weight: 500;
        color: #303133;
      }

      .resource-count {
        color: #909399;
      }
    }
  }
}

.dispatch-card, .personnel-card, .equipment-card, .history-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.personnel-row {
  margin-bottom: 20px;
}

.resource-popover-item {
  padding: 4px 0;
  font-size: 13px;
}

.tracking-container {
  .tracking-timeline {
    margin-bottom: 24px;
  }

  .tracking-resources {
    margin-bottom: 24px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }

  .tracking-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;
  }
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>