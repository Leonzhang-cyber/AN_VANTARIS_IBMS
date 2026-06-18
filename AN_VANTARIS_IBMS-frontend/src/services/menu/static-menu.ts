import type { AppMenuItem } from './types'

export const fallbackMenuItems: AppMenuItem[] = [
  { id: 'dashboard', label: 'Dashboard', path: '/dashboard', source: 'static' },
  {
    id: 'system',
    label: 'System',
    path: '/system',
    source: 'static',
    children: [
      { id: 'system-overview', label: 'System Overview', path: '/system', source: 'static' },
      {
        id: 'system-permissions',
        label: 'Permission Management',
        path: '/system/permissions',
        source: 'static',
      },
      {
        id: 'system-settings',
        label: 'System Settings',
        path: '/system/settings',
        source: 'static',
      },
      {
        id: 'system-audit-logs',
        label: 'Audit Logs',
        path: '/system/audit-logs',
        source: 'static',
      },
      {
        id: 'system-notification-settings',
        label: 'Notification Settings',
        path: '/system/notification-settings',
        source: 'static',
      },
      {
        id: 'system-integration-settings',
        label: 'Integration Settings',
        path: '/system/integration-settings',
        source: 'static',
      },
    ],
  },
  { id: 'iot', label: 'IoT', path: '/iot', source: 'static' },
  { id: 'did', label: 'DID', path: '/did', source: 'static' },
  { id: 'modeling', label: 'Modeling', path: '/modeling', source: 'static' },
  {
    id: 'uconsole',
    label: 'UConsole',
    path: '/console/operations',
    source: 'static',
    children: [
      {
        id: 'uconsole-platform-operations',
        label: 'Platform Operations',
        path: '/console/operations',
        source: 'static',
      },
    ],
  },
  {
    id: 'assets-topology',
    label: 'Assets & Topology',
    path: '/assets/topology',
    source: 'static',
    children: [
      {
        id: 'assets-topology-home',
        label: 'Asset Topology',
        path: '/assets/topology',
        source: 'static',
      },
    ],
  },
  {
    id: 'ucde',
    label: 'UCDE',
    path: '/ucde/evidence',
    source: 'static',
    children: [
      {
        id: 'ucde-evidence-center',
        label: 'Evidence Center',
        path: '/ucde/evidence',
        source: 'static',
      },
    ],
  },
  { id: 'reports', label: 'Reports', path: '/reports', source: 'static' },
]
