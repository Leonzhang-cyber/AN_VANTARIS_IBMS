/**
 * S02 LINK — delivery state machine.
 * PENDING → DELIVERED | RETRYING → FAILED(DLQ)
 */

export type LinkDeliveryState = 'PENDING' | 'DELIVERED' | 'RETRYING' | 'FAILED';

export interface LinkQueueRecord {
  readonly queueId: string;
  readonly state: LinkDeliveryState;
  readonly attempts: number;
  readonly enqueuedAt: string;
  readonly lastAttemptAt: string | null;
  readonly dlqReason: string | null;
}

export function transitionLinkState(
  current: LinkDeliveryState,
  deliverySucceeded: boolean,
  attempts: number,
  maxAttempts: number,
): LinkDeliveryState {
  if (deliverySucceeded) {
    return 'DELIVERED';
  }

  if (attempts < maxAttempts) {
    return 'RETRYING';
  }

  return 'FAILED';
}
