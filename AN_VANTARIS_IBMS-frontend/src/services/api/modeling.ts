import request from './request'
import type { JsonPayload } from './system'

export async function listCsv(): Promise<unknown> {
  const { data } = await request.get('/modeling/csv/list')
  return data
}

export async function trainModel(deviceCode: string, payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post(
    `/modeling/${encodeURIComponent(deviceCode)}/train`,
    payload,
  )
  return data
}

export async function predict(deviceCode: string, payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post(
    `/modeling/${encodeURIComponent(deviceCode)}/predict`,
    payload,
  )
  return data
}

export async function predictFuture(deviceCode: string, payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post(
    `/modeling/${encodeURIComponent(deviceCode)}/predict_future`,
    payload,
  )
  return data
}

export async function getModelInfo(deviceCode: string): Promise<unknown> {
  const { data } = await request.get(`/modeling/${encodeURIComponent(deviceCode)}/model_info`)
  return data
}
