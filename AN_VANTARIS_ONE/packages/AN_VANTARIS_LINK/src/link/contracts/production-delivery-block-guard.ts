/**
 * LINK-C4-04 — Production delivery block guard.
 *
 * LINK-owned guard that prevents production delivery during C4 and until an
 * explicit controlled pilot / production approval gate enables it.
 *
 * This contract does not enable production delivery.
 */

import type { LinkDeliveryTargetContract } from './delivery-target-contract.js';
import {
  isDeliveryTargetDryRunAllowed,
  isDeliveryTargetProductionApproved,
} from './delivery-target-contract.js';
import type { LinkDeliveryIdempotencyContract } from './delivery-idempotency-contract.js';
import type { LinkQueueItemContract } from './queue-item-contract.js';

export type LinkProductionDeliveryBlockCode =
  | 'LINK_DELIVERY_DRY_RUN_ALLOWED'
  | 'LINK_DELIVERY_PRODUCTION_BLOCKED'
  | 'LINK_DELIVERY_TARGET_NOT_APPROVED'
  | 'LINK_DELIVERY_TARGET_REVOKED'
  | 'LINK_DELIVERY_DIRECT_DB_PROHIBITED'
  | 'LINK_DELIVERY_WRITEBACK_PROHIBITED'
  | 'LINK_DELIVERY_CREDENTIAL_SECRET_PROHIBITED'
  | 'LINK_DELIVERY_IDEMPOTENCY_INVALID'
  | 'LINK_DELIVERY_QUEUE_ITEM_INVALID';

export interface LinkProductionDeliveryGuardResult {
  readonly allowed: boolean;
  readonly dryRunAllowed: boolean;
  readonly code: LinkProductionDeliveryBlockCode;
  readonly reason: string;
}

export function evaluateProductionDeliveryBlockGuard(input: {
  readonly target: LinkDeliveryTargetContract;
  readonly item: LinkQueueItemContract;
  readonly idempotency: LinkDeliveryIdempotencyContract;
  readonly forceProductionBlocked?: boolean;
}): LinkProductionDeliveryGuardResult {
  if (!input.item.queueId.trim() || !input.item.eventId.trim() || !input.item.traceId.trim()) {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_QUEUE_ITEM_INVALID',
      reason: 'queue item is invalid',
    };
  }

  if (
    !input.idempotency.idempotencyKey.trim() ||
    !input.idempotency.reliabilityKey.trim() ||
    !input.idempotency.duplicateRiskKey.trim()
  ) {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_IDEMPOTENCY_INVALID',
      reason: 'idempotency contract is invalid',
    };
  }

  if (input.target.status === 'REVOKED') {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_TARGET_REVOKED',
      reason: 'delivery target is revoked',
    };
  }

  if (input.target.directDbAccessAllowed !== false) {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_DIRECT_DB_PROHIBITED',
      reason: 'direct DB access is prohibited',
    };
  }

  if (input.target.writebackAllowed !== false) {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_WRITEBACK_PROHIBITED',
      reason: 'writeback is prohibited',
    };
  }

  if (input.target.credentialRef.secretMaterialStored !== false) {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_CREDENTIAL_SECRET_PROHIBITED',
      reason: 'credential secret material must not be stored',
    };
  }

  if (isDeliveryTargetDryRunAllowed(input.target)) {
    return {
      allowed: true,
      dryRunAllowed: true,
      code: 'LINK_DELIVERY_DRY_RUN_ALLOWED',
      reason: 'dry-run delivery target is allowed',
    };
  }

  if (!input.target.approved) {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_TARGET_NOT_APPROVED',
      reason: 'delivery target is not approved',
    };
  }

  if (input.forceProductionBlocked !== false) {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_PRODUCTION_BLOCKED',
      reason: 'production delivery is blocked by current LINK stage',
    };
  }

  if (!isDeliveryTargetProductionApproved(input.target)) {
    return {
      allowed: false,
      dryRunAllowed: false,
      code: 'LINK_DELIVERY_PRODUCTION_BLOCKED',
      reason: 'delivery target is not production-approved',
    };
  }

  return {
    allowed: true,
    dryRunAllowed: false,
    code: 'LINK_DELIVERY_DRY_RUN_ALLOWED',
    reason: 'production delivery would be allowed only by explicit future gate',
  };
}

export function assertProductionDeliveryBlockedForC4(input: {
  readonly target: LinkDeliveryTargetContract;
  readonly item: LinkQueueItemContract;
  readonly idempotency: LinkDeliveryIdempotencyContract;
}): LinkProductionDeliveryGuardResult {
  const result = evaluateProductionDeliveryBlockGuard({
    ...input,
    forceProductionBlocked: true,
  });

  if (result.dryRunAllowed) {
    return result;
  }

  return {
    allowed: false,
    dryRunAllowed: false,
    code:
      result.code === 'LINK_DELIVERY_DRY_RUN_ALLOWED'
        ? 'LINK_DELIVERY_PRODUCTION_BLOCKED'
        : result.code,
    reason:
      result.code === 'LINK_DELIVERY_DRY_RUN_ALLOWED'
        ? 'production delivery is blocked during LINK-C4'
        : result.reason,
  };
}
