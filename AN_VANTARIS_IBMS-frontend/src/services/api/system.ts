import request from './request'

export type JsonPayload = Record<string, unknown>

export interface PermissionRecord {
  id: string
  perm_code: string
  name?: string
  description: string
  extra?: Record<string, unknown>
}

export interface PermissionPayload {
  perm_code: string
  description: string
  name?: string
  extra?: Record<string, unknown>
}

export interface PermissionUpdatePayload {
  description?: string
  name?: string
  extra?: Record<string, unknown>
}

function unwrapData<T>(body: unknown): T {
  if (typeof body === 'object' && body !== null && 'data' in body) {
    return (body as { data: T }).data
  }
  return body as T
}

function normalizePermission(raw: unknown): PermissionRecord {
  const row = raw as Record<string, unknown>
  const extra =
    typeof row.extra === 'object' && row.extra !== null
      ? (row.extra as Record<string, unknown>)
      : undefined
  const nameFromExtra = extra?.name != null ? String(extra.name) : undefined

  return {
    id: String(row.id ?? ''),
    perm_code: String(row.perm_code ?? ''),
    description: String(row.description ?? ''),
    name: nameFromExtra,
    extra,
  }
}

function toCreateBody(payload: PermissionPayload): Record<string, unknown> {
  const description = payload.description.trim() || payload.name?.trim() || ''
  const body: Record<string, unknown> = {
    perm_code: payload.perm_code.trim(),
    description,
  }
  if (payload.name?.trim()) {
    body.extra = { ...(payload.extra ?? {}), name: payload.name.trim() }
  } else if (payload.extra) {
    body.extra = payload.extra
  }
  return body
}

function toUpdateBody(payload: PermissionUpdatePayload): Record<string, unknown> {
  const body: Record<string, unknown> = {}
  if (payload.description !== undefined) {
    body.description = payload.description.trim()
  }
  if (payload.name !== undefined || payload.extra) {
    body.extra = {
      ...(payload.extra ?? {}),
      ...(payload.name !== undefined ? { name: payload.name.trim() } : {}),
    }
  }
  return body
}

export async function getSystemPermissions(): Promise<PermissionRecord[]> {
  const { data } = await request.get('/system/permissions')
  const items = unwrapData<unknown>(data)
  if (!Array.isArray(items)) {
    return []
  }
  return items.map(normalizePermission)
}

export async function createSystemPermission(payload: PermissionPayload): Promise<PermissionRecord> {
  const { data } = await request.post('/system/permissions', toCreateBody(payload))
  return normalizePermission(unwrapData<unknown>(data))
}

export async function updateSystemPermission(
  id: string,
  payload: PermissionUpdatePayload,
): Promise<PermissionRecord> {
  const { data } = await request.put(`/system/permissions/${id}`, toUpdateBody(payload))
  return normalizePermission(unwrapData<unknown>(data))
}

export async function deleteSystemPermission(id: string): Promise<void> {
  await request.delete(`/system/permissions/${id}`)
}
