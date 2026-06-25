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
const menuLoadError = ref(false)
const sidebarCollapsed = ref(false)
const liveMode = ref(true)
const refreshInterval = ref('30s')

const activePath = computed(() => route.path)
const activeL2 = computed(() => {
  for (const l1 of menuItems.value) {
    const children = l1.children ?? []
    const exact = children.find((child) => child.path === route.path)
    if (exact) {
      return exact
    }
  }
  return undefined
})
const activeL1 = computed(() => {
  for (const l1 of menuItems.value) {
    if (l1.path === route.path) {
      return l1
    }
    if ((l1.children ?? []).some((child) => child.path === route.path)) {
      return l1
    }
  }
  return undefined
})
const activeL3Items = computed(() => activeL2.value?.l3Items ?? [])
const sidebarWidth = computed(() => (sidebarCollapsed.value ? '76px' : '286px'))
const pageTitle = computed(() => activeL2.value?.label ?? activeL1.value?.label ?? String(route.meta.title ?? 'Operations Console'))
const pageSubtitle = computed(() => 'AI-Powered Operations Intelligence for Unified Building & Facility Systems')

async function loadDynamicMenu(): Promise<void> {
  menuLoading.value = true
  menuLoadError.value = false

  try {
    const response = await menuApi.getMenus()
    const normalized = normalizeBackendMenu(response)

    if (normalized.length > 0) {
      menuItems.value = normalized
      return
    }

    menuItems.value = [...fallbackMenuItems]
    menuLoadError.value = true
  } catch {
    menuItems.value = [...fallbackMenuItems]
    menuLoadError.value = true
  } finally {
    menuLoading.value = false
  }
}

function onMenuSelect(index: string): void {
  if (!index || index === '#') {
    return
  }
  router.push(index)
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
        <div class="app-layout__brand-mark">◈</div>
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

      <p v-if="menuLoadError && !sidebarCollapsed" class="menu-fallback-note">
        Local menu active
      </p>

      <el-menu
        :default-active="activePath"
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
              :index="child.path"
              :title="child.label"
            >
              <span class="app-layout__menu-icon">{{ child.label.slice(0, 1) }}</span>
              <span>{{ child.label }}</span>
            </el-menu-item>
          </el-sub-menu>
          <el-menu-item v-else :index="item.path" :title="item.label">
            <span class="app-layout__menu-icon">{{ item.icon ?? item.label.slice(0, 1) }}</span>
            <span>{{ item.label }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>

    <el-container class="app-layout__workspace">
      <el-header class="app-layout__header">
        <div class="app-layout__title-block">
          <p>{{ pageSubtitle }}</p>
          <h1>{{ pageTitle }}</h1>
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
        <section v-if="activeL3Items.length" class="app-layout__l3-row" aria-label="L3 content navigation">
          <el-tag
            v-for="item in activeL3Items"
            :key="item.id"
            class="app-layout__l3-tab"
            :type="item.status === 'implemented' || item.status === 'mapped' ? 'success' : 'info'"
            effect="plain"
          >
            {{ item.label }}
          </el-tag>
        </section>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: #eaf2f6;
  color: #101828;
}

.app-layout__workspace {
  min-width: 0;
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

.app-layout__title-block p {
  margin: 0 0 4px;
  color: #64748b;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.app-layout__title-block h1 {
  margin: 0;
  color: #0f172a;
  font-size: 25px;
  font-weight: 850;
  line-height: 1.15;
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
  font-weight: 800;
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
  background: #ffffff;
  border-right: 1px solid #d7e3ec;
  box-shadow: 10px 0 24px rgba(15, 23, 42, 0.04);
  transition: width 0.2s ease;
}

.app-layout__aside--collapsed {
  overflow-x: hidden;
}

.app-layout__brand-panel {
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
  font-size: 18px;
  font-weight: 900;
}

.app-layout__brand-copy {
  min-width: 0;
  flex: 1;
}

.app-layout__brand-copy strong {
  display: block;
  color: #0f172a;
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 0.03em;
}

.app-layout__brand-copy span {
  display: block;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.app-layout__collapse-button {
  width: 34px;
  height: 34px;
  border-color: #d5e2ea;
  border-radius: 10px;
  color: #0f766e;
  background: #fff;
  font-size: 20px;
  font-weight: 900;
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
  font-weight: 800;
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
  font-weight: 900;
}

.app-layout__aside--collapsed .app-layout__menu-icon {
  margin-right: 0;
}

.app-layout__main {
  min-height: calc(100vh - 86px);
  padding: 18px 24px 28px;
  background: #eaf2f6;
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
  font-weight: 800;
}

.menu-fallback-note {
  margin: 10px 18px 0;
  padding: 8px 10px;
  border: 1px solid #d7e3ec;
  border-radius: 10px;
  background: #f8fbfa;
  font-size: 12px;
  color: #64748b;
  font-weight: 700;
}
</style>
