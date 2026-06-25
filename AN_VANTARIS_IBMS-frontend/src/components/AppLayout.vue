<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as menuApi from '@/services/api/menu'
import { normalizeBackendMenu } from '@/services/menu/menu-normalizer'
import { fallbackMenuItems } from '@/services/menu/static-menu'
import type { AppMenuItem } from '@/services/menu/types'
import { logoutLocal } from '@/services/auth/session'

const router = useRouter()
const route = useRoute()
const SIDEBAR_COLLAPSED_KEY = 'vantaris.menu.sidebarCollapsed'

const menuItems = ref<AppMenuItem[]>([...fallbackMenuItems])
const menuLoading = ref(true)
const sidebarCollapsed = ref(false)
const liveMode = ref(true)
const refreshInterval = ref('30s')

const activePath = computed(() => route.path)
const activeMenuId = computed(() => (typeof route.query.menu === 'string' ? route.query.menu : ''))
const activeL3Id = computed(() => (typeof route.query.l3 === 'string' ? route.query.l3 : ''))

const activeL1 = computed(() => {
  for (const l1 of menuItems.value) {
    if (l1.path === route.path || (l1.children ?? []).some((child) => child.path === route.path)) {
      return l1
    }
  }
  return undefined
})

const activeL2 = computed(() => {
  if (activeMenuId.value) {
    for (const l1 of menuItems.value) {
      const byId = (l1.children ?? []).find((child) => child.id === activeMenuId.value)
      if (byId) {
        return byId
      }
    }
  }

  for (const l1 of menuItems.value) {
    const exact = (l1.children ?? []).find((child) => child.path === route.path)
    if (exact) {
      return exact
    }
  }
  return undefined
})

const activeL3Items = computed(() => activeL2.value?.l3Items ?? [])
const activeMenuIndex = computed(() => activeL2.value?.id ?? activePath.value)
const activeL3Label = computed(() => activeL3Items.value.find((item) => item.id === activeL3Id.value)?.label ?? activeL3Items.value[0]?.label ?? '')
const sidebarWidth = computed(() => (sidebarCollapsed.value ? '76px' : '286px'))
const pageTitle = computed(() => activeL2.value?.label ?? activeL1.value?.label ?? String(route.meta.title ?? 'Operations Console'))
const pageSubtitle = computed(() => 'AI-Powered Operations Intelligence for Unified Building & Facility Systems')

async function loadDynamicMenu(): Promise<void> {
  menuLoading.value = true

  try {
    const response = await menuApi.getMenus()
    const normalized = normalizeBackendMenu(response)

    if (normalized.length > 0) {
      menuItems.value = normalized
      return
    }

    menuItems.value = [...fallbackMenuItems]
  } catch {
    menuItems.value = [...fallbackMenuItems]
  } finally {
    menuLoading.value = false
  }
}

function findMenuEntry(id: string): AppMenuItem | undefined {
  for (const l1 of menuItems.value) {
    if (l1.id === id) {
      return l1
    }

    const child = (l1.children ?? []).find((item) => item.id === id)
    if (child) {
      return child
    }
  }

  return undefined
}

function onMenuSelect(index: string): void {
  if (!index || index === '#') {
    return
  }

  const selected = findMenuEntry(index)
  if (selected?.path) {
    router.push({
      path: selected.path,
      query: {
        menu: selected.id,
      },
    })
    return
  }

  router.push(index)
}

function onL3Select(id: string): void {
  router.push({
    path: route.path,
    query: {
      ...route.query,
      menu: activeL2.value?.id,
      l3: id,
    },
  })
}

function onLogout(): void {
  logoutLocal()
  router.push('/login')
}

function toggleSidebar(): void {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, sidebarCollapsed.value ? 'true' : 'false')
}

function refreshView(): void {
  window.location.reload()
}

onMounted(() => {
  sidebarCollapsed.value = localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true' || window.innerWidth < 960
  void loadDynamicMenu()
})
</script>

<template>
  <el-container class="app-layout">
    <el-aside
      :width="sidebarWidth"
      class="app-layout__aside"
      :class="{ 'app-layout__aside--collapsed': sidebarCollapsed }"
      v-loading="menuLoading"
    >
      <div class="app-layout__brand-panel">
        <div class="app-layout__brand-mark">◇</div>
        <div v-if="!sidebarCollapsed" class="app-layout__brand-copy">
          <strong>VANTARIS™</strong>
          <span>AI Operations Platform</span>
        </div>
        <el-button
          class="app-layout__collapse-button"
          size="small"
          plain
          :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
          @click="toggleSidebar"
        >
          {{ sidebarCollapsed ? '›' : '‹' }}
        </el-button>
      </div>

      <div class="app-layout__menu-scroll">
        <el-menu
          :default-active="activeMenuIndex"
          class="app-layout__menu"
          :collapse="sidebarCollapsed"
          @select="onMenuSelect"
        >
          <template v-for="item in menuItems" :key="item.id">
            <el-sub-menu v-if="item.children?.length" :index="item.id">
              <template #title>
                <span class="app-layout__menu-icon" :title="item.label">{{ item.icon ?? item.label.slice(0, 1) }}</span>
                <span>{{ item.label }}</span>
              </template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.id"
                :index="child.id"
                :title="child.label"
              >
                <span class="app-layout__menu-icon">{{ child.label.slice(0, 1) }}</span>
                <span>{{ child.label }}</span>
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="item.id" :title="item.label">
              <span class="app-layout__menu-icon">{{ item.icon ?? item.label.slice(0, 1) }}</span>
              <span>{{ item.label }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </div>
    </el-aside>

    <el-container class="app-layout__workspace">
      <el-header class="app-layout__header">
        <div class="app-layout__title-block">
          <h1>{{ pageTitle }}</h1>
          <p>{{ pageSubtitle }}</p>
        </div>

        <div class="app-layout__toolbar">
          <el-button class="shell-button" plain @click="refreshView">↻ Refresh</el-button>
          <el-button class="shell-button shell-button--live" plain @click="liveMode = !liveMode">
            ↻ {{ liveMode ? 'Live' : 'Paused' }}
          </el-button>
          <el-select v-model="refreshInterval" class="shell-select" size="default">
            <el-option label="30s" value="30s" />
            <el-option label="60s" value="60s" />
            <el-option label="5m" value="5m" />
          </el-select>
          <el-dropdown>
            <el-button class="shell-button" plain>⚙ System Administrator</el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>Profile</el-dropdown-item>
                <el-dropdown-item disabled>Authorization</el-dropdown-item>
                <el-dropdown-item disabled>System Information</el-dropdown-item>
                <el-dropdown-item divided @click="onLogout">Logout</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-layout__main">
        <div class="app-layout__content-scroll">
          <section v-if="activeL3Items.length" class="app-layout__l3-row" aria-label="L3 content navigation">
            <el-tag
              v-for="item in activeL3Items"
              :key="item.id"
              class="app-layout__l3-tab"
              :class="{ 'app-layout__l3-tab--active': activeL3Id === item.id }"
              :type="item.status === 'implemented' || item.status === 'mapped' ? 'success' : 'info'"
              effect="plain"
              @click="onL3Select(item.id)"
            >
              {{ item.label }}
            </el-tag>
            <span v-if="activeL3Label" class="app-layout__l3-current">Current: {{ activeL3Label }}</span>
          </section>
          <router-view :key="route.fullPath" />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-layout {
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
  background: #eaf2f6;
  color: #0f172a;
}

.app-layout__workspace {
  min-width: 0;
  height: 100vh;
  overflow: hidden;
  background: #eaf2f6;
}

.app-layout__header {
  height: 86px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 18px 24px;
  background: #eaf2f6;
  border-bottom: 1px solid #d5e2ea;
}

.app-layout__title-block h1 {
  margin: 0 0 4px;
  color: #0f172a;
  font-size: 25px;
  font-weight: 750;
  line-height: 1.12;
}

.app-layout__title-block p {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  font-weight: 650;
  letter-spacing: 0.035em;
}

.app-layout__toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  min-width: 0;
}

.shell-button {
  min-height: 36px;
  border-color: #cbd9e3;
  border-radius: 9px;
  color: #1f2937;
  font-weight: 700;
  background: #ffffff;
}

.shell-button--live {
  border-color: #8ce6d2;
  color: #08796d;
  background: #e9fbf7;
}

.shell-select {
  width: 128px;
}

.app-layout__aside {
  height: 100vh;
  overflow: hidden;
  background: #ffffff;
  border-right: 1px solid #d7e3ec;
  box-shadow: 10px 0 24px rgba(15, 23, 42, 0.04);
  transition: width 0.2s ease;
}

.app-layout__aside--collapsed {
  overflow-x: hidden;
}

.app-layout__brand-panel {
  height: 86px;
  min-height: 86px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 18px 16px;
  border-bottom: 1px solid #eef3f7;
}

.app-layout__brand-mark {
  width: 34px;
  min-width: 34px;
  height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #8ce6d2;
  border-radius: 12px;
  color: #08796d;
  background: #e9fbf7;
  font-size: 17px;
  font-weight: 750;
}

.app-layout__brand-copy {
  min-width: 0;
  flex: 1;
}

.app-layout__brand-copy strong {
  display: block;
  color: #0f172a;
  font-size: 18px;
  font-weight: 800;
  letter-spacing: 0.03em;
}

.app-layout__brand-copy span {
  display: block;
  color: #64748b;
  font-size: 12px;
  font-weight: 650;
}

.app-layout__collapse-button {
  width: 34px;
  height: 34px;
  border-color: #d5e2ea;
  border-radius: 10px;
  color: #0f766e;
  background: #fff;
  font-size: 20px;
  font-weight: 700;
}

.app-layout__menu-scroll {
  height: calc(100vh - 86px);
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 18px;
}

.app-layout__menu-scroll::-webkit-scrollbar,
.app-layout__content-scroll::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.app-layout__menu-scroll::-webkit-scrollbar-thumb,
.app-layout__content-scroll::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: #c7d6df;
}

.app-layout__menu {
  border-right: none;
  padding: 12px;
  background: transparent;
}

.app-layout__menu :deep(.el-sub-menu__title),
.app-layout__menu :deep(.el-menu-item) {
  height: 44px;
  margin: 4px 0;
  border-radius: 10px;
  color: #475569;
  font-size: 14px;
  font-weight: 500;
}

.app-layout__menu :deep(.el-sub-menu__title:hover),
.app-layout__menu :deep(.el-menu-item:hover) {
  background: #f0faf7;
  color: #0f766e;
}

.app-layout__menu :deep(.el-menu-item.is-active) {
  background: #e4f4f1;
  color: #08796d;
}

.app-layout__menu-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.35rem;
  min-width: 1.35rem;
  height: 1.35rem;
  margin-right: 0.55rem;
  border-radius: 8px;
  background: #edf7f5;
  color: #0f766e;
  font-size: 0.72rem;
  font-weight: 700;
}

.app-layout__aside--collapsed .app-layout__menu-icon {
  margin-right: 0;
}

.app-layout__main {
  height: calc(100vh - 86px);
  overflow: hidden;
  padding: 0;
  background: #eaf2f6;
}

.app-layout__content-scroll {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 18px 24px 28px;
}

.app-layout__l3-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px 14px;
  border: 1px solid #d7e3ec;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.app-layout__l3-tab {
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
}

.app-layout__l3-tab--active {
  border-color: #0f766e !important;
  background: #e4f4f1 !important;
  color: #08796d !important;
}

.app-layout__l3-current {
  display: inline-flex;
  align-items: center;
  margin-left: auto;
  color: #64748b;
  font-size: 12px;
  font-weight: 600;
}
</style>
