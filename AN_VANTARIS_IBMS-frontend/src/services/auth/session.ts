import { clearAccessToken, getAccessToken, setAccessToken } from './token'

export const USER_INFO_STORAGE_KEY = 'ibms_user_info'

export interface SessionInfo {
  token: string | null
  isAuthenticated: boolean
}

type UnknownRecord = Record<string, unknown>

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function readTokenField(value: unknown): string | null {
  if (typeof value === 'string' && value.trim()) {
    return value.trim()
  }
  return null
}

/** Extract JWT from common backend / wrapper response shapes */
export function extractAccessToken(response: unknown): string | null {
  if (!isRecord(response)) {
    return null
  }

  const direct =
    readTokenField(response.token) ?? readTokenField(response.access_token)
  if (direct) {
    return direct
  }

  if (isRecord(response.data)) {
    return (
      readTokenField(response.data.token) ??
      readTokenField(response.data.access_token)
    )
  }

  return null
}

export function persistLoginSession(
  token: string,
  userInfo?: UnknownRecord,
): void {
  setAccessToken(token)
  if (userInfo) {
    try {
      localStorage.setItem(USER_INFO_STORAGE_KEY, JSON.stringify(userInfo))
    } catch {
      // storage unavailable — token still persisted
    }
  }
}

export function getCurrentSession(): SessionInfo {
  const token = getAccessToken()
  return {
    token,
    isAuthenticated: Boolean(token && token.length > 0),
  }
}

export function isAuthenticated(): boolean {
  return getCurrentSession().isAuthenticated
}

/** Clears local session only — does not call backend logout API */
export function logoutLocal(): void {
  clearAccessToken()
  try {
    localStorage.removeItem(USER_INFO_STORAGE_KEY)
  } catch {
    // storage unavailable — baseline noop
  }
}
