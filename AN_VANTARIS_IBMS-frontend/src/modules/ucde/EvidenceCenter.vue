<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
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
  'evidence-chain': {
    title: 'Evidence Chain',
    subtitle: 'Traceable evidence chain across source records, operational actions, decisions, and export readiness.',
    primaryAction: 'Review evidence chain',
    metrics: [
      { label: 'Evidence Records', value: '128', note: 'Records ready for customer review' },
      { label: 'Complete Chains', value: '96', note: 'Records with complete traceability' },
      { label: 'Pending Linkage', value: '12', note: 'Records requiring source linkage' },
      { label: 'Export Ready', value: '22', note: 'Evidence packages ready for export' },
    ],
    rows: [
      { item: 'Review evidence chain', focus: 'Source-to-report traceability', status: 'Ready' },
      { item: 'Open pending linkage', focus: 'Source relationship review', status: 'Review' },
      { item: 'Prepare evidence export', focus: 'Customer-ready package', status: 'Ready' },
    ],
  },
  'source-evidence': {
    title: 'Source Evidence',
    subtitle: 'Source evidence records from alarms, assets, work orders, sustainability, and reports.',
    primaryAction: 'Review source evidence',
    metrics: [
      { label: 'Source Records', value: '74', note: 'Source records represented' },
      { label: 'Module Sources', value: '8', note: 'Modules linked to evidence' },
      { label: 'Open Reviews', value: '9', note: 'Source records requiring review' },
      { label: 'Verified Links', value: '61', note: 'Source links ready for review' },
    ],
    rows: [
      { item: 'Review source evidence', focus: 'Source module and record context', status: 'Ready' },
      { item: 'Open source review items', focus: 'Source quality and linkage', status: 'Review' },
      { item: 'Check source report links', focus: 'Report and evidence alignment', status: 'Ready' },
    ],
  },
  'decision-evidence': {
    title: 'Decision Evidence',
    subtitle: 'Decision evidence view for approvals, operational decisions, policy gates, and audit review.',
    primaryAction: 'Review decision evidence',
    metrics: [
      { label: 'Decision Records', value: '18', note: 'Decision evidence records' },
      { label: 'Approval Links', value: '11', note: 'Records linked to approvals' },
      { label: 'Open Reviews', value: '4', note: 'Decision records needing review' },
      { label: 'Export Ready', value: '7', note: 'Decision packages ready' },
    ],
    rows: [
      { item: 'Review decision evidence', focus: 'Decision owner and approval chain', status: 'Review' },
      { item: 'Open approval chain', focus: 'Policy and signoff evidence', status: 'Active' },
      { item: 'Prepare decision package', focus: 'Audit-ready decision record', status: 'Ready' },
    ],
  },
  'fault-evidence': {
    title: 'Fault Evidence',
    subtitle: 'Fault evidence records linked to alarms, impacted assets, work orders, and root cause review.',
    primaryAction: 'Review fault evidence',
    metrics: [
      { label: 'Fault Records', value: '31', note: 'Fault evidence records' },
      { label: 'Alarm Links', value: '24', note: 'Faults linked to alarm records' },
      { label: 'WO Links', value: '18', note: 'Faults linked to work orders' },
      { label: 'Open Reviews', value: '6', note: 'Fault evidence needing review' },
    ],
    rows: [
      { item: 'Review fault evidence', focus: 'Alarm and fault correlation', status: 'Active' },
      { item: 'Open impacted asset evidence', focus: 'Asset and service impact', status: 'Review' },
      { item: 'Prepare RCA evidence', focus: 'Root cause evidence package', status: 'Ready' },
    ],
  },
  'maintenance-evidence': {
    title: 'Maintenance Evidence',
    subtitle: 'Maintenance evidence for work order closure, preventive maintenance, assignments, and SLA review.',
    primaryAction: 'Review maintenance evidence',
    metrics: [
      { label: 'WO Evidence', value: '42', note: 'Work order evidence records' },
      { label: 'Closure Ready', value: '8', note: 'Closure evidence packages' },
      { label: 'PM Evidence', value: '14', note: 'Preventive maintenance evidence' },
      { label: 'SLA Evidence', value: '7', note: 'SLA evidence records' },
    ],
    rows: [
      { item: 'Review work order evidence', focus: 'Maintenance closure and SLA', status: 'Review' },
      { item: 'Open preventive evidence', focus: 'PM checklist and schedule evidence', status: 'Ready' },
      { item: 'Prepare closure package', focus: 'Customer closure review', status: 'Ready' },
    ],
  },
  'energy-evidence': {
    title: 'Energy Evidence',
    subtitle: 'Energy and sustainability evidence records for exceptions, baselines, ESG metrics, and reporting.',
    primaryAction: 'Review energy evidence',
    metrics: [
      { label: 'Energy Evidence', value: '42', note: 'Energy evidence records' },
      { label: 'Exception Links', value: '13', note: 'Records linked to exceptions' },
      { label: 'ESG Links', value: '19', note: 'Records linked to ESG metrics' },
      { label: 'Reports Ready', value: '6', note: 'Report-ready evidence bundles' },
    ],
    rows: [
      { item: 'Review energy evidence', focus: 'Energy and ESG traceability', status: 'Ready' },
      { item: 'Open exception evidence', focus: 'Energy anomaly records', status: 'Review' },
      { item: 'Prepare ESG evidence export', focus: 'Customer sustainability package', status: 'Ready' },
    ],
  },
  'report-evidence': {
    title: 'Report Evidence',
    subtitle: 'Report evidence chains for operations, maintenance, ESG, compliance, and customer delivery reports.',
    primaryAction: 'Review report evidence',
    metrics: [
      { label: 'Report Evidence', value: '36', note: 'Evidence records linked to reports' },
      { label: 'Report Packs', value: '9', note: 'Report packs with evidence' },
      { label: 'Open Reviews', value: '5', note: 'Report evidence requiring review' },
      { label: 'Export Ready', value: '12', note: 'Report evidence packages ready' },
    ],
    rows: [
      { item: 'Review report evidence', focus: 'Report-to-evidence linkage', status: 'Ready' },
      { item: 'Open report evidence review', focus: 'Customer report traceability', status: 'Review' },
      { item: 'Prepare report evidence export', focus: 'Evidence bundle export', status: 'Ready' },
    ],
  },
  'hash-signature': {
    title: 'Hash / Signature',
    subtitle: 'Verification view for evidence hashes, signature readiness, tamper review, and audit trace.',
    primaryAction: 'Review verification',
    metrics: [
      { label: 'Hash Ready', value: '128', note: 'Evidence records with hash values' },
      { label: 'Signature Ready', value: '37', note: 'Records ready for signature review' },
      { label: 'Tamper Review', value: '3', note: 'Records requiring verification review' },
      { label: 'Audit Ready', value: '91', note: 'Records ready for audit review' },
    ],
    rows: [
      { item: 'Review hash status', focus: 'Evidence integrity review', status: 'Ready' },
      { item: 'Open signature review', focus: 'Signature and approval record', status: 'Review' },
      { item: 'Prepare verification package', focus: 'Audit-ready verification output', status: 'Ready' },
    ],
  },
  'export-evidence': {
    title: 'Export Evidence',
    subtitle: 'Evidence export workspace for customer handoff, report packages, compliance, and audit trail.',
    primaryAction: 'Prepare export',
    metrics: [
      { label: 'Export Ready', value: '22', note: 'Evidence packages ready for export' },
      { label: 'Customer Packs', value: '7', note: 'Customer handoff evidence packs' },
      { label: 'Compliance Packs', value: '5', note: 'Compliance evidence packages' },
      { label: 'Open Reviews', value: '4', note: 'Exports requiring review' },
    ],
    rows: [
      { item: 'Review export queue', focus: 'Evidence bundles and reports', status: 'Ready' },
      { item: 'Open customer handoff evidence', focus: 'Customer delivery package', status: 'Ready' },
      { item: 'Check export audit trail', focus: 'Export evidence review', status: 'Ready' },
    ],
  },
  'version-control': {
    title: 'Version Control',
    subtitle: 'Document and evidence version control view for revision history, approvals, and audit readiness.',
    primaryAction: 'Review versions',
    metrics: [
      { label: 'Versioned Records', value: '64', note: 'Records with version history' },
      { label: 'Open Revisions', value: '8', note: 'Revisions requiring review' },
      { label: 'Approved Versions', value: '51', note: 'Versions accepted for use' },
      { label: 'Audit Links', value: '44', note: 'Versions linked to audit trail' },
    ],
    rows: [
      { item: 'Review version history', focus: 'Revision and approval state', status: 'Ready' },
      { item: 'Open revision review', focus: 'Pending version changes', status: 'Review' },
      { item: 'Prepare version evidence', focus: 'Document audit trail', status: 'Ready' },
    ],
  },
  'approval-workflow': {
    title: 'Approval Workflow',
    subtitle: 'Approval workflow evidence view for signoff chains, policy review, and closure records.',
    primaryAction: 'Review approvals',
    metrics: [
      { label: 'Approval Records', value: '29', note: 'Approval evidence records' },
      { label: 'Pending Review', value: '6', note: 'Approvals needing review' },
      { label: 'Closure Records', value: '17', note: 'Closure records accepted' },
      { label: 'Evidence Links', value: '26', note: 'Approvals linked to evidence' },
    ],
    rows: [
      { item: 'Review approval workflow', focus: 'Approval chain and owner', status: 'Review' },
      { item: 'Open closure approvals', focus: 'Work order and report closure', status: 'Active' },
      { item: 'Prepare approval evidence', focus: 'Signoff evidence package', status: 'Ready' },
    ],
  },
  'document-audit-trail': {
    title: 'Document Audit Trail',
    subtitle: 'Document audit trail across revisions, approval events, export records, and evidence linkage.',
    primaryAction: 'Review audit trail',
    metrics: [
      { label: 'Audit Events', value: '88', note: 'Document audit events recorded' },
      { label: 'Revision Events', value: '27', note: 'Revision events under tracking' },
      { label: 'Approval Events', value: '29', note: 'Approval events linked' },
      { label: 'Export Events', value: '12', note: 'Export events with evidence' },
    ],
    rows: [
      { item: 'Review document audit trail', focus: 'Version, approval and export history', status: 'Ready' },
      { item: 'Open audit review items', focus: 'Events requiring review', status: 'Review' },
      { item: 'Prepare audit evidence export', focus: 'Customer audit package', status: 'Ready' },
    ],
  },
}

const fallbackCustomerSection = customerSections['evidence-chain']

function normalizeL3Id(value: unknown, defaultKey: string): string {
  const raw = typeof value === 'string' && value ? value : defaultKey
  const normalized = raw.replace(/-\d+$/, '')
  return customerSections[normalized] ? normalized : defaultKey
}

const activeCustomerSection = computed(() => customerSections[normalizeL3Id(route.query.l3, 'evidence-chain')] ?? fallbackCustomerSection)

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
      completionReason: 'Traceability path is shown from the latest available operational view.',
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
    <el-card shadow="never" class="customer-section-card block-space">
      <div class="customer-section-head">
        <div>
          <p class="section-kicker">Selected evidence section</p>
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
      <el-row :gutter="12" class="block-space">
        <el-col :xs="24" :md="8">
          <el-card shadow="never">
            <template #header>Evidence Pain Points</template>
            <ul class="inline-list">
              <li>{{ activeCustomerSection.title }} must prove the business conclusion, not only list files.</li>
              <li>Closure risk increases when source object, owner action, or signature is missing.</li>
              <li>Report export is weak if evidence is not tied to asset, fault, work order, or decision context.</li>
            </ul>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-card shadow="never">
            <template #header>Recommended Actions</template>
            <ul class="inline-list">
              <li>Verify source evidence before accepting decision or closure evidence.</li>
              <li>Attach missing signature, attachment, or related object before export.</li>
              <li>Escalate incomplete evidence when it blocks customer handoff or audit readiness.</li>
            </ul>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-card shadow="never">
            <template #header>Customer Value</template>
            <ul class="inline-list">
              <li>Evidence chain supports defensible closure and report export.</li>
              <li>Verification readiness reduces dispute during customer acceptance.</li>
              <li>Audit trail shows who acted, why, and what proof supports the action.</li>
            </ul>
          </el-card>
        </el-col>
      </el-row>
      <el-table :data="activeCustomerSection.rows" stripe border class="customer-section-table">
        <el-table-column prop="item" label="Action" min-width="240" />
        <el-table-column prop="focus" label="Focus Area" min-width="260" />
        <el-table-column prop="status" label="Status" min-width="140" />
      </el-table>
    </el-card>

    <el-alert
      v-if="apiError"
      type="warning"
      show-icon
      :closable="false"
      :title="customerUnavailableMessage"
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
              title="Traceability links are shown from the latest available operational view."
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
