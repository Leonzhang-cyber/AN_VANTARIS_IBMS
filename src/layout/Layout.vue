<template>
  <el-container style="height:100vh;overflow:hidden">
    <!-- 左侧菜单（全屏隐藏） -->
    <el-aside
        width="230px"
        class="sidebar"
        :style="{ width: isFullscreen ? '0' : '230px', opacity: isFullscreen ? 0 : 1 }"
    >
      <div class="logo-box">
        <el-icon size="26" color="#409eff" class="logo-icon"><Home-filled /></el-icon>
        IBMS IoT Platform
      </div>
      <el-menu
          background-color="#0a1629"
          text-color="#e5eaf3"
          active-text-color="#409eff"
          :default-active="$route.path"
          router
          style="border-right:none"
      >
        <el-sub-menu index="/">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>{{ $t('menu.dashboard') }}</span>
          </template>
          <el-menu-item index="/Factory">
            <span>Factory</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 设备管理（带子菜单） -->
        <el-sub-menu index="/device">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>{{ $t('menu.device') }}</span>
          </template>
          <el-menu-item index="/device/hvac">
            <span>HVAC</span>
          </el-menu-item>
          <el-menu-item index="/device/sas">
            <span>SAS (Security)</span>
          </el-menu-item>
          <el-menu-item index="/device/fas">
            <span>FAS (Fire)</span>
          </el-menu-item>
          <el-menu-item index="/device/lighting">
            <span>Lighting Control</span>
          </el-menu-item>
          <el-menu-item index="/device/plumbing">
            <span>Plumbing</span>
          </el-menu-item>
          <el-menu-item index="/device/energy">
            <span>Energy</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/energy">
          <el-icon><DataAnalysis /></el-icon>
          <span>{{ $t('menu.energy') }}</span>
        </el-menu-item>
        <el-menu-item index="/alarm">
          <el-icon><Warning /></el-icon>
          <span>{{ $t('menu.alarm') }}</span>
        </el-menu-item>
        <el-menu-item index="/maintain">
          <el-icon><Tools /></el-icon>
          <span>{{ $t('menu.maintain') }}</span>
        </el-menu-item>
        <el-menu-item index="/report">
          <el-icon><Document /></el-icon>
          <span>{{ $t('menu.report') }}</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>{{ $t('menu.settings') }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部栏（全屏隐藏） -->
      <el-header
          class="header-bar"
          :style="{ height: isFullscreen ? '0' : '60px', opacity: isFullscreen ? 0 : 1, padding: isFullscreen ? 0 : '0 20px' }"
      >
        <div class="header-title">{{ currentMenuName }}</div>
        <div class="header-tools">
          <el-tooltip :content="isFullscreen ? 'Exit Full Screen' : 'Full Screen'" placement="bottom">
            <FullScreen class="fullscreen-icon" @click="toggleFullScreen" />
          </el-tooltip>

          <el-button-group>
            <el-button size="small" @click="setLang('zh')" :type="locale=='zh'?'primary':''">中文</el-button>
            <el-button size="small" @click="setLang('en')" :type="locale=='en'?'primary':''">English</el-button>
          </el-button-group>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <el-main
          class="main-content"
          :style="{ padding: isFullscreen ? '0' : '0px' }"
      >
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  HomeFilled, Box, DataAnalysis, Warning, Tools, Document, Setting, FullScreen
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { locale } = useI18n()
const isFullscreen = ref(false)
const setLang = (l) => (locale.value = l)

// 菜单路径（上下键切换顺序，包含所有子路由）
const menuPaths = [
  '/',
  '/device/hvac',
  '/device/sas',
  '/device/fas',
  '/device/lighting',
  '/device/plumbing',
  '/device/energy',
  '/energy',
  '/alarm',
  '/maintain',
  '/report',
  '/settings'
]

// 当前菜单名称映射（支持子路由）
const currentMenuName = computed(() => {
  const map = {
    // '/': 'Dashboard',
    '/Factory': 'Dashboard - Factory',
    '/device/hvac': 'Device Management - HVAC',
    '/device/sas': 'Device Management - SAS',
    '/device/fas': 'Device Management - FAS',
    '/device/lighting': 'Device Management - Lighting',
    '/device/plumbing': 'Device Management - Plumbing',
    '/device/energy': 'Device Management - Energy',
    '/energy': 'Energy Analysis',
    '/alarm': 'Alarm Center',
    '/maintain': 'Maintenance Management',
    '/report': 'Data Reports',
    '/settings': 'System Settings'
  }
  return map[route.path] || 'IBMS Platform'
})

const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {
      ElMessage.warning('Fullscreen failed')
    })
  } else {
    document.exitFullscreen()
  }
}

const onFullScreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

// 全屏模式下上下键切换路由
const onKeydown = (e) => {
  if (!isFullscreen.value) return

  const currentIndex = menuPaths.findIndex(p => p === route.path)
  if (currentIndex === -1) return

  if (e.key === 'ArrowUp') {
    e.preventDefault()
    const prevIndex = currentIndex <= 0 ? menuPaths.length - 1 : currentIndex - 1
    router.push(menuPaths[prevIndex])
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    const nextIndex = currentIndex >= menuPaths.length - 1 ? 0 : currentIndex + 1
    router.push(menuPaths[nextIndex])
  }
}

onMounted(() => {
  document.addEventListener('fullscreenchange', onFullScreenChange)
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', onFullScreenChange)
  window.removeEventListener('keydown', onKeydown)
})
</script>

<style scoped>
/* 侧边栏 */
.sidebar {
  background: #0a1629;
  transition: all 0.3s;
}

/* LOGO */
.logo-box {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.logo-icon {
  margin-right: 10px;
}

/* 顶部栏 */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.header-title {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.header-tools {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 全屏图标样式 */
.fullscreen-icon {
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.fullscreen-icon:hover {
  color: #409eff;
}

/* 内容区域 */
.main-content {
  background: #f5f7fa;
  overflow: auto;
  transition: all 0.3s;
}

/* 切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
}
</style>