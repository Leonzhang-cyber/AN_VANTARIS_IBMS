import request from './request'
import type { JsonPayload } from './system'

export async function getMenuVersions(): Promise<unknown> {
  const { data } = await request.get('/system/versions')
  return data
}

export async function getMenus(): Promise<unknown> {
  const { data } = await request.get('/system/menus')
  return data
}

export async function getVersionMenus(versionId: string): Promise<unknown> {
  const { data } = await request.get(`/system/version-menus/${encodeURIComponent(versionId)}`)
  return data
}

export async function createMenu(payload: JsonPayload): Promise<unknown> {
  const { data } = await request.post('/system/menus-add', payload)
  return data
}

export async function updateMenu(id: number | string, payload: JsonPayload): Promise<unknown> {
  const { data } = await request.put(`/system/menus-update/${id}`, payload)
  return data
}

export async function deleteMenu(id: number | string): Promise<unknown> {
  const { data } = await request.delete(`/system/menus-delete/${id}`)
  return data
}
