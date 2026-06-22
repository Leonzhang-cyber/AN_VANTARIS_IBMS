// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

export const EDGE_EVENT_SCHEMA_VERSION = 'v1';

export type { WireEventV1 as EdgeEvent, WireEventInput as EdgeEventInput } from './wire-event-v1.js';
export type {
  CoreWireTraceResponse,
  WireEventLifecycle,
  WireEventMetrics,
  WireEventSignPayload,
  WireEventV1,
  WireEventV1_1,
  WireTransportEvent,
} from './wire-event-v1.js';

export {
  WIRE_PROTOCOL_VERSION,
  WIRE_PROTOCOL_VERSION_V1_1,
  isSupportedWireProtocolVersion,
  isWireEventV1_1,
} from './wire-event-v1.js';

export type { WireErrorCode } from './wire-errors.js';
export { WIRE_ERROR_CODES, WireTransportError } from './wire-errors.js';
export { parseWireEventJson, serializeWireEvent, serializeWireEventSignInput } from './wire-serializer-v1.js';
