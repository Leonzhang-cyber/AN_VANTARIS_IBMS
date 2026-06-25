<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ApiError } from '@/services/api/errors'
import {
  getEvidenceDetail,
  getEvidenceList,
  getEvidenceRelationships,
  getEvidenceSummary,
  getUcdeHealth,
  verifyEvidenceRecord,
  type EvidenceRelationshipGraph,
  type EvidenceRecord,
  type EvidenceSummary,
  type EvidenceVerificationResult,
  type UcdeHealth,
} from '@/services/api/ucde'

const loading = ref(false)
const apiError = ref('')
const verificationError = ref('')
const showDetailDrawer = ref(false)
const selectedEvidence = ref<EvidenceRecord | null>(null)
const selectedVerification = ref<EvidenceVerificationResult | null>(null)
const selectedRelationships = ref<EvidenceRelationshipGraph | null>(null)
const activeDetailTab = ref('overview')

const health = ref<UcdeHealth>({
  status: 'unknown',
  moduleId: 'ucde',
  moduleName: 'UCDE Evidence Center',
  runtimeMode: 'skeleton',
  provider: 'local-ucde-provider',
  sourceSemantics: 'ibms-neutral',
  readOnly: true,
  controlActionsEnabled: false,
  certified: false,
  iec62443Certified: false,
  evidenceChainMode: 'hash-only-local-evidence',
  signatureIntegrated: false,
  dbPersistenceIntegrated: false,
  ucdeRuntimeIntegrated: false,
})

const summary = ref<EvidenceSummary>({
  totalEvidence: 0,
  readinessEvidence: 0,
  auditEvidence: 0,
  platformEvidence: 0,
  hashReadyEvidence: 0,
  signedEvidence: 0,
  certifiedEvidence: 0,
  iec62443CertifiedEvidence: 0,
  sourceModules: [],
  evidenceTypes: [],
  totalSourceReferences: 0,
  totalEvidenceReferences: 0,
  totalAuditReferences: 0,
  totalCorrelationReferences: 0,
  traceabilityPathCount: 0,
  runtimeLinkedReferences: 0,
  completeTraceabilityPaths: 0,
  skeletonTraceabilityPaths: 0,
  relationshipGraphReady: false,
  limitations: [],
})

const evidenceRows = ref<EvidenceRecord[]>([])
const filters = reactive({
  evidenceType: '',
  sourceModuleId: '',
  evidenceStatus: '',
  evidenceCategory: '',
})

const fallbackEvidenceRows: EvidenceRecord[] = [
  {
    evidenceId: 'fallback-ucde-r1',
    evidenceType: 'readiness-evidence',
    evidenceName: 'UCDE Fallback Readiness Entry',
    evidenceStatus: 'foundation',
    evidenceCategory: 'module-readiness',
    sourceSystem: 'vantaris-one-platform',
    sourceModuleId: 'ucde',
    sourceRecordId: 'fallback-local',
    sourceTimestamp: new Date().toISOString(),
    capturedAt: new Date().toISOString(),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    provider: 'local-ucde-provider',
    runtimeMode: 'skeleton',
    sourceSemantics: 'ibms-neutral',
    mockData: true,
    evidenceHash: 'fallback-evidence-hash',
    traceabilityHash: 'fallback-traceability-hash',
    hashAlgorithm: 'SHA-256',
    tamperEvidenceMode: 'hash-only-local-evidence',
    certified: false,
    iec62443Certified: false,
    sourceReferences: [
      {
        referenceId: 'src-fallback-local',
        sourceModuleId: 'ucde',
        sourceRecordId: 'fallback-local',
        sourceRecordType: 'readiness-record',
        relationship: 'originated-from',
        sourceTimestamp: new Date().toISOString(),
        runtimeLinked: false,
        notes: 'Local skeleton reference only; no runtime call.',
      },
    ],
    evidenceReferences: [],
    auditReferences: [],
    correlationReferences: [],
    traceabilityPath: {
      pathId: 'trace-fallback-ucde-r1',
      pathMode: 'local-skeleton-traceability',
      sourceModuleId: 'ucde',
      sourceRecordId: 'fallback-local',
      evidenceId: 'fallback-ucde-r1',
      steps: [
        {
          stepOrder: 1,
          stepType: 'source-record',
          label: 'Source Record',
          referenceId: 'src-fallback-local',
          runtimeLinked: false,
        },
        {
          stepOrder: 2,
          stepType: 'evidence-record',
          label: 'Evidence Record',
          referenceId: 'evref-fallback-ucde-r1',
          runtimeLinked: false,
        },
        {
          stepOrder: 3,
          stepType: 'hash-verification',
          label: 'Hash Verification',
          referenceId: 'verify-fallback-ucde-r1',
          runtimeLinked: false,
        },
      ],
      complete: false,
      completionReason: 'R2 local skeleton path only; runtime source linkage is not integrated.',
      certified: false,
      iec62443Certified: false,
    },
    tags: ['fallback'],
    metadata: {},
    limitations: ['Fallback mode: API data unavailable.'],
    notes: 'Fallback local evidence list for non-blocking UI behavior.',
  },
]

const hasEvidence = computed(() => evidenceRows.value.length > 0)
const currentVerification = computed(() => {
  if (!selectedEvidence.value || !selectedVerification.value) {
    return null
  }
  return selectedVerification.value.evidenceId === selectedEvidence.value.evidenceId ? selectedVerification.value : null
})

function normalizeError(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback
}

function emptyRelationshipGraph(evidenceId: string, note = 'Relationship graph API unavailable; showing local empty skeleton.'): EvidenceRelationshipGraph {
  return {
    evidenceId,
    graphMode: 'local-skeleton-relationships',
    nodes: [],
    edges: [],
    certified: false,
    iec62443Certified: false,
    notes: note,
  }
}

async function loadEvidenceCenter(): Promise<void> {
  loading.value = true
  apiError.value = ''
  verificationError.value = ''
  selectedVerification.value = null
  try {
    const [healthResult, summaryResult, listResult] = await Promise.all([
      getUcdeHealth(),
      getEvidenceSummary(),
      getEvidenceList(filters),
    ])
    health.value = healthResult
    summary.value = summaryResult
    evidenceRows.value = listResult.items
  } catch (error) {
    apiError.value = normalizeError(error, 'UCDE API unavailable. Showing local fallback evidence list.')
    evidenceRows.value = [...fallbackEvidenceRows]
    summary.value = {
      ...summary.value,
      totalEvidence: fallbackEvidenceRows.length,
      readinessEvidence: 1,
      hashReadyEvidence: 1,
      totalSourceReferences: 1,
      traceabilityPathCount: 1,
      runtimeLinkedReferences: 0,
      completeTraceabilityPaths: 0,
      skeletonTraceabilityPaths: 1,
      relationshipGraphReady: true,
    }
  } finally {
    loading.value = false
  }
}

async function applyFilters(): Promise<void> {
  try {
    loading.value = true
    const listResult = await getEvidenceList(filters)
    evidenceRows.value = listResult.items
    summary.value = listResult.summary
  } catch (error) {
    apiError.value = normalizeError(error, 'Evidence filter request failed. Showing fallback records.')
    evidenceRows.value = [...fallbackEvidenceRows]
  } finally {
    loading.value = false
  }
}

async function viewDetail(evidenceId: string): Promise<void> {
  selectedVerification.value = null
  selectedRelationships.value = emptyRelationshipGraph(evidenceId)
  verificationError.value = ''
  const current = evidenceRows.value.find((row) => row.evidenceId === evidenceId) || null
  selectedEvidence.value = current
  activeDetailTab.value = 'overview'
  showDetailDrawer.value = true
  try {
    const [detail, relationships] = await Promise.all([
      getEvidenceDetail(evidenceId),
      getEvidenceRelationships(evidenceId).catch(() =>
        emptyRelationshipGraph(evidenceId, 'Relationship graph API unavailable; fallback to local empty graph skeleton.')
      ),
    ])
    selectedEvidence.value = detail
    selectedRelationships.value = relationships
  } catch {
    selectedEvidence.value = current
    selectedRelationships.value = emptyRelationshipGraph(
      evidenceId,
      'Detail API unavailable; fallback to local empty relationship graph skeleton.'
    )
  }
}

async function verifyHash(evidenceId: string): Promise<void> {
  verificationError.value = ''
  try {
    selectedVerification.value = await verifyEvidenceRecord(evidenceId)
    if (selectedEvidence.value?.evidenceId !== evidenceId) {
      selectedEvidence.value = evidenceRows.value.find((row) => row.evidenceId === evidenceId) || null
      showDetailDrawer.value = true
    }
  } catch (error) {
    verificationError.value = normalizeError(error, 'Verify hash failed in current environment.')
  }
}

function clearFilters(): void {
  filters.evidenceType = ''
  filters.sourceModuleId = ''
  filters.evidenceStatus = ''
  filters.evidenceCategory = ''
  void applyFilters()
}

onMounted(() => {
  void loadEvidenceCenter()
})
</script>

<template>
  <div class="ucde-page">
    <el-card shadow="never" class="hero-card block-space">
      <div class="page-header">
        <div>
          <h1>UCDE Evidence Center</h1>
          <p>Evidence chain, source traceability, decision records, audit trail, and export-ready operational evidence.</p>
        </div>
        <el-space wrap>
          <el-tag type="success">Evidence-backed review</el-tag>
          <el-tag type="info">Traceability workspace</el-tag>
          <el-tag type="warning">Audit readiness</el-tag>
        </el-space>
      </div>
    </el-card>

    <el-alert
      v-if="apiError"
      type="warning"
      show-icon
      :closable="false"
      :title="apiError"
      class="block-space"
    />

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Evidence Summary</div>
      </template>
      <el-skeleton v-if="loading" :rows="3" animated />
      <el-descriptions v-else :column="4" border>
        <el-descriptions-item label="totalEvidence">{{ summary.totalEvidence }}</el-descriptions-item>
        <el-descriptions-item label="readinessEvidence">{{ summary.readinessEvidence }}</el-descriptions-item>
        <el-descriptions-item label="auditEvidence">{{ summary.auditEvidence }}</el-descriptions-item>
        <el-descriptions-item label="platformEvidence">{{ summary.platformEvidence }}</el-descriptions-item>
        <el-descriptions-item label="hashReadyEvidence">{{ summary.hashReadyEvidence }}</el-descriptions-item>
        <el-descriptions-item label="totalSourceReferences">{{ summary.totalSourceReferences }}</el-descriptions-item>
        <el-descriptions-item label="totalEvidenceReferences">{{ summary.totalEvidenceReferences }}</el-descriptions-item>
        <el-descriptions-item label="totalAuditReferences">{{ summary.totalAuditReferences }}</el-descriptions-item>
        <el-descriptions-item label="totalCorrelationReferences">{{ summary.totalCorrelationReferences }}</el-descriptions-item>
        <el-descriptions-item label="traceabilityPathCount">{{ summary.traceabilityPathCount }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinkedReferences">{{ summary.runtimeLinkedReferences }}</el-descriptions-item>
        <el-descriptions-item label="completeTraceabilityPaths">{{ summary.completeTraceabilityPaths }}</el-descriptions-item>
        <el-descriptions-item label="skeletonTraceabilityPaths">{{ summary.skeletonTraceabilityPaths }}</el-descriptions-item>
        <el-descriptions-item label="relationshipGraphReady">{{ summary.relationshipGraphReady }}</el-descriptions-item>
        <el-descriptions-item label="signedEvidence">{{ summary.signedEvidence }}</el-descriptions-item>
        <el-descriptions-item label="certifiedEvidence">{{ summary.certifiedEvidence }}</el-descriptions-item>
        <el-descriptions-item label="iec62443CertifiedEvidence">{{ summary.iec62443CertifiedEvidence }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Evidence Filters</div>
      </template>
      <div class="filter-row">
        <el-input v-model="filters.evidenceType" placeholder="evidenceType" class="filter-field" clearable />
        <el-input v-model="filters.sourceModuleId" placeholder="sourceModuleId" class="filter-field" clearable />
        <el-input v-model="filters.evidenceStatus" placeholder="evidenceStatus" class="filter-field" clearable />
        <el-input v-model="filters.evidenceCategory" placeholder="evidenceCategory" class="filter-field" clearable />
        <el-button type="primary" plain @click="applyFilters">Apply</el-button>
        <el-button plain @click="clearFilters">Reset</el-button>
      </div>
    </el-card>

    <el-card shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Evidence Table</div>
      </template>
      <el-skeleton v-if="loading" :rows="4" animated />
      <template v-else>
        <el-empty v-if="!hasEvidence" description="No evidence records available." />
        <el-table v-else :data="evidenceRows" row-key="evidenceId" empty-text="No evidence records">
          <el-table-column prop="evidenceId" label="evidenceId" min-width="180" />
          <el-table-column prop="evidenceName" label="evidenceName" min-width="220" />
          <el-table-column prop="evidenceType" label="evidenceType" min-width="170" />
          <el-table-column prop="evidenceStatus" label="evidenceStatus" min-width="130" />
          <el-table-column prop="evidenceCategory" label="evidenceCategory" min-width="160" />
          <el-table-column prop="sourceModuleId" label="sourceModuleId" min-width="150" />
          <el-table-column prop="sourceRecordId" label="sourceRecordId" min-width="170" />
          <el-table-column label="sourceReferenceCount" min-width="160">
            <template #default="{ row }">{{ row.sourceReferences.length }}</template>
          </el-table-column>
          <el-table-column label="auditReferenceCount" min-width="150">
            <template #default="{ row }">{{ row.auditReferences.length }}</template>
          </el-table-column>
          <el-table-column label="traceabilityPathMode" min-width="200">
            <template #default="{ row }">{{ row.traceabilityPath?.pathMode || 'n/a' }}</template>
          </el-table-column>
          <el-table-column label="runtimeLinked" min-width="130">
            <template #default>
              <el-tag type="info">false</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="evidenceHash" label="evidenceHash" min-width="220" />
          <el-table-column prop="traceabilityHash" label="traceabilityHash" min-width="220" />
          <el-table-column prop="capturedAt" label="capturedAt" min-width="190" />
          <el-table-column label="actions" min-width="180" fixed="right">
            <template #default="{ row }">
              <el-space>
                <el-button link type="primary" @click="viewDetail(row.evidenceId)">View Detail</el-button>
                <el-button link type="primary" @click="verifyHash(row.evidenceId)">Verify Hash</el-button>
              </el-space>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-card>

    <el-card v-if="selectedVerification || verificationError" shadow="never" class="block-space">
      <template #header>
        <div class="section-title">Verification Result</div>
      </template>
      <el-alert
        v-if="verificationError"
        type="warning"
        show-icon
        :closable="false"
        :title="verificationError"
        class="block-space"
      />
      <el-descriptions v-if="selectedVerification" :column="2" border>
        <el-descriptions-item label="verified">{{ selectedVerification.verified }}</el-descriptions-item>
        <el-descriptions-item label="verificationMode">{{ selectedVerification.verificationMode }}</el-descriptions-item>
        <el-descriptions-item label="evidenceHashMatches">{{ selectedVerification.evidenceHashMatches }}</el-descriptions-item>
        <el-descriptions-item label="traceabilityHashMatches">{{ selectedVerification.traceabilityHashMatches }}</el-descriptions-item>
        <el-descriptions-item label="evidenceHashExpected">{{ selectedVerification.evidenceHashExpected }}</el-descriptions-item>
        <el-descriptions-item label="evidenceHashActual">{{ selectedVerification.evidenceHashActual }}</el-descriptions-item>
        <el-descriptions-item label="traceabilityHashExpected">{{
          selectedVerification.traceabilityHashExpected
        }}</el-descriptions-item>
        <el-descriptions-item label="traceabilityHashActual">{{ selectedVerification.traceabilityHashActual }}</el-descriptions-item>
        <el-descriptions-item label="sourceReferenceCount">{{ selectedVerification.sourceReferenceCount }}</el-descriptions-item>
        <el-descriptions-item label="evidenceReferenceCount">{{ selectedVerification.evidenceReferenceCount }}</el-descriptions-item>
        <el-descriptions-item label="auditReferenceCount">{{ selectedVerification.auditReferenceCount }}</el-descriptions-item>
        <el-descriptions-item label="correlationReferenceCount">{{
          selectedVerification.correlationReferenceCount
        }}</el-descriptions-item>
        <el-descriptions-item label="traceabilityPathComplete">{{
          selectedVerification.traceabilityPathComplete
        }}</el-descriptions-item>
        <el-descriptions-item label="certified">{{ selectedVerification.certified }}</el-descriptions-item>
        <el-descriptions-item label="iec62443Certified">{{ selectedVerification.iec62443Certified }}</el-descriptions-item>
      </el-descriptions>
      <el-card v-if="selectedVerification" shadow="never" class="block-space">
        <template #header>verificationNotes</template>
        <ul class="inline-list">
          <li v-for="item in selectedVerification.verificationNotes" :key="item">{{ item }}</li>
        </ul>
      </el-card>
      <el-card v-if="selectedVerification" shadow="never">
        <template #header>limitations</template>
        <ul class="inline-list">
          <li v-for="item in selectedVerification.limitations" :key="item">{{ item }}</li>
        </ul>
      </el-card>
    </el-card>

    <el-drawer v-model="showDetailDrawer" title="Evidence Detail" size="52%">
      <el-empty v-if="!selectedEvidence" description="No evidence selected." />
      <template v-else>
        <el-tabs v-model="activeDetailTab">
          <el-tab-pane name="overview" label="Overview">
            <el-card shadow="never" class="block-space">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="evidenceId">{{ selectedEvidence.evidenceId }}</el-descriptions-item>
                <el-descriptions-item label="evidenceName">{{ selectedEvidence.evidenceName }}</el-descriptions-item>
                <el-descriptions-item label="evidenceType">{{ selectedEvidence.evidenceType }}</el-descriptions-item>
                <el-descriptions-item label="evidenceStatus">{{ selectedEvidence.evidenceStatus }}</el-descriptions-item>
                <el-descriptions-item label="sourceModuleId">{{ selectedEvidence.sourceModuleId }}</el-descriptions-item>
                <el-descriptions-item label="sourceRecordId">{{ selectedEvidence.sourceRecordId }}</el-descriptions-item>
                <el-descriptions-item label="evidenceHash">{{ selectedEvidence.evidenceHash }}</el-descriptions-item>
                <el-descriptions-item label="traceabilityHash">{{ selectedEvidence.traceabilityHash }}</el-descriptions-item>
                <el-descriptions-item label="certified">{{ selectedEvidence.certified }}</el-descriptions-item>
                <el-descriptions-item label="iec62443Certified">{{ selectedEvidence.iec62443Certified }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>Tags</template>
              <ul class="inline-list">
                <li v-for="item in selectedEvidence.tags" :key="item">{{ item }}</li>
                <li v-if="selectedEvidence.tags.length === 0">No tags.</li>
              </ul>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>Metadata</template>
              <pre class="summary-block">{{ JSON.stringify(selectedEvidence.metadata, null, 2) }}</pre>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>Limitations</template>
              <ul class="inline-list">
                <li v-for="item in selectedEvidence.limitations" :key="item">{{ item }}</li>
                <li v-if="selectedEvidence.limitations.length === 0">No limitations declared.</li>
              </ul>
            </el-card>
            <el-card shadow="never">
              <template #header>Notes</template>
              <p class="notes">{{ selectedEvidence.notes }}</p>
            </el-card>
          </el-tab-pane>

          <el-tab-pane name="source" label="Source References">
            <el-table :data="selectedEvidence.sourceReferences" empty-text="No source references">
              <el-table-column prop="referenceId" label="referenceId" min-width="180" />
              <el-table-column prop="sourceModuleId" label="sourceModuleId" min-width="120" />
              <el-table-column prop="sourceRecordId" label="sourceRecordId" min-width="180" />
              <el-table-column prop="sourceRecordType" label="sourceRecordType" min-width="160" />
              <el-table-column prop="relationship" label="relationship" min-width="130" />
              <el-table-column prop="sourceTimestamp" label="sourceTimestamp" min-width="180" />
              <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
              <el-table-column prop="notes" label="notes" min-width="260" />
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="evidence" label="Evidence References">
            <el-table :data="selectedEvidence.evidenceReferences" empty-text="No evidence references">
              <el-table-column prop="referenceId" label="referenceId" min-width="180" />
              <el-table-column prop="evidenceId" label="evidenceId" min-width="180" />
              <el-table-column prop="relationship" label="relationship" min-width="130" />
              <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
              <el-table-column prop="notes" label="notes" min-width="260" />
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="audit" label="Audit References">
            <el-table :data="selectedEvidence.auditReferences" empty-text="No audit references">
              <el-table-column prop="referenceId" label="referenceId" min-width="180" />
              <el-table-column prop="auditId" label="auditId" min-width="180" />
              <el-table-column prop="auditEventType" label="auditEventType" min-width="180" />
              <el-table-column prop="sourceModuleId" label="sourceModuleId" min-width="120" />
              <el-table-column prop="relationship" label="relationship" min-width="150" />
              <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
              <el-table-column prop="notes" label="notes" min-width="260" />
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="correlation" label="Correlation References">
            <el-table :data="selectedEvidence.correlationReferences" empty-text="No correlation references">
              <el-table-column prop="referenceId" label="referenceId" min-width="180" />
              <el-table-column prop="correlationType" label="correlationType" min-width="170" />
              <el-table-column prop="relationship" label="relationship" min-width="150" />
              <el-table-column label="relatedModuleIds" min-width="220">
                <template #default="{ row }">{{ row.relatedModuleIds.join(', ') }}</template>
              </el-table-column>
              <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
              <el-table-column prop="notes" label="notes" min-width="260" />
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="traceability" label="Traceability Path">
            <el-alert
              type="info"
              show-icon
              :closable="false"
              title="Traceability links are local skeleton references in R2. Runtime source validation is not integrated."
              class="block-space"
            />
            <el-card shadow="never" class="block-space">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="pathMode">{{
                  selectedEvidence.traceabilityPath?.pathMode || 'n/a'
                }}</el-descriptions-item>
                <el-descriptions-item label="pathId">{{ selectedEvidence.traceabilityPath?.pathId || 'n/a' }}</el-descriptions-item>
                <el-descriptions-item label="complete">{{
                  selectedEvidence.traceabilityPath?.complete ?? false
                }}</el-descriptions-item>
                <el-descriptions-item label="completionReason">{{
                  selectedEvidence.traceabilityPath?.completionReason || 'n/a'
                }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
            <el-table :data="selectedEvidence.traceabilityPath?.steps || []" empty-text="No traceability steps">
              <el-table-column prop="stepOrder" label="stepOrder" min-width="110" />
              <el-table-column prop="stepType" label="stepType" min-width="170" />
              <el-table-column prop="label" label="label" min-width="170" />
              <el-table-column prop="referenceId" label="referenceId" min-width="200" />
              <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="graph" label="Relationship Graph">
            <el-card shadow="never" class="block-space">
              <el-descriptions :column="1" border>
                <el-descriptions-item label="graphMode">{{
                  selectedRelationships?.graphMode || 'local-skeleton-relationships'
                }}</el-descriptions-item>
                <el-descriptions-item label="notes">{{ selectedRelationships?.notes || 'n/a' }}</el-descriptions-item>
                <el-descriptions-item label="certified">{{ selectedRelationships?.certified ?? false }}</el-descriptions-item>
                <el-descriptions-item label="iec62443Certified">{{
                  selectedRelationships?.iec62443Certified ?? false
                }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
            <el-card shadow="never" class="block-space">
              <template #header>nodes</template>
              <el-table :data="selectedRelationships?.nodes || []" empty-text="No nodes">
                <el-table-column prop="nodeId" label="nodeId" min-width="220" />
                <el-table-column prop="nodeType" label="nodeType" min-width="130" />
                <el-table-column prop="label" label="label" min-width="220" />
                <el-table-column prop="moduleId" label="moduleId" min-width="180" />
                <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
              </el-table>
            </el-card>
            <el-card shadow="never">
              <template #header>edges</template>
              <el-table :data="selectedRelationships?.edges || []" empty-text="No edges">
                <el-table-column prop="edgeId" label="edgeId" min-width="220" />
                <el-table-column prop="from" label="from" min-width="220" />
                <el-table-column prop="to" label="to" min-width="220" />
                <el-table-column prop="relationship" label="relationship" min-width="180" />
                <el-table-column prop="runtimeLinked" label="runtimeLinked" min-width="120" />
              </el-table>
            </el-card>
          </el-tab-pane>

          <el-tab-pane name="verification" label="Verification">
            <el-card shadow="never" class="block-space">
              <el-button type="primary" plain @click="verifyHash(selectedEvidence.evidenceId)">Verify Hash</el-button>
            </el-card>
            <el-alert
              v-if="verificationError"
              type="warning"
              show-icon
              :closable="false"
              :title="verificationError"
              class="block-space"
            />
            <el-empty v-if="!currentVerification" description="Run Verify Hash to load verification details." />
            <template v-else>
              <el-card shadow="never" class="block-space">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="verificationMode">{{ currentVerification.verificationMode }}</el-descriptions-item>
                  <el-descriptions-item label="verified">{{ currentVerification.verified }}</el-descriptions-item>
                  <el-descriptions-item label="evidenceHashExpected">{{ currentVerification.evidenceHashExpected }}</el-descriptions-item>
                  <el-descriptions-item label="evidenceHashActual">{{ currentVerification.evidenceHashActual }}</el-descriptions-item>
                  <el-descriptions-item label="traceabilityHashExpected">{{
                    currentVerification.traceabilityHashExpected
                  }}</el-descriptions-item>
                  <el-descriptions-item label="traceabilityHashActual">{{
                    currentVerification.traceabilityHashActual
                  }}</el-descriptions-item>
                  <el-descriptions-item label="sourceReferenceCount">{{
                    currentVerification.sourceReferenceCount
                  }}</el-descriptions-item>
                  <el-descriptions-item label="evidenceReferenceCount">{{
                    currentVerification.evidenceReferenceCount
                  }}</el-descriptions-item>
                  <el-descriptions-item label="auditReferenceCount">{{ currentVerification.auditReferenceCount }}</el-descriptions-item>
                  <el-descriptions-item label="correlationReferenceCount">{{
                    currentVerification.correlationReferenceCount
                  }}</el-descriptions-item>
                  <el-descriptions-item label="traceabilityPathComplete">{{
                    currentVerification.traceabilityPathComplete
                  }}</el-descriptions-item>
                  <el-descriptions-item label="certified">{{ currentVerification.certified }}</el-descriptions-item>
                  <el-descriptions-item label="iec62443Certified">{{
                    currentVerification.iec62443Certified
                  }}</el-descriptions-item>
                </el-descriptions>
              </el-card>
              <el-card shadow="never" class="block-space">
                <template #header>verificationNotes</template>
                <ul class="inline-list">
                  <li v-for="item in currentVerification.verificationNotes" :key="item">{{ item }}</li>
                </ul>
              </el-card>
              <el-card shadow="never">
                <template #header>limitations</template>
                <ul class="inline-list">
                  <li v-for="item in currentVerification.limitations" :key="item">{{ item }}</li>
                </ul>
              </el-card>
            </template>
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.ucde-page {
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
  width: 220px;
}

.inline-list {
  margin: 0;
  padding-left: 18px;
}

.summary-block {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.notes {
  margin: 0;
}
</style>

