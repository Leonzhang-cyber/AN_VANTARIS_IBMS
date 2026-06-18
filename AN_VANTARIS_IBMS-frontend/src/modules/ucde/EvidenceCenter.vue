<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ApiError } from '@/services/api/errors'
import {
  getEvidenceDetail,
  getEvidenceList,
  getEvidenceSummary,
  getUcdeHealth,
  verifyEvidenceRecord,
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
    sourceReferences: ['ucde:fallback'],
    evidenceReferences: [],
    auditReferences: [],
    correlationReferences: [],
    tags: ['fallback'],
    metadata: {},
    limitations: ['Fallback mode: API data unavailable.'],
    notes: 'Fallback local evidence list for non-blocking UI behavior.',
  },
]

const hasEvidence = computed(() => evidenceRows.value.length > 0)

function normalizeError(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback
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
  verificationError.value = ''
  const current = evidenceRows.value.find((row) => row.evidenceId === evidenceId) || null
  selectedEvidence.value = current
  showDetailDrawer.value = true
  try {
    selectedEvidence.value = await getEvidenceDetail(evidenceId)
  } catch {
    selectedEvidence.value = current
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
          <p>Read-only evidence and traceability workspace for VANTARIS ONE.</p>
        </div>
        <el-space wrap>
          <el-tag type="info">runtimeMode: {{ health.runtimeMode }}</el-tag>
          <el-tag type="success">provider: {{ health.provider }}</el-tag>
          <el-tag>sourceSemantics: {{ health.sourceSemantics }}</el-tag>
          <el-tag type="warning">evidenceChainMode: {{ health.evidenceChainMode }}</el-tag>
          <el-tag>readOnly: {{ health.readOnly }}</el-tag>
          <el-tag>certified: {{ health.certified }}</el-tag>
          <el-tag>iec62443Certified: {{ health.iec62443Certified }}</el-tag>
        </el-space>
      </div>
    </el-card>

    <el-alert
      type="info"
      show-icon
      :closable="false"
      title="UCDE R1 uses hash-only local evidence for traceability readiness. It is not a formal evidence chain or certification proof."
      class="block-space"
    />

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
        <el-descriptions-item label="certified">{{ selectedVerification.certified }}</el-descriptions-item>
        <el-descriptions-item label="iec62443Certified">{{ selectedVerification.iec62443Certified }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-drawer v-model="showDetailDrawer" title="Evidence Detail" size="52%">
      <el-empty v-if="!selectedEvidence" description="No evidence selected." />
      <template v-else>
        <el-card shadow="never" class="block-space">
          <template #header>Overview</template>
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
          <template #header>Source References</template>
          <ul class="inline-list">
            <li v-for="item in selectedEvidence.sourceReferences" :key="item">{{ item }}</li>
            <li v-if="selectedEvidence.sourceReferences.length === 0">No source references.</li>
          </ul>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>Evidence References</template>
          <ul class="inline-list">
            <li v-for="item in selectedEvidence.evidenceReferences" :key="item">{{ item }}</li>
            <li v-if="selectedEvidence.evidenceReferences.length === 0">No evidence references.</li>
          </ul>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>Audit References</template>
          <ul class="inline-list">
            <li v-for="item in selectedEvidence.auditReferences" :key="item">{{ item }}</li>
            <li v-if="selectedEvidence.auditReferences.length === 0">No audit references.</li>
          </ul>
        </el-card>

        <el-card shadow="never" class="block-space">
          <template #header>Correlation References</template>
          <ul class="inline-list">
            <li v-for="item in selectedEvidence.correlationReferences" :key="item">{{ item }}</li>
            <li v-if="selectedEvidence.correlationReferences.length === 0">No correlation references.</li>
          </ul>
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

