/** localStorage key for bearer access token — not a secret value */
export const TOKEN_STORAGE_KEY = 'ibms_access_token'

const storage: Storage = localStorage

export function getAccessToken(): string | null {
  try {
    return storage.getItem(TOKEN_STORAGE_KEY)
  } catch {
    return null
  }
}

export function setAccessToken(token: string): void {
  storage.setItem(TOKEN_STORAGE_KEY, token.trim())
}

export function clearAccessToken(): void {
  storage.removeItem(TOKEN_STORAGE_KEY)
}
