export type HttpProductionAdapterMode = 'PRODUCTION_HTTP_READONLY';

export type HttpProductionMethod = 'GET' | 'HEAD';

export type HttpProductionTlsMode = 'REQUIRED' | 'LOOPBACK_HTTP_TEST';

export type HttpProductionDnsMode = 'VALIDATED_RESOLVER' | 'INJECTED_TEST';

export type HttpProductionFormulaPrefixPolicy = 'REJECT' | 'MARK';

export type HttpProductionDangerousKeyPolicy = 'REJECT';

export type HttpProductionErrorCode =
  | 'HTTP_CONFIG_INVALID'
  | 'HTTP_METHOD_NOT_ALLOWED'
  | 'HTTP_TARGET_REFERENCE_NOT_FOUND'
  | 'HTTP_URL_INVALID'
  | 'HTTP_SCHEME_NOT_ALLOWED'
  | 'HTTP_USERINFO_REJECTED'
  | 'HTTP_TARGET_NOT_ALLOWLISTED'
  | 'HTTP_DNS_RESOLUTION_FAILED'
  | 'HTTP_DNS_RESULT_REJECTED'
  | 'HTTP_METADATA_TARGET_REJECTED'
  | 'HTTP_REDIRECT_NOT_ALLOWED'
  | 'HTTP_REDIRECT_LIMIT_EXCEEDED'
  | 'HTTP_REDIRECT_TARGET_REJECTED'
  | 'HTTP_TLS_REQUIRED'
  | 'HTTP_TLS_VALIDATION_FAILED'
  | 'HTTP_HEADER_REJECTED'
  | 'HTTP_CREDENTIAL_REFERENCE_FAILED'
  | 'HTTP_CONNECT_TIMEOUT'
  | 'HTTP_RESPONSE_TIMEOUT'
  | 'HTTP_RESPONSE_SIZE_LIMIT_EXCEEDED'
  | 'HTTP_HEADER_LIMIT_EXCEEDED'
  | 'HTTP_CONTENT_TYPE_NOT_ALLOWED'
  | 'HTTP_STATUS_REJECTED'
  | 'HTTP_ENCODING_INVALID'
  | 'HTTP_JSON_INVALID'
  | 'HTTP_NDJSON_INVALID'
  | 'HTTP_CSV_INVALID'
  | 'HTTP_DANGEROUS_KEY_REJECTED'
  | 'HTTP_FORMULA_PREFIX_REJECTED'
  | 'HTTP_FOUNDATION_VALIDATION_FAILED'
  | 'HTTP_REQUEST_FAILED'
  | 'HTTP_ADAPTER_DISABLED';

export type HttpProductionResourceLimits = {
  readonly maxRedirects: number;
  readonly connectTimeoutMs: number;
  readonly responseTimeoutMs: number;
  readonly maxResponseBytes: number;
  readonly maxHeaderBytes: number;
  readonly maxHeaderCount: number;
  readonly maxJsonDepth: number;
  readonly maxRecordCount: number;
  readonly maxFieldCount: number;
  readonly maxFieldLength: number;
  readonly maxDnsResults: number;
  readonly maxProcessingMilliseconds: number;
};

export type HttpProductionAdapterConfig = {
  readonly adapterMode: HttpProductionAdapterMode;
  readonly enabled: boolean;
  readonly targetReferenceId: string;
  readonly method: HttpProductionMethod;
  readonly relativePath: string;
  readonly queryParameters?: Readonly<Record<string, string>>;
  readonly headerReferenceIds?: readonly string[];
  readonly credentialReferenceId?: string;
  readonly certificateReferenceId?: string;
  readonly expectedContentTypes: readonly string[];
  readonly tlsMode: HttpProductionTlsMode;
  readonly dnsMode: HttpProductionDnsMode;
  readonly formulaPrefixPolicy: HttpProductionFormulaPrefixPolicy;
  readonly dangerousKeyPolicy: HttpProductionDangerousKeyPolicy;
} & HttpProductionResourceLimits;

export type HttpProductionTargetResolver = (targetReferenceId: string) => string | undefined;

export type HttpProductionHeaderResolver = (headerReferenceId: string) => Readonly<Record<string, string>> | undefined;

export type HttpProductionCredentialResolver = (credentialReferenceId: string) => Readonly<Record<string, string>> | undefined;

export type HttpProductionDnsResolver = (hostname: string) => readonly string[] | undefined;

export type HttpProductionReadRequest = {
  readonly config: HttpProductionAdapterConfig;
  readonly resolveTarget: HttpProductionTargetResolver;
  readonly resolveHeaders?: HttpProductionHeaderResolver;
  readonly resolveCredential?: HttpProductionCredentialResolver;
  readonly resolveDns?: HttpProductionDnsResolver;
  readonly testMode?: boolean;
};

export type HttpProductionNormalizedRecord = {
  readonly fields: Readonly<Record<string, string>>;
};

export type HttpProductionReadSuccess = {
  readonly ok: true;
  readonly targetReferenceId: string;
  readonly hostReferenceHash: string;
  readonly method: HttpProductionMethod;
  readonly statusCode: number;
  readonly contentType?: string;
  readonly recordCount: number;
  readonly records: readonly HttpProductionNormalizedRecord[];
  readonly foundationAccepted: true;
};

export type HttpProductionHeadSuccess = {
  readonly ok: true;
  readonly targetReferenceId: string;
  readonly hostReferenceHash: string;
  readonly method: 'HEAD';
  readonly statusCode: number;
  readonly contentType?: string;
  readonly foundationAccepted: true;
};

export type HttpProductionReadFailure = {
  readonly ok: false;
  readonly errorCode: HttpProductionErrorCode;
  readonly targetReferenceId?: string;
  readonly hostReferenceHash?: string;
  readonly lineNumber?: number;
  readonly redirectHop?: number;
};

export type HttpProductionReadResult = HttpProductionReadSuccess | HttpProductionHeadSuccess | HttpProductionReadFailure;

export type HttpProductionReadOnlyAdapter = {
  readonly readOnce: (request: HttpProductionReadRequest) => Promise<HttpProductionReadResult>;
  readonly headOnce: (request: HttpProductionReadRequest) => Promise<HttpProductionReadResult>;
};

export const HTTP_PRODUCTION_LIMIT_CAPS: HttpProductionResourceLimits = {
  maxRedirects: 5,
  connectTimeoutMs: 30_000,
  responseTimeoutMs: 30_000,
  maxResponseBytes: 10_485_760,
  maxHeaderBytes: 65_536,
  maxHeaderCount: 64,
  maxJsonDepth: 32,
  maxRecordCount: 10_000,
  maxFieldCount: 256,
  maxFieldLength: 8_192,
  maxDnsResults: 16,
  maxProcessingMilliseconds: 30_000,
};

export const HTTP_PRODUCTION_ALLOWED_METHODS = ['GET', 'HEAD'] as const;

export const HTTP_PRODUCTION_WRITE_METHODS = [
  'POST',
  'PUT',
  'PATCH',
  'DELETE',
  'CONNECT',
  'TRACE',
  'OPTIONS',
] as const;

export const HTTP_PRODUCTION_DANGEROUS_KEYS = ['__proto__', 'prototype', 'constructor'] as const;

export const HTTP_PRODUCTION_FORMULA_PREFIXES = ['=', '+', '-', '@'] as const;

export const HTTP_PRODUCTION_DENIED_HEADER_NAMES = [
  'host',
  'connection',
  'upgrade',
  'proxy-connection',
  'proxy-authorization',
  'transfer-encoding',
  'te',
  'trailer',
] as const;

export const HTTP_PRODUCTION_METADATA_HOSTS = [
  '169.254.169.254',
  '100.100.100.200',
  'metadata.google.internal',
  'metadata.azure.internal',
  'localhost',
  'localhost.localdomain',
] as const;
