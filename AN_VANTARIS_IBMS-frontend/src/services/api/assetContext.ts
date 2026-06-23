import request from './request'

export interface AssetContextSummary {
  scope: string
  visualStyle: string
  readOnly: boolean
  runtimeEnabled: boolean
  dbWriteEnabled: boolean
  assetGraphWriteEnabled: boolean
  edgeCommandExecution: boolean
  linkCommandExecution: boolean
  deviceControlEnabled: boolean
  productionActivation: boolean
  totalAssets: number
  totalSystems: number
  totalDevices: number
  totalEvents: number
  totalWorkOrders: number
  totalEvidence: number
  totalReports: number
  totalPanels: number
  linkedObjectTypes: string[]
  guardrails: string[]
  limitations: string[]
}

export interface AssetContextItem {
  assetId: string
  assetName: string
  assetType: string
  systemId: string
  systemName: string
  siteId: string
  zoneId: string
  operationalStatus: string
  linkedWorkOrders: Record<string, unknown>[]
  linkedEvents: Record<string, unknown>[]
  linkedEvidence: Record<string, unknown>[]
  linkedUhmiPanels: Record<string, unknown>[]
  linkedReports: Record<string, unknown>[]
  linkedDeliveryItems: Record<string, unknown>[]
  linkedDiagnostics: Record<string, unknown>[]
  relationshipSummary: Record<string, number>
  readOnly: boolean
}

export interface AssetContextList {
  scope: string
  items: AssetContextItem[]
  total: number
  limitations: string[]
  providerStatuses: Record<string, Record<string, unknown>>
}

export interface AssetContextDetail {
  scope: string
  asset: AssetContextItem | null
  assetRelationships: Record<string, unknown>
  workOrders: Record<string, unknown>[]
  maintenanceTasks: Record<string, unknown>[]
  events: Record<string, unknown>[]
  evidence: Record<string, unknown>[]
  uhmiPanels: Record<string, unknown>[]
  reports: Record<string, unknown>[]
  customerDelivery: Record<string, unknown>[]
  foundationDiagnostics: Record<string, unknown>[]
  traceabilityPath: string[]
  limitations: string[]
  guardrails: string[]
  readOnly: boolean
}

export interface AssetContextGraph {
  graphMode: string
  nodes: Record<string, unknown>[]
  edges: Record<string, unknown>[]
  summary: { nodeCount: number; edgeCount: number }
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.filter((item) => typeof item === 'object' && item !== null).map((item) => item as Record<string, unknown>)
    : []
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : []
}

function unwrap<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

function normalizeItem(raw: unknown): AssetContextItem {
  const data = asRecord(raw)
  return {
    assetId: String(data.assetId ?? ''),
    assetName: String(data.assetName ?? ''),
    assetType: String(data.assetType ?? ''),
    systemId: String(data.systemId ?? ''),
    systemName: String(data.systemName ?? ''),
    siteId: String(data.siteId ?? ''),
    zoneId: String(data.zoneId ?? ''),
    operationalStatus: String(data.operationalStatus ?? ''),
    linkedWorkOrders: asRecordArray(data.linkedWorkOrders),
    linkedEvents: asRecordArray(data.linkedEvents),
    linkedEvidence: asRecordArray(data.linkedEvidence),
    linkedUhmiPanels: asRecordArray(data.linkedUhmiPanels),
    linkedReports: asRecordArray(data.linkedReports),
    linkedDeliveryItems: asRecordArray(data.linkedDeliveryItems),
    linkedDiagnostics: asRecordArray(data.linkedDiagnostics),
    relationshipSummary: asRecord(data.relationshipSummary) as Record<string, number>,
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
  }
}

function normalizeSummary(raw: unknown): AssetContextSummary {
  const data = asRecord(raw)
  return {
    scope: String(data.scope ?? 'ASSET_CONTEXT_GA_R1'),
    visualStyle: String(data.visualStyle ?? 'VANTARIS_LIGHT_OPERATIONS_CONSOLE'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    runtimeEnabled: Boolean(data.runtimeEnabled),
    dbWriteEnabled: Boolean(data.dbWriteEnabled),
    assetGraphWriteEnabled: Boolean(data.assetGraphWriteEnabled),
    edgeCommandExecution: Boolean(data.edgeCommandExecution),
    linkCommandExecution: Boolean(data.linkCommandExecution),
    deviceControlEnabled: Boolean(data.deviceControlEnabled),
    productionActivation: Boolean(data.productionActivation),
    totalAssets: Number(data.totalAssets ?? 0),
    totalSystems: Number(data.totalSystems ?? 0),
    totalDevices: Number(data.totalDevices ?? 0),
    totalEvents: Number(data.totalEvents ?? 0),
    totalWorkOrders: Number(data.totalWorkOrders ?? 0),
    totalEvidence: Number(data.totalEvidence ?? 0),
    totalReports: Number(data.totalReports ?? 0),
    totalPanels: Number(data.totalPanels ?? 0),
    linkedObjectTypes: asStringArray(data.linkedObjectTypes),
    guardrails: asStringArray(data.guardrails),
    limitations: asStringArray(data.limitations),
  }
}

export async function getAssetContextSummary(): Promise<AssetContextSummary> {
  return normalizeSummary(unwrap(await request.get('/v1/one/asset-context/summary')))
}

export async function getAssetContextAssets(): Promise<AssetContextList> {
  const data = asRecord(unwrap(await request.get('/v1/one/asset-context/assets')))
  return {
    scope: String(data.scope ?? 'ASSET_CONTEXT_GA_R1'),
    items: asRecordArray(data.items).map((item) => normalizeItem(item)),
    total: Number(data.total ?? 0),
    limitations: asStringArray(data.limitations),
    providerStatuses: asRecord(data.providerStatuses) as Record<string, Record<string, unknown>>,
  }
}

export async function getAssetContextDetail(assetId: string): Promise<AssetContextDetail> {
  const data = asRecord(unwrap(await request.get(`/v1/one/asset-context/assets/${assetId}`)))
  return {
    scope: String(data.scope ?? 'ASSET_CONTEXT_GA_R1'),
    asset: data.asset ? normalizeItem(data.asset) : null,
    assetRelationships: asRecord(data.assetRelationships),
    workOrders: asRecordArray(data.workOrders),
    maintenanceTasks: asRecordArray(data.maintenanceTasks),
    events: asRecordArray(data.events),
    evidence: asRecordArray(data.evidence),
    uhmiPanels: asRecordArray(data.uhmiPanels),
    reports: asRecordArray(data.reports),
    customerDelivery: asRecordArray(data.customerDelivery),
    foundationDiagnostics: asRecordArray(data.foundationDiagnostics),
    traceabilityPath: asStringArray(data.traceabilityPath),
    limitations: asStringArray(data.limitations),
    guardrails: asStringArray(data.guardrails),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
  }
}

export async function getAssetContextGraph(): Promise<AssetContextGraph> {
  const data = asRecord(unwrap(await request.get('/v1/one/asset-context/graph')))
  const summary = asRecord(data.summary)
  return {
    graphMode: String(data.graphMode ?? 'local-readonly-asset-context-projection'),
    nodes: asRecordArray(data.nodes),
    edges: asRecordArray(data.edges),
    summary: {
      nodeCount: Number(summary.nodeCount ?? 0),
      edgeCount: Number(summary.edgeCount ?? 0),
    },
  }
}

