import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios'
import { getAccessToken } from '../auth/token'
import { ApiError, isForbidden, isUnauthorized, normalizeApiError } from './errors'

export type AuthErrorHandler = (error: ApiError) => void

let unauthorizedHandler: AuthErrorHandler | null = null
let forbiddenHandler: AuthErrorHandler | null = null

export function setUnauthorizedHandler(handler: AuthErrorHandler | null): void {
  unauthorizedHandler = handler
}

export function setForbiddenHandler(handler: AuthErrorHandler | null): void {
  forbiddenHandler = handler
}

export function resolveBaseUrl(): string {
  const envUrl = import.meta.env.VITE_IBMS_API_BASE_URL
  if (typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl.trim().replace(/\/$/, '')
  }
  return '/api'
}

export const request: AxiosInstance = axios.create({
  baseURL: resolveBaseUrl(),
  timeout: 120_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

request.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

request.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    const apiError = normalizeApiError(error)

    if (isUnauthorized(apiError.status)) {
      unauthorizedHandler?.(apiError)
    } else if (isForbidden(apiError.status)) {
      forbiddenHandler?.(apiError)
    }

    return Promise.reject(apiError)
  },
)

export default request
