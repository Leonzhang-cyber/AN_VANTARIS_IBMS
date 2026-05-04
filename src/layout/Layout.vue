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
        <el-menu-item index="/"><el-icon><Home-filled /></el-icon><span>{{ $t('dashboard') }}</span></el-menu-item>
        <el-menu-item index="/device"><el-icon><Box /></el-icon><span>{{ $t('device') }}</span></el-menu-item>
        <el-menu-item index="/energy"><el-icon><DataAnalysis /></el-icon><span>{{ $t('energy') }}</span></el-menu-item>
        <el-menu-item index="/alarm"><el-icon><Warning /></el-icon><span>{{ $t('alarm') }}</span></el-menu-item>
        <el-menu-item index="/maintain"><el-icon><Tools /></el-icon><span>{{ $t('maintain') }}</span></el-menu-item>
        <el-menu-item index="/report"><el-icon><Document /></el-icon><span>{{ $t('report') }}</span></el-menu-item>
        <el-menu-item index="/settings"><el-icon><Setting /></el-icon><span>{{ $t('settings') }}</span></el-menu-item>
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
          :style="{ padding: isFullscreen ? '0' : '20px' }"
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
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const route = useRoute()
const { locale } = useI18n()
const isFullscreen = ref(false)
const setLang = (l) => (locale.value = l)

const currentMenuName = computed(() => {
  const map = {
    '/': 'Dashboard',
    '/device': 'Device Management',
    '/energy': 'Energy Analysis',
    '/alarm': 'Alarm Center',
    '/maintain': 'Maintenance Management',
    '/report': 'Data Reports',
    '/settings': 'System Settings'
  }
  return map[route.path] || 'Dashboard'
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

onMounted(() => {
  document.addEventListener('fullscreenchange', onFullScreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', onFullScreenChange)
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

/* 全屏图标样式（可点击、友好、大区域） */
.fullscreen-icon {
  width: 32px;
  height: 32px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  //border-radius: 6px;
  //color: #333;
  transition: all 0.2s;
}

.fullscreen-icon:hover {
  //background-color: #f0f2f5;
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