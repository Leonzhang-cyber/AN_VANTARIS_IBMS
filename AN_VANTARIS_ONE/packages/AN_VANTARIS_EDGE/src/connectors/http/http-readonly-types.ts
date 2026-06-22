export type HttpRedirectPolicy = 'REJECT' | 'FOLLOW';
export type HttpCredentialMode = 'REFERENCE_ONLY' | 'PLAINTEXT';
export type HttpDnsResolutionMode = 'MODELED_ONLY' | 'REAL';
export type HttpResponseParsingMode = 'FOUNDATION_JSON_CSV';

export type HttpPollingReadOnlyPolicy = {
  readonly schemaVersion: '1.0';
  readonly taskId: 'UFMS-EDGE-C5-02';
  readonly classification: 'CONTROLLED_HTTP_POLLING_READ_ONLY_FOUNDATION';
  readonly allowedSchemes: readonly string[];
  readonly allowedMethods: readonly string[];
  readonly allowedHosts: readonly string[];
  readonly deniedHosts: readonly string[];
  readonly deniedCidrs: readonly string[];
  readonly httpsRequiredForProduction: boolean;
  readonly redirectPolicy: HttpRedirectPolicy;
  readonly maxRedirects: number;
  readonly requestTimeoutMs: number;
  readonly maxRetryAttempts: number;
  readonly retryableStatusCodes: readonly number[];
  readonly retryableErrorClasses: readonly string[];
  readonly backoffBaseMs: number;
  readonly backoffMultiplier: number;
  readonly backoffMaxMs: number;
  readonly maxResponseBytes: number;
  readonly allowedContentTypes: readonly string[];
  readonly credentialMode: HttpCredentialMode;
  readonly plaintextCredentialsAllowed: boolean;
  readonly dnsResolutionMode: HttpDnsResolutionMode;
  readonly networkAccessAllowed: boolean;
  readonly syntheticTransportOnly: boolean;
  readonly writeMethodsAllowed: boolean;
  readonly responseParsingMode: HttpResponseParsingMode;
  readonly jsonAllowObject: boolean;
  readonly jsonAllowArray: boolean;
  readonly jsonAllowScalar: boolean;
  readonly jsonMaxDepth: number;
  readonly csvHeaderRequired: boolean;
  readonly csvDelimiter: ',';
  readonly csvMaxRows: number;
  readonly candidateStatus: 'CONTROLLED_HTTP_POLLING_READ_ONLY_FOUNDATION';
  readonly readinessKey: 'UFMS_EDGE_C5_02_HTTP_POLLING_CONTROLLED_READ_ONLY_FOUNDATION_PASS';
};

export type ValidationResult = {
  readonly ok: boolean;
  readonly errors: readonly string[];
};

export type HttpMethodValidation = ValidationResult & {
  readonly method: string;
};

export type HttpNormalizedDestination = {
  readonly originalUrl: string;
  readonly normalizedUrl: string;
  readonly scheme: string;
  readonly hostname: string;
  readonly port: string;
  readonly path: string;
};

export type HttpDestinationValidation = ValidationResult & {
  readonly destination?: HttpNormalizedDestination;
};

export type SsrfRiskCategory =
  | 'LOCALHOST'
  | 'LOOPBACK'
  | 'PRIVATE_IPV4'
  | 'PRIVATE_IPV6'
  | 'LINK_LOCAL'
  | 'MULTICAST'
  | 'UNSPECIFIED'
  | 'METADATA'
  | 'NON_ALLOWLISTED_HOST'
  | 'EMBEDDED_USERINFO'
  | 'MALFORMED_URL'
  | 'MISSING_HOST'
  | 'INVALID_SCHEME'
  | 'SUSPICIOUS_HOSTNAME'
  | 'IPV4_MAPPED_BYPASS'
  | 'DNS_REBINDING_RISK';

export type SsrfRiskEvaluation = {
  readonly ok: boolean;
  readonly risks: readonly SsrfRiskCategory[];
  readonly errors: readonly string[];
  readonly dnsRebindingModeled: boolean;
};

export type HttpCredentialValidation = ValidationResult & {
  readonly credentialRef?: string;
};

export type HttpResponseMetadata = {
  readonly statusCode: number;
  readonly contentType?: string;
  readonly contentLength?: number;
  readonly bodyBytes: number;
  readonly redirectLocation?: string;
  readonly encoding?: string;
};

export type HttpResponseMetadataValidation = ValidationResult & {
  readonly metadata: HttpResponseMetadata;
};

export type HttpRetryDecision = {
  readonly shouldRetry: boolean;
  readonly attempt: number;
  readonly maxAttempts: number;
  readonly reason?: string;
  readonly exhausted: boolean;
};

export type HttpRetryBackoff = {
  readonly attempt: number;
  readonly delayMs: number;
  readonly clamped: boolean;
};

export type ParsedHttpJsonResponse = {
  readonly kind: 'json';
  readonly records: readonly Record<string, unknown>[];
};

export type ParsedHttpCsvResponse = {
  readonly kind: 'csv';
  readonly headers: readonly string[];
  readonly records: readonly Record<string, string>[];
};

export type ParsedHttpResponse = ParsedHttpJsonResponse | ParsedHttpCsvResponse;

export type HttpSyntheticFixtureRequest = {
  readonly method: string;
  readonly url: string;
  readonly credentialRef?: string;
  readonly headers?: Readonly<Record<string, string>>;
};

export type HttpSyntheticFixtureResponse = {
  readonly statusCode: number;
  readonly headers?: Readonly<Record<string, string>>;
  readonly body?: string;
  readonly simulatedTimeout?: boolean;
  readonly simulatedErrorClass?: string;
};

export type HttpSyntheticFixture = {
  readonly request: HttpSyntheticFixtureRequest;
  readonly response: HttpSyntheticFixtureResponse;
};

export type HttpSyntheticTransportResult = {
  readonly accepted: boolean;
  readonly transportMode: 'SYNTHETIC_TRANSPORT_ONLY';
  readonly method: string;
  readonly url: string;
  readonly statusCode?: number;
  readonly parsed?: ParsedHttpResponse;
  readonly retryDecision?: HttpRetryDecision;
  readonly backoffMs?: number;
  readonly redirectRejected: boolean;
  readonly errors: readonly string[];
};

export type HttpPollingAcceptanceResult =
  | 'HTTP_POLLING_READ_ONLY_FOUNDATION_ACCEPTED'
  | 'HTTP_POLLING_READ_ONLY_FOUNDATION_REJECTED';
