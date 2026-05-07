import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        redirect: '/Factory',
        // component: () => import('../views/Factory.vue'),
        children: [
          { path: 'Factory', name: 'Factory', component: () => import('../views/Factory.vue') }
        ]
      },
      {
        path: 'device',
        name: 'Device',
        // component: () => import('../views/Device.vue'),
        redirect: '/device/hvac',  // 默认重定向到HVAC分类
        children: [
          { path: 'hvac', name: 'DeviceHVAC', component: () => import('../views/DeviceHVAC.vue') },
          { path: 'sas', name: 'DeviceSAS', component: () => import('../views/DeviceSAS.vue') },
          { path: 'fas', name: 'DeviceFAS', component: () => import('../views/DeviceFAS.vue') },
          { path: 'lighting', name: 'DeviceLighting', component: () => import('../views/DeviceLighting.vue') },
          { path: 'plumbing', name: 'DevicePlumbing', component: () => import('../views/DevicePlumbing.vue') },
          { path: 'energy', name: 'DeviceEnergy', component: () => import('../views/DeviceEnergy.vue') }
        ]
      },
      { path: 'energy', name: 'Energy', component: () => import('../views/Energy.vue') },
      { path: 'alarm', name: 'Alarm', component: () => import('../views/Alarm.vue') },
      { path: 'maintain', name: 'Maintain', component: () => import('../views/Maintain.vue') },
      { path: 'report', name: 'Report', component: () => import('../views/Report.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue') },
    ]
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})