import request from './request'

export const AIRPORT_HMI_MAP_ID = 'T3-GF-HMI-001'

export interface AirportHmiMapPayload {
  platform?: string
  readOnly?: boolean
  productionActivation?: boolean
  runtimeActivation?: boolean
  databaseAccess?: boolean
  dbWrite?: boolean
  approvalExecution?: boolean
  map_id?: string
  overlay_mode?: string
  source_mode?: string
  asset_import_readiness?: string
  asset_overlay_status?: string
  formal_asset_registry_write?: boolean
  formal_event_registry_write?: boolean
  formal_work_order_write?: boolean
  formal_evidence_write?: boolean
  formal_work_order_closure?: boolean
  confirm_enabled?: boolean
  closure_status?: string
  export_ready?: boolean
  export_status?: string
  summary?: Record<string, unknown>
  audit?: Record<string, unknown>
  data?: Array<Record<string, unknown>>
  gates?: Array<Record<string, unknown>>
  fault?: Record<string, unknown>
  work_order?: Record<string, unknown>
  operational_context?: Record<string, unknown>
  evidence_context?: Record<string, unknown>
  data_source_status?: string
  source?: string
}

export interface AirportHmiMapContent {
  map: AirportHmiMapPayload
  zoneSummary: AirportHmiMapPayload
  locationSummary: AirportHmiMapPayload
  assetOverlay: AirportHmiMapPayload
  systemOverlay: AirportHmiMapPayload
  faultOverlay: AirportHmiMapPayload
  workOrderOverlay: AirportHmiMapPayload
  technicianNavigation: AirportHmiMapPayload
  decisionLens: AirportHmiMapPayload
  evidenceOverlay: AirportHmiMapPayload
  workOrderEvidence: AirportHmiMapPayload
  closureReadiness: AirportHmiMapPayload
  importAuditSummary: AirportHmiMapPayload
  exportEvidenceCenter: AirportHmiMapPayload
  sourceState: string
}

type Envelope = {
  code?: number
  message?: string
  data?: AirportHmiMapPayload
}

const readonlyBase: AirportHmiMapPayload = {
  platform: 'VANTARIS ONE',
  readOnly: true,
  productionActivation: false,
  runtimeActivation: false,
  databaseAccess: false,
  dbWrite: false,
  approvalExecution: false,
  map_id: AIRPORT_HMI_MAP_ID,
  overlay_mode: 'readonly_projection',
  source_mode: 'controlled_sample_projection',
  asset_import_readiness: 'HOLD_BLOCKED',
  asset_overlay_status: 'blocked_by_data_quality',
  formal_asset_registry_write: false,
  formal_event_registry_write: false,
  formal_work_order_write: false,
  formal_evidence_write: false,
  formal_work_order_closure: false,
  confirm_enabled: false,
  closure_status: 'not_ready_due_to_asset_quality_blockers',
  data_source_status: 'Readonly airport map data is currently unavailable.',
}

function unwrap(body: Envelope | AirportHmiMapPayload): AirportHmiMapPayload {
  if (
    body
    && typeof body === 'object'
    && ('code' in body || 'message' in body)
    && 'data' in body
    && body.data
    && typeof body.data === 'object'
    && !Array.isArray(body.data)
  ) {
    return body.data
  }
  return body as AirportHmiMapPayload
}

function unavailablePayload(partial: AirportHmiMapPayload = {}): AirportHmiMapPayload {
  return {
    ...readonlyBase,
    ...partial,
    summary: {
      source_state: readonlyBase.data_source_status,
      ...(partial.summary ?? {}),
    },
  }
}

async function getPayload(path: string, unavailable: AirportHmiMapPayload): Promise<AirportHmiMapPayload> {
  try {
    const response = await request.get<Envelope | AirportHmiMapPayload>(path)
    return unwrap(response.data)
  } catch {
    return unavailablePayload(unavailable)
  }
}

export async function getAirportHmiMapContent(mapId = AIRPORT_HMI_MAP_ID): Promise<AirportHmiMapContent> {
  const endpoints = {
    map: '/v1/one/airport/console/data-asset-map',
    zoneSummary: `/v1/assets/hmi-maps/${mapId}/zone-summary`,
    locationSummary: `/v1/assets/hmi-maps/${mapId}/location-summary`,
    assetOverlay: `/v1/assets/hmi-maps/${mapId}/asset-overlay`,
    systemOverlay: `/v1/assets/hmi-maps/${mapId}/system-overlay`,
    faultOverlay: `/v1/assets/hmi-maps/${mapId}/fault-overlay`,
    workOrderOverlay: `/v1/assets/hmi-maps/${mapId}/work-order-overlay`,
    technicianNavigation: `/v1/assets/hmi-maps/${mapId}/technician-navigation`,
    decisionLens: `/v1/assets/hmi-maps/${mapId}/decision-lens`,
    evidenceOverlay: `/v1/assets/hmi-maps/${mapId}/evidence-overlay`,
    workOrderEvidence: `/v1/assets/hmi-maps/${mapId}/work-order-evidence`,
    closureReadiness: `/v1/assets/hmi-maps/${mapId}/closure-readiness`,
    importAuditSummary: `/v1/assets/hmi-maps/${mapId}/import-audit-summary`,
    exportEvidenceCenter: `/v1/assets/hmi-maps/${mapId}/export-evidence-center`,
  }

  const [
    map,
    zoneSummary,
    locationSummary,
    assetOverlay,
    systemOverlay,
    faultOverlay,
    workOrderOverlay,
    technicianNavigation,
    decisionLens,
    evidenceOverlay,
    workOrderEvidence,
    closureReadiness,
    importAuditSummary,
    exportEvidenceCenter,
  ] = await Promise.all([
    getPayload(endpoints.map, { summary: { base_layer: 'Registered base layer' }, data: [] }),
    getPayload(endpoints.zoneSummary, { summary: { zone_count: 0, asset_records_seen: 5187 }, data: [] }),
    getPayload(endpoints.locationSummary, { summary: { location_count: 0, asset_records_seen: 5187 }, data: [] }),
    getPayload(endpoints.assetOverlay, { summary: { records_seen: 5187, overlay_markers: 0, blocked_by_quality: true }, data: [] }),
    getPayload(endpoints.systemOverlay, { summary: { system_count: 0, asset_records_seen: 5187 }, data: [] }),
    getPayload(endpoints.faultOverlay, { summary: { fault_count: 0, blocked_by_asset_quality: true }, data: [] }),
    getPayload(endpoints.workOrderOverlay, { summary: { work_order_count: 0, blocked_by_asset_quality: true }, data: [] }),
    getPayload(endpoints.technicianNavigation, { summary: { route_count: 0, critical_routes: 0 }, data: [] }),
    getPayload(endpoints.decisionLens, {
      operational_context: {
        impact: 'Readonly projection is blocked by asset data quality.',
        recommended_action: 'Resolve critical asset import blockers before formal registry write.',
        related_system: 'Pending customer-approved map conversion',
        related_location: 'Terminal 3 / Ground Floor',
      },
      evidence_context: {
        required: true,
        required_items: ['Evidence readiness review'],
        status: 'pending_closure_evidence',
      },
    }),
    getPayload(endpoints.evidenceOverlay, { summary: { evidence_items_required: 0, closure_ready: false }, data: [] }),
    getPayload(endpoints.workOrderEvidence, { summary: { work_order_count: 0, evidence_required_count: 0 }, data: [] }),
    getPayload(endpoints.closureReadiness, {
      summary: { total_work_orders: 0, ready_to_close: 0, pending_evidence: 0 },
      gates: [
        { gate: 'Asset Import Quality', status: 'blocked', reason: 'Asset import readiness is HOLD_BLOCKED' },
        { gate: 'Evidence Required', status: 'pending', reason: 'Closure evidence is not formally uploaded' },
      ],
    }),
    getPayload(endpoints.importAuditSummary, {
      source: 'asset_import_quality_report',
      summary: { total_records: 5187, blocker_count: 2, major_count: 1, warning_count: 7, info_count: 0, readiness: 'HOLD_BLOCKED' },
      audit: { formal_import_committed: false, formal_asset_registry_write: false, quality_report_available: false, confirm_enabled: false },
    }),
    getPayload(endpoints.exportEvidenceCenter, { export_ready: false, export_status: 'blocked_by_asset_quality' }),
  ])

  const payloads = [
    map,
    zoneSummary,
    locationSummary,
    assetOverlay,
    systemOverlay,
    faultOverlay,
    workOrderOverlay,
    technicianNavigation,
    decisionLens,
    evidenceOverlay,
    workOrderEvidence,
    closureReadiness,
    importAuditSummary,
    exportEvidenceCenter,
  ]
  const unavailableActive = payloads.some((payload) => String(payload.data_source_status ?? '').includes('currently unavailable'))

  return {
    map,
    zoneSummary,
    locationSummary,
    assetOverlay,
    systemOverlay,
    faultOverlay,
    workOrderOverlay,
    technicianNavigation,
    decisionLens,
    evidenceOverlay,
    workOrderEvidence,
    closureReadiness,
    importAuditSummary,
    exportEvidenceCenter,
    sourceState: unavailableActive ? 'Readonly airport map data is currently unavailable.' : 'Backend readonly API',
  }
}
