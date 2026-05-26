// src/stores/counter.ts
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

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

  // ========== 菜单配置（从后端API获取，不存缓存）==========
  const menuConfig = ref<any[]>([])
  const menuVersion = ref<string>('professional')
  const allVersions = ref<any[]>([])
  const isLoading = ref(false)

  // 设置菜单配置
  function setMenuConfig(config: any[]) {
    menuConfig.value = config
  }

  // 设置版本
  function setMenuVersion(version: string) {
    menuVersion.value = version
  }

  // 设置所有版本列表
  function setAllVersions(versions: any[]) {
    allVersions.value = versions
  }

  // 设置加载状态
  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  // 重置所有菜单数据
  function resetMenuData() {
    menuConfig.value = []
    menuVersion.value = 'professional'
    allVersions.value = []
    isLoading.value = false
  }

  // 获取当前版本名称
  const currentVersionName = computed(() => {
    const version = allVersions.value.find(v => v.version_code === menuVersion.value)
    return version?.version_name || 'Professional'
  })

  // 获取版本完整名称
  const currentVersionFullName = computed(() => {
    const version = allVersions.value.find(v => v.version_code === menuVersion.value)
    return version?.version_name || 'Professional Edition'
  })

  // 获取版本描述
  const currentVersionDesc = computed(() => {
    const version = allVersions.value.find(v => v.version_code === menuVersion.value)
    return version?.description || ''
  })

  // 获取当前版本图标
  const currentVersionIcon = computed(() => {
    const version = allVersions.value.find(v => v.version_code === menuVersion.value)
    return version?.icon || '📦'
  })

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
    // 菜单相关（从API获取）
    menuConfig,
    menuVersion,
    allVersions,
    isLoading,
    setMenuConfig,
    setMenuVersion,
    setAllVersions,
    setLoading,
    resetMenuData,
    currentVersionName,
    currentVersionFullName,
    currentVersionDesc,
    currentVersionIcon
  }
})





// const menuConfig = ref([
//   {
//     index: '/',
//     title: 'Dashboard',
//     icon: 'View'
//   },
//   {
//     index: '/control',
//     title: 'Quick Control',
//     icon: 'Coordinate'
//   },
//   {
//     index: '/sites',
//     title: 'Sites',
//     icon: 'Odometer',
//     children: [
//       { index: '/sites/Factory', title: 'Factory' },
//       { index: '/sites/Building', title: 'Building' },
//       { index: '/sites/Airport', title: 'Airport' },
//       { index: '/sites/Shopping', title: 'Shopping Mall' },
//       { index: '/sites/Hospital', title: 'Hospital' },
//       { index: '/sites/Hotel', title: 'Hotel' }
//     ]
//   },
//   {
//     index: '/device',
//     title: 'Device',
//     icon: 'Cpu',
//     children: [
//       { index: '/device/area-topology', title: 'Area Topology' },
//       { index: '/device/protocol', title: 'Protocol Hub' },
//       { index: '/device/cctv', title: 'CCTV' },
//       { index: '/device/hvac', title: 'HVAC' },
//       { index: '/device/access', title: 'Access' },
//       { index: '/device/sas', title: 'SAS (Security)' },
//       { index: '/device/fas', title: 'FAS (Fire)' },
//       { index: '/device/lighting', title: 'Lighting Control' },
//       { index: '/device/plumbing', title: 'Plumbing' }
//     ]
//   },
//   {
//     index: '/energy',
//     title: 'Energy & Carbon',
//     icon: 'TrendCharts',
//     children: [
//       { index: '/energy/overview', title: 'Energy Overview' },
//       { index: '/energy/wind', title: 'Wind Energy' },
//       { index: '/energy/solar', title: 'Solar Energy' },
//       { index: '/energy/electricity', title: 'Electricity Energy' },
//       { index: '/energy/waste', title: 'Waste to Energy' },
//       { index: '/energy/hydrogen', title: 'Hydrogen Energy' },
//       { index: '/energy/storage', title: 'Energy Storage' },
//       { index: '/energy/geothermal', title: 'Geothermal Energy' },
//       { index: '/energy/carbon', title: 'Carbon Emission' },
//       { index: '/energy/savings', title: 'Energy Savings' }
//     ]
//   },
//   {
//     index: '/prediction',
//     title: 'Prediction',
//     icon: 'MagicStick',
//     children: [
//       { index: '/prediction/hvac', title: 'HVAC Prediction' },
//       { index: '/prediction/lighting', title: 'Lighting Prediction' },
//       { index: '/prediction/power-socket', title: 'Power & Socket' },
//       { index: '/prediction/ev-charging', title: 'EV Charging' },
//       { index: '/prediction/renewable', title: 'Renewable Generation' },
//       { index: '/prediction/storage', title: 'Storage Strategy' }
//     ]
//   },
//   {
//     index: '/property',
//     title: 'Smart Facility',
//     icon: 'SwitchFilled',
//     children: [
//       { index: '/property/parking', title: 'Parking' },
//       { index: '/property/visitor', title: 'Visitor' },
//       { index: '/property/space', title: 'Space' },
//       { index: '/property/waste', title: 'Waste' }
//     ]
//   },
//   {
//     index: '/maintain',
//     title: 'Maintenance',
//     icon: 'SetUp',
//     children: [
//       { index: '/maintain/predictive', title: 'Predictive Maintenance' }
//     ]
//   },
//   {
//     index: '/alarm',
//     title: 'Alarm Center',
//     icon: 'BellFilled',
//     children: [
//       { index: '/alarm/index', title: 'Alarm Center' },
//       { index: '/alarm/notify', title: 'Multi‑dim Notification' },
//       { index: '/alarm/history', title: 'Alarm History' }
//     ]
//   },
//   {
//     index: '/blockchain',
//     title: 'Integrations & Web3',
//     icon: 'Connection',
//     children: [
//       { index: '/blockchain/did', title: 'DID' },
//       { index: '/blockchain/contracts', title: 'Smart Contracts' },
//       { index: '/blockchain/anchoring', title: 'Blockchain Anchoring' },
//       { index: '/blockchain/api', title: 'API Management' },
//       { index: '/blockchain/node', title: 'Node Management' },
//       { index: '/blockchain/edge-nodes', title: 'Edge Nodes' },
//       { index: '/blockchain/web3', title: 'Web3 Services' },
//       { index: '/blockchain/introduction', title: 'Introduction' }
//     ]
//   },
//   {
//     index: '/report',
//     title: 'Reports',
//     icon: 'Reading',
//     children: [
//       { index: '/report/data', title: 'Data Reports' },
//       { index: '/report/energy', title: 'Energy Reports' },
//       { index: '/report/device', title: 'Device Reports' },
//       { index: '/report/maintenance', title: 'Maintenance Reports' },
//       { index: '/report/carbon', title: 'Carbon Reports' }
//     ]
//   },
//   {
//     index: '/support',
//     title: 'Terminal',
//     icon: 'Platform',
//     children: [
//       { index: '/support/mobile', title: 'Mobile Terminal' }
//     ]
//   },
//   {
//     index: '/settings',
//     title: 'Voice & AI',
//     icon: 'Mic',
//     children: [
//       { index: '/settings/voice-cmd', title: 'Voice Commands' },
//       { index: '/settings/tts-rule', title: 'TTS Broadcast Rules' },
//       { index: '/settings/voice-log', title: 'Voice Training Logs' },
//       { index: '/settings/lang', title: 'Multi-language Pack' }
//     ]
//   },
//   {
//     index: '/administration',
//     title: 'Administration',
//     icon: 'Setting',
//     children: [
//       { index: '/administration/user', title: 'User Management' },
//       { index: '/administration/role', title: 'Role Management' },
//       { index: '/administration/permission', title: 'Permission Management' },
//       { index: '/administration/system', title: 'System Configuration' },
//       { index: '/administration/license', title: 'License Management' },
//       { index: '/administration/edition', title: 'Edition Management' }
//     ]
//   }
// ])