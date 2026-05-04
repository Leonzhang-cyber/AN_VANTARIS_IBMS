import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../layout/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'device', name: 'Device', component: () => import('../views/Device.vue') },
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