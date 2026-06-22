/**
 * S01 EDGE — HMAC signing for S02 LINK ingress (re-export wire security).
 */

export {
  attachWireEventSignature,
  buildEdgeLinkHeaders,
  computeWireEventSignature,
  extractLinkIngressHeaders,
  signEdgeEventPayload,
  signWireEventPayload,
  verifyWireEventSignature,
  type EdgeLinkSecurityContext,
} from '../../generated/security/edge-link-security-headers.js';
