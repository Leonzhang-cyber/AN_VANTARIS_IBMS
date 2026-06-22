import type { ConnectorProtocol } from './connector-types.js';
import type { ProtocolPluginPollResult } from './protocol-plugin-types.js';

export type NormalizedQuality = 'good' | 'uncertain' | 'bad';

export interface NormalizedSampleSource {
  readonly connectorId: string;
  readonly sourceSystemId: string;
  readonly protocol: ConnectorProtocol;
  readonly pluginId: string;
  readonly sampleId: string;
}

export interface NormalizedSampleMetadata {
  readonly normalizedAt: string;
  readonly synthetic: boolean;
  readonly sequence: number;
  readonly tags: readonly string[];
}

export interface NormalizedPointSample {
  readonly sampleId: string;
  readonly pointRef: string;
  readonly value: number | string | boolean;
  readonly valueType: 'float' | 'int' | 'string' | 'bool';
  readonly unit: string;
  readonly quality: NormalizedQuality;
  readonly timestamp: string;
  readonly source: NormalizedSampleSource;
  readonly metadata: NormalizedSampleMetadata;
}

export interface NormalizedEventSample {
  readonly sampleId: string;
  readonly eventType: string;
  readonly severity: 'info' | 'warning' | 'critical';
  readonly message: string;
  readonly quality: NormalizedQuality;
  readonly timestamp: string;
  readonly source: NormalizedSampleSource;
  readonly metadata: NormalizedSampleMetadata;
}

export interface NormalizationWarning {
  readonly code: string;
  readonly message: string;
  readonly sampleId: string | null;
}

export interface NormalizationError {
  readonly code: string;
  readonly message: string;
  readonly sampleId: string | null;
}

export interface NormalizationResult {
  readonly pluginId: string;
  readonly connectorId: string;
  readonly protocol: ConnectorProtocol;
  readonly normalizedPoints: readonly NormalizedPointSample[];
  readonly normalizedEvents: readonly NormalizedEventSample[];
  readonly warnings: readonly NormalizationWarning[];
  readonly errors: readonly NormalizationError[];
  readonly generatedAt: string;
  readonly sourcePollResult: Pick<ProtocolPluginPollResult, 'connectorId' | 'protocol'>;
}
