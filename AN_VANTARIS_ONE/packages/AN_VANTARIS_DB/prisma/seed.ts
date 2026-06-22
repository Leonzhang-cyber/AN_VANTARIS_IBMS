import { PrismaClient } from '@prisma/client'
import * as bcrypt from 'bcrypt'
import { buildCatalogReferenceCodeRows } from './seed-reference-catalog'
import { seedCommercialFoundation } from './seed-commercial-foundation'
import { seedUatEnhancements } from './seed-uat-enhancements'
import { seedProductizedIntegrationPackage } from './seed-productized-integration-package'
import {
  UFMS_PERMISSION_SEED,
  UFMS_ROLE_DEFINITIONS,
  UFMS_TEST_USERS,
  buildUfmsRolePermissionCodes,
} from './seed-ufms-rbac'

const prisma = new PrismaClient()
const BCRYPT_ROUNDS = 10

const SEED_NOW = new Date('2026-06-02T10:00:00.000Z')

function parseMockTimestamp(value: string): Date {
  const normalized = value.replace(' ', 'T')
  return new Date(`${normalized}:00.000Z`)
}

function parseDueDate(value: string): Date {
  return new Date(`${value}T00:00:00.000Z`)
}

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, BCRYPT_ROUNDS)
}

const PERMISSION_SEED = [
  { permissionId: 'PERM-001', permissionCode: 'registry:read', permissionName: 'Registry Read' },
  { permissionId: 'PERM-002', permissionCode: 'integration:read', permissionName: 'Integration Read' },
  { permissionId: 'PERM-003', permissionCode: 'operations:read', permissionName: 'Operations Read' },
  { permissionId: 'PERM-004', permissionCode: 'trust:read', permissionName: 'Trust Read' },
  { permissionId: 'PERM-005', permissionCode: 'decision:read', permissionName: 'Decision Read' },
  { permissionId: 'PERM-006', permissionCode: 'dashboard:read', permissionName: 'Dashboard Read' },
  { permissionId: 'PERM-007', permissionCode: 'operations:write', permissionName: 'Operations Write' },
  { permissionId: 'PERM-008', permissionCode: 'trust:append', permissionName: 'Trust Append' },
  { permissionId: 'PERM-009', permissionCode: 'evidence:upload', permissionName: 'Evidence Upload' },
  { permissionId: 'PERM-010', permissionCode: 'approval:request', permissionName: 'Approval Request' },
  { permissionId: 'PERM-011', permissionCode: 'approval:decide', permissionName: 'Approval Decide' },
  { permissionId: 'PERM-012', permissionCode: 'decision:submit', permissionName: 'Decision Submit' },
  { permissionId: 'PERM-013', permissionCode: 'decision:approve', permissionName: 'Decision Approve' },
  { permissionId: 'PERM-014', permissionCode: 'iam:user:read', permissionName: 'IAM User Read' },
  { permissionId: 'PERM-015', permissionCode: 'iam:user:create', permissionName: 'IAM User Create' },
  { permissionId: 'PERM-016', permissionCode: 'iam:user:update', permissionName: 'IAM User Update' },
  { permissionId: 'PERM-017', permissionCode: 'iam:user:disable', permissionName: 'IAM User Disable' },
  {
    permissionId: 'PERM-018',
    permissionCode: 'iam:user:reset-password',
    permissionName: 'IAM User Reset Password',
  },
  { permissionId: 'PERM-019', permissionCode: 'iam:role:assign', permissionName: 'IAM Role Assign' },
  {
    permissionId: 'PERM-020',
    permissionCode: 'import_batch:read',
    permissionName: 'Import Batch Governance Read',
  },
  {
    permissionId: 'PERM-021',
    permissionCode: 'import_batch:write',
    permissionName: 'Import Batch Governance Write',
  },
  {
    permissionId: 'PERM-022',
    permissionCode: 'fault_source:read',
    permissionName: 'Fault Source Governance Read',
  },
  {
    permissionId: 'PERM-023',
    permissionCode: 'fault_source:write',
    permissionName: 'Fault Source Governance Write',
  },
  {
    permissionId: 'PERM-024',
    permissionCode: 'data_quality:read',
    permissionName: 'Data Quality Dashboard Read',
  },
  {
    permissionId: 'PERM-025',
    permissionCode: 'data_lineage:read',
    permissionName: 'Data Lineage Lite Read',
  },
  {
    permissionId: 'PERM-026',
    permissionCode: 'pilot_activity:read',
    permissionName: 'Pilot Activity & Access Audit Read',
  },
  {
    permissionId: 'PERM-027',
    permissionCode: 'integration_config:read',
    permissionName: 'Integration Configuration Read',
  },
  {
    permissionId: 'PERM-028',
    permissionCode: 'integration_config:write',
    permissionName: 'Integration Configuration Write',
  },
  { permissionId: 'PERM-029', permissionCode: 'events:read', permissionName: 'Events Read' },
  { permissionId: 'PERM-030', permissionCode: 'events:create', permissionName: 'Events Create' },
  { permissionId: 'PERM-031', permissionCode: 'events:acknowledge', permissionName: 'Events Acknowledge' },
  { permissionId: 'PERM-032', permissionCode: 'events:promote', permissionName: 'Events Promote' },
  { permissionId: 'PERM-033', permissionCode: 'events:close', permissionName: 'Events Close' },
  { permissionId: 'PERM-034', permissionCode: 'incidents:read', permissionName: 'Incidents Read' },
  { permissionId: 'PERM-035', permissionCode: 'incidents:create', permissionName: 'Incidents Create' },
  { permissionId: 'PERM-036', permissionCode: 'incidents:update', permissionName: 'Incidents Update' },
  { permissionId: 'PERM-037', permissionCode: 'incidents:assign', permissionName: 'Incidents Assign' },
  { permissionId: 'PERM-038', permissionCode: 'incidents:close', permissionName: 'Incidents Close' },
  { permissionId: 'PERM-039', permissionCode: 'work_orders:read', permissionName: 'Work Orders Read' },
  { permissionId: 'PERM-040', permissionCode: 'work_orders:create', permissionName: 'Work Orders Create' },
  { permissionId: 'PERM-041', permissionCode: 'work_orders:update', permissionName: 'Work Orders Update' },
  { permissionId: 'PERM-042', permissionCode: 'work_orders:assign', permissionName: 'Work Orders Assign' },
  { permissionId: 'PERM-043', permissionCode: 'work_orders:close', permissionName: 'Work Orders Close' },
  { permissionId: 'PERM-044', permissionCode: 'timeline:read', permissionName: 'Timeline Read' },
  { permissionId: 'PERM-045', permissionCode: 'timeline:create', permissionName: 'Timeline Create' },
  { permissionId: 'PERM-046', permissionCode: 'evidence:read', permissionName: 'Evidence Read' },
  { permissionId: 'PERM-047', permissionCode: 'evidence:create', permissionName: 'Evidence Create' },
  { permissionId: 'PERM-048', permissionCode: 'audit_logs:read', permissionName: 'Audit Logs Read' },
  { permissionId: 'PERM-049', permissionCode: 'fault_sources:read', permissionName: 'Fault Sources Read' },
  { permissionId: 'PERM-050', permissionCode: 'fault_sources:write', permissionName: 'Fault Sources Write' },
  {
    permissionId: 'PERM-051',
    permissionCode: 'integration_config:test',
    permissionName: 'Integration Configuration Test',
  },
  { permissionId: 'PERM-052', permissionCode: 'alarms:read', permissionName: 'Alarms Read' },
  { permissionId: 'PERM-053', permissionCode: 'alarms:create', permissionName: 'Alarms Create' },
  { permissionId: 'PERM-054', permissionCode: 'alarms:acknowledge', permissionName: 'Alarms Acknowledge' },
  { permissionId: 'PERM-055', permissionCode: 'alarms:manage', permissionName: 'Alarms Manage' },
  { permissionId: 'PERM-056', permissionCode: 'episodes:read', permissionName: 'Episodes Read' },
  { permissionId: 'PERM-057', permissionCode: 'episodes:create', permissionName: 'Episodes Create' },
  { permissionId: 'PERM-058', permissionCode: 'episodes:update', permissionName: 'Episodes Update' },
  { permissionId: 'PERM-059', permissionCode: 'problems:read', permissionName: 'Problems Read' },
  { permissionId: 'PERM-060', permissionCode: 'problems:create', permissionName: 'Problems Create' },
  { permissionId: 'PERM-061', permissionCode: 'problems:update', permissionName: 'Problems Update' },
  { permissionId: 'PERM-062', permissionCode: 'problems:close', permissionName: 'Problems Close' },
  { permissionId: 'PERM-063', permissionCode: 'sla:read', permissionName: 'SLA Read' },
  { permissionId: 'PERM-064', permissionCode: 'sla:configure', permissionName: 'SLA Configure' },
  { permissionId: 'PERM-065', permissionCode: 'sop:read', permissionName: 'SOP Read' },
  { permissionId: 'PERM-066', permissionCode: 'sop:configure', permissionName: 'SOP Configure' },
  { permissionId: 'PERM-067', permissionCode: 'notifications:read', permissionName: 'Notifications Read' },
  { permissionId: 'PERM-068', permissionCode: 'inspections:read', permissionName: 'Inspections Read' },
  { permissionId: 'PERM-069', permissionCode: 'inspections:create', permissionName: 'Inspections Create' },
  { permissionId: 'PERM-070', permissionCode: 'inspections:execute', permissionName: 'Inspections Execute' },
  { permissionId: 'PERM-071', permissionCode: 'contractors:read', permissionName: 'Contractors Read' },
  { permissionId: 'PERM-072', permissionCode: 'contractors:write', permissionName: 'Contractors Write' },
  { permissionId: 'PERM-073', permissionCode: 'spare_parts:read', permissionName: 'Spare Parts Read' },
  { permissionId: 'PERM-074', permissionCode: 'spare_parts:write', permissionName: 'Spare Parts Write' },
  { permissionId: 'PERM-075', permissionCode: 'reports:read', permissionName: 'Reports Read' },
  { permissionId: 'PERM-076', permissionCode: 'rfq:read', permissionName: 'RFQ Read' },
  { permissionId: 'PERM-077', permissionCode: 'rfq:configure', permissionName: 'RFQ Configure' },
  { permissionId: 'PERM-078', permissionCode: 'registry:write', permissionName: 'Registry Write' },
  { permissionId: 'PERM-079', permissionCode: 'connectors:write', permissionName: 'Connectors Write' },
  { permissionId: 'PERM-080', permissionCode: 'connectors:health:read', permissionName: 'Connector Health Read' },
  { permissionId: 'PERM-081', permissionCode: 'field:execute', permissionName: 'Field Execute' },
  { permissionId: 'PERM-082', permissionCode: 'portal:requester', permissionName: 'Portal Requester' },
  { permissionId: 'PERM-083', permissionCode: 'asset_analytics:read', permissionName: 'Asset Analytics Read' },
  ...UFMS_PERMISSION_SEED,
] as const

const ALL_PERMISSION_CODES = PERMISSION_SEED.map((p) => p.permissionCode)
const ROLE_PERMISSION_CODES = buildUfmsRolePermissionCodes(ALL_PERMISSION_CODES)

async function main() {
  await prisma.rolePermission.deleteMany()
  await prisma.userRole.deleteMany()
  await prisma.user.deleteMany()
  await prisma.role.deleteMany()
  await prisma.permission.deleteMany()
  await prisma.notification.deleteMany()
  await prisma.diagnosticReport.deleteMany()
  await prisma.healthCheckItem.deleteMany()
  await prisma.healthCheckRun.deleteMany()
  await prisma.maintenanceSession.deleteMany()
  await prisma.maintenanceAccessConfig.deleteMany()
  await prisma.maintenanceLog.deleteMany()
  await prisma.workOrderSparePart.deleteMany()
  await prisma.inspectionRecord.deleteMany()
  await prisma.inspectionChecklist.deleteMany()
  await prisma.inspectionPlan.deleteMany()
  await prisma.report.deleteMany()
  await prisma.rfqComplianceItem.deleteMany()
  await prisma.decisionEvidence.deleteMany()
  await prisma.decision.deleteMany()
  await prisma.approval.deleteMany()
  await prisma.dataQualityResult.deleteMany()
  await prisma.dataLineage.deleteMany()
  await prisma.alarm.deleteMany()
  await prisma.episode.deleteMany()
  await prisma.problem.deleteMany()
  await prisma.slaPolicy.deleteMany()
  await prisma.sopRule.deleteMany()
  await prisma.requester.deleteMany()
  await prisma.contractor.deleteMany()
  await prisma.sparePart.deleteMany()
  await prisma.evidence.deleteMany()
  await prisma.auditLog.deleteMany()
  await prisma.timeline.deleteMany()
  await prisma.workOrder.deleteMany()
  await prisma.importBatchItem.deleteMany()
  await prisma.importBatch.deleteMany()
  await prisma.rawMessage.deleteMany()
  await prisma.event.deleteMany()
  await prisma.incident.deleteMany()
  await prisma.integrationTestResult.deleteMany()
  await prisma.integrationTestRun.deleteMany()
  await prisma.statusHistory.deleteMany()
  await prisma.referenceCode.deleteMany()
  await prisma.objectLink.deleteMany()
  await prisma.connectionProfile.deleteMany()
  await prisma.protocolProfile.deleteMany()
  await prisma.integrationValueMapping.deleteMany()
  await prisma.integrationFieldMapping.deleteMany()
  await prisma.integrationProfile.deleteMany()
  await prisma.mappingTemplate.deleteMany()
  await prisma.faultSource.deleteMany()
  await prisma.connector.deleteMany()
  await prisma.externalSystem.deleteMany()
  await prisma.adapter.deleteMany()
  await prisma.point.deleteMany()
  await prisma.device.deleteMany()
  await prisma.asset.deleteMany()
  await prisma.location.deleteMany()
  await prisma.site.deleteMany()

  await prisma.site.createMany({
    data: [
      {
        siteId: 'SITE-001',
        siteCode: 'SG-DC',
        siteName: 'Singapore DC',
        country: 'Singapore',
        city: 'Singapore',
        siteType: 'data_center',
        status: 'active',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        siteId: 'SITE-002',
        siteCode: 'JUR-PLANT',
        siteName: 'Jurong Plant',
        country: 'Singapore',
        city: 'Jurong',
        siteType: 'industrial',
        status: 'active',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.asset.createMany({
    data: [
      {
        assetId: 'AST-001',
        siteId: 'SITE-001',
        parentAssetId: null,
        assetCode: 'SG-DC-BLD',
        assetName: 'Singapore DC Building',
        assetType: 'building',
        status: 'active',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        assetId: 'AST-002',
        siteId: 'SITE-001',
        parentAssetId: 'AST-001',
        assetCode: 'L1',
        assetName: 'Level 1',
        assetType: 'floor',
        status: 'active',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        assetId: 'AST-003',
        siteId: 'SITE-001',
        parentAssetId: 'AST-002',
        assetCode: 'UPS-RM',
        assetName: 'UPS Room',
        assetType: 'room',
        status: 'active',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        assetId: 'AST-004',
        siteId: 'SITE-001',
        parentAssetId: 'AST-003',
        assetCode: 'UPS-01',
        assetName: 'UPS-01',
        assetType: 'equipment',
        status: 'active',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.device.createMany({
    data: [
      {
        deviceId: 'DEV-001',
        siteId: 'SITE-001',
        assetId: 'AST-004',
        deviceCode: 'UPS-CTRL',
        deviceName: 'UPS Controller',
        deviceType: 'ups',
        status: 'online',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        deviceId: 'DEV-002',
        siteId: 'SITE-001',
        assetId: 'AST-004',
        deviceCode: 'CRAC-CTRL',
        deviceName: 'CRAC Controller',
        deviceType: 'crac',
        status: 'warning',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        deviceId: 'DEV-003',
        siteId: 'SITE-002',
        assetId: 'AST-004',
        deviceCode: 'PLC-CTRL',
        deviceName: 'PLC Controller',
        deviceType: 'plc',
        status: 'online',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.point.createMany({
    data: [
      {
        pointId: 'PT-001',
        deviceId: 'DEV-001',
        assetId: 'AST-004',
        pointCode: 'UPS.BATT.VOLT',
        pointName: 'Battery Voltage',
        pointType: 'analog',
        unit: 'V',
        value: 48.2,
        quality: 'good',
        timestamp: parseMockTimestamp('2026-06-02 10:15'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        pointId: 'PT-002',
        deviceId: 'DEV-001',
        assetId: 'AST-004',
        pointCode: 'UPS.BATT.AMP',
        pointName: 'Battery Current',
        pointType: 'analog',
        unit: 'A',
        value: 12.5,
        quality: 'good',
        timestamp: parseMockTimestamp('2026-06-02 10:15'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        pointId: 'PT-003',
        deviceId: 'DEV-001',
        assetId: 'AST-004',
        pointCode: 'UPS.BATT.TEMP',
        pointName: 'Battery Temperature',
        pointType: 'analog',
        unit: '°C',
        value: 32.1,
        quality: 'warning',
        timestamp: parseMockTimestamp('2026-06-02 10:16'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.adapter.createMany({
    data: [
      {
        adapterId: 'ADP-001',
        adapterCode: 'BACNET_ADAPTER',
        adapterName: 'BACnet Adapter',
        protocol: 'bacnet',
        version: '1.0',
        status: 'active',
        description: 'Generic BACnet adapter for BMS integration',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        adapterId: 'ADP-002',
        adapterCode: 'MODBUS_TCP_ADAPTER',
        adapterName: 'Modbus TCP Adapter',
        protocol: 'modbus',
        version: '1.0',
        status: 'active',
        description: 'Generic Modbus TCP adapter for PLC integration',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        adapterId: 'ADP-003',
        adapterCode: 'MQTT_ADAPTER',
        adapterName: 'MQTT Adapter',
        protocol: 'mqtt',
        version: '1.0',
        status: 'active',
        description: 'Generic MQTT adapter for IoT gateway integration',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        adapterId: 'ADP-004',
        adapterCode: 'REST_API_ADAPTER',
        adapterName: 'REST API Adapter',
        protocol: 'rest',
        version: '1.0',
        status: 'active',
        description: 'Generic REST API adapter for DCIM and external systems',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        adapterId: 'ADP-005',
        adapterCode: 'OPCUA_ADAPTER',
        adapterName: 'OPC-UA Adapter',
        protocol: 'opcua',
        version: '1.0',
        status: 'active',
        description: 'Generic OPC-UA adapter for industrial integration',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.externalSystem.createMany({
    data: [
      {
        externalSystemId: 'SYS-001',
        systemCode: 'IBMS-AEGIS',
        systemName: 'AegisNexus IBMS',
        systemType: 'ibms',
        vendor: 'AegisNexus',
        siteId: 'SITE-001',
        status: 'active',
        description:
          'Primary integrated building management system at Singapore DC.',
        productName: 'AegisNexus IBMS',
        productVersion: '4.2.1',
        networkZone: 'OT',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        externalSystemId: 'SYS-002',
        systemCode: 'BMS-GEN',
        systemName: 'Building BMS',
        systemType: 'bms',
        vendor: 'Generic',
        siteId: 'SITE-001',
        status: 'active',
        description: 'Building-level BMS for HVAC and electrical monitoring.',
        productName: 'Generic BMS',
        productVersion: '2.0',
        networkZone: 'OT',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        externalSystemId: 'SYS-003',
        systemCode: 'DCIM-GEN',
        systemName: 'Data Center DCIM',
        systemType: 'dcim',
        vendor: 'Generic',
        siteId: 'SITE-001',
        status: 'active',
        description: 'Data center infrastructure management platform.',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        externalSystemId: 'SYS-004',
        systemCode: 'PLC-NET',
        systemName: 'PLC Network',
        systemType: 'plc',
        vendor: 'Generic',
        siteId: 'SITE-002',
        status: 'active',
        description: 'PLC network at Changi Facility.',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        externalSystemId: 'SYS-005',
        systemCode: 'TENABLE-OT',
        systemName: 'Tenable OT Security',
        systemType: 'ot_security',
        vendor: 'Tenable',
        siteId: 'SITE-001',
        status: 'active',
        description: 'OT security monitoring platform (Tenable OT).',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.connector.createMany({
    data: [
      {
        connectorId: 'CON-001',
        connectorCode: 'BMS-CONN',
        connectorName: 'Building BMS Connector',
        adapterId: 'ADP-001',
        protocol: 'BACnet',
        externalSystemId: 'SYS-002',
        status: 'ONLINE',
        siteId: 'SITE-001',
        lastPollTime: parseMockTimestamp('2026-06-02 10:15'),
        description:
          'BACnet/IP ingest for building management system at Singapore DC.',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        connectorId: 'CON-002',
        connectorCode: 'DCIM-CONN',
        connectorName: 'Data Center DCIM Connector',
        adapterId: 'ADP-004',
        protocol: 'REST API',
        externalSystemId: 'SYS-003',
        status: 'ONLINE',
        siteId: 'SITE-001',
        lastPollTime: parseMockTimestamp('2026-06-02 10:18'),
        description: 'REST API ingest for data center DCIM platform.',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        connectorId: 'CON-003',
        connectorCode: 'PLC-CONN',
        connectorName: 'PLC Network Connector',
        adapterId: 'ADP-002',
        protocol: 'Modbus TCP',
        externalSystemId: 'SYS-004',
        status: 'DEGRADED',
        siteId: 'SITE-002',
        lastPollTime: parseMockTimestamp('2026-06-02 10:20'),
        description: 'Modbus TCP ingest for PLC network at Changi Facility.',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        connectorId: 'CON-004',
        connectorCode: 'TENABLE-CONN',
        connectorName: 'Tenable OT Connector',
        adapterId: 'ADP-004',
        protocol: 'API',
        externalSystemId: 'SYS-005',
        status: 'ONLINE',
        siteId: 'SITE-001',
        lastPollTime: parseMockTimestamp('2026-06-02 10:25'),
        description: 'API ingest for Tenable OT security platform.',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.faultSource.createMany({
    data: [
      {
        sourceId: 'SRC-001',
        sourceName: 'BMS Alarm Feed',
        protocol: 'BACnet',
        status: 'Connected',
        lastPollTime: parseMockTimestamp('2026-06-02 10:15'),
        connectorId: 'CON-001',
        externalSystemId: 'SYS-002',
        sourceType: 'BMS',
        sourceCategory: 'building_automation',
        systemDomain: 'Building Management',
        siteName: 'DC Hall A',
        location: 'Building A',
        ownerTeam: 'BMS Operations',
        governanceStatus: 'ACTIVE',
        trustLevel: 'HIGH',
        dataCriticality: 'high',
        validationRequired: true,
        importAllowed: true,
        eventCreationAllowed: true,
        notes: 'Primary BMS alarm feed for hosted demo.',
        lastSeenAt: parseMockTimestamp('2026-06-02 10:15'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        sourceId: 'SRC-002',
        sourceName: 'CSV Pilot Import Source',
        protocol: 'CSV',
        status: 'Connected',
        lastPollTime: parseMockTimestamp('2026-06-02 10:18'),
        connectorId: 'CON-002',
        externalSystemId: 'SYS-003',
        sourceType: 'CSV_IMPORT',
        sourceCategory: 'csv_import',
        systemDomain: 'Operations',
        siteName: 'DC Hall A',
        location: 'Operations',
        ownerTeam: 'Operations',
        governanceStatus: 'ACTIVE',
        trustLevel: 'MEDIUM',
        dataCriticality: 'medium',
        validationRequired: true,
        importAllowed: true,
        eventCreationAllowed: true,
        notes: 'Governed CSV pilot import source (use in CSV faultSourceId).',
        lastSeenAt: parseMockTimestamp('2026-06-02 10:18'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        sourceId: 'SRC-003',
        sourceName: 'Manual Operator Entry',
        protocol: 'Manual',
        status: 'Connected',
        lastPollTime: parseMockTimestamp('2026-06-02 10:20'),
        connectorId: 'CON-003',
        externalSystemId: 'SYS-004',
        sourceType: 'MANUAL',
        sourceCategory: 'manual_entry',
        systemDomain: 'Facility Operations',
        siteName: 'DC Hall A',
        location: 'Control Room',
        ownerTeam: 'Operations',
        governanceStatus: 'ACTIVE',
        trustLevel: 'MEDIUM',
        dataCriticality: 'medium',
        validationRequired: false,
        importAllowed: false,
        eventCreationAllowed: true,
        notes: 'Operator manual fault observations.',
        lastSeenAt: parseMockTimestamp('2026-06-02 10:20'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        sourceId: 'SRC-004',
        sourceName: 'Legacy Chiller Fault Feed',
        protocol: 'SCADA',
        status: 'Warning',
        lastPollTime: parseMockTimestamp('2026-06-02 10:25'),
        connectorId: 'CON-004',
        externalSystemId: 'SYS-005',
        sourceType: 'SCADA',
        sourceCategory: 'hvac',
        systemDomain: 'Mechanical / HVAC',
        siteName: 'DC Hall A',
        location: 'Plant Room',
        ownerTeam: 'Mechanical',
        governanceStatus: 'DEGRADED',
        trustLevel: 'LOW',
        dataCriticality: 'high',
        validationRequired: true,
        importAllowed: true,
        eventCreationAllowed: true,
        notes: 'Legacy chiller feed — degraded reliability.',
        lastSeenAt: parseMockTimestamp('2026-06-02 10:25'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.integrationProfile.create({
    data: {
      profileId: 'PROFILE-001',
      profileCode: 'PROFILE-001',
      profileName: 'BMS Alarm Feed Mapping',
      description: 'Maps BMS alarm CSV columns to UFMS event fields for pilot imports.',
      sourceSystemName: 'Building Management System',
      sourceSystemType: 'BMS',
      inputMode: 'CSV_UPLOAD',
      linkedFaultSourceId: 'SRC-001',
      siteName: 'DC Hall A',
      systemDomain: 'Building Management',
      status: 'ACTIVE',
      ownerTeam: 'BMS Operations',
      unknownSeverityHandling: 'USE_DEFAULT',
      unknownStatusHandling: 'USE_DEFAULT',
      defaultSeverity: 'minor',
      defaultStatus: 'new',
      notes: 'Demo integration profile for B27 no-code mapping.',
      lastTestedAt: SEED_NOW,
      lastActivatedAt: SEED_NOW,
      externalSystemId: 'SYS-002',
      sourceType: 'CSV',
      targetObjectType: 'event',
      profileVersion: '1.0',
      createdBy: 'seed-admin',
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
      fieldMappings: {
        create: [
          {
            mappingId: 'IFM-0001',
            externalFieldName: 'AlarmID',
            ufmsFieldName: 'externalEventId',
            isRequired: false,
            sortOrder: 0,
          },
          {
            mappingId: 'IFM-0002',
            externalFieldName: 'AlarmText',
            ufmsFieldName: 'title',
            isRequired: true,
            sortOrder: 1,
          },
          {
            mappingId: 'IFM-0003',
            externalFieldName: 'Priority',
            ufmsFieldName: 'severity',
            isRequired: true,
            defaultValue: 'minor',
            sortOrder: 2,
          },
          {
            mappingId: 'IFM-0004',
            externalFieldName: 'AlarmTime',
            ufmsFieldName: 'occurredAt',
            isRequired: true,
            sortOrder: 3,
          },
          {
            mappingId: 'IFM-0005',
            externalFieldName: 'EquipmentName',
            ufmsFieldName: 'assetName',
            isRequired: false,
            sortOrder: 4,
          },
          {
            mappingId: 'IFM-0006',
            externalFieldName: 'CurrentStatus',
            ufmsFieldName: 'status',
            isRequired: false,
            defaultValue: 'new',
            sortOrder: 5,
          },
        ],
      },
      valueMappings: {
        create: [
          { mappingId: 'IVM-0001', mappingType: 'severity', externalValue: 'P1', ufmsValue: 'critical', sortOrder: 0 },
          { mappingId: 'IVM-0002', mappingType: 'severity', externalValue: 'P2', ufmsValue: 'major', sortOrder: 1 },
          { mappingId: 'IVM-0003', mappingType: 'severity', externalValue: 'P3', ufmsValue: 'minor', sortOrder: 2 },
          { mappingId: 'IVM-0004', mappingType: 'severity', externalValue: 'Warning', ufmsValue: 'warning', sortOrder: 3 },
          { mappingId: 'IVM-0005', mappingType: 'severity', externalValue: 'Info', ufmsValue: 'info', sortOrder: 4 },
          { mappingId: 'IVM-0006', mappingType: 'status', externalValue: 'Active', ufmsValue: 'new', sortOrder: 0 },
          { mappingId: 'IVM-0007', mappingType: 'status', externalValue: 'Acknowledged', ufmsValue: 'acknowledged', sortOrder: 1 },
          { mappingId: 'IVM-0008', mappingType: 'status', externalValue: 'Cleared', ufmsValue: 'resolved', sortOrder: 2 },
        ],
      },
    },
  })

  await prisma.mappingTemplate.create({
    data: {
      mappingTemplateId: 'MTPL-001',
      templateCode: 'BMS-CSV-V1',
      templateName: 'BMS CSV Alarm Template',
      sourceSystemType: 'BMS',
      inputMode: 'CSV_UPLOAD',
      status: 'ACTIVE',
      description: 'Standard BMS alarm CSV column layout for UFMS event import.',
      templateSchema: {
        columns: ['AlarmID', 'AlarmText', 'Priority', 'AlarmTime', 'EquipmentName', 'CurrentStatus'],
      },
      isActive: true,
      createdById: 'seed-admin',
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
    },
  })

  await prisma.integrationProfile.update({
    where: { profileId: 'PROFILE-001' },
    data: { mappingTemplateId: 'MTPL-001' },
  })

  await prisma.referenceCode.createMany({
    data: [
      {
        referenceCodeId: 'RC-001',
        objectType: 'external_system',
        objectId: 'SYS-002',
        codeType: 'vendor_code',
        codeValue: 'BMS-GEN',
        description: 'Building BMS vendor reference',
        isActive: true,
        createdById: 'seed-admin',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        referenceCodeId: 'RC-002',
        objectType: 'integration_profile',
        objectId: 'PROFILE-001',
        codeType: 'profile_alias',
        codeValue: 'BMS-ALARM-FEED',
        description: 'Operational alias for BMS alarm mapping profile',
        isActive: true,
        createdById: 'seed-admin',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      ...buildCatalogReferenceCodeRows(SEED_NOW, 100),
    ],
  })

  await prisma.objectLink.create({
    data: {
      objectLinkId: 'OL-001',
      sourceObjectType: 'integration_profile',
      sourceObjectId: 'PROFILE-001',
      targetObjectType: 'fault_source',
      targetObjectId: 'SRC-001',
      linkType: 'maps_to',
      linkStatus: 'active',
      createdById: 'seed-admin',
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
    },
  })

  await prisma.connectionProfile.create({
    data: {
      connectionProfileId: 'CP-001',
      connectorId: 'CON-001',
      profileCode: 'BMS-POLL-V1',
      profileName: 'BMS Polling Connection',
      protocol: 'REST',
      protocolType: 'REST_API',
      transport: 'HTTPS',
      direction: 'INBOUND',
      host: 'bms.example.local',
      port: 443,
      baseUrl: 'https://bms.example.local',
      endpointPath: '/api/v1/alarms',
      pollingIntervalSec: 60,
      authType: 'api_key',
      supportsPolling: true,
      endpointUrl: 'https://bms.example.local/api/v1/alarms',
      authMode: 'api_key',
      status: 'ACTIVE',
      trustLevel: 'MEDIUM',
      isActive: true,
      createdById: 'seed-admin',
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
    },
  })

  await prisma.integrationProfile.update({
    where: { profileId: 'PROFILE-001' },
    data: { connectionProfileId: 'CP-001' },
  })

  await seedProductizedIntegrationPackage(prisma, SEED_NOW, parseMockTimestamp)

  await prisma.protocolProfile.create({
    data: {
      protocolProfileId: 'PP-001',
      adapterId: 'ADP-001',
      profileCode: 'REST-V1',
      profileName: 'REST Adapter Profile',
      protocol: 'REST',
      protocolType: 'REST_API',
      transport: 'HTTPS',
      direction: 'BIDIRECTIONAL',
      supportsPolling: true,
      supportsPush: true,
      securityMode: 'TLS',
      version: '1.0',
      status: 'ACTIVE',
      trustLevel: 'MEDIUM',
      isActive: true,
      createdById: 'seed-admin',
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
    },
  })

  await prisma.integrationTestRun.create({
    data: {
      testRunId: 'ITR-001',
      profileId: 'PROFILE-001',
      runBy: 'seed-admin',
      runAt: SEED_NOW,
      status: 'Valid',
      sampleInput: {
        AlarmID: 'A-1001',
        AlarmText: 'Chiller high temperature',
        Priority: 'P1',
        AlarmTime: '2026-06-05T10:00:00Z',
        EquipmentName: 'Chiller Plant 1',
        CurrentStatus: 'Active',
      },
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
      results: {
        create: {
          testResultId: 'ITRES-001',
          validationStatus: 'Valid',
          mappedEvent: {
            title: 'Chiller high temperature',
            severity: 'critical',
            occurredAt: '2026-06-05T10:00:00Z',
            assetName: 'Chiller Plant 1',
            status: 'new',
            externalEventId: 'A-1001',
            faultSourceId: 'SRC-001',
          },
          csvPreview: {
            eventTitle: 'Chiller high temperature',
            severity: 'critical',
            status: 'new',
            occurredAt: '2026-06-05T10:00:00Z',
            faultSourceId: 'SRC-001',
          },
          errors: [],
          warnings: [],
          missingRequired: [],
          normalizedPayload: {
            title: 'Chiller high temperature',
            severity: 'critical',
            occurredAt: '2026-06-05T10:00:00Z',
            assetName: 'Chiller Plant 1',
            status: 'new',
            externalEventId: 'A-1001',
            faultSourceId: 'SRC-001',
          },
          qualityScore: 1,
          createdAt: SEED_NOW,
          updatedAt: SEED_NOW,
        },
      },
    },
  })

  await prisma.statusHistory.createMany({
    data: [
      {
        statusHistoryId: 'SH-001',
        objectType: 'integration_profile',
        objectId: 'PROFILE-001',
        statusFrom: 'DRAFT',
        statusTo: 'ACTIVE',
        changeReason: 'activated',
        changedById: 'seed-admin',
        changedAt: SEED_NOW,
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        statusHistoryId: 'SH-002',
        objectType: 'external_system',
        objectId: 'SYS-002',
        statusTo: 'active',
        changeReason: 'created',
        changedById: 'seed-admin',
        changedAt: SEED_NOW,
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.incident.createMany({
    data: [
      {
        incidentId: 'INC-001',
        title: 'UPS Battery Incident',
        priority: 'P1',
        status: 'Investigating',
        severity: 'critical',
        category: 'equipment_fault',
        assignedTo: 'Leon',
        assetLabel: 'UPS-01',
        createdAt: parseMockTimestamp('2026-06-02 10:20'),
        updatedAt: SEED_NOW,
      },
      {
        incidentId: 'INC-002',
        title: 'High Temperature Incident',
        priority: 'P2',
        status: 'Assigned',
        severity: 'major',
        category: 'environmental_fault',
        assignedTo: 'Engineer A',
        assetLabel: 'CRAC-02',
        createdAt: parseMockTimestamp('2026-06-02 10:30'),
        updatedAt: SEED_NOW,
      },
      {
        incidentId: 'INC-003',
        title: 'PLC Communication Incident',
        priority: 'P3',
        status: 'Open',
        severity: 'minor',
        category: 'communication_fault',
        assignedTo: 'Engineer B',
        assetLabel: 'PLC-01',
        createdAt: parseMockTimestamp('2026-06-02 10:40'),
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.rawMessage.create({
    data: {
      id: 'clseedrawmsg00001',
      externalSystemId: 'SYS-002',
      integrationProfileId: 'PROFILE-001',
      faultSourceId: 'SRC-001',
      sourceRecordId: 'BMS-CHILLER-9001',
      protocolType: 'CSV',
      messageType: 'CSV_IMPORT',
      rawPayload: {
        AlarmID: 'BMS-CHILLER-9001',
        AlarmText: 'BMS Chiller High Temperature',
        Priority: 'P1',
        EquipmentName: 'Chiller-01',
      },
      processingStatus: 'PROCESSED',
      normalizedEventId: 'EVT-004',
      receivedAt: parseMockTimestamp('2026-06-02 10:40'),
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
    },
  })

  await prisma.event.createMany({
    data: [
      {
        eventId: 'EVT-001',
        sourceId: 'SRC-004',
        sourceLabel: 'Legacy Chiller Fault Feed',
        severity: 'critical',
        category: 'equipment_fault',
        assetLabel: 'UPS-01',
        title: 'UPS Battery Alarm',
        status: 'New',
        occurredTime: parseMockTimestamp('2026-06-02 10:15'),
        incidentId: 'INC-001',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-002',
        sourceId: 'SRC-002',
        sourceLabel: 'CSV Pilot Import Source',
        severity: 'major',
        category: 'environmental_fault',
        assetLabel: 'CRAC-02',
        title: 'High Temperature Alarm',
        status: 'Active',
        occurredTime: parseMockTimestamp('2026-06-02 10:22'),
        incidentId: 'INC-002',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-003',
        sourceId: 'SRC-001',
        sourceLabel: 'BMS Alarm Feed',
        severity: 'minor',
        category: 'communication_fault',
        assetLabel: 'PLC-01',
        title: 'Communication Loss',
        status: 'Promoted',
        occurredTime: parseMockTimestamp('2026-06-02 10:31'),
        incidentId: 'INC-003',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-004',
        sourceId: 'SRC-001',
        sourceLabel: 'BMS Alarm Feed',
        severity: 'critical',
        category: 'equipment_fault',
        assetLabel: 'Chiller-01',
        title: 'BMS Chiller High Temperature',
        status: 'New',
        occurredTime: parseMockTimestamp('2026-06-02 10:40'),
        siteId: 'SITE-001',
        externalSystemId: 'SYS-002',
        integrationProfileId: 'PROFILE-001',
        rawMessageId: 'clseedrawmsg00001',
        sourceRecordId: 'BMS-CHILLER-9001',
        sourceType: 'CSV',
        eventCategory: 'equipment_fault',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-005',
        sourceId: 'SRC-002',
        sourceLabel: 'CSV Pilot Import Source',
        severity: 'major',
        category: 'equipment_fault',
        assetLabel: 'Pump-03',
        title: 'Pump Fault',
        status: 'Active',
        occurredTime: parseMockTimestamp('2026-06-02 10:45'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-006',
        sourceId: 'SRC-003',
        sourceLabel: 'SCADA Pressure Feed',
        severity: 'critical',
        category: 'safety_fault',
        assetLabel: 'Main Switchboard',
        title: 'Power Trip',
        status: 'New',
        occurredTime: parseMockTimestamp('2026-06-02 10:50'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-007',
        sourceId: 'SRC-001',
        sourceLabel: 'BMS Alarm Feed',
        severity: 'warning',
        category: 'safety_fault',
        assetLabel: 'Fire Panel L1',
        title: 'Fire Alarm Panel Warning',
        status: 'Acknowledged',
        acknowledgedAt: parseMockTimestamp('2026-06-02 10:55'),
        occurredTime: parseMockTimestamp('2026-06-02 10:52'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-008',
        sourceId: 'SRC-002',
        sourceLabel: 'CSV Pilot Import Source',
        severity: 'major',
        category: 'safety_fault',
        assetLabel: 'Loading Bay Cam-02',
        title: 'AI Video Safety Alert',
        status: 'Active',
        occurredTime: parseMockTimestamp('2026-06-02 11:00'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-009',
        sourceId: 'SRC-004',
        sourceLabel: 'Legacy Chiller Fault Feed',
        severity: 'warning',
        category: 'environmental_fault',
        assetLabel: 'Chiller Plant',
        title: 'SCADA Pressure Warning',
        status: 'New',
        occurredTime: parseMockTimestamp('2026-06-02 11:05'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        eventId: 'EVT-010',
        sourceId: 'SRC-003',
        sourceLabel: 'SCADA Pressure Feed',
        severity: 'info',
        category: 'operational_fault',
        assetLabel: 'CRAC-02',
        title: 'CRAC Filter Maintenance Due',
        status: 'New',
        occurredTime: parseMockTimestamp('2026-06-02 11:10'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.workOrder.createMany({
    data: [
      {
        workOrderId: 'WO-001',
        incidentId: 'INC-001',
        title: 'UPS Battery Replacement',
        assetId: 'AST-004',
        assetLabel: 'UPS-01',
        assignedTo: 'Leon',
        priority: 'P1',
        status: 'IN_PROGRESS',
        dueDate: parseDueDate('2026-06-03'),
        createdAt: new Date('2026-06-02T10:25:00.000Z'),
        updatedAt: SEED_NOW,
      },
      {
        workOrderId: 'WO-002',
        incidentId: 'INC-002',
        title: 'CRAC High Temperature Investigation',
        assetId: 'AST-004',
        assetLabel: 'CRAC-02',
        assignedTo: 'Engineer A',
        priority: 'P2',
        status: 'ASSIGNED',
        dueDate: parseDueDate('2026-06-04'),
        createdAt: new Date('2026-06-02T10:35:00.000Z'),
        updatedAt: SEED_NOW,
      },
      {
        workOrderId: 'WO-003',
        incidentId: 'INC-003',
        title: 'PLC Communication Recovery',
        assetId: 'AST-004',
        assetLabel: 'PLC-01',
        assignedTo: 'Engineer B',
        priority: 'P3',
        status: 'NEW',
        dueDate: parseDueDate('2026-06-05'),
        createdAt: new Date('2026-06-02T10:45:00.000Z'),
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.timeline.createMany({
    data: [
      {
        timelineId: 'TL-001',
        entityType: 'event',
        entityId: 'EVT-001',
        action: 'created',
        message: 'UPS Battery Alarm received',
        actor: 'system',
        timestamp: parseMockTimestamp('2026-06-02 10:15'),
        source: 'system',
        syncStatus: 'synced',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        timelineId: 'TL-002',
        entityType: 'event',
        entityId: 'EVT-001',
        action: 'promoted',
        message: 'Event promoted to Incident INC-001',
        actor: 'Leon',
        timestamp: parseMockTimestamp('2026-06-02 10:20'),
        source: 'local',
        syncStatus: 'synced',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        timelineId: 'TL-003',
        entityType: 'incident',
        entityId: 'INC-001',
        action: 'investigating',
        message: 'Incident investigation started',
        actor: 'Leon',
        timestamp: parseMockTimestamp('2026-06-02 10:22'),
        source: 'local',
        syncStatus: 'synced',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        timelineId: 'TL-004',
        entityType: 'work_order',
        entityId: 'WO-001',
        action: 'work_order_created',
        message: 'Work Order created for UPS-01',
        actor: 'Leon',
        timestamp: parseMockTimestamp('2026-06-02 10:25'),
        source: 'local',
        syncStatus: 'synced',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        timelineId: 'TL-005',
        entityType: 'work_order',
        entityId: 'WO-001',
        action: 'in_progress',
        message: 'Technician started work',
        actor: 'Leon',
        timestamp: parseMockTimestamp('2026-06-02 10:40'),
        source: 'local',
        syncStatus: 'synced',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.auditLog.createMany({
    data: [
      {
        auditId: 'AUD-001',
        entityType: 'incident',
        entityId: 'INC-001',
        action: 'status_changed',
        oldValue: { status: 'Assigned' },
        newValue: { status: 'Investigating' },
        actor: 'Leon',
        timestamp: parseMockTimestamp('2026-06-02 10:21'),
        hash: 'a3f5c8e91b2d4f6078e9c1a2b3d4e5f6789012345678901234567890abcd',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        auditId: 'AUD-002',
        entityType: 'work_order',
        entityId: 'WO-001',
        action: 'assigned',
        oldValue: { assignedTo: null },
        newValue: { assignedTo: 'Leon' },
        actor: 'Supervisor',
        timestamp: parseMockTimestamp('2026-06-02 10:24'),
        hash: 'b4e6d9f02c3e5a7189f0d2b3c4d5e6f7890123456789012345678901bcde',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        auditId: 'AUD-003',
        entityType: 'work_order',
        entityId: 'WO-001',
        action: 'status_changed',
        oldValue: { status: 'ASSIGNED' },
        newValue: { status: 'IN_PROGRESS' },
        actor: 'Leon',
        timestamp: parseMockTimestamp('2026-06-02 10:26'),
        hash: 'c5f7e0a13d4f6b8290a1e3c4d5e6f7a8901234567890123456789012cdef',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.evidence.createMany({
    data: [
      {
        evidenceId: 'EVD-001',
        entityType: 'incident',
        entityId: 'INC-001',
        fileName: 'ups-battery-inspection.pdf',
        fileHash: 'd6e8f1b24e5a7c9301b2d4e5f6a7b8c9012345678901234567890def1',
        storagePath: 'evidence/EVD-001/ups-battery-inspection.pdf',
        uploadedBy: 'Leon',
        uploadedAt: parseMockTimestamp('2026-06-02 10:23'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        evidenceId: 'EVD-002',
        entityType: 'work_order',
        entityId: 'WO-001',
        fileName: 'wo-001-completion-photo.jpg',
        fileHash: 'e7f9a2c35f6b8d0412c3e4f5a6b7c8d01234567890123456789012ef12',
        storagePath: 'evidence/EVD-002/wo-001-completion-photo.jpg',
        uploadedBy: 'Leon',
        uploadedAt: parseMockTimestamp('2026-06-02 10:35'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await seedCommercialFoundation(prisma, SEED_NOW, parseMockTimestamp)
  await seedUatEnhancements(prisma, SEED_NOW, parseMockTimestamp)

  await prisma.dataLineage.createMany({
    data: [
      {
        lineageId: 'DL-001',
        objectType: 'event',
        objectId: 'EVT-004',
        sourceSystemId: 'SYS-001',
        sourceRecordId: 'BMS-CHILLER-9001',
        transformationStep: 'csv_import',
        mappingProfileId: 'PROFILE-001',
        integrationProfileId: 'PROFILE-001',
        mappingTemplateId: 'MTPL-001',
        rawMessageId: 'clseedrawmsg00001',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        lineageId: 'DL-002',
        objectType: 'event',
        objectId: 'EVT-005',
        sourceSystemId: 'SYS-002',
        sourceRecordId: 'PUMP-FAULT-2201',
        transformationStep: 'connector_poll',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.dataQualityResult.createMany({
    data: [
      {
        resultId: 'DQR-001',
        objectType: 'event',
        objectId: 'EVT-004',
        checkType: 'required_fields',
        status: 'pass',
        score: 100,
        message: 'All required event fields present',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        resultId: 'DQR-002',
        objectType: 'event',
        objectId: 'EVT-009',
        checkType: 'severity_mapping',
        status: 'warn',
        score: 75,
        message: 'Severity mapped from legacy SCADA code',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        resultId: 'DQR-003',
        objectType: 'fault_source',
        objectId: 'SRC-004',
        checkType: 'trust_level',
        status: 'fail',
        score: 40,
        message: 'Fault source trust level is LOW',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.approval.createMany({
    data: [
      {
        approvalId: 'APR-001',
        entityType: 'incident',
        entityId: 'INC-001',
        approvalType: 'incident_closure',
        status: 'pending',
        requestedBy: 'Leon',
        approvedBy: null,
        requestedAt: parseMockTimestamp('2026-06-02 11:00'),
        approvedAt: null,
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        approvalId: 'APR-002',
        entityType: 'work_order',
        entityId: 'WO-001',
        approvalType: 'work_order_completion',
        status: 'approved',
        requestedBy: 'Leon',
        approvedBy: 'Supervisor',
        requestedAt: parseMockTimestamp('2026-06-02 10:30'),
        approvedAt: parseMockTimestamp('2026-06-02 10:45'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.decision.createMany({
    data: [
      {
        decisionId: 'DEC-001',
        incidentId: 'INC-001',
        workOrderId: 'WO-001',
        parentDecisionId: null,
        decisionType: 'root_cause_analysis',
        decisionStatus: 'approved',
        decisionSummary: 'UPS battery degradation confirmed',
        recommendedAction: 'Replace UPS battery module',
        approvedAction: 'Replace UPS battery module',
        decisionBy: 'Leon',
        approvedBy: 'Supervisor',
        decisionTime: parseMockTimestamp('2026-06-02 10:28'),
        decisionHash: 'f8a1b2c3d4e5f60718293a4b5c6d7e8f9012345678901234567890abcd',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        decisionId: 'DEC-002',
        incidentId: 'INC-002',
        workOrderId: 'WO-002',
        parentDecisionId: null,
        decisionType: 'maintenance_decision',
        decisionStatus: 'submitted',
        decisionSummary: 'CRAC temperature abnormal condition requires investigation',
        recommendedAction: 'Inspect CRAC cooling loop',
        approvedAction: null,
        decisionBy: 'Engineer A',
        approvedBy: null,
        decisionTime: parseMockTimestamp('2026-06-02 10:32'),
        decisionHash: 'a9b2c3d4e5f61829304b5c6d7e8f9a0123456789012345678901bcde',
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.decisionEvidence.createMany({
    data: [
      {
        decisionEvidenceId: 'DEC-EVD-001',
        decisionId: 'DEC-001',
        evidenceId: 'EVD-001',
        linkType: 'supporting_evidence',
        linkedBy: 'Leon',
        linkedAt: parseMockTimestamp('2026-06-02 10:29'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
      {
        decisionEvidenceId: 'DEC-EVD-002',
        decisionId: 'DEC-001',
        evidenceId: 'EVD-002',
        linkType: 'work_order_evidence',
        linkedBy: 'Leon',
        linkedAt: parseMockTimestamp('2026-06-02 10:36'),
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    ],
  })

  await prisma.permission.createMany({
    data: PERMISSION_SEED.map((p) => ({
      ...p,
      description: `UFMS permission ${p.permissionCode}`,
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
    })),
  })

  await prisma.role.createMany({
    data: UFMS_ROLE_DEFINITIONS.map((role) => ({
      roleId: role.roleId,
      roleCode: role.roleCode,
      roleName: role.roleName,
      description: role.description,
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
    })),
  })

  const passwordHashes = new Map<string, string>()
  await Promise.all(
    UFMS_TEST_USERS.map(async (user) => {
      passwordHashes.set(user.username, await hashPassword(user.password))
    }),
  )

  await prisma.user.createMany({
    data: UFMS_TEST_USERS.map((user) => ({
      userId: user.userId,
      username: user.username,
      displayName: user.displayName,
      email: user.email,
      passwordHash: passwordHashes.get(user.username)!,
      status: 'active',
      forcePasswordChange: false,
      failedLoginCount: 0,
      lastLoginAt: null,
      createdAt: SEED_NOW,
      updatedAt: SEED_NOW,
    })),
  })

  await prisma.userRole.createMany({
    data: UFMS_TEST_USERS.map((user, index) => {
      const role = UFMS_ROLE_DEFINITIONS.find((r) => r.roleCode === user.roleCode)
      if (!role) {
        throw new Error(`Missing role definition for ${user.roleCode}`)
      }
      return {
        userRoleId: `UR-${String(index + 1).padStart(3, '0')}`,
        userId: user.userId,
        roleId: role.roleId,
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      }
    }),
  })

  const permissionByCode = new Map<string, string>(
    PERMISSION_SEED.map((p) => [p.permissionCode, p.permissionId]),
  )
  const roleByCode: Record<string, string> = Object.fromEntries(
    UFMS_ROLE_DEFINITIONS.map((role) => [role.roleCode, role.roleId]),
  )

  let rolePermissionIndex = 1
  const rolePermissionRows: {
    rolePermissionId: string
    roleId: string
    permissionId: string
    createdAt: Date
    updatedAt: Date
  }[] = []

  for (const [roleCode, codes] of Object.entries(ROLE_PERMISSION_CODES)) {
    for (const code of codes) {
      const permissionId = permissionByCode.get(code)
      if (!permissionId) {
        throw new Error(`Missing permission seed for ${code}`)
      }
      rolePermissionRows.push({
        rolePermissionId: `RP-${String(rolePermissionIndex).padStart(3, '0')}`,
        roleId: roleByCode[roleCode],
        permissionId,
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      })
      rolePermissionIndex += 1
    }
  }

  await prisma.rolePermission.createMany({ data: rolePermissionRows })

  // Development-only maintenance view password (never hard-code production credentials).
  // Rotate via UFMS_MAINTENANCE_VIEW_PASSWORD env or update MaintenanceAccessConfig in DB.
  if (process.env.NODE_ENV !== 'production') {
    const devMaintenancePassword =
      process.env.UFMS_MAINTENANCE_VIEW_PASSWORD?.trim() || 'dev-maintenance-change-me'
    await prisma.maintenanceAccessConfig.create({
      data: {
        maintenanceAccessConfigId: 'MAC-DEV',
        passwordHash: await hashPassword(devMaintenancePassword),
        enabled: true,
        changedBy: 'seed-dev',
        lastChangedAt: SEED_NOW,
        createdAt: SEED_NOW,
        updatedAt: SEED_NOW,
      },
    })
    console.log(
      'Maintenance access: development password seeded (set UFMS_MAINTENANCE_VIEW_PASSWORD to override; rotate via DB or env before production).',
    )
  }

  console.log(
    'Seed complete: registry (2 sites, 10 assets, 5 locations, 3 devices, 3 points) + commercial foundation (SLA, SOP, alarms, episode, problem, contractors, spare parts, inspection, RFQ, reports) + integration + operations + trust + decision + auth',
  )
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
