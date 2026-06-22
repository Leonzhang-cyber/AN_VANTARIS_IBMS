/**
 * S01 EDGE — Acquisition Layer exports.
 */

export {
  createEdgeAcquisitionService,
  EdgeAcquisitionService,
  type EdgeAcquisitionContext,
} from './edge-acquisition.service.js';

export type { EdgeEvent, EdgeEventInput } from './edge-acquisition.service.js';

export { createEdgeWalBuffer, EdgeWalBuffer, type EdgeWalEntry } from './edge-buffer.service.js';
export { buildEdgeHeartbeatEvent, type EdgeHeartbeatInput } from './edge-heartbeat.service.js';
export { buildEdgeLinkHeaders, signEdgeEventPayload } from './edge-signing.js';
export {
  createNoopEdgeHandoffPublisher,
  type EdgeHandoffPublisher,
  type EdgeHandoffPublishResult,
  type EdgeHandoffPublishStatus,
} from './edge-handoff-publisher.js';
