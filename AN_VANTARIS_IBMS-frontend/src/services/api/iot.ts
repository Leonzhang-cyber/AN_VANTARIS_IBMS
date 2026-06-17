import request from './request'
import type { JsonPayload } from './system'

export async function registerDevice(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/iot/device/register', payload)
  return data
}

export async function sendDeviceCommand(deviceDid: string, payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post(
    `/iot/device/${encodeURIComponent(deviceDid)}/command`,
    payload,
  )
  return data
}

export async function ingestHttp(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/iot/ingest/http', payload)
  return data
}

export async function getStandardFields(): Promise<unknown> {
  const { data } = await request.get('/iot/standard-fields')
  return data
}

export async function createStandardField(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/iot/standard-fields', payload)
  return data
}
