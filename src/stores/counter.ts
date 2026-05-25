// src/stores/counter.ts
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 定义菜单项类型
interface MenuItem {
  index: string
  title: string
  icon?: string
  children?: MenuItem[]
}

// 定义菜单版本类型
type MenuVersion = 'essential' | 'professional' | 'smart-campus' | 'enterprise-ai'

// ==================== allMenu 全部菜单（作为基准参照） ====================
const allMenu: MenuItem[] = [
  {
    index: '/',
    title: 'Dashboard',
    icon: 'View'
  },
  {
    index: '/control',
    title: 'Quick Control',
    icon: 'Coordinate'
  },
  {
    index: '/sites',
    title: 'Sites',
    icon: 'Odometer',
    children: [
      { index: '/sites/Factory', title: 'Factory' },
      { index: '/sites/Building', title: 'Building' },
      { index: '/sites/Airport', title: 'Airport' },
      { index: '/sites/Shopping', title: 'Shopping Mall' },
      { index: '/sites/Hospital', title: 'Hospital' },
      { index: '/sites/Hotel', title: 'Hotel' }
    ]
  },
  {
    index: '/device',
    title: 'Device',
    icon: 'Cpu',
    children: [
      { index: '/device/area-topology', title: 'Area Topology' },
      { index: '/device/protocol', title: 'Protocol Hub' },
      { index: '/device/cctv', title: 'CCTV' },
      { index: '/device/hvac', title: 'HVAC' },
      { index: '/device/access', title: 'Access' },
      { index: '/device/sas', title: 'SAS (Security)' },
      { index: '/device/fas', title: 'FAS (Fire)' },
      { index: '/device/lighting', title: 'Lighting Control' },
      { index: '/device/plumbing', title: 'Plumbing' }
    ]
  },
  {
    index: '/energy',
    title: 'Energy & Carbon',
    icon: 'TrendCharts',
    children: [
      { index: '/energy/overview', title: 'Energy Overview' },
      { index: '/energy/wind', title: 'Wind Energy' },
      { index: '/energy/solar', title: 'Solar Energy' },
      { index: '/energy/electricity', title: 'Electricity Energy' },
      { index: '/energy/waste', title: 'Waste to Energy' },
      { index: '/energy/hydrogen', title: 'Hydrogen Energy' },
      { index: '/energy/storage', title: 'Energy Storage' },
      { index: '/energy/geothermal', title: 'Geothermal Energy' },
      { index: '/energy/carbon', title: 'Carbon Emission' },
      { index: '/energy/savings', title: 'Energy Savings' }
    ]
  },
  {
    index: '/prediction',
    title: 'Prediction',
    icon: 'MagicStick',
    children: [
      { index: '/prediction/hvac', title: 'HVAC Prediction' },
      { index: '/prediction/lighting', title: 'Lighting Prediction' },
      { index: '/prediction/power-socket', title: 'Power & Socket' },
      { index: '/prediction/ev-charging', title: 'EV Charging' },
      { index: '/prediction/renewable', title: 'Renewable Generation' },
      { index: '/prediction/storage', title: 'Storage Strategy' }
    ]
  },
  {
    index: '/property',
    title: 'Smart Facility',
    icon: 'SwitchFilled',
    children: [
      { index: '/property/parking', title: 'Parking' },
      { index: '/property/visitor', title: 'Visitor' },
      { index: '/property/space', title: 'Space' },
      { index: '/property/waste', title: 'Waste' }
    ]
  },
  {
    index: '/maintain',
    title: 'Maintenance',
    icon: 'SetUp',
    children: [
      { index: '/maintain/predictive', title: 'Predictive Maintenance' }
    ]
  },
  {
    index: '/alarm',
    title: 'Alarm Center',
    icon: 'BellFilled',
    children: [
      { index: '/alarm/index', title: 'Alarm Center' },
      { index: '/alarm/notify', title: 'Multi‑dim Notification' },
      { index: '/alarm/history', title: 'Alarm History' }
    ]
  },
  {
    index: '/blockchain',
    title: 'Integrations & Web3',
    icon: 'Connection',
    children: [
      { index: '/blockchain/did', title: 'DID' },
      { index: '/blockchain/contracts', title: 'Smart Contracts' },
      { index: '/blockchain/anchoring', title: 'Blockchain Anchoring' },
      { index: '/blockchain/api', title: 'API Management' },
      { index: '/blockchain/node', title: 'Node Management' },
      { index: '/blockchain/edge-nodes', title: 'Edge Nodes' },
      { index: '/blockchain/web3', title: 'Web3 Services' },
      { index: '/blockchain/introduction', title: 'Introduction' }
    ]
  },
  {
    index: '/report',
    title: 'Reports',
    icon: 'Reading',
    children: [
      { index: '/report/data', title: 'Data Reports' },
      { index: '/report/energy', title: 'Energy Reports' },
      { index: '/report/device', title: 'Device Reports' },
      { index: '/report/maintenance', title: 'Maintenance Reports' },
      { index: '/report/carbon', title: 'Carbon Reports' }
    ]
  },
  {
    index: '/support',
    title: 'Terminal',
    icon: 'Platform',
    children: [
      { index: '/support/mobile', title: 'Mobile Terminal' }
    ]
  },
  {
    index: '/settings',
    title: 'Voice & AI',
    icon: 'Mic',
    children: [
      { index: '/settings/voice-cmd', title: 'Voice Commands' },
      { index: '/settings/tts-rule', title: 'TTS Broadcast Rules' },
      { index: '/settings/voice-log', title: 'Voice Training Logs' },
      { index: '/settings/lang', title: 'Multi-language Pack' }
    ]
  },
  {
    index: '/administration',
    title: 'Administration',
    icon: 'Setting',
    children: [
      { index: '/administration/user', title: 'User Management' },
      { index: '/administration/role', title: 'Role Management' },
      { index: '/administration/permission', title: 'Permission Management' },
      { index: '/administration/system', title: 'System Configuration' },
      { index: '/administration/license', title: 'License Management' },
      { index: '/administration/edition', title: 'Edition Management' }
    ]
  }
]

// ==================== 各版本菜单配置 ====================

// Essential 基础版菜单
const essentialMenu: MenuItem[] = [
  {
    index: '/',
    title: 'Dashboard',
    icon: 'View'
  },
  {
    index: '/control',
    title: 'Quick Control',
    icon: 'Coordinate'
  },
  {
    index: '/device',
    title: 'Device',
    icon: 'Cpu',
    children: [
      { index: '/device/area-topology', title: 'Area Topology' },
      { index: '/device/protocol', title: 'Protocol Hub' },
      { index: '/device/cctv', title: 'CCTV' },
      { index: '/device/hvac', title: 'HVAC' },
      { index: '/device/access', title: 'Access' },
      { index: '/device/sas', title: 'SAS (Security)' },
      { index: '/device/fas', title: 'FAS (Fire)' },
      { index: '/device/lighting', title: 'Lighting Control' },
      { index: '/device/plumbing', title: 'Plumbing' }
    ]
  },
  {
    index: '/prediction',
    title: 'Prediction',
    icon: 'MagicStick',
    children: [
      { index: '/prediction/hvac', title: 'HVAC Prediction' },
      { index: '/prediction/lighting', title: 'Lighting Prediction' },
      { index: '/prediction/power-socket', title: 'Power & Socket' },
      { index: '/prediction/ev-charging', title: 'EV Charging' },
      { index: '/prediction/renewable', title: 'Renewable Generation' },
      { index: '/prediction/storage', title: 'Storage Strategy' }
    ]
  },
  {
    index: '/administration',
    title: 'Administration',
    icon: 'Setting',
    children: [
      { index: '/administration/user', title: 'User Management' },
      { index: '/administration/role', title: 'Role Management' },
      { index: '/administration/permission', title: 'Permission Management' },
      { index: '/administration/system', title: 'System Configuration' },
      { index: '/administration/license', title: 'License Management' },
      { index: '/administration/edition', title: 'Edition Management' }
    ]
  }
]

// Professional 专业版菜单
const professionalMenu: MenuItem[] = [
  {
    index: '/',
    title: 'Dashboard',
    icon: 'View'
  },
  {
    index: '/control',
    title: 'Quick Control',
    icon: 'Coordinate'
  },
  {
    index: '/sites',
    title: 'Sites',
    icon: 'Odometer',
    children: [
      { index: '/sites/Factory', title: 'Factory' },
      { index: '/sites/Building', title: 'Building' },
      { index: '/sites/Airport', title: 'Airport' },
      { index: '/sites/Shopping', title: 'Shopping Mall' },
      { index: '/sites/Hospital', title: 'Hospital' },
      { index: '/sites/Hotel', title: 'Hotel' }
    ]
  },
  {
    index: '/device',
    title: 'Device',
    icon: 'Cpu',
    children: [
      { index: '/device/area-topology', title: 'Area Topology' },
      { index: '/device/protocol', title: 'Protocol Hub' },
      { index: '/device/cctv', title: 'CCTV' },
      { index: '/device/hvac', title: 'HVAC' },
      { index: '/device/access', title: 'Access' },
      { index: '/device/sas', title: 'SAS (Security)' },
      { index: '/device/fas', title: 'FAS (Fire)' },
      { index: '/device/lighting', title: 'Lighting Control' },
      { index: '/device/plumbing', title: 'Plumbing' }
    ]
  },
  {
    index: '/energy',
    title: 'Energy & Carbon',
    icon: 'TrendCharts',
    children: [
      { index: '/energy/overview', title: 'Energy Overview' },
      { index: '/energy/wind', title: 'Wind Energy' },
      { index: '/energy/solar', title: 'Solar Energy' },
      { index: '/energy/electricity', title: 'Electricity Energy' },
      { index: '/energy/waste', title: 'Waste to Energy' },
      { index: '/energy/hydrogen', title: 'Hydrogen Energy' },
      { index: '/energy/storage', title: 'Energy Storage' },
      { index: '/energy/geothermal', title: 'Geothermal Energy' },
      { index: '/energy/carbon', title: 'Carbon Emission' },
      { index: '/energy/savings', title: 'Energy Savings' }
    ]
  },
  {
    index: '/prediction',
    title: 'Prediction',
    icon: 'MagicStick',
    children: [
      { index: '/prediction/hvac', title: 'HVAC Prediction' },
      { index: '/prediction/lighting', title: 'Lighting Prediction' },
      { index: '/prediction/power-socket', title: 'Power & Socket' },
      { index: '/prediction/ev-charging', title: 'EV Charging' },
      { index: '/prediction/renewable', title: 'Renewable Generation' },
      { index: '/prediction/storage', title: 'Storage Strategy' }
    ]
  },
  {
    index: '/administration',
    title: 'Administration',
    icon: 'Setting',
    children: [
      { index: '/administration/user', title: 'User Management' },
      { index: '/administration/role', title: 'Role Management' },
      { index: '/administration/permission', title: 'Permission Management' },
      { index: '/administration/system', title: 'System Configuration' },
      { index: '/administration/license', title: 'License Management' },
      { index: '/administration/edition', title: 'Edition Management' }
    ]
  }
]

// Smart Campus 园区版菜单
const smartCampusMenu: MenuItem[] = [
  {
    index: '/',
    title: 'Dashboard',
    icon: 'View'
  },
  {
    index: '/control',
    title: 'Quick Control',
    icon: 'Coordinate'
  },
  {
    index: '/sites',
    title: 'Sites',
    icon: 'Odometer',
    children: [
      { index: '/sites/Factory', title: 'Factory' },
      { index: '/sites/Building', title: 'Building' },
      { index: '/sites/Airport', title: 'Airport' },
      { index: '/sites/Shopping', title: 'Shopping Mall' },
      { index: '/sites/Hospital', title: 'Hospital' },
      { index: '/sites/Hotel', title: 'Hotel' }
    ]
  },
  {
    index: '/device',
    title: 'Device',
    icon: 'Cpu',
    children: [
      { index: '/device/area-topology', title: 'Area Topology' },
      { index: '/device/protocol', title: 'Protocol Hub' },
      { index: '/device/cctv', title: 'CCTV' },
      { index: '/device/hvac', title: 'HVAC' },
      { index: '/device/access', title: 'Access' },
      { index: '/device/sas', title: 'SAS (Security)' },
      { index: '/device/fas', title: 'FAS (Fire)' },
      { index: '/device/lighting', title: 'Lighting Control' },
      { index: '/device/plumbing', title: 'Plumbing' }
    ]
  },
  {
    index: '/energy',
    title: 'Energy & Carbon',
    icon: 'TrendCharts',
    children: [
      { index: '/energy/overview', title: 'Energy Overview' },
      { index: '/energy/wind', title: 'Wind Energy' },
      { index: '/energy/solar', title: 'Solar Energy' },
      { index: '/energy/electricity', title: 'Electricity Energy' },
      { index: '/energy/waste', title: 'Waste to Energy' },
      { index: '/energy/hydrogen', title: 'Hydrogen Energy' },
      { index: '/energy/storage', title: 'Energy Storage' },
      { index: '/energy/geothermal', title: 'Geothermal Energy' },
      { index: '/energy/carbon', title: 'Carbon Emission' },
      { index: '/energy/savings', title: 'Energy Savings' }
    ]
  },
  {
    index: '/prediction',
    title: 'Prediction',
    icon: 'MagicStick',
    children: [
      { index: '/prediction/hvac', title: 'HVAC Prediction' },
      { index: '/prediction/lighting', title: 'Lighting Prediction' },
      { index: '/prediction/power-socket', title: 'Power & Socket' },
      { index: '/prediction/ev-charging', title: 'EV Charging' },
      { index: '/prediction/renewable', title: 'Renewable Generation' },
      { index: '/prediction/storage', title: 'Storage Strategy' }
    ]
  },
  {
    index: '/property',
    title: 'Smart Facility',
    icon: 'SwitchFilled',
    children: [
      { index: '/property/parking', title: 'Parking' },
      { index: '/property/visitor', title: 'Visitor' },
      { index: '/property/space', title: 'Space' },
      { index: '/property/waste', title: 'Waste' }
    ]
  },
  {
    index: '/maintain',
    title: 'Maintenance',
    icon: 'SetUp',
    children: [
      { index: '/maintain/predictive', title: 'Predictive Maintenance' }
    ]
  },
  {
    index: '/alarm',
    title: 'Alarm Center',
    icon: 'BellFilled',
    children: [
      { index: '/alarm/index', title: 'Alarm Center' },
      { index: '/alarm/notify', title: 'Multi‑dim Notification' },
      { index: '/alarm/history', title: 'Alarm History' }
    ]
  },
  {
    index: '/report',
    title: 'Reports',
    icon: 'Reading',
    children: [
      { index: '/report/data', title: 'Data Reports' },
      { index: '/report/energy', title: 'Energy Reports' },
      { index: '/report/device', title: 'Device Reports' },
      { index: '/report/maintenance', title: 'Maintenance Reports' },
      { index: '/report/carbon', title: 'Carbon Reports' }
    ]
  },
  {
    index: '/administration',
    title: 'Administration',
    icon: 'Setting',
    children: [
      { index: '/administration/user', title: 'User Management' },
      { index: '/administration/role', title: 'Role Management' },
      { index: '/administration/permission', title: 'Permission Management' },
      { index: '/administration/system', title: 'System Configuration' },
      { index: '/administration/license', title: 'License Management' },
      { index: '/administration/edition', title: 'Edition Management' }
    ]
  }
]

// Enterprise AI 旗舰版菜单
const enterpriseAIMenu: MenuItem[] = JSON.parse(JSON.stringify(allMenu))

// ==================== Pinia Store ====================
export const useCounterStore = defineStore('counter', () => {
  // ========== 原有状态 ==========
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() {
    count.value++
  }

  // 全屏状态
  const isFullscreen = ref(false)
  function setFullscreen(value: boolean) {
    isFullscreen.value = value
  }

  // 节能模式状态
  const isEnergySavingActive = ref(true)
  function setEnergySavingActive(value: boolean) {
    isEnergySavingActive.value = value
  }
  function toggleEnergySaving() {
    isEnergySavingActive.value = !isEnergySavingActive.value
  }

  // 报告显示状态
  const showEnergyReport = ref(false)
  function setShowEnergyReport(value: boolean) {
    showEnergyReport.value = value
  }
  function toggleShowEnergyReport() {
    showEnergyReport.value = !showEnergyReport.value
  }

  // ========== 菜单版本管理 ==========
  const menuVersion = ref<MenuVersion>('essential')
  // 菜单配置版本号，用于强制刷新 computed
  const menuConfigVersion = ref(0)

  // 根据版本获取菜单配置
  const menuConfig = computed(() => {
    // 依赖版本号，确保每次更新都能重新计算
    menuConfigVersion.value
    switch (menuVersion.value) {
      case 'essential':
        return essentialMenu
      case 'professional':
        return professionalMenu
      case 'smart-campus':
        return smartCampusMenu
      case 'enterprise-ai':
        return enterpriseAIMenu
      default:
        return essentialMenu
    }
  })

  // 切换菜单版本
  function setMenuVersion(version: MenuVersion) {
    menuVersion.value = version
    localStorage.setItem('menuVersion', version)
    menuConfigVersion.value++
  }

  // 初始化菜单版本
  function initMenuVersion() {
    const saved = localStorage.getItem('menuVersion') as MenuVersion
    if (saved && (saved === 'essential' || saved === 'professional' || saved === 'smart-campus' || saved === 'enterprise-ai')) {
      menuVersion.value = saved
    }
    menuConfigVersion.value++
  }

  // 获取当前版本名称
  const currentVersionName = computed(() => {
    switch (menuVersion.value) {
      case 'essential': return 'Essential'
      case 'professional': return 'Professional'
      case 'smart-campus': return 'Smart Campus'
      case 'enterprise-ai': return 'Enterprise AI'
      default: return 'Essential'
    }
  })

  // 获取版本完整名称
  const currentVersionFullName = computed(() => {
    switch (menuVersion.value) {
      case 'essential': return 'Essential Version'
      case 'professional': return 'Professional Edition'
      case 'smart-campus': return 'Smart Campus Edition'
      case 'enterprise-ai': return 'Enterprise AI Flagship'
      default: return 'Essential Version'
    }
  })

  // 获取版本描述
  const currentVersionDesc = computed(() => {
    switch (menuVersion.value) {
      case 'essential': return 'Core device management & administration'
      case 'professional': return 'Alarm, maintenance, reports & API integration'
      case 'smart-campus': return 'Multi-site, energy, blockchain & command center'
      case 'enterprise-ai': return 'AI analytics, video intelligence & digital twin'
      default: return 'Core device management'
    }
  })

  // 更新某个版本的菜单
  function updateVersionMenu(version: MenuVersion, newMenu: MenuItem[]) {
    const newMenuCopy = JSON.parse(JSON.stringify(newMenu))
    switch (version) {
      case 'essential':
        essentialMenu.length = 0
        essentialMenu.push(...newMenuCopy)
        break
      case 'professional':
        professionalMenu.length = 0
        professionalMenu.push(...newMenuCopy)
        break
      case 'smart-campus':
        smartCampusMenu.length = 0
        smartCampusMenu.push(...newMenuCopy)
        break
      case 'enterprise-ai':
        enterpriseAIMenu.length = 0
        enterpriseAIMenu.push(...newMenuCopy)
        break
    }
    // 递增版本号，强制 menuConfig 重新计算
    menuConfigVersion.value++
  }

  // 获取某个版本的菜单
  function getVersionMenu(version: MenuVersion): MenuItem[] {
    switch (version) {
      case 'essential': return essentialMenu
      case 'professional': return professionalMenu
      case 'smart-campus': return smartCampusMenu
      case 'enterprise-ai': return enterpriseAIMenu
      default: return essentialMenu
    }
  }

  // 刷新当前菜单
  function refreshCurrentMenu() {
    menuConfigVersion.value++
  }

  return {
    // 原有
    count,
    doubleCount,
    increment,
    isFullscreen,
    setFullscreen,
    isEnergySavingActive,
    setEnergySavingActive,
    toggleEnergySaving,
    showEnergyReport,
    setShowEnergyReport,
    toggleShowEnergyReport,
    // 菜单相关
    allMenu,
    menuConfig,
    menuVersion,
    setMenuVersion,
    initMenuVersion,
    currentVersionName,
    currentVersionFullName,
    currentVersionDesc,
    // 供 Edition 页面使用
    updateVersionMenu,
    getVersionMenu,
    refreshCurrentMenu
  }
})