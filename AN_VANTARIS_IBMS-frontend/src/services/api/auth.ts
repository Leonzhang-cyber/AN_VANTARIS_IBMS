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

// Local review credentials are only accepted in local / DEV review runtimes.
// They are not used by the production API login flow.
const LOCAL_REVIEW_USERS = [
  {
    username: 'admin',
    password: 'VantarisLocalReview#2026',
    otp: '260624',
    displayName: 'VANTARIS Administrator',
    role: 'Admin',
  },
  {
    username: 'superadmin',
    password: 'VantarisLocalAdmin#2026',
    otp: '260624',
    displayName: 'System Administrator',
    role: 'Administrator',
  },
  {
    username: 'maintenance',
    password: 'VantarisLocalEngineer#2026',
    otp: '260624',
    displayName: 'Maintenance Engineer',
    role: 'Engineer',
  },
]

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  if (isLocalReviewRuntime() && isLocalReviewCredential(payload)) {
    return createLocalReviewSession(payload)
  }

  const { data } = await request.post('/v1/auth/login', payload)
  return data as LoginResponse
}

function isLocalReviewRuntime(): boolean {
  const host = window.location.hostname
  return import.meta.env.DEV || host === 'localhost' || host === '127.0.0.1' || host.startsWith('192.168.') || host.startsWith('10.') || host.endsWith('.local')
}

function findLocalReviewUser(payload: LoginPayload) {
  return LOCAL_REVIEW_USERS.find((user) => (
    payload.username.trim().toLowerCase() === user.username &&
    payload.password === user.password &&
    payload.otp.trim() === user.otp
  ))
}

function isLocalReviewCredential(payload: LoginPayload): boolean {
  return Boolean(findLocalReviewUser(payload))
}

function createLocalReviewSession(payload: LoginPayload): LoginResponse {
  const user = findLocalReviewUser(payload)

  return {
    token: `local-2fa-${user?.username ?? 'review'}-token`,
    user: {
      username: user?.username ?? payload.username,
      displayName: user?.displayName ?? payload.username,
      role: user?.role ?? 'Admin',
      permissions: ['platform:read', 'system:read', 'audit:read'],
    },
  }
}
