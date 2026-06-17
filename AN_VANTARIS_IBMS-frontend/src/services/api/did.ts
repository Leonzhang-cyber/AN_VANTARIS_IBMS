import request from './request'
import type { JsonPayload } from './system'

export async function login(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/did/login', payload)
  return data
}

export async function getMe(): Promise<unknown> {
  const { data } = await request.get('/did/me')
  return data
}

export async function createEntity(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/did/entity', payload)
  return data
}

export async function generateVp(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/did/vp/generate', payload)
  return data
}

export async function reissueVc(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/did/vc/reissue', payload)
  return data
}

export async function revokeVc(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/did/vc/revoke', payload)
  return data
}
