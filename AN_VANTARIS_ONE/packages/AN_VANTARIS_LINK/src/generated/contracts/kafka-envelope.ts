// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

import type { WireTransportEvent } from './wire-event-v1.js';

export const EDGELINK_KAFKA_TOPIC = 'edgelink-wire-events';

export interface KafkaWireEnvelope {
  readonly topic: string;
  readonly partition: number;
  readonly key: string;
  readonly timestamp: string;
  readonly value: WireTransportEvent;
}

export function serializeKafkaWireEnvelope(envelope: KafkaWireEnvelope): string {
  return JSON.stringify(envelope);
}
