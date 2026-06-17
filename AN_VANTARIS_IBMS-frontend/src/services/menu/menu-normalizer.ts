import type { AppMenuItem } from './types'

type UnknownRecord = Record<string, unknown>

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function readString(value: unknown): string | undefined {
  if (typeof value === 'string' && value.trim()) {
    return value.trim()
  }
  if (typeof value === 'number' && Number.isFinite(value)) {
    return String(value)
  }
  return undefined
}

function sanitizePath(value: unknown): string {
  const raw = readString(value)
  if (!raw) {
    return '#'
  }
  if (raw.startsWith('http://') || raw.startsWith('https://')) {
    return '#'
  }
  if (raw.startsWith('/')) {
    return raw
  }
  if (raw === '#') {
    return '#'
  }
  return `/${raw.replace(/^\/+/, '')}`
}

function extractMenuArray(raw: unknown): unknown[] {
  if (Array.isArray(raw)) {
    return raw
  }
  if (!isRecord(raw)) {
    return []
  }

  const nestedData = raw.data
  if (Array.isArray(nestedData)) {
    return nestedData
  }
  if (isRecord(nestedData)) {
    for (const key of ['list', 'menus', 'items', 'records'] as const) {
      const candidate = nestedData[key]
      if (Array.isArray(candidate)) {
        return candidate
      }
    }
  }

  for (const key of ['menus', 'list', 'items', 'records'] as const) {
    const candidate = raw[key]
    if (Array.isArray(candidate)) {
      return candidate
    }
  }

  return []
}

function normalizeMenuNode(entry: unknown, index: number): AppMenuItem | null {
  if (!isRecord(entry)) {
    return null
  }

  const label =
    readString(entry.label) ??
    readString(entry.title) ??
    readString(entry.name) ??
    readString(entry.menuName) ??
    readString(entry.menu_name) ??
    `Menu ${index + 1}`

  const id =
    readString(entry.id) ??
    readString(entry.menu_id) ??
    readString(entry.code) ??
    readString(entry.menu_code) ??
    `${label}-${index}`

  const path = sanitizePath(
    entry.path ?? entry.route ?? entry.url ?? entry.menu_path ?? entry.router,
  )

  const permission = readString(entry.permission) ?? readString(entry.perm_code)

  const rawChildren = entry.children ?? entry.subMenus ?? entry.sub_menus
  let children: AppMenuItem[] | undefined
  if (Array.isArray(rawChildren)) {
    children = rawChildren
      .map((child, childIndex) => normalizeMenuNode(child, childIndex))
      .filter((child): child is AppMenuItem => child !== null)
    if (children.length === 0) {
      children = undefined
    }
  }

  return {
    id,
    label,
    path,
    icon: readString(entry.icon),
    permission,
    children,
    source: 'backend',
  }
}

/** Normalize backend menu payloads into AppMenuItem[] without dynamic code execution */
export function normalizeBackendMenu(raw: unknown): AppMenuItem[] {
  const entries = extractMenuArray(raw)
  const normalized = entries
    .map((entry, index) => normalizeMenuNode(entry, index))
    .filter((item): item is AppMenuItem => item !== null)

  return normalized
}
