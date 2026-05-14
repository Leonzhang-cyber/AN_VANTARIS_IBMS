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
        :style="{ width: isFullscreen ? '0' : (isMobile ? '260px' : '260px'), opacity: isFullscreen ? 0 : 1 }"
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
            style="border-right:none;"
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
            <el-menu-item index="/device/area-topology">
              <span>Area Device Topology</span>
            </el-menu-item>
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


          <!-- 仪表盘子菜单 -->
          <el-sub-menu index="/property">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>Smart Property</span>
            </template>
            <el-menu-item index="/property/parking">
              <span>Parking Management</span>
            </el-menu-item>
            <el-menu-item index="/property/visitor">
              <span>Visitor Management</span>
            </el-menu-item>
            <el-menu-item index="/property/space">
              <span>Space Management</span>
            </el-menu-item>
            <el-menu-item index="/property/waste">
              <span>Waste Management</span>
            </el-menu-item>
          </el-sub-menu>

          <!-- 仪表盘子菜单 -->
          <el-sub-menu index="/blockchain">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>Blockchain Services</span>
            </template>
            <el-menu-item index="/blockchain/node">
              <span>Node Management</span>
            </el-menu-item>
            <el-menu-item index="/blockchain/web3">
              <span>Web3 Services</span>
            </el-menu-item>
            <el-menu-item index="/blockchain/did">
              <span>DID Management</span>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/alarm">
            <el-icon><Warning /></el-icon>
            <span>{{ $t('menu.alarm') }}</span>
          </el-menu-item>

          <!-- 仪表盘子菜单 -->
          <el-sub-menu index="/maintain">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>Maintenance</span>
            </template>
            <el-menu-item index="/maintain/predictive">
              <span>Predictive Maintenance</span>
            </el-menu-item>
          </el-sub-menu>

          <!-- 仪表盘子菜单 -->
          <el-sub-menu index="/carbon">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>Carbon Credit</span>
            </template>
            <el-menu-item index="/carbon/realtime">
              <span>Carbon Emission</span>
            </el-menu-item>
          </el-sub-menu>

          <!--          <el-menu-item index="/carbon">-->
          <!--            <el-icon><HelpFilled /></el-icon>-->
          <!--            <span>{{ $t('menu.carbon') }}</span>-->
          <!--          </el-menu-item>-->

          <!--          <el-menu-item index="/maintain">-->
          <!--            <el-icon><Tools /></el-icon>-->
          <!--            <span>{{ $t('menu.maintain') }}</span>-->
          <!--          </el-menu-item>-->

          <el-menu-item index="/report">
            <el-icon><Document /></el-icon>
            <span>Data Reports</span>
          </el-menu-item>

          <!-- 仪表盘子菜单 -->
          <el-sub-menu index="/support">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>System Support</span>
            </template>
            <el-menu-item index="/support/mobile">
              <span>Mobile Terminal</span>
            </el-menu-item>
            <el-menu-item index="/support/notify">
              <span>Multi‑dim Notification</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="/settings">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>System Settings</span>
            </template>
            <el-menu-item index="/settings/voice-cmd">
              <span>Voice Command Settings</span>
            </el-menu-item>
            <el-menu-item index="/settings/tts-rule">
              <span>TTS Broadcast Rules</span>
            </el-menu-item>
            <el-menu-item index="/settings/lang">
              <span>Multi‑language Pack</span>
            </el-menu-item>
            <el-menu-item index="/settings/voice-log">
              <span>Voice Training Logs</span>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>{{ $t('menu.settings') }}</span>
          </el-menu-item>
        </el-menu>
      </div>


      <!-- 版权固定底部 -->
      <div class="sidebar-footer">
        <span>© {{ new Date().getFullYear() }} AegisNexus All rights reserved.</span>
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

        <!-- 快捷控制按钮组（仅桌面端显示） -->
        <div class="header-controls" v-if="!isMobile">
          <!-- 开门控制 -->
          <el-dropdown trigger="click" @command="handleDoorOpen">
            <el-button size="small" type="success" :icon="Lock">
              开门控制
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="lobby">
                  <el-icon><OfficeBuilding /></el-icon>
                  大堂区域
                </el-dropdown-item>
                <el-dropdown-item command="parking">
                  <el-icon><Van /></el-icon>
                  停车场区域
                </el-dropdown-item>
                <el-dropdown-item command="office">
                  <el-icon><Grid /></el-icon>
                  办公区域
                </el-dropdown-item>
                <el-dropdown-item command="warehouse">
                  <el-icon><Box /></el-icon>
                  仓库区域
                </el-dropdown-item>
                <el-dropdown-item divided command="all">
                  <el-icon><Key /></el-icon>
                  全部开门
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- 灯光控制 -->
          <el-dropdown trigger="click" @command="handleLightControl">
            <el-button size="small" type="warning" :icon="Sunny">
              灯光控制
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="lobby-on">大堂 - 开灯</el-dropdown-item>
                <el-dropdown-item command="lobby-off">大堂 - 关灯</el-dropdown-item>
                <el-dropdown-item command="parking-on">停车场 - 开灯</el-dropdown-item>
                <el-dropdown-item command="parking-off">停车场 - 关灯</el-dropdown-item>
                <el-dropdown-item divided command="all-on">全部开灯</el-dropdown-item>
                <el-dropdown-item command="all-off">全部关灯</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- 空调控制 -->
          <el-dropdown trigger="click" @command="handleACControl">
            <el-button size="small" type="primary" :icon="ColdDrink">
              空调控制
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="temp-24">温度 24°C</el-dropdown-item>
                <el-dropdown-item command="temp-26">温度 26°C</el-dropdown-item>
                <el-dropdown-item command="temp-28">温度 28°C</el-dropdown-item>
                <el-dropdown-item divided command="mode-cool">制冷模式</el-dropdown-item>
                <el-dropdown-item command="mode-fan">送风模式</el-dropdown-item>
                <el-dropdown-item divided command="all-off">全部关闭</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- 场景模式 -->
          <el-dropdown trigger="click" @command="handleSceneMode">
            <el-button size="small" :icon="MagicStick">
              场景模式
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="work">工作模式</el-dropdown-item>
                <el-dropdown-item command="meeting">会议模式</el-dropdown-item>
                <el-dropdown-item command="rest">休息模式</el-dropdown-item>
                <el-dropdown-item command="energy">节能模式</el-dropdown-item>
                <el-dropdown-item divided command="security">安防模式</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <!-- 紧急按钮 -->
          <el-button size="small" type="danger" :icon="Bell" @click="handleEmergency">
            紧急处置
          </el-button>
        </div>

        <div class="header-tools">
          <!-- 新加坡时间 -->
          <div class="singapore-time" v-if="!isMobile">{{ mobileTimeDisplay }}</div>

          <!-- 全屏按钮 -->
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
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Box, Warning, Tools, Document, Setting, FullScreen, Menu,
  Lock, ArrowDown, OfficeBuilding, Van, Grid, Key,
  Sunny, ColdDrink, MagicStick, Bell
} from '@element-plus/icons-vue'
// 引入 store
import { useCounterStore } from '@/stores/counter.js'  // 或者使用 fullscreen store

const route = useRoute()
const router = useRouter()
const { locale } = useI18n()
const isFullscreen = ref(false)
const counterStore = useCounterStore()

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

// ============ 快捷控制方法 ============
// 开门控制
const handleDoorOpen = async (area) => {
  const areaNames = {
    lobby: '大堂区域',
    parking: '停车场区域',
    office: '办公区域',
    warehouse: '仓库区域',
    all: '所有区域'
  }

  try {
    await ElMessageBox.confirm(
        `确认打开 ${areaNames[area]} 的门禁？`,
        '开门确认',
        {
          confirmButtonText: '确认开门',
          cancelButtonText: '取消',
          type: 'warning',
        }
    )
    // 这里调用实际的开门 API
    ElMessage.success(`${areaNames[area]} 门禁已打开`)
    // await api.openDoor(area)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`开门失败: ${error.message}`)
    }
  }
}

// 灯光控制
const handleLightControl = (command) => {
  const commands = {
    'lobby-on': { area: '大堂', action: '开灯', status: 'on' },
    'lobby-off': { area: '大堂', action: '关灯', status: 'off' },
    'parking-on': { area: '停车场', action: '开灯', status: 'on' },
    'parking-off': { area: '停车场', action: '关灯', status: 'off' },
    'all-on': { area: '所有区域', action: '开灯', status: 'on' },
    'all-off': { area: '所有区域', action: '关灯', status: 'off' }
  }

  const cmd = commands[command]
  if (cmd) {
    // 这里调用实际的灯光控制 API
    ElMessage.success(`${cmd.area}${cmd.action}成功`)
    // await api.controlLight(cmd.area, cmd.status)
  }
}

// 空调控制
const handleACControl = (command) => {
  if (command.startsWith('temp-')) {
    const temp = command.split('-')[1]
    ElMessage.success(`空调温度已设置为 ${temp}°C`)
    // await api.setACTemperature(temp)
  } else if (command.startsWith('mode-')) {
    const modes = {
      'mode-cool': '制冷模式',
      'mode-fan': '送风模式'
    }
    ElMessage.success(`空调已切换为${modes[command]}`)
    // await api.setACMode(command)
  } else if (command === 'all-off') {
    ElMessage.success('所有空调已关闭')
    // await api.turnOffAllAC()
  }
}

// 场景模式
const handleSceneMode = async (mode) => {
  const modeNames = {
    work: { name: '工作模式', desc: '灯光100%, 空调24°C, 门禁正常' },
    meeting: { name: '会议模式', desc: '灯光80%, 空调26°C, 投影仪开启' },
    rest: { name: '休息模式', desc: '灯光50%, 空调28°C, 背景音乐' },
    energy: { name: '节能模式', desc: '灯光30%, 空调关闭, 设备休眠' },
    security: { name: '安防模式', desc: '灯光关闭, 门禁锁定, 监控全开' }
  }

  const modeInfo = modeNames[mode]
  if (modeInfo) {
    try {
      await ElMessageBox.confirm(
          `${modeInfo.name}: ${modeInfo.desc}`,
          '场景模式确认',
          {
            confirmButtonText: '启动',
            cancelButtonText: '取消',
            type: 'info',
          }
      )
      ElMessage.success(`已启动${modeInfo.name}`)
      // await api.activateScene(mode)
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('场景启动失败')
      }
    }
  }
}

// 紧急处置
const handleEmergency = async () => {
  try {
    await ElMessageBox.confirm(
        '确认启动紧急处置程序？\n这将立即锁定所有门禁并触发警报系统。',
        '紧急处置确认',
        {
          confirmButtonText: '确认启动',
          cancelButtonText: '取消',
          type: 'error',
          confirmButtonClass: 'el-button--danger',
        }
    )
    ElMessage({
      message: '紧急处置程序已启动！所有门禁已锁定，警报已触发',
      type: 'error',
      duration: 5000,
      showClose: true
    })
    // await api.emergencyLockdown()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('紧急处置启动失败')
    }
  }
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
  '/Factory','/Building','/Airport','/Shopping','/Hospital','/Hotel','/device/area-topology',
  '/device/hvac','/device/sas','/device/fas','/device/lighting','/device/plumbing',
  '/property/parking','/property/visitor','/property/space','/property/waste',
  '/blockchain/node','/blockchain/web3','/blockchain/did',
  '/maintain/predictive',
  '/energy/wind','/energy/solar','/energy/electricity','/energy/waste','/energy/hydrogen','/energy/storage','/energy/geothermal',
  '/carbon/realtime',
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
    '/device/area-topology': 'Device Management - Area Topology',
    '/device/hvac': 'Device Management - HVAC',
    '/device/sas': 'Device Management - SAS',
    '/device/fas': 'Device Management - FAS',
    '/device/lighting': 'Device Management - Lighting',
    '/device/plumbing': 'Device Management - Plumbing',

    '/property/parking': 'Property Management - Parking',
    '/property/visitor': 'Property Management - Visitor',
    '/property/space': 'Property Management - Space',
    '/property/waste': 'Property Management - Waste',

    '/energy/wind': 'Wind Energy Analysis',
    '/energy/solar': 'Solar Energy Analysis',
    '/energy/electricity': 'Power Grid & Consumption',
    '/energy/waste': 'Waste to Energy Recovery',
    '/energy/hydrogen': 'Hydrogen Energy Production',
    '/energy/storage': 'Energy Storage Systems',
    '/energy/geothermal': 'Geothermal Energy',

    '/maintain/predictive': 'Predictive Maintenance',

    '/blockchain/node': 'Blockchain - Node Management',
    '/blockchain/web3': 'Blockchain - Web3',
    '/blockchain/did': 'Blockchain - DID',

    '/carbon/realtime': 'Carbon Emission',
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
  const previousState = isFullscreen.value
  isFullscreen.value = !!document.fullscreenElement
  counterStore.setFullscreen(isFullscreen.value)
  // 增加这两行打印
  console.log(`[FullScreen] 状态变更: ${previousState ? '全屏' : '窗口模式'} -> ${isFullscreen.value ? '全屏' : '窗口模式'}`)
  console.log(`[FullScreen] 当前全屏元素:`,counterStore.isFullscreen)
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
  text-align: center;
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
  gap: 12px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

/* 快捷控制按钮组 */
.header-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: center;
  flex-wrap: nowrap;
  overflow: hidden;
}

.header-controls .el-button {
  white-space: nowrap;
  font-size: 13px;
  padding: 8px 12px;
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
  white-space: nowrap;
}

.header-tools {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-shrink: 0;
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

  .header-controls {
    display: none; /* 移动端隐藏快捷控制按钮 */
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
  .header-controls .el-button {
    font-size: 12px;
    padding: 6px 10px;
  }

  .singapore-time {
    font-size: 12px;
    padding: 4px 8px;
  }

  .header-title {
    font-size: 14px;
  }
}

/* 中等屏幕优化（1024-1280） */
@media (min-width: 1025px) and (max-width: 1280px) {
  .header-controls {
    gap: 6px;
  }

  .header-controls .el-button {
    font-size: 12px;
    padding: 7px 10px;
  }
}
</style>