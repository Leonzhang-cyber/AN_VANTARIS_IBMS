/**
 * LINK-C3-01 — Queue state contract.
 *
 * LINK-owned GA-ready queue state model.
 *
 * This contract extends current transport queue behavior without enabling
 * production delivery.
 */

export type LinkGaQueueState =
  | 'RECEIVED'
  | 'VALIDATED'
  | 'QUEUED'
  | 'DELIVERING'
  | 'DELIVERED'
  | 'ACKED'
  | 'RETRY_PENDING'
  | 'DLQ'
  | 'REJECTED'
  | 'EXPIRED';

export type LinkLegacyQueueState = 'PENDING' | 'RETRYING' | 'FAILED' | 'DELIVERED';

export type LinkQueueTransitionReason =
  | 'INGRESS_RECEIVED'
  | 'INGRESS_VALIDATED'
  | 'INGRESS_QUEUED'
  | 'DELIVERY_STARTED'
  | 'DELIVERY_ACCEPTED'
  | 'DELIVERY_ACKED'
  | 'DELIVERY_RETRY_PENDING'
  | 'DELIVERY_EXHAUSTED'
  | 'SCHEMA_REJECTED'
  | 'SECURITY_REJECTED'
  | 'POLICY_BLOCKED'
  | 'QUEUE_EXPIRED'
  | 'QUEUE_BACKPRESSURE'
  | 'UNKNOWN';

export interface LinkQueueStateSnapshot {
  readonly state: LinkGaQueueState;
  readonly reason: LinkQueueTransitionReason;
  readonly updatedAt: string;
  readonly attempts: number;
  readonly retryable: boolean;
  readonly terminal: boolean;
}

export interface LinkQueueStateTransition {
  readonly from: LinkGaQueueState;
  readonly to: LinkGaQueueState;
  readonly reason: LinkQueueTransitionReason;
  readonly transitionedAt: string;
}

export function isTerminalLinkQueueState(state: LinkGaQueueState): boolean {
  return state === 'ACKED' || state === 'DLQ' || state === 'REJECTED' || state === 'EXPIRED';
}

export function isRetryableLinkQueueState(state: LinkGaQueueState): boolean {
  return state === 'RETRY_PENDING' || state === 'QUEUED';
}

export function mapLegacyQueueStateToGaState(state: LinkLegacyQueueState): LinkGaQueueState {
  switch (state) {
    case 'PENDING':
      return 'QUEUED';
    case 'RETRYING':
      return 'RETRY_PENDING';
    case 'FAILED':
      return 'DLQ';
    case 'DELIVERED':
      return 'DELIVERED';
  }
}

export function createLinkQueueStateSnapshot(
  state: LinkGaQueueState,
  reason: LinkQueueTransitionReason,
  attempts = 0,
  updatedAt = new Date().toISOString(),
): LinkQueueStateSnapshot {
  return {
    state,
    reason,
    updatedAt,
    attempts,
    retryable: isRetryableLinkQueueState(state),
    terminal: isTerminalLinkQueueState(state),
  };
}

export function createLinkQueueStateTransition(
  from: LinkGaQueueState,
  to: LinkGaQueueState,
  reason: LinkQueueTransitionReason,
  transitionedAt = new Date().toISOString(),
): LinkQueueStateTransition {
  return {
    from,
    to,
    reason,
    transitionedAt,
  };
}

export function canTransitionLinkQueueState(
  from: LinkGaQueueState,
  to: LinkGaQueueState,
): boolean {
  if (isTerminalLinkQueueState(from)) {
    return false;
  }

  const allowed: Readonly<Record<LinkGaQueueState, readonly LinkGaQueueState[]>> = {
    RECEIVED: ['VALIDATED', 'REJECTED'],
    VALIDATED: ['QUEUED', 'REJECTED', 'BLOCKED' as never],
    QUEUED: ['DELIVERING', 'RETRY_PENDING', 'DLQ', 'EXPIRED'],
    DELIVERING: ['DELIVERED', 'RETRY_PENDING', 'DLQ'],
    DELIVERED: ['ACKED', 'RETRY_PENDING', 'DLQ'],
    ACKED: [],
    RETRY_PENDING: ['QUEUED', 'DELIVERING', 'DLQ', 'EXPIRED'],
    DLQ: [],
    REJECTED: [],
    EXPIRED: [],
  };

  return allowed[from].includes(to);
}
