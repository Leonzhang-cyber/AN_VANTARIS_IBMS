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

const menuItems = ref<AppMenuItem[]>([...fallbackMenuItems])
const menuLoading = ref(true)
const menuLoadError = ref(false)

const activePath = computed(() => route.path)

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

onMounted(() => {
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
      <el-aside width="220px" class="app-layout__aside" v-loading="menuLoading">
        <p v-if="menuLoadError" class="menu-fallback-note">
          Using fallback menu
        </p>
        <el-menu
          :default-active="activePath"
          class="app-layout__menu"
          @select="onMenuSelect"
        >
          <template v-for="item in menuItems" :key="item.id">
            <el-sub-menu v-if="item.children?.length" :index="item.id">
              <template #title>{{ item.label }}</template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.id"
                :index="child.path"
              >
                {{ child.label }}
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item v-else :index="item.path">
              {{ item.label }}
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>

      <el-main class="app-layout__main">
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
}

.app-layout__menu {
  border-right: none;
}

.app-layout__main {
  background: #f8fafc;
}

.menu-fallback-note {
  margin: 0.5rem 0.75rem 0;
  font-size: 0.75rem;
  color: #64748b;
}
</style>
