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
  sourceReferences: string[]
  evidenceReferences: string[]
  auditReferences: string[]
  correlationReferences: string[]
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
  limitations: string[]
}

export interface EvidenceVerificationResult {
  verified: boolean
  verificationMode: string
  evidenceId: string
  evidenceHashMatches: boolean
  traceabilityHashMatches: boolean
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
    sourceReferences: asStringArray(data.sourceReferences),
    evidenceReferences: asStringArray(data.evidenceReferences),
    auditReferences: asStringArray(data.auditReferences),
    correlationReferences: asStringArray(data.correlationReferences),
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
    certified: Boolean(data.certified),
    iec62443Certified: Boolean(data.iec62443Certified),
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

