import { createHash, randomUUID } from 'node:crypto';

import type { EdgeLocalEnvelope, NormalizedMessageType } from './types.js';

interface BuildEnvelopeInput {
  readonly edgeId: string;
  readonly siteId: string;
  readonly sourceSystemId: string;
  readonly connectorId: string;
  readonly messageType: NormalizedMessageType;
  readonly payload: Record<string, unknown>;
}

function checksum(payload: Record<string, unknown>, nonce: string): string {
  const canonical = JSON.stringify({ nonce, payload });
  return createHash('sha256').update(canonical).digest('hex');
}

export function buildCanonicalEnvelope(input: BuildEnvelopeInput): EdgeLocalEnvelope {
  const traceId = randomUUID();
  const nonce = randomUUID();
  return {
    messageId: randomUUID(),
    edgeId: input.edgeId,
    siteId: input.siteId,
    sourceSystemId: input.sourceSystemId,
    connectorId: input.connectorId,
    messageType: input.messageType,
    timestamp: new Date().toISOString(),
    nonce,
    payload: input.payload,
    trace: {
      traceId,
      spanId: randomUUID(),
    },
    integrity: {
      algorithm: 'sha256',
      checksum: checksum(input.payload, nonce),
      signature: null,
      signatureStatus: 'disabled',
    },
  };
}

export function runNormalizationDryRun(edgeId: string, siteId: string): {
  readonly telemetry: EdgeLocalEnvelope;
  readonly event: EdgeLocalEnvelope;
  readonly alarm: EdgeLocalEnvelope;
  readonly health: EdgeLocalEnvelope;
  readonly evidence: EdgeLocalEnvelope;
} {
  const common = { edgeId, siteId, sourceSystemId: 'dryrun-system-001' };
  return {
    telemetry: buildCanonicalEnvelope({
      ...common,
      connectorId: 'connector-modbus-01',
      messageType: 'telemetry.point.updated',
      payload: { pointCode: 'supply_air_temperature', value: 23.6, unit: 'C', quality: 'good' },
    }),
    event: buildCanonicalEnvelope({
      ...common,
      connectorId: 'connector-mqtt-01',
      messageType: 'event.created',
      payload: { eventCode: 'door_opened', severity: 'info' },
    }),
    alarm: buildCanonicalEnvelope({
      ...common,
      connectorId: 'connector-http-01',
      messageType: 'alarm.raised',
      payload: { alarmCode: 'high_pressure', severity: 'high' },
    }),
    health: buildCanonicalEnvelope({
      ...common,
      connectorId: 'connector-opcua-01',
      messageType: 'device.health.updated',
      payload: { deviceCode: 'DDC-AHU-01', status: 'healthy' },
    }),
    evidence: buildCanonicalEnvelope({
      ...common,
      connectorId: 'connector-vendor-sdk-01',
      messageType: 'evidence.captured',
      payload: { artifactType: 'snapshot', reference: 'local://dryrun/evidence-1' },
    }),
  };
}
