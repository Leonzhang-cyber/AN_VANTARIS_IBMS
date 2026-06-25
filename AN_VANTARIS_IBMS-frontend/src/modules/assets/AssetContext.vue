<template>
  <main class="asset-context">
    <RouteL3ContentPanel />

    <section class="hero">
      <div>
        <p class="eyebrow">VANTARIS ONE</p>
        <h1>Asset Context</h1>
        <p class="subtitle">
          Unified Asset / System / Event / Work Order / Evidence Linkage for customer preview review.
        </p>
      </div>
      <div class="hero-badges">
        <span>Read-only Mode</span>
        <span>Customer Preview</span>
        <span>Skeleton Runtime</span>
      </div>
    </section>

    <section class="cards">
      <article v-for="card in summaryCards" :key="card.label" class="metric-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
      </article>
    </section>

    <section class="workspace">
      <div class="table-panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">Unified Context</p>
            <h2>Asset context table</h2>
          </div>
          <span>{{ assets.length }} assets</span>
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Asset</th>
                <th>System</th>
                <th>Status</th>
                <th>Work Orders</th>
                <th>Events</th>
                <th>Evidence</th>
                <th>Reports</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="asset in assets"
                :key="asset.assetId"
                :class="{ selected: selectedAsset?.assetId === asset.assetId }"
                @click="selectAsset(asset.assetId)"
              >
                <td>
                  <strong>{{ asset.assetName }}</strong>
                  <small>{{ asset.assetType }} / {{ asset.assetId }}</small>
                </td>
                <td>{{ asset.systemName }}</td>
                <td><span class="status">{{ asset.operationalStatus || 'readonly' }}</span></td>
                <td>{{ asset.relationshipSummary.workOrderCount ?? 0 }}</td>
                <td>{{ asset.relationshipSummary.eventCount ?? 0 }}</td>
                <td>{{ asset.relationshipSummary.evidenceCount ?? 0 }}</td>
                <td>{{ asset.relationshipSummary.reportCount ?? 0 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <aside class="detail-panel">
        <div class="section-head">
          <div>
            <p class="eyebrow">Selected asset</p>
            <h2>{{ selectedAsset?.assetName || 'Asset detail' }}</h2>
          </div>
        </div>
        <dl v-if="selectedAsset">
          <div><dt>Asset ID</dt><dd>{{ selectedAsset.assetId }}</dd></div>
          <div><dt>System</dt><dd>{{ selectedAsset.systemName }}</dd></div>
          <div><dt>Site</dt><dd>{{ selectedAsset.siteId || 'readonly reference' }}</dd></div>
          <div><dt>Zone</dt><dd>{{ selectedAsset.zoneId || 'readonly reference' }}</dd></div>
        </dl>
        <div class="trace">
          <span v-for="step in detail?.traceabilityPath || []" :key="step">{{ step }}</span>
        </div>
      </aside>
    </section>

    <section class="matrix">
      <div class="section-head">
        <div>
          <p class="eyebrow">Linkage matrix</p>
          <h2>Asset to operational evidence chain</h2>
        </div>
        <span>{{ graph.summary.nodeCount }} nodes / {{ graph.summary.edgeCount }} edges</span>
      </div>
      <div class="matrix-grid">
        <article v-for="group in linkageGroups" :key="group.title">
          <h3>{{ group.title }}</h3>
          <ul>
            <li v-for="item in group.items" :key="item">{{ item }}</li>
            <li v-if="!group.items.length">Read-only reference pending</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="lower-grid">
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Guardrails</p>
            <h2>Read-only guardrails panel</h2>
          </div>
        </div>
        <ul class="guardrails">
          <li v-for="item in summary.guardrails" :key="item">{{ item }}</li>
        </ul>
      </article>
      <article>
        <div class="section-head">
          <div>
            <p class="eyebrow">Limitations</p>
            <h2>Not Production GA note</h2>
          </div>
        </div>
        <ul class="guardrails">
          <li>Read-only projection for customer preview review.</li>
          <li>No production activation.</li>
          <li v-for="item in limitations" :key="item">{{ item }}</li>
        </ul>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import {
  getAssetContextAssets,
  getAssetContextDetail,
  getAssetContextGraph,
  getAssetContextSummary,
  type AssetContextDetail,
  type AssetContextGraph,
  type AssetContextItem,
  type AssetContextSummary,
} from '@/services/api/assetContext'

const emptySummary: AssetContextSummary = {
  scope: 'ASSET_CONTEXT_GA_R1',
  visualStyle: 'VANTARIS_LIGHT_OPERATIONS_CONSOLE',
  readOnly: true,
  runtimeEnabled: false,
  dbWriteEnabled: false,
  assetGraphWriteEnabled: false,
  edgeCommandExecution: false,
  linkCommandExecution: false,
  deviceControlEnabled: false,
  productionActivation: false,
  totalAssets: 0,
  totalSystems: 0,
  totalDevices: 0,
  totalEvents: 0,
  totalWorkOrders: 0,
  totalEvidence: 0,
  totalReports: 0,
  totalPanels: 0,
  linkedObjectTypes: [],
  guardrails: [],
  limitations: [],
}

const summary = ref<AssetContextSummary>(emptySummary)
const assets = ref<AssetContextItem[]>([])
const detail = ref<AssetContextDetail | null>(null)
const graph = ref<AssetContextGraph>({ graphMode: 'local-readonly-asset-context-projection', nodes: [], edges: [], summary: { nodeCount: 0, edgeCount: 0 } })
const selectedAssetId = ref('')

const selectedAsset = computed(() => assets.value.find((item) => item.assetId === selectedAssetId.value) || assets.value[0] || null)

const summaryCards = computed(() => [
  { label: 'Assets', value: summary.value.totalAssets },
  { label: 'Systems', value: summary.value.totalSystems },
  { label: 'Devices', value: summary.value.totalDevices },
  { label: 'Events', value: summary.value.totalEvents },
  { label: 'Work Orders', value: summary.value.totalWorkOrders },
  { label: 'Evidence', value: summary.value.totalEvidence },
  { label: 'Reports', value: summary.value.totalReports },
  { label: 'UHMI Panels', value: summary.value.totalPanels },
])

const limitations = computed(() => [...summary.value.limitations, ...(detail.value?.limitations || [])])

function labelRows(rows: Record<string, unknown>[], keys: string[]): string[] {
  return rows.slice(0, 4).map((row) => {
    for (const key of keys) {
      if (row[key]) return String(row[key])
    }
    return 'Read-only reference'
  })
}

const linkageGroups = computed(() => [
  { title: 'Asset -> Work Orders', items: labelRows(detail.value?.workOrders || [], ['workOrderName', 'workOrderId', 'title']) },
  { title: 'Work Orders -> Events', items: labelRows(detail.value?.events || [], ['title', 'eventId']) },
  { title: 'Events -> Evidence', items: labelRows(detail.value?.evidence || [], ['evidenceName', 'evidenceId', 'title']) },
  { title: 'Evidence -> Reports', items: labelRows(detail.value?.reports || [], ['reportName', 'reportId']) },
  { title: 'Reports -> UHMI Panels', items: labelRows(detail.value?.uhmiPanels || [], ['panelName', 'panelId']) },
  { title: 'Customer Delivery -> Foundation Diagnostics', items: labelRows([...(detail.value?.customerDelivery || []), ...(detail.value?.foundationDiagnostics || [])], ['itemName', 'packageName', 'checkName']) },
])

async function selectAsset(assetId: string) {
  selectedAssetId.value = assetId
  detail.value = await getAssetContextDetail(assetId)
}

onMounted(async () => {
  const [summaryData, assetData, graphData] = await Promise.all([
    getAssetContextSummary(),
    getAssetContextAssets(),
    getAssetContextGraph(),
  ])
  summary.value = summaryData
  assets.value = assetData.items
  graph.value = graphData
  if (assets.value[0]) {
    await selectAsset(assets.value[0].assetId)
  }
})
</script>

<style scoped>
.asset-context {
  min-height: 100vh;
  background: #f7fbf9;
  color: #17211f;
  padding: 28px;
}

.hero,
.workspace,
.matrix,
.lower-grid > article {
  background: #ffffff;
  border: 1px solid #dce9e3;
  border-radius: 8px;
  box-shadow: 0 12px 28px rgba(24, 57, 48, 0.08);
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
}

.eyebrow {
  color: #247668;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
  margin: 0 0 8px;
  text-transform: uppercase;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

h1 {
  font-size: 34px;
  margin-bottom: 10px;
}

h2 {
  font-size: 18px;
  margin-bottom: 0;
}

h3 {
  font-size: 14px;
  margin-bottom: 12px;
}

.subtitle {
  color: #596a65;
  max-width: 760px;
  margin-bottom: 0;
}

.hero-badges,
.trace {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-badges span,
.trace span,
.status {
  background: #e8f5f0;
  border: 1px solid #c8e4d8;
  border-radius: 999px;
  color: #176255;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 10px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin: 18px 0;
}

.metric-card {
  background: #ffffff;
  border: 1px solid #dce9e3;
  border-radius: 8px;
  padding: 18px;
}

.metric-card span {
  color: #66736f;
  display: block;
  font-size: 12px;
  margin-bottom: 8px;
}

.metric-card strong {
  font-size: 28px;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(300px, 0.8fr);
  gap: 18px;
  padding: 18px;
}

.section-head {
  align-items: flex-start;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.section-head > span {
  color: #247668;
  font-size: 12px;
  font-weight: 800;
}

.table-wrap {
  overflow-x: auto;
}

table {
  border-collapse: collapse;
  min-width: 860px;
  width: 100%;
}

th,
td {
  border-bottom: 1px solid #e3ede8;
  padding: 12px;
  text-align: left;
}

th {
  color: #60716c;
  font-size: 12px;
  text-transform: uppercase;
}

td small {
  color: #71827d;
  display: block;
  margin-top: 4px;
}

tbody tr {
  cursor: pointer;
}

tbody tr.selected {
  background: #eef8f4;
}

.detail-panel {
  border-left: 1px solid #e3ede8;
  padding-left: 18px;
}

dl div {
  border-bottom: 1px solid #e3ede8;
  padding: 12px 0;
}

dt {
  color: #60716c;
  font-size: 12px;
}

dd {
  font-weight: 700;
  margin: 4px 0 0;
}

.matrix {
  margin-top: 18px;
  padding: 18px;
}

.matrix-grid,
.lower-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.matrix-grid article {
  background: #f8fcfa;
  border: 1px solid #dce9e3;
  border-radius: 8px;
  padding: 16px;
}

ul {
  margin: 0;
  padding-left: 18px;
}

li {
  color: #4e625c;
  margin: 8px 0;
}

.lower-grid {
  margin-top: 18px;
}

.lower-grid > article {
  padding: 18px;
}

.guardrails {
  columns: 2;
}

@media (max-width: 1100px) {
  .cards,
  .workspace,
  .matrix-grid,
  .lower-grid {
    grid-template-columns: 1fr;
  }

  .detail-panel {
    border-left: 0;
    border-top: 1px solid #e3ede8;
    padding-left: 0;
    padding-top: 18px;
  }
}
</style>
