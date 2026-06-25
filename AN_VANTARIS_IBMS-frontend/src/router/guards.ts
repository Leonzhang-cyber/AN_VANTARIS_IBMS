import type { NavigationGuardNext, RouteLocationNormalized, Router } from 'vue-router'
import { isAuthenticated } from '@/services/auth/session'

/**
 * Placeholder permission check — backend remains source of truth.
 * TODO(FRONTEND-A3+): load permissions from session/store after login.
 */
export function hasPermission(_required: string[]): boolean {
  return true
}

function handleAuthGuard(
  to: RouteLocationNormalized,
  next: NavigationGuardNext,
): void {
  const requiresAuth = to.meta.requiresAuth === true

  if (requiresAuth && !isAuthenticated()) {
    next({
      path: '/login',
      query: { redirect: to.fullPath },
    })
    return
  }

  const permissions = to.meta.permissions
  if (Array.isArray(permissions) && permissions.length > 0 && !hasPermission(permissions)) {
    next({ path: '/403' })
    return
  }

  if (to.path === '/login' && isAuthenticated()) {
    next({ path: '/dashboard' })
    return
  }

  next()
}

export function registerNavigationGuards(router: Router): void {
  router.beforeEach((to, _from, next) => {
    if (to.meta.title && typeof document !== 'undefined') {
      document.title = `${String(to.meta.title)} — VANTARIS ONE`
    }
    handleAuthGuard(to, next)
  })
}
