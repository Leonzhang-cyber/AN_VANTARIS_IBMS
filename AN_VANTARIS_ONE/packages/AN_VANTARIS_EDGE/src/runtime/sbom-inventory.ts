import { createHash } from 'node:crypto';
import { existsSync, lstatSync, readFileSync, realpathSync } from 'node:fs';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

import type {
  ComponentInventory,
  ConnectorDependencyInventory,
  LicenseInventory,
  NodeDependencyInventory,
  OsDependencyInventory,
  SbomAcceptanceResult,
  SecurityDependencyInventory,
  ValidationResult,
  VulnerabilityAssessment,
} from './sbom-inventory-types.js';

const READINESS_KEY = 'UFMS_EDGE_C4_03_SBOM_DEPENDENCY_INVENTORY_FOUNDATION_PASS';
const runtimeDir = dirname(fileURLToPath(import.meta.url));
const EDGE_ROOT = resolve(runtimeDir, '..', '..');
const SBOM_ROOT = resolve(EDGE_ROOT, 'deploy', 'offline-bundle', 'sbom');

function assertInsideEdge(pathValue: string): string {
  const resolved = resolve(pathValue);
  if (!resolved.startsWith(EDGE_ROOT + sep) && resolved !== EDGE_ROOT) {
    throw new Error(`path outside edge root: ${pathValue}`);
  }
  return resolved;
}

function parseJson<T>(pathValue: string): T {
  const safe = assertInsideEdge(pathValue);
  return JSON.parse(readFileSync(safe, 'utf8')) as T;
}

function collectErrors(row: ComponentInventory): string[] {
  const errors: string[] = [];
  if (row.schemaVersion !== '1.0') errors.push('schemaVersion must be 1.0');
  if (row.taskId !== 'UFMS-EDGE-C4-03') errors.push('taskId mismatch');
  if (row.classification !== 'SBOM_FOUNDATION_ONLY') errors.push('classification mismatch');
  if (row.productionSbom !== false) errors.push('productionSbom must be false');
  if (row.sbomStandard !== 'INTERNAL_FOUNDATION') errors.push('sbomStandard mismatch');
  if (row.networkLookupPerformed !== false) errors.push('networkLookupPerformed must be false');
  if (row.vulnerabilityScanPerformed !== false) errors.push('vulnerabilityScanPerformed must be false');
  if (row.licenseLegalReviewPerformed !== false) errors.push('licenseLegalReviewPerformed must be false');
  if (!Array.isArray(row.components)) errors.push('components must be array');
  if (row.componentCount !== row.components.length) errors.push('componentCount mismatch');
  if (row.readinessKey !== READINESS_KEY) errors.push('readinessKey mismatch');
  return errors;
}

export function loadComponentInventory(pathValue: string = resolve(SBOM_ROOT, 'COMPONENT_INVENTORY.edge.json')): ComponentInventory {
  return parseJson<ComponentInventory>(pathValue);
}

export function validateComponentInventory(inventory: unknown): ValidationResult {
  const row = inventory as ComponentInventory;
  const errors = collectErrors(row);
  if (Array.isArray(row.components)) {
    let previous = '';
    for (const comp of row.components) {
      if (comp.componentId < previous) errors.push('component ordering is not deterministic');
      previous = comp.componentId;
      if (comp.source.includes('..')) errors.push(`component source contains traversal: ${comp.componentId}`);
    }
  }
  const digest = calculateComponentAggregateDigest(Array.isArray(row.components) ? row.components : []);
  if ((row.aggregateDigest || '') !== digest) {
    errors.push('aggregateDigest mismatch');
  }
  return { ok: errors.length === 0, errors };
}

export function loadNodeDependencyInventory(
  pathValue: string = resolve(SBOM_ROOT, 'NODE_DEPENDENCY_INVENTORY.edge.json'),
): NodeDependencyInventory {
  return parseJson<NodeDependencyInventory>(pathValue);
}

export function loadOsDependencyInventory(
  pathValue: string = resolve(SBOM_ROOT, 'OS_DEPENDENCY_INVENTORY.edge.json'),
): OsDependencyInventory {
  return parseJson<OsDependencyInventory>(pathValue);
}

export function loadConnectorDependencyInventory(
  pathValue: string = resolve(SBOM_ROOT, 'CONNECTOR_DEPENDENCY_INVENTORY.edge.json'),
): ConnectorDependencyInventory {
  return parseJson<ConnectorDependencyInventory>(pathValue);
}

export function loadSecurityDependencyInventory(
  pathValue: string = resolve(SBOM_ROOT, 'SECURITY_DEPENDENCY_INVENTORY.edge.json'),
): SecurityDependencyInventory {
  return parseJson<SecurityDependencyInventory>(pathValue);
}

export function loadLicenseInventory(
  pathValue: string = resolve(SBOM_ROOT, 'LICENSE_INVENTORY.edge.json'),
): LicenseInventory {
  return parseJson<LicenseInventory>(pathValue);
}

export function loadVulnerabilityAssessment(
  pathValue: string = resolve(SBOM_ROOT, 'VULNERABILITY_ASSESSMENT.edge.json'),
): VulnerabilityAssessment {
  return parseJson<VulnerabilityAssessment>(pathValue);
}

export function calculateComponentAggregateDigest(
  components: readonly {
    componentId: string;
    version: string;
    type: string;
    provenanceStatus: string;
  }[],
): string {
  const payload = [...components]
    .sort((a, b) => (a.componentId < b.componentId ? -1 : a.componentId > b.componentId ? 1 : 0))
    .map((c) => `${c.componentId}:${c.version}:${c.type}:${c.provenanceStatus}`)
    .join('\n');
  return createHash('sha256').update(payload).digest('hex');
}

export function verifyComponentInventory(
  inventory: ComponentInventory,
  rootPath: string = EDGE_ROOT,
): ValidationResult {
  const errors: string[] = [];
  const root = assertInsideEdge(rootPath);
  for (const component of inventory.components) {
    if (!component.source.startsWith('AN_VANTARIS_EDGE/')) {
      continue;
    }
    if (component.source.startsWith('AN_VANTARIS_EDGE/.runtime/')) {
      errors.push(`component source contains runtime path: ${component.componentId}`);
      continue;
    }
    const abs = resolve(resolve(root, '..'), component.source);
    if (!existsSync(abs)) {
      errors.push(`component source missing: ${component.componentId}`);
      continue;
    }
    const stat = lstatSync(abs);
    if (stat.isSymbolicLink()) {
      const real = realpathSync(abs);
      assertInsideEdge(real);
    }
  }
  return { ok: errors.length === 0, errors };
}

export function evaluateSbomAcceptance(
  inventory: ComponentInventory,
  vulnerability: VulnerabilityAssessment,
  connectorInventory: ConnectorDependencyInventory,
  securityInventory: SecurityDependencyInventory,
): SbomAcceptanceResult {
  const v = validateComponentInventory(inventory);
  if (!v.ok) return 'SBOM_FOUNDATION_REJECTED';
  if (vulnerability.assessmentStatus !== 'NOT_SCANNED') return 'SBOM_FOUNDATION_REJECTED';
  if (
    vulnerability.networkScanPerformed ||
    vulnerability.registryAuditPerformed ||
    vulnerability.nvdLookupPerformed ||
    vulnerability.osvLookupPerformed ||
    vulnerability.npmAuditPerformed
  ) {
    return 'SBOM_FOUNDATION_REJECTED';
  }
  if (connectorInventory.connectors.length !== 6) return 'SBOM_FOUNDATION_REJECTED';
  if (
    connectorInventory.connectors.some(
      (c) =>
        c.syntheticFixtureOnly !== true ||
        c.realConnectivityEnabled !== false ||
        c.productionDependencyIncluded !== false ||
        c.currentMaturity !== 'FOUNDATION_READY' ||
        c.enablementGate !== 'C5-00',
    )
  ) {
    return 'SBOM_FOUNDATION_REJECTED';
  }
  if (securityInventory.dependencies.some((d) => d.installedByC4_03 || d.configured || d.productionEnabled)) {
    return 'SBOM_FOUNDATION_REJECTED';
  }
  return 'SBOM_FOUNDATION_ACCEPTED_NOT_PRODUCTION';
}
