<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import {
  getAssetDetail,
  getAssetImpact,
  getAssetLineage,
  getAssetRelationships,
  getAssetsHealth,
  getAssetsList,
  getAssetTopology,
  type AssetImpactSkeleton,
  type AssetRelationshipGroups,
  type AssetRelationshipPath,
  type AssetRelationshipSummary,
  type AssetRecord,
  type AssetRelationships,
  type AssetsHealth,
  type AssetsSummary,
  type AssetTopology,
  type AssetTopologyLineage,
} from '@/services/api/assets'

type CustomerSection = {
  title: string
  subtitle: string
  primaryAction: string
  metrics: Array<{ label: string; value: string; note: string }>
  rows: Array<{ item: string; focus: string; status: string }>
}

const route = useRoute()
const customerUnavailableMessage = 'Live service is temporarily unavailable. Showing the latest available operational view.'

const customerSections: Record<string, CustomerSection> = {
  'portfolio-list': {
    title: 'Site Portfolio',
    subtitle: 'Portfolio view across customer sites, operating health, location hierarchy, and asset coverage.',
    primaryAction: 'Review portfolio assets',
    metrics: [
      { label: 'Sites', value: '12', note: 'Sites represented in portfolio view' },
      { label: 'Buildings', value: '38', note: 'Buildings mapped to site hierarchy' },
      { label: 'Systems', value: '64', note: 'Systems available for review' },
      { label: 'Asset Records', value: '428', note: 'Assets linked to topology context' },
    ],
    rows: [
      { item: 'Review portfolio hierarchy', focus: 'Site / building / zone structure', status: 'Ready' },
      { item: 'Open site asset coverage', focus: 'Assets by site and system', status: 'Active' },
      { item: 'Check portfolio evidence', focus: 'Evidence-linked asset records', status: 'Ready' },
    ],
  },
  'site-health': {
    title: 'Site Health',
    subtitle: 'Site health view across availability, degraded assets, operational impact, and evidence readiness.',
    primaryAction: 'Review site health',
    metrics: [
      { label: 'Healthy Sites', value: '8', note: 'Sites operating within target range' },
      { label: 'Warning Sites', value: '3', note: 'Sites with degraded indicators' },
      { label: 'Critical Sites', value: '1', note: 'Site requiring immediate review' },
      { label: 'Evidence Links', value: '31', note: 'Health records linked to evidence' },
    ],
    rows: [
      { item: 'Inspect warning site', focus: 'Availability and asset condition', status: 'Review' },
      { item: 'Open impacted assets', focus: 'Assets connected to health warnings', status: 'Active' },
      { item: 'Prepare health evidence', focus: 'Traceable health summary', status: 'Ready' },
    ],
  },
  'site-risk': {
    title: 'Site Risk',
    subtitle: 'Risk posture for customer sites including impacted assets, service exposure, and mitigation actions.',
    primaryAction: 'Review site risk',
    metrics: [
      { label: 'Open Risks', value: '9', note: 'Site risks under review' },
      { label: 'High Impact', value: '3', note: 'Risks with customer impact' },
      { label: 'Mitigations', value: '7', note: 'Mitigation actions in progress' },
      { label: 'Evidence Ready', value: '8', note: 'Risks with supporting evidence' },
    ],
    rows: [
      { item: 'Review critical site risk', focus: 'Service impact and affected systems', status: 'High' },
      { item: 'Open mitigation tracker', focus: 'Risk owner and action state', status: 'Active' },
      { item: 'Check risk evidence', focus: 'Evidence and report linkage', status: 'Ready' },
    ],
  },
  'building-list': {
    title: 'Building List',
    subtitle: 'Building hierarchy, floor coverage, system distribution, and asset readiness by location.',
    primaryAction: 'Review buildings',
    metrics: [
      { label: 'Buildings', value: '38', note: 'Buildings in mapped portfolio' },
      { label: 'Floors', value: '146', note: 'Floors linked to asset hierarchy' },
      { label: 'Zones', value: '512', note: 'Operational zones represented' },
      { label: 'Systems', value: '64', note: 'Systems mapped to buildings' },
    ],
    rows: [
      { item: 'Open building overview', focus: 'Building / floor / zone mapping', status: 'Ready' },
      { item: 'Review system distribution', focus: 'Systems by building', status: 'Active' },
      { item: 'Check building evidence', focus: 'Location evidence coverage', status: 'Ready' },
    ],
  },
  'building-overview': {
    title: 'Building Overview',
    subtitle: 'Building-level operational view for floors, zones, systems, assets, and service exposure.',
    primaryAction: 'Open building overview',
    metrics: [
      { label: 'Mapped Floors', value: '146', note: 'Floors with asset context' },
      { label: 'Active Zones', value: '489', note: 'Zones operating normally' },
      { label: 'Warning Zones', value: '23', note: 'Zones requiring review' },
      { label: 'Linked Assets', value: '428', note: 'Assets mapped to building context' },
    ],
    rows: [
      { item: 'Review building status', focus: 'Operational state by floor', status: 'Active' },
      { item: 'Open zone conditions', focus: 'Zone health and service impact', status: 'Review' },
      { item: 'Check asset evidence', focus: 'Evidence-linked location records', status: 'Ready' },
    ],
  },
  'floor-plan': {
    title: 'Floor Plan',
    subtitle: 'Floor plan context for zones, asset overlays, alarm overlays, and customer service impact.',
    primaryAction: 'Review floor plan',
    metrics: [
      { label: 'Floor Views', value: '146', note: 'Floor plans available for review' },
      { label: 'Asset Overlays', value: '428', note: 'Assets represented on plans' },
      { label: 'Alarm Overlays', value: '34', note: 'Alarm points linked to space context' },
      { label: 'Evidence Links', value: '52', note: 'Floor-plan evidence records' },
    ],
    rows: [
      { item: 'Open zone overlay', focus: 'Floor / zone operating view', status: 'Ready' },
      { item: 'Review alarm overlay', focus: 'Alarm impact by location', status: 'Active' },
      { item: 'Check floor evidence', focus: 'Evidence linked to floor context', status: 'Ready' },
    ],
  },
  'zone-list': {
    title: 'Zone List',
    subtitle: 'Zone-level operating context for occupancy, assets, system coverage, and service impact.',
    primaryAction: 'Review zones',
    metrics: [
      { label: 'Zones', value: '512', note: 'Zones mapped in topology' },
      { label: 'Warning Zones', value: '23', note: 'Zones requiring operator review' },
      { label: 'Linked Systems', value: '64', note: 'Systems associated with zones' },
      { label: 'Linked Assets', value: '428', note: 'Assets associated with zones' },
    ],
    rows: [
      { item: 'Review zone conditions', focus: 'Zone status and system coverage', status: 'Active' },
      { item: 'Open zone assets', focus: 'Equipment by zone', status: 'Ready' },
      { item: 'Prepare zone report', focus: 'Customer location summary', status: 'Ready' },
    ],
  },
  'asset-to-space-mapping': {
    title: 'Asset-to-Space Mapping',
    subtitle: 'Mapping quality for asset placement, location hierarchy, evidence records, and mapping gaps.',
    primaryAction: 'Review mapping',
    metrics: [
      { label: 'Mapped Assets', value: '391', note: 'Assets with location binding' },
      { label: 'Mapping Gaps', value: '37', note: 'Assets requiring mapping review' },
      { label: 'Space Links', value: '512', note: 'Spaces connected to asset records' },
      { label: 'Evidence Links', value: '44', note: 'Mapping evidence records' },
    ],
    rows: [
      { item: 'Review mapping gaps', focus: 'Asset and location alignment', status: 'Review' },
      { item: 'Open mapped equipment', focus: 'Equipment by space', status: 'Ready' },
      { item: 'Check mapping evidence', focus: 'Traceable mapping records', status: 'Ready' },
    ],
  },
  'system-list': {
    title: 'System List',
    subtitle: 'System registry view across availability, linked assets, alarms, faults, and evidence coverage.',
    primaryAction: 'Review systems',
    metrics: [
      { label: 'Systems', value: '64', note: 'Systems in registry' },
      { label: 'Critical Systems', value: '11', note: 'Systems with high service impact' },
      { label: 'Linked Assets', value: '428', note: 'Assets assigned to systems' },
      { label: 'Evidence Ready', value: '58', note: 'System records with evidence' },
    ],
    rows: [
      { item: 'Review system registry', focus: 'System inventory and status', status: 'Ready' },
      { item: 'Open system alarms', focus: 'Alarm and fault linkage', status: 'Active' },
      { item: 'Check system evidence', focus: 'System evidence package', status: 'Ready' },
    ],
  },
  'system-topology': {
    title: 'System Topology',
    subtitle: 'Relationship topology for systems, assets, points, upstream dependencies, and service impact paths.',
    primaryAction: 'Open topology',
    metrics: [
      { label: 'Systems', value: '64', note: 'Systems represented in topology' },
      { label: 'Relationships', value: '812', note: 'Topology relationships under review' },
      { label: 'Impact Paths', value: '28', note: 'Paths with operational impact' },
      { label: 'Data Quality', value: '91%', note: 'Topology completeness indicator' },
    ],
    rows: [
      { item: 'Review dependency graph', focus: 'System-to-asset relationship paths', status: 'Active' },
      { item: 'Open impact path', focus: 'Service impact from upstream assets', status: 'Review' },
      { item: 'Check topology quality', focus: 'Relationship evidence and gaps', status: 'Ready' },
    ],
  },
  'asset-list': {
    title: 'Asset List',
    subtitle: 'Asset registry view for customer-visible equipment, systems, locations, lifecycle, and evidence.',
    primaryAction: 'Review asset list',
    metrics: [
      { label: 'Assets', value: '428', note: 'Assets in customer-visible registry' },
      { label: 'Active Assets', value: '391', note: 'Assets currently active' },
      { label: 'Warning Assets', value: '21', note: 'Assets requiring review' },
      { label: 'Evidence Links', value: '76', note: 'Assets with evidence records' },
    ],
    rows: [
      { item: 'Review asset registry', focus: 'Asset status and hierarchy', status: 'Ready' },
      { item: 'Open critical assets', focus: 'Operational status and impact', status: 'Active' },
      { item: 'Check asset evidence', focus: 'Asset evidence chain', status: 'Ready' },
    ],
  },
  'asset-detail': {
    title: 'Asset Detail',
    subtitle: 'Focused asset record with context, relationships, operational state, history, and evidence.',
    primaryAction: 'Open asset detail',
    metrics: [
      { label: 'Context Fields', value: '18', note: 'Core asset context fields' },
      { label: 'Relationships', value: '12', note: 'Related assets and systems' },
      { label: 'Open Events', value: '3', note: 'Events linked to selected asset' },
      { label: 'Evidence Items', value: '7', note: 'Evidence linked to asset detail' },
    ],
    rows: [
      { item: 'Review asset detail', focus: 'Identity, lifecycle and operating state', status: 'Ready' },
      { item: 'Open relationship context', focus: 'Upstream and downstream assets', status: 'Active' },
      { item: 'Check asset history', focus: 'Events, work orders and evidence', status: 'Ready' },
    ],
  },
  'asset-context': {
    title: 'Asset Context',
    subtitle: 'Unified asset context across relationships, health, history, work orders, and evidence records.',
    primaryAction: 'Review asset context',
    metrics: [
      { label: 'Context Records', value: '428', note: 'Assets with context records' },
      { label: 'Health Views', value: '391', note: 'Assets with health posture' },
      { label: 'Linked WOs', value: '42', note: 'Work orders linked to assets' },
      { label: 'Evidence Ready', value: '76', note: 'Asset evidence records' },
    ],
    rows: [
      { item: 'Review asset context', focus: 'Asset health and operational linkage', status: 'Active' },
      { item: 'Open maintenance history', focus: 'Work orders and closure evidence', status: 'Ready' },
      { item: 'Check evidence links', focus: 'Traceability across records', status: 'Ready' },
    ],
  },
  'equipment-list': {
    title: 'Equipment List',
    subtitle: 'Equipment-level view across operating state, maintenance history, vendor context, and evidence.',
    primaryAction: 'Review equipment',
    metrics: [
      { label: 'Equipment', value: '312', note: 'Equipment assets in registry' },
      { label: 'Critical Equipment', value: '34', note: 'High-impact equipment records' },
      { label: 'Maintenance Links', value: '42', note: 'Equipment linked to work orders' },
      { label: 'Vendor Records', value: '28', note: 'Equipment with vendor context' },
    ],
    rows: [
      { item: 'Review equipment list', focus: 'Equipment operating status', status: 'Ready' },
      { item: 'Open maintenance history', focus: 'Work orders by equipment', status: 'Active' },
      { item: 'Check vendor evidence', focus: 'Vendor and warranty context', status: 'Ready' },
    ],
  },
  'runtime-status': {
    title: 'Runtime Status',
    subtitle: 'Customer operations view of runtime-facing status without exposing internal integration details.',
    primaryAction: 'Review runtime status',
    metrics: [
      { label: 'Online Assets', value: '391', note: 'Assets showing available status' },
      { label: 'Warning Assets', value: '21', note: 'Assets requiring review' },
      { label: 'Unavailable Assets', value: '4', note: 'Assets requiring escalation' },
      { label: 'Status Evidence', value: '62', note: 'Status records linked to evidence' },
    ],
    rows: [
      { item: 'Review asset status', focus: 'Availability and health indicators', status: 'Active' },
      { item: 'Open unavailable assets', focus: 'Customer service impact', status: 'High' },
      { item: 'Prepare status report', focus: 'Operational status evidence', status: 'Ready' },
    ],
  },
  'point-list': {
    title: 'Point List',
    subtitle: 'Point and tag inventory view across mapping quality, source systems, and data readiness.',
    primaryAction: 'Review points',
    metrics: [
      { label: 'Points', value: '1,284', note: 'Points represented in mapping view' },
      { label: 'Mapped Tags', value: '1,126', note: 'Tags mapped to assets or systems' },
      { label: 'Quality Review', value: '73', note: 'Points requiring quality review' },
      { label: 'Evidence Links', value: '41', note: 'Point mapping evidence records' },
    ],
    rows: [
      { item: 'Review point inventory', focus: 'Point identity and system mapping', status: 'Ready' },
      { item: 'Open point quality review', focus: 'Quality and mapping gaps', status: 'Review' },
      { item: 'Check point evidence', focus: 'Mapping evidence records', status: 'Ready' },
    ],
  },
  'tag-mapping': {
    title: 'Tag Mapping',
    subtitle: 'Tag-to-asset and tag-to-system mapping quality with gaps, lineage, and evidence readiness.',
    primaryAction: 'Review tag mapping',
    metrics: [
      { label: 'Mapped Tags', value: '1,126', note: 'Tags mapped to system context' },
      { label: 'Mapping Gaps', value: '158', note: 'Tags needing mapping review' },
      { label: 'Asset Links', value: '902', note: 'Tags linked to asset records' },
      { label: 'Evidence Links', value: '41', note: 'Tag mapping evidence records' },
    ],
    rows: [
      { item: 'Review tag mapping gaps', focus: 'Tag-to-asset alignment', status: 'Review' },
      { item: 'Open mapped tags', focus: 'System and asset tag coverage', status: 'Ready' },
      { item: 'Prepare mapping evidence', focus: 'Traceable mapping records', status: 'Ready' },
    ],
  },
  'relationship-graph': {
    title: 'Relationship Graph',
    subtitle: 'Asset relationship graph across hierarchy, dependency, upstream/downstream, and evidence links.',
    primaryAction: 'Open relationship graph',
    metrics: [
      { label: 'Graph Nodes', value: '428', note: 'Asset nodes represented' },
      { label: 'Graph Edges', value: '812', note: 'Relationship edges represented' },
      { label: 'Impact Paths', value: '28', note: 'Paths requiring operational review' },
      { label: 'Data Quality', value: '91%', note: 'Relationship data completeness' },
    ],
    rows: [
      { item: 'Review relationship graph', focus: 'Asset and system dependencies', status: 'Active' },
      { item: 'Open dependency path', focus: 'Upstream and downstream impact', status: 'Review' },
      { item: 'Check graph evidence', focus: 'Relationship evidence coverage', status: 'Ready' },
    ],
  },
  'dependency-view': {
    title: 'Dependency View',
    subtitle: 'Dependency view for critical systems, assets, upstream services, downstream impact, and risk.',
    primaryAction: 'Review dependencies',
    metrics: [
      { label: 'Dependencies', value: '812', note: 'Dependencies tracked in topology' },
      { label: 'Critical Paths', value: '28', note: 'Paths with high service relevance' },
      { label: 'Impacted Assets', value: '34', note: 'Assets affected by dependency risk' },
      { label: 'Evidence Ready', value: '52', note: 'Dependency evidence records' },
    ],
    rows: [
      { item: 'Review dependency view', focus: 'Critical path and impact analysis', status: 'Active' },
      { item: 'Open impacted systems', focus: 'Systems affected by upstream assets', status: 'Review' },
      { item: 'Prepare dependency evidence', focus: 'Traceable relationship records', status: 'Ready' },
    ],
  },
  'impact-path': {
    title: 'Impact Path',
    subtitle: 'Impact path review across asset dependencies, service exposure, fault impact, and evidence linkage.',
    primaryAction: 'Review impact path',
    metrics: [
      { label: 'Impact Paths', value: '28', note: 'Paths tracked for service exposure' },
      { label: 'High Impact', value: '7', note: 'Paths requiring urgent review' },
      { label: 'Linked Faults', value: '19', note: 'Faults tied to impact paths' },
      { label: 'Evidence Ready', value: '24', note: 'Impact records with evidence' },
    ],
    rows: [
      { item: 'Review high-impact path', focus: 'Fault-to-service exposure', status: 'High' },
      { item: 'Open affected assets', focus: 'Assets and systems on path', status: 'Active' },
      { item: 'Check impact evidence', focus: 'Evidence and report linkage', status: 'Ready' },
    ],
  },
  'data-quality': {
    title: 'Data Quality',
    subtitle: 'Asset topology data quality view across completeness, mapping gaps, relationship gaps, and evidence.',
    primaryAction: 'Review data quality',
    metrics: [
      { label: 'Completeness', value: '91%', note: 'Asset topology completeness' },
      { label: 'Mapping Gaps', value: '37', note: 'Asset mapping records needing review' },
      { label: 'Relationship Gaps', value: '18', note: 'Relationship records needing review' },
      { label: 'Evidence Links', value: '44', note: 'Quality records with evidence' },
    ],
    rows: [
      { item: 'Review data quality gaps', focus: 'Completeness and mapping quality', status: 'Review' },
      { item: 'Open relationship gaps', focus: 'Dependency and topology quality', status: 'Active' },
      { item: 'Prepare quality evidence', focus: 'Quality evidence package', status: 'Ready' },
    ],
  },
}

const fallbackCustomerSection: CustomerSection = customerSections['asset-list']

function normalizeL3Id(value: unknown, defaultKey: string): string {
  const raw = typeof value === 'string' && value ? value : defaultKey
  const normalized = raw.replace(/-\d+$/, '')
  return customerSections[normalized] ? normalized : defaultKey
}

const activeCustomerSection = computed(() => customerSections[normalizeL3Id(route.query.l3, 'asset-list')] ?? fallbackCustomerSection)

const loading = ref(false)
const apiError = ref('')
const showDetailDrawer = ref(false)
const activeDetailTab = ref('overview')
const selectedAsset = ref<AssetRecord | null>(null)
const selectedRelationships = ref<AssetRelationships | null>(null)
const selectedLineage = ref<AssetTopologyLineage | null>(null)
const selectedImpact = ref<AssetImpactSkeleton | null>(null)

const health = ref<AssetsHealth>({
  status: 'unknown',
  moduleId: 'assets-topology',
  moduleName: 'Assets & Topology',
  runtimeMode: 'skeleton',
  provider: 'local-assets-provider',
  sourceSemantics: 'ibms-neutral',
  readOnly: true,
  controlActionsEnabled: false,
  discoveryEnabled: false,
  edgeRuntimeIntegrated: false,
  linkRuntimeIntegrated: false,
  dbPersistenceIntegrated: false,
  totalAssets: 0,
  runtimeLinkedAssets: 0,
  certified: false,
  iec62443Certified: false,
})

const summary = ref<AssetsSummary>({
  totalAssets: 0,
  siteCount: 0,
  buildingCount: 0,
  floorCount: 0,
  zoneCount: 0,
  systemCount: 0,
  equipmentCount: 0,
  pointCount: 0,
  activeAssets: 0,
  mockAssets: 0,
  runtimeLinkedAssets: 0,
  certifiedAssets: 0,
  iec62443CertifiedAssets: 0,
  totalRelationships: 0,
  containmentRelationships: 0,
  pointRelationships: 0,
  relatedRelationships: 0,
  rootAssets: 0,
  leafAssets: 0,
  maxHierarchyDepth: 0,
  runtimeLinkedRelationships: 0,
  topologyValidationMode: 'local-skeleton-validation',
  topologyValidated: false,
  assetTypes: [],
  assetCategories: [],
  limitations: [],
})

const topology = ref<AssetTopology>({
  topologyMode: 'local-skeleton-topology',
  nodes: [],
  edges: [],
  runtimeLinked: false,
  certified: false,
  iec62443Certified: false,
  notes: '',
  summary: {
    nodeCount: 0,
    edgeCount: 0,
    runtimeLinked: false,
  },
})

const assets = ref<AssetRecord[]>([])
const filters = reactive({
  assetType: '',
  assetCategory: '',
  lifecycleStatus: '',
  operationalStatus: '',
  siteId: '',
  systemId: '',
})

const fallbackAssets: AssetRecord[] = [
  {
    assetId: 'fallback-site',
    assetCode: 'FALLBACK-SITE',
    assetName: 'Fallback Site',
    assetType: 'site',
    assetCategory: 'location',
    lifecycleStatus: 'active',
    operationalStatus: 'online',
    siteId: 'fallback-site',
    siteName: 'Fallback Site',
    buildingId: '',
    buildingName: '',
    floorId: '',
    floorName: '',
    zoneId: '',
    zoneName: '',
    systemId: '',
    systemName: '',
    parentAssetId: '',
    childrenAssetIds: [],
    relatedAssetIds: [],
    sourceSystem: 'vantaris-one-platform',
    sourceRecordId: 'fallback-site',
    provider: 'local-assets-provider',
    runtimeMode: 'skeleton',
    sourceSemantics: 'ibms-neutral',
    mockData: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    tags: ['fallback'],
    metadata: {},
    limitations: ['Fallback mode: API data unavailable.'],
    hierarchyPath: {
      pathMode: 'local-skeleton-hierarchy',
      assetId: 'fallback-site',
      levels: [
        {
          level: 1,
          assetId: 'fallback-site',
          assetName: 'Fallback Site',
          assetType: 'site',
          relationship: 'root',
        },
      ],
      complete: true,
      runtimeLinked: false,
      notes: 'Local skeleton hierarchy; no DB or runtime topology validation.',
    },
    runtimeLinked: false,
    certified: false,
    iec62443Certified: false,
  },
]

const fallbackTopology: AssetTopology = {
  topologyMode: 'local-skeleton-topology',
  nodes: [
    {
      nodeId: 'node-fallback-site',
      assetId: 'fallback-site',
      label: 'Fallback Site',
      nodeType: 'site',
      assetCategory: 'location',
      status: 'online',
      runtimeLinked: false,
    },
  ],
  edges: [],
  runtimeLinked: false,
  certified: false,
  iec62443Certified: false,
  notes: 'Fallback local topology when API is unavailable.',
  summary: {
    nodeCount: 1,
    edgeCount: 0,
    runtimeLinked: false,
  },
}

const hasAssets = computed(() => assets.value.length > 0)

function normalizeError(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback
}

const emptyRelationshipSummary = (): AssetRelationshipSummary => ({
  parentCount: 0,
  childCount: 0,
  relatedCount: 0,
  upstreamCount: 0,
  downstreamCount: 0,
  pointCount: 0,
  equipmentCount: 0,
  systemCount: 0,
  runtimeLinkedRelationships: 0,
})

const emptyRelationshipGroups = (): AssetRelationshipGroups => ({
  parent: [],
  children: [],
  related: [],
  upstream: [],
  downstream: [],
  points: [],
  equipment: [],
  systems: [],
})

const emptyRelationshipPath = (assetId: string): AssetRelationshipPath => ({
  pathMode: 'local-skeleton-relationship-path',
  assetId,
  rootAssetId: '',
  rootToAsset: [],
  assetToLeaves: [],
  complete: false,
  runtimeLinked: false,
})

const emptyLineage = (assetId: string): AssetTopologyLineage => ({
  assetId,
  lineageMode: 'local-skeleton-lineage',
  upstream: [],
  downstream: [],
  siblings: [],
  containedAssets: [],
  containingAssets: [],
  runtimeLinked: false,
  certified: false,
  iec62443Certified: false,
  notes: 'Local topology lineage only; no runtime impact calculation.',
})

const emptyImpact = (assetId: string): AssetImpactSkeleton => ({
  assetId,
  impactMode: 'local-skeleton-impact',
  potentiallyImpactedAssets: [],
  potentiallyImpactedSystems: [],
  potentiallyImpactedZones: [],
  impactScore: null,
  impactCalculated: false,
  runtimeLinked: false,
  limitations: [
    'No runtime telemetry',
    'No telemetry correlation',
    'No EDGE/LINK integration',
    'No DB-backed dependency graph',
  ],
  certified: false,
  iec62443Certified: false,
})

function hierarchyDepth(asset: AssetRecord): number {
  return asset.hierarchyPath?.levels.length || 0
}

function relationshipCount(asset: AssetRecord): number {
  return (asset.childrenAssetIds?.length || 0) + (asset.relatedAssetIds?.length || 0) + (asset.parentAssetId ? 1 : 0)
}

async function loadAssetsPage(): Promise<void> {
  loading.value = true
  apiError.value = ''
  try {
    const [healthResult, listResult, topologyResult] = await Promise.all([
      getAssetsHealth(),
      getAssetsList(filters),
      getAssetTopology(),
    ])
    health.value = healthResult
    assets.value = listResult.items
    summary.value = listResult.summary
    topology.value = topologyResult
  } catch (error) {
    apiError.value = normalizeError(error, 'Assets API unavailable. Showing local fallback data.')
    assets.value = [...fallbackAssets]
    topology.value = { ...fallbackTopology }
    summary.value = {
      ...summary.value,
      totalAssets: fallbackAssets.length,
      siteCount: 1,
      runtimeLinkedAssets: 0,
      totalRelationships: 0,
      containmentRelationships: 0,
      pointRelationships: 0,
      relatedRelationships: 0,
      rootAssets: 1,
      leafAssets: 1,
      maxHierarchyDepth: 1,
      runtimeLinkedRelationships: 0,
      topologyValidated: false,
    }
  } finally {
    loading.value = false
  }
}

async function applyFilters(): Promise<void> {
  loading.value = true
  try {
    const listResult = await getAssetsList(filters)
    assets.value = listResult.items
    summary.value = listResult.summary
  } catch (error) {
    apiError.value = normalizeError(error, 'Assets filter request failed. Showing fallback data.')
    assets.value = [...fallbackAssets]
  } finally {
    loading.value = false
  }
}

function resetFilters(): void {
  filters.assetType = ''
  filters.assetCategory = ''
  filters.lifecycleStatus = ''
  filters.operationalStatus = ''
  filters.siteId = ''
  filters.systemId = ''
  void applyFilters()
}

async function viewDetail(assetId: string): Promise<void> {
  const row = assets.value.find((item) => item.assetId === assetId) || null
  selectedAsset.value = row
  selectedRelationships.value = null
  selectedLineage.value = emptyLineage(assetId)
  selectedImpact.value = emptyImpact(assetId)
  activeDetailTab.value = 'overview'
  showDetailDrawer.value = true
  try {
    const [detail, relationships, lineage, impact] = await Promise.all([
      getAssetDetail(assetId),
      getAssetRelationships(assetId).catch(() => ({
        assetId,
        relationshipMode: 'local-skeleton-relationships',
        parent: null,
        children: [],
        related: [],
        relationshipSummary: emptyRelationshipSummary(),
        relationshipGroups: emptyRelationshipGroups(),
        relationshipPath: emptyRelationshipPath(assetId),
        edges: [],
        runtimeLinked: false,
        certified: false,
        iec62443Certified: false,
      })),
      getAssetLineage(assetId).catch(() => emptyLineage(assetId)),
      getAssetImpact(assetId).catch(() => emptyImpact(assetId)),
    ])
    selectedAsset.value = detail
    selectedRelationships.value = relationships
    selectedLineage.value = lineage
    selectedImpact.value = impact
  } catch {
    selectedAsset.value = row
  }
}

async function viewRelationships(assetId: string): Promise<void> {
  const row = assets.value.find((item) => item.assetId === assetId) || null
  selectedAsset.value = row
  selectedRelationships.value = null
  selectedLineage.value = emptyLineage(assetId)
  selectedImpact.value = emptyImpact(assetId)
  activeDetailTab.value = 'relationships'
  showDetailDrawer.value = true
  try {
    const [detail, relationships, lineage, impact] = await Promise.all([
      getAssetDetail(assetId).catch(() => row),
      getAssetRelationships(assetId),
      getAssetLineage(assetId).catch(() => emptyLineage(assetId)),
      getAssetImpact(assetId).catch(() => emptyImpact(assetId)),
    ])
    selectedAsset.value = detail || row
    selectedRelationships.value = relationships
    selectedLineage.value = lineage
    selectedImpact.value = impact
  } catch {
    selectedRelationships.value = {
      assetId,
      relationshipMode: 'local-skeleton-relationships',
      parent: null,
      children: [],
      related: [],
      relationshipSummary: emptyRelationshipSummary(),
      relationshipGroups: emptyRelationshipGroups(),
      relationshipPath: emptyRelationshipPath(assetId),
      edges: [],
      runtimeLinked: false,
      certified: false,
      iec62443Certified: false,
    }
  }
}

onMounted(() => {
  void loadAssetsPage()
})
</script>

<template>
  <div class="assets-page">
    <el-card shadow="never" class="customer-section-card block-space">
      <div class="customer-section-head">
        <div>
          <p class="section-kicker">Selected asset section</p>
          <h2>{{ activeCustomerSection.title }}</h2>
          <p>{{ activeCustomerSection.subtitle }}</p>
        </div>
        <el-button type="primary" plain>{{ activeCustomerSection.primaryAction }}</el-button>
      </div>
      <div class="customer-metric-grid">
        <article v-for="metric in activeCustomerSection.metrics" :key="metric.label" class="customer-metric">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <em>{{ metric.note }}</em>
        </article>
      </div>
      <el-table :data="activeCustomerSection.rows" stripe border class="customer-section-table">
        <el-table-column prop="item" label="Action" min-width="240" />
        <el-table-column prop="focus" label="Focus Area" min-width="260" />
        <el-table-column prop="status" label="Status" min-width="140" />
      </el-table>
    </el-card>

    <el-alert v-if="apiError" type="warning" show-icon :closable="false" :title="customerUnavailableMessage" class="block-space" />

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Assets Summary</div>
      </template>
      <el-skeleton v-if="loading" :rows="3" animated />
      <el-descriptions v-else :column="4" border>
        <el-descriptions-item label="totalAssets">{{ summary.totalAssets }}</el-descriptions-item>
        <el-descriptions-item label="siteCount">{{ summary.siteCount }}</el-descriptions-item>
        <el-descriptions-item label="buildingCount">{{ summary.buildingCount }}</el-descriptions-item>
        <el-descriptions-item label="floorCount">{{ summary.floorCount }}</el-descriptions-item>
        <el-descriptions-item label="zoneCount">{{ summary.zoneCount }}</el-descriptions-item>
        <el-descriptions-item label="systemCount">{{ summary.systemCount }}</el-descriptions-item>
        <el-descriptions-item label="equipmentCount">{{ summary.equipmentCount }}</el-descriptions-item>
        <el-descriptions-item label="pointCount">{{ summary.pointCount }}</el-descriptions-item>
        <el-descriptions-item label="totalRelationships">{{ summary.totalRelationships }}</el-descriptions-item>
        <el-descriptions-item label="containmentRelationships">{{ summary.containmentRelationships }}</el-descriptions-item>
        <el-descriptions-item label="pointRelationships">{{ summary.pointRelationships }}</el-descriptions-item>
        <el-descriptions-item label="relatedRelationships">{{ summary.relatedRelationships }}</el-descriptions-item>
        <el-descriptions-item label="rootAssets">{{ summary.rootAssets }}</el-descriptions-item>
        <el-descriptions-item label="leafAssets">{{ summary.leafAssets }}</el-descriptions-item>
        <el-descriptions-item label="maxHierarchyDepth">{{ summary.maxHierarchyDepth }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinkedRelationships">{{ summary.runtimeLinkedRelationships }}</el-descriptions-item>
        <el-descriptions-item label="topologyValidated">{{ summary.topologyValidated }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinkedAssets">{{ summary.runtimeLinkedAssets }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Asset Filters</div>
      </template>
      <div class="filter-row">
        <el-input v-model="filters.assetType" clearable placeholder="assetType" class="filter-field" />
        <el-input v-model="filters.assetCategory" clearable placeholder="assetCategory" class="filter-field" />
        <el-input v-model="filters.lifecycleStatus" clearable placeholder="lifecycleStatus" class="filter-field" />
        <el-input v-model="filters.operationalStatus" clearable placeholder="operationalStatus" class="filter-field" />
        <el-input v-model="filters.siteId" clearable placeholder="siteId" class="filter-field" />
        <el-input v-model="filters.systemId" clearable placeholder="systemId" class="filter-field" />
        <el-button type="primary" plain @click="applyFilters">Apply</el-button>
        <el-button plain @click="resetFilters">Reset</el-button>
      </div>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Asset Table</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <el-empty v-if="!hasAssets" description="No assets available." />
        <el-table v-else :data="assets" row-key="assetId" empty-text="No assets found">
          <el-table-column prop="assetId" label="assetId" min-width="160" />
          <el-table-column prop="assetName" label="assetName" min-width="180" />
          <el-table-column prop="assetType" label="assetType" min-width="120" />
          <el-table-column prop="assetCategory" label="assetCategory" min-width="150" />
          <el-table-column prop="lifecycleStatus" label="lifecycleStatus" min-width="130" />
          <el-table-column prop="operationalStatus" label="operationalStatus" min-width="140" />
          <el-table-column prop="siteName" label="siteName" min-width="140" />
          <el-table-column prop="buildingName" label="buildingName" min-width="150" />
          <el-table-column prop="floorName" label="floorName" min-width="130" />
          <el-table-column prop="zoneName" label="zoneName" min-width="140" />
          <el-table-column prop="systemName" label="systemName" min-width="150" />
          <el-table-column prop="parentAssetId" label="parentAssetId" min-width="160" />
          <el-table-column label="hierarchyDepth" min-width="130">
            <template #default="{ row }">{{ hierarchyDepth(row) }}</template>
          </el-table-column>
          <el-table-column label="childrenCount" min-width="120">
            <template #default="{ row }">{{ row.childrenAssetIds.length }}</template>
          </el-table-column>
          <el-table-column label="relationshipCount" min-width="140">
            <template #default="{ row }">{{ relationshipCount(row) }}</template>
          </el-table-column>
          <el-table-column label="actions" min-width="180" fixed="right">
            <template #default="{ row }">
              <el-space>
                <el-button link type="primary" @click="viewDetail(row.assetId)">View Detail</el-button>
                <el-button link type="primary" @click="viewRelationships(row.assetId)">View Relationships</el-button>
              </el-space>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Topology</div>
      </template>
      <el-descriptions :column="3" border class="block-space">
        <el-descriptions-item label="topologyMode">{{ topology.topologyMode }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinked">{{ topology.runtimeLinked }}</el-descriptions-item>
        <el-descriptions-item label="nodeCount">{{ topology.summary.nodeCount }}</el-descriptions-item>
        <el-descriptions-item label="edgeCount">{{ topology.summary.edgeCount }}</el-descriptions-item>
        <el-descriptions-item label="certified">{{ topology.certified }}</el-descriptions-item>
        <el-descriptions-item label="iec62443Certified">{{ topology.iec62443Certified }}</el-descriptions-item>
      </el-descriptions>
      <el-alert type="info" show-icon :closable="false" :title="topology.notes" class="block-space" />
      <el-card shadow="never" class="block-space">
        <template #header>nodes</template>
        <el-table :data="topology.nodes" empty-text="No topology nodes">
          <el-table-column prop="nodeId" label="nodeId" min-width="180" />
          <el-table-column prop="assetId" label="assetId" min-width="160" />
          <el-table-column prop="label" label="label" min-width="180" />
          <el-table-column prop="nodeType" label="nodeType" min-width="110" />
          <el-table-column prop="assetCategory" label="assetCategory" min-width="140" />
          <el-table-column prop="status" label="status" min-width="110" />
          <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
        </el-table>
      </el-card>
      <el-card shadow="never">
        <template #header>edges</template>
        <el-table :data="topology.edges" empty-text="No topology edges">
          <el-table-column prop="edgeId" label="edgeId" min-width="180" />
          <el-table-column prop="from" label="from" min-width="170" />
          <el-table-column prop="to" label="to" min-width="170" />
          <el-table-column prop="relationship" label="relationship" min-width="140" />
          <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
        </el-table>
      </el-card>
    </el-card>

    <el-drawer v-model="showDetailDrawer" title="Asset Detail" size="60%">
      <el-empty v-if="!selectedAsset" description="No asset selected." />
      <template v-else>
        <el-tabs v-model="activeDetailTab">
          <el-tab-pane name="overview" label="Overview">
            <el-card shadow="never" class="block-space">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="assetId">{{ selectedAsset.assetId }}</el-descriptions-item>
                <el-descriptions-item label="assetName">{{ selectedAsset.assetName }}</el-descriptions-item>
                <el-descriptions-item label="assetType">{{ selectedAsset.assetType }}</el-descriptions-item>
                <el-descriptions-item label="assetCategory">{{ selectedAsset.assetCategory }}</el-descriptions-item>
                <el-descriptions-item label="lifecycleStatus">{{ selectedAsset.lifecycleStatus }}</el-descriptions-item>
                <el-descriptions-item label="operationalStatus">{{ selectedAsset.operationalStatus }}</el-descriptions-item>
                <el-descriptions-item label="parentAssetId">{{ selectedAsset.parentAssetId }}</el-descriptions-item>
                <el-descriptions-item label="certified">{{ selectedAsset.certified }}</el-descriptions-item>
                <el-descriptions-item label="iec62443Certified">{{ selectedAsset.iec62443Certified }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-tab-pane>

          <el-tab-pane name="hierarchy" label="Hierarchy Path">
            <el-card shadow="never" class="block-space">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="pathMode">{{ selectedAsset.hierarchyPath?.pathMode || 'n/a' }}</el-descriptions-item>
                <el-descriptions-item label="complete">{{ selectedAsset.hierarchyPath?.complete ?? false }}</el-descriptions-item>
                <el-descriptions-item label="notes">{{ selectedAsset.hierarchyPath?.notes || 'n/a' }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
            <el-table :data="selectedAsset.hierarchyPath?.levels || []" empty-text="No hierarchy levels">
              <el-table-column prop="level" label="level" min-width="90" />
              <el-table-column prop="assetId" label="assetId" min-width="160" />
              <el-table-column prop="assetName" label="assetName" min-width="180" />
              <el-table-column prop="assetType" label="assetType" min-width="120" />
              <el-table-column prop="relationship" label="relationship" min-width="140" />
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="relationships" label="Relationships">
            <el-card shadow="never" class="block-space">
              <el-descriptions :column="3" border>
                <el-descriptions-item label="parentCount">{{
                  selectedRelationships?.relationshipSummary.parentCount || 0
                }}</el-descriptions-item>
                <el-descriptions-item label="childCount">{{
                  selectedRelationships?.relationshipSummary.childCount || 0
                }}</el-descriptions-item>
                <el-descriptions-item label="relatedCount">{{
                  selectedRelationships?.relationshipSummary.relatedCount || 0
                }}</el-descriptions-item>
                <el-descriptions-item label="upstreamCount">{{
                  selectedRelationships?.relationshipSummary.upstreamCount || 0
                }}</el-descriptions-item>
                <el-descriptions-item label="downstreamCount">{{
                  selectedRelationships?.relationshipSummary.downstreamCount || 0
                }}</el-descriptions-item>
                <el-descriptions-item label="pointCount">{{
                  selectedRelationships?.relationshipSummary.pointCount || 0
                }}</el-descriptions-item>
                <el-descriptions-item label="equipmentCount">{{
                  selectedRelationships?.relationshipSummary.equipmentCount || 0
                }}</el-descriptions-item>
                <el-descriptions-item label="systemCount">{{
                  selectedRelationships?.relationshipSummary.systemCount || 0
                }}</el-descriptions-item>
                <el-descriptions-item label="runtimeLinkedRelationships">{{
                  selectedRelationships?.relationshipSummary.runtimeLinkedRelationships || 0
                }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>relationshipPath</template>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="pathMode">{{
                  selectedRelationships?.relationshipPath.pathMode || 'local-skeleton-relationship-path'
                }}</el-descriptions-item>
                <el-descriptions-item label="rootAssetId">{{
                  selectedRelationships?.relationshipPath.rootAssetId || 'n/a'
                }}</el-descriptions-item>
                <el-descriptions-item label="complete">{{
                  selectedRelationships?.relationshipPath.complete ?? false
                }}</el-descriptions-item>
                <el-descriptions-item label="runtimeLinked">{{
                  selectedRelationships?.relationshipPath.runtimeLinked ?? false
                }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>rootToAsset</template>
              <el-table :data="selectedRelationships?.relationshipPath.rootToAsset || []" empty-text="No root path">
                <el-table-column prop="level" label="level" min-width="90" />
                <el-table-column prop="assetId" label="assetId" min-width="150" />
                <el-table-column prop="assetName" label="assetName" min-width="180" />
                <el-table-column prop="assetType" label="assetType" min-width="120" />
              </el-table>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>group: parent</template>
              <el-table :data="selectedRelationships?.relationshipGroups.parent || []" empty-text="No parent">
                <el-table-column prop="assetId" label="assetId" min-width="160" />
                <el-table-column prop="assetName" label="assetName" min-width="180" />
                <el-table-column prop="assetType" label="assetType" min-width="120" />
              </el-table>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>group: children</template>
              <el-table :data="selectedRelationships?.relationshipGroups.children || []" empty-text="No children">
                <el-table-column prop="assetId" label="assetId" min-width="160" />
                <el-table-column prop="assetName" label="assetName" min-width="180" />
                <el-table-column prop="assetType" label="assetType" min-width="120" />
              </el-table>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>group: related</template>
              <el-table :data="selectedRelationships?.relationshipGroups.related || []" empty-text="No related assets">
                <el-table-column prop="assetId" label="assetId" min-width="160" />
                <el-table-column prop="assetName" label="assetName" min-width="180" />
                <el-table-column prop="assetType" label="assetType" min-width="120" />
              </el-table>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>group: upstream / downstream</template>
              <el-table :data="selectedRelationships?.relationshipGroups.upstream || []" empty-text="No upstream">
                <el-table-column prop="assetId" label="upstream.assetId" min-width="160" />
                <el-table-column prop="assetName" label="upstream.assetName" min-width="180" />
                <el-table-column prop="assetType" label="upstream.assetType" min-width="120" />
              </el-table>
              <el-table :data="selectedRelationships?.relationshipGroups.downstream || []" empty-text="No downstream">
                <el-table-column prop="assetId" label="downstream.assetId" min-width="160" />
                <el-table-column prop="assetName" label="downstream.assetName" min-width="180" />
                <el-table-column prop="assetType" label="downstream.assetType" min-width="120" />
              </el-table>
            </el-card>
            <el-card shadow="never">
              <template #header>group: points / equipment / systems</template>
              <el-table :data="selectedRelationships?.relationshipGroups.points || []" empty-text="No points">
                <el-table-column prop="assetId" label="point.assetId" min-width="160" />
                <el-table-column prop="assetName" label="point.assetName" min-width="180" />
              </el-table>
              <el-table :data="selectedRelationships?.relationshipGroups.equipment || []" empty-text="No equipment">
                <el-table-column prop="assetId" label="equipment.assetId" min-width="160" />
                <el-table-column prop="assetName" label="equipment.assetName" min-width="180" />
              </el-table>
              <el-table :data="selectedRelationships?.relationshipGroups.systems || []" empty-text="No systems">
                <el-table-column prop="assetId" label="system.assetId" min-width="160" />
                <el-table-column prop="assetName" label="system.assetName" min-width="180" />
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane name="lineage" label="Lineage">
            <el-card shadow="never" class="block-space">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="lineageMode">{{
                  selectedLineage?.lineageMode || 'local-skeleton-lineage'
                }}</el-descriptions-item>
                <el-descriptions-item label="runtimeLinked">{{ selectedLineage?.runtimeLinked ?? false }}</el-descriptions-item>
                <el-descriptions-item label="notes">{{ selectedLineage?.notes || 'n/a' }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>upstream</template>
              <el-table :data="selectedLineage?.upstream || []" empty-text="No upstream lineage">
                <el-table-column prop="assetId" label="assetId" min-width="160" />
                <el-table-column prop="assetName" label="assetName" min-width="180" />
                <el-table-column prop="assetType" label="assetType" min-width="120" />
              </el-table>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>downstream</template>
              <el-table :data="selectedLineage?.downstream || []" empty-text="No downstream lineage">
                <el-table-column prop="assetId" label="assetId" min-width="160" />
                <el-table-column prop="assetName" label="assetName" min-width="180" />
                <el-table-column prop="assetType" label="assetType" min-width="120" />
              </el-table>
            </el-card>
            <el-card shadow="never">
              <template #header>siblings / containedAssets / containingAssets</template>
              <el-table :data="selectedLineage?.siblings || []" empty-text="No siblings">
                <el-table-column prop="assetId" label="sibling.assetId" min-width="160" />
                <el-table-column prop="assetName" label="sibling.assetName" min-width="180" />
              </el-table>
              <el-table :data="selectedLineage?.containedAssets || []" empty-text="No contained assets">
                <el-table-column prop="assetId" label="contained.assetId" min-width="160" />
                <el-table-column prop="assetName" label="contained.assetName" min-width="180" />
              </el-table>
              <el-table :data="selectedLineage?.containingAssets || []" empty-text="No containing assets">
                <el-table-column prop="assetId" label="containing.assetId" min-width="160" />
                <el-table-column prop="assetName" label="containing.assetName" min-width="180" />
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane name="impact" label="Impact Skeleton">
            <el-card shadow="never" class="block-space">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="impactMode">{{
                  selectedImpact?.impactMode || 'local-skeleton-impact'
                }}</el-descriptions-item>
                <el-descriptions-item label="impactCalculated">{{ selectedImpact?.impactCalculated ?? false }}</el-descriptions-item>
                <el-descriptions-item label="impactScore">{{ selectedImpact?.impactScore ?? 'null' }}</el-descriptions-item>
                <el-descriptions-item label="runtimeLinked">{{ selectedImpact?.runtimeLinked ?? false }}</el-descriptions-item>
                <el-descriptions-item label="certified">{{ selectedImpact?.certified ?? false }}</el-descriptions-item>
                <el-descriptions-item label="iec62443Certified">{{
                  selectedImpact?.iec62443Certified ?? false
                }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>potentiallyImpactedAssets</template>
              <ul class="inline-list">
                <li v-for="item in selectedImpact?.potentiallyImpactedAssets || []" :key="item">{{ item }}</li>
                <li v-if="(selectedImpact?.potentiallyImpactedAssets || []).length === 0">No impacted assets in the current operational view.</li>
              </ul>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>potentiallyImpactedSystems</template>
              <ul class="inline-list">
                <li v-for="item in selectedImpact?.potentiallyImpactedSystems || []" :key="item">{{ item }}</li>
                <li v-if="(selectedImpact?.potentiallyImpactedSystems || []).length === 0">No impacted systems in the current operational view.</li>
              </ul>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>potentiallyImpactedZones</template>
              <ul class="inline-list">
                <li v-for="item in selectedImpact?.potentiallyImpactedZones || []" :key="item">{{ item }}</li>
                <li v-if="(selectedImpact?.potentiallyImpactedZones || []).length === 0">No impacted zones in the current operational view.</li>
              </ul>
            </el-card>
            <el-card shadow="never">
              <template #header>limitations</template>
              <ul class="inline-list">
                <li v-for="item in selectedImpact?.limitations || []" :key="item">{{ item }}</li>
              </ul>
            </el-card>
          </el-tab-pane>

          <el-tab-pane name="metadata" label="Metadata">
            <el-card shadow="never">
              <pre class="meta-block">{{ JSON.stringify(selectedAsset.metadata, null, 2) }}</pre>
            </el-card>
          </el-tab-pane>

          <el-tab-pane name="limitations" label="Limitations">
            <el-card shadow="never">
              <ul class="inline-list">
                <li v-for="item in selectedAsset.limitations" :key="item">{{ item }}</li>
                <li v-if="selectedAsset.limitations.length === 0">No limitations declared.</li>
              </ul>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.assets-page {
  padding: 16px;
}

.hero-card {
  border-left: 4px solid var(--el-color-primary);
}

.customer-section-card {
  border: 1px solid #dbe7e4;
}

.customer-section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.customer-section-head h2 {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 22px;
}

.customer-section-head p {
  margin: 0;
  color: #52615d;
}

.section-kicker {
  margin-bottom: 8px !important;
  color: #0f766e !important;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.customer-metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.customer-metric {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  background: #f8fbfa;
}

.customer-metric span,
.customer-metric em {
  display: block;
  color: #64748b;
  font-style: normal;
}

.customer-metric strong {
  display: block;
  margin: 6px 0;
  color: #0f766e;
  font-size: 24px;
}

.customer-section-table {
  margin-top: 16px;
}

.page-header h1 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.block-space {
  margin-bottom: 16px;
}

.section-title {
  font-weight: 600;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-field {
  width: 210px;
}

.inline-list {
  margin: 0;
  padding-left: 18px;
}

.meta-block {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
