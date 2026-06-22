import { readFileSync } from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

import type {
  ConnectorEnablementAcceptanceResult,
  ConnectorEnablementDecision,
  ConnectorEnablementEvaluationResult,
  ConnectorEnablementMatrix,
  ConnectorEnablementRecord,
  ConnectorGateStatus,
  ConnectorRegistryKey,
  ConnectorRiskClassification,
  ProtocolReadinessRequirements,
  ValidationResult,
} from './connector-enablement-types.js';

const runtimeDir = dirname(fileURLToPath(import.meta.url));
const EDGE_ROOT = resolve(runtimeDir, '..', '..');
const ENABLEMENT_ROOT = resolve(EDGE_ROOT, 'deploy', 'offline-bundle', 'connector-enablement');
const READINESS_KEY = 'UFMS_EDGE_C5_00_PRODUCTION_CONNECTOR_ENABLEMENT_GATE_PASS';
const REQUIRED_KEYS: readonly ConnectorRegistryKey[] = ['file', 'http', 'snmp', 'modbus', 'bacnet', 'opcua'];

function assertInsideEdge(pathValue: string): string {
  const p = resolve(pathValue);
  if (!p.startsWith(EDGE_ROOT + sep) && p !== EDGE_ROOT) {
    throw new Error(`path outside EDGE root: ${pathValue}`);
  }
  return p;
}

function loadJson<T>(pathValue: string): T {
  return JSON.parse(readFileSync(assertInsideEdge(pathValue), 'utf8')) as T;
}

function allowedGateStatus(value: string): value is ConnectorGateStatus {
  return ['PASS', 'FAIL', 'NOT_EVALUATED', 'NOT_APPLICABLE', 'DEFERRED', 'REQUIRES_APPROVAL'].includes(value);
}

function allowedDecision(value: string): value is ConnectorEnablementDecision {
  return [
    'BLOCKED_NOT_PRODUCTION_READY',
    'ELIGIBLE_FOR_CONTROLLED_READ_ONLY_PILOT',
    'APPROVED_FOR_PRODUCTION_READ_ONLY',
    'REJECTED',
    'REVOKED',
  ].includes(value);
}

export function loadConnectorEnablementMatrix(
  pathValue: string = resolve(ENABLEMENT_ROOT, 'CONNECTOR_ENABLEMENT_MATRIX.edge.json'),
): ConnectorEnablementMatrix {
  return loadJson<ConnectorEnablementMatrix>(pathValue);
}

export function loadConnectorRiskClassification(
  pathValue: string = resolve(ENABLEMENT_ROOT, 'CONNECTOR_RISK_CLASSIFICATION.edge.json'),
): ConnectorRiskClassification {
  return loadJson<ConnectorRiskClassification>(pathValue);
}

export function loadProtocolReadinessRequirements(
  pathValue: string = resolve(ENABLEMENT_ROOT, 'PROTOCOL_READINESS_REQUIREMENTS.edge.json'),
): ProtocolReadinessRequirements {
  return loadJson<ProtocolReadinessRequirements>(pathValue);
}

export function validateConnectorEnablementMatrix(matrix: unknown): ValidationResult {
  const row = matrix as ConnectorEnablementMatrix;
  const errors: string[] = [];
  if (row.schemaVersion !== '1.0') errors.push('schemaVersion mismatch');
  if (row.taskId !== 'UFMS-EDGE-C5-00') errors.push('taskId mismatch');
  if (row.classification !== 'CONNECTOR_ENABLEMENT_FOUNDATION_ONLY') errors.push('classification mismatch');
  if (row.readinessKey !== READINESS_KEY) errors.push('readinessKey mismatch');
  const keys = new Set(row.connectors?.map((x) => x.registryKey));
  for (const key of REQUIRED_KEYS) {
    if (!keys.has(key)) errors.push(`missing connector: ${key}`);
  }
  if ((row.connectors?.length || 0) !== REQUIRED_KEYS.length) {
    errors.push('connector count mismatch');
  }
  for (const connector of row.connectors || []) {
    if (connector.currentMaturity !== 'FOUNDATION_READY') errors.push(`${connector.registryKey}: maturity mismatch`);
    if (connector.requestedMode !== 'FOUNDATION_ONLY') errors.push(`${connector.registryKey}: requestedMode mismatch`);
    if (connector.permittedMode !== 'SYNTHETIC_ONLY') errors.push(`${connector.registryKey}: permittedMode mismatch`);
    if (!connector.syntheticFixtureOnly) errors.push(`${connector.registryKey}: syntheticFixtureOnly must be true`);
    if (connector.realConnectivityEnabled) errors.push(`${connector.registryKey}: realConnectivityEnabled must be false`);
    if (connector.productionDependencyIncluded) errors.push(`${connector.registryKey}: productionDependencyIncluded must be false`);
    if (connector.supportsWriteback) errors.push(`${connector.registryKey}: supportsWriteback must be false`);
    if (!allowedDecision(connector.decision)) errors.push(`${connector.registryKey}: invalid decision`);
    if (connector.decision !== 'BLOCKED_NOT_PRODUCTION_READY') {
      errors.push(`${connector.registryKey}: unexpected non-blocked decision`);
    }
    const gates: readonly ConnectorGateStatus[] = [
      connector.dependencyGate,
      connector.securityGate,
      connector.configurationGate,
      connector.protocolGate,
      connector.networkAuthorizationGate,
      connector.readOnlyEnforcementGate,
      connector.credentialProvisioningGate,
      connector.evidenceGate,
      connector.rollbackGate,
      connector.operatorApprovalGate,
    ];
    if (!gates.every((g) => allowedGateStatus(g))) {
      errors.push(`${connector.registryKey}: invalid gate status detected`);
    }
    if (!Array.isArray(connector.rejectionReasons) || connector.rejectionReasons.length === 0) {
      errors.push(`${connector.registryKey}: rejectionReasons must be non-empty`);
    }
    if (!connector.rejectionReasons.includes('READ_ONLY_ENFORCEMENT_NOT_PRODUCTION_VERIFIED')) {
      errors.push(`${connector.registryKey}: read-only rejection reason missing`);
    }
  }
  return { ok: errors.length === 0, errors };
}

export function evaluateConnectorGate(
  record: ConnectorEnablementRecord,
): ConnectorEnablementDecision {
  if (record.supportsWriteback || record.realConnectivityEnabled || record.productionDependencyIncluded) {
    return 'REJECTED';
  }
  if (record.readOnlyEnforcementGate !== 'PASS') {
    return 'BLOCKED_NOT_PRODUCTION_READY';
  }
  if (
    record.dependencyGate === 'PASS' &&
    record.securityGate === 'PASS' &&
    record.configurationGate === 'PASS' &&
    record.protocolGate === 'PASS' &&
    record.networkAuthorizationGate === 'PASS' &&
    record.credentialProvisioningGate === 'PASS' &&
    record.evidenceGate === 'PASS' &&
    record.rollbackGate === 'PASS' &&
    record.operatorApprovalGate === 'PASS'
  ) {
    return 'APPROVED_FOR_PRODUCTION_READ_ONLY';
  }
  return 'BLOCKED_NOT_PRODUCTION_READY';
}

export function listConnectorRejectionReasons(record: ConnectorEnablementRecord): readonly string[] {
  return record.rejectionReasons;
}

export function isConnectorProductionEligible(record: ConnectorEnablementRecord): boolean {
  if (record.supportsWriteback) return false;
  if (record.readOnlyEnforcementGate !== 'PASS') return false;
  return evaluateConnectorGate(record) === 'APPROVED_FOR_PRODUCTION_READ_ONLY';
}

export function isConnectorReadOnlyPilotEligible(record: ConnectorEnablementRecord): boolean {
  if (record.supportsWriteback) return false;
  if (record.readOnlyEnforcementGate !== 'PASS') return false;
  return evaluateConnectorGate(record) === 'ELIGIBLE_FOR_CONTROLLED_READ_ONLY_PILOT';
}

export function evaluateConnectorEnablement(
  matrix: ConnectorEnablementMatrix,
): readonly ConnectorEnablementEvaluationResult[] {
  return matrix.connectors.map((record) => ({
    connector: record.registryKey,
    productionEligible: isConnectorProductionEligible(record),
    readOnlyPilotEligible: isConnectorReadOnlyPilotEligible(record),
    decision: evaluateConnectorGate(record),
    rejectionReasons: listConnectorRejectionReasons(record),
  }));
}

export function evaluateConnectorEnablementAcceptance(
  matrix: ConnectorEnablementMatrix,
): ConnectorEnablementAcceptanceResult {
  const validation = validateConnectorEnablementMatrix(matrix);
  if (!validation.ok) return 'CONNECTOR_ENABLEMENT_GATE_FOUNDATION_REJECTED';
  const allBlocked = matrix.connectors.every((record) => evaluateConnectorGate(record) === 'BLOCKED_NOT_PRODUCTION_READY');
  if (!allBlocked) return 'CONNECTOR_ENABLEMENT_GATE_FOUNDATION_REJECTED';
  return 'CONNECTOR_ENABLEMENT_GATE_FOUNDATION_ACCEPTED';
}
