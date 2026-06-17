import { createRouter, createWebHistory } from 'vue-router'
import { registerNavigationGuards } from './guards'
import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

registerNavigationGuards(router)

export default router
