import http from 'node:http';
import https from 'node:https';
import { lookup as dnsLookup } from 'node:dns/promises';
import { type IncomingMessage, type RequestOptions } from 'node:http';
import { type RequestOptions as HttpsRequestOptions } from 'node:https';

import type {
  HttpProductionAdapterConfig,
  HttpProductionErrorCode,
  HttpProductionReadFailure,
  HttpProductionReadOnlyAdapter,
  HttpProductionReadRequest,
  HttpProductionReadResult,
} from './http-production-adapter.types.js';
import {
  runFoundationPolicyValidation,
  validateAndParseResponseBody,
  validateProductionAdapterConfig,
  validateProductionMethod,
  validateResolvedHeaders,
} from './http-production-response-normalizer.js';
import {
  createHostReferenceHash,
  createTargetReferenceId,
  resolveProductionTargetUrl,
  validateAllResolvedIps,
  validateProductionTargetUrl,
} from './http-production-target-policy.js';

const REDIRECT_STATUSES = new Set([301, 302, 303, 307, 308]);

type HttpExecutionResult = {
  statusCode: number;
  headers: Record<string, string>;
  body: string;
};

function failure(
  errorCode: HttpProductionErrorCode,
  config: HttpProductionAdapterConfig,
  hostname?: string,
  extra?: Partial<HttpProductionReadFailure>,
): HttpProductionReadFailure {
  return {
    ok: false,
    errorCode,
    targetReferenceId: createTargetReferenceId(config.targetReferenceId, config.relativePath),
    hostReferenceHash: hostname ? createHostReferenceHash(hostname) : undefined,
    ...extra,
  };
}

function normalizeHeaderBlock(rawHeaders: IncomingMessage['headers']): Record<string, string> {
  const headers: Record<string, string> = {};
  for (const [key, value] of Object.entries(rawHeaders)) {
    if (Array.isArray(value)) headers[key.toLowerCase()] = value.join(',');
    else if (typeof value === 'string') headers[key.toLowerCase()] = value;
  }
  return headers;
}

async function readBoundedBody(response: IncomingMessage, maxBytes: number): Promise<string> {
  const chunks: Buffer[] = [];
  let total = 0;
  for await (const chunk of response) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    total += buffer.length;
    if (total > maxBytes) {
      response.destroy();
      throw new Error('HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED');
    }
    chunks.push(buffer);
  }
  const combined = Buffer.concat(chunks, total);
  try {
    new TextDecoder('utf-8', { fatal: true }).decode(combined);
  } catch {
    throw new Error('HTTP_ENCODING_INVALID');
  }
  return combined.toString('utf8');
}

async function resolveHostnameIps(
  hostname: string,
  request: HttpProductionReadRequest,
): Promise<{ ok: true; ips: string[] } | { ok: false; errorCode: HttpProductionErrorCode }> {
  const { config, resolveDns, testMode = false } = request;
  if (resolveDns) {
    const injected = resolveDns(hostname);
    if (!injected || injected.length === 0) return { ok: false, errorCode: 'HTTP_DNS_RESOLUTION_FAILED' };
    if (injected.length > config.maxDnsResults) return { ok: false, errorCode: 'HTTP_DNS_RESOLUTION_FAILED' };
    const ipError = validateAllResolvedIps(injected, testMode);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, ips: [...injected] };
  }
  if (testMode) return { ok: false, errorCode: 'HTTP_DNS_RESOLUTION_FAILED' };
  try {
    const results = await dnsLookup(hostname, { all: true, verbatim: true });
    const ips = results.map((entry) => entry.address).slice(0, config.maxDnsResults);
    const ipError = validateAllResolvedIps(ips, testMode);
    if (ipError) return { ok: false, errorCode: ipError };
    return { ok: true, ips };
  } catch {
    return { ok: false, errorCode: 'HTTP_DNS_RESOLUTION_FAILED' };
  }
}

function buildRequestHeaders(request: HttpProductionReadRequest, hostname: string): { ok: true; headers: Record<string, string> } | { ok: false; errorCode: HttpProductionErrorCode } {
  const { config, resolveHeaders, resolveCredential } = request;
  const headers: Record<string, string> = {
    accept: config.expectedContentTypes.join(', '),
    'user-agent': 'vantaris-edge-http-production-readonly/1.0',
  };

  if (resolveCredential && config.credentialReferenceId) {
    const credentialHeaders = resolveCredential(config.credentialReferenceId);
    if (!credentialHeaders) return { ok: false, errorCode: 'HTTP_CREDENTIAL_REFERENCE_FAILED' };
    Object.assign(headers, credentialHeaders);
  }

  if (config.headerReferenceIds && resolveHeaders) {
    for (const ref of config.headerReferenceIds) {
      const resolved = resolveHeaders(ref);
      if (!resolved) return { ok: false, errorCode: 'HTTP_CREDENTIAL_REFERENCE_FAILED' };
      Object.assign(headers, resolved);
    }
  }

  const headerError = validateResolvedHeaders(headers, config);
  if (headerError) return { ok: false, errorCode: headerError };
  return { ok: true, headers };
}

function executeHttpRequest(
  url: string,
  method: string,
  headers: Record<string, string>,
  config: HttpProductionAdapterConfig,
  signal: AbortSignal,
): Promise<HttpExecutionResult> {
  return new Promise((resolve, reject) => {
    let parsed: URL;
    try {
      parsed = new URL(url);
    } catch {
      reject(new Error('HTTP_URL_INVALID'));
      return;
    }

    const isHttps = parsed.protocol === 'https:';
    const requestFn = isHttps ? https.request : http.request;
    const options: RequestOptions & HttpsRequestOptions = {
      protocol: parsed.protocol,
      hostname: parsed.hostname,
      port: parsed.port || (isHttps ? 443 : 80),
      path: `${parsed.pathname}${parsed.search}`,
      method,
      headers,
      signal,
      timeout: config.connectTimeoutMs,
      rejectUnauthorized: true,
      minVersion: 'TLSv1.2',
      servername: parsed.hostname,
    };

    const req = requestFn(options, (res) => {
      const statusCode = res.statusCode ?? 0;
      const responseHeaders = normalizeHeaderBlock(res.headers);
      if (method === 'HEAD' || statusCode === 204 || statusCode === 304) {
        res.resume();
        resolve({ statusCode, headers: responseHeaders, body: '' });
        return;
      }
      readBoundedBody(res, config.maxResponseBytes)
        .then((body) => resolve({ statusCode, headers: responseHeaders, body }))
        .catch(reject);
    });

    req.on('timeout', () => {
      req.destroy(new Error('HTTP_CONNECT_TIMEOUT'));
    });
    req.on('error', (error) => reject(error));
    req.end();
  });
}

async function performRequestOnce(
  request: HttpProductionReadRequest,
  url: string,
  hostname: string,
  method: string,
  includeBody: boolean,
): Promise<HttpProductionReadResult | { redirect: string; hop: number }> {
  const { config } = request;
  const headerResult = buildRequestHeaders(request, hostname);
  if (!headerResult.ok) return failure(headerResult.errorCode, config, hostname);

  const controller = new AbortController();
  const overallTimer = setTimeout(() => controller.abort(), config.maxProcessingMilliseconds);
  const responseTimer = setTimeout(() => controller.abort(), config.responseTimeoutMs);

  try {
    if (process.env.NODE_TLS_REJECT_UNAUTHORIZED === '0') {
      return failure('HTTP_TLS_VALIDATION_FAILED', config, hostname);
    }

    const execution = await executeHttpRequest(url, method, headerResult.headers, config, controller.signal);
    clearTimeout(responseTimer);

    if (REDIRECT_STATUSES.has(execution.statusCode)) {
      const location = execution.headers.location;
      if (!location) return failure('HTTP_REDIRECT_TARGET_REJECTED', config, hostname, { redirectHop: 1 });
      if (config.maxRedirects <= 0) return failure('HTTP_REDIRECT_NOT_ALLOWED', config, hostname, { redirectHop: 1 });
      let nextUrl: string;
      try {
        nextUrl = new URL(location, url).toString();
      } catch {
        return failure('HTTP_REDIRECT_TARGET_REJECTED', config, hostname, { redirectHop: 1 });
      }
      const nextParsed = new URL(nextUrl);
      if (nextParsed.protocol === 'http:' && new URL(url).protocol === 'https:') {
        return failure('HTTP_REDIRECT_TARGET_REJECTED', config, hostname, { redirectHop: 1 });
      }
      return { redirect: nextUrl, hop: 1 };
    }

    if (execution.statusCode < 200 || execution.statusCode >= 300) {
      return failure('HTTP_STATUS_REJECTED', config, hostname);
    }

    if (!includeBody || method === 'HEAD') {
      return {
        ok: true,
        targetReferenceId: createTargetReferenceId(config.targetReferenceId, config.relativePath),
        hostReferenceHash: createHostReferenceHash(hostname),
        method: 'HEAD',
        statusCode: execution.statusCode,
        contentType: execution.headers['content-type'],
        foundationAccepted: true,
      };
    }

    const metadata = {
      statusCode: execution.statusCode,
      contentType: execution.headers['content-type'],
      contentLength: Number(execution.headers['content-length'] ?? execution.body.length),
      bodyBytes: Buffer.byteLength(execution.body, 'utf8'),
      encoding: execution.headers['content-encoding'],
    };

    if (metadata.encoding && metadata.encoding !== 'identity') {
      return failure('HTTP_CONTENT_TYPE_NOT_ALLOWED', config, hostname);
    }

    const parsed = validateAndParseResponseBody(
      execution.body,
      metadata,
      hostname,
      config,
      request.testMode === true,
    );
    if (!parsed.ok) return failure(parsed.errorCode, config, hostname, { lineNumber: parsed.lineNumber });

    return {
      ok: true,
      targetReferenceId: createTargetReferenceId(config.targetReferenceId, config.relativePath),
      hostReferenceHash: createHostReferenceHash(hostname),
      method: 'GET',
      statusCode: execution.statusCode,
      contentType: metadata.contentType,
      recordCount: parsed.records.length,
      records: parsed.records,
      foundationAccepted: true,
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : 'HTTP_REQUEST_FAILED';
    if (message.includes('HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED')) return failure('HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED', config, hostname);
    if (message.includes('HTTP_ENCODING_INVALID')) return failure('HTTP_ENCODING_INVALID', config, hostname);
    if (message.includes('HTTP_CONNECT_TIMEOUT') || message === 'AbortError') {
      return failure(controller.signal.aborted ? 'HTTP_RESPONSE_TIMEOUT' : 'HTTP_CONNECT_TIMEOUT', config, hostname);
    }
    if (message.includes('CERT') || message.includes('TLS') || message.includes('self signed')) {
      return failure('HTTP_TLS_VALIDATION_FAILED', config, hostname);
    }
    return failure('HTTP_REQUEST_FAILED', config, hostname);
  } finally {
    clearTimeout(overallTimer);
    clearTimeout(responseTimer);
  }
}

async function executeControlledRequest(
  request: HttpProductionReadRequest,
  includeBody: boolean,
): Promise<HttpProductionReadResult> {
  const { config, resolveTarget, testMode = false } = request;
  const configError = validateProductionAdapterConfig(config);
  if (configError) return failure(configError, config);

  const methodError = validateProductionMethod(config.method);
  if (methodError) return failure(methodError, config);

  const baseUrl = resolveTarget(config.targetReferenceId);
  if (!baseUrl) return failure('HTTP_TARGET_REFERENCE_NOT_FOUND', config);

  const resolved = resolveProductionTargetUrl(baseUrl, config);
  if (!resolved.ok) return failure(resolved.errorCode, config);

  const targetValidation = validateProductionTargetUrl(resolved.url, config, testMode);
  if (!targetValidation.ok) return failure(targetValidation.errorCode, config);

  const foundationError = runFoundationPolicyValidation(targetValidation.hostname, config, testMode);
  if (foundationError) return failure(foundationError, config, targetValidation.hostname);

  const dnsResult = await resolveHostnameIps(targetValidation.hostname, request);
  if (!dnsResult.ok) return failure(dnsResult.errorCode, config, targetValidation.hostname);

  let currentUrl = resolved.url;
  let hop = 0;
  const visited = new Set<string>();

  while (true) {
    if (visited.has(currentUrl)) return failure('HTTP_REDIRECT_LIMIT_EXCEEDED', config, targetValidation.hostname, { redirectHop: hop });
    visited.add(currentUrl);

    const hopValidation = validateProductionTargetUrl(currentUrl, config, testMode);
    if (!hopValidation.ok) return failure('HTTP_REDIRECT_TARGET_REJECTED', config, targetValidation.hostname, { redirectHop: hop });

    const hopDns = await resolveHostnameIps(hopValidation.hostname, request);
    if (!hopDns.ok) return failure(hopDns.errorCode, config, hopValidation.hostname, { redirectHop: hop });

    const result = await performRequestOnce(
      request,
      currentUrl,
      hopValidation.hostname,
      config.method,
      includeBody,
    );

    if ('redirect' in result) {
      hop += 1;
      if (hop > config.maxRedirects) return failure('HTTP_REDIRECT_LIMIT_EXCEEDED', config, hopValidation.hostname, { redirectHop: hop });
      currentUrl = result.redirect;
      continue;
    }

    if (!result.ok) return { ...result, redirectHop: hop || undefined };
    return result;
  }
}

export function createHttpProductionReadOnlyAdapter(): HttpProductionReadOnlyAdapter {
  return {
    readOnce: async (request: HttpProductionReadRequest): Promise<HttpProductionReadResult> => {
      if (request.config.method !== 'GET') return failure('HTTP_METHOD_NOT_ALLOWED', request.config);
      return executeControlledRequest({ ...request, config: { ...request.config, method: 'GET' } }, true);
    },
    headOnce: async (request: HttpProductionReadRequest): Promise<HttpProductionReadResult> => {
      if (request.config.method !== 'HEAD') {
        return executeControlledRequest({ ...request, config: { ...request.config, method: 'HEAD' } }, false);
      }
      return executeControlledRequest(request, false);
    },
  };
}

export const httpProductionReadOnlyAdapter: HttpProductionReadOnlyAdapter = createHttpProductionReadOnlyAdapter();
