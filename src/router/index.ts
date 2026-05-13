import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/Layout.vue'

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
        redirect: '/device/hvac',
        children: [
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
        path: 'alarm',
        name: 'Alarm',
        component: () => import('../views/Alarm/Alarm.vue'),
        meta: { title: 'Alarm Center' }
      },
      {
        path: 'maintain',
        name: 'Maintain',
        component: () => import('../views/Maintain/Maintain.vue'),
        meta: { title: 'Maintenance Management' }
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/Report/Report.vue'),
        meta: { title: 'Data Reports' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Setting/Settings.vue'),
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