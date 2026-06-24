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
const activeL3Items = computed(() => activeL2.value?.l3Items ?? [])
const sidebarWidth = computed(() => (sidebarCollapsed.value ? '72px' : '260px'))

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

onMounted(() => {
  sidebarCollapsed.value = localStorage.getItem(SIDEBAR_COLLAPSED_KEY) === 'true' || window.innerWidth < 960
  void loadDynamicMenu()
})
</script>

<template>
  <el-container class="app-layout">
    <el-header class="app-layout__header">
      <div class="app-layout__brand">VANTARIS IBMS</div>
      <el-button type="danger" plain size="small" @click="onLogout">
        Logout
      </el-button>
    </el-header>

    <el-container>
      <el-aside :width="sidebarWidth" class="app-layout__aside" :class="{ 'app-layout__aside--collapsed': sidebarCollapsed }" v-loading="menuLoading">
        <div class="app-layout__sidebar-tools">
          <el-button class="app-layout__collapse-button" size="small" text :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'" @click="toggleSidebar">
            {{ sidebarCollapsed ? '>>' : '<<' }}
          </el-button>
        </div>
        <p v-if="menuLoadError" class="menu-fallback-note">
          Using fallback menu
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
}

.app-layout__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #0f172a;
  color: #f8fafc;
}

.app-layout__brand {
  font-weight: 600;
  letter-spacing: 0.02em;
}

.app-layout__aside {
  background: #fff;
  border-right: 1px solid #e2e8f0;
  transition: width 0.2s ease;
}

.app-layout__aside--collapsed {
  overflow-x: hidden;
}

.app-layout__sidebar-tools {
  display: flex;
  justify-content: flex-end;
  padding: 0.5rem;
}

.app-layout__collapse-button {
  color: #334155;
}

.app-layout__menu-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  min-width: 1.25rem;
  height: 1.25rem;
  margin-right: 0.5rem;
  border-radius: 6px;
  background: #e8f5f0;
  color: #176255;
  font-size: 0.7rem;
  font-weight: 700;
}

.app-layout__menu {
  border-right: none;
}

.app-layout__main {
  background: #f8fafc;
}

.app-layout__l3-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  border: 1px solid #dce9e3;
  border-radius: 8px;
  background: #ffffff;
}

.app-layout__l3-tab {
  border-radius: 999px;
}

.menu-fallback-note {
  margin: 0.5rem 0.75rem 0;
  font-size: 0.75rem;
  color: #64748b;
}
</style>
