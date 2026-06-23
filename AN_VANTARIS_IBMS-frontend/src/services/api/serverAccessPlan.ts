import request from './request'

export interface ServerAccessSummary {
  appServerIp: string
  dbServerIp: string
  accessWindowStatus: string
  approvalsRequired: number
  allowedCommandCount: number
  forbiddenActionCount: number
  evidenceCaptureItems: number
  stopConditionCount: number
  readyForR3: boolean
  readyForSSH: boolean
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

function summary(raw: unknown): ServerAccessSummary {
  const data = asRecord(raw)
  return {
    appServerIp: String(data.appServerIp ?? '192.168.60.21'),
    dbServerIp: String(data.dbServerIp ?? '192.168.60.22'),
    accessWindowStatus: String(data.accessWindowStatus ?? 'PLANNING_ONLY'),
    approvalsRequired: Number(data.approvalsRequired ?? 0),
    allowedCommandCount: Number(data.allowedCommandCount ?? 0),
    forbiddenActionCount: Number(data.forbiddenActionCount ?? 0),
    evidenceCaptureItems: Number(data.evidenceCaptureItems ?? 0),
    stopConditionCount: Number(data.stopConditionCount ?? 0),
    readyForR3: Boolean(data.readyForR3),
    readyForSSH: Boolean(data.readyForSSH),
    readyForDeployment: Boolean(data.readyForDeployment),
    productionGaStatus: String(data.productionGaStatus ?? 'NOT_YET'),
  }
}

export async function getServerAccessSummary(): Promise<ServerAccessSummary> {
  return summary(unwrap(await request.get('/v1/one/server-access-plan/summary')))
}

export async function getAccessWindow(): Promise<Record<string, unknown>> {
  return asRecord(unwrap(await request.get('/v1/one/server-access-plan/access-window')))
}

export async function getApprovalBoundary(): Promise<Record<string, unknown>[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-access-plan/approval-boundary')))
  return asArray(data.items)
}

export async function getReadonlyCommands(): Promise<Record<string, unknown>[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-access-plan/allowed-readonly-commands')))
  return asArray(data.items)
}

export async function getEvidenceCapture(): Promise<Record<string, unknown>> {
  return asRecord(unwrap(await request.get('/v1/one/server-access-plan/evidence-capture')))
}

export async function getStopConditions(): Promise<Record<string, unknown>[]> {
  const data = asRecord(unwrap(await request.get('/v1/one/server-access-plan/stop-conditions')))
  return asArray(data.items)
}

export async function getR3Readiness(): Promise<Record<string, unknown>> {
  return asRecord(unwrap(await request.get('/v1/one/server-access-plan/r3-readiness')))
}

export function listStrings(value: unknown): string[] {
  return asStrings(value)
}

