import type { ConnectorProtocol } from './connector-types.js';
import type { NormalizedEventSample, NormalizedPointSample, NormalizedQuality } from './normalization-types.js';

export interface EdgeEnvelopeHeader {
  readonly envelopeId: string;
  readonly schemaVersion: string;
  readonly edgeNodeId: string;
  readonly connectorId: string;
  readonly protocol: ConnectorProtocol;
  readonly sourceRef: string;
  readonly createdAt: string;
  readonly payloadType: 'normalized.samples';
}

export interface EdgeEnvelopePayload {
  readonly points: readonly NormalizedPointSample[];
  readonly events: readonly NormalizedEventSample[];
}

export interface EdgeEnvelopeTrace {
  readonly traceId: string;
  readonly spanId: string;
  readonly generatedBy: string;
  readonly stage: 'local-normalization-envelope';
}

export interface EdgeEnvelope {
  readonly header: EdgeEnvelopeHeader;
  readonly payload: EdgeEnvelopePayload;
  readonly trace: EdgeEnvelopeTrace;
  readonly qualitySummary: {
    readonly totalPoints: number;
    readonly totalEvents: number;
    readonly good: number;
    readonly uncertain: number;
    readonly bad: number;
  };
}

export interface EdgeEnvelopeValidationResult {
  readonly valid: boolean;
  readonly errors: readonly string[];
  readonly warnings: readonly string[];
}

export interface EdgeEnvelopeExportResult {
  readonly path: string;
  readonly bytes: number;
  readonly exportedAt: string;
}

export interface EdgeEnvelopeBuildInput {
  readonly edgeNodeId: string;
  readonly connectorId: string;
  readonly protocol: ConnectorProtocol;
  readonly sourceRef: string;
  readonly points: readonly NormalizedPointSample[];
  readonly events: readonly NormalizedEventSample[];
}

export type QualityCounter = Record<NormalizedQuality, number>;
