import type {
  OpcUaEndpointRiskEvaluation,
  OpcUaEndpointValidation,
  OpcUaNormalizedEndpoint,
  OpcUaReadOnlyPolicy,
} from './opcua-readonly-types.js';

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
  if (parts.length !== 4) return null;
  return parts;
}

function parseHexIpv4(value: string): number[] | null {
  if (!/^0x[0-9a-f]+$/i.test(value)) return null;
  return parseDecimalIpv4(String(parseInt(value, 16)));
}

function parseDottedIpv4(hostname: string): number[] | null {
  if (!/^(\d{1,3}|0x[0-9a-f]+|0[0-7]+)(\.(\d{1,3}|0x[0-9a-f]+|0[0-7]+)){0,3}$/i.test(hostname)) return null;
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
  return all.map((part) => parseInt(part, 16));
}

function parseHostnameAsIp(hostname: string): { version: 4 | 6; parts: number[] } | null {
  for (const parser of [parseDecimalIpv4, parseOctalIpv4, parseHexIpv4, parseDottedIpv4]) {
    const parsed = parser(hostname);
    if (parsed) return { version: 4, parts: parsed };
  }
  const v6 = parseIpv6(hostname);
  if (v6) return { version: 6, parts: v6 };
  return null;
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

function parseOpcTcpUrl(url: string): OpcUaNormalizedEndpoint | null {
  if (!url || typeof url !== 'string') return null;
  if (/[\x00-\x1f\x7f]/.test(url)) return null;
  const trimmed = url.trim();
  const match = /^([a-z][a-z0-9+.-]*):\/\/([^/?#]*)(\/[^?#]*)?(?:\?[^#]*)?(?:#.*)?$/i.exec(trimmed);
  if (!match) return null;

  const scheme = match[1].toLowerCase();
  const authority = match[2] ?? '';
  const path = match[3] ?? '';

  if (authority.includes('@')) return null;
  if (trimmed.includes('?') || trimmed.includes('#')) return null;

  let hostname = authority;
  let port = 4840;
  if (authority.startsWith('[')) {
    const closing = authority.indexOf(']');
    if (closing < 0) return null;
    hostname = authority.slice(1, closing);
    const rest = authority.slice(closing + 1);
    if (rest.startsWith(':')) {
      port = Number(rest.slice(1));
    } else if (rest.length > 0) {
      return null;
    }
  } else if (authority.includes(':')) {
    const lastColon = authority.lastIndexOf(':');
    port = Number(authority.slice(lastColon + 1));
    hostname = authority.slice(0, lastColon);
  }

  hostname = normalizeHostname(hostname.replace(/^\[|\]$/g, ''));
  if (!hostname || !Number.isInteger(port) || port <= 0 || port > 65535) return null;

  return {
    originalUrl: url,
    scheme,
    hostname,
    port,
    path: path === '/' ? '' : path,
  };
}

export function normalizeOpcUaEndpoint(
  url: string,
  policy: OpcUaReadOnlyPolicy,
): OpcUaNormalizedEndpoint | null {
  const parsed = parseOpcTcpUrl(url);
  if (!parsed) return null;
  if (parsed.scheme !== 'opc.tcp') return null;
  if (parsed.path && parsed.path !== '') return null;
  if (!policy.allowedPorts.includes(parsed.port)) return parsed;
  return parsed;
}

export function evaluateOpcUaEndpointRisk(
  endpoint: OpcUaNormalizedEndpoint,
  policy: OpcUaReadOnlyPolicy,
  flags?: { endpointDiscovery?: boolean },
): OpcUaEndpointRiskEvaluation {
  const risks: string[] = [];
  const errors: string[] = [];

  if (endpoint.scheme !== 'opc.tcp') {
    errors.push('OPCUA_ENDPOINT_SCHEME_NOT_ALLOWED');
    return { ok: false, risks, endpoint, errors: [...new Set(errors)] };
  }

  if (endpoint.path && endpoint.path !== '') {
    errors.push('OPCUA_ENDPOINT_INVALID');
  }

  if (!policy.allowedPorts.includes(endpoint.port)) {
    risks.push('NON_ALLOWLISTED_PORT');
    errors.push('OPCUA_ENDPOINT_PORT_NOT_ALLOWED');
  }

  if (flags?.endpointDiscovery && policy.endpointDiscoveryMode === 'MODELED_ONLY') {
    risks.push('ENDPOINT_DISCOVERY');
    errors.push('OPCUA_ENDPOINT_DISCOVERY_DISABLED');
  }

  if (endpoint.hostname === 'localhost' || endpoint.hostname === 'metadata.google.internal') {
    risks.push('LOCALHOST');
    errors.push('OPCUA_ENDPOINT_RISK_REJECTED');
  }

  const parsedIp = parseHostnameAsIp(endpoint.hostname);
  if (parsedIp) {
    const categories = parsedIp.version === 4 ? classifyIpv4(parsedIp.parts) : classifyIpv6(parsedIp.parts);
    for (const category of categories) {
      risks.push(category);
      errors.push('OPCUA_ENDPOINT_RISK_REJECTED');
    }
  } else {
    const allowedHosts = policy.allowedHosts.map((h) => normalizeHostname(h));
    if (!allowedHosts.includes(endpoint.hostname)) {
      risks.push('NON_ALLOWLISTED');
      errors.push('OPCUA_ENDPOINT_NOT_ALLOWED');
    }
  }

  const canonical = `opc.tcp://${endpoint.hostname}:${endpoint.port}`;
  const allowedUrls = policy.allowedEndpointUrls.map((u) => u.trim().toLowerCase());
  if (!allowedUrls.includes(canonical)) {
    risks.push('NON_ALLOWLISTED_URL');
    errors.push('OPCUA_ENDPOINT_NOT_ALLOWED');
  }

  return {
    ok: errors.length === 0,
    risks: [...new Set(risks)],
    endpoint,
    errors: [...new Set(errors)],
  };
}

export function validateOpcUaEndpoint(
  url: string,
  policy: OpcUaReadOnlyPolicy,
  flags?: { endpointDiscovery?: boolean },
): OpcUaEndpointValidation {
  if (!url || typeof url !== 'string') {
    return { ok: false, errors: ['OPCUA_ENDPOINT_INVALID'] };
  }
  if (/[\x00-\x1f\x7f]/.test(url)) {
    return { ok: false, errors: ['OPCUA_ENDPOINT_INVALID'] };
  }
  if (url.includes('@')) {
    return { ok: false, errors: ['OPCUA_ENDPOINT_INVALID'] };
  }
  if (url.includes('?') || url.includes('#')) {
    return { ok: false, errors: ['OPCUA_ENDPOINT_INVALID'] };
  }

  const parsed = parseOpcTcpUrl(url);
  if (!parsed) {
    return { ok: false, errors: ['OPCUA_ENDPOINT_INVALID'] };
  }
  if (parsed.scheme !== 'opc.tcp') {
    return { ok: false, errors: ['OPCUA_ENDPOINT_SCHEME_NOT_ALLOWED'] };
  }

  const risk = evaluateOpcUaEndpointRisk(parsed, policy, flags);
  return { ok: risk.ok, endpoint: parsed, errors: risk.errors };
}
