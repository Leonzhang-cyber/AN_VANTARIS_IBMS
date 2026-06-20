import request from './request'

export type AirportEndpointKey =
  | 'AIRPORT_OVERVIEW'
  | 'SYSTEMS_INTEGRATION_HEALTH'
  | 'ASSETS_TOPOLOGY'
  | 'ALARMS_EVENTS'
  | 'FAULT_CASES'
  | 'MAINTENANCE_WORK_ORDERS'
  | 'EVIDENCE_INVESTIGATION'
  | 'REPORTS'

export interface AirportGaReadonlySource {
  type: string
  path: string
  rootKey: string
  sourceRootKey?: string
  authority: string
}

export interface AirportGaReadonlyPayload {
  platform: 'VANTARIS ONE'
  industryProjection: 'airport'
  releaseCandidate: string
  endpointKey: AirportEndpointKey
  route: string
  method: 'GET'
  readOnly: boolean
  productionActivation: boolean
  runtimeActivation: boolean
  databaseAccess: boolean
  dbWrite: boolean
  approvalExecution: boolean
  customerIdentifierLeakage: boolean
  source: AirportGaReadonlySource
  summary: unknown
  data: unknown
  filters: unknown
  facets: unknown
  pagination: unknown
}

export interface AirportGaReadonlyEnvelope {
  code: number
  message: string
  data: AirportGaReadonlyPayload
}

export interface AirportGaReadonlyEndpointDefinition {
  key: AirportEndpointKey
  title: string
  frontendPath: string
  apiPath: string
}

export const airportGaReadonlyEndpoints: AirportGaReadonlyEndpointDefinition[] = [
  {
    key: 'AIRPORT_OVERVIEW',
    title: 'Airport Overview',
    frontendPath: '/one/airport/overview',
    apiPath: '/v1/one/airport/console/overview',
  },
  {
    key: 'SYSTEMS_INTEGRATION_HEALTH',
    title: 'Systems & Integration Health',
    frontendPath: '/one/airport/systems-integration-health',
    apiPath: '/v1/one/airport/console/systems-integration-health',
  },
  {
    key: 'ASSETS_TOPOLOGY',
    title: 'Assets & Topology',
    frontendPath: '/one/airport/assets-topology',
    apiPath: '/v1/one/airport/console/assets-topology',
  },
  {
    key: 'ALARMS_EVENTS',
    title: 'Alarms & Events',
    frontendPath: '/one/airport/alarms-events',
    apiPath: '/v1/one/airport/console/alarms-events',
  },
  {
    key: 'FAULT_CASES',
    title: 'Fault Cases',
    frontendPath: '/one/airport/fault-cases',
    apiPath: '/v1/one/airport/console/fault-cases',
  },
  {
    key: 'MAINTENANCE_WORK_ORDERS',
    title: 'Maintenance Work Orders',
    frontendPath: '/one/airport/maintenance-work-orders',
    apiPath: '/v1/one/airport/console/maintenance-work-orders',
  },
  {
    key: 'EVIDENCE_INVESTIGATION',
    title: 'Evidence & Investigation',
    frontendPath: '/one/airport/evidence-investigation',
    apiPath: '/v1/one/airport/console/evidence-investigation',
  },
  {
    key: 'REPORTS',
    title: 'Reports',
    frontendPath: '/one/airport/reports',
    apiPath: '/v1/one/airport/console/reports',
  },
]

function unwrapPayload(body: AirportGaReadonlyEnvelope | AirportGaReadonlyPayload): AirportGaReadonlyPayload {
  if ('data' in body && typeof body.data === 'object' && body.data !== null) {
    return body.data as AirportGaReadonlyPayload
  }
  return body as AirportGaReadonlyPayload
}

export async function getAirportGaReadonlySection(
  endpoint: AirportGaReadonlyEndpointDefinition,
): Promise<AirportGaReadonlyPayload> {
  const response = await request.get<AirportGaReadonlyEnvelope | AirportGaReadonlyPayload>(endpoint.apiPath)
  return unwrapPayload(response.data)
}

export async function getAirportGaReadonlySections(): Promise<AirportGaReadonlyPayload[]> {
  const responses = await Promise.all(airportGaReadonlyEndpoints.map((endpoint) => getAirportGaReadonlySection(endpoint)))
  return responses
}
