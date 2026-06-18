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
  hierarchyPath: AssetHierarchyPath | null
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface AssetHierarchyLevel {
  level: number
  assetId: string
  assetName: string
  assetType: string
  relationship: string
}

export interface AssetHierarchyPath {
  pathMode: string
  assetId: string
  levels: AssetHierarchyLevel[]
  complete: boolean
  runtimeLinked: boolean
  notes: string
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
  totalRelationships: number
  containmentRelationships: number
  pointRelationships: number
  relatedRelationships: number
  rootAssets: number
  leafAssets: number
  maxHierarchyDepth: number
  runtimeLinkedRelationships: number
  topologyValidationMode: string
  topologyValidated: boolean
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
  relationshipSummary: AssetRelationshipSummary
  relationshipGroups: AssetRelationshipGroups
  relationshipPath: AssetRelationshipPath
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

export interface AssetRelationshipSummary {
  parentCount: number
  childCount: number
  relatedCount: number
  upstreamCount: number
  downstreamCount: number
  pointCount: number
  equipmentCount: number
  systemCount: number
  runtimeLinkedRelationships: number
}

export interface AssetRelationshipGroups {
  parent: AssetRecord[]
  children: AssetRecord[]
  related: AssetRecord[]
  upstream: AssetRecord[]
  downstream: AssetRecord[]
  points: AssetRecord[]
  equipment: AssetRecord[]
  systems: AssetRecord[]
}

export interface AssetRelationshipPath {
  pathMode: string
  assetId: string
  rootAssetId: string
  rootToAsset: AssetHierarchyLevel[]
  assetToLeaves: Array<Array<{ assetId: string; assetName: string; assetType: string }>>
  complete: boolean
  runtimeLinked: boolean
}

export interface AssetTopologyLineage {
  assetId: string
  lineageMode: string
  upstream: AssetRecord[]
  downstream: AssetRecord[]
  siblings: AssetRecord[]
  containedAssets: AssetRecord[]
  containingAssets: AssetRecord[]
  runtimeLinked: boolean
  certified: boolean
  iec62443Certified: boolean
  notes: string
}

export interface AssetImpactSkeleton {
  assetId: string
  impactMode: string
  potentiallyImpactedAssets: string[]
  potentiallyImpactedSystems: string[]
  potentiallyImpactedZones: string[]
  impactScore: number | null
  impactCalculated: boolean
  runtimeLinked: boolean
  limitations: string[]
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
    hierarchyPath: normalizeHierarchyPath(data.hierarchyPath),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeHierarchyLevel(raw: unknown): AssetHierarchyLevel {
  const data = asRecord(raw)
  return {
    level: Number(data.level ?? 0),
    assetId: String(data.assetId ?? ''),
    assetName: String(data.assetName ?? ''),
    assetType: String(data.assetType ?? ''),
    relationship: String(data.relationship ?? ''),
  }
}

function normalizeHierarchyPath(raw: unknown): AssetHierarchyPath | null {
  if (!raw || typeof raw !== 'object') {
    return null
  }
  const data = asRecord(raw)
  return {
    pathMode: String(data.pathMode ?? 'local-skeleton-hierarchy'),
    assetId: String(data.assetId ?? ''),
    levels: asRecordArray(data.levels).map((item) => normalizeHierarchyLevel(item)),
    complete: Boolean(data.complete),
    runtimeLinked: Boolean(data.runtimeLinked),
    notes: String(data.notes ?? ''),
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
    totalRelationships: Number(data.totalRelationships ?? 0),
    containmentRelationships: Number(data.containmentRelationships ?? 0),
    pointRelationships: Number(data.pointRelationships ?? 0),
    relatedRelationships: Number(data.relatedRelationships ?? 0),
    rootAssets: Number(data.rootAssets ?? 0),
    leafAssets: Number(data.leafAssets ?? 0),
    maxHierarchyDepth: Number(data.maxHierarchyDepth ?? 0),
    runtimeLinkedRelationships: Number(data.runtimeLinkedRelationships ?? 0),
    topologyValidationMode: String(data.topologyValidationMode ?? 'local-skeleton-validation'),
    topologyValidated: Boolean(data.topologyValidated),
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
  const relationshipSummary = asRecord(data.relationshipSummary)
  const relationshipGroups = asRecord(data.relationshipGroups)
  const relationshipPath = asRecord(data.relationshipPath)
  return {
    assetId: String(data.assetId ?? ''),
    relationshipMode: String(data.relationshipMode ?? 'local-skeleton-relationships'),
    parent: data.parent ? normalizeAsset(data.parent) : null,
    children: asRecordArray(data.children).map((item) => normalizeAsset(item)),
    related: asRecordArray(data.related).map((item) => normalizeAsset(item)),
    relationshipSummary: {
      parentCount: Number(relationshipSummary.parentCount ?? 0),
      childCount: Number(relationshipSummary.childCount ?? 0),
      relatedCount: Number(relationshipSummary.relatedCount ?? 0),
      upstreamCount: Number(relationshipSummary.upstreamCount ?? 0),
      downstreamCount: Number(relationshipSummary.downstreamCount ?? 0),
      pointCount: Number(relationshipSummary.pointCount ?? 0),
      equipmentCount: Number(relationshipSummary.equipmentCount ?? 0),
      systemCount: Number(relationshipSummary.systemCount ?? 0),
      runtimeLinkedRelationships: Number(relationshipSummary.runtimeLinkedRelationships ?? 0),
    },
    relationshipGroups: {
      parent: asRecordArray(relationshipGroups.parent).map((item) => normalizeAsset(item)),
      children: asRecordArray(relationshipGroups.children).map((item) => normalizeAsset(item)),
      related: asRecordArray(relationshipGroups.related).map((item) => normalizeAsset(item)),
      upstream: asRecordArray(relationshipGroups.upstream).map((item) => normalizeAsset(item)),
      downstream: asRecordArray(relationshipGroups.downstream).map((item) => normalizeAsset(item)),
      points: asRecordArray(relationshipGroups.points).map((item) => normalizeAsset(item)),
      equipment: asRecordArray(relationshipGroups.equipment).map((item) => normalizeAsset(item)),
      systems: asRecordArray(relationshipGroups.systems).map((item) => normalizeAsset(item)),
    },
    relationshipPath: {
      pathMode: String(relationshipPath.pathMode ?? 'local-skeleton-relationship-path'),
      assetId: String(relationshipPath.assetId ?? ''),
      rootAssetId: String(relationshipPath.rootAssetId ?? ''),
      rootToAsset: asRecordArray(relationshipPath.rootToAsset).map((item) => normalizeHierarchyLevel(item)),
      assetToLeaves: Array.isArray(relationshipPath.assetToLeaves)
        ? relationshipPath.assetToLeaves.map((entry) =>
            asRecordArray(entry).map((leaf) => ({
              assetId: String(leaf.assetId ?? ''),
              assetName: String(leaf.assetName ?? ''),
              assetType: String(leaf.assetType ?? ''),
            }))
          )
        : [],
      complete: Boolean(relationshipPath.complete),
      runtimeLinked: Boolean(relationshipPath.runtimeLinked),
    },
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

function normalizeLineage(raw: unknown): AssetTopologyLineage {
  const data = asRecord(raw)
  return {
    assetId: String(data.assetId ?? ''),
    lineageMode: String(data.lineageMode ?? 'local-skeleton-lineage'),
    upstream: asRecordArray(data.upstream).map((item) => normalizeAsset(item)),
    downstream: asRecordArray(data.downstream).map((item) => normalizeAsset(item)),
    siblings: asRecordArray(data.siblings).map((item) => normalizeAsset(item)),
    containedAssets: asRecordArray(data.containedAssets).map((item) => normalizeAsset(item)),
    containingAssets: asRecordArray(data.containingAssets).map((item) => normalizeAsset(item)),
    runtimeLinked: Boolean(data.runtimeLinked),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    notes: String(data.notes ?? ''),
  }
}

function normalizeImpact(raw: unknown): AssetImpactSkeleton {
  const data = asRecord(raw)
  return {
    assetId: String(data.assetId ?? ''),
    impactMode: String(data.impactMode ?? 'local-skeleton-impact'),
    potentiallyImpactedAssets: asStringArray(data.potentiallyImpactedAssets),
    potentiallyImpactedSystems: asStringArray(data.potentiallyImpactedSystems),
    potentiallyImpactedZones: asStringArray(data.potentiallyImpactedZones),
    impactScore: data.impactScore === null || data.impactScore === undefined ? null : Number(data.impactScore),
    impactCalculated: Boolean(data.impactCalculated),
    runtimeLinked: Boolean(data.runtimeLinked),
    limitations: asStringArray(data.limitations),
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

export async function getAssetLineage(assetId: string): Promise<AssetTopologyLineage> {
  const { data } = await request.get(`/v1/assets/${encodeURIComponent(assetId)}/lineage`)
  return normalizeLineage(unwrapData<unknown>(data))
}

export async function getAssetImpact(assetId: string): Promise<AssetImpactSkeleton> {
  const { data } = await request.get(`/v1/assets/${encodeURIComponent(assetId)}/impact`)
  return normalizeImpact(unwrapData<unknown>(data))
}

