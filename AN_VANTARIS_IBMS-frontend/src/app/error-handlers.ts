import type { Router } from 'vue-router'
import { setForbiddenHandler, setUnauthorizedHandler } from '@/services/api/request'
import { logoutLocal } from '@/services/auth/session'

export function handleUnauthorized(router: Router): void {
  logoutLocal()
  const redirect = router.currentRoute.value.fullPath
  router.push({
    path: '/login',
    query: redirect && redirect !== '/login' ? { redirect } : undefined,
  })
}

export function handleForbidden(router: Router): void {
  router.push({ path: '/403' })
}

/** Wire 401/403 API errors to router navigation — no backend calls */
export function bindApiAuthErrorHandlers(router: Router): void {
  setUnauthorizedHandler(() => {
    handleUnauthorized(router)
  })
  setForbiddenHandler(() => {
    handleForbidden(router)
  })
}
