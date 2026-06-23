import request from './request'

export type UhmiSectionKey =
  | 'HMI_OVERVIEW'
  | 'SYSTEM_HMI'
  | 'DEVICE_HMI'
  | 'ALARM_EVENT_HMI'
  | 'EDGE_LINK_DIAGNOSTICS'
  | 'EVIDENCE_REPORTS'

export interface UhmiMenuItem {
  key: UhmiSectionKey
  label: string
  route: string
}

export interface UhmiSectionPayload {
  platform: 'VANTARIS_ONE'
  capability: 'UHMI'
  definition: string
  placement: 'UConsole / UHMI Workspace'
  releaseScope: string
  sectionKey: UhmiSectionKey
  sectionLabel: string
  route: string
  method: 'GET'
  purpose: string
  dataFlow: string
  futureControlledActionPath: string
  futureControlledActionStatus: string
  forbiddenDirectPaths: string[]
  l3WorkspaceInsidePage: boolean
  readOnly: boolean
  runtimeActivation: boolean
  productionActivation: boolean
  controlActionsEnabled: boolean
  directDeviceControl: boolean
  directDatabaseWrite: boolean
  edgeCommandEnabled: boolean
  linkCommandEnabled: boolean
  nexusAiExecution: boolean
  bypassCode: boolean
  dbMigration: boolean
  installOrRollback: boolean
  futureControlledActionExecuted: boolean
  rows: Array<Record<string, string | boolean>>
}

export interface UhmiMenuIaPayload {
  platform: 'VANTARIS_ONE'
  capability: 'UHMI'
  placement: 'UConsole / UHMI Workspace'
  l1: string
  l2: string
  l3Policy: string
  menuItems: UhmiMenuItem[]
  productionLabelPolicy: string
  readOnly: boolean
  runtimeActivation: boolean
  productionActivation: boolean
  controlActionsEnabled: boolean
}

export interface UhmiHealthPayload {
  status: string
  moduleId: string
  moduleName: string
  placement: 'UConsole / UHMI Workspace'
  readOnlyFoundation: boolean
  uiSkeletonReady: boolean
  apiSkeletonReady: boolean
  menuItemCount: number
  readOnly: boolean
  runtimeActivation: boolean
  productionActivation: boolean
  controlActionsEnabled: boolean
}

export const uhmiSections: UhmiMenuItem[] = [
  { key: 'HMI_OVERVIEW', label: 'HMI Overview', route: '/one/uhmi/overview' },
  { key: 'SYSTEM_HMI', label: 'System HMI', route: '/one/uhmi/system' },
  { key: 'DEVICE_HMI', label: 'Device HMI', route: '/one/uhmi/device' },
  { key: 'ALARM_EVENT_HMI', label: 'Alarm & Event HMI', route: '/one/uhmi/alarms-events' },
  { key: 'EDGE_LINK_DIAGNOSTICS', label: 'EDGE / LINK Diagnostics', route: '/one/uhmi/edge-link-diagnostics' },
  { key: 'EVIDENCE_REPORTS', label: 'Evidence & Reports', route: '/one/uhmi/evidence-reports' },
]

export async function getUhmiHealth(): Promise<UhmiHealthPayload> {
  const response = await request.get<UhmiHealthPayload>('/v1/one/uhmi/health')
  return response.data
}

export async function getUhmiMenuIa(): Promise<UhmiMenuIaPayload> {
  const response = await request.get<UhmiMenuIaPayload>('/v1/one/uhmi/menu')
  return response.data
}

export async function getUhmiSection(sectionKey: UhmiSectionKey): Promise<UhmiSectionPayload> {
  const response = await request.get<UhmiSectionPayload>(`/v1/one/uhmi/sections/${sectionKey}`)
  return response.data
}

