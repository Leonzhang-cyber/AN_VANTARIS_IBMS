<script setup lang="ts">
import { ref, onMounted, computed, watch, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  User, Monitor, BellFilled, Refresh, Connection, Setting,
  Search, Lock, Key, Clock,
  UserFilled, Cellphone, Location, Warning
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing Access SDK...',
  'Connecting to access controllers...',
  'Syncing door status...',
  'Loading user database...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const searchUserKeyword = ref('')
const doorControlVisible = ref(false)
const configDrawerVisible = ref(false)
const userDetailsVisible = ref(false)
const accessLogsVisible = ref(false)
const doorChartRef = ref(null)
const accessChartRef = ref(null)

let doorChart: echarts.ECharts | null = null
let accessChart: echarts.ECharts | null = null

const selectedDoor = ref<any>(null)
const selectedUser = ref<any>(null)
const currentChartPeriod = ref('week')

// Statistics data
const stats = reactive({
  totalDoors: 45,
  onlineDoors: 43,
  offlineDoors: 2,
  onlineRate: 95.6,
  totalUsers: 1250,
  activeUsers: 1180,
  todayAccess: 3420,
  todayDenied: 156,
  totalReaders: 52,
  totalControllers: 12,
  pendingRequests: 8,
  expiredCards: 45
})

// Doors data
const doors = ref([
  { id: 'D001', name: 'Main Entrance', location: 'Lobby', ip: '192.168.6.101', status: 'online', locked: false, lastHeartbeat: '2024-01-15 10:23:45', controllerId: 'C001', doorType: 'Swing', todayAccess: 342, firmware: 'v2.1.0' },
  { id: 'D002', name: 'Side Entrance', location: 'East Wing', ip: '192.168.6.102', status: 'online', locked: false, lastHeartbeat: '2024-01-15 10:22:30', controllerId: 'C001', doorType: 'Swing', todayAccess: 187, firmware: 'v2.1.0' },
  { id: 'D003', name: 'Back Entrance', location: 'West Wing', ip: '192.168.6.103', status: 'online', locked: true, lastHeartbeat: '2024-01-15 10:24:12', controllerId: 'C002', doorType: 'Swing', todayAccess: 56, firmware: 'v2.0.5' },
  { id: 'D004', name: 'Server Room', location: 'B2 Data Center', ip: '192.168.6.104', status: 'online', locked: true, lastHeartbeat: '2024-01-15 10:20:00', controllerId: 'C003', doorType: 'Sliding', todayAccess: 23, firmware: 'v2.1.2' },
  { id: 'D005', name: 'Executive Office', location: '5F East', ip: '192.168.6.105', status: 'online', locked: false, lastHeartbeat: '2024-01-15 10:23:00', controllerId: 'C004', doorType: 'Swing', todayAccess: 89, firmware: 'v2.1.0' },
  { id: 'D006', name: 'HR Department', location: '4F', ip: '192.168.6.106', status: 'offline', locked: false, lastHeartbeat: '2024-01-14 18:30:00', controllerId: 'C005', doorType: 'Swing', todayAccess: 0, firmware: 'v2.0.5' },
  { id: 'D007', name: 'IT Department', location: '3F', ip: '192.168.6.107', status: 'online', locked: false, lastHeartbeat: '2024-01-15 10:22:15', controllerId: 'C006', doorType: 'Swing', todayAccess: 67, firmware: 'v2.1.0' },
  { id: 'D008', name: 'Finance Department', location: '2F', ip: '192.168.6.108', status: 'online', locked: true, lastHeartbeat: '2024-01-15 10:21:30', controllerId: 'C007', doorType: 'Swing', todayAccess: 34, firmware: 'v2.1.2' },
  { id: 'D009', name: 'R&D Lab', location: 'B1 Lab', ip: '192.168.6.109', status: 'online', locked: true, lastHeartbeat: '2024-01-15 10:23:45', controllerId: 'C008', doorType: 'Sliding', todayAccess: 45, firmware: 'v2.0.8' },
  { id: 'D010', name: 'Emergency Exit', location: 'North Staircase', ip: '192.168.6.110', status: 'online', locked: false, lastHeartbeat: '2024-01-15 10:22:30', controllerId: 'C009', doorType: 'Fire', todayAccess: 12, firmware: 'v2.0.5' },
  { id: 'D011', name: 'Warehouse Entrance', location: 'Warehouse', ip: '192.168.6.111', status: 'online', locked: false, lastHeartbeat: '2024-01-15 10:24:12', controllerId: 'C010', doorType: 'Rolling', todayAccess: 78, firmware: 'v2.1.0' },
  { id: 'D012', name: 'Parking Gate', location: 'Underground', ip: '192.168.6.112', status: 'offline', locked: false, lastHeartbeat: '2024-01-14 22:15:00', controllerId: 'C011', doorType: 'Barrier', todayAccess: 0, firmware: 'v2.0.5' }
])

// Users data
const users = ref([
  { id: 'U001', name: 'John Smith', email: 'john.smith@company.com', department: 'IT', role: 'Employee', cardId: 'CARD001', accessLevel: 'Level 3', lastAccess: '2024-01-15 09:15:23', status: 'Active', phone: '+65 9123 4567' },
  { id: 'U002', name: 'Sarah Johnson', email: 'sarah.j@company.com', department: 'HR', role: 'Manager', cardId: 'CARD002', accessLevel: 'Level 4', lastAccess: '2024-01-15 08:45:12', status: 'Active', phone: '+65 9234 5678' },
  { id: 'U003', name: 'Michael Chen', email: 'michael.chen@company.com', department: 'Finance', role: 'Employee', cardId: 'CARD003', accessLevel: 'Level 2', lastAccess: '2024-01-15 10:30:45', status: 'Active', phone: '+65 9345 6789' },
  { id: 'U004', name: 'Emily Wong', email: 'emily.wong@company.com', department: 'Executive', role: 'Executive', cardId: 'CARD004', accessLevel: 'Level 5', lastAccess: '2024-01-15 07:55:30', status: 'Active', phone: '+65 9456 7890' },
  { id: 'U005', name: 'David Lee', email: 'david.lee@company.com', department: 'R&D', role: 'Employee', cardId: 'CARD005', accessLevel: 'Level 3', lastAccess: '2024-01-14 17:30:00', status: 'Active', phone: '+65 9567 8901' },
  { id: 'U006', name: 'Lisa Tan', email: 'lisa.tan@company.com', department: 'HR', role: 'Employee', cardId: 'CARD006', accessLevel: 'Level 2', lastAccess: '2024-01-15 09:45:22', status: 'Inactive', phone: '+65 9678 9012' },
  { id: 'U007', name: 'James Wilson', email: 'james.w@company.com', department: 'Security', role: 'Security', cardId: 'CARD007', accessLevel: 'Level 5', lastAccess: '2024-01-15 10:15:34', status: 'Active', phone: '+65 9789 0123' },
  { id: 'U008', name: 'Maria Garcia', email: 'maria.g@company.com', department: 'Marketing', role: 'Employee', cardId: 'CARD008', accessLevel: 'Level 2', lastAccess: '2024-01-14 16:20:15', status: 'Active', phone: '+65 9890 1234' }
])

// Recent access logs
const accessLogs = ref([
  { id: 'L001', user: 'John Smith', door: 'Main Entrance', time: '2024-01-15 10:23:45', status: 'Granted', credentialType: 'Card' },
  { id: 'L002', user: 'Unknown', door: 'Back Entrance', time: '2024-01-15 10:22:30', status: 'Denied', credentialType: 'Invalid Card', reason: 'Unauthorized' },
  { id: 'L003', user: 'Sarah Johnson', door: 'Executive Office', time: '2024-01-15 10:15:22', status: 'Granted', credentialType: 'Fingerprint' },
  { id: 'L004', user: 'Michael Chen', door: 'Server Room', time: '2024-01-15 10:08:45', status: 'Denied', credentialType: 'Card', reason: 'Insufficient Access Level' },
  { id: 'L005', user: 'Emily Wong', door: 'Main Entrance', time: '2024-01-15 09:55:12', status: 'Granted', credentialType: 'Face Recognition' },
  { id: 'L006', user: 'David Lee', door: 'R&D Lab', time: '2024-01-15 09:42:33', status: 'Granted', credentialType: 'Card' },
  { id: 'L007', user: 'James Wilson', door: 'Server Room', time: '2024-01-15 09:30:18', status: 'Granted', credentialType: 'Fingerprint' },
  { id: 'L008', user: 'Unknown', door: 'Emergency Exit', time: '2024-01-15 09:15:05', status: 'Alert', credentialType: 'Force Open', reason: 'Door Forced' }
])

// Platform configuration
const platformConfig = ref({
  host: 'https://access-platform.example.com',
  apiKey: '',
  databaseUrl: '',
  syncInterval: 900,
  lockdownPassword: '',
  doorOpenDuration: 10,
  maxFailedAttempts: 5,
  emailNotifications: true,
  smsNotifications: false
})

// Door control form
const doorControlForm = ref({
  action: 'unlock',
  duration: 30,
  reason: ''
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: doors.value.length
})

const userPagination = reactive({
  page: 1,
  pageSize: 10,
  total: users.value.length
})

// Filtered doors
const filteredDoors = computed(() => {
  let filtered = doors.value
  if (searchKeyword.value) {
    filtered = filtered.filter(d =>
        d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.location.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        d.controllerId.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// Filtered users
const filteredUsers = computed(() => {
  let filtered = users.value
  if (searchUserKeyword.value) {
    filtered = filtered.filter(u =>
        u.name.toLowerCase().includes(searchUserKeyword.value.toLowerCase()) ||
        u.id.toLowerCase().includes(searchUserKeyword.value.toLowerCase()) ||
        u.department.toLowerCase().includes(searchUserKeyword.value.toLowerCase()) ||
        u.cardId.toLowerCase().includes(searchUserKeyword.value.toLowerCase())
    )
  }
  userPagination.total = filtered.length
  const start = (userPagination.page - 1) * userPagination.pageSize
  const end = start + userPagination.pageSize
  return filtered.slice(start, end)
})

// Watch for search keywords to reset pagination
watch(searchKeyword, () => {
  pagination.page = 1
})

watch(searchUserKeyword, () => {
  userPagination.page = 1
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
      setTimeout(() => {
        initDoorChart()
        initAccessChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initDoorChart = () => {
  if (!doorChartRef.value) return

  doorChart = echarts.init(doorChartRef.value)
  updateDoorChart()
}

const updateDoorChart = () => {
  const weekData = {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    online: [43, 44, 44, 45, 45, 44, 43],
    offline: [2, 1, 1, 0, 0, 1, 2]
  }

  const monthData = {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    online: [44, 44, 45, 44],
    offline: [1, 1, 0, 1]
  }

  const data = currentChartPeriod.value === 'week' ? weekData : monthData

  doorChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Online Doors', 'Offline Doors'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: data.xAxis },
    yAxis: { type: 'value', name: 'Doors' },
    series: [
      { name: 'Online Doors', type: 'line', data: data.online, smooth: true, lineStyle: { color: '#67C23A', width: 2 }, areaStyle: { opacity: 0.1, color: '#67C23A' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Offline Doors', type: 'line', data: data.offline, smooth: true, lineStyle: { color: '#F56C6C', width: 2 }, symbol: 'diamond', symbolSize: 8 }
    ]
  })
}

const initAccessChart = () => {
  if (!accessChartRef.value) return

  accessChart = echarts.init(accessChartRef.value)
  updateAccessChart()
}

const updateAccessChart = () => {
  const weekData = {
    xAxis: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    granted: [2850, 2950, 3100, 3250, 3420, 2100, 1850],
    denied: [125, 130, 145, 150, 156, 45, 38]
  }

  const monthData = {
    xAxis: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    granted: [19800, 20500, 21500, 22200],
    denied: [850, 890, 920, 950]
  }

  const data = currentChartPeriod.value === 'week' ? weekData : monthData

  accessChart?.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Granted Access', 'Denied Access'], bottom: 0 },
    xAxis: { type: 'category', data: data.xAxis },
    yAxis: { type: 'value', name: 'Access Events' },
    series: [
      { name: 'Granted Access', type: 'bar', data: data.granted, itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Denied Access', type: 'bar', data: data.denied, itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const handleResize = () => {
  doorChart?.resize()
  accessChart?.resize()
}

// ==================== Actions ====================
const formatTime = (time: string) => {
  return time
}

const toggleChartPeriod = () => {
  currentChartPeriod.value = currentChartPeriod.value === 'week' ? 'month' : 'week'
  updateDoorChart()
  updateAccessChart()
}

const syncDevices = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('Door synchronization completed successfully')
  } catch (error) {
    ElMessage.error('Sync failed')
  } finally {
    loading.value = false
  }
}

const testConnection = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    ElMessage.success('Access platform connection successful')
  } catch (error) {
    ElMessage.error('Connection failed')
  }
}

const openConfigDrawer = () => {
  configDrawerVisible.value = true
}

const saveConfig = async () => {
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    ElMessage.success('Configuration saved successfully')
    configDrawerVisible.value = false
  } catch (error) {
    ElMessage.error('Failed to save configuration')
  }
}

const openDoorControl = (door: any) => {
  selectedDoor.value = door
  doorControlForm.value = { action: door.locked ? 'unlock' : 'lock', duration: 30, reason: '' }
  doorControlVisible.value = true
}

const executeDoorControl = async () => {
  if (selectedDoor.value) {
    const actionText = doorControlForm.value.action === 'unlock' ? 'Unlocking' : 'Locking'
    ElMessage.info(`${actionText} door ${selectedDoor.value.name}...`)
    await new Promise(resolve => setTimeout(resolve, 1500))
    selectedDoor.value.locked = doorControlForm.value.action === 'lock'
    ElMessage.success(`Door ${selectedDoor.value.name} ${doorControlForm.value.action}ed successfully`)
    doorControlVisible.value = false
  }
}

const viewUserDetails = (user: any) => {
  selectedUser.value = user
  userDetailsVisible.value = true
}

const viewAccessLogs = () => {
  accessLogsVisible.value = true
}

const syncUsers = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    ElMessage.success('User synchronization completed successfully')
  } catch (error) {
    ElMessage.error('Sync failed')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const handleUserSizeChange = (val: number) => {
  userPagination.pageSize = val
  userPagination.page = 1
}

const handleUserPageChange = (val: number) => {
  userPagination.page = val
}

const getLockIcon = (locked: boolean) => {
  return locked ? Lock : Key
}
</script>

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
          <span class="loading-title">Loading Access Platform</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Access Control System Adapter</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="access-platform-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Access Platform Adapter</h2>
        <el-tag type="success" effect="dark">Connected</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">System Version: v4.1.0</el-tag>
      </div>
    </div>

    <!-- Stat Cards Row 1 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon door-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalDoors }}</div>
            <div class="stat-label">Total Doors</div>
            <div class="stat-trend">
              <el-progress :percentage="stats.onlineRate" :color="'#67C23A'" :stroke-width="6" />
              <span class="online-rate-text">{{ stats.onlineRate }}% Online</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon user-icon">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">Total Users</div>
            <div class="stat-sub-value">{{ stats.activeUsers }} Active</div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon access-icon">
            <el-icon><Key /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.todayAccess.toLocaleString() }}</div>
            <div class="stat-label">Today's Access</div>
            <div class="stat-trend">
              <span class="denied-text">{{ stats.todayDenied }} Denied</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon pending-icon">
            <el-icon><BellFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingRequests }}</div>
            <div class="stat-label">Pending Requests</div>
            <div class="stat-sub-value">{{ stats.expiredCards }} Expired Cards</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart Section -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Door Status Trend</span>
              <el-button text type="primary" @click="toggleChartPeriod">
                {{ currentChartPeriod === 'week' ? 'This Week' : 'This Month' }}
              </el-button>
            </div>
          </template>
          <div ref="doorChartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Access Events</span>
              <el-button text type="primary" @click="viewAccessLogs">View Logs</el-button>
            </div>
          </template>
          <div ref="accessChartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Doors Table -->
    <el-card shadow="never" class="door-table-card">
      <template #header>
        <div class="table-header">
          <span>Doors & Controllers</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search doors..."
                :prefix-icon="Search"
                style="width: 220px"
                clearable
            />
            <el-button type="primary" @click="syncDevices" :loading="loading">
              <el-icon><Refresh /></el-icon>
              Sync Doors
            </el-button>
            <el-button @click="openConfigDrawer">
              <el-icon><Setting /></el-icon>
              Platform Settings
            </el-button>
            <el-button @click="testConnection">
              <el-icon><Connection /></el-icon>
              Test Connection
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredDoors" stripe v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="Door ID" width="90" />
        <el-table-column prop="name" label="Door Name" min-width="150" />
        <el-table-column prop="location" label="Location" width="140" />
        <el-table-column prop="ip" label="IP Address" width="130" />
        <el-table-column prop="controllerId" label="Controller" width="100" />
        <el-table-column prop="doorType" label="Type" width="90" />
        <el-table-column label="Status" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'" size="small">
              {{ row.status === 'online' ? 'Online' : 'Offline' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Lock" width="80" align="center">
          <template #default="{ row }">
            <el-icon :color="row.locked ? '#F56C6C' : '#67C23A'" size="18">
              <component :is="getLockIcon(row.locked)" />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="todayAccess" label="Today Access" width="100" align="center" />
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDoorControl(row)">
              <el-icon><Key /></el-icon> Control
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Users Table -->
    <el-card shadow="never" class="user-table-card">
      <template #header>
        <div class="table-header">
          <span>Users & Credentials</span>
          <div class="table-actions">
            <el-input
                v-model="searchUserKeyword"
                placeholder="Search users..."
                :prefix-icon="Search"
                style="width: 220px"
                clearable
            />
            <el-button type="primary" @click="syncUsers" :loading="loading">
              <el-icon><Refresh /></el-icon>
              Sync Users
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredUsers" stripe style="width: 100%">
        <el-table-column prop="id" label="User ID" width="90" />
        <el-table-column prop="name" label="Name" min-width="150" />
        <el-table-column prop="department" label="Department" width="120" />
        <el-table-column prop="role" label="Role" width="100" />
        <el-table-column prop="cardId" label="Card ID" width="100" />
        <el-table-column prop="accessLevel" label="Access Level" width="100" />
        <el-table-column prop="lastAccess" label="Last Access" width="160" />
        <el-table-column label="Status" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewUserDetails(row)">
              <el-icon><User /></el-icon> Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="userPagination.page"
            v-model:page-size="userPagination.pageSize"
            :total="userPagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleUserSizeChange"
            @current-change="handleUserPageChange"
        />
      </div>
    </el-card>

    <!-- Door Control Dialog -->
    <el-dialog v-model="doorControlVisible" :title="`Door Control - ${selectedDoor?.name}`" width="450px">
      <el-form :model="doorControlForm" label-width="100px">
        <el-form-item label="Action">
          <el-radio-group v-model="doorControlForm.action">
            <el-radio value="unlock">Unlock Door</el-radio>
            <el-radio value="lock">Lock Door</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Duration (s)" v-if="doorControlForm.action === 'unlock'">
          <el-input-number v-model="doorControlForm.duration" :min="5" :max="300" />
        </el-form-item>
        <el-form-item label="Reason">
          <el-input v-model="doorControlForm.reason" type="textarea" rows="2" placeholder="Reason for action" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="doorControlVisible = false">Cancel</el-button>
        <el-button type="primary" @click="executeDoorControl">Execute</el-button>
      </template>
    </el-dialog>

    <!-- User Details Dialog -->
    <el-dialog v-model="userDetailsVisible" :title="`User Details - ${selectedUser?.name}`" width="550px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="User ID">{{ selectedUser?.id }}</el-descriptions-item>
        <el-descriptions-item label="Name">{{ selectedUser?.name }}</el-descriptions-item>
        <el-descriptions-item label="Email">{{ selectedUser?.email }}</el-descriptions-item>
        <el-descriptions-item label="Phone">{{ selectedUser?.phone }}</el-descriptions-item>
        <el-descriptions-item label="Department">{{ selectedUser?.department }}</el-descriptions-item>
        <el-descriptions-item label="Role">{{ selectedUser?.role }}</el-descriptions-item>
        <el-descriptions-item label="Card ID">{{ selectedUser?.cardId }}</el-descriptions-item>
        <el-descriptions-item label="Access Level">{{ selectedUser?.accessLevel }}</el-descriptions-item>
        <el-descriptions-item label="Last Access">{{ selectedUser?.lastAccess }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedUser?.status === 'Active' ? 'success' : 'info'" size="small">
            {{ selectedUser?.status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="userDetailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Access Logs Dialog -->
    <el-dialog v-model="accessLogsVisible" title="Recent Access Logs" width="800px">
      <el-table :data="accessLogs" stripe style="width: 100%" max-height="400">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="user" label="User" width="140" />
        <el-table-column prop="door" label="Door" width="140" />
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Granted' ? 'success' : row.status === 'Denied' ? 'danger' : 'warning'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="credentialType" label="Credential" width="120" />
        <el-table-column prop="reason" label="Reason" min-width="100">
          <template #default="{ row }">
            {{ row.reason || '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- Platform Configuration Drawer -->
    <el-drawer v-model="configDrawerVisible" title="Platform Configuration" direction="rtl" size="500px">
      <el-form :model="platformConfig" label-width="140px">
        <el-form-item label="Platform URL">
          <el-input v-model="platformConfig.host" placeholder="https://your-access-platform.com" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="platformConfig.apiKey" placeholder="Enter API key" />
        </el-form-item>
        <el-form-item label="Database URL">
          <el-input v-model="platformConfig.databaseUrl" placeholder="Database connection string" />
        </el-form-item>
        <el-form-item label="Sync Interval">
          <el-select v-model="platformConfig.syncInterval">
            <el-option label="5 minutes" :value="300" />
            <el-option label="15 minutes" :value="900" />
            <el-option label="30 minutes" :value="1800" />
            <el-option label="1 hour" :value="3600" />
          </el-select>
        </el-form-item>
        <el-form-item label="Lockdown Password">
          <el-input v-model="platformConfig.lockdownPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="Door Open Duration (s)">
          <el-input-number v-model="platformConfig.doorOpenDuration" :min="5" :max="60" />
        </el-form-item>
        <el-form-item label="Max Failed Attempts">
          <el-input-number v-model="platformConfig.maxFailedAttempts" :min="3" :max="10" />
        </el-form-item>
        <el-form-item label="Email Notifications">
          <el-switch v-model="platformConfig.emailNotifications" />
        </el-form-item>
        <el-form-item label="SMS Notifications">
          <el-switch v-model="platformConfig.smsNotifications" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">Save Configuration</el-button>
          <el-button @click="testConnection">Test Connection</el-button>
        </el-form-item>
      </el-form>
    </el-drawer>
  </div>
</template>

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

/* ==================== Main Content ==================== */
.access-platform-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.stat-cards {
  margin: 20px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.door-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.user-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.access-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.pending-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 12px;
  color: #67c23a;
  margin-top: 2px;
}

.stat-trend {
  margin-top: 8px;
}

.online-rate-text {
  font-size: 12px;
  color: #409eff;
  margin-left: 8px;
}

.denied-text {
  font-size: 12px;
  color: #f56c6c;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 380px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.door-table-card,
.user-table-card {
  margin-top: 20px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.chart {
  width: 100%;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 1200px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-actions {
    width: 100%;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>