import request from './request'

export interface LoginPayload {
  username: string
  password: string
  otp: string
}

export interface LoginUser {
  username: string
  displayName: string
  role: string
  permissions: string[]
}

export interface LoginResponse {
  token: string
  user: LoginUser
}

const LOCAL_REVIEW_USERNAME = 'admin'
const LOCAL_REVIEW_PASSWORD = 'Admin@2026'
const LOCAL_REVIEW_OTP = '260624'

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  try {
    const { data } = await request.post('/v1/auth/login', payload)
    return data as LoginResponse
  } catch (error) {
    if (import.meta.env.DEV && isLocalReviewCredential(payload)) {
      return {
        token: 'local-2fa-customer-ga-review-token',
        user: {
          username: payload.username,
          displayName: 'VANTARIS Administrator',
          role: 'Admin',
          permissions: ['platform:read', 'system:read', 'audit:read'],
        },
      }
    }

    throw error
  }
}

function isLocalReviewCredential(payload: LoginPayload): boolean {
  return (
    payload.username.trim() === LOCAL_REVIEW_USERNAME &&
    payload.password === LOCAL_REVIEW_PASSWORD &&
    payload.otp.trim() === LOCAL_REVIEW_OTP
  )
}
