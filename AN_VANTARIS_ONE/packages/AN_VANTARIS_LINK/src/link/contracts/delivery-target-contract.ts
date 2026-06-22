/**
 * LINK-C4-01 — Delivery target contract.
 *
 * LINK-owned contract for approved upper-layer API delivery targets.
 *
 * This contract does not enable production delivery.
 * LINK must not deliver to unapproved targets.
 * LINK must not access UFMS DB directly.
 */

export type LinkDeliveryTargetType =
  | 'UFMS_APP_API'
  | 'VANTARIS_CODE_API'
  | 'SYNTHETIC_DRY_RUN'
  | 'UNKNOWN';

export type LinkDeliveryTargetStatus =
  | 'DRAFT'
  | 'APPROVED_DRY_RUN'
  | 'APPROVED_PILOT'
  | 'APPROVED_PRODUCTION'
  | 'BLOCKED'
  | 'REVOKED';

export interface LinkDeliveryApprovalRef {
  readonly approvalId: string;
  readonly approvalType:
    | 'endpoint_approval'
    | 'pilot_approval'
    | 'production_approval'
    | 'synthetic_dry_run'
    | 'unknown';
  readonly approvedBy?: string;
  readonly approvedAt?: string;
  readonly evidenceRef?: string;
}

export interface LinkDeliveryCredentialRef {
  readonly credentialRefId: string;
  readonly credentialType:
    | 'machine_identity'
    | 'hmac_reference'
    | 'mtls_certificate_reference'
    | 'bearer_token_reference'
    | 'none';
  readonly secretMaterialStored: false;
}

export interface LinkDeliveryTargetContract {
  readonly targetId: string;
  readonly targetType: LinkDeliveryTargetType;
  readonly status: LinkDeliveryTargetStatus;
  readonly baseUrl: string;
  readonly apiVersion: string;
  readonly endpointPath: string;
  readonly timeoutMs: number;
  readonly approved: boolean;
  readonly approvalRef: LinkDeliveryApprovalRef;
  readonly credentialRef: LinkDeliveryCredentialRef;
  readonly productionDeliveryAllowed: boolean;
  readonly directDbAccessAllowed: false;
  readonly writebackAllowed: false;
}

export interface LinkDeliveryTargetValidationResult {
  readonly valid: boolean;
  readonly reasons: readonly string[];
}

export function createSyntheticDryRunDeliveryTarget(
  targetId = 'synthetic-dry-run-target',
): LinkDeliveryTargetContract {
  return {
    targetId,
    targetType: 'SYNTHETIC_DRY_RUN',
    status: 'APPROVED_DRY_RUN',
    baseUrl: 'local://synthetic-dry-run',
    apiVersion: 'v1',
    endpointPath: '/dry-run/link-delivery',
    timeoutMs: 1000,
    approved: true,
    approvalRef: {
      approvalId: 'synthetic-dry-run-approval',
      approvalType: 'synthetic_dry_run',
    },
    credentialRef: {
      credentialRefId: 'none',
      credentialType: 'none',
      secretMaterialStored: false,
    },
    productionDeliveryAllowed: false,
    directDbAccessAllowed: false,
    writebackAllowed: false,
  };
}

export function isDeliveryTargetProductionApproved(
  target: LinkDeliveryTargetContract,
): boolean {
  return (
    target.approved === true &&
    target.status === 'APPROVED_PRODUCTION' &&
    target.productionDeliveryAllowed === true &&
    target.directDbAccessAllowed === false &&
    target.writebackAllowed === false &&
    target.credentialRef.secretMaterialStored === false
  );
}

export function isDeliveryTargetDryRunAllowed(
  target: LinkDeliveryTargetContract,
): boolean {
  return (
    target.approved === true &&
    target.status === 'APPROVED_DRY_RUN' &&
    target.productionDeliveryAllowed === false &&
    target.directDbAccessAllowed === false &&
    target.writebackAllowed === false
  );
}

export function validateLinkDeliveryTargetContract(
  target: LinkDeliveryTargetContract,
): LinkDeliveryTargetValidationResult {
  const reasons: string[] = [];

  if (!target.targetId.trim()) {
    reasons.push('targetId is required');
  }

  if (!target.baseUrl.trim()) {
    reasons.push('baseUrl is required');
  }

  if (!target.apiVersion.trim()) {
    reasons.push('apiVersion is required');
  }

  if (!target.endpointPath.trim()) {
    reasons.push('endpointPath is required');
  }

  if (!Number.isInteger(target.timeoutMs) || target.timeoutMs < 1) {
    reasons.push('timeoutMs must be greater than zero');
  }

  if (!target.approvalRef.approvalId.trim()) {
    reasons.push('approvalRef.approvalId is required');
  }

  if (!target.credentialRef.credentialRefId.trim()) {
    reasons.push('credentialRef.credentialRefId is required');
  }

  if (target.credentialRef.secretMaterialStored !== false) {
    reasons.push('credential material must not be stored in source code');
  }

  if (target.directDbAccessAllowed !== false) {
    reasons.push('direct DB access is prohibited');
  }

  if (target.writebackAllowed !== false) {
    reasons.push('writeback is prohibited');
  }

  if (target.productionDeliveryAllowed === true && target.status !== 'APPROVED_PRODUCTION') {
    reasons.push('productionDeliveryAllowed requires APPROVED_PRODUCTION status');
  }

  return {
    valid: reasons.length === 0,
    reasons,
  };
}
