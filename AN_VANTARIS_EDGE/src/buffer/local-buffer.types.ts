export type LocalBufferStatus =
  | "pending"
  | "accepted_local"
  | "failed"
  | "expired"
  | "purged";

export interface LocalBufferRecord {
  bufferId: string;
  messageId: string;
  traceId: string;
  status: LocalBufferStatus;
  createdAt: string;
  updatedAt: string;
}
