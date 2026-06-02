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
        <div class="loading-tip">Device Groups</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="device-groups-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Groups</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" :icon="Plus" @click="openCreateGroupDialog">
          Create Group
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Folder /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ groups.length }}</span>
          <span class="stat-label">Total Groups</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Monitor /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ totalDevicesInGroups }}</span>
          <span class="stat-label">Devices in Groups</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Connection /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.onlineDevices }}</span>
          <span class="stat-label">Online Devices</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><DataLine /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ avgHealthScore.toFixed(1) }}%</span>
          <span class="stat-label">Avg Health Score</span>
        </div>
      </div>
    </div>

    <!-- 组列表 - 卡片视图 -->
    <div class="groups-container">
      <div v-for="group in groups" :key="group.id" class="group-card" :class="{ expanded: expandedGroupId === group.id }">
        <div class="group-header" @click="toggleGroupExpand(group.id)">
          <div class="group-info">
            <div class="group-icon" :style="{ backgroundColor: group.color }">
              <el-icon><component :is="getGroupIcon(group.icon)" /></el-icon>
            </div>
            <div class="group-details">
              <h3>{{ group.name }}</h3>
              <p>{{ group.description || 'No description' }}</p>
            </div>
          </div>
          <div class="group-stats">
            <div class="stat-badge">
              <el-icon><Monitor /></el-icon>
              <span>{{ group.devices.length }} devices</span>
            </div>
            <div class="stat-badge">
              <div class="health-indicator" :style="{ backgroundColor: getGroupHealthColor(group.healthScore) }"></div>
              <span>{{ group.healthScore.toFixed(1) }}%</span>
            </div>
            <el-button size="small" :icon="Edit" @click.stop="editGroup(group)">Edit</el-button>
            <el-dropdown trigger="click" @command="(cmd: string) => handleGroupCommand(cmd, group)">
              <el-button size="small" :icon="MoreFilled" @click.stop />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename">Rename</el-dropdown-item>
                  <el-dropdown-item command="duplicate">Duplicate</el-dropdown-item>
                  <el-dropdown-item command="export">Export Devices</el-dropdown-item>
                  <el-dropdown-item divided command="delete">Delete</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <!-- 组内设备列表（展开时显示） -->
        <transition name="expand">
          <div v-if="expandedGroupId === group.id" class="group-devices">
            <div class="devices-header">
              <span>Devices in this group</span>
              <el-button size="small" :icon="Plus" @click="addDeviceToGroup(group)">Add Device</el-button>
            </div>
            <el-table :data="group.devices" stripe border size="small" style="width: 100%">
              <el-table-column type="index" label="#" width="40" />
              <el-table-column label="Device" min-width="200">
                <template #default="{ row }">
                  <div class="device-cell">
                    <el-avatar :src="row.imageUrl" :size="28" shape="square" fit="cover">
                      <template #error><el-icon><Cpu /></el-icon></template>
                    </el-avatar>
                    <div class="device-info">
                      <span class="device-name">{{ row.name }}</span>
                      <span class="device-model">{{ row.model }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="systemType" label="System" width="100">
                <template #default="{ row }">
                  <el-tag :type="getSystemTagType(row.systemType)" size="small">{{ getSystemLabel(row.systemType) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Status" width="100">
                <template #default="{ row }">
                  <div class="status-cell">
                    <div class="status-indicator" :class="row.status"></div>
                    <span>{{ row.status.toUpperCase() }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="Health" width="120">
                <template #default="{ row }">
                  <el-progress :percentage="row.healthScore" :stroke-width="6" :color="getHealthColor(row.healthScore)" :show-text="false" style="width: 80px" />
                  <span style="margin-left: 8px">{{ row.healthScore.toFixed(1) }}%</span>
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="100">
                <template #default="{ row }">
                  <el-button size="small" text @click.stop="viewDevice(row)">View</el-button>
                  <el-button size="small" text type="danger" @click.stop="removeDeviceFromGroup(group, row)">Remove</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </transition>
      </div>

      <!-- 空状态 -->
      <div v-if="groups.length === 0" class="empty-state">
        <el-empty description="No device groups created">
          <el-button type="primary" @click="openCreateGroupDialog">Create Your First Group</el-button>
        </el-empty>
      </div>
    </div>

    <!-- 创建/编辑组对话框 -->
    <el-dialog v-model="groupDialogVisible" :title="editingGroup ? 'Edit Group' : 'Create New Group'" width="500px">
      <el-form :model="groupForm" :rules="groupRules" ref="groupFormRef" label-width="100px">
        <el-form-item label="Group Name" prop="name">
          <el-input v-model="groupForm.name" placeholder="Enter group name" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="groupForm.description" type="textarea" :rows="3" placeholder="Enter group description" />
        </el-form-item>
        <el-form-item label="Icon" prop="icon">
          <el-select v-model="groupForm.icon" placeholder="Select icon" style="width: 100%">
            <el-option label="🏠 Building" value="building" />
            <el-option label="❄️ HVAC" value="hvac" />
            <el-option label="💡 Lighting" value="lighting" />
            <el-option label="🔒 Security" value="security" />
            <el-option label="🔥 Fire" value="fire" />
            <el-option label="💧 Plumbing" value="plumbing" />
            <el-option label="⚡ Power" value="power" />
            <el-option label="📊 Analytics" value="analytics" />
            <el-option label="🖥️ IT" value="it" />
            <el-option label="🏭 Industrial" value="industrial" />
          </el-select>
        </el-form-item>
        <el-form-item label="Color" prop="color">
          <el-color-picker v-model="groupForm.color" show-alpha :predefine="predefineColors" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="groupDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveGroup" :loading="saving">Save</el-button>
      </template>
    </el-dialog>

    <!-- 添加设备到组对话框 -->
    <el-dialog v-model="addDeviceDialogVisible" :title="`Add Devices to ${selectedGroup?.name || 'Group'}`" width="600px">
      <div class="add-device-search">
        <el-input
            v-model="deviceSearchKeyword"
            placeholder="Search devices..."
            clearable
            :prefix-icon="Search"
        />
      </div>
      <el-table
          :data="availableDevices"
          stripe
          @selection-change="handleDeviceSelectionChange"
          max-height="400"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="Device" min-width="200">
          <template #default="{ row }">
            <div class="device-cell">
              <el-avatar :src="row.imageUrl" :size="28" shape="square" fit="cover">
                <template #error><el-icon><Cpu /></el-icon></template>
              </el-avatar>
              <div class="device-info">
                <span class="device-name">{{ row.name }}</span>
                <span class="device-model">{{ row.model }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="systemType" label="System" width="100">
          <template #default="{ row }">
            <el-tag :type="getSystemTagType(row.systemType)" size="small">{{ getSystemLabel(row.systemType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <div class="status-cell">
              <div class="status-indicator" :class="row.status"></div>
              <span>{{ row.status.toUpperCase() }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="addDeviceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAddDevices" :disabled="selectedDevicesToAdd.length === 0">
          Add {{ selectedDevicesToAdd.length }} Device(s)
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus, Edit, MoreFilled, Folder, Monitor, Connection, DataLine,
  Cpu, Search, Delete, CopyDocument, Download
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading device groups...')
const router = useRouter()
const loadingMessages = ['Initializing...', 'Loading device groups...', 'Loading devices...', 'Almost ready...']

// ==================== Types ====================
interface Device {
  id: string
  name: string
  model: string
  manufacturer: string
  serialNumber: string
  systemType: string
  area: string
  status: 'online' | 'offline' | 'warning' | 'error'
  imageUrl: string
  healthScore: number
}

interface DeviceGroup {
  id: string
  name: string
  description: string
  icon: string
  color: string
  devices: Device[]
  healthScore: number
  createdAt: string
}

// ==================== State ====================
const groups = ref<DeviceGroup[]>([])
const expandedGroupId = ref<string | null>(null)
const groupDialogVisible = ref(false)
const editingGroup = ref<DeviceGroup | null>(null)
const saving = ref(false)
const addDeviceDialogVisible = ref(false)
const selectedGroup = ref<DeviceGroup | null>(null)
const deviceSearchKeyword = ref('')
const selectedDevicesToAdd = ref<Device[]>([])
const groupFormRef = ref<FormInstance>()

// 表单数据
const groupForm = ref({
  name: '',
  description: '',
  icon: 'building',
  color: '#409eff'
})

const groupRules: FormRules = {
  name: [{ required: true, message: 'Please enter group name', trigger: 'blur' }]
}

const predefineColors = [
  '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399',
  '#5470c6', '#fac858', '#ee6666', '#73c0de', '#3ba272'
]

// ==================== Mock Data ====================
// 生成模拟设备数据
const generateMockDevices = (): Device[] => {
  const baseDevices = [
    { id: '1', name: 'AHU-B2-01 Air Handler', model: 'Carrier 39G', manufacturer: 'Carrier', serial: 'CA-2024-B201', system: 'hvac', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', status: 'online', health: 94.2 },
    { id: '2', name: 'FCU-B2-01 Fan Coil', model: 'Daikin FXMQ', manufacturer: 'Daikin', serial: 'DK-2024-B201', system: 'hvac', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013141234431.webp', status: 'online', health: 91.5 },
    { id: '3', name: 'CH-B2-01 Chiller', model: 'Carrier AquaEdge', manufacturer: 'Carrier', serial: 'CA-2024-B202', system: 'hvac', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013145678.jpg', status: 'warning', health: 65.8 },
    { id: '4', name: 'EF-B2-02 Exhaust Fan', model: 'Greenheck CUBE', manufacturer: 'Greenheck', serial: 'GH-2024-B202', system: 'hvac', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/520131452044.webp', status: 'error', health: 35.2 },
    { id: '5', name: 'LIGHT-B2-01 Controller', model: 'Philips Dynalite', manufacturer: 'Philips', serial: 'PH-2024-B201', system: 'lighting', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp', status: 'online', health: 96.3 },
    { id: '6', name: 'ACS-1F-01 Entrance', model: 'HID VertX', manufacturer: 'HID', serial: 'HD-2024-1F01', system: 'sas', area: 'Lobby 1F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147643.jpg', status: 'online', health: 98.1 },
    { id: '7', name: 'SD-1F-01 Smoke Detector', model: 'Honeywell XLS', manufacturer: 'Honeywell', serial: 'HW-2024-1F01', system: 'fas', area: 'Lobby 1F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567123.jpg', status: 'online', health: 99.0 },
    { id: '8', name: 'PUMP-B2-02 Booster', model: 'Grundfos CR', manufacturer: 'Grundfos', serial: 'GF-2024-B202', system: 'plumbing', area: 'Basement B2', img: 'https://aegisnx.com/wp-content/uploads/2026/05/1779181211735.png', status: 'warning', health: 55.7 },
    { id: '9', name: 'AHU-2F-01 Air Handler', model: 'Trane IntelliPak', manufacturer: 'Trane', serial: 'TR-2024-2F01', system: 'hvac', area: 'Office 2F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/5201314567.webp', status: 'error', health: 28.6 },
    { id: '10', name: 'LIGHT-1F-01 Lobby Light', model: 'Lutron Quantum', manufacturer: 'Lutron', serial: 'LT-2024-1F01', system: 'lighting', area: 'Lobby 1F', img: 'https://aegisnx.com/wp-content/uploads/2026/05/52013147890.webp', status: 'online', health: 97.4 }
  ]

  return baseDevices.map(d => ({
    id: d.id,
    name: d.name,
    model: d.model,
    manufacturer: d.manufacturer,
    serialNumber: d.serial,
    systemType: d.system,
    area: d.area,
    status: d.status as any,
    imageUrl: d.img,
    healthScore: d.health
  }))
}

const allDevices = ref<Device[]>([])

// 生成模拟组数据
const generateMockGroups = (devices: Device[]): DeviceGroup[] => {
  const hvacDevices = devices.filter(d => d.systemType === 'hvac')
  const lightingDevices = devices.filter(d => d.systemType === 'lighting')
  const securityDevices = devices.filter(d => d.systemType === 'sas')
  const criticalDevices = devices.filter(d => d.healthScore < 60)

  const calculateGroupHealth = (deviceList: Device[]) => {
    if (deviceList.length === 0) return 100
    const sum = deviceList.reduce((s, d) => s + d.healthScore, 0)
    return sum / deviceList.length
  }

  return [
    {
      id: '1',
      name: 'HVAC Systems',
      description: 'All heating, ventilation and air conditioning equipment',
      icon: 'hvac',
      color: '#5470c6',
      devices: hvacDevices,
      healthScore: calculateGroupHealth(hvacDevices),
      createdAt: '2024-01-15'
    },
    {
      id: '2',
      name: 'Lighting Controls',
      description: 'Building lighting and dimming systems',
      icon: 'lighting',
      color: '#fac858',
      devices: lightingDevices,
      healthScore: calculateGroupHealth(lightingDevices),
      createdAt: '2024-01-20'
    },
    {
      id: '3',
      name: 'Security Systems',
      description: 'Access control and surveillance equipment',
      icon: 'security',
      color: '#73c0de',
      devices: securityDevices,
      healthScore: calculateGroupHealth(securityDevices),
      createdAt: '2024-02-01'
    },
    {
      id: '4',
      name: 'Critical Alerts',
      description: 'Devices requiring immediate attention',
      icon: 'alert',
      color: '#f56c6c',
      devices: criticalDevices,
      healthScore: calculateGroupHealth(criticalDevices),
      createdAt: '2024-02-10'
    }
  ]
}

// ==================== Computed ====================
const totalDevicesInGroups = computed(() => {
  const allDevIds = new Set<string>()
  groups.value.forEach(g => g.devices.forEach(d => allDevIds.add(d.id)))
  return allDevIds.size
})

const stats = computed(() => {
  let onlineDevices = 0
  groups.value.forEach(g => {
    onlineDevices += g.devices.filter(d => d.status === 'online').length
  })
  return { onlineDevices }
})

const avgHealthScore = computed(() => {
  if (groups.value.length === 0) return 0
  const sum = groups.value.reduce((s, g) => s + g.healthScore, 0)
  return sum / groups.value.length
})

const availableDevices = computed(() => {
  if (!selectedGroup.value) return []
  const existingDeviceIds = new Set(selectedGroup.value.devices.map(d => d.id))
  let available = allDevices.value.filter(d => !existingDeviceIds.has(d.id))

  if (deviceSearchKeyword.value) {
    const kw = deviceSearchKeyword.value.toLowerCase()
    available = available.filter(d =>
        d.name.toLowerCase().includes(kw) ||
        d.model.toLowerCase().includes(kw) ||
        d.serialNumber.toLowerCase().includes(kw)
    )
  }
  return available
})

// ==================== Helper Functions ====================
const toOneDecimal = (num: number): number => Math.round(num * 10) / 10

const getGroupIcon = (iconName: string) => {
  const icons: Record<string, any> = {
    building: Folder,
    hvac: Cpu,
    lighting: Monitor,
    security: Connection,
    fire: DataLine,
    plumbing: DataLine,
    power: DataLine,
    analytics: DataLine,
    it: Cpu,
    industrial: Cpu,
    alert: DataLine
  }
  return icons[iconName] || Folder
}

const getGroupHealthColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}

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

const getHealthColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#409eff'
  if (score >= 40) return '#e6a23c'
  return '#f56c6c'
}

// ==================== Actions ====================
const toggleGroupExpand = (groupId: string) => {
  expandedGroupId.value = expandedGroupId.value === groupId ? null : groupId
}

const openCreateGroupDialog = () => {
  editingGroup.value = null
  groupForm.value = {
    name: '',
    description: '',
    icon: 'building',
    color: '#409eff'
  }
  groupDialogVisible.value = true
}

const editGroup = (group: DeviceGroup) => {
  editingGroup.value = group
  groupForm.value = {
    name: group.name,
    description: group.description,
    icon: group.icon,
    color: group.color
  }
  groupDialogVisible.value = true
}

const saveGroup = async () => {
  if (!groupFormRef.value) return
  await groupFormRef.value.validate(async (valid) => {
    if (valid) {
      saving.value = true
      await new Promise(resolve => setTimeout(resolve, 500))

      if (editingGroup.value) {
        // 更新现有组
        const index = groups.value.findIndex(g => g.id === editingGroup.value!.id)
        if (index !== -1) {
          groups.value[index] = {
            ...groups.value[index],
            name: groupForm.value.name,
            description: groupForm.value.description,
            icon: groupForm.value.icon,
            color: groupForm.value.color
          }
        }
        ElMessage.success('Group updated successfully')
      } else {
        // 创建新组
        const newGroup: DeviceGroup = {
          id: Date.now().toString(),
          name: groupForm.value.name,
          description: groupForm.value.description,
          icon: groupForm.value.icon,
          color: groupForm.value.color,
          devices: [],
          healthScore: 100,
          createdAt: new Date().toISOString()
        }
        groups.value.push(newGroup)
        ElMessage.success('Group created successfully')
      }

      groupDialogVisible.value = false
      saving.value = false
    }
  })
}

const handleGroupCommand = (command: string, group: DeviceGroup) => {
  switch (command) {
    case 'rename':
      editGroup(group)
      break
    case 'duplicate':
      duplicateGroup(group)
      break
    case 'export':
      exportGroupDevices(group)
      break
    case 'delete':
      deleteGroup(group)
      break
  }
}

const duplicateGroup = async (group: DeviceGroup) => {
  const newGroup: DeviceGroup = {
    ...group,
    id: Date.now().toString(),
    name: `${group.name} (Copy)`,
    createdAt: new Date().toISOString()
  }
  groups.value.push(newGroup)
  ElMessage.success(`Group "${group.name}" duplicated`)
}

const exportGroupDevices = (group: DeviceGroup) => {
  ElMessage.success(`Exporting ${group.devices.length} devices from "${group.name}"`)
}

const deleteGroup = async (group: DeviceGroup) => {
  try {
    await ElMessageBox.confirm(
        `Are you sure you want to delete group "${group.name}"? This action cannot be undone.`,
        'Confirm Delete',
        { confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning' }
    )
    groups.value = groups.value.filter(g => g.id !== group.id)
    if (expandedGroupId.value === group.id) {
      expandedGroupId.value = null
    }
    ElMessage.success('Group deleted')
  } catch (error) {
    // cancelled
  }
}

const addDeviceToGroup = (group: DeviceGroup) => {
  selectedGroup.value = group
  deviceSearchKeyword.value = ''
  selectedDevicesToAdd.value = []
  addDeviceDialogVisible.value = true
}

const handleDeviceSelectionChange = (selection: Device[]) => {
  selectedDevicesToAdd.value = selection
}

const confirmAddDevices = () => {
  if (!selectedGroup.value || selectedDevicesToAdd.value.length === 0) return

  selectedGroup.value.devices.push(...selectedDevicesToAdd.value)

  // 重新计算组健康分数
  const sum = selectedGroup.value.devices.reduce((s, d) => s + d.healthScore, 0)
  selectedGroup.value.healthScore = toOneDecimal(sum / selectedGroup.value.devices.length)

  addDeviceDialogVisible.value = false
  ElMessage.success(`Added ${selectedDevicesToAdd.value.length} device(s) to "${selectedGroup.value.name}"`)
}

const removeDeviceFromGroup = async (group: DeviceGroup, device: Device) => {
  try {
    await ElMessageBox.confirm(
        `Remove "${device.name}" from group "${group.name}"?`,
        'Confirm Remove',
        { confirmButtonText: 'Remove', cancelButtonText: 'Cancel', type: 'info' }
    )
    group.devices = group.devices.filter(d => d.id !== device.id)

    // 重新计算组健康分数
    if (group.devices.length > 0) {
      const sum = group.devices.reduce((s, d) => s + d.healthScore, 0)
      group.healthScore = toOneDecimal(sum / group.devices.length)
    } else {
      group.healthScore = 100
    }

    ElMessage.success(`Removed "${device.name}" from group`)
  } catch (error) {
    // cancelled
  }
}

const viewDevice = (device: Device) => {
  router.push(`/systems-devices/device-inventory/device-details/${device.id}`)
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
      allDevices.value = generateMockDevices()
      groups.value = generateMockGroups(allDevices.value)
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

.device-groups-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat-icon .el-icon { font-size: 32px; color: #3b82f6; }
.stat-info .stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-info .stat-label { font-size: 13px; color: #64748b; }

.groups-container { display: flex; flex-direction: column; gap: 16px; }
.group-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.group-card:hover { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.group-card.expanded { box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12); }

.group-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; cursor: pointer; transition: background 0.2s; }
.group-header:hover { background: #f8fafc; }
.group-info { display: flex; align-items: center; gap: 16px; }
.group-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.group-icon .el-icon { font-size: 24px; }
.group-details h3 { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #1e293b; }
.group-details p { margin: 0; font-size: 12px; color: #64748b; }
.group-stats { display: flex; align-items: center; gap: 16px; }
.stat-badge { display: flex; align-items: center; gap: 6px; padding: 6px 12px; background: #f1f5f9; border-radius: 20px; font-size: 13px; color: #1e293b; }
.health-indicator { width: 8px; height: 8px; border-radius: 50%; }

.group-devices { border-top: 1px solid #e2e8f0; padding: 16px 20px; background: #fafbfc; }
.devices-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.devices-header span { font-weight: 600; color: #1e293b; }

.expand-enter-active, .expand-leave-active { transition: all 0.3s ease; }
.expand-enter-from, .expand-leave-to { opacity: 0; transform: translateY(-10px); }

.empty-state { padding: 60px; text-align: center; background: white; border-radius: 12px; }

.device-cell { display: flex; align-items: center; gap: 12px; }
.device-info { display: flex; flex-direction: column; }
.device-name { font-weight: 500; color: #1e293b; font-size: 13px; }
.device-model { font-size: 11px; color: #64748b; }
.status-cell { display: flex; align-items: center; gap: 6px; }
.status-indicator { width: 8px; height: 8px; border-radius: 50%; }
.status-indicator.online { background: #10b981; }
.status-indicator.warning { background: #f59e0b; animation: pulse 2s infinite; }
.status-indicator.error { background: #ef4444; animation: pulse 1s infinite; }
.status-indicator.offline { background: #6b7280; }

.add-device-search { margin-bottom: 16px; }

@media (max-width: 1024px) { .stats-cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .stats-cards { grid-template-columns: 1fr; }
  .group-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .group-stats { width: 100%; justify-content: space-between; }
}
</style>