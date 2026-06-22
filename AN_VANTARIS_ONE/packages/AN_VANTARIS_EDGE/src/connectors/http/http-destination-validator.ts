import type {
  HttpCredentialValidation,
  HttpDestinationValidation,
  HttpMethodValidation,
  HttpNormalizedDestination,
  HttpPollingReadOnlyPolicy,
  SsrfRiskEvaluation,
} from './http-readonly-types.js';

const WRITE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE', 'CONNECT', 'TRACE', 'OPTIONS', 'HEAD']);

type ParsedIp = {
  readonly version: 4 | 6;
  readonly parts: readonly number[];
};

function normalizeHostname(hostname: string): string {
  return hostname.trim().toLowerCase().replace(/\.$/, '');
}

function parseDecimalIpv4(value: string): number[] | null {
  if (!/^\d+$/.test(value)) return null;
  const num = Number(value);
  if (!Number.isInteger(num) || num < 0 || num > 4294967295) return null;
  return [(num >>> 24) & 255, (num >>> 16) & 255, (num >>> 8) & 255, num & 255];
}

function parseOctalIpv4(value: string): number[] | null {
  if (!/^0[0-7]+(\.[0-7]+)*$/.test(value)) return null;
  const parts = value.split('.').map((part) => parseInt(part, 8));
  if (parts.some((part) => part < 0 || part > 255)) return null;
  while (parts.length < 4) parts.unshift(0);
  if (parts.length > 4) return null;
  return parts;
}

function parseHexIpv4(value: string): number[] | null {
  if (!/^0x[0-9a-f]+$/i.test(value)) return null;
  return parseDecimalIpv4(String(parseInt(value, 16)));
}

function parseDottedIpv4(hostname: string): number[] | null {
  if (!/^(\d{1,3}|0x[0-9a-f]+|0[0-7]+)(\.(\d{1,3}|0x[0-9a-f]+|0[0-7]+)){0,3}$/i.test(hostname)) {
    return null;
  }
  const parts: number[] = [];
  for (const token of hostname.split('.')) {
    if (/^0x/i.test(token)) {
      const hex = parseInt(token, 16);
      if (hex < 0 || hex > 255) return null;
      parts.push(hex);
      continue;
    }
    if (/^0[0-7]+$/.test(token)) {
      const oct = parseInt(token, 8);
      if (oct < 0 || oct > 255) return null;
      parts.push(oct);
      continue;
    }
    const dec = Number(token);
    if (!Number.isInteger(dec) || dec < 0 || dec > 255) return null;
    parts.push(dec);
  }
  while (parts.length < 4) parts.unshift(0);
  if (parts.length !== 4) return null;
  return parts;
}

function parseIpv6(hostname: string): number[] | null {
  const normalized = hostname.toLowerCase();
  if (!normalized.includes(':')) return null;
  if (normalized.includes('::ffff:')) {
    const suffix = normalized.split('::ffff:')[1];
    if (suffix && /^(\d{1,3}\.){3}\d{1,3}$/.test(suffix)) {
      const v4 = parseDottedIpv4(suffix);
      if (v4) return [0, 0, 0, 0, 0, 0xffff, (v4[0] << 8) | v4[1], (v4[2] << 8) | v4[3]];
    }
  }
  const [head, tail = ''] = normalized.includes('::') ? normalized.split('::') : [normalized, ''];
  const headParts = head ? head.split(':').filter(Boolean) : [];
  const tailParts = tail ? tail.split(':').filter(Boolean) : [];
  const missing = 8 - (headParts.length + tailParts.length);
  if (missing < 0) return null;
  const all = [...headParts, ...Array(missing).fill('0'), ...tailParts];
  if (all.length !== 8) return null;
  const parts: number[] = [];
  for (const part of all) {
    if (!/^[0-9a-f]{1,4}$/.test(part)) return null;
    parts.push(parseInt(part, 16));
  }
  return parts;
}

function parseHostnameAsIp(hostname: string): ParsedIp | null {
  const decimal = parseDecimalIpv4(hostname);
  if (decimal) return { version: 4, parts: decimal };
  const octal = parseOctalIpv4(hostname);
  if (octal) return { version: 4, parts: octal };
  const hex = parseHexIpv4(hostname);
  if (hex) return { version: 4, parts: hex };
  const dotted = parseDottedIpv4(hostname);
  if (dotted) return { version: 4, parts: dotted };
  const v6 = parseIpv6(hostname);
  if (v6) return { version: 6, parts: v6 };
  return null;
}

function ipv4ToNumber(parts: readonly number[]): number {
  return ((parts[0] << 24) >>> 0) + (parts[1] << 16) + (parts[2] << 8) + parts[3];
}

function isIpv4InCidr(parts: readonly number[], cidr: string): boolean {
  const [network, prefixRaw] = cidr.split('/');
  const prefix = Number(prefixRaw);
  const networkParts = parseDottedIpv4(network);
  if (!networkParts || !Number.isInteger(prefix) || prefix < 0 || prefix > 32) return false;
  const mask = prefix === 0 ? 0 : (~0 << (32 - prefix)) >>> 0;
  return (ipv4ToNumber(parts) & mask) === (ipv4ToNumber(networkParts) & mask);
}

function isIpv6InCidr(parts: readonly number[], cidr: string): boolean {
  const [network, prefixRaw] = cidr.split('/');
  const prefix = Number(prefixRaw);
  const networkParts = parseIpv6(network);
  if (!networkParts || !Number.isInteger(prefix) || prefix < 0 || prefix > 128) return false;
  const fullBits = [...parts.map((p) => p.toString(16).padStart(4, '0')).join('')];
  const netBits = [...networkParts.map((p) => p.toString(16).padStart(4, '0')).join('')];
  return fullBits.join('').slice(0, Math.floor(prefix / 4)) === netBits.join('').slice(0, Math.floor(prefix / 4));
}

function classifyIpv4(parts: readonly number[]): string[] {
  const risks: string[] = [];
  if (parts.every((p) => p === 0)) risks.push('UNSPECIFIED');
  if (parts[0] === 127) risks.push('LOOPBACK');
  if (parts[0] === 10 || (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) || (parts[0] === 192 && parts[1] === 168)) {
    risks.push('PRIVATE_IPV4');
  }
  if (parts[0] === 169 && parts[1] === 254) risks.push('LINK_LOCAL');
  if (parts[0] >= 224 && parts[0] <= 239) risks.push('MULTICAST');
  if (parts[0] === 127 || parts.join('.') === '0.0.0.0') risks.push('LOCALHOST');
  if (parts.join('.') === '169.254.169.254') risks.push('METADATA');
  return risks;
}

function classifyIpv6(parts: readonly number[]): string[] {
  const risks: string[] = [];
  if (parts.every((p) => p === 0)) risks.push('UNSPECIFIED');
  if (parts.every((p, i) => (i === 7 ? p === 1 : p === 0))) risks.push('LOOPBACK');
  if ((parts[0] & 0xfe00) === 0xfc00) risks.push('PRIVATE_IPV6');
  if ((parts[0] & 0xffc0) === 0xfe80) risks.push('LINK_LOCAL');
  if ((parts[0] & 0xff00) === 0xff00) risks.push('MULTICAST');
  if (parts[0] === 0 && parts[1] === 0 && parts[2] === 0 && parts[3] === 0 && parts[4] === 0 && parts[5] === 0xffff) {
    const mapped = [(parts[6] >> 8) & 255, parts[6] & 255, (parts[7] >> 8) & 255, parts[7] & 255];
    risks.push('IPV4_MAPPED_BYPASS', ...classifyIpv4(mapped));
  }
  return risks;
}

export function normalizeHttpDestination(url: string): HttpNormalizedDestination | null {
  try {
    const parsed = new URL(url);
    const scheme = parsed.protocol.replace(/:$/, '').toLowerCase();
    const hostname = normalizeHostname(parsed.hostname);
    const port = parsed.port || (scheme === 'https' ? '443' : scheme === 'http' ? '80' : '');
    return {
      originalUrl: url,
      normalizedUrl: `${scheme}://${hostname}${port ? `:${port}` : ''}${parsed.pathname}${parsed.search}`,
      scheme,
      hostname,
      port,
      path: `${parsed.pathname}${parsed.search}`,
    };
  } catch {
    return null;
  }
}

export function validateHttpMethod(method: string, policy: HttpPollingReadOnlyPolicy): HttpMethodValidation {
  const normalized = method.trim().toUpperCase();
  const allowed = policy.allowedMethods.map((x) => x.toUpperCase());
  if (WRITE_METHODS.has(normalized) || !allowed.includes(normalized)) {
    return { ok: false, method: normalized, errors: ['HTTP_METHOD_NOT_ALLOWED'] };
  }
  return { ok: true, method: normalized, errors: [] };
}

export function validateHttpCredentialModel(
  input: {
    credentialRef?: string;
    username?: string;
    password?: string;
    bearerToken?: string;
    apiKey?: string;
    authorizationHeader?: string;
    url?: string;
  },
  policy: HttpPollingReadOnlyPolicy,
): HttpCredentialValidation {
  const errors: string[] = [];
  if (input.username || input.password || input.bearerToken || input.apiKey || input.authorizationHeader) {
    errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
  }
  if (input.url) {
    try {
      const parsed = new URL(input.url);
      if (parsed.username || parsed.password) errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
    } catch {
      /* handled elsewhere */
    }
  }
  if (policy.plaintextCredentialsAllowed) errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
  if (policy.credentialMode !== 'REFERENCE_ONLY') errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
  if (input.credentialRef) {
    if (!/^secret:\/\/edge\/http\/.+/.test(input.credentialRef)) {
      errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
    }
  }
  return {
    ok: errors.length === 0,
    credentialRef: input.credentialRef,
    errors,
  };
}

export function evaluateSsrfRisk(
  destination: HttpNormalizedDestination,
  policy: HttpPollingReadOnlyPolicy,
): SsrfRiskEvaluation {
  const risks: string[] = [];
  const errors: string[] = [];
  let dnsRebindingModeled = false;

  if (!policy.allowedSchemes.map((x) => x.toLowerCase()).includes(destination.scheme)) {
    risks.push('INVALID_SCHEME');
    errors.push('INVALID_SCHEME');
  }

  const deniedHostSet = new Set(policy.deniedHosts.map((x) => normalizeHostname(x)));
  if (deniedHostSet.has(destination.hostname) || destination.hostname === 'localhost') {
    risks.push('LOCALHOST');
    errors.push('SSRF_LOCALHOST_REJECTED');
  }
  if (destination.hostname === 'metadata.google.internal') {
    risks.push('METADATA');
    errors.push('SSRF_METADATA_REJECTED');
  }
  if (/[^a-z0-9.-]/.test(destination.hostname) || destination.hostname.includes('..')) {
    risks.push('SUSPICIOUS_HOSTNAME');
    errors.push('SSRF_SUSPICIOUS_HOSTNAME');
  }

  const parsedIp = parseHostnameAsIp(destination.hostname);
  if (parsedIp) {
    const categories = parsedIp.version === 4 ? classifyIpv4(parsedIp.parts) : classifyIpv6(parsedIp.parts);
    for (const category of categories) {
      risks.push(category);
      errors.push(`SSRF_${category}_REJECTED`);
    }
    for (const cidr of policy.deniedCidrs) {
      const inCidr = parsedIp.version === 4 ? isIpv4InCidr(parsedIp.parts, cidr) : isIpv6InCidr(parsedIp.parts, cidr);
      if (inCidr && !errors.includes(`SSRF_CIDR_${cidr}_REJECTED`)) {
        errors.push(`SSRF_CIDR_${cidr}_REJECTED`);
      }
    }
  } else {
    const allowed = policy.allowedHosts.map((x) => normalizeHostname(x));
    if (!allowed.includes(destination.hostname)) {
      risks.push('NON_ALLOWLISTED_HOST');
      errors.push('SSRF_NON_ALLOWLISTED_HOST');
    } else {
      dnsRebindingModeled = true;
      risks.push('DNS_REBINDING_RISK');
    }
  }

  return {
    ok: errors.length === 0,
    risks: [...new Set(risks)] as SsrfRiskEvaluation['risks'],
    errors: [...new Set(errors)],
    dnsRebindingModeled,
  };
}

export function validateHttpDestination(url: string, policy: HttpPollingReadOnlyPolicy): HttpDestinationValidation {
  const errors: string[] = [];
  if (!url || typeof url !== 'string') {
    return { ok: false, errors: ['MALFORMED_URL'] };
  }

  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\/\//.test(url.trim())) {
    return { ok: false, errors: ['MISSING_HOST'] };
  }

  let parsedUrl: URL;
  try {
    parsedUrl = new URL(url);
  } catch {
    return { ok: false, errors: ['MALFORMED_URL'] };
  }

  if (parsedUrl.username || parsedUrl.password) {
    return { ok: false, errors: ['PLAINTEXT_CREDENTIAL_PROHIBITED'] };
  }

  const destination = normalizeHttpDestination(url);
  if (!destination) return { ok: false, errors: ['MALFORMED_URL'] };
  if (!destination.hostname) return { ok: false, errors: ['MISSING_HOST'] };

  const methodCheck = validateHttpCredentialModel({ url }, policy);
  if (!methodCheck.ok) errors.push(...methodCheck.errors);

  const ssrf = evaluateSsrfRisk(destination, policy);
  if (!ssrf.ok) errors.push(...ssrf.errors);

  return {
    ok: errors.length === 0,
    destination,
    errors: [...new Set(errors)],
  };
}
