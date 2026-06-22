import { Prisma } from '@prisma/client'

const CATALOG_OBJECT_TYPE = 'catalog'
const CATALOG_OBJECT_ID = 'GLOBAL'

const PROTOCOL_TYPES = [
  'BACNET_IP',
  'MODBUS_TCP',
  'OPC_UA',
  'MQTT',
  'REST_API',
  'WEBHOOK',
  'ONVIF',
  'RTSP',
  'SDK',
  'CSV',
  'EXCEL',
  'DATABASE',
  'SYSLOG',
  'MANUAL',
  'FILE_DROP',
] as const

const SYSTEM_TYPES = [
  'BMS',
  'IBMS',
  'SCADA',
  'PLC',
  'CCTV',
  'VMS',
  'AI_VIDEO',
  'EMS',
  'IPMS',
  'FIRE_ALARM',
  'POWER_METER',
  'DATA_DIODE',
  'OT_SECURITY',
  'CSV_IMPORT',
  'MANUAL',
  'AEGIS_IBMS',
  'OTHER',
] as const

const EVIDENCE_TYPES = [
  'TEXT_NOTE',
  'IMAGE',
  'SNAPSHOT',
  'VIDEO_CLIP',
  'SYSTEM_LOG',
  'TEST_RESULT',
  'INSPECTION_RECORD',
  'AI_DETECTION',
  'MAPPING_RESULT',
  'CSV_IMPORT_RECORD',
] as const

const CATALOG_ENTRIES: Array<{ codeType: string; values: readonly string[] }> = [
  { codeType: 'SYSTEM_TYPE', values: SYSTEM_TYPES },
  { codeType: 'PROTOCOL_TYPE', values: PROTOCOL_TYPES },
  {
    codeType: 'CONNECTION_MODE',
    values: ['POLL', 'PUSH', 'BATCH', 'REALTIME', 'HYBRID', 'MANUAL'],
  },
  { codeType: 'NETWORK_ZONE', values: ['DMZ', 'OT', 'IT', 'CLOUD', 'EDGE', 'UNKNOWN'] },
  {
    codeType: 'SOURCE_TYPE',
    values: ['CONNECTOR', 'CSV', 'API', 'WEBHOOK', 'DEVICE', 'MANUAL', 'FILE_DROP'],
  },
  {
    codeType: 'EVENT_CATEGORY',
    values: ['operational_fault', 'safety', 'security', 'maintenance', 'environmental', 'other'],
  },
  { codeType: 'EVENT_STATUS', values: ['new', 'acknowledged', 'in_progress', 'closed', 'suppressed'] },
  {
    codeType: 'INCIDENT_STATUS',
    values: ['open', 'investigating', 'mitigated', 'resolved', 'closed'],
  },
  {
    codeType: 'WORK_ORDER_STATUS',
    values: ['draft', 'assigned', 'in_progress', 'completed', 'cancelled'],
  },
  { codeType: 'SEVERITY', values: ['critical', 'major', 'minor', 'info'] },
  { codeType: 'PRIORITY', values: ['P1', 'P2', 'P3', 'P4'] },
  { codeType: 'EVIDENCE_TYPE', values: EVIDENCE_TYPES },
  {
    codeType: 'INTEGRATION_STATUS',
    values: ['DRAFT', 'ACTIVE', 'DISABLED', 'ERROR', 'TESTING'],
  },
  {
    codeType: 'PROCESSING_STATUS',
    values: ['RECEIVED', 'PROCESSING', 'PROCESSED', 'FAILED', 'SKIPPED', 'REPROCESSING'],
  },
  { codeType: 'DATA_QUALITY_STATUS', values: ['PASS', 'WARN', 'FAIL', 'UNKNOWN'] },
]

export function buildCatalogReferenceCodeRows(
  seedNow: Date,
  startId = 100,
): Prisma.ReferenceCodeCreateManyInput[] {
  const rows: Prisma.ReferenceCodeCreateManyInput[] = []
  let id = startId
  for (const entry of CATALOG_ENTRIES) {
    for (const value of entry.values) {
      rows.push({
        referenceCodeId: `RC-${String(id).padStart(3, '0')}`,
        objectType: CATALOG_OBJECT_TYPE,
        objectId: CATALOG_OBJECT_ID,
        codeType: entry.codeType,
        codeValue: value,
        description: `${entry.codeType} catalog value`,
        isActive: true,
        createdById: 'seed-admin',
        createdAt: seedNow,
        updatedAt: seedNow,
      })
      id += 1
    }
  }
  return rows
}
