export type DeliveryAuditEventType =
  | 'buffer.ingested'
  | 'buffer.pending'
  | 'buffer.failed'
  | 'buffer.acknowledged'
  | 'buffer.quarantined'
  | 'delivery.preview.created'
  | 'delivery.retry.evaluated'
  | 'delivery.cursor.updated'
  | 'delivery.batch.pending'
  | 'delivery.batch.failed'
  | 'delivery.batch.acknowledged';

export type DeliveryAuditActor = 'buffer-store' | 'delivery-orchestrator' | 'connector-manager' | 'runtime';

export interface DeliveryAuditTarget {
  readonly recordId: string | null;
  readonly envelopeId: string | null;
  readonly connectorId: string | null;
  readonly batchId: string | null;
}

export interface DeliveryAuditEvent {
  readonly eventId: string;
  readonly eventType: DeliveryAuditEventType;
  readonly actor: DeliveryAuditActor;
  readonly target: DeliveryAuditTarget;
  readonly at: string;
  readonly details: Record<string, unknown>;
}

export interface DeliveryAuditChainRecord {
  readonly sequence: number;
  readonly previousHash: string;
  readonly currentHash: string;
  readonly event: DeliveryAuditEvent;
}

export interface DeliveryAuditIntegritySummary {
  readonly valid: boolean;
  readonly recordCount: number;
  readonly firstHash: string | null;
  readonly lastHash: string | null;
  readonly brokenAtSequence: number | null;
  readonly generatedAt: string;
}

export interface DeliveryAuditEvidenceExport {
  readonly generatedAt: string;
  readonly ledgerPath: string;
  readonly integrity: DeliveryAuditIntegritySummary;
  readonly records: readonly DeliveryAuditChainRecord[];
}

export interface DeliveryAuditError {
  readonly code: string;
  readonly message: string;
  readonly sequence: number | null;
}
