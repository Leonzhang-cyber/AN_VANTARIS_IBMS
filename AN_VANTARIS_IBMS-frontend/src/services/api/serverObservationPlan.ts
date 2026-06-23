import request from './request'

export interface ServerObservationSummary {
  appServerIp: string
  dbServerIp: string
  observationStatus: string
  executionSequenceCount: number
  appObservationCommandCount: number
  dbObservationCommandCount: number
  evidencePackageItemCount: number
  stopConditionCount: number
  approvalChecklistCount: number
  readyForActualSSH: boolean
  readyForDeployment: boolean
  productionGaStatus: string
}

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {}
}

function asArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.filter((item) => typeof item === 'object' && item !== null).map((item) => item as Record<string, unknown>) : []
}

function asStrings(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String) : []
}

function unwrap<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) return (body as { data: T }).data
  return body as T
}

function summary(raw: unknown): ServerObservationSummary {
  const data = asRecord(raw)
  return {
    appServerIp: String(data.appServerIp ?? '192.168.60.21'),
    dbServerIp: String(data.dbServerIp ?? '192.168.60.22'),
    observationStatus: String(data.observationStatus ?? 'PLANNING_ONLY'),
    executionSequenceCount: Number(data.executionSequenceCount ?? 0),
    appObservationCommandCount: Number(data.appObservationCommandCount ?? 0),
    dbObservationCommandCount: Number(data.dbObservationCommandCount ?? 0),
    evidencePackageItemCount: Number(data.evidencePackageItemCount ?? 0),
    stopConditionCount: Number(data.stopConditionCount ?? 0),
    approvalChecklistCount: Number(data.approvalChecklistCount ?? 0),
    readyForActualSSH: Boolean(data.readyForActualSSH),
    readyForDeployment: Boolean(data.readyForDeployment),
    productionGaStatus: String(data.productionGaStatus ?? 'NOT_YET'),
  }
}

export async function getServerObservationSummary(): Promise<ServerObservationSummary> {
  return summary(unwrap(await request.get('/v1/one/server-observation-plan/summary')))
}

export async function getExecutionSequence(): Promise<Record<string, unknown>[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-observation-plan/execution-sequence')))
  return asArray(data.items)
}

export async function getAppServerObservation(): Promise<Record<string, unknown>> {
  return asRecord(unwrap(await request.get('/v1/one/server-observation-plan/app-server-observation')))
}

export async function getDbServerObservation(): Promise<Record<string, unknown>> {
  return asRecord(unwrap(await request.get('/v1/one/server-observation-plan/db-server-observation')))
}

export async function getObservationEvidencePackage(): Promise<Record<string, unknown>> {
  return asRecord(unwrap(await request.get('/v1/one/server-observation-plan/evidence-package')))
}

export async function getObservationStopConditions(): Promise<Record<string, unknown>[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-observation-plan/stop-conditions')))
  return asArray(data.items)
}

export async function getApprovalChecklist(): Promise<Record<string, unknown>[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-observation-plan/approval-checklist')))
  return asArray(data.items)
}

export async function getObservationGuardrails(): Promise<string[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-observation-plan/guardrails')))
  return asStrings(data.guardrails)
}

export function listStrings(value: unknown): string[] {
  return asStrings(value)
}

export function listRecords(value: unknown): Record<string, unknown>[] {
  return asArray(value)
}
