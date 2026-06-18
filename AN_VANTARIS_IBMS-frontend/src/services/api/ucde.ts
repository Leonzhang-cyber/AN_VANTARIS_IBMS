import request from './request'

export interface UcdeHealth {
  status: string
  moduleId: string
  moduleName: string
  runtimeMode: string
  provider: string
  sourceSemantics: string
  readOnly: boolean
  controlActionsEnabled: boolean
  certified: boolean
  iec62443Certified: boolean
  evidenceChainMode: string
  signatureIntegrated: boolean
  dbPersistenceIntegrated: boolean
  ucdeRuntimeIntegrated: boolean
}

export interface EvidenceReferenceBase {
  referenceId: string
  relationship: string
  runtimeLinked: boolean
  notes: string
}

export interface SourceReference extends EvidenceReferenceBase {
  sourceModuleId: string
  sourceRecordId: string
  sourceRecordType: string
  sourceTimestamp: string
}

export interface EvidenceReference extends EvidenceReferenceBase {
  evidenceId: string
}

export interface AuditReference extends EvidenceReferenceBase {
  auditId: string
  auditEventType: string
  sourceModuleId: string
}

export interface CorrelationReference extends EvidenceReferenceBase {
  correlationType: string
  relatedModuleIds: string[]
}

export interface TraceabilityStep {
  stepOrder: number
  stepType: string
  label: string
  referenceId: string
  runtimeLinked: boolean
}

export interface TraceabilityPath {
  pathId: string
  pathMode: string
  sourceModuleId: string
  sourceRecordId: string
  evidenceId: string
  steps: TraceabilityStep[]
  complete: boolean
  completionReason: string
  certified: boolean
  iec62443Certified: boolean
}

export interface EvidenceRelationshipNode {
  nodeId: string
  nodeType: 'evidence' | 'source' | 'audit' | 'correlation'
  label: string
  moduleId: string
  runtimeLinked: boolean
}

export interface EvidenceRelationshipEdge {
  edgeId: string
  from: string
  to: string
  relationship: string
  runtimeLinked: boolean
}

export interface EvidenceRelationshipGraph {
  evidenceId: string
  graphMode: string
  nodes: EvidenceRelationshipNode[]
  edges: EvidenceRelationshipEdge[]
  certified: boolean
  iec62443Certified: boolean
  notes: string
}

export interface EvidenceRecord {
  evidenceId: string
  evidenceType: string
  evidenceName: string
  evidenceStatus: string
  evidenceCategory: string
  sourceSystem: string
  sourceModuleId: string
  sourceRecordId: string
  sourceTimestamp: string
  capturedAt: string
  createdAt: string
  updatedAt: string
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  evidenceHash: string
  traceabilityHash: string
  hashAlgorithm: string
  tamperEvidenceMode: string
  certified: boolean
  iec62443Certified: boolean
  sourceReferences: SourceReference[]
  evidenceReferences: EvidenceReference[]
  auditReferences: AuditReference[]
  correlationReferences: CorrelationReference[]
  traceabilityPath: TraceabilityPath | null
  tags: string[]
  metadata: Record<string, unknown>
  limitations: string[]
  notes: string
}

export interface EvidenceSummary {
  totalEvidence: number
  readinessEvidence: number
  auditEvidence: number
  platformEvidence: number
  hashReadyEvidence: number
  signedEvidence: number
  certifiedEvidence: number
  iec62443CertifiedEvidence: number
  sourceModules: string[]
  evidenceTypes: string[]
  totalSourceReferences: number
  totalEvidenceReferences: number
  totalAuditReferences: number
  totalCorrelationReferences: number
  traceabilityPathCount: number
  runtimeLinkedReferences: number
  completeTraceabilityPaths: number
  skeletonTraceabilityPaths: number
  relationshipGraphReady: boolean
  limitations: string[]
}

export interface EvidenceVerificationResult {
  verified: boolean
  verificationMode: string
  evidenceId: string
  evidenceHashMatches: boolean
  traceabilityHashMatches: boolean
  evidenceHashExpected: string
  evidenceHashActual: string
  traceabilityHashExpected: string
  traceabilityHashActual: string
  sourceReferenceCount: number
  evidenceReferenceCount: number
  auditReferenceCount: number
  correlationReferenceCount: number
  traceabilityPathComplete: boolean
  verificationNotes: string[]
  limitations: string[]
  certified: boolean
  iec62443Certified: boolean
}

export interface EvidenceListResponse {
  items: EvidenceRecord[]
  total: number
  filters: {
    evidenceType: string
    sourceModuleId: string
    evidenceStatus: string
    evidenceCategory: string
  }
  summary: EvidenceSummary
  provider: string
  runtimeMode: string
  sourceSemantics: string
  mockData: boolean
  readOnly: boolean
  certified: boolean
  iec62443Certified: boolean
}

export interface GetEvidenceListParams {
  evidenceType?: string
  sourceModuleId?: string
  evidenceStatus?: string
  evidenceCategory?: string
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
}

function asStringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map((item) => String(item)) : []
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value)
    ? value.filter((item) => typeof item === 'object' && item !== null).map((item) => item as Record<string, unknown>)
    : []
}

function unwrapData<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

function normalizeHealth(raw: unknown): UcdeHealth {
  const data = asRecord(raw)
  return {
    status: String(data.status ?? 'unknown'),
    moduleId: String(data.moduleId ?? 'ucde'),
    moduleName: String(data.moduleName ?? 'UCDE Evidence Center'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    provider: String(data.provider ?? 'local-ucde-provider'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    controlActionsEnabled: Boolean(data.controlActionsEnabled),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    evidenceChainMode: String(data.evidenceChainMode ?? 'hash-only-local-evidence'),
    signatureIntegrated: Boolean(data.signatureIntegrated),
    dbPersistenceIntegrated: Boolean(data.dbPersistenceIntegrated),
    ucdeRuntimeIntegrated: Boolean(data.ucdeRuntimeIntegrated),
  }
}

function normalizeEvidenceRecord(raw: unknown): EvidenceRecord {
  const data = asRecord(raw)
  return {
    evidenceId: String(data.evidenceId ?? ''),
    evidenceType: String(data.evidenceType ?? ''),
    evidenceName: String(data.evidenceName ?? ''),
    evidenceStatus: String(data.evidenceStatus ?? 'foundation'),
    evidenceCategory: String(data.evidenceCategory ?? ''),
    sourceSystem: String(data.sourceSystem ?? 'vantaris-one-platform'),
    sourceModuleId: String(data.sourceModuleId ?? ''),
    sourceRecordId: String(data.sourceRecordId ?? ''),
    sourceTimestamp: String(data.sourceTimestamp ?? ''),
    capturedAt: String(data.capturedAt ?? ''),
    createdAt: String(data.createdAt ?? ''),
    updatedAt: String(data.updatedAt ?? ''),
    provider: String(data.provider ?? 'local-ucde-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    evidenceHash: String(data.evidenceHash ?? ''),
    traceabilityHash: String(data.traceabilityHash ?? ''),
    hashAlgorithm: String(data.hashAlgorithm ?? 'SHA-256'),
    tamperEvidenceMode: String(data.tamperEvidenceMode ?? 'hash-only-local-evidence'),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    sourceReferences: asRecordArray(data.sourceReferences).map((item) => normalizeSourceReference(item)),
    evidenceReferences: asRecordArray(data.evidenceReferences).map((item) => normalizeEvidenceReference(item)),
    auditReferences: asRecordArray(data.auditReferences).map((item) => normalizeAuditReference(item)),
    correlationReferences: asRecordArray(data.correlationReferences).map((item) => normalizeCorrelationReference(item)),
    traceabilityPath: normalizeTraceabilityPath(data.traceabilityPath),
    tags: asStringArray(data.tags),
    metadata: asRecord(data.metadata),
    limitations: asStringArray(data.limitations),
    notes: String(data.notes ?? ''),
  }
}

function normalizeEvidenceSummary(raw: unknown): EvidenceSummary {
  const data = asRecord(raw)
  return {
    totalEvidence: Number(data.totalEvidence ?? 0),
    readinessEvidence: Number(data.readinessEvidence ?? 0),
    auditEvidence: Number(data.auditEvidence ?? 0),
    platformEvidence: Number(data.platformEvidence ?? 0),
    hashReadyEvidence: Number(data.hashReadyEvidence ?? 0),
    signedEvidence: Number(data.signedEvidence ?? 0),
    certifiedEvidence: Number(data.certifiedEvidence ?? 0),
    iec62443CertifiedEvidence: Number(data.iec62443CertifiedEvidence ?? 0),
    sourceModules: asStringArray(data.sourceModules),
    evidenceTypes: asStringArray(data.evidenceTypes),
    totalSourceReferences: Number(data.totalSourceReferences ?? 0),
    totalEvidenceReferences: Number(data.totalEvidenceReferences ?? 0),
    totalAuditReferences: Number(data.totalAuditReferences ?? 0),
    totalCorrelationReferences: Number(data.totalCorrelationReferences ?? 0),
    traceabilityPathCount: Number(data.traceabilityPathCount ?? 0),
    runtimeLinkedReferences: Number(data.runtimeLinkedReferences ?? 0),
    completeTraceabilityPaths: Number(data.completeTraceabilityPaths ?? 0),
    skeletonTraceabilityPaths: Number(data.skeletonTraceabilityPaths ?? 0),
    relationshipGraphReady: Boolean(data.relationshipGraphReady),
    limitations: asStringArray(data.limitations),
  }
}

function normalizeEvidenceVerification(raw: unknown): EvidenceVerificationResult {
  const data = asRecord(raw)
  return {
    verified: Boolean(data.verified),
    verificationMode: String(data.verificationMode ?? 'hash-only-local-evidence'),
    evidenceId: String(data.evidenceId ?? ''),
    evidenceHashMatches: Boolean(data.evidenceHashMatches),
    traceabilityHashMatches: Boolean(data.traceabilityHashMatches),
    evidenceHashExpected: String(data.evidenceHashExpected ?? ''),
    evidenceHashActual: String(data.evidenceHashActual ?? ''),
    traceabilityHashExpected: String(data.traceabilityHashExpected ?? ''),
    traceabilityHashActual: String(data.traceabilityHashActual ?? ''),
    sourceReferenceCount: Number(data.sourceReferenceCount ?? 0),
    evidenceReferenceCount: Number(data.evidenceReferenceCount ?? 0),
    auditReferenceCount: Number(data.auditReferenceCount ?? 0),
    correlationReferenceCount: Number(data.correlationReferenceCount ?? 0),
    traceabilityPathComplete: Boolean(data.traceabilityPathComplete),
    verificationNotes: asStringArray(data.verificationNotes),
    limitations: asStringArray(data.limitations),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeReferenceBase(raw: unknown): EvidenceReferenceBase {
  const data = asRecord(raw)
  return {
    referenceId: String(data.referenceId ?? ''),
    relationship: String(data.relationship ?? ''),
    runtimeLinked: Boolean(data.runtimeLinked),
    notes: String(data.notes ?? ''),
  }
}

function normalizeSourceReference(raw: unknown): SourceReference {
  const data = asRecord(raw)
  const base = normalizeReferenceBase(data)
  return {
    ...base,
    sourceModuleId: String(data.sourceModuleId ?? ''),
    sourceRecordId: String(data.sourceRecordId ?? ''),
    sourceRecordType: String(data.sourceRecordType ?? ''),
    sourceTimestamp: String(data.sourceTimestamp ?? ''),
  }
}

function normalizeEvidenceReference(raw: unknown): EvidenceReference {
  const data = asRecord(raw)
  const base = normalizeReferenceBase(data)
  return {
    ...base,
    evidenceId: String(data.evidenceId ?? ''),
  }
}

function normalizeAuditReference(raw: unknown): AuditReference {
  const data = asRecord(raw)
  const base = normalizeReferenceBase(data)
  return {
    ...base,
    auditId: String(data.auditId ?? ''),
    auditEventType: String(data.auditEventType ?? ''),
    sourceModuleId: String(data.sourceModuleId ?? ''),
  }
}

function normalizeCorrelationReference(raw: unknown): CorrelationReference {
  const data = asRecord(raw)
  const base = normalizeReferenceBase(data)
  return {
    ...base,
    correlationType: String(data.correlationType ?? ''),
    relatedModuleIds: asStringArray(data.relatedModuleIds),
  }
}

function normalizeTraceabilityStep(raw: unknown): TraceabilityStep {
  const data = asRecord(raw)
  return {
    stepOrder: Number(data.stepOrder ?? 0),
    stepType: String(data.stepType ?? ''),
    label: String(data.label ?? ''),
    referenceId: String(data.referenceId ?? ''),
    runtimeLinked: Boolean(data.runtimeLinked),
  }
}

function normalizeTraceabilityPath(raw: unknown): TraceabilityPath | null {
  if (!raw || typeof raw !== 'object') {
    return null
  }
  const data = asRecord(raw)
  return {
    pathId: String(data.pathId ?? ''),
    pathMode: String(data.pathMode ?? ''),
    sourceModuleId: String(data.sourceModuleId ?? ''),
    sourceRecordId: String(data.sourceRecordId ?? ''),
    evidenceId: String(data.evidenceId ?? ''),
    steps: asRecordArray(data.steps).map((item) => normalizeTraceabilityStep(item)),
    complete: Boolean(data.complete),
    completionReason: String(data.completionReason ?? ''),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

function normalizeRelationshipNode(raw: unknown): EvidenceRelationshipNode {
  const data = asRecord(raw)
  return {
    nodeId: String(data.nodeId ?? ''),
    nodeType: String(data.nodeType ?? 'evidence') as EvidenceRelationshipNode['nodeType'],
    label: String(data.label ?? ''),
    moduleId: String(data.moduleId ?? ''),
    runtimeLinked: Boolean(data.runtimeLinked),
  }
}

function normalizeRelationshipEdge(raw: unknown): EvidenceRelationshipEdge {
  const data = asRecord(raw)
  return {
    edgeId: String(data.edgeId ?? ''),
    from: String(data.from ?? ''),
    to: String(data.to ?? ''),
    relationship: String(data.relationship ?? ''),
    runtimeLinked: Boolean(data.runtimeLinked),
  }
}

function normalizeRelationshipGraph(raw: unknown): EvidenceRelationshipGraph {
  const data = asRecord(raw)
  return {
    evidenceId: String(data.evidenceId ?? ''),
    graphMode: String(data.graphMode ?? 'local-skeleton-relationships'),
    nodes: asRecordArray(data.nodes).map((item) => normalizeRelationshipNode(item)),
    edges: asRecordArray(data.edges).map((item) => normalizeRelationshipEdge(item)),
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
    notes: String(data.notes ?? ''),
  }
}

function normalizeEvidenceList(raw: unknown): EvidenceListResponse {
  const data = asRecord(raw)
  const filters = asRecord(data.filters)
  return {
    items: Array.isArray(data.items) ? data.items.map((item) => normalizeEvidenceRecord(item)) : [],
    total: Number(data.total ?? 0),
    filters: {
      evidenceType: String(filters.evidenceType ?? ''),
      sourceModuleId: String(filters.sourceModuleId ?? ''),
      evidenceStatus: String(filters.evidenceStatus ?? ''),
      evidenceCategory: String(filters.evidenceCategory ?? ''),
    },
    summary: normalizeEvidenceSummary(data.summary),
    provider: String(data.provider ?? 'local-ucde-provider'),
    runtimeMode: String(data.runtimeMode ?? 'skeleton'),
    sourceSemantics: String(data.sourceSemantics ?? 'ibms-neutral'),
    mockData: data.mockData !== undefined ? Boolean(data.mockData) : true,
    readOnly: data.readOnly !== undefined ? Boolean(data.readOnly) : true,
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
  }
}

export async function getUcdeHealth(): Promise<UcdeHealth> {
  const { data } = await request.get('/v1/ucde/health')
  return normalizeHealth(unwrapData<unknown>(data))
}

export async function getEvidenceList(params: GetEvidenceListParams = {}): Promise<EvidenceListResponse> {
  const { data } = await request.get('/v1/ucde/evidence', { params })
  return normalizeEvidenceList(unwrapData<unknown>(data))
}

export async function getEvidenceDetail(evidenceId: string): Promise<EvidenceRecord> {
  const { data } = await request.get(`/v1/ucde/evidence/${encodeURIComponent(evidenceId)}`)
  return normalizeEvidenceRecord(unwrapData<unknown>(data))
}

export async function getEvidenceSummary(): Promise<EvidenceSummary> {
  const { data } = await request.get('/v1/ucde/evidence/summary')
  return normalizeEvidenceSummary(unwrapData<unknown>(data))
}

export async function verifyEvidenceRecord(evidenceId: string): Promise<EvidenceVerificationResult> {
  const { data } = await request.get(`/v1/ucde/evidence/${encodeURIComponent(evidenceId)}/verify`)
  return normalizeEvidenceVerification(unwrapData<unknown>(data))
}

export async function getEvidenceRelationships(evidenceId: string): Promise<EvidenceRelationshipGraph> {
  const { data } = await request.get(`/v1/ucde/evidence/${encodeURIComponent(evidenceId)}/relationships`)
  return normalizeRelationshipGraph(unwrapData<unknown>(data))
}

