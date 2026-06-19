import request from './request'

export interface UedgeHealth {
  status: string
  moduleId: string
  moduleName: string
  runtimeMode: string
  provider: string
  readOnly: boolean
  controlActionsEnabled: boolean
  runtimeLinked: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface UedgeSetupProfile {
  setupMode: string
  customerSetupReady: boolean
  oneClickSetupEnabled: boolean
  realDeviceRegistrationEnabled: boolean
  certificateImportEnabled: boolean
  tokenProvisioningEnabled: boolean
  networkConfigEnabled: boolean
  runtimeLinked: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  readOnly: boolean
  controlActionsEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
  lastUpdated: string
}

export interface UedgeSetupStep {
  stepId: string
  stepName: string
  stepOrder: number
  status: string
  required: boolean
  actionEnabled: boolean
  runtimeLinked: boolean
  notes: string
}

export interface UedgeDiagnosticsSummary {
  diagnosticsMode: string
  engineerDiagnosticsReady: boolean
  runtimeConnected: boolean
  connectorDiagnosticsEnabled: boolean
  protocolDiagnosticsEnabled: boolean
  mappingReviewEnabled: boolean
  bufferInspectionEnabled: boolean
  deliveryInspectionEnabled: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  runtimeLinked: boolean
  readOnly: boolean
  controlActionsEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
  lastUpdated: string
}

export interface UedgeDiagnosticsPanel {
  panelId: string
  panelName: string
  panelType: string
  status: string
  runtimeLinked: boolean
  actionEnabled: boolean
  summary: string
  limitations: string[]
}

export interface UedgeSummary {
  moduleId: string
  moduleName: string
  setupMode: string
  diagnosticsMode: string
  customerSetupReady: boolean
  engineerDiagnosticsReady: boolean
  setupStepCount: number
  diagnosticsPanelCount: number
  oneClickSetupEnabled: boolean
  runtimeConnected: boolean
  runtimeLinked: boolean
  readOnly: boolean
  controlActionsEnabled: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  certified: boolean
  iec62443Certified: boolean
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : []
}

function unwrapSuccessData<T>(body: unknown): T {
  const payload = asRecord(body)
  if ('data' in payload) {
    return payload.data as T
  }
  return body as T
}

function normalizeHealth(raw: unknown): UedgeHealth {
  const data = asRecord(raw)
  return {
    status: String(data.status ?? 'unknown'),
    moduleId: String(data.moduleId ?? 'uedge'),
    moduleName: String(data.moduleName ?? 'UEDGE Setup & Diagnostics'),
    runtimeMode: String(data.runtimeMode ?? 'local-skeleton'),
    provider: String(data.provider ?? 'local-uedge-provider'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    runtimeLinked: Boolean(data.runtimeLinked),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeSetupProfile(raw: unknown): UedgeSetupProfile {
  const data = asRecord(raw)
  return {
    setupMode: String(data.setupMode ?? 'local-skeleton-setup'),
    customerSetupReady: Boolean(data.customerSetupReady),
    oneClickSetupEnabled: Boolean(data.oneClickSetupEnabled),
    realDeviceRegistrationEnabled: Boolean(data.realDeviceRegistrationEnabled),
    certificateImportEnabled: Boolean(data.certificateImportEnabled),
    tokenProvisioningEnabled: Boolean(data.tokenProvisioningEnabled),
    networkConfigEnabled: Boolean(data.networkConfigEnabled),
    runtimeLinked: Boolean(data.runtimeLinked),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    lastUpdated: String(data.lastUpdated ?? ''),
  }
}

function normalizeSetupStep(raw: unknown): UedgeSetupStep {
  const data = asRecord(raw)
  return {
    stepId: String(data.stepId ?? ''),
    stepName: String(data.stepName ?? ''),
    stepOrder: Number(data.stepOrder ?? 0),
    status: String(data.status ?? ''),
    required: Boolean(data.required),
    actionEnabled: Boolean(data.actionEnabled),
    runtimeLinked: Boolean(data.runtimeLinked),
    notes: String(data.notes ?? ''),
  }
}

function normalizeDiagnosticsSummary(raw: unknown): UedgeDiagnosticsSummary {
  const data = asRecord(raw)
  return {
    diagnosticsMode: String(data.diagnosticsMode ?? 'local-skeleton-diagnostics'),
    engineerDiagnosticsReady: Boolean(data.engineerDiagnosticsReady),
    runtimeConnected: Boolean(data.runtimeConnected),
    connectorDiagnosticsEnabled: Boolean(data.connectorDiagnosticsEnabled),
    protocolDiagnosticsEnabled: Boolean(data.protocolDiagnosticsEnabled),
    mappingReviewEnabled: Boolean(data.mappingReviewEnabled),
    bufferInspectionEnabled: Boolean(data.bufferInspectionEnabled),
    deliveryInspectionEnabled: Boolean(data.deliveryInspectionEnabled),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    runtimeLinked: Boolean(data.runtimeLinked),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    lastUpdated: String(data.lastUpdated ?? ''),
  }
}

function normalizeDiagnosticsPanel(raw: unknown): UedgeDiagnosticsPanel {
  const data = asRecord(raw)
  return {
    panelId: String(data.panelId ?? ''),
    panelName: String(data.panelName ?? ''),
    panelType: String(data.panelType ?? ''),
    status: String(data.status ?? ''),
    runtimeLinked: Boolean(data.runtimeLinked),
    actionEnabled: Boolean(data.actionEnabled),
    summary: String(data.summary ?? ''),
    limitations: asStringArray(data.limitations),
  }
}

function normalizeSummary(raw: unknown): UedgeSummary {
  const data = asRecord(raw)
  return {
    moduleId: String(data.moduleId ?? 'uedge'),
    moduleName: String(data.moduleName ?? 'UEDGE Setup & Diagnostics'),
    setupMode: String(data.setupMode ?? 'local-skeleton-setup'),
    diagnosticsMode: String(data.diagnosticsMode ?? 'local-skeleton-diagnostics'),
    customerSetupReady: Boolean(data.customerSetupReady),
    engineerDiagnosticsReady: Boolean(data.engineerDiagnosticsReady),
    setupStepCount: Number(data.setupStepCount ?? 0),
    diagnosticsPanelCount: Number(data.diagnosticsPanelCount ?? 0),
    oneClickSetupEnabled: Boolean(data.oneClickSetupEnabled),
    runtimeConnected: Boolean(data.runtimeConnected),
    runtimeLinked: Boolean(data.runtimeLinked),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

export async function getUedgeHealth(): Promise<UedgeHealth> {
  const { data } = await request.get('/v1/uedge/health')
  return normalizeHealth(unwrapSuccessData<unknown>(data))
}

export async function getUedgeSetup(): Promise<UedgeSetupProfile> {
  const { data } = await request.get('/v1/uedge/setup')
  return normalizeSetupProfile(unwrapSuccessData<unknown>(data))
}

export async function getUedgeSetupSteps(): Promise<UedgeSetupStep[]> {
  const { data } = await request.get('/v1/uedge/setup/steps')
  const payload = asRecord(unwrapSuccessData<unknown>(data))
  return Array.isArray(payload.items) ? payload.items.map((item) => normalizeSetupStep(item)) : []
}

export async function getUedgeDiagnostics(): Promise<UedgeDiagnosticsSummary> {
  const { data } = await request.get('/v1/uedge/diagnostics')
  return normalizeDiagnosticsSummary(unwrapSuccessData<unknown>(data))
}

export async function getUedgeDiagnosticsPanels(): Promise<UedgeDiagnosticsPanel[]> {
  const { data } = await request.get('/v1/uedge/diagnostics/panels')
  const payload = asRecord(unwrapSuccessData<unknown>(data))
  return Array.isArray(payload.items) ? payload.items.map((item) => normalizeDiagnosticsPanel(item)) : []
}

export async function getUedgeSummary(): Promise<UedgeSummary> {
  const { data } = await request.get('/v1/uedge/summary')
  return normalizeSummary(unwrapSuccessData<unknown>(data))
}

