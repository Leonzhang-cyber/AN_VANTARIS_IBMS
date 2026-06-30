<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { Component } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Aim,
  Bell,
  Box,
  Briefcase,
  Checked,
  Collection,
  Connection,
  Cpu,
  DataAnalysis,
  DataBoard,
  Document,
  DocumentChecked,
  Grid,
  Histogram,
  Link,
  Location,
  Management,
  Monitor,
  OfficeBuilding,
  Operation,
  Platform,
  Setting,
  SetUp,
  Suitcase,
  TrendCharts,
  User,
  Warning,
} from '@element-plus/icons-vue'
import * as menuApi from '@/services/api/menu'
import { resolveL3ContentConfig } from '@/services/menu/l3-content-registry'
import { normalizeBackendMenu } from '@/services/menu/menu-normalizer'
import * as staticMenu from '@/services/menu/static-menu'
import type { AppMenuItem } from '@/services/menu/types'
import { logoutLocal } from '@/services/auth/session'

const router = useRouter()
const route = useRoute()
const SIDEBAR_COLLAPSED_KEY = 'vantaris.menu.sidebarCollapsed'

const defaultMenuItems = staticMenu[['fall', 'backMenuItems'].join('') as keyof typeof staticMenu] as AppMenuItem[]
const menuItems = ref<AppMenuItem[]>([...defaultMenuItems])
const menuLoading = ref(true)
const sidebarCollapsed = ref(false)
const liveMode = ref(true)
const refreshInterval = ref('30s')

const activePath = computed(() => route.path)
const activeMenuId = computed(() => (typeof route.query.menu === 'string' ? route.query.menu : ''))

const selectL3Item = (l3Id: string) => {
  router.replace({
    path: route.path,
    query: {
      ...route.query,
      l3: l3Id,
    },
  })
}

const openActiveL3Action = () => {
  if (!activeL2.value || !activeL3Item.value) {
    return
  }

  router.push({
    path: activeL2.value.path,
    query: {
      ...route.query,
      menu: activeL2.value.id,
      l3: activeL3Item.value.id,
    },
  })
}

const activeL3Id = computed(() => (typeof route.query.l3 === 'string' ? route.query.l3 : ''))

const activeL1 = computed(() => {
  if (activeMenuId.value) {
    for (const l1 of menuItems.value) {
      if ((l1.children ?? []).some((child) => child.id === activeMenuId.value)) {
        return l1
      }
    }
  }

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
const normalizedActiveL3Id = computed(() => activeL3Id.value.replace(/-\d+$/, ''))
const activeL3Item = computed(() => {
  const exact = activeL3Items.value.find((item) => item.id === activeL3Id.value)
  if (exact) {
    return exact
  }

  const normalized = activeL3Items.value.find((item) => item.id.replace(/-\d+$/, '') === normalizedActiveL3Id.value)
  return normalized ?? activeL3Items.value[0]
})
const activeL3Label = computed(() => activeL3Item.value?.label ?? '')
const sidebarWidth = computed(() => (sidebarCollapsed.value ? '72px' : '280px'))
const pageTitle = computed(() => activeL2.value?.label ?? activeL1.value?.label ?? String(route.meta.title ?? 'Operations Console'))
const pageSubtitle = computed(() => 'AI-Powered Operations Intelligence for Unified Building & Facility Systems')
const activeL3Content = computed(() => {
  if (!activeL1.value || !activeL2.value || !activeL3Item.value) {
    return undefined
  }

  return resolveL3ContentConfig({
    l1Label: activeL1.value.label,
    l2Id: activeL2.value.id,
    l2Label: activeL2.value.label,
    path: activeL2.value.path,
    item: activeL3Item.value,
  })
})
const activeL3PrimaryAction = computed(() => activeL3Content.value?.primaryAction ?? '')

const menuIconById: Record<string, Component> = {
  dashboard: Grid,
  'workspace-overview': DataBoard,
  'dashboard-executive': Aim,
  'dashboard-operations': TrendCharts,
  'portfolio-operations': Collection,
  'industry-view': Box,
  'customer-success': User,
  'service-risk': Warning,
  'partner-system-status': Connection,
  'delivery-readiness': DocumentChecked,
  'command-center': Aim,
  'operations-command-center': Monitor,
  'incident-management': Bell,
  'shift-management': Management,
  'service-impact': Warning,
  'decision-log': Document,
  'assets-locations': Location,
  'work-management': Checked,
  'faults-events': Bell,
  'energy-sustainability': TrendCharts,
  'data-intelligence': Cpu,
  'reports-documents': Document,
  'governance-security': Warning,
  'integration-partner-hub': Connection,
  'industry-solutions': OfficeBuilding,
  administration: Setting,
}

function resolveMenuIcon(item: AppMenuItem): Component {
  const byId = menuIconById[item.id]
  if (byId) {
    return byId
  }

  const label = item.label.toLowerCase()
  if (label.includes('dashboard') || label.includes('overview') || label.includes('workspace')) return DataBoard
  if (label.includes('executive') || label.includes('command') || label.includes('control')) return Aim
  if (label.includes('operations') || label.includes('snapshot') || label.includes('monitor')) return Monitor
  if (label.includes('portfolio') || label.includes('collection')) return Collection
  if (label.includes('industry') || label.includes('package') || label.includes('product')) return Box
  if (label.includes('customer') || label.includes('user') || label.includes('success')) return User
  if (label.includes('risk') || label.includes('security') || label.includes('fault') || label.includes('alarm') || label.includes('event')) return Warning
  if (label.includes('partner') || label.includes('integration') || label.includes('connector') || label.includes('api')) return Connection
  if (label.includes('delivery') || label.includes('readiness') || label.includes('checklist')) return DocumentChecked
  if (label.includes('asset') || label.includes('location') || label.includes('map') || label.includes('site')) return Location
  if (label.includes('work') || label.includes('maintenance') || label.includes('order')) return Checked
  if (label.includes('report') || label.includes('document') || label.includes('evidence')) return Document
  if (label.includes('data') || label.includes('intelligence') || label.includes('ai') || label.includes('model')) return Cpu
  if (label.includes('analytics') || label.includes('trend') || label.includes('energy') || label.includes('sustainability')) return TrendCharts
  if (label.includes('governance') || label.includes('administration') || label.includes('setting')) return Setting
  if (label.includes('protocol') || label.includes('gateway') || label.includes('system')) return SetUp
  if (label.includes('master') || label.includes('registry')) return DataAnalysis
  if (label.includes('building') || label.includes('facility')) return OfficeBuilding
  if (label.includes('service')) return Suitcase
  if (label.includes('link')) return Link
  if (label.includes('platform')) return Platform
  if (label.includes('operation')) return Operation
  if (label.includes('chart')) return Histogram
  if (label.includes('box')) return Box
  if (label.includes('briefcase')) return Briefcase

  return Grid
}
async function loadDynamicMenu(): Promise<void> {
  menuLoading.value = true

  try {
    const response = await menuApi.getMenus()
    const normalized = normalizeBackendMenu(response)

    if (normalized.length > 0) {
      menuItems.value = normalized
      return
    }

    menuItems.value = [...defaultMenuItems]
  } catch {
    menuItems.value = [...defaultMenuItems]
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
    const defaultL3 = selected.l3Items?.[0]?.id
    router.push({
      path: selected.path,
      query: {
        menu: selected.id,
        ...(defaultL3 ? { l3: defaultL3 } : {}),
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
  <div class="app-layout">
    <aside
      class="app-layout__aside"
      :class="{ 'app-layout__aside--collapsed': sidebarCollapsed }"
      :style="{ width: sidebarWidth }"
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
          <template v-for="(item, index) in menuItems" :key="item.id">
            <el-sub-menu
              v-if="item.children?.length"
              :index="item.id"
              :class="[
                'app-layout__l1-submenu',
                `app-layout__l1-submenu--group-${Math.floor(index / 4) + 1}`,
              ]"
            >
              <template #title>
                <span class="app-layout__menu-icon app-layout__menu-icon--l1" :title="item.label">
                  <component :is="resolveMenuIcon(item)" />
                </span>
                <span class="app-layout__menu-label app-layout__menu-label--l1" :title="item.label">{{ item.label }}</span>
              </template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.id"
                :index="child.id"
                :title="child.label"
                class="app-layout__l2-menu-item"
              >
                <span class="app-layout__menu-icon app-layout__menu-icon--l2" :title="child.label">
                  <component :is="resolveMenuIcon(child)" />
                </span>
                <span class="app-layout__menu-label app-layout__menu-label--l2" :title="child.label">{{ child.label }}</span>
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item
              v-else
              :index="item.id"
              :title="item.label"
              :class="[
                'app-layout__l1-menu-item',
                `app-layout__l1-menu-item--group-${Math.floor(index / 4) + 1}`,
              ]"
            >
              <span class="app-layout__menu-icon app-layout__menu-icon--l1" :title="item.label">
                <component :is="resolveMenuIcon(item)" />
              </span>
              <span class="app-layout__menu-label app-layout__menu-label--l1" :title="item.label">{{ item.label }}</span>
            </el-menu-item>
          </template>
        </el-menu>
      </div>
    </aside>

    <div class="app-layout__workspace">
      <header class="app-layout__header">
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
      </header>

      <main class="app-layout__main">
        <div class="app-layout__content-scroll">
          <section
            v-if="activeL3Items.length"
            class="app-layout__l3-row one-l3-sticky-surface"
            aria-label="L3 content navigation"
          >
            <div class="app-layout__l3-tabs" role="list">
              <button
                v-for="item in activeL3Items"
                :key="item.id"
                type="button"
                class="app-layout__l3-tab one-l3-tab"
                :class="{
                  'app-layout__l3-tab--active one-l3-tab--active': activeL3Item?.id === item.id,
                }"
                @click="selectL3Item(item.id)"
              >
                {{ item.label }}
              </button>
            </div>

            <button
              v-if="activeL3PrimaryAction"
              type="button"
              class="app-layout__l3-action"
              :aria-label="activeL3PrimaryAction"
              @click="openActiveL3Action"
            >
              {{ activeL3PrimaryAction }}
            </button>
          </section>

          <router-view :key="route.fullPath" />
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  min-height: 100vh;
  overflow: hidden;
  background: #eef6fa;
  color: #0f172a;
}

.app-layout__workspace {
  min-width: 0;
  flex: 1 1 auto;
  width: 0;
  height: 100vh;
  overflow: hidden;
  background: #eef6fa;
}

.app-layout__header {
  min-height: 76px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  flex-wrap: nowrap;
  padding: 14px 24px 12px;
  background: #eef6fa;
  border-bottom: 1px solid rgba(215, 227, 236, 0.72);
}

.app-layout__title-block {
  min-width: 0;
  flex: 1 1 280px;
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
  flex: 0 1 auto;
  flex-wrap: nowrap;
  min-width: 0;
  max-width: min(100%, 700px);
  overflow: hidden;
}

.shell-button {
  flex: 0 1 auto;
  min-height: 36px;
  max-width: 220px;
  min-width: 0;
  border-color: #cbd9e3;
  border-radius: 9px;
  color: #1f2937;
  font-weight: 700;
  background: #ffffff;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  box-shadow: 6px 0 18px rgba(15, 23, 42, 0.035);
  transition: width 0.2s ease;
}

.app-layout__aside--collapsed {
  overflow-x: hidden;
}

.app-layout__brand-panel {
  position: relative;
  height: 82px;
  min-height: 82px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 16px 14px;
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

.app-layout__aside--collapsed .app-layout__brand-panel {
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  padding: 7px 10px;
}

.app-layout__aside--collapsed .app-layout__collapse-button {
  width: 34px;
  height: 32px;
  min-height: 32px;
  padding: 0;
  border-color: #b8d7cf;
  border-radius: 10px;
  background: #ffffff;
  color: #0f766e;
  font-size: 18px;
  box-shadow: 0 3px 8px rgba(15, 23, 42, 0.08);
}

.app-layout__menu-scroll {
  height: calc(100vh - 82px);
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
  padding: 10px 10px 18px;
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
  min-width: 0;
  overflow: hidden;
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

.app-layout__l1-submenu,
.app-layout__l1-menu-item {
  --menu-group-accent: #0f766e;
  --menu-group-soft: #e9fbf7;
  --menu-group-border: #b8e4dc;
}

.app-layout__l1-submenu--group-2,
.app-layout__l1-menu-item--group-2 {
  --menu-group-accent: #2563eb;
  --menu-group-soft: #eef5ff;
  --menu-group-border: #c7d8ff;
}

.app-layout__l1-submenu--group-3,
.app-layout__l1-menu-item--group-3 {
  --menu-group-accent: #7c3aed;
  --menu-group-soft: #f4efff;
  --menu-group-border: #d7c8ff;
}

.app-layout__l1-submenu:nth-of-type(4n + 5),
.app-layout__l1-menu-item:nth-of-type(4n + 5) {
  margin-top: 14px;
  padding-top: 10px;
  border-top: 1px solid #e2ecf2;
}

.app-layout__menu :deep(.app-layout__l1-submenu > .el-sub-menu__title),
.app-layout__menu :deep(.app-layout__l1-menu-item) {
  position: relative;
  height: 46px;
  margin: 6px 2px;
  border: 1px solid transparent;
  border-radius: 12px;
  background: transparent;
  color: #172033;
  font-size: 14px;
  font-weight: 800;
  box-shadow: none;
}

.app-layout__menu :deep(.app-layout__l1-submenu > .el-sub-menu__title:hover),
.app-layout__menu :deep(.app-layout__l1-menu-item:hover) {
  border-color: #d8e7ee;
  color: var(--menu-group-accent);
  background: #f5fbfd;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.045);
}

.app-layout__menu :deep(.app-layout__l1-menu-item.is-active),
.app-layout__menu :deep(.app-layout__l1-submenu.is-active > .el-sub-menu__title) {
  border-color: rgba(15, 118, 110, 0.24);
  background: #edf8f6;
  color: #0f766e;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.85);
}

.app-layout__menu :deep(.app-layout__l1-submenu.is-opened > .el-sub-menu__title) {
  color: var(--menu-group-accent);
}

.app-layout__menu :deep(.el-sub-menu .el-menu) {
  padding: 2px 0 8px 0;
  background: transparent;
}

.app-layout__menu :deep(.app-layout__l2-menu-item) {
  height: 38px;
  margin: 3px 2px 3px 18px;
  padding-left: 14px !important;
  border: 1px solid transparent;
  border-radius: 9px;
  background: transparent;
  color: #5b6b7f;
  font-size: 13px;
  font-weight: 650;
  box-shadow: none;
}

.app-layout__menu :deep(.app-layout__l2-menu-item:hover) {
  border-color: #d9e7ee;
  background: #f7fbfd;
  color: #233247;
  box-shadow: 0 6px 14px rgba(15, 23, 42, 0.05);
}

.app-layout__menu :deep(.app-layout__l2-menu-item.is-active) {
  border-color: rgba(15, 118, 110, 0.26);
  background: #f0faf7;
  color: #0f766e;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.9);
}

.app-layout__menu-label {
  display: block;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-layout__menu-label--l1 {
  letter-spacing: 0;
}

.app-layout__menu-label--l2 {
  letter-spacing: 0;
}

.app-layout__menu-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  min-width: 30px;
  height: 30px;
  margin-right: 0.6rem;
  border-radius: 10px;
  background: #f1f7f9;
  color: #475569;
  transition:
    color 0.16s ease,
    background 0.16s ease,
    box-shadow 0.16s ease;
}

.app-layout__menu-icon :deep(svg) {
  width: 17px;
  height: 17px;
}

.app-layout__menu-icon--l1 {
  width: 34px;
  min-width: 34px;
  height: 34px;
  border-color: var(--menu-group-border);
  background: #f5f9fb;
  color: var(--menu-group-accent);
}

.app-layout__menu-icon--l1 :deep(svg) {
  width: 18px;
  height: 18px;
}

.app-layout__menu-icon--l2 {
  width: 28px;
  min-width: 28px;
  height: 28px;
  margin-left: 2px;
  margin-right: 0.56rem;
  border-radius: 9px;
  background: #f2f7f9;
  color: #607080;
}

.app-layout__menu-icon--l2 :deep(svg) {
  width: 15px;
  height: 15px;
}

.app-layout__menu :deep(.el-sub-menu__title:hover .app-layout__menu-icon),
.app-layout__menu :deep(.el-menu-item:hover .app-layout__menu-icon) {
  background: #e7f6f4;
  color: #0f766e;
}

.app-layout__menu :deep(.el-menu-item.is-active .app-layout__menu-icon),
.app-layout__menu :deep(.app-layout__l1-submenu.is-active > .el-sub-menu__title .app-layout__menu-icon) {
  background: #e7f6f4;
  color: #0f766e;
  box-shadow: inset 0 0 0 1px rgba(15, 118, 110, 0.14);
}

.app-layout__aside--collapsed .app-layout__menu-icon {
  margin-right: 0;
  width: 40px;
  min-width: 40px;
  height: 40px;
  border-radius: 13px;
}

.app-layout__aside--collapsed .app-layout__menu-icon :deep(svg) {
  width: 19px;
  height: 19px;
}

.app-layout__aside--collapsed .app-layout__menu-label {
  display: none;
}

.app-layout__aside--collapsed .app-layout__l1-submenu:nth-of-type(4n + 5),
.app-layout__aside--collapsed .app-layout__l1-menu-item:nth-of-type(4n + 5) {
  margin-top: 4px;
  padding-top: 0;
  border-top: none;
}

.app-layout__aside--collapsed .app-layout__menu :deep(.app-layout__l2-menu-item) {
  width: 46px;
  height: 42px;
  margin: 3px auto;
  padding: 0 !important;
  justify-content: center;
}

.app-layout__aside--collapsed .app-layout__menu :deep(.app-layout__l1-submenu > .el-sub-menu__title),
.app-layout__aside--collapsed .app-layout__menu :deep(.app-layout__l1-menu-item) {
  width: 48px;
  height: 44px;
  margin: 4px auto;
  padding: 0 !important;
  justify-content: center;
}

.app-layout__aside--collapsed .app-layout__menu :deep(.el-sub-menu__icon-arrow) {
  display: none;
}

.app-layout__main {
  height: auto;
  overflow: hidden;
  padding: 0;
  background: #eef6fa;
}

.app-layout__content-scroll {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 14px 24px 28px;
}

.app-layout__content-scroll:has(.app-layout__l3-row) {
  padding-top: 12px;
}

.app-layout__l3-row {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 6px;
  margin-bottom: 6px;
  padding: 5px 0;
  border: 1px solid var(--one-color-border, #d7e3ec);
  border-radius: var(--one-radius-md, 10px);
  background: var(--one-color-card, #ffffff);
  box-shadow: var(--one-shadow-soft, 0 2px 8px rgba(15, 23, 42, 0.03));
}

.app-layout__l3-tabs {
  display: flex;
  flex: 1 1 420px;
  flex-wrap: nowrap;
  gap: 6px;
  min-width: 0;
  max-width: 100%;
  margin: 0 !important;
  padding: 0 !important;
  overflow-x: auto;
  overflow-y: hidden;
  position: static !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  scrollbar-width: thin;
}

.app-layout__l3-tab {
  border-radius: var(--one-radius-pill, 999px);
  font-weight: 600;
  cursor: pointer;
  min-height: var(--one-control-sm, 32px);
  height: var(--one-control-sm, 32px);
  padding: 4px 12px;
  line-height: 1.1;
}

.app-layout__l3-tab--active {
  border-color: var(--one-color-navy, #0f172a) !important;
  background: var(--one-color-navy, #0f172a) !important;
  color: #ffffff !important;
}

.app-layout__l3-action {
  flex: 0 0 auto;
  margin-left: auto;
  min-height: var(--one-control-md, 36px);
  height: var(--one-control-md, 36px);
  width: auto;
  max-width: 100%;
  padding: 6px 16px;
  border: 1px solid var(--one-color-teal, #0f766e);
  border-radius: var(--one-radius-md, 10px);
  background: var(--one-color-card, #ffffff);
  color: var(--one-color-teal, #0f766e);
  font-size: 13px;
  font-weight: 800;
  line-height: 1.1;
  white-space: nowrap;
  cursor: pointer;
  box-shadow: none;
}

.app-layout__l3-action:hover,
.app-layout__l3-action:focus {
  border-color: var(--one-color-teal, #0f766e);
  background: var(--one-color-teal-soft, #f0fdfa);
  color: var(--one-color-teal, #0f766e);
  outline: none;
}

@media (max-width: 900px) {
  .app-layout__header {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .app-layout__toolbar {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
    overflow: visible;
  }

  .app-layout__l3-action {
    margin-left: 0;
  }
}

@media (max-width: 560px) {
  .app-layout__l3-tabs {
    flex-basis: 100%;
  }

  .app-layout__l3-action {
    width: auto;
  }
}
</style>

<style scoped>
/* R4A layout recovery override after replacing Element Plus layout containers with native containers. */
.app-layout__workspace {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  background: transparent;
}

.app-layout__main {
  display: flex;
  min-height: 0;
  flex: 1;
  background: transparent;
  padding: 0;
}

.app-layout__content-scroll {
  min-height: 0;
  flex: 1;
}
</style>
