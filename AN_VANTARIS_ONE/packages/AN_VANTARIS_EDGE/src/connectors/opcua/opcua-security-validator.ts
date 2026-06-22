import type { OpcUaMessageSecurityMode, OpcUaReadOnlyPolicy, OpcUaSecurityPolicy, ValidationResult } from './opcua-readonly-types.js';

const LEGACY_POLICIES = new Set(['Basic128Rsa15', 'Basic256']);
const INSECURE_POLICIES = new Set(['None']);

const REF_PATTERNS = {
  credential: /^secret:\/\/edge\/opcua\/[a-z0-9._-]+$/i,
  certificate: /^cert:\/\/edge\/opcua\/client\/[a-z0-9._-]+$/i,
  privateKey: /^key:\/\/edge\/opcua\/client\/[a-z0-9._-]+$/i,
  fingerprint: /^fingerprint:\/\/edge\/opcua\/server\/[a-z0-9._-]+$/i,
};

function normalizeSecurityPolicy(value: string): OpcUaSecurityPolicy {
  return value.trim().replace(/[\s-]+/g, '') as OpcUaSecurityPolicy;
}

function normalizeMessageSecurityMode(value: string): OpcUaMessageSecurityMode {
  return value.trim().toUpperCase().replace(/[\s-]+/g, '_') as OpcUaMessageSecurityMode;
}

export function validateOpcUaSecurityProfile(
  input: { securityPolicy: string; messageSecurityMode: string },
  policy: OpcUaReadOnlyPolicy,
): ValidationResult {
  const errors: string[] = [];
  const securityPolicy = normalizeSecurityPolicy(input.securityPolicy);
  const messageSecurityMode = normalizeMessageSecurityMode(input.messageSecurityMode);

  if (INSECURE_POLICIES.has(securityPolicy) || securityPolicy === 'None') {
    errors.push('OPCUA_INSECURE_ENDPOINT_REJECTED', 'OPCUA_SECURITY_POLICY_NOT_ALLOWED');
  } else if (LEGACY_POLICIES.has(securityPolicy)) {
    errors.push('OPCUA_SECURITY_POLICY_NOT_ALLOWED');
  } else if (!policy.allowedSecurityPolicies.includes(securityPolicy)) {
    errors.push('OPCUA_SECURITY_POLICY_NOT_ALLOWED');
  }

  if (messageSecurityMode === 'NONE') {
    errors.push('OPCUA_INSECURE_ENDPOINT_REJECTED', 'OPCUA_MESSAGE_SECURITY_MODE_NOT_ALLOWED');
  } else if (!policy.allowedMessageSecurityModes.includes(messageSecurityMode)) {
    errors.push('OPCUA_MESSAGE_SECURITY_MODE_NOT_ALLOWED');
  }

  return { ok: errors.length === 0, errors: [...new Set(errors)] };
}

function looksLikeInlinePem(value: string): boolean {
  return /-----BEGIN [A-Z ]+-----/.test(value);
}

export function validateOpcUaIdentityModel(
  input: {
    readonly credentialRef?: string;
    readonly clientCertificateRef?: string;
    readonly clientPrivateKeyRef?: string;
    readonly username?: string;
    readonly password?: string;
    readonly token?: string;
    readonly inlineCertificate?: string;
    readonly inlinePrivateKey?: string;
    readonly anonymous?: boolean;
  },
  policy: OpcUaReadOnlyPolicy,
): ValidationResult {
  const errors: string[] = [];

  if (input.anonymous && !policy.anonymousAllowed) {
    errors.push('OPCUA_ANONYMOUS_IDENTITY_PROHIBITED');
  }

  if (typeof input.username === 'string' && input.username.length > 0) errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
  if (typeof input.password === 'string' && input.password.length > 0) errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
  if (typeof input.token === 'string' && input.token.length > 0) errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');

  if (typeof input.inlineCertificate === 'string' && input.inlineCertificate.length > 0) {
    errors.push('INLINE_CERTIFICATE_PROHIBITED');
  }
  if (typeof input.inlinePrivateKey === 'string' && input.inlinePrivateKey.length > 0) {
    errors.push('INLINE_PRIVATE_KEY_PROHIBITED');
  }

  if (typeof input.credentialRef === 'string' && !REF_PATTERNS.credential.test(input.credentialRef)) {
    errors.push('OPCUA_IDENTITY_REFERENCE_INVALID');
  }
  if (typeof input.clientCertificateRef === 'string' && !REF_PATTERNS.certificate.test(input.clientCertificateRef)) {
    errors.push('OPCUA_IDENTITY_REFERENCE_INVALID');
  }
  if (typeof input.clientPrivateKeyRef === 'string' && !REF_PATTERNS.privateKey.test(input.clientPrivateKeyRef)) {
    errors.push('OPCUA_IDENTITY_REFERENCE_INVALID');
  }

  const hasIdentityRef =
    (typeof input.credentialRef === 'string' && REF_PATTERNS.credential.test(input.credentialRef)) ||
    (typeof input.clientCertificateRef === 'string' && REF_PATTERNS.certificate.test(input.clientCertificateRef));

  if (policy.credentialMode === 'REFERENCE_ONLY' && !input.anonymous && !hasIdentityRef) {
    errors.push('OPCUA_IDENTITY_REFERENCE_INVALID');
  }

  return { ok: errors.length === 0, errors: [...new Set(errors)] };
}

export function validateOpcUaServerIdentityModel(
  input: {
    readonly serverFingerprintRef?: string;
    readonly endpointHostname?: string;
    readonly expectedHostname?: string;
    readonly applicationUri?: string;
    readonly serverApplicationUri?: string;
    readonly trustEstablished?: boolean;
    readonly certificateMismatch?: boolean;
    readonly autoTrust?: boolean;
  },
  policy: OpcUaReadOnlyPolicy,
): ValidationResult {
  const errors: string[] = [];

  if (!input.serverFingerprintRef) {
    errors.push('OPCUA_SERVER_CERTIFICATE_REFERENCE_REQUIRED');
  } else if (!REF_PATTERNS.fingerprint.test(input.serverFingerprintRef)) {
    errors.push('OPCUA_IDENTITY_REFERENCE_INVALID');
  }

  if (policy.hostnameVerificationRequired) {
    if (!input.expectedHostname || !input.endpointHostname) {
      errors.push('OPCUA_HOSTNAME_VERIFICATION_FAILED');
    } else if (input.expectedHostname.trim().toLowerCase() !== input.endpointHostname.trim().toLowerCase()) {
      errors.push('OPCUA_HOSTNAME_VERIFICATION_FAILED');
    }
  }

  if (policy.applicationUriVerificationRequired) {
    if (!input.applicationUri || !input.serverApplicationUri) {
      errors.push('OPCUA_APPLICATION_URI_MISMATCH');
    } else if (input.applicationUri !== input.serverApplicationUri) {
      errors.push('OPCUA_APPLICATION_URI_MISMATCH');
    }
  }

  if (input.certificateMismatch) {
    errors.push('OPCUA_SERVER_CERTIFICATE_MISMATCH');
  }

  if (input.autoTrust) {
    errors.push('OPCUA_SERVER_TRUST_NOT_ESTABLISHED');
  } else if (input.trustEstablished === false) {
    errors.push('OPCUA_SERVER_TRUST_NOT_ESTABLISHED');
  }

  return { ok: errors.length === 0, errors: [...new Set(errors)] };
}
