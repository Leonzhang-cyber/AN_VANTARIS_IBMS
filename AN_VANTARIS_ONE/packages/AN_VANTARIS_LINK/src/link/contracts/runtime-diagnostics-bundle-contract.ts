/**
 * LINK-C7-02 — Runtime diagnostics bundle contract.
 *
 * LINK-owned diagnostics bundle model for local field support, health snapshot,
 * queue / DLQ / delivery / retry / replay / gateway liveness / evidence summary.
 *
 * This contract does not enable production delivery.
 */

import type {
  LinkRuntimeHealthSnapshotContract,
  LinkRuntimeHealthStatus,
} from './runtime-health-snapshot-contract.js';

export type LinkDiagnosticsBundleStatus =
  | 'READY'
  | 'DEGRADED'
  | 'INCOMPLETE'
  | 'BLOCKED'
  | 'UNKNOWN';

export type LinkDiagnosticsBundleItemType =
  | 'health_snapshot'
  | 'ingress_summary'
  | 'queue_summary'
  | 'dlq_summary'
  | 'delivery_summary'
  | 'retry_replay_summary'
  | 'gateway_liveness_summary'
  | 'evidence_summary'
  | 'config_reference'
  | 'log_reference'
  | 'unknown';

export type LinkDiagnosticsExportScope =
  | 'LOCAL_ONLY'
  | 'FIELD_ENGINEER'
  | 'SUPPORT_BUNDLE'
  | 'EDGE_LINK_HANDOFF';

export interface LinkDiagnosticsEvidenceRef {
  readonly evidenceId: string;
  readonly evidenceType:
    | 'health'
    | 'ingress'
    | 'queue'
    | 'dlq'
    | 'delivery'
    | 'retry'
    | 'replay'
    | 'gateway_liveness'
    | 'evidence_chain'
    | 'config'
    | 'log'
    | 'unknown';
  readonly sourcePath?: string;
  readonly hash?: string;
}

export interface LinkDiagnosticsBundleItem {
  readonly itemId: string;
  readonly itemType: LinkDiagnosticsBundleItemType;
  readonly status: LinkDiagnosticsBundleStatus;
  readonly generatedAt: string;
  readonly summary: string;
  readonly evidenceRefs: readonly LinkDiagnosticsEvidenceRef[];
  readonly containsSecretMaterial: false;
}

export interface LinkDiagnosticsBundleManifest {
  readonly manifestId: string;
  readonly bundleId: string;
  readonly linkNodeId: string;
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

export interface LinkRuntimeDiagnosticsBundleContract {
  readonly bundleId: string;
  readonly linkNodeId: string;
  readonly generatedAt: string;
  readonly status: LinkDiagnosticsBundleStatus;
  readonly exportScope: LinkDiagnosticsExportScope;
  readonly healthStatus: LinkRuntimeHealthStatus;
  readonly healthSnapshot: LinkRuntimeHealthSnapshotContract;
  readonly items: readonly LinkDiagnosticsBundleItem[];
  readonly manifest: LinkDiagnosticsBundleManifest;
  readonly warnings: readonly string[];
  readonly evidenceRefs: readonly LinkDiagnosticsEvidenceRef[];
  readonly containsSecretMaterial: false;
  readonly runtimeEnabled: false;
  readonly productionDeliveryAllowed: false;
  readonly writebackAllowed: false;
  readonly directDbAccessAllowed: false;
}

export function createLinkDiagnosticsBundleId(input: {
  readonly linkNodeId: string;
  readonly generatedAt: string;
}): string {
  return `link-diagnostics-${input.linkNodeId}-${input.generatedAt}`;
}

export function createLinkDiagnosticsItemId(input: {
  readonly bundleId: string;
  readonly itemType: LinkDiagnosticsBundleItemType;
}): string {
  return `${input.bundleId}-${input.itemType}`;
}

export function createLinkDiagnosticsBundleHash(input: {
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

export function deriveLinkDiagnosticsBundleStatus(
  healthStatus: LinkRuntimeHealthStatus,
): LinkDiagnosticsBundleStatus {
  switch (healthStatus) {
    case 'HEALTHY':
      return 'READY';
    case 'DEGRADED':
      return 'DEGRADED';
    case 'UNHEALTHY':
      return 'DEGRADED';
    case 'BLOCKED':
      return 'BLOCKED';
    case 'UNKNOWN':
      return 'UNKNOWN';
  }
}

export function createLinkDiagnosticsBundleItem(input: {
  readonly bundleId: string;
  readonly itemType: LinkDiagnosticsBundleItemType;
  readonly status: LinkDiagnosticsBundleStatus;
  readonly generatedAt: string;
  readonly summary: string;
  readonly evidenceRefs?: readonly LinkDiagnosticsEvidenceRef[];
}): LinkDiagnosticsBundleItem {
  return {
    itemId: createLinkDiagnosticsItemId({
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

export function createLinkDiagnosticsBundleFromHealthSnapshot(input: {
  readonly healthSnapshot: LinkRuntimeHealthSnapshotContract;
  readonly generatedAt?: string;
  readonly exportScope?: LinkDiagnosticsExportScope;
  readonly evidenceRefs?: readonly LinkDiagnosticsEvidenceRef[];
  readonly warnings?: readonly string[];
}): LinkRuntimeDiagnosticsBundleContract {
  const generatedAt = input.generatedAt ?? input.healthSnapshot.generatedAt;
  const bundleId = createLinkDiagnosticsBundleId({
    linkNodeId: input.healthSnapshot.linkNodeId,
    generatedAt,
  });
  const status = deriveLinkDiagnosticsBundleStatus(input.healthSnapshot.healthStatus);

  const items: LinkDiagnosticsBundleItem[] = [
    createLinkDiagnosticsBundleItem({
      bundleId,
      itemType: 'health_snapshot',
      status,
      generatedAt,
      summary: `health=${input.healthSnapshot.healthStatus};ready=${input.healthSnapshot.readyStatus}`,
    }),
    createLinkDiagnosticsBundleItem({
      bundleId,
      itemType: 'ingress_summary',
      status,
      generatedAt,
      summary: `accepted=${input.healthSnapshot.ingress.acceptedCount};rejected=${input.healthSnapshot.ingress.rejectedCount};blocked=${input.healthSnapshot.ingress.blockedCount}`,
    }),
    createLinkDiagnosticsBundleItem({
      bundleId,
      itemType: 'queue_summary',
      status,
      generatedAt,
      summary: `depth=${input.healthSnapshot.queue.queueDepth};oldestAgeMs=${input.healthSnapshot.queue.oldestQueueAgeMs};partitions=${input.healthSnapshot.queue.partitionCount}`,
    }),
    createLinkDiagnosticsBundleItem({
      bundleId,
      itemType: 'dlq_summary',
      status,
      generatedAt,
      summary: `dlq=${input.healthSnapshot.dlq.dlqCount};replayEligible=${input.healthSnapshot.dlq.replayEligibleCount};operatorAction=${input.healthSnapshot.dlq.operatorActionRequiredCount}`,
    }),
    createLinkDiagnosticsBundleItem({
      bundleId,
      itemType: 'delivery_summary',
      status,
      generatedAt,
      summary: `dryRunAccepted=${input.healthSnapshot.delivery.dryRunAcceptedCount};blocked=${input.healthSnapshot.delivery.blockedCount};production=${input.healthSnapshot.delivery.productionDeliveryAllowed}`,
    }),
    createLinkDiagnosticsBundleItem({
      bundleId,
      itemType: 'retry_replay_summary',
      status,
      generatedAt,
      summary: `retryPending=${input.healthSnapshot.retryReplay.retryPendingCount};replayRequested=${input.healthSnapshot.retryReplay.replayRequestedCount};stormProtected=${input.healthSnapshot.retryReplay.stormProtectedCount}`,
    }),
    createLinkDiagnosticsBundleItem({
      bundleId,
      itemType: 'gateway_liveness_summary',
      status,
      generatedAt,
      summary: `online=${input.healthSnapshot.gatewayLiveness.onlineGatewayCount};degraded=${input.healthSnapshot.gatewayLiveness.degradedGatewayCount};offline=${input.healthSnapshot.gatewayLiveness.offlineGatewayCount}`,
    }),
    createLinkDiagnosticsBundleItem({
      bundleId,
      itemType: 'evidence_summary',
      status,
      generatedAt,
      summary: `chains=${input.healthSnapshot.evidence.evidenceChainCount};incomplete=${input.healthSnapshot.evidence.incompleteChainCount};tamper=${input.healthSnapshot.evidence.tamperMismatchCount}`,
    }),
  ];

  const itemIds = items.map((item) => item.itemId);
  const bundleHash = createLinkDiagnosticsBundleHash({
    bundleId,
    itemIds,
    generatedAt,
  });

  const manifest: LinkDiagnosticsBundleManifest = {
    manifestId: `${bundleId}-manifest`,
    bundleId,
    linkNodeId: input.healthSnapshot.linkNodeId,
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
    linkNodeId: input.healthSnapshot.linkNodeId,
    generatedAt,
    status,
    exportScope: input.exportScope ?? 'LOCAL_ONLY',
    healthStatus: input.healthSnapshot.healthStatus,
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

export function validateLinkRuntimeDiagnosticsBundleContract(
  bundle: LinkRuntimeDiagnosticsBundleContract,
): readonly string[] {
  const reasons: string[] = [];

  if (!bundle.bundleId.trim()) reasons.push('bundleId is required');
  if (!bundle.linkNodeId.trim()) reasons.push('linkNodeId is required');
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
