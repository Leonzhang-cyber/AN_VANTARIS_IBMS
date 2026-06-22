import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import type {
  EdgeAuditFindingsSnapshotA0,
  EdgeConnectorAuditEntry,
  EdgeNextDevelopmentTaskA0,
  EdgeProductionBlockerA0,
} from './edge-audit-findings-types.js';

const AUDIT_FILE_PATH = resolve('./AN_VANTARIS_EDGE/config/edge-audit-findings-a0.json');
const REQUIRED_READINESS_KEY = 'UFMS_EDGE_C4_00A_AUDIT_FINDINGS_FREEZE_PASS';
const REQUIRED_CLASSIFICATION = 'AUDIT_SNAPSHOT';
const REQUIRED_CONNECTORS: ReadonlyArray<EdgeConnectorAuditEntry['registryKey']> = [
  'file',
  'http',
  'snmp',
  'modbus',
  'bacnet',
  'opcua',
];

function asRecord(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null ? (value as Record<string, unknown>) : {};
}

function asString(value: unknown): string {
  return typeof value === 'string' ? value : '';
}

function asBoolean(value: unknown): boolean {
  return value === true;
}

function asNumber(value: unknown): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : Number.NaN;
}

function validatePercent(name: string, value: unknown, errors: string[]): void {
  const numeric = asNumber(value);
  if (!Number.isFinite(numeric) || numeric < 0 || numeric > 100) {
    errors.push(`${name} must be a finite number in range 0..100`);
  }
}

function validateConnectorEntry(entry: unknown, index: number, errors: string[]): void {
  const row = asRecord(entry);
  const registryKey = asString(row.registryKey);
  if (!REQUIRED_CONNECTORS.includes(registryKey as EdgeConnectorAuditEntry['registryKey'])) {
    errors.push(`connectors[${index}].registryKey is invalid`);
  }
  if (asString(row.foundationStatus) !== 'foundation-ready') {
    errors.push(`connectors[${index}].foundationStatus must be foundation-ready`);
  }
  if (row.syntheticFixtureOnly !== true) {
    errors.push(`connectors[${index}].syntheticFixtureOnly must be true`);
  }
  if (row.realConnectivityEnabled !== false) {
    errors.push(`connectors[${index}].realConnectivityEnabled must be false`);
  }
  if (row.supportsWriteback !== false) {
    errors.push(`connectors[${index}].supportsWriteback must be false`);
  }
  if (row.productionDependencyIncluded !== false) {
    errors.push(`connectors[${index}].productionDependencyIncluded must be false`);
  }
}

function parseAuditJson(): unknown {
  const raw = readFileSync(AUDIT_FILE_PATH, 'utf8');
  return JSON.parse(raw);
}

export function validateEdgeAuditFindingsA0(
  snapshot: unknown,
): snapshot is EdgeAuditFindingsSnapshotA0 {
  const row = asRecord(snapshot);
  const errors: string[] = [];

  if (asString(row.auditId) !== 'UFMS-EDGE-CURRENT-CAPABILITY-AUDIT-A0') {
    errors.push('auditId mismatch');
  }
  if (asString(row.freezeTaskId) !== 'UFMS-EDGE-C4-00A') {
    errors.push('freezeTaskId mismatch');
  }
  if (asString(row.repository) !== '/Volumes/Work/VANTARIS_UFMS_FULL') {
    errors.push('repository mismatch');
  }
  if (asString(row.branch) !== 'main') {
    errors.push('branch must be main');
  }
  if (asString(row.baselineCommit) !== '3c70692') {
    errors.push('baselineCommit must be 3c70692');
  }
  if (asString(row.classification) !== REQUIRED_CLASSIFICATION) {
    errors.push('classification must be AUDIT_SNAPSHOT');
  }
  if (asBoolean(row.productionCertification)) {
    errors.push('productionCertification must be false');
  }
  if (asString(row.readinessKey) !== REQUIRED_READINESS_KEY) {
    errors.push('readinessKey mismatch');
  }

  validatePercent('foundationCompletenessPercent', row.foundationCompletenessPercent, errors);
  validatePercent('productionRuntimeReadinessPercent', row.productionRuntimeReadinessPercent, errors);
  validatePercent('connectorProductionReadinessPercent', row.connectorProductionReadinessPercent, errors);
  validatePercent('offlineDeploymentReadinessPercent', row.offlineDeploymentReadinessPercent, errors);
  validatePercent('securityReadinessPercent', row.securityReadinessPercent, errors);
  validatePercent('validationConfidencePercent', row.validationConfidencePercent, errors);
  validatePercent('overallConfidencePercent', row.overallConfidencePercent, errors);

  const connectors = Array.isArray(row.connectors) ? row.connectors : [];
  if (connectors.length !== 6) {
    errors.push('connectors must include exactly six entries');
  }
  connectors.forEach((entry, index) => validateConnectorEntry(entry, index, errors));
  const connectorKeys = new Set(connectors.map((entry) => asString(asRecord(entry).registryKey)));
  REQUIRED_CONNECTORS.forEach((key) => {
    if (!connectorKeys.has(key)) {
      errors.push(`missing connector registry key: ${key}`);
    }
  });

  const blockers = Array.isArray(row.productionBlockers) ? row.productionBlockers : [];
  if (blockers.length < 10) {
    errors.push('productionBlockers must include at least 10 entries');
  }
  blockers.forEach((entry, index) => {
    const item = asRecord(entry);
    if (!asString(item.id)) errors.push(`productionBlockers[${index}].id is required`);
    if (!asString(item.title)) errors.push(`productionBlockers[${index}].title is required`);
    if (!asString(item.description)) errors.push(`productionBlockers[${index}].description is required`);
    if (!asString(item.risk)) errors.push(`productionBlockers[${index}].risk is required`);
  });

  const nextSequence = Array.isArray(row.nextDevelopmentSequence) ? row.nextDevelopmentSequence : [];
  if (nextSequence.length !== 10) {
    errors.push('nextDevelopmentSequence must include exactly 10 entries');
  }
  nextSequence.forEach((entry, index) => {
    const item = asRecord(entry);
    if (!Number.isFinite(asNumber(item.order))) errors.push(`nextDevelopmentSequence[${index}].order is required`);
    if (!asString(item.code)) errors.push(`nextDevelopmentSequence[${index}].code is required`);
    if (!asString(item.title)) errors.push(`nextDevelopmentSequence[${index}].title is required`);
  });

  if (errors.length > 0) {
    throw new Error(`edge audit findings A0 validation failed: ${errors.join('; ')}`);
  }
  return true;
}

export function loadEdgeAuditFindingsA0(): EdgeAuditFindingsSnapshotA0 {
  const parsed = parseAuditJson();
  validateEdgeAuditFindingsA0(parsed);
  return parsed as EdgeAuditFindingsSnapshotA0;
}

export function getEdgeProductionBlockersA0(): readonly EdgeProductionBlockerA0[] {
  return loadEdgeAuditFindingsA0().productionBlockers;
}

export function getEdgeNextDevelopmentSequenceA0(): readonly EdgeNextDevelopmentTaskA0[] {
  return loadEdgeAuditFindingsA0().nextDevelopmentSequence;
}
