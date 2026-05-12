<template>
  <el-container style="height:100vh;overflow:hidden">
    <!-- 移动端遮罩层 -->
    <transition name="fade">
      <div
          v-if="isMobile && mobileSidebarVisible"
          class="mobile-mask"
          @click="closeMobileSidebar"
      ></div>
    </transition>

    <!-- 左侧菜单（全屏时隐藏，移动端作为抽屉） -->
    <el-aside
        width="230px"
        class="sidebar"
        :class="{
        'mobile-sidebar': isMobile,
        'open': isMobile && mobileSidebarVisible
      }"
        :style="{ width: isFullscreen ? '0' : (isMobile ? '260px' : '230px'), opacity: isFullscreen ? 0 : 1 }"
    >
      <!-- Logo 固定 -->
      <div class="logo-box">
        <img src="/favicon.ico">
        <span class="logo-text">IBMS IoT Platform</span>
      </div>

      <!-- 菜单可滚动区域 -->
      <div class="menu-scroll">
        <el-menu
            :key="route.path"
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
          </el-sub-menu>

          <!-- 能源子菜单 -->
          <el-sub-menu index="/energy">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>{{ $t('menu.energy') }}</span>
            </template>
            <el-menu-item index="/energy/wind">
              <span>Wind Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/solar">
              <span>Solar Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/electricity">
              <span>Electricity Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/waste">
              <span>Waste to Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/hydrogen">
              <span>Hydrogen Energy</span>
            </el-menu-item>
            <el-menu-item index="/energy/storage">
              <span>Energy Storage</span>
            </el-menu-item>
            <el-menu-item index="/energy/geothermal">
              <span>Geothermal Energy</span>
            </el-menu-item>
          </el-sub-menu>

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
      </div>

      <!-- 版权固定底部 -->
      <div class="sidebar-footer">
        <span>© {{ new Date().getFullYear() }} AegisNexus</span>
      </div>
    </el-aside>

    <el-container>
      <!-- 顶部栏（全屏时隐藏 + 手机端直接隐藏） -->
      <el-header
          class="header-bar"
          :style="{ height: isFullscreen ? '0' : '60px', opacity: isFullscreen ? 0 : 1, padding: isFullscreen ? 0 : '0 20px' }"
      >
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <el-icon v-if="isMobile && !isFullscreen" class="menu-icon" @click="toggleMobileSidebar">
            <Menu />
          </el-icon>
          <div class="header-title">{{ currentMenuName }}</div>
        </div>
        <div class="header-tools" v-if="!isMobile">
          <!-- 新加坡时间（移动端简化显示） -->
          <div class="singapore-time">{{ mobileTimeDisplay }}</div>

          <!-- 全屏按钮：手机端不渲染 -->
          <el-tooltip :content="isFullscreen ? 'Exit Full Screen' : 'Full Screen'" placement="bottom" v-if="!isMobile">
            <FullScreen class="fullscreen-icon" @click="toggleFullScreen" />
          </el-tooltip>

          <el-button-group class="lang-group">
            <el-button size="small" @click="setLang('zh')" :type="locale === 'zh' ? 'primary' : ''">中文</el-button>
            <el-button size="small" @click="setLang('en')" :type="locale === 'en' ? 'primary' : ''">English</el-button>
          </el-button-group>
        </div>
      </el-header>

      <!-- 内容区域 -->
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
import { computed, ref, onMounted, onUnmounted, watch, onErrorCaptured, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  Box, Warning, Tools, Document, Setting, FullScreen, Menu
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const { locale } = useI18n()
const isFullscreen = ref(false)

// 移动端适配状态
const isMobile = ref(false)
const mobileSidebarVisible = ref(false)

// 错误边界状态
const hasError = ref(false)
const errorMessage = ref('')

// 新加坡时间
const singaporeTime = ref('')
let timeTimer = null

// 移动端简化时间显示（去除毫秒）
const mobileTimeDisplay = computed(() => {
  if (isMobile.value) {
    return singaporeTime.value.replace(/\.\d{3} SGT$/, ' SGT')
  }
  return singaporeTime.value
})

// 更新新加坡时间
const updateSingaporeTime = () => {
  const now = new Date()
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))

  const year = sgTime.getFullYear()
  const month = String(sgTime.getMonth() + 1).padStart(2, '0')
  const day = String(sgTime.getDate()).padStart(2, '0')
  const hours = String(sgTime.getHours()).padStart(2, '0')
  const minutes = String(sgTime.getMinutes()).padStart(2, '0')
  const seconds = String(sgTime.getSeconds()).padStart(2, '0')
  const ms = String(sgTime.getMilliseconds()).padStart(3, '0')

  singaporeTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${ms} SGT`
}

// 移动端方法
const toggleMobileSidebar = () => {
  mobileSidebarVisible.value = !mobileSidebarVisible.value
  if (mobileSidebarVisible.value) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

const closeMobileSidebar = () => {
  mobileSidebarVisible.value = false
  document.body.style.overflow = ''
}

// 检测屏幕宽度判断是否为移动端
const checkMobile = () => {
  const width = window.innerWidth
  isMobile.value = width < 768
  if (!isMobile.value) {
    closeMobileSidebar()
  }
}

// 捕获子组件渲染错误
onErrorCaptured((err, instance, info) => {
  console.error('组件渲染错误:', err, info)
  hasError.value = true
  errorMessage.value = err.message || '未知错误'
  return false
})

// 重新加载当前路由
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

const getParentMenuForPath = (path) => {
  const dashboardChildren = ['/Factory', '/Building', '/Airport', '/Shopping', '/Hospital', '/Hotel']
  if (dashboardChildren.includes(path)) return '/'
  if (path.startsWith('/device/')) return '/device'
  if (path.startsWith('/energy/')) return '/energy'
  return null
}

const updateOpenedMenus = async () => {
  const parent = getParentMenuForPath(route.path)
  openedMenus.value = []
  await nextTick()
  openedMenus.value = parent ? [parent] : []
}

watch(() => route.path, () => {
  updateOpenedMenus()
  // 移动端路由切换后关闭侧边栏
  if (isMobile.value) {
    closeMobileSidebar()
  }
}, { immediate: true })

const handleMenuSelect = (index) => {
  if (index && index !== route.path) {
    router.push(index).catch(err => {
      if (err.name !== 'NavigationDuplicated') {
        console.error('路由跳转失败:', err)
        ElMessage.error(`页面跳转失败: ${err.message}`)
      }
    })
  }
  // 移动端点击菜单后关闭侧边栏
  if (isMobile.value) {
    closeMobileSidebar()
  }
}

const setLang = (l) => {
  locale.value = l
}

const menuPaths = [
  '/Factory','/Building','/Airport','/Shopping','/Hospital','/Hotel',
  '/device/hvac','/device/sas','/device/fas','/device/lighting','/device/plumbing',
  '/energy/wind','/energy/solar','/energy/electricity','/energy/waste','/energy/hydrogen','/energy/storage','/energy/geothermal',
  '/alarm','/maintain','/report','/settings'
]

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
    '/energy/wind': 'Wind Energy Analysis',
    '/energy/solar': 'Solar Energy Analysis',
    '/energy/electricity': 'Power Grid & Consumption',
    '/energy/waste': 'Waste to Energy Recovery',
    '/energy/hydrogen': 'Hydrogen Energy Production',
    '/energy/storage': 'Energy Storage Systems',
    '/energy/geothermal': 'Geothermal Energy',
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
      ElMessage.warning('全屏失败')
    })
  } else {
    document.exitFullscreen()
  }
}

const onFullScreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

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

// 监听窗口大小变化
let resizeTimer = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    checkMobile()
  }, 200)
}

onMounted(() => {
  updateSingaporeTime()
  timeTimer = setInterval(updateSingaporeTime, 1000)
  document.addEventListener('fullscreenchange', onFullScreenChange)
  window.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', handleResize)
  checkMobile()
})

onUnmounted(() => {
  clearInterval(timeTimer)
  document.removeEventListener('fullscreenchange', onFullScreenChange)
  window.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', handleResize)
  document.body.style.overflow = ''
})
</script>

<style scoped>
/* 侧边栏使用 flex 列布局 */
.sidebar {
  background: #0a1629;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.3s ease, width 0.3s, opacity 0.3s;
}

.logo-box {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  gap: 10px;
  font-weight: bold;
  flex-shrink: 0;
}

.logo-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 菜单滚动容器 */
.menu-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: thin;
  scrollbar-color: #409eff #1e2a3a;
}
.menu-scroll::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.menu-scroll::-webkit-scrollbar-track {
  background: #1e2a3a;
  border-radius: 6px;
}
.menu-scroll::-webkit-scrollbar-thumb {
  background: #409eff;
  border-radius: 6px;
}
.menu-scroll::-webkit-scrollbar-thumb:hover {
  background: #66b1ff;
}

/* 版权固定底部 */
.sidebar-footer {
  height: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #0a1629;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  color: #8899aa;
  font-size: 12px;
  letter-spacing: 0.5px;
  flex-shrink: 0;
  transition: all 0.3s;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #0a1629;
  border-bottom: 1px solid #0a1629;
  transition: all 0.3s;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.menu-icon {
  font-size: 20px;
  color: #fff;
  cursor: pointer;
  transition: color 0.2s;
}
.menu-icon:hover {
  color: #409eff;
}

.header-title {
  font-size: 16px;
  color: #fff;
  font-weight: 500;
}

.header-tools {
  display: flex;
  gap: 16px;
  align-items: center;
}

/* 新加坡时间样式 */
.singapore-time {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  font-size: 14px;
  color: #0ff;
  background: rgba(0, 255, 255, 0.1);
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid rgba(0, 255, 255, 0.3);
  white-space: nowrap;
}

.fullscreen-icon {
  width: 32px;
  height: 42px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: white;
  font-weight: bold;
}

.fullscreen-icon:hover {
  color: #409eff;
}

.main-content {
  background: #f5f7fa;
  overflow: hidden;
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

/* 移动端遮罩层 */
.mobile-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1999;
  backdrop-filter: blur(2px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 移动端侧边栏样式 */
@media (max-width: 767px) {
  .sidebar.mobile-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    width: 260px !important;
    z-index: 2000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    box-shadow: 2px 0 12px rgba(0, 0, 0, 0.3);
  }

  .sidebar.mobile-sidebar.open {
    transform: translateX(0);
  }

  .header-title {
    font-size: 14px;
    max-width: 150px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .singapore-time {
    font-size: 11px;
    padding: 2px 6px;
    white-space: nowrap;
  }

  .lang-group .el-button {
    padding: 5px 8px;
    font-size: 12px;
  }

  .header-tools {
    gap: 8px;
  }

  .fullscreen-icon {
    width: 28px;
    height: 36px;
  }

  .logo-text {
    font-size: 14px;
  }

  .menu-scroll {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .sidebar-footer {
    font-size: 10px;
    height: 36px;
  }
}

/* 平板竖屏适配 */
@media (min-width: 768px) and (max-width: 1024px) {
  .singapore-time {
    font-size: 12px;
    padding: 4px 8px;
  }

  .header-title {
    font-size: 14px;
  }
}
</style>