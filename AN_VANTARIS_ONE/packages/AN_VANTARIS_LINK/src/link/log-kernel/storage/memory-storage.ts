/**
 * In-memory log storage — default durable kernel backend.
 */

export {
  PartitionLogStore as MemoryLogStorage,
  createPartitionLogStore as createMemoryLogStorage,
} from '../partition-log-store.js';
