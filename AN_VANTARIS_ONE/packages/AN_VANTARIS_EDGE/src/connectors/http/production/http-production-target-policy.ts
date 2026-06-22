import { createHash } from 'node:crypto';

import { evaluateSsrfRisk, normalizeHttpDestination, validateHttpDestination } from '../http-destination-validator.js';
import type { HttpPollingReadOnlyPolicy } from '../http-readonly-types.js';

import type {
  HttpProductionAdapterConfig,
  HttpProductionErrorCode,
  HttpProductionResourceLimits,
} from './http-production-adapter.types.js';
import {
  HTTP_PRODUCTION_LIMIT_CAPS,
  HTTP_PRODUCTION_METADATA_HOSTS,
} from './http-production-adapter.types.js';

const LOOPBACK_HOSTS = new Set(['127.0.0.1', '::1', 'localhost']);

function normalizeHostname(hostname: string): string {
  return hostname.trim().toLowerCase().replace(/\.$/, '');
}

export function createTargetReferenceId(targetReferenceId: string, relativePath: string): string {
  const digest = createHash('sha256')
    .update(`${targetReferenceId}\0${relativePath}`, 'utf8')
    .digest('hex')
    .slice(0, 16);
  return `http-target:${targetReferenceId}:${digest}`;
}

export function createHostReferenceHash(hostname: string): string {
  return createHash('sha256').update(hostname, 'utf8').digest('hex').slice(0, 16);
}

export function validateRelativePath(relativePath: string): HttpProductionErrorCode | null {
  if (!relativePath || typeof relativePath !== 'string') return 'HTTP_URL_INVALID';
  if (!relativePath.startsWith('/')) return 'HTTP_URL_INVALID';
  if (relativePath.includes('\\')) return 'HTTP_URL_INVALID';
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(relativePath)) return 'HTTP_URL_INVALID';
  if (relativePath.includes('#')) return 'HTTP_URL_INVALID';
  if (relativePath.includes('..')) return 'HTTP_URL_INVALID';
  return null;
}

export function buildFoundationPolicyForProduction(
  allowedHost: string,
  config: HttpProductionAdapterConfig,
  testMode: boolean,
): HttpPollingReadOnlyPolicy {
  const allowedSchemes = testMode && config.tlsMode === 'LOOPBACK_HTTP_TEST' ? ['http', 'https'] : ['https'];
  return {
    schemaVersion: '1.0',
    taskId: 'UFMS-EDGE-C5-02',
    classification: 'CONTROLLED_HTTP_POLLING_READ_ONLY_FOUNDATION',
    allowedSchemes,
    allowedMethods: ['GET'],
    allowedHosts: [normalizeHostname(allowedHost)],
    deniedHosts: [...HTTP_PRODUCTION_METADATA_HOSTS],
    deniedCidrs: [
      '127.0.0.0/8',
      '10.0.0.0/8',
      '172.16.0.0/12',
      '192.168.0.0/16',
      '169.254.0.0/16',
      '0.0.0.0/8',
      '100.64.0.0/10',
      '::1/128',
      'fc00::/7',
      'fe80::/10',
      'ff00::/8',
      '::/128',
    ],
    httpsRequiredForProduction: !testMode,
    redirectPolicy: config.maxRedirects > 0 ? 'FOLLOW' : 'REJECT',
    maxRedirects: Math.min(config.maxRedirects, HTTP_PRODUCTION_LIMIT_CAPS.maxRedirects),
    requestTimeoutMs: Math.min(config.responseTimeoutMs, HTTP_PRODUCTION_LIMIT_CAPS.responseTimeoutMs),
    maxRetryAttempts: 0,
    retryableStatusCodes: [],
    retryableErrorClasses: [],
    backoffBaseMs: 100,
    backoffMultiplier: 2,
    backoffMaxMs: 5000,
    maxResponseBytes: Math.min(config.maxResponseBytes, HTTP_PRODUCTION_LIMIT_CAPS.maxResponseBytes),
    allowedContentTypes: [...config.expectedContentTypes],
    credentialMode: 'REFERENCE_ONLY',
    plaintextCredentialsAllowed: false,
    dnsResolutionMode: testMode ? 'MODELED_ONLY' : 'REAL',
    networkAccessAllowed: false,
    syntheticTransportOnly: false,
    writeMethodsAllowed: false,
    responseParsingMode: 'FOUNDATION_JSON_CSV',
    jsonAllowObject: true,
    jsonAllowArray: true,
    jsonAllowScalar: false,
    jsonMaxDepth: Math.min(config.maxJsonDepth, HTTP_PRODUCTION_LIMIT_CAPS.maxJsonDepth),
    csvHeaderRequired: true,
    csvDelimiter: ',',
    csvMaxRows: Math.min(config.maxRecordCount, HTTP_PRODUCTION_LIMIT_CAPS.maxRecordCount),
    candidateStatus: 'CONTROLLED_HTTP_POLLING_READ_ONLY_FOUNDATION',
    readinessKey: 'UFMS_EDGE_C5_02_HTTP_POLLING_CONTROLLED_READ_ONLY_FOUNDATION_PASS',
  };
}

export function isMetadataHost(hostname: string): boolean {
  const normalized = normalizeHostname(hostname);
  return HTTP_PRODUCTION_METADATA_HOSTS.some((host) => normalized === normalizeHostname(host));
}

export function validateResolvedIpAddress(ip: string, testMode: boolean): HttpProductionErrorCode | null {
  const normalized = ip.trim().toLowerCase();
  if (isMetadataHost(normalized)) return 'HTTP_METADATA_TARGET_REJECTED';
  if (normalized === '169.254.169.254' || normalized === '100.100.100.200') return 'HTTP_METADATA_TARGET_REJECTED';
  if (LOOPBACK_HOSTS.has(normalized)) {
    return testMode ? null : 'HTTP_TARGET_NOT_ALLOWLISTED';
  }
  if (/^10\./.test(normalized) || /^192\.168\./.test(normalized) || /^172\.(1[6-9]|2\d|3[0-1])\./.test(normalized)) {
    return testMode ? null : 'HTTP_TARGET_NOT_ALLOWLISTED';
  }
  if (normalized.startsWith('169.254.') || normalized.startsWith('fe80:') || normalized === '::1' || normalized === '0.0.0.0') {
    return testMode ? null : 'HTTP_TARGET_NOT_ALLOWLISTED';
  }
  return null;
}

export function validateAllResolvedIps(ips: readonly string[], testMode: boolean): HttpProductionErrorCode | null {
  if (ips.length === 0) return 'HTTP_DNS_RESOLUTION_FAILED';
  for (const ip of ips) {
    const err = validateResolvedIpAddress(ip, testMode);
    if (err) return err;
  }
  return null;
}

export function resolveProductionTargetUrl(
  baseUrl: string,
  config: HttpProductionAdapterConfig,
): { ok: true; url: string; hostname: string } | { ok: false; errorCode: HttpProductionErrorCode } {
  const relError = validateRelativePath(config.relativePath);
  if (relError) return { ok: false, errorCode: relError };

  let base: URL;
  try {
    base = new URL(baseUrl);
  } catch {
    return { ok: false, errorCode: 'HTTP_TARGET_REFERENCE_NOT_FOUND' };
  }

  if (base.username || base.password) return { ok: false, errorCode: 'HTTP_USERINFO_REJECTED' };
  if (base.hash) return { ok: false, errorCode: 'HTTP_URL_INVALID' };

  const path = config.relativePath.startsWith('/') ? config.relativePath : `/${config.relativePath}`;
  const url = new URL(path, base);
  if (config.queryParameters) {
    for (const [key, value] of Object.entries(config.queryParameters)) {
      url.searchParams.set(key, value);
    }
  }

  if (url.username || url.password) return { ok: false, errorCode: 'HTTP_USERINFO_REJECTED' };
  if (url.hash) return { ok: false, errorCode: 'HTTP_URL_INVALID' };
  if (!url.hostname) return { ok: false, errorCode: 'HTTP_URL_INVALID' };

  return { ok: true, url: url.toString(), hostname: normalizeHostname(url.hostname) };
}

export function validateProductionTargetUrl(
  url: string,
  config: HttpProductionAdapterConfig,
  testMode: boolean,
): { ok: true; hostname: string } | { ok: false; errorCode: HttpProductionErrorCode } {
  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    return { ok: false, errorCode: 'HTTP_URL_INVALID' };
  }

  if (parsed.username || parsed.password) return { ok: false, errorCode: 'HTTP_USERINFO_REJECTED' };
  if (parsed.hash) return { ok: false, errorCode: 'HTTP_URL_INVALID' };
  if (parsed.protocol === 'http:' && !testMode) return { ok: false, errorCode: 'HTTP_TLS_REQUIRED' };
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') return { ok: false, errorCode: 'HTTP_SCHEME_NOT_ALLOWED' };

  const hostname = normalizeHostname(parsed.hostname);
  if (isMetadataHost(hostname)) return { ok: false, errorCode: 'HTTP_METADATA_TARGET_REJECTED' };

  if (testMode && parsed.protocol === 'http:' && !LOOPBACK_HOSTS.has(hostname)) {
    return { ok: false, errorCode: 'HTTP_SCHEME_NOT_ALLOWED' };
  }

  if (
    testMode
    && config.tlsMode === 'LOOPBACK_HTTP_TEST'
    && LOOPBACK_HOSTS.has(hostname)
    && parsed.protocol === 'http:'
  ) {
    return { ok: true, hostname };
  }

  const policy = buildFoundationPolicyForProduction(hostname, config, testMode);
  const destinationValidation = validateHttpDestination(url, policy);
  if (!destinationValidation.ok) {
    if (destinationValidation.errors.some((e) => e.includes('METADATA'))) return { ok: false, errorCode: 'HTTP_METADATA_TARGET_REJECTED' };
    if (destinationValidation.errors.some((e) => e.includes('LOCALHOST') || e.includes('LOOPBACK'))) {
      return { ok: false, errorCode: testMode ? 'HTTP_TARGET_NOT_ALLOWLISTED' : 'HTTP_METADATA_TARGET_REJECTED' };
    }
    return { ok: false, errorCode: 'HTTP_TARGET_NOT_ALLOWLISTED' };
  }

  const destination = normalizeHttpDestination(url);
  if (!destination) return { ok: false, errorCode: 'HTTP_URL_INVALID' };
  const ssrf = evaluateSsrfRisk(destination, policy);
  if (!ssrf.ok) {
    if (ssrf.errors.some((e) => e.includes('METADATA'))) return { ok: false, errorCode: 'HTTP_METADATA_TARGET_REJECTED' };
    return { ok: false, errorCode: 'HTTP_TARGET_NOT_ALLOWLISTED' };
  }

  return { ok: true, hostname };
}

export function validatePositiveIntOrZero(value: unknown, cap: number): boolean {
  if (typeof value !== 'number' || !Number.isInteger(value) || value < 0) return false;
  return value <= cap;
}

export function validatePositiveInt(value: unknown, cap: number): boolean {
  if (typeof value !== 'number' || !Number.isInteger(value) || value <= 0) return false;
  return value <= cap;
}

export function validateProductionResourceLimits(limits: HttpProductionResourceLimits): HttpProductionErrorCode | null {
  if (!validatePositiveIntOrZero(limits.maxRedirects, HTTP_PRODUCTION_LIMIT_CAPS.maxRedirects)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.connectTimeoutMs, HTTP_PRODUCTION_LIMIT_CAPS.connectTimeoutMs)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.responseTimeoutMs, HTTP_PRODUCTION_LIMIT_CAPS.responseTimeoutMs)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxResponseBytes, HTTP_PRODUCTION_LIMIT_CAPS.maxResponseBytes)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxHeaderBytes, HTTP_PRODUCTION_LIMIT_CAPS.maxHeaderBytes)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxHeaderCount, HTTP_PRODUCTION_LIMIT_CAPS.maxHeaderCount)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxJsonDepth, HTTP_PRODUCTION_LIMIT_CAPS.maxJsonDepth)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxRecordCount, HTTP_PRODUCTION_LIMIT_CAPS.maxRecordCount)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxFieldCount, HTTP_PRODUCTION_LIMIT_CAPS.maxFieldCount)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxFieldLength, HTTP_PRODUCTION_LIMIT_CAPS.maxFieldLength)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxDnsResults, HTTP_PRODUCTION_LIMIT_CAPS.maxDnsResults)) return 'HTTP_CONFIG_INVALID';
  if (!validatePositiveInt(limits.maxProcessingMilliseconds, HTTP_PRODUCTION_LIMIT_CAPS.maxProcessingMilliseconds)) return 'HTTP_CONFIG_INVALID';
  return null;
}
