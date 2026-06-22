// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

export const DELIVERY_ACK_PROTOCOL_VERSION = 'v1';

export type DeliveryAckStatus = 'ACK' | 'RETRY' | 'DLQ';

export interface DeliveryAck {
  readonly protocolVersion: string;
  readonly partitionId: number;
  readonly offset: number;
  readonly eventId: string;
  readonly status: DeliveryAckStatus;
  readonly timestamp: string;
  readonly reason?: string;
}

export function createDeliveryAck(input: {
  partitionId: number;
  offset: number;
  eventId: string;
  status: DeliveryAckStatus;
  timestamp: string;
  reason?: string;
}): DeliveryAck {
  return {
    protocolVersion: DELIVERY_ACK_PROTOCOL_VERSION,
    ...input,
  };
}
