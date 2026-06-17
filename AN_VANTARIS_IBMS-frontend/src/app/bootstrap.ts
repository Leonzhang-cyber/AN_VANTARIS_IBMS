import type { App } from 'vue'
import type { Router } from 'vue-router'
import { bindApiAuthErrorHandlers } from './error-handlers'

export function bootstrapApp(app: App, router: Router): void {
  bindApiAuthErrorHandlers(router)
  // Extension point: Pinia, i18n, Element Plus — FRONTEND-A5+
  void app
}
