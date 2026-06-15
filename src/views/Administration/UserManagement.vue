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
          <span class="loading-title">Loading User Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Manage Users, Roles, and Permissions</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="user-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">User Management</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Administration</el-breadcrumb-item>
          <el-breadcrumb-item>User Management</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="createUser">
          <el-icon><Plus /></el-icon>
          Create User
        </el-button>
        <el-button type="success" plain @click="importUsers">
          <el-icon><Upload /></el-icon>
          Import Users
        </el-button>
        <el-button type="info" plain @click="exportUsers">
          <el-icon><Download /></el-icon>
          Export Users
        </el-button>
      </div>
    </div>

    <!-- User Statistics -->
    <div class="stats-section">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><User /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalUsers }}</div>
            <div class="stat-label">Total Users</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><CircleCheck /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ activeUsers }}</div>
            <div class="stat-label">Active Users</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Lock /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ lockedUsers }}</div>
            <div class="stat-label">Locked Users</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Clock /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ pendingApprovals }}</div>
            <div class="stat-label">Pending Approvals</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Filters and Search -->
    <el-card class="filters-card" shadow="hover">
      <div class="filters-section">
        <el-input v-model="searchKeyword" placeholder="Search by name, email, or role..." size="large" class="search-input" clearable>
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="roleFilter" placeholder="Role" size="large" style="width: 160px" clearable>
          <el-option label="All Roles" value="" />
          <el-option label="Admin" value="admin" />
          <el-option label="Operator" value="operator" />
          <el-option label="Viewer" value="viewer" />
          <el-option label="Engineer" value="engineer" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" size="large" style="width: 140px" clearable>
          <el-option label="All Status" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
          <el-option label="Locked" value="locked" />
          <el-option label="Pending" value="pending" />
        </el-select>
        <el-button type="primary" size="large" @click="applyFilters">
          <el-icon><Search /></el-icon>
          Apply Filters
        </el-button>
        <el-button size="large" @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          Reset
        </el-button>
      </div>
    </el-card>

    <!-- Users Table -->
    <div class="users-section">
      <el-card class="users-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><List /></el-icon> User List</span>
            <div class="table-actions">
              <el-button size="small" text @click="refreshUsers">
                <el-icon><Refresh /></el-icon> Refresh
              </el-button>
              <el-button size="small" text @click="customizeColumns">
                <el-icon><Setting /></el-icon> Columns
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="filteredUsers" stripe style="width: 100%" v-loading="tableLoading">
          <el-table-column prop="avatar" label="" width="50">
            <template #default="{ row }">
              <el-avatar :size="32" :icon="User" />
            </template>
          </el-table-column>
          <el-table-column prop="name" label="Name" min-width="150" sortable />
          <el-table-column prop="email" label="Email" min-width="200" sortable />
          <el-table-column prop="role" label="Role" width="120">
            <template #default="{ row }">
              <el-tag :type="getRoleTagType(row.role)" size="small">{{ row.role }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="department" label="Department" width="140" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastLogin" label="Last Login" width="160" sortable />
          <el-table-column label="MFA" width="70" align="center">
            <template #default="{ row }">
              <el-icon v-if="row.mfaEnabled" color="#10b981"><CircleCheck /></el-icon>
              <el-icon v-else color="#cbd5e1"><Warning /></el-icon>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="180" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="editUser(row)">
                <el-icon><Edit /></el-icon>
              </el-button>
              <el-button size="small" text type="warning" @click="resetUserPassword(row)">
                <el-icon><Key /></el-icon>
              </el-button>
              <el-dropdown trigger="click" @command="(cmd) => handleUserAction(cmd, row)">
                <el-button size="small" text>
                  <el-icon><More /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="enable">Enable</el-dropdown-item>
                    <el-dropdown-item command="disable">Disable</el-dropdown-item>
                    <el-dropdown-item command="lock">Lock</el-dropdown-item>
                    <el-dropdown-item command="unlock">Unlock</el-dropdown-item>
                    <el-dropdown-item divided command="delete">Delete</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <div class="pagination-section">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="filteredUsers.length"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- User Groups & Roles Summary -->
    <div class="groups-section">
      <el-card class="roles-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Key /></el-icon> Roles & Permissions Summary</span>
            <el-button text type="primary" @click="manageRoles">Manage Roles</el-button>
          </div>
        </template>
        <div class="roles-grid">
          <div v-for="role in roleSummary" :key="role.name" class="role-item">
            <div class="role-header">
              <span class="role-name">{{ role.name }}</span>
              <el-tag :type="getRoleTagType(role.name)" size="small">{{ role.userCount }} users</el-tag>
            </div>
            <div class="role-permissions">
              <el-tag v-for="perm in role.permissions.slice(0, 5)" :key="perm" size="small" type="info">{{ perm }}</el-tag>
              <el-tag v-if="role.permissions.length > 5" size="small" type="info">+{{ role.permissions.length - 5 }} more</el-tag>
            </div>
          </div>
        </div>
      </el-card>

      <!-- Recent User Activities -->
      <el-card class="activities-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Clock /></el-icon> Recent User Activities</span>
            <el-button text type="primary" @click="viewAllActivities">View All</el-button>
          </div>
        </template>
        <div class="activities-list">
          <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon" :style="{ backgroundColor: getActivityColor(activity.type) }">
              <el-icon><component :is="getActivityIcon(activity.type)" /></el-icon>
            </div>
            <div class="activity-info">
              <div class="activity-user">{{ activity.user }}</div>
              <div class="activity-action">{{ activity.action }}</div>
            </div>
            <div class="activity-time">{{ activity.time }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Pending Approvals -->
    <div class="pending-section">
      <el-card class="pending-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Message /></el-icon> Pending Approvals</span>
            <el-button text type="primary" @click="viewAllPending">View All</el-button>
          </div>
        </template>
        <el-table :data="pendingApprovalsList" stripe style="width: 100%">
          <el-table-column prop="requestor" label="Requestor" width="180" />
          <el-table-column prop="type" label="Type" width="120">
            <template #default="{ row }">
              <el-tag size="small">{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="details" label="Details" min-width="250" />
          <el-table-column prop="requestedAt" label="Requested" width="160" />
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button size="small" type="success" @click="approveRequest(row)">Approve</el-button>
              <el-button size="small" type="danger" @click="rejectRequest(row)">Reject</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="inviteUsers">
          <el-icon><Message /></el-icon>
          Invite Users
        </el-button>
        <el-button type="success" plain @click="syncDirectory">
          <el-icon><Connection /></el-icon>
          Sync Directory
        </el-button>
        <el-button type="warning" plain @click="bulkUpdate">
          <el-icon><Edit /></el-icon>
          Bulk Update
        </el-button>
        <el-button type="info" plain @click="auditLogs">
          <el-icon><List /></el-icon>
          Audit Logs
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Setting, User, Clock, Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic, Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service, Search, Edit, Plus, VideoPlay,
  VideoPause, Operation, Headset, Monitor, Cpu, Connection, Lock, Key, Medal,
  Flag, DataAnalysis, EditPen, Tickets, Filter, SuccessFilled, List, Grid, Calendar, Bell, History, More
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading User Management...')

const loadingMessages = [
  'Loading User Management...',
  'Fetching user data...',
  'Loading roles and permissions...',
  'User management ready!'
]

// Statistics
const totalUsers = ref(1248)
const activeUsers = ref(1124)
const lockedUsers = ref(18)
const pendingApprovals = ref(7)

// Filters
const searchKeyword = ref('')
const roleFilter = ref('')
const statusFilter = ref('')
const tableLoading = ref(false)

// Pagination
const currentPage = ref(1)
const pageSize = ref(10)

// Users data
const users = ref([
  { id: 1, name: 'John Anderson', email: 'john.anderson@ibms.com', role: 'admin', department: 'IT Security', status: 'active', lastLogin: '2024-01-15 09:30:22', mfaEnabled: true },
  { id: 2, name: 'Sarah Chen', email: 'sarah.chen@ibms.com', role: 'operator', department: 'Facility Operations', status: 'active', lastLogin: '2024-01-15 08:45:12', mfaEnabled: true },
  { id: 3, name: 'Mike Johnson', email: 'mike.johnson@ibms.com', role: 'engineer', department: 'Engineering', status: 'active', lastLogin: '2024-01-14 16:20:45', mfaEnabled: false },
  { id: 4, name: 'Emma Wilson', email: 'emma.wilson@ibms.com', role: 'viewer', department: 'Compliance', status: 'active', lastLogin: '2024-01-14 11:15:33', mfaEnabled: true },
  { id: 5, name: 'David Kim', email: 'david.kim@ibms.com', role: 'operator', department: 'Energy Management', status: 'inactive', lastLogin: '2024-01-10 14:22:18', mfaEnabled: false },
  { id: 6, name: 'Lisa Martinez', email: 'lisa.martinez@ibms.com', role: 'engineer', department: 'Data Center', status: 'active', lastLogin: '2024-01-15 10:05:44', mfaEnabled: true },
  { id: 7, name: 'James Brown', email: 'james.brown@ibms.com', role: 'admin', department: 'IT Operations', status: 'locked', lastLogin: '2024-01-12 08:30:21', mfaEnabled: true },
  { id: 8, name: 'Patricia Lee', email: 'patricia.lee@ibms.com', role: 'viewer', department: 'ESG Reporting', status: 'pending', lastLogin: 'Never', mfaEnabled: false },
  { id: 9, name: 'Robert Taylor', email: 'robert.taylor@ibms.com', role: 'operator', department: 'Security', status: 'active', lastLogin: '2024-01-14 13:45:56', mfaEnabled: true },
  { id: 10, name: 'Jennifer White', email: 'jennifer.white@ibms.com', role: 'engineer', department: 'HVAC Systems', status: 'active', lastLogin: '2024-01-15 09:15:33', mfaEnabled: false }
])

// Role summary
const roleSummary = ref([
  { name: 'admin', userCount: 12, permissions: ['user.manage', 'role.manage', 'system.config', 'audit.view', 'reports.generate', 'api.manage'] },
  { name: 'operator', userCount: 345, permissions: ['device.control', 'alarm.acknowledge', 'workorder.create', 'dashboard.view', 'reports.view'] },
  { name: 'engineer', userCount: 87, permissions: ['device.configure', 'point.write', 'system.diagnose', 'logs.view', 'firmware.update'] },
  { name: 'viewer', userCount: 804, permissions: ['dashboard.view', 'reports.view', 'alarm.view', 'device.view'] }
])

// Recent activities
const recentActivities = ref([
  { id: 1, user: 'John Anderson', action: 'Created new user "Robert Taylor"', type: 'create', time: '2 min ago' },
  { id: 2, user: 'Sarah Chen', action: 'Updated role permissions for Engineer', type: 'update', time: '15 min ago' },
  { id: 3, user: 'Mike Johnson', action: 'Locked user account "james.brown"', type: 'lock', time: '1 hour ago' },
  { id: 4, user: 'Emma Wilson', action: 'Exported user list (1248 users)', type: 'export', time: '2 hours ago' },
  { id: 5, user: 'David Kim', action: 'Changed password', type: 'security', time: '3 hours ago' }
])

// Pending approvals
const pendingApprovalsList = ref([
  { id: 1, requestor: 'John Anderson', type: 'Role Change', details: 'Request to change role from Operator to Engineer', requestedAt: '2024-01-15 10:30:22' },
  { id: 2, requestor: 'Sarah Chen', type: 'User Creation', details: 'New user: "Thomas Lee" (Engineer role)', requestedAt: '2024-01-15 09:15:44' },
  { id: 3, requestor: 'Mike Johnson', type: 'Permission Request', details: 'Requesting API access for automation scripts', requestedAt: '2024-01-14 16:45:12' }
])

// Filtered users
const filteredUsers = computed(() => {
  let result = users.value
  if (searchKeyword.value) {
    const search = searchKeyword.value.toLowerCase()
    result = result.filter(u => u.name.toLowerCase().includes(search) || u.email.toLowerCase().includes(search))
  }
  if (roleFilter.value) {
    result = result.filter(u => u.role === roleFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter(u => u.status === statusFilter.value)
  }

  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return result.slice(start, end)
})

// Helper functions
const getRoleTagType = (role: string) => {
  switch (role) {
    case 'admin': return 'danger'
    case 'operator': return 'primary'
    case 'engineer': return 'warning'
    case 'viewer': return 'info'
    default: return ''
  }
}

const getStatusTagType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'info'
    case 'locked': return 'danger'
    case 'pending': return 'warning'
    default: return ''
  }
}

const getActivityColor = (type: string) => {
  switch (type) {
    case 'create': return '#10b981'
    case 'update': return '#3b82f6'
    case 'lock': return '#ef4444'
    case 'export': return '#8b5cf6'
    case 'security': return '#f59e0b'
    default: return '#64748b'
  }
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'create': return 'Plus'
    case 'update': return 'Edit'
    case 'lock': return 'Lock'
    case 'export': return 'Download'
    case 'security': return 'Key'
    default: return 'User'
  }
}

// Event handlers
const createUser = () => {
  ElMessageBox.prompt('Enter user email', 'Create User', {
    confirmButtonText: 'Create',
    cancelButtonText: 'Cancel',
    inputPlaceholder: 'user@example.com'
  }).then(({ value }) => {
    if (value) {
      ElMessage.success(`User invitation sent to ${value}`)
    }
  }).catch(() => {})
}

const importUsers = () => {
  ElMessage.info('Import users dialog opened')
}

const exportUsers = () => {
  ElMessage.info('Exporting user list...')
  setTimeout(() => {
    ElMessage.success('Users exported successfully')
  }, 1000)
}

const applyFilters = () => {
  currentPage.value = 1
  ElMessage.success('Filters applied')
}

const resetFilters = () => {
  searchKeyword.value = ''
  roleFilter.value = ''
  statusFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const refreshUsers = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('User list refreshed')
  }, 800)
}

const customizeColumns = () => {
  ElMessage.info('Customize columns dialog opened')
}

const editUser = (user: any) => {
  ElMessage.info(`Editing user: ${user.name}`)
}

const resetUserPassword = (user: any) => {
  ElMessageBox.confirm(`Reset password for ${user.name}?`, 'Confirm Reset', {
    confirmButtonText: 'Reset',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    ElMessage.success(`Password reset email sent to ${user.email}`)
  }).catch(() => {})
}

const handleUserAction = (cmd: string, user: any) => {
  const actions: Record<string, string> = {
    enable: `User ${user.name} enabled`,
    disable: `User ${user.name} disabled`,
    lock: `User ${user.name} locked`,
    unlock: `User ${user.name} unlocked`,
    delete: `User ${user.name} deleted`
  }

  if (cmd === 'delete') {
    ElMessageBox.confirm(`Delete user ${user.name}? This action cannot be undone.`, 'Confirm Delete', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'danger'
    }).then(() => {
      users.value = users.value.filter(u => u.id !== user.id)
      ElMessage.success(`User ${user.name} deleted`)
    }).catch(() => {})
  } else {
    ElMessage.success(actions[cmd])
  }
}

const handleSizeChange = (val: number) => {
  pageSize.value = val
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const manageRoles = () => {
  ElMessage.info('Managing roles and permissions')
}

const viewAllActivities = () => {
  ElMessage.info('Viewing all activities')
}

const viewAllPending = () => {
  ElMessage.info('Viewing all pending approvals')
}

const approveRequest = (request: any) => {
  ElMessageBox.confirm(`Approve ${request.type} request from ${request.requestor}?`, 'Confirm Approval', {
    confirmButtonText: 'Approve',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    pendingApprovalsList.value = pendingApprovalsList.value.filter(r => r.id !== request.id)
    ElMessage.success(`Request approved`)
  }).catch(() => {})
}

const rejectRequest = (request: any) => {
  ElMessageBox.confirm(`Reject ${request.type} request from ${request.requestor}?`, 'Confirm Rejection', {
    confirmButtonText: 'Reject',
    cancelButtonText: 'Cancel',
    type: 'danger'
  }).then(() => {
    pendingApprovalsList.value = pendingApprovalsList.value.filter(r => r.id !== request.id)
    ElMessage.warning(`Request rejected`)
  }).catch(() => {})
}

const inviteUsers = () => {
  ElMessage.info('Invite users dialog opened')
}

const syncDirectory = () => {
  ElMessage.info('Syncing directory...')
  setTimeout(() => {
    ElMessage.success('Directory sync completed')
  }, 2000)
}

const bulkUpdate = () => {
  ElMessage.info('Bulk update dialog opened')
}

const auditLogs = () => {
  ElMessage.info('Viewing audit logs')
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
  }, 2500)
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
  font-size: 24px;
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
.user-management-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  background: white;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

/* Filters Section */
.filters-card {
  margin-bottom: 24px;
  border-radius: 12px;
  background: white;
}

.filters-section {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
}

/* Users Section */
.users-section {
  margin-bottom: 24px;
}

.users-card {
  border-radius: 12px;
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.pagination-section {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* Groups Section */
.groups-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.roles-card,
.activities-card {
  border-radius: 12px;
  background: white;
}

.roles-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.role-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.role-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.role-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  text-transform: capitalize;
}

.role-permissions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.activities-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 8px;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.activity-info {
  flex: 1;
}

.activity-user {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.activity-action {
  font-size: 11px;
  color: #64748b;
}

.activity-time {
  font-size: 11px;
  color: #94a3b8;
}

/* Pending Section */
.pending-section {
  margin-bottom: 24px;
}

.pending-card {
  border-radius: 12px;
  background: white;
}

/* Footer Actions */
.footer-actions {
  margin-top: 8px;
}

.action-group {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .groups-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .filters-section {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>