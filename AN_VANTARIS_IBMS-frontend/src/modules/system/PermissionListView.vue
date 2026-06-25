<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import { ApiError } from '@/services/api/errors'
import {
  createSystemPermission,
  deleteSystemPermission,
  getSystemPermissions,
  updateSystemPermission,
  type PermissionRecord,
} from '@/services/api/system'

const loading = ref(false)
const saving = ref(false)
const errorMessage = ref('')
const permissions = ref<PermissionRecord[]>([])

const createDialogVisible = ref(false)
const editDialogVisible = ref(false)

const createForm = reactive({
  perm_code: '',
  name: '',
  description: '',
})

const editForm = reactive({
  id: '',
  perm_code: '',
  name: '',
  description: '',
})

function displayName(row: PermissionRecord): string {
  return row.name?.trim() || row.perm_code
}

async function loadPermissions(): Promise<void> {
  loading.value = true
  errorMessage.value = ''
  try {
    permissions.value = await getSystemPermissions()
  } catch (error) {
    permissions.value = []
    errorMessage.value =
      error instanceof ApiError ? error.message : 'Failed to load permissions.'
  } finally {
    loading.value = false
  }
}

function openCreateDialog(): void {
  createForm.perm_code = ''
  createForm.name = ''
  createForm.description = ''
  createDialogVisible.value = true
}

function openEditDialog(row: PermissionRecord): void {
  editForm.id = row.id
  editForm.perm_code = row.perm_code
  editForm.name = row.name ?? ''
  editForm.description = row.description
  editDialogVisible.value = true
}

async function submitCreate(): Promise<void> {
  if (!createForm.perm_code.trim()) {
    ElMessage.warning('Permission code is required.')
    return
  }
  if (!createForm.description.trim() && !createForm.name.trim()) {
    ElMessage.warning('Name or description is required.')
    return
  }

  saving.value = true
  try {
    await createSystemPermission({
      perm_code: createForm.perm_code,
      name: createForm.name,
      description: createForm.description,
    })
    createDialogVisible.value = false
    ElMessage.success('Permission created.')
    await loadPermissions()
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : 'Create failed.')
  } finally {
    saving.value = false
  }
}

async function submitEdit(): Promise<void> {
  if (!editForm.id) {
    return
  }

  saving.value = true
  try {
    await updateSystemPermission(editForm.id, {
      name: editForm.name,
      description: editForm.description,
    })
    editDialogVisible.value = false
    ElMessage.success('Permission updated.')
    await loadPermissions()
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : 'Update failed.')
  } finally {
    saving.value = false
  }
}

async function confirmDelete(row: PermissionRecord): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `Delete permission "${row.perm_code}"? This cannot be undone.`,
      'Delete permission',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  try {
    await deleteSystemPermission(row.id)
    ElMessage.success('Permission deleted.')
    await loadPermissions()
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : 'Delete failed.')
  }
}

onMounted(() => {
  void loadPermissions()
})
</script>

<template>
  <div class="permission-page">
    <RouteL3ContentPanel />

    <el-card shadow="never">
      <template #header>
        <div class="page-header">
          <div>
            <h1>Permission Management</h1>
            <p>Manage backend permission codes used by protected ONE APIs.</p>
          </div>
          <el-button type="primary" @click="openCreateDialog">Create permission</el-button>
        </div>
      </template>

      <el-alert
        v-if="errorMessage"
        type="error"
        :title="errorMessage"
        show-icon
        :closable="false"
        class="page-alert"
      />

      <el-table v-loading="loading" :data="permissions" row-key="id" empty-text="No permissions found">
        <el-table-column prop="perm_code" label="Permission Code" min-width="180" />
        <el-table-column label="Name" min-width="160">
          <template #default="{ row }">
            {{ displayName(row) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="240" show-overflow-tooltip />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">Edit</el-button>
            <el-button link type="danger" @click="confirmDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="createDialogVisible" title="Create permission" width="480px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="Permission code" required>
          <el-input v-model="createForm.perm_code" placeholder="system:read" />
        </el-form-item>
        <el-form-item label="Name">
          <el-input v-model="createForm.name" placeholder="Display name" />
        </el-form-item>
        <el-form-item label="Description" required>
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="What this permission allows"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="saving" @click="submitCreate">Create</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="Edit permission" width="480px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="Permission code">
          <el-input v-model="editForm.perm_code" disabled />
        </el-form-item>
        <el-form-item label="Name">
          <el-input v-model="editForm.name" placeholder="Display name" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="What this permission allows"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="saving" @click="submitEdit">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.permission-page {
  padding: 16px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.page-alert {
  margin-bottom: 16px;
}
</style>
