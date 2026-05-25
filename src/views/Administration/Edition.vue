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
        <div class="loading-tip">Edition Menu Manager</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="edition-manager">
    <!-- Header -->
    <div class="manager-header">
      <div class="header-title">
        <el-icon><Edit /></el-icon>
        <span>Edition Menu Manager</span>
      </div>
      <div class="header-actions">
        <el-button type="success" @click="saveAllChanges" :loading="saving">
          <el-icon><Check /></el-icon>
          Save Configuration
        </el-button>
        <el-button @click="resetAllChanges">
          <el-icon><Refresh /></el-icon>
          Reset
        </el-button>
      </div>
    </div>

    <!-- 当前系统激活版本显示 + 切换按钮 -->
    <div class="active-version-bar">
      <div class="active-version-content">
        <el-tag type="primary" size="large" effect="dark" class="active-version-tag">
          <el-icon><Monitor /></el-icon>
          <span>Currently Active: </span>
          <strong>{{ systemActiveVersionFullName }}</strong>
        </el-tag>
        <el-tag type="info" size="small" class="active-version-desc">
          {{ systemActiveVersionDesc }}
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
              <el-dropdown-item command="essential" :class="{ 'is-active': systemActiveVersion === 'essential' }">
                <span class="version-option-icon">📊</span>
                <span>Essential Version</span>
                <el-icon v-if="systemActiveVersion === 'essential'" class="check-icon"><Check /></el-icon>
              </el-dropdown-item>
              <el-dropdown-item command="professional" :class="{ 'is-active': systemActiveVersion === 'professional' }">
                <span class="version-option-icon">🚀</span>
                <span>Professional Edition</span>
                <el-icon v-if="systemActiveVersion === 'professional'" class="check-icon"><Check /></el-icon>
              </el-dropdown-item>
              <el-dropdown-item command="smart-campus" :class="{ 'is-active': systemActiveVersion === 'smart-campus' }">
                <span class="version-option-icon">🏢</span>
                <span>Smart Campus Edition</span>
                <el-icon v-if="systemActiveVersion === 'smart-campus'" class="check-icon"><Check /></el-icon>
              </el-dropdown-item>
              <el-dropdown-item command="enterprise-ai" :class="{ 'is-active': systemActiveVersion === 'enterprise-ai' }">
                <span class="version-option-icon">👑</span>
                <span>Enterprise AI Flagship</span>
                <el-icon v-if="systemActiveVersion === 'enterprise-ai'" class="check-icon"><Check /></el-icon>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- Version Tabs -->
    <div class="version-tabs">
      <el-tabs v-model="activeVersion" type="card" @tab-click="handleTabClick">
        <el-tab-pane name="essential">
          <template #label>
            <span class="tab-label" :class="{ 'is-system-active': systemActiveVersion === 'essential' }">
              <span class="tab-icon">📊</span>
              <span>Essential</span>
              <el-tag v-if="systemActiveVersion === 'essential'" size="small" type="primary" class="active-badge">Active</el-tag>
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="professional">
          <template #label>
            <span class="tab-label" :class="{ 'is-system-active': systemActiveVersion === 'professional' }">
              <span class="tab-icon">🚀</span>
              <span>Professional</span>
              <el-tag v-if="systemActiveVersion === 'professional'" size="small" type="primary" class="active-badge">Active</el-tag>
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="smart-campus">
          <template #label>
            <span class="tab-label" :class="{ 'is-system-active': systemActiveVersion === 'smart-campus' }">
              <span class="tab-icon">🏢</span>
              <span>Smart Campus</span>
              <el-tag v-if="systemActiveVersion === 'smart-campus'" size="small" type="primary" class="active-badge">Active</el-tag>
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="enterprise-ai">
          <template #label>
            <span class="tab-label" :class="{ 'is-system-active': systemActiveVersion === 'enterprise-ai' }">
              <span class="tab-icon">👑</span>
              <span>Enterprise AI</span>
              <el-tag v-if="systemActiveVersion === 'enterprise-ai'" size="small" type="primary" class="active-badge">Active</el-tag>
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Version Info Bar - 当前编辑的版本信息 + 展开/折叠按钮 -->
    <div class="version-info-bar">
      <div class="info-content">
        <el-icon><Edit /></el-icon>
        <span class="info-label">Editing:</span>
        <span class="version-name">{{ currentVersionFullName }}</span>
        <span class="version-desc">{{ currentVersionDesc }}</span>
      </div>
      <div class="selection-info">
        <span>Selected: <strong>{{ selectedCount }}</strong> / <strong>{{ totalMenuCount }}</strong> menus</span>
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

    <!-- Menu Tree -->
    <div class="menu-editor">
      <div class="menu-tree-container">
        <el-tree
            ref="treeRef"
            :data="allMenu"
            node-key="index"
            :expand-on-click-node="false"
            :highlight-current="false"
            :default-expanded-keys="expandedKeys"
        >
          <template #default="{ data }">
            <div class="tree-node">
              <div class="node-icon">
                <el-icon v-if="data.children && data.children.length"><Folder /></el-icon>
                <el-icon v-else><Document /></el-icon>
              </div>
              <div class="node-info">
                <span class="node-title">{{ data.title }}</span>
                <span class="node-path">{{ data.index }}</span>
              </div>
              <div class="node-checkbox">
                <el-checkbox
                    :model-value="isMenuSelected(data.index)"
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

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit, Check, Refresh, InfoFilled, Folder, Document, Select, Close,
  Monitor, Switch, ArrowDown, Expand, Fold
} from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter'

const counterStore = useCounterStore()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading Edition Manager...')
const loadingMessages = [
  'Loading Edition Manager...',
  'Loading menu data...',
  'Initializing editor...',
  'Almost ready...'
]

// Editor state
const activeVersion = ref<'essential' | 'professional' | 'smart-campus' | 'enterprise-ai'>('essential')
const allMenu = computed(() => counterStore.allMenu)
const currentSelections = ref<string[]>([])
const originalSelections = ref<string[]>([])
const expandedKeys = ref<string[]>([])
const treeRef = ref()
const saving = ref(false)

// 系统当前激活的版本
const systemActiveVersion = computed(() => counterStore.menuVersion)
const systemActiveVersionFullName = computed(() => counterStore.currentVersionFullName)
const systemActiveVersionDesc = computed(() => counterStore.currentVersionDesc)

// 当前编辑的版本信息
const currentVersionFullName = computed(() => {
  switch (activeVersion.value) {
    case 'essential': return 'Essential Version'
    case 'professional': return 'Professional Edition'
    case 'smart-campus': return 'Smart Campus Edition'
    case 'enterprise-ai': return 'Enterprise AI Flagship'
    default: return 'Essential Version'
  }
})

const currentVersionDesc = computed(() => {
  switch (activeVersion.value) {
    case 'essential': return 'Core device management & administration'
    case 'professional': return 'Alarm, maintenance, reports & API integration'
    case 'smart-campus': return 'Multi-site, energy, blockchain & command center'
    case 'enterprise-ai': return 'AI analytics, video intelligence & digital twin'
    default: return 'Core device management'
  }
})

// 获取所有菜单的 index
const getAllMenuIndexes = (nodes: any[]): string[] => {
  let indexes: string[] = []
  nodes.forEach(node => {
    indexes.push(node.index)
    if (node.children && node.children.length) {
      indexes = indexes.concat(getAllMenuIndexes(node.children))
    }
  })
  return indexes
}

// 从菜单获取所有选中的 index
const getSelectedIndexesFromMenu = (menu: any[]): string[] => {
  const indexes: string[] = []
  const collect = (nodes: any[]) => {
    nodes.forEach(node => {
      indexes.push(node.index)
      if (node.children && node.children.length) {
        collect(node.children)
      }
    })
  }
  collect(menu)
  return indexes
}

const totalMenuCount = computed(() => getAllMenuIndexes(allMenu.value).length)
const selectedCount = computed(() => currentSelections.value.length)

// 判断菜单是否选中
const isMenuSelected = (menuIndex: string): boolean => {
  return currentSelections.value.includes(menuIndex)
}

// 切换菜单选择（包括子菜单）
const toggleMenuSelection = (menu: any, checked: boolean) => {
  const selections = [...currentSelections.value]
  const menuIndexes = [menu.index]

  // 如果有子菜单，收集所有子菜单的 index
  if (menu.children && menu.children.length) {
    const collectChildIndexes = (nodes: any[]) => {
      nodes.forEach(node => {
        menuIndexes.push(node.index)
        if (node.children && node.children.length) {
          collectChildIndexes(node.children)
        }
      })
    }
    collectChildIndexes(menu.children)
  }

  if (checked) {
    // 添加菜单及其所有子菜单
    menuIndexes.forEach(idx => {
      if (!selections.includes(idx)) {
        selections.push(idx)
      }
    })
  } else {
    // 移除菜单及其所有子菜单
    menuIndexes.forEach(idx => {
      const index = selections.indexOf(idx)
      if (index > -1) {
        selections.splice(index, 1)
      }
    })
  }

  currentSelections.value = selections
}

// 全选所有菜单
const selectAllMenus = () => {
  currentSelections.value = getAllMenuIndexes(allMenu.value)
  ElMessage.success(`Selected all ${currentSelections.value.length} menus`)
}

// 取消全选
const deselectAllMenus = () => {
  currentSelections.value = []
  ElMessage.success('All menus deselected')
}

// 展开所有节点 - 修复
const expandAll = () => {
  nextTick(() => {
    const allKeys = getAllMenuIndexes(allMenu.value)
    expandedKeys.value = [...allKeys]
    // 强制刷新树组件
    if (treeRef.value) {
      // 先清空再设置，强制刷新
      treeRef.value.store.nodesMap = {}
      expandedKeys.value = [...allKeys]
    }
    ElMessage.info('All menus expanded')
  })
}

// 折叠所有节点 - 修复：清空 expandedKeys
const collapseAll = () => {
  nextTick(() => {
    // 关键修复：清空展开的 keys
    expandedKeys.value = []
    ElMessage.info('All menus collapsed')
  })
}

// 加载版本数据 - 修复：确保数据正确加载
const loadVersionData = () => {
  const versionMenu = counterStore.getVersionMenu(activeVersion.value)
  // 深拷贝避免引用问题
  currentSelections.value = [...getSelectedIndexesFromMenu(JSON.parse(JSON.stringify(versionMenu)))]
  originalSelections.value = [...currentSelections.value]
  // 展开所有节点
  nextTick(() => {
    expandedKeys.value = getAllMenuIndexes(allMenu.value)
  })
}

// Tab 切换 - 修复：重新加载数据
const handleTabClick = () => {
  loadVersionData()
}

// 切换系统激活版本 - 修复：不刷新页面也能更新菜单
const handleSwitchActiveVersion = (version: string) => {
  const versionMap: Record<string, 'essential' | 'professional' | 'smart-campus' | 'enterprise-ai'> = {
    essential: 'essential',
    professional: 'professional',
    'smart-campus': 'smart-campus',
    'enterprise-ai': 'enterprise-ai'
  }
  const selectedVersion = versionMap[version]

  if (selectedVersion && selectedVersion !== systemActiveVersion.value) {
    counterStore.setMenuVersion(selectedVersion)
    ElMessage.success(`Switched to ${counterStore.currentVersionFullName.value}`)
    // 重新加载当前编辑版本的数据，确保显示正确
    loadVersionData()
  } else if (selectedVersion === systemActiveVersion.value) {
    ElMessage.info('This version is already active')
  }
}

// 保存所有更改 - 修复：保存后自动刷新当前激活版本的菜单
const saveAllChanges = async () => {
  saving.value = true
  try {
    // 根据选中的 index 从 allMenu 生成新菜单
    const generateMenuFromSelections = (selectedIndexes: string[]): any[] => {
      const deepCopyAllMenu = JSON.parse(JSON.stringify(allMenu.value))
      const filterMenu = (nodes: any[]): any[] => {
        return nodes.filter(node => {
          if (selectedIndexes.includes(node.index)) {
            if (node.children && node.children.length) {
              const filteredChildren = filterMenu(node.children)
              if (filteredChildren.length > 0) {
                node.children = filteredChildren
              } else {
                delete node.children
              }
            }
            return true
          }
          return false
        }).map(node => ({ ...node }))
      }
      return filterMenu(deepCopyAllMenu)
    }

    const newMenu = generateMenuFromSelections(currentSelections.value)
    counterStore.updateVersionMenu(activeVersion.value, newMenu)
    originalSelections.value = [...currentSelections.value]

    // 关键修复：如果当前编辑的版本就是系统激活的版本，立即更新 menuConfig
    if (activeVersion.value === systemActiveVersion.value) {
      // 直接更新 store 中的菜单配置，触发 Layout 重新渲染
      counterStore.refreshCurrentMenu()
    }

    ElMessage.success(`Configuration saved! ${currentSelections.value.length} menus enabled for ${currentVersionFullName.value}`)
  } catch (error) {
    console.error('Save error:', error)
    ElMessage.error('Failed to save configuration')
  } finally {
    saving.value = false
  }



}

// 重置所有更改
const resetAllChanges = () => {
  ElMessageBox.confirm(
      'Are you sure you want to reset? All unsaved changes will be lost.',
      'Confirm Reset',
      { confirmButtonText: 'Reset', cancelButtonText: 'Cancel', type: 'warning' }
  ).then(() => {
    currentSelections.value = [...originalSelections.value]
    ElMessage.success('Reset completed')
  }).catch(() => {})
}

// 监听激活版本变化，更新当前编辑版本的数据
watch(systemActiveVersion, () => {
  // 如果当前编辑的版本不是激活版本，重新加载数据
  if (activeVersion.value !== systemActiveVersion.value) {
    loadVersionData()
  }
})

// Initialize
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
      loadVersionData()
      isLoaded.value = true
    }, 400)
  }, 2000)
})
</script>

<style scoped>
/* 样式保持不变，与之前相同 */
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

/* Main Content */
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

/* Dropdown menu active item */
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
  0%, 100% { text-shadow: 0 0 0px #409eff; }
  50% { text-shadow: 0 0 4px #409eff; }
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
</style>