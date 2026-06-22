import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname } from 'node:path';

export interface DiagnosticsPack {
  readonly generatedAt: string;
  readonly edgeIdentity: {
    readonly edgeId: string;
    readonly siteId: string;
    readonly mode: 'edge-only';
  };
  readonly connectorRegistry: unknown;
  readonly pluginCapabilities: unknown;
  readonly healthSnapshot: unknown;
  readonly hardwareKey: {
    readonly required: boolean;
    readonly present: boolean;
    readonly provider: string;
    readonly serial: string;
    readonly status: string;
    readonly lockedReason: string | null;
    readonly runtimeMode: string;
  };
  readonly bufferSnapshot: unknown;
  readonly restartRecoveryEvidence: unknown;
  readonly persistencePressure: unknown;
  readonly quarantine: unknown;
  readonly normalizationDryRunResult: unknown;
  readonly auditPlaceholderEvents: unknown;
  readonly boundaryAssertions: {
    readonly noExternalServiceCalls: true;
    readonly noDbWrite: true;
    readonly noLinkRuntimeCall: true;
    readonly signatureNotForged: true;
  };
  readonly validationSummary: {
    readonly typecheckEdge: 'pass';
    readonly boundaryMode: 'edge-only';
  };
}

export function exportDiagnosticsPack(path: string, payload: DiagnosticsPack): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(payload, null, 2) + '\n', 'utf8');
}
