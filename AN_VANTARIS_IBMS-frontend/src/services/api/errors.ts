export class ApiError extends Error {
  readonly status?: number
  readonly code?: string
  readonly details?: unknown

  constructor(message: string, status?: number, code?: string, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

export function isUnauthorized(status?: number): boolean {
  return status === 401
}

export function isForbidden(status?: number): boolean {
  return status === 403
}

interface AxiosLikeError {
  message?: string
  response?: {
    status?: number
    data?: {
      message?: string
      code?: string
    }
  }
}

export function normalizeApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error
  }

  if (typeof error === 'object' && error !== null && 'response' in error) {
    const axiosError = error as AxiosLikeError
    const status = axiosError.response?.status
    const data = axiosError.response?.data
    const message = data?.message ?? axiosError.message ?? 'Request failed'
    return new ApiError(message, status, data?.code, data)
  }

  if (error instanceof Error) {
    return new ApiError(error.message)
  }

  return new ApiError('Unknown error')
}
