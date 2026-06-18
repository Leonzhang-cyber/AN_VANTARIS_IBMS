<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
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
    <el-card shadow="never" class="hero-card block-space">
      <div class="page-header">
        <div>
          <h1>Assets &amp; Topology</h1>
          <p>Read-only asset and topology workspace for VANTARIS ONE.</p>
        </div>
        <el-space wrap>
          <el-tag type="info">runtimeMode: {{ health.runtimeMode }}</el-tag>
          <el-tag type="success">provider: {{ health.provider }}</el-tag>
          <el-tag>sourceSemantics: {{ health.sourceSemantics }}</el-tag>
          <el-tag>readOnly: {{ health.readOnly }}</el-tag>
          <el-tag>discoveryEnabled: {{ health.discoveryEnabled }}</el-tag>
          <el-tag>edgeRuntimeIntegrated: {{ health.edgeRuntimeIntegrated }}</el-tag>
          <el-tag>linkRuntimeIntegrated: {{ health.linkRuntimeIntegrated }}</el-tag>
          <el-tag>certified: {{ health.certified }}</el-tag>
          <el-tag>iec62443Certified: {{ health.iec62443Certified }}</el-tag>
        </el-space>
      </div>
    </el-card>

    <el-alert
      type="info"
      show-icon
      :closable="false"
      title="Topology relationships are local skeleton references. Runtime discovery, telemetry correlation and EDGE/LINK integration are not integrated."
      class="block-space"
    />

    <el-alert v-if="apiError" type="warning" show-icon :closable="false" :title="apiError" class="block-space" />

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
                <li v-if="(selectedImpact?.potentiallyImpactedAssets || []).length === 0">No impacted assets in local skeleton.</li>
              </ul>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>potentiallyImpactedSystems</template>
              <ul class="inline-list">
                <li v-for="item in selectedImpact?.potentiallyImpactedSystems || []" :key="item">{{ item }}</li>
                <li v-if="(selectedImpact?.potentiallyImpactedSystems || []).length === 0">No impacted systems in local skeleton.</li>
              </ul>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>potentiallyImpactedZones</template>
              <ul class="inline-list">
                <li v-for="item in selectedImpact?.potentiallyImpactedZones || []" :key="item">{{ item }}</li>
                <li v-if="(selectedImpact?.potentiallyImpactedZones || []).length === 0">No impacted zones in local skeleton.</li>
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

