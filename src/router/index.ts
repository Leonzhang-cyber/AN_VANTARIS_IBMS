import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/layout/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/Factory',  // 直接重定向，不要嵌套 children 的重定向
    children: [
      {
        path: 'Factory',
        name: 'Factory',
        component: () => import('../views/Dashboard/Factory.vue'),
        meta: { title: 'Factory Dashboard' }
      },
      {
        path: 'Building',
        name: 'Building',
        component: () => import('../views/Dashboard/Building.vue'),
        meta: { title: 'Building Dashboard' }
      },
      {
        path: 'Airport',
        name: 'Airport',
        component: () => import('../views/Dashboard/Airport.vue'),
        meta: { title: 'Airport Dashboard' }
      },
      {
        path: 'Shopping',
        name: 'Shopping',
        component: () => import('../views/Dashboard/Shopping.vue'),
        meta: { title: 'Shopping Dashboard' }
      },
      {
        path: 'Hospital',
        name: 'Hospital',
        component: () => import('../views/Dashboard/Hospital.vue'),
        meta: { title: 'Hospital Dashboard' }
      },
      {
        path: 'Hotel',
        name: 'Hotel',
        component: () => import('../views/Dashboard/Hotel.vue'),
        meta: { title: 'Hotel Dashboard' }
      },
      {
        path: 'device',
        name: 'Device',
        redirect: '/device/area-topology',
        children: [
          {
            path: 'area-topology',
            name: 'AreaTopology',
            component: () => import('../views/Device/AreaTopology.vue'),
            meta: { title: 'Area Topology' }
          },
          {
            path: 'hvac',
            name: 'DeviceHVAC',
            component: () => import('../views/Device/DeviceHVAC.vue'),
            meta: { title: 'HVAC Management' }
          },
          {
            path: 'sas',
            name: 'DeviceSAS',
            component: () => import('../views/Device/DeviceSAS.vue'),
            meta: { title: 'Security Access System' }
          },
          {
            path: 'fas',
            name: 'DeviceFAS',
            component: () => import('../views/Device/DeviceFAS.vue'),
            meta: { title: 'Fire Alarm System' }
          },
          {
            path: 'lighting',
            name: 'DeviceLighting',
            component: () => import('../views/Device/DeviceLighting.vue'),
            meta: { title: 'Lighting Control System' }
          },
          {
            path: 'plumbing',
            name: 'DevicePlumbing',
            component: () => import('../views/Device/DevicePlumbing.vue'),
            meta: { title: 'Plumbing System' }
          }
        ]
      },
      {
        path: 'energy',
        name: 'Energy',
        redirect: '/energy/wind',
        children: [
          {
            path: 'wind',
            name: 'Wind',
            component: () => import('../views/Energy/Wind.vue'),
            meta: { title: 'Wind Energy Analysis' }
          },
          {
            path: 'solar',
            name: 'Solar',
            component: () => import('../views/Energy/Solar.vue'),
            meta: { title: 'Solar Energy Analysis' }
          },
          {
            path: 'electricity',
            name: 'Electricity',
            component: () => import('../views/Energy/Electricity.vue'),
            meta: { title: 'Power Grid & Consumption' }
          },
          {
            path: 'waste',
            name: 'WasteToEnergy',
            component: () => import('../views/Energy/WasteToEnergy.vue'),
            meta: { title: 'Waste-to-Energy Recovery' }
          },
          {
            path: 'hydrogen',
            name: 'Hydrogen',
            component: () => import('../views/Energy/Hydrogen.vue'),
            meta: { title: 'Hydrogen Energy Production' }
          },
          {
            path: 'storage',
            name: 'Storage',
            component: () => import('../views/Energy/EnergyStorage.vue'),
            meta: { title: 'Energy Storage Systems' }
          },
          {
            path: 'geothermal',
            name: 'Geothermal',
            component: () => import('../views/Energy/Geothermal.vue'),
            meta: { title: 'Geothermal Energy' }
          }
        ]
      },
      {
        path: 'property',
        name: 'Smart Property',
        redirect: '/property/parking',
        children: [
          {
            path: 'parking',
            name: 'Parking',
            component: () => import('../views/Property/Parking.vue'),
            meta: { title: 'Parking Management' }
          },
          {
            path: 'visitor',
            name: 'Visitor',
            component: () => import('../views/Property/Visitor.vue'),
            meta: { title: 'Visitor Management' }
          },
          {
            path: 'space',
            name: 'Space',
            component: () => import('../views/Property/Space.vue'),
            meta: { title: 'Space & Workspace Management' }
          },
          {
            path: 'waste',
            name: 'Waste',
            component: () => import('../views/Property/Waste.vue'),
            meta: { title: 'Waste Collection Management' }
          }
        ]
      },
      {
        path: 'blockchain',
        name: 'Blockchain Services',
        redirect: '/blockchain/node',
        children: [
          {
            path: 'node',
            name: 'NodeDetail',
            component: () => import('../views/Blockchain/NodeDetail.vue'),
            meta: { title: 'Node Management' }
          },
          {
            path: 'web3',
            name: 'Web3Services',
            component: () => import('../views/Blockchain/Web3Services.vue'),
            meta: { title: 'Web3 Services' }
          },
          {
            path: 'did',
            name: 'DIDManagement',
            component: () => import('../views/Blockchain/DIDManagement.vue'),
            meta: { title: 'DID Management' }
          },
          {
            path: 'introduction',
            name: 'Introduction',
            component: () => import('../views/Blockchain/Introduction.vue'),
            meta: { title: 'Web3 Introduction' }
          }
        ]
      },
      {
        path: 'alarm',
        name: 'Alarm Center',
        redirect: '/maintain/predictive',
        children: [
          {
            path: 'index',
            name: 'Alarm',
            component: () => import('../views/Alarm/Alarm.vue'),
            meta: { title: 'Alarm Center' }
          },
          {
            path: 'notify',
            name: 'Notify',
            component: () => import('../views/Alarm/Notification.vue'),
            meta: { title: 'Multi‑dim Notification' }
          }
        ]
      },
      {
        path: 'maintain',
        name: 'Maintenance Management',
        redirect: '/maintain/predictive',
        children: [
          {
            path: 'predictive',
            name: 'Predictive',
            component: () => import('../views/Maintain/Predictive.vue'),
            meta: { title: 'Predictive Maintenance' }
          }
        ]
      },
      {
        path: 'carbon',
        name: 'Carbon Credit',
        redirect: '/carbon/realtime',
        children: [
          {
            path: 'realtime',
            name: 'Carbon Emission',
            component: () => import('../views/Carbon/Carbon.vue'),
            meta: { title: 'Carbon Emission' }
          }
        ]
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/Report/Report.vue'),
        meta: { title: 'Data Reports' }
      },

      {
        path: 'support',
        name: 'System Support',
        redirect: '/support/mobile',
        children: [
          {
            path: 'mobile',
            name: 'Mobile Terminal',
            component: () => import('../views/Support/Mobile.vue'),
            meta: { title: 'Mobile Terminal' }
          }
        ]
      },
      {
        path: 'settings',
        name: 'System Settings',
        redirect: '/settings/voice-cmd',
        children: [
          {
            path: 'voice-cmd',
            name: 'Voice Command Settings',
            component: () => import('../views/Settings/Voice.vue'),
            meta: { title: 'Voice Command Settings' }
          },
          {
            path: 'tts-rule',
            name: 'TTS Broadcast Rules',
            component: () => import('../views/Settings/Rules.vue'),
            meta: { title: 'TTS Broadcast Rulesn' }
          },
          {
            path: 'lang',
            name: 'Multi-language Pack',
            component: () => import('../views/Settings/Language.vue'),
            meta: { title: 'Multi-language Pack' }
          },
          {
            path: 'voice-log',
            name: 'Voice Training Logs',
            component: () => import('../views/Settings/VoiceTraining.vue'),
            meta: { title: 'Voice Training Logs' }
          }
        ]
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings/Settings.vue'),
        meta: { title: 'System Settings' }
      },
      // 404 处理 - 必须放在最后
      {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        redirect: '/Factory'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes,
  // 滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由错误处理
router.onError((error) => {
  console.error('Router error:', error)
  const pattern = /Loading chunk (\d)+ failed/g
  const isChunkLoadFailed = error.message.match(pattern)
  if (isChunkLoadFailed) {
    // 加载失败时刷新页面
    window.location.reload()
  }
})

// 导航守卫 - 处理加载失败
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  if (to.meta?.title) {
    document.title = `${to.meta.title} - IBMS IoT Platform`
  } else {
    document.title = 'IBMS IoT Platform'
  }

  next()
})

// 路由完成后处理
router.afterEach((to, from, failure) => {
  if (failure) {
    console.warn('Navigation failed:', failure)
  }
})

export default router