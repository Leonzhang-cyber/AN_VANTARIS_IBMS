import request from './request'

export interface AssetsHealth {
  status: string
  moduleId: string
  moduleName: string
  runtimeMode: string
  provider: string
  sourceSemantics: string
  readOnly: boolean
  controlActionsEnabled: boolean
  discoveryEnabled: boolean
  edgeRuntimeIntegrated: boolean
  linkRuntimeIntegrated: boolean
  dbPersistenceIntegrated: boolean
  totalAssets: number
  runtimeLinkedAssets: number
  certified: boolean
  iec62443Certified: boolean
}

export interface AssetRecord {
  assetId: string
  assetCode: string
  assetName: string
  assetType: string
  assetCategory: string
  lifecycleStatus: string
  operationalStatus: string
  siteId: string
  siteName: string
  buildingId: string
  buildingName: string
  floorId: string
  floorName: string
  zoneId: string
  zoneName: string
  systemId: string
  systemName: string
  parentAssetId: string
  childrenAssetIds: string[]
  relatedAssetIds: string[]
  sourceSystem: string
  sourceRecordId: string
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  createdAt: string
  updatedAt: string
  tags: string[]
  metadata: Record<string, unknown>
  limitations: string[]
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface AssetsSummary {
  totalAssets: number
  siteCount: number
  buildingCount: number
  floorCount: number
  zoneCount: number
  systemCount: number
  equipmentCount: number
  pointCount: number
  activeAssets: number
  mockAssets: number
  runtimeLinkedAssets: number
  certifiedAssets: number
  iec62443CertifiedAssets: number
  assetTypes: string[]
  assetCategories: string[]
  limitations: string[]
}

export interface TopologyNode {
  nodeId: string
  assetId: string
  label: string
  nodeType: 'site' | 'building' | 'floor' | 'zone' | 'system' | 'equipment' | 'point'
  assetCategory: string
  status: string
  runtimeLinked: boolean
}

export interface TopologyEdge {
  edgeId: string
  from: string
  to: string
  relationship: 'contains' | 'hosts' | 'belongs-to' | 'measures' | 'related-to'
  runtimeLinked: boolean
}

export interface AssetTopology {
  topologyMode: string
  nodes: TopologyNode[]
  edges: TopologyEdge[]
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
  notes: string
  summary: {
    nodeCount: number
    edgeCount: number
    runtimeLinked: boolean
  }
}

export interface AssetRelationships {
  assetId: string
  relationshipMode: string
  parent: AssetRecord | null
  children: AssetRecord[]
  related: AssetRecord[]
  edges: Array<{
    edgeId: string
    from: string
    to: string
    relationship: string
    runtimeLinked: boolean
  }>
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface AssetListResponse {
  items: AssetRecord[]
  total: number
  filters: {
    assetType: string
    assetCategory: string
    lifecycleStatus: string
    operationalStatus: string
    siteId: string
    systemId: string
  }
  summary: AssetsSummary
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  readOnly: boolean
  discoveryEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface GetAssetsListParams {
  assetType?: string
  assetCategory?: string
  lifecycleStatus?: string
  operationalStatus?: string
  siteId?: string
  systemId?: string
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

function unwrapData<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

function normalizeAsset(raw: unknown): AssetRecord {
  const data = asRecord(raw)
  return {
    assetId: String(data.assetId ?? ''),
    assetCode: String(data.assetCode ?? ''),
    assetName: String(data.assetName ?? ''),
    assetType: String(data.assetType ?? ''),
    assetCategory: String(data.assetCategory ?? ''),
    lifecycleStatus: String(data.lifecycleStatus ?? ''),
    operationalStatus: String(data.operationalStatus ?? ''),
    siteId: String(data.siteId ?? ''),
    siteName: String(data.siteName ?? ''),
    buildingId: String(data.buildingId ?? ''),
    buildingName: String(data.buildingName ?? ''),
    floorId: String(data.floorId ?? ''),
    floorName: String(data.floorName ?? ''),
    zoneId: String(data.zoneId ?? ''),
    zoneName: String(data.zoneName ?? ''),
    systemId: String(data.systemId ?? ''),
    systemName: String(data.systemName ?? ''),
    parentAssetId: String(data.parentAssetId ?? ''),
    childrenAssetIds: asStringArray(data.childrenAssetIds),
    relatedAssetIds: asStringArray(data.relatedAssetIds),
    sourceSystem: String(data.sourceSystem ?? ''),
    sourceRecordId: String(data.sourceRecordId ?? ''),
    provider: String(data.provider ?? 'local-assets-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    createdAt: String(data.createdAt ?? ''),
    updatedAt: String(data.updatedAt ?? ''),
    tags: asStringArray(data.tags),
    metadata: asRecord(data.metadata),
    limitations: asStringArray(data.limitations),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeSummary(raw: unknown): AssetsSummary {
  const data = asRecord(raw)
  return {
    totalAssets: Number(data.totalAssets ?? 0),
    siteCount: Number(data.siteCount ?? 0),
    buildingCount: Number(data.buildingCount ?? 0),
    floorCount: Number(data.floorCount ?? 0),
    zoneCount: Number(data.zoneCount ?? 0),
    systemCount: Number(data.systemCount ?? 0),
    equipmentCount: Number(data.equipmentCount ?? 0),
    pointCount: Number(data.pointCount ?? 0),
    activeAssets: Number(data.activeAssets ?? 0),
    mockAssets: Number(data.mockAssets ?? 0),
    runtimeLinkedAssets: Number(data.runtimeLinkedAssets ?? 0),
    certifiedAssets: Number(data.certifiedAssets ?? 0),
    iec62443CertifiedAssets: Number(data.iec62443CertifiedAssets ?? 0),
    assetTypes: asStringArray(data.assetTypes),
    assetCategories: asStringArray(data.assetCategories),
    limitations: asStringArray(data.limitations),
  }
}

function normalizeHealth(raw: unknown): AssetsHealth {
  const data = asRecord(raw)
  return {
    status: String(data.status ?? 'unknown'),
    moduleId: String(data.moduleId ?? 'assets-topology'),
    moduleName: String(data.moduleName ?? 'Assets & Topology'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    provider: String(data.provider ?? 'local-assets-provider'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    discoveryEnabled: Boolean(data.discoveryEnabled),
    edgeRuntimeIntegrated: Boolean(data.edgeRuntimeIntegrated),
    linkRuntimeIntegrated: Boolean(data.linkRuntimeIntegrated),
    dbPersistenceIntegrated: Boolean(data.dbPersistenceIntegrated),
    totalAssets: Number(data.totalAssets ?? 0),
    runtimeLinkedAssets: Number(data.runtimeLinkedAssets ?? 0),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeTopologyNode(raw: unknown): TopologyNode {
  const data = asRecord(raw)
  return {
    nodeId: String(data.nodeId ?? ''),
    assetId: String(data.assetId ?? ''),
    label: String(data.label ?? ''),
    nodeType: String(data.nodeType ?? 'site') as TopologyNode['nodeType'],
    assetCategory: String(data.assetCategory ?? ''),
    status: String(data.status ?? ''),
    runtimeLinked: Boolean(data.runtimeLinked),
  }
}

function normalizeTopologyEdge(raw: unknown): TopologyEdge {
  const data = asRecord(raw)
  return {
    edgeId: String(data.edgeId ?? ''),
    from: String(data.from ?? ''),
    to: String(data.to ?? ''),
    relationship: String(data.relationship ?? 'contains') as TopologyEdge['relationship'],
    runtimeLinked: Boolean(data.runtimeLinked),
  }
}

function normalizeTopology(raw: unknown): AssetTopology {
  const data = asRecord(raw)
  const summary = asRecord(data.summary)
  return {
    topologyMode: String(data.topologyMode ?? 'local-skeleton-topology'),
    nodes: asRecordArray(data.nodes).map((item) => normalizeTopologyNode(item)),
    edges: asRecordArray(data.edges).map((item) => normalizeTopologyEdge(item)),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    notes: String(data.notes ?? ''),
    summary: {
      nodeCount: Number(summary.nodeCount ?? 0),
      edgeCount: Number(summary.edgeCount ?? 0),
      runtimeLinked: Boolean(summary.runtimeLinked),
    },
  }
}

function normalizeRelationships(raw: unknown): AssetRelationships {
  const data = asRecord(raw)
  return {
    assetId: String(data.assetId ?? ''),
    relationshipMode: String(data.relationshipMode ?? 'local-skeleton-relationships'),
    parent: data.parent ? normalizeAsset(data.parent) : null,
    children: asRecordArray(data.children).map((item) => normalizeAsset(item)),
    related: asRecordArray(data.related).map((item) => normalizeAsset(item)),
    edges: asRecordArray(data.edges).map((item) => ({
      edgeId: String(item.edgeId ?? ''),
      from: String(item.from ?? ''),
      to: String(item.to ?? ''),
      relationship: String(item.relationship ?? ''),
      runtimeLinked: Boolean(item.runtimeLinked),
    })),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeList(raw: unknown): AssetListResponse {
  const data = asRecord(raw)
  const filters = asRecord(data.filters)
  return {
    items: asRecordArray(data.items).map((item) => normalizeAsset(item)),
    total: Number(data.total ?? 0),
    filters: {
      assetType: String(filters.assetType ?? ''),
      assetCategory: String(filters.assetCategory ?? ''),
      lifecycleStatus: String(filters.lifecycleStatus ?? ''),
      operationalStatus: String(filters.operationalStatus ?? ''),
      siteId: String(filters.siteId ?? ''),
      systemId: String(filters.systemId ?? ''),
    },
    summary: normalizeSummary(data.summary),
    provider: String(data.provider ?? 'local-assets-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    discoveryEnabled: Boolean(data.discoveryEnabled),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

export async function getAssetsHealth(): Promise<AssetsHealth> {
  const { data } = await request.get('/v1/assets/health')
  return normalizeHealth(unwrapData<unknown>(data))
}

export async function getAssetsList(params: GetAssetsListParams = {}): Promise<AssetListResponse> {
  const { data } = await request.get('/v1/assets', { params })
  return normalizeList(unwrapData<unknown>(data))
}

export async function getAssetDetail(assetId: string): Promise<AssetRecord> {
  const { data } = await request.get(`/v1/assets/${encodeURIComponent(assetId)}`)
  return normalizeAsset(unwrapData<unknown>(data))
}

export async function getAssetsSummary(): Promise<AssetsSummary> {
  const { data } = await request.get('/v1/assets/summary')
  return normalizeSummary(unwrapData<unknown>(data))
}

export async function getAssetTopology(): Promise<AssetTopology> {
  const { data } = await request.get('/v1/assets/topology')
  return normalizeTopology(unwrapData<unknown>(data))
}

export async function getAssetRelationships(assetId: string): Promise<AssetRelationships> {
  const { data } = await request.get(`/v1/assets/${encodeURIComponent(assetId)}/relationships`)
  return normalizeRelationships(unwrapData<unknown>(data))
}

