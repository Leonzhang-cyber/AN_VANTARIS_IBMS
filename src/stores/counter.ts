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

// ==================== Essential 基础版菜单 ====================
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
    title: 'Device Management',
    icon: 'Cpu',
    children: [
      { index: '/device/area-topology', title: 'Area Topology' },
      { index: '/device/protocol', title: 'Protocol Hub' },
      { index: '/device/cctv', title: 'CCTV' },
      { index: '/device/hvac', title: 'HVAC' },
      { index: '/device/access', title: 'Access Control' },
      { index: '/device/sas', title: 'Security System' },
      { index: '/device/fas', title: 'Fire Alarm' },
      { index: '/device/lighting', title: 'Lighting Control' },
      { index: '/device/plumbing', title: 'Plumbing' }
    ]
  },
  {
    index: '/administration',
    title: 'Administration',
    icon: 'Setting',
    children: [
      { index: '/administration/user-role', title: 'User & Role' },
      { index: '/administration/system-logs', title: 'System Logs' },
      { index: '/administration/multi-language', title: 'Multi-language' },
      { index: '/administration/theme', title: 'Theme & Language' },
      { index: '/administration/license', title: 'License & Upgrade' }
    ]
  }
]

// ==================== Professional 专业版菜单 ====================
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
    index: '/device',
    title: 'Device Management',
    icon: 'Cpu',
    children: [
      { index: '/device/area-topology', title: 'Area Topology' },
      { index: '/device/protocol', title: 'Protocol Hub' },
      { index: '/device/cctv', title: 'CCTV' },
      { index: '/device/hvac', title: 'HVAC' },
      { index: '/device/access', title: 'Access Control' },
      { index: '/device/sas', title: 'Security System' },
      { index: '/device/fas', title: 'Fire Alarm' },
      { index: '/device/lighting', title: 'Lighting Control' },
      { index: '/device/plumbing', title: 'Plumbing' }
    ]
  },
  {
    index: '/alarm',
    title: 'Alarm Center',
    icon: 'BellFilled',
    children: [
      { index: '/alarm/index', title: 'Alarm Center' },
      { index: '/alarm/notify', title: 'Multi-dim Notification' },
      { index: '/alarm/history', title: 'Alarm History' }
    ]
  },
  {
    index: '/maintain',
    title: 'Maintenance',
    icon: 'SetUp',
    children: [
      { index: '/maintain/predictive', title: 'Predictive Maintenance' },
      { index: '/maintain/inspection', title: 'Inspection Management' }
    ]
  },
  {
    index: '/property',
    title: 'Smart Facility',
    icon: 'SwitchFilled',
    children: [
      { index: '/property/visitor', title: 'Visitor Management' }
    ]
  },
  {
    index: '/report',
    title: 'Reports & Analytics',
    icon: 'Reading',
    children: [
      { index: '/report/data', title: 'Data Reports' },
      { index: '/report/device', title: 'Device Reports' },
      { index: '/report/maintenance', title: 'Maintenance Reports' }
    ]
  },
  {
    index: '/support',
    title: 'Mobile & API',
    icon: 'Platform',
    children: [
      { index: '/support/mobile', title: 'Mobile Terminal' },
      { index: '/support/api', title: 'API Management' }
    ]
  },
  {
    index: '/administration',
    title: 'Administration',
    icon: 'Setting',
    children: [
      { index: '/administration/user-role', title: 'User & Role' },
      { index: '/administration/system-logs', title: 'System Logs' },
      { index: '/administration/multi-language', title: 'Multi-language' },
      { index: '/administration/theme', title: 'Theme & Language' },
      { index: '/administration/license', title: 'License & Upgrade' }
    ]
  }
]

// ==================== Smart Campus 园区版菜单 ====================
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
    title: 'Multi-Site Management',
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
    title: 'Device Management',
    icon: 'Cpu',
    children: [
      { index: '/device/area-topology', title: 'Area Topology' },
      { index: '/device/protocol', title: 'Protocol Hub' },
      { index: '/device/cctv', title: 'CCTV' },
      { index: '/device/hvac', title: 'HVAC' },
      { index: '/device/access', title: 'Access Control' },
      { index: '/device/sas', title: 'Security System' },
      { index: '/device/fas', title: 'Fire Alarm' },
      { index: '/device/lighting', title: 'Lighting Control' },
      { index: '/device/plumbing', title: 'Plumbing' }
    ]
  },
  {
    index: '/alarm',
    title: 'Alarm Center',
    icon: 'BellFilled',
    children: [
      { index: '/alarm/index', title: 'Alarm Center' },
      { index: '/alarm/notify', title: 'Multi-dim Notification' },
      { index: '/alarm/rules', title: 'Alarm Rules' },
      { index: '/alarm/history', title: 'Alarm History' }
    ]
  },
  {
    index: '/maintain',
    title: 'Maintenance',
    icon: 'SetUp',
    children: [
      { index: '/maintain/predictive', title: 'Predictive Maintenance' },
      { index: '/maintain/inspection', title: 'Inspection Management' },
      { index: '/maintain/assets', title: 'Asset Management' }
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
      { index: '/energy/electricity', title: 'Electricity' },
      { index: '/energy/waste', title: 'Waste to Energy' },
      { index: '/energy/hydrogen', title: 'Hydrogen Energy' },
      { index: '/energy/storage', title: 'Energy Storage' },
      { index: '/energy/geothermal', title: 'Geothermal' },
      { index: '/energy/carbon', title: 'Carbon Emission' },
      { index: '/energy/savings', title: 'Energy Savings' }
    ]
  },
  {
    index: '/prediction',
    title: 'AI Prediction',
    icon: 'MagicStick',
    children: [
      { index: '/prediction/hvac', title: 'HVAC Prediction' },
      { index: '/prediction/lighting', title: 'Lighting Prediction' },
      { index: '/prediction/power-socket', title: 'Power Prediction' },
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
      { index: '/property/parking', title: 'Parking Management' },
      { index: '/property/visitor', title: 'Visitor Management' },
      { index: '/property/space', title: 'Space Management' },
      { index: '/property/waste', title: 'Waste Management' }
    ]
  },
  {
    index: '/report',
    title: 'Reports & Analytics',
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
    title: 'Mobile & API',
    icon: 'Platform',
    children: [
      { index: '/support/mobile', title: 'Mobile Terminal' },
      { index: '/support/api', title: 'API Management' }
    ]
  },
  {
    index: '/command-center',
    title: 'Command Center',
    icon: 'Monitor',
    children: [
      { index: '/command-center/dashboard', title: 'Command Dashboard' },
      { index: '/command-center/gis', title: 'GIS Map' }
    ]
  },
  {
    index: '/blockchain',
    title: 'Web3 & Blockchain',
    icon: 'Connection',
    children: [
      { index: '/blockchain/did', title: 'DID Management' },
      { index: '/blockchain/contracts', title: 'Smart Contracts' },
      { index: '/blockchain/anchoring', title: 'Blockchain Anchoring' },
      { index: '/blockchain/web3', title: 'Web3 Services' }
    ]
  },
  {
    index: '/administration',
    title: 'Administration',
    icon: 'Setting',
    children: [
      { index: '/administration/user-role', title: 'User & Role' },
      { index: '/administration/system-logs', title: 'System Logs' },
      { index: '/administration/multi-language', title: 'Multi-language' },
      { index: '/administration/theme', title: 'Theme & Language' },
      { index: '/administration/license', title: 'License & Upgrade' }
    ]
  }
]

// ==================== Enterprise AI 旗舰版菜单 ====================
const enterpriseAIMenu: MenuItem[] = [
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
    title: 'Multi-Site Management',
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
    title: 'Device Management',
    icon: 'Cpu',
    children: [
      { index: '/device/area-topology', title: 'Area Topology' },
      { index: '/device/protocol', title: 'Protocol Hub' },
      { index: '/device/cctv', title: 'CCTV' },
      { index: '/device/hvac', title: 'HVAC' },
      { index: '/device/access', title: 'Access Control' },
      { index: '/device/sas', title: 'Security System' },
      { index: '/device/fas', title: 'Fire Alarm' },
      { index: '/device/lighting', title: 'Lighting Control' },
      { index: '/device/plumbing', title: 'Plumbing' }
    ]
  },
  {
    index: '/alarm',
    title: 'Alarm Center',
    icon: 'BellFilled',
    children: [
      { index: '/alarm/index', title: 'Alarm Center' },
      { index: '/alarm/notify', title: 'Multi-dim Notification' },
      { index: '/alarm/rules', title: 'Alarm Rules' },
      { index: '/alarm/history', title: 'Alarm History' }
    ]
  },
  {
    index: '/maintain',
    title: 'Maintenance',
    icon: 'SetUp',
    children: [
      { index: '/maintain/predictive', title: 'Predictive Maintenance' },
      { index: '/maintain/inspection', title: 'Inspection Management' },
      { index: '/maintain/assets', title: 'Asset Management' }
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
      { index: '/energy/electricity', title: 'Electricity' },
      { index: '/energy/waste', title: 'Waste to Energy' },
      { index: '/energy/hydrogen', title: 'Hydrogen Energy' },
      { index: '/energy/storage', title: 'Energy Storage' },
      { index: '/energy/geothermal', title: 'Geothermal' },
      { index: '/energy/carbon', title: 'Carbon Emission' },
      { index: '/energy/savings', title: 'Energy Savings' }
    ]
  },
  {
    index: '/prediction',
    title: 'AI Prediction',
    icon: 'MagicStick',
    children: [
      { index: '/prediction/hvac', title: 'HVAC Prediction' },
      { index: '/prediction/lighting', title: 'Lighting Prediction' },
      { index: '/prediction/power-socket', title: 'Power Prediction' },
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
      { index: '/property/parking', title: 'Parking Management' },
      { index: '/property/visitor', title: 'Visitor Management' },
      { index: '/property/space', title: 'Space Management' },
      { index: '/property/waste', title: 'Waste Management' }
    ]
  },
  {
    index: '/report',
    title: 'Reports & Analytics',
    icon: 'Reading',
    children: [
      { index: '/report/data', title: 'Data Reports' },
      { index: '/report/energy', title: 'Energy Reports' },
      { index: '/report/device', title: 'Device Reports' },
      { index: '/report/maintenance', title: 'Maintenance Reports' },
      { index: '/report/carbon', title: 'Carbon Reports' },
      { index: '/report/bi', title: 'BI Analytics' }
    ]
  },
  {
    index: '/support',
    title: 'Mobile & API',
    icon: 'Platform',
    children: [
      { index: '/support/mobile', title: 'Mobile Terminal' },
      { index: '/support/api', title: 'API Management' }
    ]
  },
  {
    index: '/command-center',
    title: 'Command Center',
    icon: 'Monitor',
    children: [
      { index: '/command-center/dashboard', title: 'Command Dashboard' },
      { index: '/command-center/gis', title: 'GIS Map' },
      { index: '/command-center/large-screen', title: 'Large Screen Display' }
    ]
  },
  {
    index: '/ai-center',
    title: 'AI Intelligence Center',
    icon: 'Cpu',
    children: [
      { index: '/ai-center/insights', title: 'AI Insights' },
      { index: '/ai-center/anomaly', title: 'Anomaly Detection' },
      { index: '/ai-center/optimization', title: 'Energy Optimization' },
      { index: '/ai-center/forecast', title: 'Demand Forecast' },
      { index: '/ai-center/recommendations', title: 'Smart Recommendations' }
    ]
  },
  {
    index: '/video-ai',
    title: 'Video AI Analytics',
    icon: 'Camera',
    children: [
      { index: '/video-ai/analytics', title: 'Video Analytics' },
      { index: '/video-ai/recognition', title: 'Face Recognition' },
      { index: '/video-ai/behavior', title: 'Behavior Analysis' },
      { index: '/video-ai/traffic', title: 'Traffic Monitoring' },
      { index: '/video-ai/safety', title: 'Safety Detection' }
    ]
  },
  {
    index: '/digital-twin',
    title: 'Digital Twin',
    icon: 'Grid',
    children: [
      { index: '/digital-twin/model', title: '3D Model Viewer' },
      { index: '/digital-twin/simulation', title: 'Simulation' },
      { index: '/digital-twin/analytics', title: 'Twin Analytics' },
      { index: '/digital-twin/real-time', title: 'Real-time Sync' }
    ]
  },
  {
    index: '/blockchain',
    title: 'Web3 & Blockchain',
    icon: 'Connection',
    children: [
      { index: '/blockchain/did', title: 'DID Management' },
      { index: '/blockchain/contracts', title: 'Smart Contracts' },
      { index: '/blockchain/anchoring', title: 'Blockchain Anchoring' },
      { index: '/blockchain/web3', title: 'Web3 Services' },
      { index: '/blockchain/traceability', title: 'Traceability' }
    ]
  },
  {
    index: '/administration',
    title: 'Administration',
    icon: 'Setting',
    children: [
      { index: '/administration/user-role', title: 'User & Role' },
      { index: '/administration/system-logs', title: 'System Logs' },
      { index: '/administration/multi-language', title: 'Multi-language' },
      { index: '/administration/theme', title: 'Theme & Language' },
      { index: '/administration/license', title: 'License & Upgrade' }
    ]
  }
]

// ==================== Pinia Store ====================
export const useCounterStore = defineStore('counter', () => {
  // 原有状态
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

  // ========== 新增：菜单版本管理 ==========
  const menuVersion = ref<MenuVersion>('essential')

  // 根据版本获取菜单配置
  const menuConfig = computed(() => {
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
    // 保存到 localStorage，持久化用户选择
    localStorage.setItem('menuVersion', version)
  }

  // 初始化菜单版本（从 localStorage 读取）
  function initMenuVersion() {
    const saved = localStorage.getItem('menuVersion') as MenuVersion
    if (saved && (saved === 'essential' || saved === 'professional' || saved === 'smart-campus' || saved === 'enterprise-ai')) {
      menuVersion.value = saved
    }
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

  // 添加菜单项动态配置的方法
  function addMenuItem(parentIndex: string, newItem: MenuItem) {
    const findAndAdd = (items: MenuItem[], targetIndex: string): boolean => {
      for (let i = 0; i < items.length; i++) {
        if (items[i].index === targetIndex) {
          if (!items[i].children) items[i].children = []
          items[i].children!.push(newItem)
          return true
        }
        if (items[i].children && findAndAdd(items[i].children, targetIndex)) return true
      }
      return false
    }
    // 根据当前版本添加到对应的菜单
    switch (menuVersion.value) {
      case 'essential':
        findAndAdd(essentialMenu, parentIndex)
        break
      case 'professional':
        findAndAdd(professionalMenu, parentIndex)
        break
      case 'smart-campus':
        findAndAdd(smartCampusMenu, parentIndex)
        break
      case 'enterprise-ai':
        findAndAdd(enterpriseAIMenu, parentIndex)
        break
    }
  }

  function removeMenuItem(itemIndex: string) {
    const remove = (items: MenuItem[]): boolean => {
      for (let i = 0; i < items.length; i++) {
        if (items[i].index === itemIndex) {
          items.splice(i, 1)
          return true
        }
        if (items[i].children && remove(items[i].children)) return true
      }
      return false
    }
    switch (menuVersion.value) {
      case 'essential':
        remove(essentialMenu)
        break
      case 'professional':
        remove(professionalMenu)
        break
      case 'smart-campus':
        remove(smartCampusMenu)
        break
      case 'enterprise-ai':
        remove(enterpriseAIMenu)
        break
    }
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
    // 新增菜单相关
    menuConfig,
    menuVersion,
    setMenuVersion,
    initMenuVersion,
    currentVersionName,
    currentVersionFullName,
    currentVersionDesc,
    addMenuItem,
    removeMenuItem
  }
})