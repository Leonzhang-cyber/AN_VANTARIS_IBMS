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
        <div class="loading-tip">Operations Logbook</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="operations-logbook">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Operations Logbook</h2>
        <p class="subtitle">Centralized record of all system events, maintenance activities, and operational notes</p>
      </div>
      <div class="header-actions">
        <div class="view-toggle">
          <el-button :type="viewMode === 'table' ? 'primary' : 'default'" @click="viewMode = 'table'">
            <el-icon><Grid /></el-icon> Table
          </el-button>
          <el-button :type="viewMode === 'timeline' ? 'primary' : 'default'" @click="viewMode = 'timeline'">
            <el-icon><List /></el-icon> Timeline
          </el-button>
        </div>
        <el-button type="success" @click="showAddDialog = true">
          <el-icon><Plus /></el-icon> Add Entry
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">📋</div>
        <div class="stat-info">
          <div class="stat-value">{{ logEntries.length }}</div>
          <div class="stat-label">Total Entries</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ getStats().warnings }}</div>
          <div class="stat-label">Warnings</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon alert">🚨</div>
        <div class="stat-info">
          <div class="stat-value">{{ getStats().alerts }}</div>
          <div class="stat-label">Alerts</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon maint">🔧</div>
        <div class="stat-info">
          <div class="stat-value">{{ getStats().maintenance }}</div>
          <div class="stat-label">Maintenance</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon resolved">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ getStats().resolved }}</div>
          <div class="stat-label">Resolved</div>
        </div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="search-bar">
      <el-input v-model="searchText" placeholder="Search by title, description or operator..." clearable :prefix-icon="Search" style="width: 300px" />
      <el-select v-model="filterCategory" placeholder="Category" clearable style="width: 150px">
        <el-option label="All" value="all" />
        <el-option label="System" value="System" />
        <el-option label="HVAC" value="HVAC" />
        <el-option label="Security" value="Security" />
        <el-option label="Electrical" value="Electrical" />
        <el-option label="Power" value="Power" />
        <el-option label="Network" value="Network" />
      </el-select>
      <el-select v-model="filterType" placeholder="Type" clearable style="width: 130px">
        <el-option label="All" value="all" />
        <el-option label="Info" value="info" />
        <el-option label="Warning" value="warning" />
        <el-option label="Alert" value="alert" />
        <el-option label="Maintenance" value="maintenance" />
      </el-select>
      <el-button @click="resetFilters">Reset</el-button>
    </div>

    <!-- Results Info -->
    <div class="results-info">
      <span>Showing {{ filteredEntries.length }} of {{ logEntries.length }} entries</span>
    </div>

    <!-- Table View -->
    <div v-if="viewMode === 'table'" class="table-container">
      <el-table :data="paginatedEntries" stripe style="width: 100%">
        <el-table-column prop="timestamp" label="Timestamp" width="170" />
        <el-table-column label="Type" width="100" align="center">
          <template #default="{ row }">
            <span :class="['type-badge', row.type]">{{ row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="Category" width="120" />
        <el-table-column prop="title" label="Title" min-width="200" />
        <el-table-column prop="description" label="Description" min-width="250" show-overflow-tooltip />
        <el-table-column prop="operator" label="Operator" width="130" />
        <el-table-column label="Status" width="100" align="center">
          <template #default="{ row }">
            <span :class="['status-badge', row.resolved ? 'resolved' : 'open']">
              {{ row.resolved ? 'Resolved' : 'Open' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button v-if="!row.resolved" type="success" link size="small" @click="resolveEntry(row)">Resolve</el-button>
            <el-button type="danger" link size="small" @click="deleteEntry(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredEntries.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Timeline View -->
    <div v-else class="timeline-container">
      <div v-for="group in groupedEntries" :key="group.date" class="timeline-group">
        <div class="timeline-date">{{ group.date }}</div>
        <div v-for="entry in group.entries" :key="entry.id" class="timeline-item" :class="entry.type">
          <div class="timeline-time">{{ entry.time }}</div>
          <div class="timeline-content">
            <div class="timeline-header">
              <div class="timeline-title">
                <span :class="['type-dot', entry.type]"></span>
                <strong>{{ entry.title }}</strong>
              </div>
              <div class="timeline-meta">
                <span>{{ entry.category }}</span>
                <span>by {{ entry.operator }}</span>
                <span v-if="entry.resolved" class="resolved-tag">Resolved</span>
                <span v-else class="open-tag">Open</span>
              </div>
            </div>
            <div class="timeline-desc">{{ entry.description }}</div>
            <div v-if="entry.action" class="timeline-action">Action: {{ entry.action }}</div>
            <div v-if="!entry.resolved" class="timeline-action-btn">
              <el-button size="small" type="success" @click="resolveEntry(entry)">Mark Resolved</el-button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="groupedEntries.length === 0" class="empty-state">
        <el-empty description="No log entries found" />
      </div>
    </div>

    <!-- Add Entry Dialog -->
    <el-dialog v-model="showAddDialog" title="Add Log Entry" width="500px">
      <el-form :model="newEntryForm" label-width="80px">
        <el-form-item label="Category">
          <el-select v-model="newEntryForm.category" style="width: 100%">
            <el-option label="System" value="System" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Security" value="Security" />
            <el-option label="Electrical" value="Electrical" />
            <el-option label="Power" value="Power" />
            <el-option label="Network" value="Network" />
            <el-option label="Energy" value="Energy" />
          </el-select>
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="newEntryForm.type" style="width: 100%">
            <el-option label="Info" value="info" />
            <el-option label="Warning" value="warning" />
            <el-option label="Alert" value="alert" />
            <el-option label="Maintenance" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="Title">
          <el-input v-model="newEntryForm.title" placeholder="Enter title" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newEntryForm.description" type="textarea" :rows="3" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">Cancel</el-button>
        <el-button type="primary" @click="addEntry">Add</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Search, Grid, List, Plus, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading operations logbook...',
  'Fetching recent activities...',
  'Organizing entries by date...',
  'Ready for review...'
]

// Helper function to get current timestamp
const getCurrentTimestamp = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

const getToday = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const getYesterday = () => {
  const now = new Date()
  now.setDate(now.getDate() - 1)
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Data with current timestamps
const logEntries = ref([
  { id: 1, timestamp: getCurrentTimestamp(), type: 'info', category: 'System', title: 'System Startup', description: 'Daily system startup completed successfully', operator: 'System', resolved: true },
  { id: 2, timestamp: getCurrentTimestamp(), type: 'warning', category: 'HVAC', title: 'Temperature Deviation', description: 'AHU-03 supply temperature exceeded setpoint by 2°C', operator: 'System', resolved: true, action: 'Adjusted setpoint' },
  { id: 3, timestamp: getCurrentTimestamp(), type: 'alert', category: 'Security', title: 'Unauthorized Access', description: 'Failed badge swipe at Server Room door', operator: 'Security', resolved: true, action: 'Investigated' },
  { id: 4, timestamp: getCurrentTimestamp(), type: 'maintenance', category: 'Electrical', title: 'UPS Battery Test', description: 'UPS-01 battery inspection and testing', operator: 'John Zhang', resolved: true },
  { id: 5, timestamp: getCurrentTimestamp(), type: 'info', category: 'Energy', title: 'Energy Report', description: 'Daily consumption: 1850 kWh - 5% below target', operator: 'System', resolved: true },
  { id: 6, timestamp: getCurrentTimestamp(), type: 'alert', category: 'Network', title: 'Communication Loss', description: 'BACnet communication lost between BMS and chiller', operator: 'System', resolved: false, action: 'Investigating' },
  { id: 7, timestamp: getCurrentTimestamp(), type: 'maintenance', category: 'Lighting', title: 'Firmware Update', description: 'Lighting controller firmware update', operator: 'Sarah Li', resolved: true },
  { id: 8, timestamp: getCurrentTimestamp(), type: 'info', category: 'Safety', title: 'Fire Alarm Test', description: 'Monthly fire alarm test - all zones passed', operator: 'Safety Team', resolved: true },
  { id: 9, timestamp: `${getYesterday()} ${new Date().getHours().toString().padStart(2, '0')}:${new Date().getMinutes().toString().padStart(2, '0')}:${new Date().getSeconds().toString().padStart(2, '0')}`, type: 'info', category: 'Shift', title: 'Shift Handover', description: 'Night shift report: No incidents', operator: 'Mike Wang', resolved: true },
  { id: 10, timestamp: `${getYesterday()} ${(new Date().getHours() - 5).toString().padStart(2, '0')}:${new Date().getMinutes().toString().padStart(2, '0')}:${new Date().getSeconds().toString().padStart(2, '0')}`, type: 'warning', category: 'HVAC', title: 'Chiller Efficiency Drop', description: 'Chiller COP decreased from 5.2 to 4.8', operator: 'System', resolved: true },
  { id: 11, timestamp: `${getYesterday()} ${(new Date().getHours() - 3).toString().padStart(2, '0')}:${new Date().getMinutes().toString().padStart(2, '0')}:${new Date().getSeconds().toString().padStart(2, '0')}`, type: 'warning', category: 'Power', title: 'Voltage Sag', description: 'Utility voltage sag detected - UPS compensated', operator: 'System', resolved: true },
  { id: 12, timestamp: `${getToday()} ${(new Date().getHours() - 1).toString().padStart(2, '0')}:${new Date().getMinutes().toString().padStart(2, '0')}:${new Date().getSeconds().toString().padStart(2, '0')}`, type: 'info', category: 'Shift', title: 'Evening Shift Start', description: 'Evening shift took over', operator: 'Emma Zhao', resolved: true }
])

// UI State
const viewMode = ref<'table' | 'timeline'>('table')
const showAddDialog = ref(false)
const searchText = ref('')
const filterCategory = ref('all')
const filterType = ref('all')
const currentPage = ref(1)
const pageSize = ref(10)

// New entry form
const newEntryForm = ref({
  category: 'System',
  type: 'info',
  title: '',
  description: ''
})

// Computed
const filteredEntries = computed(() => {
  let result = [...logEntries.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    result = result.filter(e =>
        e.title.toLowerCase().includes(keyword) ||
        e.description.toLowerCase().includes(keyword) ||
        e.operator.toLowerCase().includes(keyword)
    )
  }

  if (filterCategory.value !== 'all') {
    result = result.filter(e => e.category === filterCategory.value)
  }

  if (filterType.value !== 'all') {
    result = result.filter(e => e.type === filterType.value)
  }

  return result.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
})

const paginatedEntries = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredEntries.value.slice(start, start + pageSize.value)
})

const groupedEntries = computed(() => {
  const groups: { date: string; entries: any[]; time: string }[] = []
  const groupMap = new Map()

  filteredEntries.value.forEach(entry => {
    const date = entry.timestamp.split(' ')[0]
    const time = entry.timestamp.split(' ')[1]
    if (!groupMap.has(date)) {
      groupMap.set(date, [])
    }
    groupMap.get(date).push({ ...entry, time })
  })

  for (const [date, entries] of groupMap) {
    groups.push({ date, entries })
  }
  return groups
})

// Methods
const getStats = () => {
  const warnings = logEntries.value.filter(e => e.type === 'warning').length
  const alerts = logEntries.value.filter(e => e.type === 'alert').length
  const maintenance = logEntries.value.filter(e => e.type === 'maintenance').length
  const resolved = logEntries.value.filter(e => e.resolved).length
  return { warnings, alerts, maintenance, resolved }
}

const resetFilters = () => {
  searchText.value = ''
  filterCategory.value = 'all'
  filterType.value = 'all'
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const addEntry = () => {
  if (!newEntryForm.value.title.trim()) {
    ElMessage.warning('Please enter a title')
    return
  }

  const newEntry = {
    id: Date.now(),
    timestamp: getCurrentTimestamp(),
    type: newEntryForm.value.type,
    category: newEntryForm.value.category,
    title: newEntryForm.value.title,
    description: newEntryForm.value.description || 'No description',
    operator: 'Current User',
    resolved: false
  }

  logEntries.value.unshift(newEntry)
  ElMessage.success('Entry added successfully')

  newEntryForm.value = { category: 'System', type: 'info', title: '', description: '' }
  showAddDialog.value = false
}

const resolveEntry = (entry: any) => {
  ElMessageBox.confirm(`Mark "${entry.title}" as resolved?`, 'Confirm', {
    confirmButtonText: 'Resolve',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    entry.resolved = true
    ElMessage.success('Entry marked as resolved')
  }).catch(() => {})
}

const deleteEntry = (entry: any) => {
  ElMessageBox.confirm(`Delete "${entry.title}"?`, 'Confirm', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = logEntries.value.findIndex(e => e.id === entry.id)
    if (index !== -1) {
      logEntries.value.splice(index, 1)
      ElMessage.success('Entry deleted')
    }
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

// Loading animation
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
</script>

<style scoped>
/* Loading Screen */
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

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

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.operations-logbook {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.view-toggle {
  display: flex;
  gap: 0;
  border-radius: 8px;
  overflow: hidden;
}

.view-toggle .el-button {
  border-radius: 0;
  margin: 0;
}

/* Stats Cards */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
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

.stat-icon.total { background: rgba(64, 158, 255, 0.1); }
.stat-icon.warning { background: rgba(230, 162, 60, 0.1); }
.stat-icon.alert { background: rgba(245, 108, 108, 0.1); }
.stat-icon.maint { background: rgba(103, 194, 58, 0.1); }
.stat-icon.resolved { background: rgba(103, 194, 58, 0.1); }

.stat-info { flex: 1; }
.stat-value { font-size: 28px; font-weight: 700; color: #303133; }
.stat-label { font-size: 12px; color: #909399; margin-top: 4px; }

/* Search Bar */
.search-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.results-info {
  margin-bottom: 16px;
  font-size: 13px;
  color: #909399;
}

/* Table */
.table-container {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.type-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.info { background: #e6f7ff; color: #409eff; }
.type-badge.warning { background: #fff7e6; color: #e6a23c; }
.type-badge.alert { background: #ffefef; color: #f56c6c; }
.type-badge.maintenance { background: #e8f5e9; color: #67c23a; }

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.resolved { background: #e8f5e9; color: #67c23a; }
.status-badge.open { background: #ffefef; color: #f56c6c; }

.pagination {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Timeline */
.timeline-container {
  background: white;
  border-radius: 16px;
  padding: 20px;
}

.timeline-group {
  margin-bottom: 24px;
}

.timeline-date {
  font-size: 16px;
  font-weight: 600;
  padding: 8px 0;
  border-bottom: 2px solid #e4e7ed;
  margin-bottom: 16px;
}

.timeline-item {
  display: flex;
  gap: 20px;
  padding: 16px;
  margin-bottom: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid;
}

.timeline-item.info { border-left-color: #409eff; }
.timeline-item.warning { border-left-color: #e6a23c; }
.timeline-item.alert { border-left-color: #f56c6c; }
.timeline-item.maintenance { border-left-color: #67c23a; }

.timeline-time {
  font-family: monospace;
  font-size: 13px;
  color: #909399;
  min-width: 80px;
}

.timeline-content { flex: 1; }

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 8px;
}

.timeline-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.type-dot.info { background: #409eff; }
.type-dot.warning { background: #e6a23c; }
.type-dot.alert { background: #f56c6c; }
.type-dot.maintenance { background: #67c23a; }

.timeline-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.timeline-desc { font-size: 13px; color: #606266; margin-bottom: 8px; }
.timeline-action { font-size: 12px; color: #409eff; margin-top: 8px; padding-top: 8px; border-top: 1px solid #e4e7ed; }
.timeline-action-btn { margin-top: 12px; }

.resolved-tag { color: #67c23a; }
.open-tag { color: #f56c6c; }

.empty-state {
  padding: 60px;
  text-align: center;
}

/* Responsive */
@media (max-width: 768px) {
  .operations-logbook { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .timeline-item { flex-direction: column; }
  .timeline-header { flex-direction: column; align-items: flex-start; }
}
</style>