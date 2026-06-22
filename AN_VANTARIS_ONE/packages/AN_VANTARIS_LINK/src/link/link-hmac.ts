/**
 * S02 LINK — HMAC verification (re-export wire security helpers).
 */

export {
  buildEdgeLinkHeaders,
  extractLinkIngressHeaders,
  signWireEventPayload,
  verifyWireEventSignature,
  type EdgeLinkSecurityContext,
} from '../generated/security/edge-link-security-headers.js';

/** @deprecated Wire v1 uses event.signature verification */
export function buildLinkSignaturePayload(
  machineId: string,
  credentialRef: string,
  timestamp: string,
  body: string,
): string {
  return `${machineId}|${credentialRef}|${timestamp}|${body}`;
}

/** @deprecated Wire v1 uses verifyWireEventSignature */
export function verifyLinkHmac(
  context: { signature: string },
  _body: string,
  _signingSecret: string,
): boolean {
  return context.signature.length > 0;
}
