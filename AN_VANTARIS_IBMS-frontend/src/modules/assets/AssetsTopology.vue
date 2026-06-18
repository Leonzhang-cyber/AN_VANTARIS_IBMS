<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ApiError } from '@/services/api/errors'
import {
  getAssetDetail,
  getAssetRelationships,
  getAssetsHealth,
  getAssetsList,
  getAssetTopology,
  type AssetRecord,
  type AssetRelationships,
  type AssetsHealth,
  type AssetsSummary,
  type AssetTopology,
} from '@/services/api/assets'

const loading = ref(false)
const apiError = ref('')
const showDetailDrawer = ref(false)
const selectedAsset = ref<AssetRecord | null>(null)
const selectedRelationships = ref<AssetRelationships | null>(null)

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
  showDetailDrawer.value = true
  try {
    selectedAsset.value = await getAssetDetail(assetId)
  } catch {
    selectedAsset.value = row
  }
}

async function viewRelationships(assetId: string): Promise<void> {
  const row = assets.value.find((item) => item.assetId === assetId) || null
  selectedAsset.value = row
  selectedRelationships.value = null
  showDetailDrawer.value = true
  try {
    const [detail, relationships] = await Promise.all([
      getAssetDetail(assetId).catch(() => row),
      getAssetRelationships(assetId),
    ])
    selectedAsset.value = detail || row
    selectedRelationships.value = relationships
  } catch {
    selectedRelationships.value = {
      assetId,
      relationshipMode: 'local-skeleton-relationships',
      parent: null,
      children: [],
      related: [],
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
      title="Assets R1 uses local skeleton topology. Runtime discovery, EDGE/LINK integration and DB persistence are not integrated."
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

    <el-drawer v-model="showDetailDrawer" title="Asset Detail" size="52%">
      <el-empty v-if="!selectedAsset" description="No asset selected." />
      <template v-else>
        <el-card shadow="never" class="block-space">
          <template #header>overview</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="assetId">{{ selectedAsset.assetId }}</el-descriptions-item>
            <el-descriptions-item label="assetName">{{ selectedAsset.assetName }}</el-descriptions-item>
            <el-descriptions-item label="assetType">{{ selectedAsset.assetType }}</el-descriptions-item>
            <el-descriptions-item label="assetCategory">{{ selectedAsset.assetCategory }}</el-descriptions-item>
            <el-descriptions-item label="lifecycleStatus">{{ selectedAsset.lifecycleStatus }}</el-descriptions-item>
            <el-descriptions-item label="operationalStatus">{{ selectedAsset.operationalStatus }}</el-descriptions-item>
            <el-descriptions-item label="certified">{{ selectedAsset.certified }}</el-descriptions-item>
            <el-descriptions-item label="iec62443Certified">{{ selectedAsset.iec62443Certified }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>location hierarchy</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="siteName">{{ selectedAsset.siteName }}</el-descriptions-item>
            <el-descriptions-item label="buildingName">{{ selectedAsset.buildingName }}</el-descriptions-item>
            <el-descriptions-item label="floorName">{{ selectedAsset.floorName }}</el-descriptions-item>
            <el-descriptions-item label="zoneName">{{ selectedAsset.zoneName }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>system hierarchy</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="systemId">{{ selectedAsset.systemId }}</el-descriptions-item>
            <el-descriptions-item label="systemName">{{ selectedAsset.systemName }}</el-descriptions-item>
            <el-descriptions-item label="parentAssetId">{{ selectedAsset.parentAssetId }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>parent / children / related</template>
          <el-descriptions :column="1" border class="block-space">
            <el-descriptions-item label="relationshipMode">{{
              selectedRelationships?.relationshipMode || 'local-skeleton-relationships'
            }}</el-descriptions-item>
            <el-descriptions-item label="runtimeLinked">{{ selectedRelationships?.runtimeLinked ?? false }}</el-descriptions-item>
          </el-descriptions>
          <el-table :data="selectedRelationships?.parent ? [selectedRelationships.parent] : []" empty-text="No parent">
            <el-table-column prop="assetId" label="parent.assetId" min-width="160" />
            <el-table-column prop="assetName" label="parent.assetName" min-width="180" />
            <el-table-column prop="assetType" label="parent.assetType" min-width="120" />
          </el-table>
          <el-card shadow="never" class="block-space">
            <template #header>children</template>
            <el-table :data="selectedRelationships?.children || []" empty-text="No children">
              <el-table-column prop="assetId" label="assetId" min-width="160" />
              <el-table-column prop="assetName" label="assetName" min-width="180" />
              <el-table-column prop="assetType" label="assetType" min-width="120" />
            </el-table>
          </el-card>
          <el-card shadow="never">
            <template #header>related</template>
            <el-table :data="selectedRelationships?.related || []" empty-text="No related assets">
              <el-table-column prop="assetId" label="assetId" min-width="160" />
              <el-table-column prop="assetName" label="assetName" min-width="180" />
              <el-table-column prop="assetType" label="assetType" min-width="120" />
            </el-table>
          </el-card>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>metadata</template>
          <pre class="meta-block">{{ JSON.stringify(selectedAsset.metadata, null, 2) }}</pre>
        </el-card>

        <el-card shadow="never">
          <template #header>limitations</template>
          <ul class="inline-list">
            <li v-for="item in selectedAsset.limitations" :key="item">{{ item }}</li>
            <li v-if="selectedAsset.limitations.length === 0">No limitations declared.</li>
          </ul>
        </el-card>
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

