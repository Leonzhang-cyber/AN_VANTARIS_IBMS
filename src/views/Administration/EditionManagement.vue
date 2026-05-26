<template>
  <div class="edition-manager">
    <!-- 头部 -->
    <div class="manager-header">
      <div class="header-title">
        <el-icon><Edit /></el-icon>
        <span>Edition Menu Manager</span>
      </div>
      <div class="header-actions">
        <el-button
            type="success"
            @click="saveAllChanges"
            :loading="saving"
            :disabled="!hasChanges"
        >
          <el-icon><Check /></el-icon>
          Save Configuration
        </el-button>
        <el-button @click="resetChanges" :disabled="!hasChanges">
          <el-icon><Refresh /></el-icon>
          Reset
        </el-button>
      </div>
    </div>

    <!-- 当前激活版本显示 + 切换按钮 -->
    <div class="active-version-bar">
      <div class="active-version-content">
        <el-tag type="primary" size="large" effect="dark" class="active-version-tag">
          <el-icon><Monitor /></el-icon>
          <span>Currently Active: </span>
          <strong>{{ activeVersionName }}</strong>
        </el-tag>
        <el-tag type="info" size="small" class="active-version-desc">
          {{ activeVersionDesc }}
        </el-tag>
      </div>
      <div class="active-version-actions">
        <el-dropdown trigger="click" @command="handleSwitchActiveVersion">
          <el-button type="primary" size="small">
            <el-icon><Switch /></el-icon>
            Switch Active Version
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                  v-for="version in allVersions"
                  :key="version.version_code"
                  :command="version.version_code"
                  :class="{ 'is-active': currentActiveVersion === version.version_code }"
              >
                <span class="version-option-icon">{{ version.icon || '📦' }}</span>
                <span>{{ version.version_name }}</span>
                <el-icon v-if="currentActiveVersion === version.version_code" class="check-icon"><Check /></el-icon>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 版本标签页 -->
    <div class="version-tabs">
      <el-tabs v-model="currentEditVersion" type="card" @tab-click="handleTabChange">
        <el-tab-pane
            v-for="version in allVersions"
            :key="version.version_code"
            :name="version.version_code"
        >
          <template #label>
            <span class="tab-label" :class="{ 'is-system-active': currentActiveVersion === version.version_code }">
              <span class="tab-icon">{{ version.icon || '📦' }}</span>
              <span>{{ version.version_name }}</span>
              <el-tag v-if="currentActiveVersion === version.version_code" size="small" type="primary" class="active-badge">Active</el-tag>
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 当前编辑版本信息 -->
    <div class="version-info-bar">
      <div class="info-content">
        <el-icon><Edit /></el-icon>
        <span class="info-label">Editing:</span>
        <span class="version-name">{{ currentEditVersionName }}</span>
        <span class="version-desc">{{ currentEditVersionDesc }}</span>
      </div>
      <div class="selection-info">
        <span>Selected: <strong>{{ currentSelectedCount }}</strong> / <strong>{{ totalMenuCount }}</strong> menus</span>
        <el-button size="small" @click="selectAllMenus" class="select-all-btn">
          <el-icon><Select /></el-icon>
          Select All
        </el-button>
        <el-button size="small" @click="deselectAllMenus" class="deselect-all-btn">
          <el-icon><Close /></el-icon>
          Deselect All
        </el-button>
        <el-divider direction="vertical" />
        <el-button size="small" @click="expandAll" class="expand-btn">
          <el-icon><Expand /></el-icon>
          Expand All
        </el-button>
        <el-button size="small" @click="collapseAll" class="collapse-btn">
          <el-icon><Fold /></el-icon>
          Collapse All
        </el-button>
      </div>
    </div>

    <!-- 菜单树 -->
    <div class="menu-editor">
      <div class="menu-tree-container">
        <div v-if="loading" class="loading-state">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>Loading menu data...</span>
        </div>
        <div v-else-if="menuTree.length === 0" class="empty-state">
          <el-icon><FolderOpened /></el-icon>
          <span>No menu data available</span>
        </div>
        <el-tree
            v-else
            ref="treeRef"
            :data="menuTree"
            node-key="menu_path"
            :expand-on-click-node="false"
            :highlight-current="false"
            :default-expanded-keys="expandedKeys"
            :props="treeProps"
        >
          <template #default="{ data }">
            <div class="tree-node">
              <div class="node-icon">
                <el-icon v-if="data.children && data.children.length"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
              </div>
              <div class="node-info">
                <span class="node-title">{{ data.menu_title }}</span>
                <span class="node-path">{{ data.menu_path }}</span>
              </div>
              <div class="node-checkbox">
                <el-checkbox
                    :model-value="isMenuSelectedForCurrentVersion(data.menu_path)"
                    @change="(val) => toggleMenuSelection(data, val)"
                />
              </div>
            </div>
          </template>
        </el-tree>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, watch, nextTick} from 'vue'
import {ElMessage, ElMessageBox} from 'element-plus'
import {
  Edit, Check, Refresh, Folder, Document, Select, Close,
  Monitor, Switch, ArrowDown, Expand, Fold, FolderOpened, Loading
} from '@element-plus/icons-vue'
import {
  getDefaultVersion,
  listVersions,
  getMenuTree,
  getVersionMenus,
  batchUpdateVersionMenus
} from '@/api/system_api'
import {useCounterStore} from '@/stores/counter'

const counterStore = useCounterStore()

// ==================== 数据状态 ====================
const loading = ref(true)
const saving = ref(false)
const allVersions = ref([])
const menuTree = ref([])

// 版本菜单配置存储
const versionSelections = ref({})  // { version_code: { selected: Set, original: Set } }

// UI状态
const currentEditVersion = ref('')
const currentActiveVersion = ref('')
const expandedKeys = ref([])
const treeRef = ref()
const hasChanges = ref(false)

// ==================== 计算属性 ====================
// 当前激活版本信息
const activeVersionName = computed(() => {
  const version = allVersions.value.find(v => v.version_code === currentActiveVersion.value)
  return version?.version_name || 'Unknown'
})

const activeVersionDesc = computed(() => {
  const version = allVersions.value.find(v => v.version_code === currentActiveVersion.value)
  return version?.description || ''
})

// 当前编辑版本信息
const currentEditVersionName = computed(() => {
  const version = allVersions.value.find(v => v.version_code === currentEditVersion.value)
  return version?.version_name || 'Unknown'
})

const currentEditVersionDesc = computed(() => {
  const version = allVersions.value.find(v => v.version_code === currentEditVersion.value)
  return version?.description || ''
})

// 当前编辑版本的选中数量
const currentSelectedCount = computed(() => {
  return versionSelections.value[currentEditVersion.value]?.selected?.size || 0
})

// 总菜单数量
const totalMenuCount = computed(() => {
  return getAllMenuIndexes(menuTree.value).length
})

// ==================== 工具函数 ====================
// 获取所有菜单的 index
const getAllMenuIndexes = (nodes) => {
  let indexes = []
  if (!nodes || !Array.isArray(nodes)) return indexes
  for (const node of nodes) {
    if (node && node.index) {
      indexes.push(node.index)
      if (node.children && Array.isArray(node.children) && node.children.length) {
        indexes = indexes.concat(getAllMenuIndexes(node.children))
      }
    }
  }
  return indexes
}

// 收集所有子菜单 index
const getAllChildIndexes = (menu) => {
  const indexes = [menu.index]
  if (menu.children && menu.children.length) {
    for (const child of menu.children) {
      indexes.push(...getAllChildIndexes(child))
    }
  }
  return indexes
}

// 从版本菜单配置获取选中的 Set
const getSelectedSetFromVersionMenus = (data) => {
  if (!data) return new Set()
  let menus = []
  if (data.menus && Array.isArray(data.menus)) {
    menus = data.menus
  } else if (Array.isArray(data)) {
    menus = data
  } else {
    return new Set()
  }
  return new Set(
      menus
          .filter(m => m.is_visible === true || m.is_visible === 1 || m.is_visible === 'true')
          .map(m => m.menu_path)
  )
}

// ==================== 菜单操作 ====================
// 判断当前编辑版本的菜单是否选中
const isMenuSelectedForCurrentVersion = (menuIndex) => {
  return versionSelections.value[currentEditVersion.value]?.selected?.has(menuIndex) || false
}

// 切换菜单选择
const toggleMenuSelection = (menu, checked) => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (!versionData) return

  const newSelected = new Set(versionData.selected)
  const childIndexes = getAllChildIndexes(menu)

  if (checked) {
    childIndexes.forEach(idx => newSelected.add(idx))
  } else {
    childIndexes.forEach(idx => newSelected.delete(idx))
  }

  versionData.selected = newSelected
  checkChanges()
}

// 全选
const selectAllMenus = () => {
  const allIndexes = getAllMenuIndexes(menuTree.value)
  const versionData = versionSelections.value[currentEditVersion.value]
  if (versionData) {
    versionData.selected = new Set(allIndexes)
    checkChanges()
    ElMessage.success(`Selected all ${allIndexes.length} menus`)
  }
}

// 取消全选
const deselectAllMenus = () => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (versionData) {
    versionData.selected = new Set()
    checkChanges()
    ElMessage.success('Deselected all menus')
  }
}

// 检查是否有未保存的更改
const checkChanges = () => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (!versionData) {
    hasChanges.value = false
    return
  }

  // 比较两个 Set 是否相等
  const isEqual = versionData.selected.size === versionData.original.size &&
      [...versionData.selected].every(v => versionData.original.has(v))

  hasChanges.value = !isEqual
}

// 重置当前版本的更改
const resetChanges = () => {
  const versionData = versionSelections.value[currentEditVersion.value]
  if (versionData) {
    versionData.selected = new Set(versionData.original)
    checkChanges()
    ElMessage.success('Reset completed')
  }
}

// 展开所有节点
const expandAll = () => {
  expandedKeys.value = getAllMenuIndexes(menuTree.value)
  ElMessage.info('All menus expanded')
}

// 折叠所有节点
const collapseAll = () => {
  expandedKeys.value = []
  ElMessage.info('All menus collapsed')
}

// ==================== API 操作 ====================
// 加载单个版本的菜单配置
const loadVersionMenus = async (versionCode) => {
  try {
    const data = await getVersionMenus(versionCode)
    const selectedSet = getSelectedSetFromVersionMenus(data)

    if (!versionSelections.value[versionCode]) {
      versionSelections.value[versionCode] = {
        selected: new Set(),
        original: new Set()
      }
    }
    versionSelections.value[versionCode].selected = new Set(selectedSet)
    versionSelections.value[versionCode].original = new Set(selectedSet)

    console.log(`版本 ${versionCode} 菜单配置加载成功，选中 ${selectedSet.size} 个菜单`)
  } catch (error) {
    console.error(`加载版本 ${versionCode} 菜单配置失败:`, error)
    // 失败时使用默认全选
    const allIndexes = getAllMenuIndexes(menuTree.value)
    if (!versionSelections.value[versionCode]) {
      versionSelections.value[versionCode] = {
        selected: new Set(),
        original: new Set()
      }
    }
    versionSelections.value[versionCode].selected = new Set(allIndexes)
    versionSelections.value[versionCode].original = new Set(allIndexes)
  }
}

// 保存所有更改
const saveAllChanges = async () => {
  saving.value = true
  try {
    const versionData = versionSelections.value[currentEditVersion.value]
    if (!versionData) return

    const allMenuIndexes = getAllMenuIndexes(menuTree.value)
    const menusToSave = allMenuIndexes.map(menuPath => ({
      menu_path: menuPath,
      is_visible: versionData.selected.has(menuPath)
    }))

    await batchUpdateVersionMenus(currentEditVersion.value, menusToSave)

    // 更新原始数据
    versionData.original = new Set(versionData.selected)
    checkChanges()

    // 如果当前编辑的版本就是系统激活的版本，更新 store
    if (currentEditVersion.value === currentActiveVersion.value) {
      counterStore.setMenuVersion(currentEditVersion.value)
      // 重新获取菜单配置
      const menuRes = await getVersionMenus(currentEditVersion.value)
      const newSelectedSet = getSelectedSetFromVersionMenus(menuRes)
      // 触发 Layout 刷新（通过重新加载页面）
      setTimeout(() => {
        window.location.reload()
      }, 1000)
    }

    ElMessage.success(`Configuration saved for ${currentEditVersionName.value}`)
  } catch (error) {
    console.error('Save error:', error)
    ElMessage.error('Failed to save configuration')
  } finally {
    saving.value = false
  }
}

// 切换系统激活版本
const handleSwitchActiveVersion = async (versionCode) => {
  if (versionCode === currentActiveVersion.value) {
    ElMessage.info('This version is already active')
    return
  }

  try {
    // 更新 store 中的激活版本
    counterStore.setMenuVersion(versionCode)
    currentActiveVersion.value = versionCode

    ElMessage.success(`Switched to ${counterStore.currentVersionFullName.value}`)

    // 刷新页面以应用新菜单
    setTimeout(() => {
      window.location.reload()
    }, 500)
  } catch (error) {
    console.error('Switch version error:', error)
    ElMessage.error('Failed to switch version')
  }
}

// ==================== 初始化 ====================
const initData = async () => {
  try {
    console.log('=== 开始初始化请求 ===')

    // 并行请求
    const [defaultVer, versions, tree] = await Promise.all([
      getDefaultVersion(),
      listVersions(),
      getMenuTree()
    ])

    console.log('默认版本:', defaultVer)
    console.log('所有版本:', versions)
    console.log('菜单树:', tree)

    allVersions.value = versions
    menuTree.value = tree
    currentActiveVersion.value = defaultVer?.version_code || versions[0]?.version_code

    // 设置默认编辑版本为激活版本
    currentEditVersion.value = currentActiveVersion.value

    // 加载所有版本的菜单配置
    const loadPromises = versions.map(v => loadVersionMenus(v.version_code))
    await Promise.all(loadPromises)

    // 展开所有节点
    expandedKeys.value = getAllMenuIndexes(menuTree.value)

    console.log('=== 所有接口请求完成 ===')
  } catch (error) {
    console.error('初始化异常:', error)
    ElMessage.error('Failed to initialize data')
  } finally {
    loading.value = false
  }
}

// Tab 切换时重置 changes 状态
const handleTabChange = () => {
  checkChanges()
  // 展开所有节点
  expandedKeys.value = getAllMenuIndexes(menuTree.value)
}

// 监听编辑版本变化，重置 changes 状态
watch(currentEditVersion, () => {
  checkChanges()
})

// 组件挂载
onMounted(() => {
  initData()
})
</script>

<style scoped>
.edition-manager {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  overflow: hidden;
}

/* Header */
.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-title .el-icon {
  font-size: 22px;
  color: #409eff;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Active Version Bar */
.active-version-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: linear-gradient(135deg, #e8f4ff, #d9ecff);
  border-bottom: 2px solid #409eff;
}

.active-version-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.active-version-tag {
  padding: 8px 16px;
  font-size: 14px;
  background: linear-gradient(135deg, #409eff, #66b1ff);
  border: none;
}

.active-version-tag .el-icon {
  margin-right: 8px;
}

.active-version-tag strong {
  font-weight: 700;
  margin-left: 4px;
}

.active-version-desc {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.3);
  color: #409eff;
}

.active-version-actions {
  display: flex;
  gap: 12px;
}

/* Dropdown */
:deep(.el-dropdown-menu__item.is-active) {
  background: #ecf5ff;
  color: #409eff;
}

.version-option-icon {
  margin-right: 8px;
  font-size: 14px;
}

.check-icon {
  margin-left: auto;
  color: #409eff;
}

/* Version Tabs */
.version-tabs {
  background: #fff;
  padding: 0 24px;
  border-bottom: 1px solid #e4e7ed;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.tab-label.is-system-active .tab-icon {
  animation: pulse-glow 1.5s ease-in-out infinite;
}

.tab-icon {
  font-size: 16px;
}

.active-badge {
  margin-left: 6px;
}

@keyframes pulse-glow {
  0%, 100% {
    text-shadow: 0 0 0px #409eff;
  }
  50% {
    text-shadow: 0 0 4px #409eff;
  }
}

/* Version Info Bar */
.version-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #f0f7ff;
  border-bottom: 1px solid #d9ecff;
}

.info-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-content .el-icon {
  font-size: 18px;
  color: #409eff;
}

.info-label {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.version-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.version-desc {
  font-size: 12px;
  color: #606266;
  margin-left: 8px;
}

.selection-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selection-info span {
  font-size: 13px;
  color: #606266;
}

.selection-info strong {
  color: #409eff;
  font-size: 15px;
}

.select-all-btn, .deselect-all-btn, .expand-btn, .collapse-btn {
  padding: 4px 12px;
  font-size: 12px;
}

.select-all-btn {
  background: #ecf5ff;
  border-color: #d9ecff;
  color: #409eff;
}

.deselect-all-btn {
  background: #fef0f0;
  border-color: #fde2e2;
  color: #f56c6c;
}

.expand-btn, .collapse-btn {
  background: #f5f7fa;
  border-color: #e4e7ed;
  color: #606266;
}

.expand-btn:hover, .collapse-btn:hover {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

/* Menu Editor */
.menu-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 20px;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.menu-tree-container {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
  gap: 12px;
}

.loading-state .el-icon, .empty-state .el-icon {
  font-size: 48px;
}

/* Tree Node Styles */
.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.tree-node:hover {
  background: #f5f7fa;
}

.node-icon {
  width: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.node-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 8px;
}

.node-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.node-path {
  font-size: 11px;
  color: #c0c4cc;
  margin-top: 2px;
}

.node-checkbox {
  margin: 0 12px;
}

/* Deep Tree Styles */
:deep(.el-tree-node__content) {
  height: auto;
  padding: 0;
}

:deep(.el-tree-node__content:hover) {
  background: transparent;
}

:deep(.el-tree) {
  --el-tree-node-hover-bg-color: transparent;
}

.el-divider--vertical {
  height: 20px;
  margin: 0 4px;
}

.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>