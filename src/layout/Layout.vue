<template>
  <el-container style="height:100vh;overflow:hidden">
    <!-- 左侧菜单（全屏时隐藏） -->
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
          :default-active="activeMenu"
          v-model:default-openeds="openedMenus"
          @select="handleMenuSelect"
          style="border-right:none"
      >
        <!-- 仪表盘子菜单 -->
        <el-sub-menu index="/">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>{{ $t('menu.dashboard') }}</span>
          </template>
          <el-menu-item index="/Factory">
            <span>Factory</span>
          </el-menu-item>
          <el-menu-item index="/Building">
            <span>Building</span>
          </el-menu-item>
          <el-menu-item index="/Airport">
            <span>Airport</span>
          </el-menu-item>
          <el-menu-item index="/Shopping">
            <span>Shopping</span>
          </el-menu-item>
          <el-menu-item index="/Hospital">
            <span>Hospital</span>
          </el-menu-item>
          <el-menu-item index="/Hotel">
            <span>Hotel</span>
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
<!--          <el-menu-item index="/device/energy">
            <span>Energy</span>
          </el-menu-item>-->
        </el-sub-menu>

        <!-- 一级菜单 -->

        <el-sub-menu index="/energy">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>{{ $t('menu.energy') }}</span>
          </template>
          <el-menu-item index="/energy/wind">
            <span>Wind Energy</span>
          </el-menu-item>
        </el-sub-menu>

<!--        <el-menu-item index="/energy">-->
<!--          <el-icon><DataAnalysis /></el-icon>-->
<!--          <span>{{ $t('menu.energy') }}</span>-->
<!--        </el-menu-item>-->


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
      <!-- 顶部栏（全屏时隐藏） -->
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
            <el-button size="small" @click="setLang('zh')" :type="locale === 'zh' ? 'primary' : ''">中文</el-button>
            <el-button size="small" @click="setLang('en')" :type="locale === 'en' ? 'primary' : ''">English</el-button>
          </el-button-group>
        </div>
      </el-header>

      <!-- 内容区域：使用 key 强制刷新，捕获错误 -->
      <el-main class="main-content" :style="{ padding: isFullscreen ? '0' : '0px' }">
        <div v-if="hasError" class="error-placeholder">
          <el-result icon="error" title="页面加载失败" :sub-title="errorMessage">
            <template #extra>
              <el-button type="primary" @click="reloadRoute">重新加载</el-button>
            </template>
          </el-result>
        </div>
        <router-view v-else :key="$route.fullPath" v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch, onErrorCaptured } from 'vue'
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

// 错误边界状态
const hasError = ref(false)
const errorMessage = ref('')

// 捕获子组件渲染错误，避免页面静默空白
onErrorCaptured((err, instance, info) => {
  console.error('组件渲染错误:', err, info)
  hasError.value = true
  errorMessage.value = err.message || '未知错误'
  return false // 阻止错误继续向上传播
})

// 重新加载当前路由（强制刷新）
const reloadRoute = async () => {
  hasError.value = false
  errorMessage.value = ''
  try {
    await router.replace({ path: route.fullPath })
  } catch (err) {
    console.error('重新加载失败:', err)
    ElMessage.error('重新加载失败，请刷新页面')
  }
}

// 高亮菜单项
const activeMenu = computed(() => route.path)

// 动态控制父菜单展开
const openedMenus = ref([])

const updateOpenedMenus = () => {
  const path = route.path
  if (path.startsWith('/device/')) {
    openedMenus.value = ['/device']
  } else {
    // 可根据需要添加其他父菜单，例如未来可能有的 '/report/xxx'
    openedMenus.value = []
  }
}

watch(() => route.path, updateOpenedMenus, { immediate: true })

// 手动处理菜单点击（避免 el-menu 的 router 模式不可控）
const handleMenuSelect = (index) => {
  if (index && index !== route.path) {
    router.push(index).catch(err => {
      if (err.name !== 'NavigationDuplicated') {
        console.error('路由跳转失败:', err)
        ElMessage.error(`页面跳转失败: ${err.message}`)
      }
    })
  }
}

// 语言切换
const setLang = (l) => {
  locale.value = l
}

// 菜单路径映射（用于全屏上下键切换）
const menuPaths = [
  '/Factory',
  '/Building',
  '/Airport',
  '/Shopping',
  '/Hospital',
  '/Hotel',
  '/device/hvac',
  '/device/sas',
  '/device/fas',
  '/device/lighting',
  '/device/plumbing',
  // '/device/energy',
  '/energy/wind',
  '/alarm',
  '/maintain',
  '/report',
  '/settings'
]

// 当前菜单名称映射
const currentMenuName = computed(() => {
  const map = {
    '/Factory': 'Dashboard - Factory',
    '/Building': 'Dashboard - Building',
    '/Airport': 'Dashboard - Airport',
    '/Shopping': 'Dashboard - Shopping',
    '/Hospital': 'Dashboard - Hospital',
    '/Hotel': 'Dashboard - Hotel',
    '/device/hvac': 'Device Management - HVAC',
    '/device/sas': 'Device Management - SAS',
    '/device/fas': 'Device Management - FAS',
    '/device/lighting': 'Device Management - Lighting',
    '/device/plumbing': 'Device Management - Plumbing',
    // '/device/energy': 'Device Management - Energy',
    '/energy/wind': 'Wind Energy Analysis',
    '/alarm': 'Alarm Center',
    '/maintain': 'Maintenance Management',
    '/report': 'Data Reports',
    '/settings': 'System Settings'
  }
  return map[route.path] || 'IBMS Platform'
})

// 全屏控制
const toggleFullScreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(() => {
      ElMessage.warning('全屏失败')
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
    router.push(menuPaths[prevIndex]).catch(err => {
      if (err.name !== 'NavigationDuplicated') console.error(err)
    })
  } else if (e.key === 'ArrowDown') {
    e.preventDefault()
    const nextIndex = currentIndex >= menuPaths.length - 1 ? 0 : currentIndex + 1
    router.push(menuPaths[nextIndex]).catch(err => {
      if (err.name !== 'NavigationDuplicated') console.error(err)
    })
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
.sidebar {
  background: #0a1629;
  transition: all 0.3s;
  overflow-x: hidden;
}

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

.main-content {
  background: #f5f7fa;
  overflow: auto;
  padding: 0 !important;
  position: relative;
}

.error-placeholder {
  padding: 40px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>