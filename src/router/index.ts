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
        component: () => import('../views/Factory.vue'),
        meta: { title: 'Factory Dashboard' }
      },
      {
        path: 'Building',
        name: 'Building',
        component: () => import('../views/Building.vue'),
        meta: { title: 'Building Dashboard' }
      },
      {
        path: 'Airport',
        name: 'Airport',
        component: () => import('../views/Airport.vue'),
        meta: { title: 'Airport Dashboard' }
      },
      {
        path: 'Shopping',
        name: 'Shopping',
        component: () => import('../views/Shopping.vue'),
        meta: { title: 'Shopping Dashboard' }
      },
      {
        path: 'Hospital',
        name: 'Hospital',
        component: () => import('../views/Hospital.vue'),
        meta: { title: 'Hospital Dashboard' }
      },
      {
        path: 'Hotel',
        name: 'Hotel',
        component: () => import('../views/Hotel.vue'),
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
            component: () => import('../views/DeviceHVAC.vue'),
            meta: { title: 'HVAC Management' }
          },
          {
            path: 'sas',
            name: 'DeviceSAS',
            component: () => import('../views/DeviceSAS.vue'),
            meta: { title: 'Security Access System' }
          },
          {
            path: 'fas',
            name: 'DeviceFAS',
            component: () => import('../views/DeviceFAS.vue'),
            meta: { title: 'Fire Alarm System' }
          },
          {
            path: 'lighting',
            name: 'DeviceLighting',
            component: () => import('../views/DeviceLighting.vue'),
            meta: { title: 'Lighting Control System' }
          },
          {
            path: 'plumbing',
            name: 'DevicePlumbing',
            component: () => import('../views/DevicePlumbing.vue'),
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
            component: () => import('../views/Wind.vue'),
            meta: { title: 'Wind Energy Analysis' }
          },
          {
            path: 'solar',
            name: 'Solar',
            component: () => import('../views/Solar.vue'),
            meta: { title: 'Solar Energy Analysis' }
          },
          {
            path: 'electricity',
            name: 'Electricity',
            component: () => import('../views/Electricity.vue'),
            meta: { title: 'Power Grid & Consumption' }
          },
          {
            path: 'waste',
            name: 'WasteToEnergy',
            component: () => import('../views/WasteToEnergy.vue'),
            meta: { title: 'Waste-to-Energy Recovery' }
          },
          {
            path: 'hydrogen',
            name: 'Hydrogen',
            component: () => import('../views/Hydrogen.vue'),
            meta: { title: 'Hydrogen Energy Production' }
          },
          {
            path: 'storage',
            name: 'Storage',
            component: () => import('../views/EnergyStorage.vue'),
            meta: { title: 'Energy Storage Systems' }
          },
          {
            path: 'geothermal',
            name: 'Geothermal',
            component: () => import('../views/Geothermal.vue'),
            meta: { title: 'Geothermal Energy' }
          }
        ]
      },
      {
        path: 'alarm',
        name: 'Alarm',
        component: () => import('../views/Alarm.vue'),
        meta: { title: 'Alarm Center' }
      },
      {
        path: 'maintain',
        name: 'Maintain',
        component: () => import('../views/Maintain.vue'),
        meta: { title: 'Maintenance Management' }
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/Report.vue'),
        meta: { title: 'Data Reports' }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('../views/Settings.vue'),
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