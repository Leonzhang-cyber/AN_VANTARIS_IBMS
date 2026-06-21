import type { RouteRecordRaw } from 'vue-router'
import DashboardPlaceholder from '@/views/DashboardPlaceholder'
import ForbiddenPlaceholder from '@/views/ForbiddenPlaceholder'
import LoginView from '@/views/LoginView.vue'
import NotFoundPlaceholder from '@/views/NotFoundPlaceholder'
import AuditLogsView from '@/modules/system/AuditLogsView.vue'
import IntegrationSettingsView from '@/modules/system/IntegrationSettingsView.vue'
import NotificationSettingsView from '@/modules/system/NotificationSettingsView.vue'
import PermissionListView from '@/modules/system/PermissionListView.vue'
import PlatformOperationsDashboard from '@/modules/console/PlatformOperationsDashboard.vue'
import ReportsView from '@/modules/reports/ReportsView.vue'
import EvidenceCenter from '@/modules/ucde/EvidenceCenter.vue'
import AssetsTopology from '@/modules/assets/AssetsTopology.vue'
import UesgSustainability from '@/modules/uesg/UesgSustainability.vue'
import UmmsMaintenance from '@/modules/umms/UmmsMaintenance.vue'
import UmmsReadonlyOverview from '@/modules/umms/UmmsReadonlyOverview.vue'
import UedgeSetup from '@/modules/uedge/UedgeSetup.vue'
import UedgeDiagnostics from '@/modules/uedge/UedgeDiagnostics.vue'
import SystemOverviewView from '@/modules/system/SystemOverviewView.vue'
import SystemSettingsView from '@/modules/system/SystemSettingsView.vue'
import AirportGaReadonlyConsole from '@/modules/airport/AirportGaReadonlyConsole.vue'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    permissions?: string[]
    title?: string
    layout?: boolean
  }
}

export const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresAuth: false, title: 'Login', layout: false },
  },
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: DashboardPlaceholder,
    meta: { requiresAuth: true, title: 'Dashboard', layout: true },
  },
  {
    path: '/system',
    name: 'system',
    component: SystemOverviewView,
    meta: { requiresAuth: true, permissions: ['system:read'], title: 'System Administration', layout: true },
  },
  {
    path: '/system/settings',
    name: 'system-settings',
    component: SystemSettingsView,
    meta: { requiresAuth: true, permissions: ['system:read'], title: 'System Settings', layout: true },
  },
  {
    path: '/system/permissions',
    name: 'system-permissions',
    component: PermissionListView,
    meta: { requiresAuth: true, permissions: ['system:read'], title: 'Permission Management', layout: true },
  },
  {
    path: '/system/audit-logs',
    name: 'system-audit-logs',
    component: AuditLogsView,
    meta: { requiresAuth: true, permissions: ['audit:read'], title: 'Audit Logs', layout: true },
  },
  {
    path: '/system/notification-settings',
    name: 'system-notification-settings',
    component: NotificationSettingsView,
    meta: { requiresAuth: true, permissions: ['system:read'], title: 'Notification Settings', layout: true },
  },
  {
    path: '/system/integration-settings',
    name: 'system-integration-settings',
    component: IntegrationSettingsView,
    meta: { requiresAuth: true, permissions: ['system:read'], title: 'Integration Settings', layout: true },
  },
  {
    path: '/iot',
    name: 'iot',
    component: DashboardPlaceholder,
    meta: { requiresAuth: true, title: 'IoT', layout: true },
  },
  {
    path: '/did',
    name: 'did',
    component: DashboardPlaceholder,
    meta: { requiresAuth: true, title: 'DID', layout: true },
  },
  {
    path: '/modeling',
    name: 'modeling',
    component: DashboardPlaceholder,
    meta: { requiresAuth: true, title: 'Modeling', layout: true },
  },
  {
    path: '/console/operations',
    name: 'console-operations',
    component: PlatformOperationsDashboard,
    meta: { requiresAuth: true, title: 'Platform Operations', layout: true },
  },
  {
    path: '/reports',
    name: 'reports',
    component: ReportsView,
    meta: { requiresAuth: true, title: 'Reports', layout: true },
  },
  {
    path: '/ucde/evidence',
    name: 'ucde-evidence-center',
    component: EvidenceCenter,
    meta: { requiresAuth: true, title: 'UCDE Evidence Center', layout: true },
  },
  {
    path: '/assets/topology',
    name: 'assets-topology',
    component: AssetsTopology,
    meta: { requiresAuth: true, title: 'Assets & Topology', layout: true },
  },
  {
    path: '/uesg/sustainability',
    name: 'uesg-sustainability',
    component: UesgSustainability,
    meta: { requiresAuth: true, title: 'UESG Sustainability', layout: true },
  },
  {
    path: '/umms/maintenance',
    name: 'umms-maintenance',
    component: UmmsMaintenance,
    meta: { requiresAuth: true, title: 'UMMS Maintenance', layout: true },
  },
  {
    path: '/one/umms/overview',
    name: 'umms-readonly-overview',
    component: UmmsReadonlyOverview,
    meta: { requiresAuth: true, title: 'UMMS Read-only Overview', layout: true },
  },
  {
    path: '/uedge/setup',
    name: 'uedge-setup',
    component: UedgeSetup,
    meta: { requiresAuth: true, title: 'UEDGE Customer Setup', layout: true },
  },
  {
    path: '/uedge/diagnostics',
    name: 'uedge-diagnostics',
    component: UedgeDiagnostics,
    meta: { requiresAuth: true, title: 'UEDGE Engineer Diagnostics', layout: true },
  },
  {
    path: '/one/airport/overview',
    name: 'airport-ga-readonly-overview',
    component: AirportGaReadonlyConsole,
    meta: { requiresAuth: true, title: 'Airport Overview', layout: true },
  },
  {
    path: '/one/airport/systems-integration-health',
    name: 'airport-ga-readonly-systems-integration-health',
    component: AirportGaReadonlyConsole,
    meta: { requiresAuth: true, title: 'Airport Systems & Integration Health', layout: true },
  },
  {
    path: '/one/airport/assets-topology',
    name: 'airport-ga-readonly-assets-topology',
    component: AirportGaReadonlyConsole,
    meta: { requiresAuth: true, title: 'Airport Assets & Topology', layout: true },
  },
  {
    path: '/one/airport/alarms-events',
    name: 'airport-ga-readonly-alarms-events',
    component: AirportGaReadonlyConsole,
    meta: { requiresAuth: true, title: 'Airport Alarms & Events', layout: true },
  },
  {
    path: '/one/airport/fault-cases',
    name: 'airport-ga-readonly-fault-cases',
    component: AirportGaReadonlyConsole,
    meta: { requiresAuth: true, title: 'Airport Fault Cases', layout: true },
  },
  {
    path: '/one/airport/maintenance-work-orders',
    name: 'airport-ga-readonly-maintenance-work-orders',
    component: AirportGaReadonlyConsole,
    meta: { requiresAuth: true, title: 'Airport Maintenance Work Orders', layout: true },
  },
  {
    path: '/one/airport/evidence-investigation',
    name: 'airport-ga-readonly-evidence-investigation',
    component: AirportGaReadonlyConsole,
    meta: { requiresAuth: true, title: 'Airport Evidence & Investigation', layout: true },
  },
  {
    path: '/one/airport/reports',
    name: 'airport-ga-readonly-reports',
    component: AirportGaReadonlyConsole,
    meta: { requiresAuth: true, title: 'Airport Reports', layout: true },
  },
  {
    path: '/403',
    name: 'forbidden',
    component: ForbiddenPlaceholder,
    meta: { requiresAuth: false, title: 'Forbidden', layout: false },
  },
  {
    path: '/forbidden',
    redirect: '/403',
  },
  // TODO(FRONTEND-A8+): replace placeholders with module views
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundPlaceholder,
    meta: { requiresAuth: false, title: 'Not Found' },
  },
]
