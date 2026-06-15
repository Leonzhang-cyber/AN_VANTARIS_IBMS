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
          <span class="loading-title">Loading Role Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Manage Roles, Permissions, and Access Control</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="role-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Role Management</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Administration</el-breadcrumb-item>
          <el-breadcrumb-item>Role Management</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="createRole">
          <el-icon><Plus /></el-icon>
          Create Role
        </el-button>
        <el-button type="success" plain @click="exportRoles">
          <el-icon><Download /></el-icon>
          Export Roles
        </el-button>
        <el-button type="info" plain @click="importRoles">
          <el-icon><Upload /></el-icon>
          Import Roles
        </el-button>
      </div>
    </div>

    <!-- Role Statistics -->
    <div class="stats-section">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Key /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalRoles }}</div>
            <div class="stat-label">Total Roles</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><User /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ assignedUsers }}</div>
            <div class="stat-label">Assigned Users</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Setting /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalPermissions }}</div>
            <div class="stat-label">Total Permissions</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Clock /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ lastUpdated }}</div>
            <div class="stat-label">Last Updated</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Filters -->
    <el-card class="filters-card" shadow="hover">
      <div class="filters-section">
        <el-input v-model="searchKeyword" placeholder="Search roles..." size="large" class="search-input" clearable>
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="statusFilter" placeholder="Status" size="large" style="width: 140px" clearable>
          <el-option label="All Status" value="" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
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

    <!-- Roles Table -->
    <div class="roles-section">
      <el-card class="roles-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><List /></el-icon> Roles & Permissions</span>
            <div class="table-actions">
              <el-button size="small" text @click="refreshRoles">
                <el-icon><Refresh /></el-icon> Refresh
              </el-button>
            </div>
          </div>
        </template>
        <el-table :data="filteredRoles" stripe style="width: 100%" row-key="id" v-loading="tableLoading">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="expand-content">
                <div class="permissions-section-expand">
                  <div class="expand-title">Permissions</div>
                  <div class="permissions-grid-expand">
                    <div v-for="(perms, category) in row.permissions" :key="category" class="permission-category-expand">
                      <div class="category-title-expand">{{ category }}</div>
                      <div class="permission-list-expand">
                        <el-tag v-for="perm in perms" :key="perm" size="small" type="info">{{ perm }}</el-tag>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="users-section-expand">
                  <div class="expand-title">Assigned Users ({{ row.userCount }})</div>
                  <div class="user-list-expand">
                    <el-tag v-for="user in row.assignedUsers" :key="user.id" size="small" closable @close="removeUserFromRole(row, user)">
                      {{ user.name }}
                    </el-tag>
                    <el-button size="small" text type="primary" @click="addUserToRole(row)">
                      <el-icon><Plus /></el-icon> Add User
                    </el-button>
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="Role Name" width="160">
            <template #default="{ row }">
              <span class="role-name">{{ row.name }}</span>
              <el-tag v-if="row.isSystem" type="danger" size="small">System</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="Description" min-width="200" />
          <el-table-column prop="userCount" label="Users" width="80" align="center" sortable />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="Created" width="120" />
          <el-table-column label="Actions" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="editRole(row)">
                <el-icon><Edit /></el-icon> Edit
              </el-button>
              <el-button size="small" text type="primary" @click="cloneRole(row)">
                <el-icon><CopyDocument /></el-icon> Clone
              </el-button>
              <el-dropdown trigger="click" @command="(cmd) => handleRoleAction(cmd, row)">
                <el-button size="small" text>
                  <el-icon><More /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="activate" v-if="row.status !== 'active'">Activate</el-dropdown-item>
                    <el-dropdown-item command="deactivate" v-if="row.status === 'active'">Deactivate</el-dropdown-item>
                    <el-dropdown-item divided command="delete" :disabled="row.isSystem">Delete</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Permission Categories Summary -->
    <div class="permissions-summary-section">
      <el-card class="permissions-summary-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Grid /></el-icon> Permission Categories</span>
            <el-button text type="primary" @click="managePermissionTemplates">Manage Templates</el-button>
          </div>
        </template>
        <div class="categories-grid">
          <div v-for="category in permissionCategories" :key="category.name" class="category-card">
            <div class="category-header">
              <div class="category-icon" :style="{ backgroundColor: category.color }">
                <el-icon :size="20"><component :is="category.icon" /></el-icon>
              </div>
              <span class="category-name">{{ category.name }}</span>
              <span class="category-count">{{ category.permissionCount }} permissions</span>
            </div>
            <div class="category-permissions">
              <el-tag v-for="perm in category.permissions.slice(0, 4)" :key="perm" size="small" type="info">{{ perm }}</el-tag>
              <el-tag v-if="category.permissions.length > 4" size="small" type="info">+{{ category.permissions.length - 4 }} more</el-tag>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Role Assignment History -->
    <div class="history-section">
      <el-card class="history-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Clock /></el-icon> Role Assignment History</span>
            <el-button text type="primary" @click="viewAllHistory">View All</el-button>
          </div>
        </template>
        <el-table :data="assignmentHistory" stripe style="width: 100%">
          <el-table-column prop="timestamp" label="Time" width="160" />
          <el-table-column prop="user" label="User" width="160" />
          <el-table-column prop="action" label="Action" width="120">
            <template #default="{ row }">
              <el-tag :type="row.action === 'assigned' ? 'success' : 'danger'" size="small">{{ row.action }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="role" label="Role" width="140" />
          <el-table-column prop="changedBy" label="Changed By" width="160" />
          <el-table-column prop="reason" label="Reason" min-width="200" />
        </el-table>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="bulkAssignRoles">
          <el-icon><Edit /></el-icon>
          Bulk Assign Roles
        </el-button>
        <el-button type="success" plain @click="generateRoleReport">
          <el-icon><Document /></el-icon>
          Generate Report
        </el-button>
        <el-button type="warning" plain @click="roleComparison">
          <el-icon><DataAnalysis /></el-icon>
          Role Comparison
        </el-button>
        <el-button type="info" plain @click="viewAuditLog">
          <el-icon><List /></el-icon>
          Audit Log
        </el-button>
      </div>
    </div>

    <!-- Create/Edit Role Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form :model="currentRole" :rules="roleRules" ref="roleFormRef" label-width="100px">
        <el-form-item label="Role Name" prop="name">
          <el-input v-model="currentRole.name" placeholder="Enter role name" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="currentRole.description" type="textarea" :rows="2" placeholder="Enter role description" />
        </el-form-item>
        <el-form-item label="Status">
          <el-radio-group v-model="currentRole.status">
            <el-radio value="active">Active</el-radio>
            <el-radio value="inactive">Inactive</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Permissions">
          <el-tabs class="permission-tabs">
            <el-tab-pane v-for="(perms, category) in allPermissions" :key="category" :label="category">
              <el-checkbox-group v-model="currentRole.selectedPermissions[category]">
                <div class="permission-checkbox-group">
                  <el-checkbox v-for="perm in perms" :key="perm" :label="perm">{{ perm }}</el-checkbox>
                </div>
              </el-checkbox-group>
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRole">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Refresh, Setting, User, Clock, Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic, Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service, Search, Edit, Plus, VideoPlay,
  VideoPause, Operation, Headset, Monitor, Cpu, Connection, Lock, Key, Medal,
  Flag, DataAnalysis, EditPen, Tickets, Filter, SuccessFilled, List, Grid, Calendar, Bell, More
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading Role Management...')

const loadingMessages = [
  'Loading Role Management...',
  'Fetching roles and permissions...',
  'Loading assignment data...',
  'Role management ready!'
]

// Statistics
const totalRoles = ref(12)
const assignedUsers = ref(1248)
const totalPermissions = ref(86)
const lastUpdated = ref('2024-01-15')

// Filters
const searchKeyword = ref('')
const statusFilter = ref('')
const tableLoading = ref(false)

// Dialog
const dialogVisible = ref(false)
const dialogTitle = ref('Create Role')
const roleFormRef = ref<FormInstance>()

// Current role for editing
const currentRole = ref({
  id: null,
  name: '',
  description: '',
  status: 'active',
  isSystem: false,
  selectedPermissions: {} as Record<string, string[]>
})

// Role rules
const roleRules: FormRules = {
  name: [{ required: true, message: 'Please enter role name', trigger: 'blur' }],
  description: [{ required: true, message: 'Please enter role description', trigger: 'blur' }]
}

// All permissions by category
const allPermissions = ref({
  'User Management': ['user.view', 'user.create', 'user.edit', 'user.delete', 'user.activate', 'user.deactivate', 'user.resetPassword', 'user.export'],
  'Role Management': ['role.view', 'role.create', 'role.edit', 'role.delete', 'role.assign', 'permission.view', 'permission.grant'],
  'Device Management': ['device.view', 'device.control', 'device.configure', 'device.firmware', 'device.export'],
  'System Settings': ['system.config', 'system.backup', 'system.restore', 'system.logs', 'system.monitor'],
  'Security': ['security.policies', 'security.audit', 'security.mfa', 'security.encryption', 'security.incident'],
  'Reports': ['report.view', 'report.create', 'report.export', 'report.schedule', 'report.share']
})

// Roles data
const roles = ref([
  {
    id: 1,
    name: 'admin',
    description: 'Full system access with all administrative privileges',
    status: 'active',
    userCount: 12,
    isSystem: true,
    createdAt: '2023-01-01',
    permissions: {
      'User Management': ['user.view', 'user.create', 'user.edit', 'user.delete', 'user.activate', 'user.deactivate', 'user.resetPassword', 'user.export'],
      'Role Management': ['role.view', 'role.create', 'role.edit', 'role.delete', 'role.assign', 'permission.view', 'permission.grant'],
      'Device Management': ['device.view', 'device.control', 'device.configure', 'device.firmware', 'device.export'],
      'System Settings': ['system.config', 'system.backup', 'system.restore', 'system.logs', 'system.monitor'],
      'Security': ['security.policies', 'security.audit', 'security.mfa', 'security.encryption', 'security.incident'],
      'Reports': ['report.view', 'report.create', 'report.export', 'report.schedule', 'report.share']
    },
    assignedUsers: [
      { id: 1, name: 'John Anderson' },
      { id: 2, name: 'Sarah Chen' },
      { id: 3, name: 'Mike Johnson' }
    ]
  },
  {
    id: 2,
    name: 'operator',
    description: 'Daily operations including device control and alarm management',
    status: 'active',
    userCount: 345,
    isSystem: true,
    createdAt: '2023-01-01',
    permissions: {
      'User Management': ['user.view'],
      'Role Management': [],
      'Device Management': ['device.view', 'device.control'],
      'System Settings': [],
      'Security': ['security.incident'],
      'Reports': ['report.view', 'report.export']
    },
    assignedUsers: [
      { id: 4, name: 'Robert Taylor' },
      { id: 5, name: 'Lisa Martinez' }
    ]
  },
  {
    id: 3,
    name: 'engineer',
    description: 'Technical configuration and troubleshooting',
    status: 'active',
    userCount: 87,
    isSystem: true,
    createdAt: '2023-01-01',
    permissions: {
      'User Management': ['user.view'],
      'Role Management': [],
      'Device Management': ['device.view', 'device.control', 'device.configure', 'device.firmware'],
      'System Settings': ['system.logs', 'system.monitor'],
      'Security': [],
      'Reports': ['report.view', 'report.export']
    },
    assignedUsers: [
      { id: 6, name: 'David Kim' },
      { id: 7, name: 'Jennifer White' }
    ]
  },
  {
    id: 4,
    name: 'viewer',
    description: 'Read-only access to dashboards and reports',
    status: 'active',
    userCount: 804,
    isSystem: true,
    createdAt: '2023-01-01',
    permissions: {
      'User Management': [],
      'Role Management': [],
      'Device Management': ['device.view'],
      'System Settings': [],
      'Security': [],
      'Reports': ['report.view']
    },
    assignedUsers: [
      { id: 8, name: 'Emma Wilson' },
      { id: 9, name: 'Patricia Lee' }
    ]
  },
  {
    id: 5,
    name: 'auditor',
    description: 'Access to audit logs and compliance reports',
    status: 'active',
    userCount: 23,
    isSystem: false,
    createdAt: '2023-06-15',
    permissions: {
      'User Management': ['user.view'],
      'Role Management': ['role.view'],
      'Device Management': [],
      'System Settings': ['system.logs'],
      'Security': ['security.audit'],
      'Reports': ['report.view', 'report.export']
    },
    assignedUsers: [
      { id: 10, name: 'James Wilson' },
      { id: 11, name: 'Maria Garcia' }
    ]
  },
  {
    id: 6,
    name: 'maintenance',
    description: 'Equipment maintenance and work order management',
    status: 'inactive',
    userCount: 0,
    isSystem: false,
    createdAt: '2023-09-20',
    permissions: {
      'User Management': [],
      'Role Management': [],
      'Device Management': ['device.view', 'device.control'],
      'System Settings': [],
      'Security': [],
      'Reports': ['report.view']
    },
    assignedUsers: []
  }
])

// Permission categories for summary
const permissionCategories = ref([
  { name: 'User Management', icon: 'User', color: '#3b82f6', permissionCount: 8, permissions: ['user.view', 'user.create', 'user.edit', 'user.delete', 'user.activate'] },
  { name: 'Role Management', icon: 'Key', color: '#8b5cf6', permissionCount: 7, permissions: ['role.view', 'role.create', 'role.edit', 'role.delete', 'role.assign'] },
  { name: 'Device Management', icon: 'Monitor', color: '#10b981', permissionCount: 5, permissions: ['device.view', 'device.control', 'device.configure', 'device.firmware'] },
  { name: 'System Settings', icon: 'Setting', color: '#f59e0b', permissionCount: 5, permissions: ['system.config', 'system.backup', 'system.restore', 'system.logs'] },
  { name: 'Security', icon: 'Lock', color: '#ef4444', permissionCount: 5, permissions: ['security.policies', 'security.audit', 'security.mfa', 'security.encryption'] },
  { name: 'Reports', icon: 'Document', color: '#06b6d4', permissionCount: 5, permissions: ['report.view', 'report.create', 'report.export', 'report.schedule'] }
])

// Assignment history
const assignmentHistory = ref([
  { id: 1, timestamp: '2024-01-15 09:45:32', user: 'John Anderson', action: 'assigned', role: 'operator', changedBy: 'Admin User', reason: 'New hire onboarding' },
  { id: 2, timestamp: '2024-01-14 16:20:18', user: 'Sarah Chen', action: 'removed', role: 'viewer', changedBy: 'Security Team', reason: 'Role updated to operator' },
  { id: 3, timestamp: '2024-01-14 11:05:44', user: 'Mike Johnson', action: 'assigned', role: 'engineer', changedBy: 'HR System', reason: 'Role change approval' },
  { id: 4, timestamp: '2024-01-13 14:30:22', user: 'Emma Wilson', action: 'assigned', role: 'auditor', changedBy: 'Compliance Team', reason: 'Audit access required' },
  { id: 5, timestamp: '2024-01-12 10:15:33', user: 'David Kim', action: 'removed', role: 'maintenance', changedBy: 'System', reason: 'Role deactivated' }
])

// Filtered roles
const filteredRoles = computed(() => {
  let result = roles.value
  if (searchKeyword.value) {
    const search = searchKeyword.value.toLowerCase()
    result = result.filter(r => r.name.toLowerCase().includes(search) || r.description.toLowerCase().includes(search))
  }
  if (statusFilter.value) {
    result = result.filter(r => r.status === statusFilter.value)
  }
  return result
})

// Helper functions
const applyFilters = () => {
  ElMessage.success('Filters applied')
}

const resetFilters = () => {
  searchKeyword.value = ''
  statusFilter.value = ''
  ElMessage.success('Filters reset')
}

const refreshRoles = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Role list refreshed')
  }, 800)
}

const createRole = () => {
  dialogTitle.value = 'Create Role'
  currentRole.value = {
    id: null,
    name: '',
    description: '',
    status: 'active',
    isSystem: false,
    selectedPermissions: {
      'User Management': [],
      'Role Management': [],
      'Device Management': [],
      'System Settings': [],
      'Security': [],
      'Reports': []
    }
  }
  dialogVisible.value = true
}

const editRole = (role: any) => {
  if (role.isSystem) {
    ElMessage.warning('System roles cannot be edited')
    return
  }
  dialogTitle.value = 'Edit Role'
  currentRole.value = {
    ...role,
    selectedPermissions: JSON.parse(JSON.stringify(role.permissions))
  }
  dialogVisible.value = true
}

const cloneRole = (role: any) => {
  dialogTitle.value = 'Clone Role'
  currentRole.value = {
    id: null,
    name: `${role.name}_copy`,
    description: `Clone of ${role.name}`,
    status: 'active',
    isSystem: false,
    selectedPermissions: JSON.parse(JSON.stringify(role.permissions))
  }
  dialogVisible.value = true
}

const saveRole = async () => {
  if (!roleFormRef.value) return
  await roleFormRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success(`Role ${currentRole.value.id ? 'updated' : 'created'} successfully`)
      dialogVisible.value = false
    }
  })
}

const handleRoleAction = (cmd: string, role: any) => {
  if (cmd === 'activate') {
    role.status = 'active'
    ElMessage.success(`Role ${role.name} activated`)
  } else if (cmd === 'deactivate') {
    role.status = 'inactive'
    ElMessage.success(`Role ${role.name} deactivated`)
  } else if (cmd === 'delete') {
    ElMessageBox.confirm(`Delete role "${role.name}"? This will unassign all users.`, 'Confirm Delete', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'danger'
    }).then(() => {
      roles.value = roles.value.filter(r => r.id !== role.id)
      ElMessage.success(`Role ${role.name} deleted`)
    }).catch(() => {})
  }
}

const removeUserFromRole = (role: any, user: any) => {
  ElMessageBox.confirm(`Remove ${user.name} from ${role.name}?`, 'Confirm Remove', {
    confirmButtonText: 'Remove',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    role.assignedUsers = role.assignedUsers.filter((u: any) => u.id !== user.id)
    role.userCount--
    ElMessage.success(`User removed from role`)
  }).catch(() => {})
}

const addUserToRole = (role: any) => {
  ElMessage.info(`Add user to ${role.name} dialog opened`)
}

const exportRoles = () => {
  ElMessage.info('Exporting roles...')
  setTimeout(() => {
    ElMessage.success('Roles exported successfully')
  }, 1000)
}

const importRoles = () => {
  ElMessage.info('Import roles dialog opened')
}

const managePermissionTemplates = () => {
  ElMessage.info('Manage permission templates')
}

const viewAllHistory = () => {
  ElMessage.info('Viewing all role assignment history')
}

const bulkAssignRoles = () => {
  ElMessage.info('Bulk assign roles dialog opened')
}

const generateRoleReport = () => {
  ElMessage.info('Generating role report...')
}

const roleComparison = () => {
  ElMessage.info('Role comparison tool opened')
}

const viewAuditLog = () => {
  ElMessage.info('Viewing audit log')
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
.role-management-container {
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

/* Roles Section */
.roles-section {
  margin-bottom: 24px;
}

.roles-card {
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

.role-name {
  font-weight: 600;
  color: #1e293b;
  text-transform: capitalize;
  margin-right: 8px;
}

/* Expand Content */
.expand-content {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.expand-title {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.permissions-section-expand {
  margin-bottom: 20px;
}

.permissions-grid-expand {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.permission-category-expand {
  background: white;
  padding: 12px;
  border-radius: 8px;
}

.category-title-expand {
  font-size: 12px;
  font-weight: 600;
  color: #3b82f6;
  margin-bottom: 8px;
}

.permission-list-expand {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.user-list-expand {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

/* Permissions Summary Section */
.permissions-summary-section {
  margin-bottom: 24px;
}

.permissions-summary-card {
  border-radius: 12px;
  background: white;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.category-card {
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.category-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.category-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}

.category-count {
  font-size: 11px;
  color: #64748b;
}

.category-permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* History Section */
.history-section {
  margin-bottom: 24px;
}

.history-card {
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

/* Dialog Styles */
.permission-tabs {
  width: 100%;
}

.permission-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .permissions-grid-expand {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }

  .permissions-grid-expand {
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