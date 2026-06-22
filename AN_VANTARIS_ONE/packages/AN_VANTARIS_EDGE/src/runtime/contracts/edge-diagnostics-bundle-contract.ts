/**
 * EDGE-C8-12 — EDGE diagnostics bundle contract.
 *
 * EDGE-owned diagnostics bundle model for local field support, health snapshot,
 * heartbeat, outbox, adapter/connector summaries, resource status, policy state,
 * and evidence references.
 *
 * This contract does not enable runtime, pilot, production, writeback, or direct
 * UFMS DB access.
 */

import type {
  EdgeHealthSnapshotContract,
  EdgeHealthOverallStatus,
} from './edge-health-snapshot-contract.js';

export type EdgeDiagnosticsBundleStatus =
  | 'READY'
  | 'DEGRADED'
  | 'INCOMPLETE'
  | 'BLOCKED'
  | 'UNKNOWN';

export type EdgeDiagnosticsBundleItemType =
  | 'health_snapshot'
  | 'heartbeat'
  | 'outbox_summary'
  | 'adapter_summary'
  | 'connector_summary'
  | 'resource_summary'
  | 'security_summary'
  | 'policy_summary'
  | 'evidence_manifest'
  | 'log_reference'
  | 'config_reference'
  | 'package_integrity'
  | 'unknown';

export type EdgeDiagnosticsExportScope =
  | 'LOCAL_ONLY'
  | 'LINK_HANDOFF'
  | 'FIELD_ENGINEER'
  | 'SUPPORT_BUNDLE';

export interface EdgeDiagnosticsEvidenceRef {
  readonly evidenceId: string;
  readonly evidenceType:
    | 'health'
    | 'heartbeat'
    | 'outbox'
    | 'adapter'
    | 'connector'
    | 'resource'
    | 'security'
    | 'policy'
    | 'package'
    | 'log'
    | 'config'
    | 'unknown';
  readonly sourcePath?: string;
  readonly hash?: string;
}

export interface EdgeDiagnosticsBundleItem {
  readonly itemId: string;
  readonly itemType: EdgeDiagnosticsBundleItemType;
  readonly status: EdgeDiagnosticsBundleStatus;
  readonly generatedAt: string;
  readonly summary: string;
  readonly evidenceRefs: readonly EdgeDiagnosticsEvidenceRef[];
  readonly containsSecretMaterial: false;
}

export interface EdgeDiagnosticsBundleManifest {
  readonly manifestId: string;
  readonly bundleId: string;
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly generatedAt: string;
  readonly itemCount: number;
  readonly itemIds: readonly string[];
  readonly bundleHash: string;
  readonly containsSecretMaterial: false;
  readonly runtimeEnabled: false;
  readonly productionDeliveryAllowed: false;
  readonly writebackAllowed: false;
  readonly directDbAccessAllowed: false;
}

export interface EdgeDiagnosticsBundleContract {
  readonly bundleId: string;
  readonly gatewayId: string;
  readonly edgeId?: string;
  readonly tenantId?: string;
  readonly siteId?: string;
  readonly generatedAt: string;
  readonly status: EdgeDiagnosticsBundleStatus;
  readonly exportScope: EdgeDiagnosticsExportScope;
  readonly healthStatus: EdgeHealthOverallStatus;
  readonly healthSnapshot: EdgeHealthSnapshotContract;
  readonly items: readonly EdgeDiagnosticsBundleItem[];
  readonly manifest: EdgeDiagnosticsBundleManifest;
  readonly warnings: readonly string[];
  readonly evidenceRefs: readonly EdgeDiagnosticsEvidenceRef[];
  readonly containsSecretMaterial: false;
  readonly runtimeEnabled: false;
  readonly productionDeliveryAllowed: false;
  readonly writebackAllowed: false;
  readonly directDbAccessAllowed: false;
}

export function createEdgeDiagnosticsBundleId(input: {
  readonly gatewayId: string;
  readonly generatedAt: string;
}): string {
  return `edge-diagnostics-${input.gatewayId}-${input.generatedAt}`;
}

export function createEdgeDiagnosticsItemId(input: {
  readonly bundleId: string;
  readonly itemType: EdgeDiagnosticsBundleItemType;
}): string {
  return `${input.bundleId}-${input.itemType}`;
}

export function createDiagnosticsBundleHash(input: {
  readonly bundleId: string;
  readonly itemIds: readonly string[];
  readonly generatedAt: string;
}): string {
  let hash = 2166136261;
  const value = [input.bundleId, input.generatedAt, ...input.itemIds].join('|');

  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }

  return `fnv1a32:${(hash >>> 0).toString(16).padStart(8, '0')}`;
}

export function deriveDiagnosticsBundleStatus(
  healthStatus: EdgeHealthOverallStatus,
): EdgeDiagnosticsBundleStatus {
  switch (healthStatus) {
    case 'HEALTHY':
      return 'READY';
    case 'DEGRADED':
      return 'DEGRADED';
    case 'UNHEALTHY':
      return 'DEGRADED';
    case 'LOCKED':
      return 'BLOCKED';
    case 'MAINTENANCE':
      return 'DEGRADED';
    case 'UNKNOWN':
      return 'UNKNOWN';
  }
}

export function createDiagnosticsBundleItem(input: {
  readonly bundleId: string;
  readonly itemType: EdgeDiagnosticsBundleItemType;
  readonly status: EdgeDiagnosticsBundleStatus;
  readonly generatedAt: string;
  readonly summary: string;
  readonly evidenceRefs?: readonly EdgeDiagnosticsEvidenceRef[];
}): EdgeDiagnosticsBundleItem {
  return {
    itemId: createEdgeDiagnosticsItemId({
      bundleId: input.bundleId,
      itemType: input.itemType,
    }),
    itemType: input.itemType,
    status: input.status,
    generatedAt: input.generatedAt,
    summary: input.summary,
    evidenceRefs: input.evidenceRefs ?? [],
    containsSecretMaterial: false,
  };
}

export function createDiagnosticsBundleFromHealthSnapshot(input: {
  readonly healthSnapshot: EdgeHealthSnapshotContract;
  readonly generatedAt?: string;
  readonly exportScope?: EdgeDiagnosticsExportScope;
  readonly evidenceRefs?: readonly EdgeDiagnosticsEvidenceRef[];
  readonly warnings?: readonly string[];
}): EdgeDiagnosticsBundleContract {
  const generatedAt = input.generatedAt ?? input.healthSnapshot.generatedAt;
  const bundleId = createEdgeDiagnosticsBundleId({
    gatewayId: input.healthSnapshot.gatewayId,
    generatedAt,
  });

  const status = deriveDiagnosticsBundleStatus(input.healthSnapshot.overallStatus);

  const items: EdgeDiagnosticsBundleItem[] = [
    createDiagnosticsBundleItem({
      bundleId,
      itemType: 'health_snapshot',
      status,
      generatedAt,
      summary: `overallStatus=${input.healthSnapshot.overallStatus}`,
    }),
    createDiagnosticsBundleItem({
      bundleId,
      itemType: 'heartbeat',
      status,
      generatedAt,
      summary: `liveness=${input.healthSnapshot.heartbeat.livenessStatus};link=${input.healthSnapshot.heartbeat.linkConnectivityStatus}`,
    }),
    createDiagnosticsBundleItem({
      bundleId,
      itemType: 'outbox_summary',
      status,
      generatedAt,
      summary: `depth=${input.healthSnapshot.outbox.depth};retryPending=${input.healthSnapshot.outbox.retryPendingCount};localDlq=${input.healthSnapshot.outbox.localDlqCount}`,
    }),
    createDiagnosticsBundleItem({
      bundleId,
      itemType: 'security_summary',
      status,
      generatedAt,
      summary: `lockedMode=${input.healthSnapshot.security.lockedMode};secretMaterialStored=${input.healthSnapshot.security.secretMaterialStored}`,
    }),
    createDiagnosticsBundleItem({
      bundleId,
      itemType: 'policy_summary',
      status,
      generatedAt,
      summary: `runtimeEnabled=${input.healthSnapshot.policy.runtimeEnabled};productionApproved=${input.healthSnapshot.policy.productionApproved};writebackProhibited=${input.healthSnapshot.policy.writebackProhibited}`,
    }),
    createDiagnosticsBundleItem({
      bundleId,
      itemType: 'resource_summary',
      status,
      generatedAt,
      summary: `cpuLoad=${input.healthSnapshot.resources.cpuLoadPercent ?? 'unknown'};diskFree=${input.healthSnapshot.resources.diskFreeBytes ?? 'unknown'}`,
    }),
  ];

  const itemIds = items.map((item) => item.itemId);
  const bundleHash = createDiagnosticsBundleHash({
    bundleId,
    itemIds,
    generatedAt,
  });

  const manifest: EdgeDiagnosticsBundleManifest = {
    manifestId: `${bundleId}-manifest`,
    bundleId,
    gatewayId: input.healthSnapshot.gatewayId,
    ...(input.healthSnapshot.edgeId !== undefined ? { edgeId: input.healthSnapshot.edgeId } : {}),
    generatedAt,
    itemCount: items.length,
    itemIds,
    bundleHash,
    containsSecretMaterial: false,
    runtimeEnabled: false,
    productionDeliveryAllowed: false,
    writebackAllowed: false,
    directDbAccessAllowed: false,
  };

  return {
    bundleId,
    gatewayId: input.healthSnapshot.gatewayId,
    ...(input.healthSnapshot.edgeId !== undefined ? { edgeId: input.healthSnapshot.edgeId } : {}),
    ...(input.healthSnapshot.tenantId !== undefined ? { tenantId: input.healthSnapshot.tenantId } : {}),
    ...(input.healthSnapshot.siteId !== undefined ? { siteId: input.healthSnapshot.siteId } : {}),
    generatedAt,
    status,
    exportScope: input.exportScope ?? 'LOCAL_ONLY',
    healthStatus: input.healthSnapshot.overallStatus,
    healthSnapshot: input.healthSnapshot,
    items,
    manifest,
    warnings: input.warnings ?? [],
    evidenceRefs: input.evidenceRefs ?? [],
    containsSecretMaterial: false,
    runtimeEnabled: false,
    productionDeliveryAllowed: false,
    writebackAllowed: false,
    directDbAccessAllowed: false,
  };
}

export function validateEdgeDiagnosticsBundleContract(
  bundle: EdgeDiagnosticsBundleContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!bundle.bundleId.trim()) reasons.push('bundleId is required');
  if (!bundle.gatewayId.trim()) reasons.push('gatewayId is required');
  if (!bundle.generatedAt.trim()) reasons.push('generatedAt is required');
  if (!bundle.manifest.manifestId.trim()) reasons.push('manifest.manifestId is required');
  if (bundle.manifest.bundleId !== bundle.bundleId) {
    reasons.push('manifest.bundleId must match bundleId');
  }

  if (bundle.manifest.itemCount !== bundle.items.length) {
    reasons.push('manifest.itemCount must match items length');
  }

  const itemIds = bundle.items.map((item) => item.itemId);
  if (bundle.manifest.itemIds.join('|') !== itemIds.join('|')) {
    reasons.push('manifest.itemIds must match bundle items');
  }

  if (!bundle.manifest.bundleHash.trim()) {
    reasons.push('manifest.bundleHash is required');
  }

  for (const item of bundle.items) {
    if (!item.itemId.trim()) reasons.push('itemId is required');
    if (!item.generatedAt.trim()) reasons.push('item.generatedAt is required');
    if (item.containsSecretMaterial !== false) {
      reasons.push('item.containsSecretMaterial must remain false');
    }
  }

  if (bundle.containsSecretMaterial !== false) {
    reasons.push('containsSecretMaterial must remain false');
  }

  if (bundle.manifest.containsSecretMaterial !== false) {
    reasons.push('manifest.containsSecretMaterial must remain false');
  }

  if (bundle.runtimeEnabled !== false) reasons.push('runtimeEnabled must remain false');
  if (bundle.productionDeliveryAllowed !== false) {
    reasons.push('productionDeliveryAllowed must remain false');
  }
  if (bundle.writebackAllowed !== false) reasons.push('writebackAllowed must remain false');
  if (bundle.directDbAccessAllowed !== false) {
    reasons.push('directDbAccessAllowed must remain false');
  }

  if (bundle.manifest.runtimeEnabled !== false) reasons.push('manifest.runtimeEnabled must remain false');
  if (bundle.manifest.productionDeliveryAllowed !== false) {
    reasons.push('manifest.productionDeliveryAllowed must remain false');
  }
  if (bundle.manifest.writebackAllowed !== false) reasons.push('manifest.writebackAllowed must remain false');
  if (bundle.manifest.directDbAccessAllowed !== false) {
    reasons.push('manifest.directDbAccessAllowed must remain false');
  }

  return reasons;
}
