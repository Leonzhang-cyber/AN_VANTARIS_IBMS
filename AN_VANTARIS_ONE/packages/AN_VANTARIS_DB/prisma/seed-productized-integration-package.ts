import { ConnectorStatus, Prisma, PrismaClient } from '@prisma/client'

const PACKAGE_META = {
  packageName: 'UFMS Productized Integration Package V1.0',
  packageVersion: 'V1.0',
  packagePurpose: 'SALES_POC',
  isStandardPackage: true,
  isSample: true,
} as const

type SeedTimestamps = {
  seedNow: Date
  parseMockTimestamp: (value: string) => Date
}

type FieldMappingSeed = {
  mappingId: string
  externalFieldName: string
  ufmsFieldName: string
  isRequired?: boolean
  defaultValue?: string | null
  sortOrder: number
}

type ValueMappingSeed = {
  mappingId: string
  mappingType: string
  externalValue: string
  ufmsValue: string
  sortOrder: number
}

type ProductizedPackageSeed = {
  packageType: string
  businessDescription: string
  businessValue: string
  pocUsageNotes: string
  engineeringGuide: string
  compatibleSystems: string[]
  supportedInputModes: string[]
  samplePayload: Record<string, unknown>
  expectedNormalizedEvent: Record<string, unknown>
  externalSystem: {
    externalSystemId: string
    systemCode: string
    systemName: string
    systemType: string
    vendor: string
    productName: string
    productVersion: string
    networkZone: string
    description: string
    pocUsage: string
  }
  connector: {
    connectorId: string
    connectorCode: string
    connectorName: string
    adapterId: string
    protocol: string
  }
  protocolProfile: {
    protocolProfileId: string
    profileCode: string
    profileName: string
    protocol: string
    protocolType: string
    supportedModes: string[]
  }
  connectionProfile: {
    connectionProfileId: string
    profileCode: string
    profileName: string
    protocol: string
    protocolType: string
    inputMode: string
    baseUrl?: string | null
    endpointPath?: string | null
    filePath?: string | null
    authType?: string | null
    supportsPolling?: boolean
    supportsPush?: boolean
    supportsBatch?: boolean
    metadata?: Prisma.InputJsonValue
  }
  faultSource: {
    sourceId: string
    code: string
    sourceName: string
    sourceType: string
    protocol: string
    systemDomain: string
    siteName: string
    location: string
    ownerTeam: string
  }
  mappingTemplate: {
    mappingTemplateId: string
    templateCode: string
    templateName: string
    sourceSystemType: string
    inputMode: string
    description: string
    templateSchema: Prisma.InputJsonValue
  }
  integrationProfile: {
    profileId: string
    profileCode: string
    profileName: string
    description: string
    sourceSystemName: string
    sourceSystemType: string
    inputMode: string
    systemDomain: string
    siteName: string
    ownerTeam: string
    defaultSeverity: string
    defaultStatus: string
    sourceType: string
    fieldMappings: FieldMappingSeed[]
    valueMappings: ValueMappingSeed[]
  }
  rawMessage: {
    id: string
    sourceRecordId: string
    protocolType: string
    messageType: string
  }
  sampleEvent?: {
    eventId: string
    title: string
    severity: string
    category: string
    assetLabel: string
    status: string
    occurredTime: string
    externalReferenceId: string
    sourceType: string
    eventCategory: string
    deviceId?: string
    assetId?: string
    confidence?: number
    snapshotUrl?: string
    metadata?: Prisma.InputJsonValue
  }
}

const PACKAGES: ProductizedPackageSeed[] = [
  {
    packageType: 'BMS_FAULT',
    businessDescription:
      'Standard package for integrating BMS/BAS fault alarms into UFMS for sales demonstrations, PoC deployments, and early project delivery.',
    businessValue:
      'Accelerates BMS alarm onboarding with pre-validated field mappings, severity translation, and a ready-to-test integration profile.',
    pocUsageNotes:
      'Use for customer PoC when BMS alarms must appear in UFMS within hours. Validate one alarm type end-to-end before expanding scope.',
    engineeringGuide:
      'Configure REST polling or CSV/file-drop ingestion. Map customer alarm fields to the standard template, run mapping test, then activate after site credential and endpoint validation.',
    compatibleSystems: [
      'Honeywell BMS',
      'Schneider Electric BMS',
      'Siemens BMS',
      'Johnson Controls',
      'Tridium Niagara',
      'Delta Controls',
      'Generic BMS/BAS',
    ],
    supportedInputModes: ['REST_API', 'CSV', 'FILE_DROP', 'MANUAL'],
    samplePayload: {
      alarm_name: 'Chiller High Temperature',
      alarm_level: '5',
      device_code: 'CH-01',
      location: 'Plant Room',
      occur_time: '2026-06-05T10:30:00',
      alarm_status: 'new',
      external_alarm_id: 'BMS-ALM-0001',
    },
    expectedNormalizedEvent: {
      title: 'Chiller High Temperature',
      severity: 'CRITICAL',
      sourceType: 'BMS',
      eventCategory: 'FACILITY',
      deviceId: 'CH-01',
      occurredAt: '2026-06-05T10:30:00',
      status: 'NEW',
      externalReferenceId: 'BMS-ALM-0001',
      metadata: { location: 'Plant Room' },
    },
    externalSystem: {
      externalSystemId: 'EXT-PKG-BMS-FAULT',
      systemCode: 'PKG-BMS-FAULT',
      systemName: 'BMS Fault Integration',
      systemType: 'BMS',
      vendor: 'Multi-vendor',
      productName: 'Building Management System',
      productVersion: 'Standard Package',
      networkZone: 'IT',
      description: 'Productized BMS fault alarm integration for UFMS sales, PoC, and early delivery.',
      pocUsage: 'Standard BMS alarm integration for PoC and early project delivery.',
    },
    connector: {
      connectorId: 'CON-PKG-BMS-FAULT',
      connectorCode: 'PKG-BMS-FAULT',
      connectorName: 'BMS Fault Integration Connector',
      adapterId: 'ADP-004',
      protocol: 'REST API',
    },
    protocolProfile: {
      protocolProfileId: 'PP-PKG-BMS-REST-CSV',
      profileCode: 'PKG-BMS-REST-CSV',
      profileName: 'BMS REST and CSV Protocol Profile',
      protocol: 'REST',
      protocolType: 'REST_API',
      supportedModes: ['REST_API', 'CSV', 'FILE_DROP', 'MANUAL'],
    },
    connectionProfile: {
      connectionProfileId: 'CP-PKG-BMS-FAULT',
      profileCode: 'PKG-BMS-FAULT-CONN',
      profileName: 'BMS Fault Connection Profile',
      protocol: 'REST',
      protocolType: 'REST_API',
      inputMode: 'REST_API',
      baseUrl: 'https://bms.customer.local',
      endpointPath: '/api/v1/alarms',
      authType: 'api_key',
      supportsPolling: true,
      supportsBatch: true,
      metadata: {
        csvFilePath: '/imports/bms-alarms',
        delimiter: ',',
        encoding: 'UTF-8',
        headerRow: 1,
      },
    },
    faultSource: {
      sourceId: 'FS-PKG-BMS-FAULT',
      code: 'FS-PKG-BMS-FAULT',
      sourceName: 'BMS Fault Integration Source',
      sourceType: 'BMS',
      protocol: 'REST API',
      systemDomain: 'Building Management',
      siteName: 'Singapore DC',
      location: 'Plant Room',
      ownerTeam: 'BMS Operations',
    },
    mappingTemplate: {
      mappingTemplateId: 'MT-PKG-BMS-FAULT',
      templateCode: 'PKG-BMS-FAULT-V1',
      templateName: 'BMS Fault Integration Package',
      sourceSystemType: 'BMS',
      inputMode: 'REST_API',
      description: 'Standard BMS fault field layout for UFMS productized integration.',
      templateSchema: {
        columns: [
          'alarm_name',
          'alarm_level',
          'device_code',
          'location',
          'occur_time',
          'alarm_status',
          'external_alarm_id',
        ],
      },
    },
    integrationProfile: {
      profileId: 'PROFILE-PKG-BMS-FAULT',
      profileCode: 'PKG-BMS-FAULT',
      profileName: 'BMS Fault Integration Package',
      description: 'Productized BMS fault integration profile with standard mappings and value translations.',
      sourceSystemName: 'BMS Fault Integration',
      sourceSystemType: 'BMS',
      inputMode: 'REST_API',
      systemDomain: 'Building Management',
      siteName: 'Singapore DC',
      ownerTeam: 'BMS Operations',
      defaultSeverity: 'MEDIUM',
      defaultStatus: 'NEW',
      sourceType: 'BMS',
      fieldMappings: [
        { mappingId: 'IFM-PKG-BMS-01', externalFieldName: 'alarm_name', ufmsFieldName: 'title', isRequired: true, sortOrder: 0 },
        { mappingId: 'IFM-PKG-BMS-02', externalFieldName: 'alarm_level', ufmsFieldName: 'severity', isRequired: true, sortOrder: 1 },
        { mappingId: 'IFM-PKG-BMS-03', externalFieldName: 'device_code', ufmsFieldName: 'deviceId', isRequired: false, sortOrder: 2 },
        { mappingId: 'IFM-PKG-BMS-04', externalFieldName: 'occur_time', ufmsFieldName: 'occurredAt', isRequired: true, sortOrder: 3 },
        { mappingId: 'IFM-PKG-BMS-05', externalFieldName: 'alarm_status', ufmsFieldName: 'status', isRequired: false, defaultValue: 'NEW', sortOrder: 4 },
        { mappingId: 'IFM-PKG-BMS-06', externalFieldName: 'external_alarm_id', ufmsFieldName: 'externalReferenceId', isRequired: false, sortOrder: 5 },
        { mappingId: 'IFM-PKG-BMS-07', externalFieldName: 'location', ufmsFieldName: 'metadata.location', isRequired: false, sortOrder: 6 },
      ],
      valueMappings: [
        { mappingId: 'IVM-PKG-BMS-01', mappingType: 'severity', externalValue: '1', ufmsValue: 'INFO', sortOrder: 0 },
        { mappingId: 'IVM-PKG-BMS-02', mappingType: 'severity', externalValue: '2', ufmsValue: 'LOW', sortOrder: 1 },
        { mappingId: 'IVM-PKG-BMS-03', mappingType: 'severity', externalValue: '3', ufmsValue: 'MEDIUM', sortOrder: 2 },
        { mappingId: 'IVM-PKG-BMS-04', mappingType: 'severity', externalValue: '4', ufmsValue: 'HIGH', sortOrder: 3 },
        { mappingId: 'IVM-PKG-BMS-05', mappingType: 'severity', externalValue: '5', ufmsValue: 'CRITICAL', sortOrder: 4 },
        { mappingId: 'IVM-PKG-BMS-06', mappingType: 'status', externalValue: 'new', ufmsValue: 'NEW', sortOrder: 5 },
        { mappingId: 'IVM-PKG-BMS-07', mappingType: 'status', externalValue: 'ack', ufmsValue: 'ACKNOWLEDGED', sortOrder: 6 },
        { mappingId: 'IVM-PKG-BMS-08', mappingType: 'status', externalValue: 'done', ufmsValue: 'RESOLVED', sortOrder: 7 },
        { mappingId: 'IVM-PKG-BMS-09', mappingType: 'status', externalValue: 'closed', ufmsValue: 'CLOSED', sortOrder: 8 },
      ],
    },
    rawMessage: {
      id: 'RAW-PKG-BMS-FAULT-001',
      sourceRecordId: 'BMS-ALM-0001',
      protocolType: 'REST_API',
      messageType: 'ALARM_EVENT',
    },
    sampleEvent: {
      eventId: 'EVT-PKG-BMS-001',
      title: 'Chiller High Temperature',
      severity: 'critical',
      category: 'equipment_fault',
      assetLabel: 'CH-01',
      status: 'New',
      occurredTime: '2026-06-05 10:30',
      externalReferenceId: 'BMS-ALM-0001',
      sourceType: 'BMS',
      eventCategory: 'FACILITY',
      deviceId: 'CH-01',
      metadata: { location: 'Plant Room' },
    },
  },
  {
    packageType: 'AI_VIDEO_SAFETY',
    businessDescription:
      'Standard package for integrating AI video safety alerts from analytics platforms into UFMS operations workflows.',
    businessValue:
      'Provides ready-made mappings for helmet, fall, and intrusion detections with media references and confidence scoring.',
    pocUsageNotes:
      'Ideal for safety PoC with VMS or AI box webhook delivery. Confirm camera naming and snapshot URL accessibility during site walkthrough.',
    engineeringGuide:
      'Configure webhook endpoint and credential reference. Validate event type translations and snapshot URL mapping before activation.',
    compatibleSystems: [
      'Hikvision',
      'Dahua',
      'AI Box',
      'AI Camera',
      'VMS Webhook',
      'Generic AI Video Analytics',
    ],
    supportedInputModes: ['WEBHOOK', 'REST_API', 'CSV', 'FILE_DROP'],
    samplePayload: {
      eventType: 'helmet_missing',
      eventTime: '2026-06-05T10:15:00',
      cameraIndexCode: 'CAM-001',
      confidence: 0.91,
      picUrl: '/snapshot/helmet_missing_001.jpg',
      eventId: 'HK-20260605-0001',
    },
    expectedNormalizedEvent: {
      title: 'Helmet Missing Detected',
      severity: 'HIGH',
      sourceType: 'AI_VIDEO',
      eventCategory: 'SAFETY',
      deviceId: 'CAM-001',
      confidence: 0.91,
      snapshotUrl: '/snapshot/helmet_missing_001.jpg',
      externalReferenceId: 'HK-20260605-0001',
      occurredAt: '2026-06-05T10:15:00',
      status: 'NEW',
    },
    externalSystem: {
      externalSystemId: 'EXT-PKG-AIVIDEO-SAFETY',
      systemCode: 'PKG-AIVIDEO-SAFETY',
      systemName: 'AI Video Safety Integration',
      systemType: 'AI_VIDEO',
      vendor: 'Multi-vendor',
      productName: 'AI Video Analytics Platform',
      productVersion: 'Standard Package',
      networkZone: 'IT',
      description: 'Productized AI video safety integration for UFMS sales, PoC, and early delivery.',
      pocUsage: 'Standard AI video safety alert integration for PoC and channel demonstrations.',
    },
    connector: {
      connectorId: 'CON-PKG-AIVIDEO-SAFETY',
      connectorCode: 'PKG-AIVIDEO-SAFETY',
      connectorName: 'AI Video Safety Connector',
      adapterId: 'ADP-004',
      protocol: 'Webhook',
    },
    protocolProfile: {
      protocolProfileId: 'PP-PKG-AIVIDEO-WEBHOOK',
      profileCode: 'PKG-AIVIDEO-WEBHOOK',
      profileName: 'AI Video Webhook Protocol Profile',
      protocol: 'WEBHOOK',
      protocolType: 'WEBHOOK',
      supportedModes: ['WEBHOOK', 'REST_API', 'CSV', 'FILE_DROP'],
    },
    connectionProfile: {
      connectionProfileId: 'CP-PKG-AIVIDEO-SAFETY',
      profileCode: 'PKG-AIVIDEO-SAFETY-CONN',
      profileName: 'AI Video Safety Connection Profile',
      protocol: 'WEBHOOK',
      protocolType: 'WEBHOOK',
      inputMode: 'WEBHOOK',
      endpointPath: '/webhooks/ai-video-safety',
      authType: 'hmac',
      supportsPush: true,
      metadata: { payloadFormat: 'json', allowedSourceIp: '10.0.0.0/24' },
    },
    faultSource: {
      sourceId: 'FS-PKG-AIVIDEO-SAFETY',
      code: 'FS-PKG-AIVIDEO-SAFETY',
      sourceName: 'AI Video Safety Integration Source',
      sourceType: 'AI_VIDEO',
      protocol: 'Webhook',
      systemDomain: 'Safety Operations',
      siteName: 'Singapore DC',
      location: 'Loading Bay',
      ownerTeam: 'Safety Operations',
    },
    mappingTemplate: {
      mappingTemplateId: 'MT-PKG-AIVIDEO-SAFETY',
      templateCode: 'PKG-AIVIDEO-SAFETY-V1',
      templateName: 'AI Video Safety Integration Package',
      sourceSystemType: 'AI_VIDEO',
      inputMode: 'WEBHOOK',
      description: 'Standard AI video safety event layout for UFMS productized integration.',
      templateSchema: {
        columns: ['eventType', 'eventTime', 'cameraIndexCode', 'confidence', 'picUrl', 'eventId'],
      },
    },
    integrationProfile: {
      profileId: 'PROFILE-PKG-AIVIDEO-SAFETY',
      profileCode: 'PKG-AIVIDEO-SAFETY',
      profileName: 'AI Video Safety Integration Package',
      description: 'Productized AI video safety integration profile with event type translations and media mapping.',
      sourceSystemName: 'AI Video Safety Integration',
      sourceSystemType: 'AI_VIDEO',
      inputMode: 'WEBHOOK',
      systemDomain: 'Safety Operations',
      siteName: 'Singapore DC',
      ownerTeam: 'Safety Operations',
      defaultSeverity: 'HIGH',
      defaultStatus: 'NEW',
      sourceType: 'AI_VIDEO',
      fieldMappings: [
        { mappingId: 'IFM-PKG-AIV-01', externalFieldName: 'eventType', ufmsFieldName: 'title', isRequired: true, sortOrder: 0 },
        { mappingId: 'IFM-PKG-AIV-02', externalFieldName: 'eventTime', ufmsFieldName: 'occurredAt', isRequired: true, sortOrder: 1 },
        { mappingId: 'IFM-PKG-AIV-03', externalFieldName: 'cameraIndexCode', ufmsFieldName: 'deviceId', isRequired: false, sortOrder: 2 },
        { mappingId: 'IFM-PKG-AIV-04', externalFieldName: 'confidence', ufmsFieldName: 'confidence', isRequired: false, sortOrder: 3 },
        { mappingId: 'IFM-PKG-AIV-05', externalFieldName: 'picUrl', ufmsFieldName: 'snapshotUrl', isRequired: false, sortOrder: 4 },
        { mappingId: 'IFM-PKG-AIV-06', externalFieldName: 'eventId', ufmsFieldName: 'externalReferenceId', isRequired: false, sortOrder: 5 },
      ],
      valueMappings: [
        { mappingId: 'IVM-PKG-AIV-01', mappingType: 'event_type', externalValue: 'helmet_missing', ufmsValue: 'Helmet Missing Detected', sortOrder: 0 },
        { mappingId: 'IVM-PKG-AIV-02', mappingType: 'event_type', externalValue: 'fall_detected', ufmsValue: 'Fall Detection Alert', sortOrder: 1 },
        { mappingId: 'IVM-PKG-AIV-03', mappingType: 'event_type', externalValue: 'intrusion', ufmsValue: 'Intrusion Detection Alert', sortOrder: 2 },
        { mappingId: 'IVM-PKG-AIV-04', mappingType: 'severity', externalValue: 'default', ufmsValue: 'HIGH', sortOrder: 3 },
        { mappingId: 'IVM-PKG-AIV-05', mappingType: 'status', externalValue: 'default', ufmsValue: 'NEW', sortOrder: 4 },
        { mappingId: 'IVM-PKG-AIV-06', mappingType: 'category', externalValue: 'default', ufmsValue: 'SAFETY', sortOrder: 5 },
      ],
    },
    rawMessage: {
      id: 'RAW-PKG-AIVIDEO-SAFETY-001',
      sourceRecordId: 'HK-20260605-0001',
      protocolType: 'WEBHOOK',
      messageType: 'AI_EVENT',
    },
    sampleEvent: {
      eventId: 'EVT-PKG-AIVIDEO-001',
      title: 'Helmet Missing Detected',
      severity: 'high',
      category: 'safety_fault',
      assetLabel: 'CAM-001',
      status: 'New',
      occurredTime: '2026-06-05 10:15',
      externalReferenceId: 'HK-20260605-0001',
      sourceType: 'AI_VIDEO',
      eventCategory: 'SAFETY',
      deviceId: 'CAM-001',
      confidence: 0.91,
      snapshotUrl: '/snapshot/helmet_missing_001.jpg',
    },
  },
  {
    packageType: 'CSV_FAULT_IMPORT',
    businessDescription:
      'Low-risk import package for customers without API access or direct system connectivity.',
    businessValue:
      'Enables spreadsheet-based fault ingestion with governed mappings for PoC, historical import, and isolated environments.',
    pocUsageNotes:
      'Use when the customer cannot expose APIs. Start with a small CSV sample and expand after data quality review.',
    engineeringGuide:
      'Place CSV or Excel files in the agreed folder or upload manually. Validate delimiter, header row, and severity columns before activation.',
    compatibleSystems: [
      'No API available',
      'Customer offline export',
      'Historical fault import',
      'Early PoC',
      'Isolated industrial environment',
    ],
    supportedInputModes: ['CSV', 'EXCEL', 'FILE_DROP', 'MANUAL'],
    samplePayload: {
      fault_title: 'Pump Fault',
      severity: 'HIGH',
      equipment_code: 'PUMP-01',
      fault_time: '2026-06-05T11:00:00',
      status: 'NEW',
      source_ref: 'CSV-ROW-001',
    },
    expectedNormalizedEvent: {
      title: 'Pump Fault',
      severity: 'HIGH',
      sourceType: 'CSV_IMPORT',
      eventCategory: 'FACILITY',
      assetId: 'PUMP-01',
      occurredAt: '2026-06-05T11:00:00',
      status: 'NEW',
      externalReferenceId: 'CSV-ROW-001',
    },
    externalSystem: {
      externalSystemId: 'EXT-PKG-CSV-FAULT',
      systemCode: 'PKG-CSV-FAULT',
      systemName: 'CSV / Excel Fault Import',
      systemType: 'CSV_IMPORT',
      vendor: 'Multi-vendor',
      productName: 'Spreadsheet Fault Import',
      productVersion: 'Standard Package',
      networkZone: 'IT',
      description: 'Productized CSV and Excel fault import for UFMS sales, PoC, and early delivery.',
      pocUsage: 'Low-risk spreadsheet import for customers without API connectivity.',
    },
    connector: {
      connectorId: 'CON-PKG-CSV-FAULT',
      connectorCode: 'PKG-CSV-FAULT',
      connectorName: 'CSV Fault Import Connector',
      adapterId: 'ADP-004',
      protocol: 'CSV',
    },
    protocolProfile: {
      protocolProfileId: 'PP-PKG-CSV-IMPORT',
      profileCode: 'PKG-CSV-IMPORT',
      profileName: 'CSV Import Protocol Profile',
      protocol: 'CSV',
      protocolType: 'CSV',
      supportedModes: ['CSV', 'EXCEL', 'FILE_DROP', 'MANUAL'],
    },
    connectionProfile: {
      connectionProfileId: 'CP-PKG-CSV-FAULT',
      profileCode: 'PKG-CSV-FAULT-CONN',
      profileName: 'CSV Fault Import Connection Profile',
      protocol: 'CSV',
      protocolType: 'CSV',
      inputMode: 'CSV_UPLOAD',
      filePath: '/imports/csv-faults',
      supportsBatch: true,
      supportsPolling: true,
      metadata: { delimiter: ',', encoding: 'UTF-8', headerRow: 1, pollingIntervalSec: 120 },
    },
    faultSource: {
      sourceId: 'FS-PKG-CSV-FAULT',
      code: 'FS-PKG-CSV-FAULT',
      sourceName: 'CSV Fault Import Source',
      sourceType: 'CSV_IMPORT',
      protocol: 'CSV',
      systemDomain: 'Operations',
      siteName: 'Singapore DC',
      location: 'Operations',
      ownerTeam: 'Operations',
    },
    mappingTemplate: {
      mappingTemplateId: 'MT-PKG-CSV-FAULT',
      templateCode: 'PKG-CSV-FAULT-V1',
      templateName: 'CSV / Excel Low-Risk Import Package',
      sourceSystemType: 'CSV_IMPORT',
      inputMode: 'CSV_UPLOAD',
      description: 'Standard CSV fault import layout for UFMS productized integration.',
      templateSchema: {
        columns: ['fault_title', 'severity', 'equipment_code', 'fault_time', 'status', 'source_ref'],
      },
    },
    integrationProfile: {
      profileId: 'PROFILE-PKG-CSV-FAULT',
      profileCode: 'PKG-CSV-FAULT',
      profileName: 'CSV / Excel Low-Risk Import Package',
      description: 'Productized spreadsheet fault import profile for low-risk customer onboarding.',
      sourceSystemName: 'CSV / Excel Fault Import',
      sourceSystemType: 'CSV_IMPORT',
      inputMode: 'CSV_UPLOAD',
      systemDomain: 'Operations',
      siteName: 'Singapore DC',
      ownerTeam: 'Operations',
      defaultSeverity: 'MEDIUM',
      defaultStatus: 'NEW',
      sourceType: 'CSV_IMPORT',
      fieldMappings: [
        { mappingId: 'IFM-PKG-CSV-01', externalFieldName: 'fault_title', ufmsFieldName: 'title', isRequired: true, sortOrder: 0 },
        { mappingId: 'IFM-PKG-CSV-02', externalFieldName: 'severity', ufmsFieldName: 'severity', isRequired: true, sortOrder: 1 },
        { mappingId: 'IFM-PKG-CSV-03', externalFieldName: 'equipment_code', ufmsFieldName: 'assetId', isRequired: false, sortOrder: 2 },
        { mappingId: 'IFM-PKG-CSV-04', externalFieldName: 'fault_time', ufmsFieldName: 'occurredAt', isRequired: true, sortOrder: 3 },
        { mappingId: 'IFM-PKG-CSV-05', externalFieldName: 'status', ufmsFieldName: 'status', isRequired: false, defaultValue: 'NEW', sortOrder: 4 },
        { mappingId: 'IFM-PKG-CSV-06', externalFieldName: 'source_ref', ufmsFieldName: 'externalReferenceId', isRequired: false, sortOrder: 5 },
      ],
      valueMappings: [
        { mappingId: 'IVM-PKG-CSV-01', mappingType: 'severity', externalValue: 'INFO', ufmsValue: 'INFO', sortOrder: 0 },
        { mappingId: 'IVM-PKG-CSV-02', mappingType: 'severity', externalValue: 'LOW', ufmsValue: 'LOW', sortOrder: 1 },
        { mappingId: 'IVM-PKG-CSV-03', mappingType: 'severity', externalValue: 'MEDIUM', ufmsValue: 'MEDIUM', sortOrder: 2 },
        { mappingId: 'IVM-PKG-CSV-04', mappingType: 'severity', externalValue: 'HIGH', ufmsValue: 'HIGH', sortOrder: 3 },
        { mappingId: 'IVM-PKG-CSV-05', mappingType: 'severity', externalValue: 'CRITICAL', ufmsValue: 'CRITICAL', sortOrder: 4 },
      ],
    },
    rawMessage: {
      id: 'RAW-PKG-CSV-FAULT-001',
      sourceRecordId: 'CSV-ROW-001',
      protocolType: 'CSV',
      messageType: 'CSV_IMPORT',
    },
    sampleEvent: {
      eventId: 'EVT-PKG-CSV-001',
      title: 'Pump Fault',
      severity: 'high',
      category: 'equipment_fault',
      assetLabel: 'PUMP-01',
      status: 'New',
      occurredTime: '2026-06-05 11:00',
      externalReferenceId: 'CSV-ROW-001',
      sourceType: 'CSV_IMPORT',
      eventCategory: 'FACILITY',
      assetId: 'PUMP-01',
    },
  },
  {
    packageType: 'AEGIS_IBMS',
    businessDescription:
      'Standard package for integrating AegisNexus IBMS event data into UFMS within a shared digital foundation scenario.',
    businessValue:
      'Delivers native IBMS event synchronization templates for partner demonstrations and joint platform deployments.',
    pocUsageNotes:
      'Use for AegisNexus IBMS PoC and internal event sync validation before customer-specific REST or database configuration.',
    engineeringGuide:
      'Configure REST endpoint or approved database export path. Validate priority and status translations with the customer operations team.',
    compatibleSystems: ['AegisNexus IBMS', 'Internal IBMS event sync', 'Shared digital foundation scenario'],
    supportedInputModes: ['REST_API', 'DATABASE', 'CSV', 'MANUAL'],
    samplePayload: {
      eventName: 'AHU Fan Failure',
      priority: 'P2',
      assetCode: 'AHU-02',
      deviceCode: 'FAN-02',
      site: 'Singapore DC',
      eventTime: '2026-06-05T12:00:00',
      eventStatus: 'open',
      eventId: 'IBMS-EVT-0001',
    },
    expectedNormalizedEvent: {
      title: 'AHU Fan Failure',
      severity: 'HIGH',
      sourceType: 'AEGIS_IBMS',
      eventCategory: 'FACILITY',
      assetId: 'AHU-02',
      deviceId: 'FAN-02',
      occurredAt: '2026-06-05T12:00:00',
      status: 'NEW',
      externalReferenceId: 'IBMS-EVT-0001',
      metadata: { site: 'Singapore DC', priority: 'P2' },
    },
    externalSystem: {
      externalSystemId: 'EXT-PKG-AEGIS-IBMS',
      systemCode: 'PKG-AEGIS-IBMS',
      systemName: 'AegisNexus IBMS Integration',
      systemType: 'AEGIS_IBMS',
      vendor: 'AegisNexus',
      productName: 'AegisNexus IBMS',
      productVersion: 'Standard Package',
      networkZone: 'IT',
      description: 'Productized AegisNexus IBMS integration for UFMS sales, PoC, and early delivery.',
      pocUsage: 'Native IBMS event integration for partner and customer digital foundation scenarios.',
    },
    connector: {
      connectorId: 'CON-PKG-AEGIS-IBMS',
      connectorCode: 'PKG-AEGIS-IBMS',
      connectorName: 'AegisNexus IBMS Connector',
      adapterId: 'ADP-004',
      protocol: 'REST API',
    },
    protocolProfile: {
      protocolProfileId: 'PP-PKG-AEGIS-IBMS-REST',
      profileCode: 'PKG-AEGIS-IBMS-REST',
      profileName: 'AegisNexus IBMS REST Protocol Profile',
      protocol: 'REST',
      protocolType: 'REST_API',
      supportedModes: ['REST_API', 'DATABASE', 'CSV', 'MANUAL'],
    },
    connectionProfile: {
      connectionProfileId: 'CP-PKG-AEGIS-IBMS',
      profileCode: 'PKG-AEGIS-IBMS-CONN',
      profileName: 'AegisNexus IBMS Connection Profile',
      protocol: 'REST',
      protocolType: 'REST_API',
      inputMode: 'REST_API',
      baseUrl: 'https://ibms.aegisnexus.local',
      endpointPath: '/api/v1/events',
      authType: 'oauth2',
      supportsPolling: true,
      metadata: { credentialRef: 'ibms-oauth-client', timeoutMs: 30000 },
    },
    faultSource: {
      sourceId: 'FS-PKG-AEGIS-IBMS',
      code: 'FS-PKG-AEGIS-IBMS',
      sourceName: 'AegisNexus IBMS Integration Source',
      sourceType: 'AEGIS_IBMS',
      protocol: 'REST API',
      systemDomain: 'Integrated Building Management',
      siteName: 'Singapore DC',
      location: 'Building A',
      ownerTeam: 'IBMS Operations',
    },
    mappingTemplate: {
      mappingTemplateId: 'MT-PKG-AEGIS-IBMS',
      templateCode: 'PKG-AEGIS-IBMS-V1',
      templateName: 'AegisNexus IBMS Native Integration Package',
      sourceSystemType: 'AEGIS_IBMS',
      inputMode: 'REST_API',
      description: 'Standard AegisNexus IBMS event layout for UFMS productized integration.',
      templateSchema: {
        columns: [
          'eventName',
          'priority',
          'assetCode',
          'deviceCode',
          'site',
          'eventTime',
          'eventStatus',
          'eventId',
        ],
      },
    },
    integrationProfile: {
      profileId: 'PROFILE-PKG-AEGIS-IBMS',
      profileCode: 'PKG-AEGIS-IBMS',
      profileName: 'AegisNexus IBMS Native Integration Package',
      description: 'Productized AegisNexus IBMS integration profile with priority and status translations.',
      sourceSystemName: 'AegisNexus IBMS Integration',
      sourceSystemType: 'AEGIS_IBMS',
      inputMode: 'REST_API',
      systemDomain: 'Integrated Building Management',
      siteName: 'Singapore DC',
      ownerTeam: 'IBMS Operations',
      defaultSeverity: 'MEDIUM',
      defaultStatus: 'NEW',
      sourceType: 'AEGIS_IBMS',
      fieldMappings: [
        { mappingId: 'IFM-PKG-AEGIS-01', externalFieldName: 'eventName', ufmsFieldName: 'title', isRequired: true, sortOrder: 0 },
        { mappingId: 'IFM-PKG-AEGIS-02', externalFieldName: 'priority', ufmsFieldName: 'severity', isRequired: true, sortOrder: 1 },
        { mappingId: 'IFM-PKG-AEGIS-03', externalFieldName: 'assetCode', ufmsFieldName: 'assetId', isRequired: false, sortOrder: 2 },
        { mappingId: 'IFM-PKG-AEGIS-04', externalFieldName: 'deviceCode', ufmsFieldName: 'deviceId', isRequired: false, sortOrder: 3 },
        { mappingId: 'IFM-PKG-AEGIS-05', externalFieldName: 'eventTime', ufmsFieldName: 'occurredAt', isRequired: true, sortOrder: 4 },
        { mappingId: 'IFM-PKG-AEGIS-06', externalFieldName: 'eventStatus', ufmsFieldName: 'status', isRequired: false, defaultValue: 'NEW', sortOrder: 5 },
        { mappingId: 'IFM-PKG-AEGIS-07', externalFieldName: 'eventId', ufmsFieldName: 'externalReferenceId', isRequired: false, sortOrder: 6 },
        { mappingId: 'IFM-PKG-AEGIS-08', externalFieldName: 'site', ufmsFieldName: 'metadata.site', isRequired: false, sortOrder: 7 },
        { mappingId: 'IFM-PKG-AEGIS-09', externalFieldName: 'priority', ufmsFieldName: 'metadata.priority', isRequired: false, sortOrder: 8 },
      ],
      valueMappings: [
        { mappingId: 'IVM-PKG-AEGIS-01', mappingType: 'priority', externalValue: 'P1', ufmsValue: 'CRITICAL', sortOrder: 0 },
        { mappingId: 'IVM-PKG-AEGIS-02', mappingType: 'priority', externalValue: 'P2', ufmsValue: 'HIGH', sortOrder: 1 },
        { mappingId: 'IVM-PKG-AEGIS-03', mappingType: 'priority', externalValue: 'P3', ufmsValue: 'MEDIUM', sortOrder: 2 },
        { mappingId: 'IVM-PKG-AEGIS-04', mappingType: 'priority', externalValue: 'P4', ufmsValue: 'LOW', sortOrder: 3 },
        { mappingId: 'IVM-PKG-AEGIS-05', mappingType: 'priority', externalValue: 'P5', ufmsValue: 'INFO', sortOrder: 4 },
        { mappingId: 'IVM-PKG-AEGIS-06', mappingType: 'status', externalValue: 'open', ufmsValue: 'NEW', sortOrder: 5 },
        { mappingId: 'IVM-PKG-AEGIS-07', mappingType: 'status', externalValue: 'in_progress', ufmsValue: 'IN_PROGRESS', sortOrder: 6 },
        { mappingId: 'IVM-PKG-AEGIS-08', mappingType: 'status', externalValue: 'closed', ufmsValue: 'CLOSED', sortOrder: 7 },
        { mappingId: 'IVM-PKG-AEGIS-09', mappingType: 'status', externalValue: 'resolved', ufmsValue: 'RESOLVED', sortOrder: 8 },
      ],
    },
    rawMessage: {
      id: 'RAW-PKG-AEGIS-IBMS-001',
      sourceRecordId: 'IBMS-EVT-0001',
      protocolType: 'REST_API',
      messageType: 'IBMS_EVENT',
    },
    sampleEvent: {
      eventId: 'EVT-PKG-AEGIS-001',
      title: 'AHU Fan Failure',
      severity: 'high',
      category: 'equipment_fault',
      assetLabel: 'AHU-02',
      status: 'New',
      occurredTime: '2026-06-05 12:00',
      externalReferenceId: 'IBMS-EVT-0001',
      sourceType: 'AEGIS_IBMS',
      eventCategory: 'FACILITY',
      assetId: 'AHU-02',
      deviceId: 'FAN-02',
      metadata: { site: 'Singapore DC', priority: 'P2' },
    },
  },
]

function templateMetadata(pkg: ProductizedPackageSeed): Prisma.InputJsonValue {
  return {
    ...PACKAGE_META,
    packageType: pkg.packageType,
    compatibleSystems: pkg.compatibleSystems,
    supportedInputModes: pkg.supportedInputModes,
    businessDescription: pkg.businessDescription,
    businessValue: pkg.businessValue,
    pocUsage: pkg.pocUsageNotes,
    pocUsageNotes: pkg.pocUsageNotes,
    engineeringGuide: pkg.engineeringGuide,
    samplePayload: pkg.samplePayload,
    expectedNormalizedEvent: pkg.expectedNormalizedEvent,
  } as Prisma.InputJsonValue
}

async function upsertIntegrationProfileMappings(
  prisma: PrismaClient,
  profileId: string,
  fieldMappings: FieldMappingSeed[],
  valueMappings: ValueMappingSeed[],
  seedNow: Date,
) {
  await prisma.integrationFieldMapping.deleteMany({ where: { profileId } })
  await prisma.integrationValueMapping.deleteMany({ where: { profileId } })
  if (fieldMappings.length) {
    await prisma.integrationFieldMapping.createMany({
      data: fieldMappings.map((m) => ({
        ...m,
        profileId,
        isRequired: m.isRequired ?? false,
        defaultValue: m.defaultValue ?? null,
        createdAt: seedNow,
        updatedAt: seedNow,
      })),
      skipDuplicates: true,
    })
  }
  if (valueMappings.length) {
    await prisma.integrationValueMapping.createMany({
      data: valueMappings.map((m) => ({
        ...m,
        profileId,
        createdAt: seedNow,
        updatedAt: seedNow,
      })),
      skipDuplicates: true,
    })
  }
}

async function seedPackage(prisma: PrismaClient, pkg: ProductizedPackageSeed, ts: SeedTimestamps) {
  const { seedNow, parseMockTimestamp } = ts
  const siteId = 'SITE-001'

  await prisma.externalSystem.upsert({
    where: { externalSystemId: pkg.externalSystem.externalSystemId },
    create: {
      externalSystemId: pkg.externalSystem.externalSystemId,
      siteId,
      systemCode: pkg.externalSystem.systemCode,
      systemName: pkg.externalSystem.systemName,
      systemType: pkg.externalSystem.systemType,
      vendor: pkg.externalSystem.vendor,
      status: 'ACTIVE',
      description: pkg.externalSystem.description,
      productName: pkg.externalSystem.productName,
      productVersion: pkg.externalSystem.productVersion,
      networkZone: pkg.externalSystem.networkZone,
      isActive: true,
      metadata: {
        ...PACKAGE_META,
        packageType: pkg.packageType,
        compatibleSystems: pkg.compatibleSystems,
        pocUsage: pkg.externalSystem.pocUsage,
      },
      createdAt: seedNow,
      updatedAt: seedNow,
    },
    update: {
      systemName: pkg.externalSystem.systemName,
      systemType: pkg.externalSystem.systemType,
      vendor: pkg.externalSystem.vendor,
      status: 'ACTIVE',
      description: pkg.externalSystem.description,
      productName: pkg.externalSystem.productName,
      productVersion: pkg.externalSystem.productVersion,
      networkZone: pkg.externalSystem.networkZone,
      isActive: true,
      metadata: {
        ...PACKAGE_META,
        packageType: pkg.packageType,
        compatibleSystems: pkg.compatibleSystems,
        pocUsage: pkg.externalSystem.pocUsage,
      },
      updatedAt: seedNow,
    },
  })

  await prisma.connector.upsert({
    where: { connectorId: pkg.connector.connectorId },
    create: {
      connectorId: pkg.connector.connectorId,
      connectorCode: pkg.connector.connectorCode,
      connectorName: pkg.connector.connectorName,
      adapterId: pkg.connector.adapterId,
      protocol: pkg.connector.protocol,
      externalSystemId: pkg.externalSystem.externalSystemId,
      status: ConnectorStatus.ONLINE,
      siteId,
      lastPollTime: seedNow,
      description: `Productized integration connector for ${pkg.integrationProfile.profileName}.`,
      createdAt: seedNow,
      updatedAt: seedNow,
    },
    update: {
      connectorName: pkg.connector.connectorName,
      protocol: pkg.connector.protocol,
      externalSystemId: pkg.externalSystem.externalSystemId,
      status: ConnectorStatus.ONLINE,
      updatedAt: seedNow,
    },
  })

  await prisma.protocolProfile.upsert({
    where: { protocolProfileId: pkg.protocolProfile.protocolProfileId },
    create: {
      protocolProfileId: pkg.protocolProfile.protocolProfileId,
      adapterId: pkg.connector.adapterId,
      profileCode: pkg.protocolProfile.profileCode,
      profileName: pkg.protocolProfile.profileName,
      protocol: pkg.protocolProfile.protocol,
      protocolType: pkg.protocolProfile.protocolType,
      version: '1.0',
      status: 'ACTIVE',
      supportsPolling: pkg.protocolProfile.supportedModes.includes('REST_API') || pkg.protocolProfile.supportedModes.includes('CSV'),
      supportsPush: pkg.protocolProfile.supportedModes.includes('WEBHOOK'),
      supportsBatch: pkg.protocolProfile.supportedModes.some((m) => ['CSV', 'EXCEL', 'FILE_DROP'].includes(m)),
      isActive: true,
      metadata: {
        ...PACKAGE_META,
        packageType: pkg.packageType,
        supportedInputModes: pkg.protocolProfile.supportedModes,
      },
      createdById: 'seed-admin',
      createdAt: seedNow,
      updatedAt: seedNow,
    },
    update: {
      profileName: pkg.protocolProfile.profileName,
      protocol: pkg.protocolProfile.protocol,
      protocolType: pkg.protocolProfile.protocolType,
      status: 'ACTIVE',
      isActive: true,
      metadata: {
        ...PACKAGE_META,
        packageType: pkg.packageType,
        supportedInputModes: pkg.protocolProfile.supportedModes,
      },
      updatedAt: seedNow,
    },
  })

  const endpointUrl =
    pkg.connectionProfile.baseUrl && pkg.connectionProfile.endpointPath
      ? `${pkg.connectionProfile.baseUrl}${pkg.connectionProfile.endpointPath}`
      : pkg.connectionProfile.baseUrl ?? null

  await prisma.connectionProfile.upsert({
    where: { connectionProfileId: pkg.connectionProfile.connectionProfileId },
    create: {
      connectionProfileId: pkg.connectionProfile.connectionProfileId,
      connectorId: pkg.connector.connectorId,
      profileCode: pkg.connectionProfile.profileCode,
      profileName: pkg.connectionProfile.profileName,
      protocol: pkg.connectionProfile.protocol,
      protocolType: pkg.connectionProfile.protocolType,
      baseUrl: pkg.connectionProfile.baseUrl ?? null,
      endpointPath: pkg.connectionProfile.endpointPath ?? null,
      endpointUrl,
      filePath: pkg.connectionProfile.filePath ?? null,
      authType: pkg.connectionProfile.authType ?? null,
      authMode: pkg.connectionProfile.authType ?? null,
      supportsPolling: pkg.connectionProfile.supportsPolling ?? false,
      supportsPush: pkg.connectionProfile.supportsPush ?? false,
      supportsBatch: pkg.connectionProfile.supportsBatch ?? false,
      status: 'ACTIVE',
      isActive: true,
      metadata: {
        ...PACKAGE_META,
        packageType: pkg.packageType,
        ...(pkg.connectionProfile.metadata as object),
      },
      createdById: 'seed-admin',
      createdAt: seedNow,
      updatedAt: seedNow,
    },
    update: {
      profileName: pkg.connectionProfile.profileName,
      protocol: pkg.connectionProfile.protocol,
      protocolType: pkg.connectionProfile.protocolType,
      baseUrl: pkg.connectionProfile.baseUrl ?? null,
      endpointPath: pkg.connectionProfile.endpointPath ?? null,
      endpointUrl,
      filePath: pkg.connectionProfile.filePath ?? null,
      authType: pkg.connectionProfile.authType ?? null,
      authMode: pkg.connectionProfile.authType ?? null,
      status: 'ACTIVE',
      isActive: true,
      metadata: {
        ...PACKAGE_META,
        packageType: pkg.packageType,
        ...(pkg.connectionProfile.metadata as object),
      },
      updatedAt: seedNow,
    },
  })

  await prisma.faultSource.upsert({
    where: { sourceId: pkg.faultSource.sourceId },
    create: {
      sourceId: pkg.faultSource.sourceId,
      connectorId: pkg.connector.connectorId,
      externalSystemId: pkg.externalSystem.externalSystemId,
      sourceName: pkg.faultSource.sourceName,
      sourceType: pkg.faultSource.sourceType,
      protocol: pkg.faultSource.protocol,
      status: 'Connected',
      lastPollTime: seedNow,
      code: pkg.faultSource.code,
      sourceCategory: 'productized_package',
      systemDomain: pkg.faultSource.systemDomain,
      siteName: pkg.faultSource.siteName,
      location: pkg.faultSource.location,
      ownerTeam: pkg.faultSource.ownerTeam,
      governanceStatus: 'ACTIVE',
      trustLevel: 'HIGH',
      dataCriticality: 'high',
      validationRequired: true,
      importAllowed: true,
      eventCreationAllowed: true,
      integrationProfileId: pkg.integrationProfile.profileId,
      isActive: true,
      metadata: { ...PACKAGE_META, packageType: pkg.packageType },
      createdAt: seedNow,
      updatedAt: seedNow,
    },
    update: {
      sourceName: pkg.faultSource.sourceName,
      sourceType: pkg.faultSource.sourceType,
      protocol: pkg.faultSource.protocol,
      status: 'Connected',
      integrationProfileId: pkg.integrationProfile.profileId,
      isActive: true,
      metadata: { ...PACKAGE_META, packageType: pkg.packageType },
      updatedAt: seedNow,
    },
  })

  await prisma.mappingTemplate.upsert({
    where: { mappingTemplateId: pkg.mappingTemplate.mappingTemplateId },
    create: {
      mappingTemplateId: pkg.mappingTemplate.mappingTemplateId,
      templateCode: pkg.mappingTemplate.templateCode,
      templateName: pkg.mappingTemplate.templateName,
      sourceSystemType: pkg.mappingTemplate.sourceSystemType,
      inputMode: pkg.mappingTemplate.inputMode,
      status: 'ACTIVE',
      description: pkg.mappingTemplate.description,
      templateSchema: pkg.mappingTemplate.templateSchema,
      isActive: true,
      metadata: templateMetadata(pkg),
      createdById: 'seed-admin',
      createdAt: seedNow,
      updatedAt: seedNow,
    },
    update: {
      templateName: pkg.mappingTemplate.templateName,
      sourceSystemType: pkg.mappingTemplate.sourceSystemType,
      inputMode: pkg.mappingTemplate.inputMode,
      status: 'ACTIVE',
      description: pkg.mappingTemplate.description,
      templateSchema: pkg.mappingTemplate.templateSchema,
      isActive: true,
      metadata: templateMetadata(pkg),
      updatedAt: seedNow,
    },
  })

  await prisma.integrationProfile.upsert({
    where: { profileId: pkg.integrationProfile.profileId },
    create: {
      profileId: pkg.integrationProfile.profileId,
      profileCode: pkg.integrationProfile.profileCode,
      profileName: pkg.integrationProfile.profileName,
      description: pkg.integrationProfile.description,
      sourceSystemName: pkg.integrationProfile.sourceSystemName,
      sourceSystemType: pkg.integrationProfile.sourceSystemType,
      inputMode: pkg.integrationProfile.inputMode,
      linkedFaultSourceId: pkg.faultSource.sourceId,
      siteName: pkg.integrationProfile.siteName,
      systemDomain: pkg.integrationProfile.systemDomain,
      status: 'ACTIVE',
      ownerTeam: pkg.integrationProfile.ownerTeam,
      unknownSeverityHandling: 'USE_DEFAULT',
      unknownStatusHandling: 'USE_DEFAULT',
      defaultSeverity: pkg.integrationProfile.defaultSeverity,
      defaultStatus: pkg.integrationProfile.defaultStatus,
      notes: pkg.pocUsageNotes,
      lastTestedAt: seedNow,
      lastActivatedAt: seedNow,
      externalSystemId: pkg.externalSystem.externalSystemId,
      connectionProfileId: pkg.connectionProfile.connectionProfileId,
      mappingTemplateId: pkg.mappingTemplate.mappingTemplateId,
      sourceType: pkg.integrationProfile.sourceType,
      targetObjectType: 'event',
      profileVersion: '1.0',
      isActive: true,
      metadata: {
        ...PACKAGE_META,
        packageType: pkg.packageType,
        mappingTemplateId: pkg.mappingTemplate.mappingTemplateId,
      },
      createdBy: 'seed-admin',
      createdAt: seedNow,
      updatedAt: seedNow,
    },
    update: {
      profileName: pkg.integrationProfile.profileName,
      description: pkg.integrationProfile.description,
      sourceSystemName: pkg.integrationProfile.sourceSystemName,
      sourceSystemType: pkg.integrationProfile.sourceSystemType,
      inputMode: pkg.integrationProfile.inputMode,
      linkedFaultSourceId: pkg.faultSource.sourceId,
      status: 'ACTIVE',
      externalSystemId: pkg.externalSystem.externalSystemId,
      connectionProfileId: pkg.connectionProfile.connectionProfileId,
      mappingTemplateId: pkg.mappingTemplate.mappingTemplateId,
      lastTestedAt: seedNow,
      lastActivatedAt: seedNow,
      isActive: true,
      metadata: {
        ...PACKAGE_META,
        packageType: pkg.packageType,
        mappingTemplateId: pkg.mappingTemplate.mappingTemplateId,
      },
      updatedAt: seedNow,
    },
  })

  await upsertIntegrationProfileMappings(
    prisma,
    pkg.integrationProfile.profileId,
    pkg.integrationProfile.fieldMappings,
    pkg.integrationProfile.valueMappings,
    seedNow,
  )

  await prisma.integrationTestRun.upsert({
    where: { testRunId: `ITR-${pkg.packageType}` },
    create: {
      testRunId: `ITR-${pkg.packageType}`,
      profileId: pkg.integrationProfile.profileId,
      runBy: 'seed-admin',
      runAt: seedNow,
      status: 'Valid',
      sampleInput: pkg.samplePayload as Prisma.InputJsonValue,
      createdAt: seedNow,
      updatedAt: seedNow,
      results: {
        create: {
          testResultId: `ITRES-${pkg.packageType}`,
          validationStatus: 'Valid',
          mappedEvent: pkg.expectedNormalizedEvent as Prisma.InputJsonValue,
          normalizedPayload: pkg.expectedNormalizedEvent as Prisma.InputJsonValue,
          qualityScore: 95,
          warnings: [],
          errors: [],
          missingRequired: [],
          createdAt: seedNow,
          updatedAt: seedNow,
        },
      },
    },
    update: {
      runAt: seedNow,
      status: 'Valid',
      sampleInput: pkg.samplePayload as Prisma.InputJsonValue,
      updatedAt: seedNow,
    },
  })

  await prisma.rawMessage.upsert({
    where: { id: pkg.rawMessage.id },
    create: {
      id: pkg.rawMessage.id,
      externalSystemId: pkg.externalSystem.externalSystemId,
      integrationProfileId: pkg.integrationProfile.profileId,
      faultSourceId: pkg.faultSource.sourceId,
      sourceRecordId: pkg.rawMessage.sourceRecordId,
      protocolType: pkg.rawMessage.protocolType,
      messageType: pkg.rawMessage.messageType,
      rawPayload: pkg.samplePayload as Prisma.InputJsonValue,
      processingStatus: 'PROCESSED',
      normalizedEventId: pkg.sampleEvent?.eventId ?? null,
      receivedAt: seedNow,
      metadata: { ...PACKAGE_META, packageType: pkg.packageType },
      createdAt: seedNow,
      updatedAt: seedNow,
    },
    update: {
      rawPayload: pkg.samplePayload as Prisma.InputJsonValue,
      processingStatus: 'PROCESSED',
      normalizedEventId: pkg.sampleEvent?.eventId ?? null,
      updatedAt: seedNow,
    },
  })

  if (pkg.sampleEvent) {
    await prisma.event.upsert({
      where: { eventId: pkg.sampleEvent.eventId },
      create: {
        eventId: pkg.sampleEvent.eventId,
        sourceId: pkg.faultSource.sourceId,
        sourceLabel: pkg.faultSource.sourceName,
        severity: pkg.sampleEvent.severity,
        category: pkg.sampleEvent.category,
        assetLabel: pkg.sampleEvent.assetLabel,
        title: pkg.sampleEvent.title,
        status: pkg.sampleEvent.status,
        occurredTime: parseMockTimestamp(pkg.sampleEvent.occurredTime),
        siteId,
        externalSystemId: pkg.externalSystem.externalSystemId,
        integrationProfileId: pkg.integrationProfile.profileId,
        rawMessageId: pkg.rawMessage.id,
        sourceRecordId: pkg.rawMessage.sourceRecordId,
        externalReferenceId: pkg.sampleEvent.externalReferenceId,
        sourceType: pkg.sampleEvent.sourceType,
        eventCategory: pkg.sampleEvent.eventCategory,
        deviceId: pkg.sampleEvent.deviceId ?? null,
        assetId: pkg.sampleEvent.assetId ?? null,
        confidence: pkg.sampleEvent.confidence ?? null,
        snapshotUrl: pkg.sampleEvent.snapshotUrl ?? null,
        metadata: pkg.sampleEvent.metadata ?? undefined,
        createdAt: seedNow,
        updatedAt: seedNow,
      },
      update: {
        title: pkg.sampleEvent.title,
        severity: pkg.sampleEvent.severity,
        status: pkg.sampleEvent.status,
        integrationProfileId: pkg.integrationProfile.profileId,
        rawMessageId: pkg.rawMessage.id,
        updatedAt: seedNow,
      },
    })
  }
}

export async function seedProductizedIntegrationPackage(
  prisma: PrismaClient,
  seedNow: Date,
  parseMockTimestamp: (value: string) => Date,
) {
  const ts: SeedTimestamps = { seedNow, parseMockTimestamp }
  for (const pkg of PACKAGES) {
    await seedPackage(prisma, pkg, ts)
  }
  console.log(
    `Productized integration package seed complete: ${PACKAGES.length} standard packages (BMS, AI Video, CSV Import, AegisNexus IBMS).`,
  )
}
