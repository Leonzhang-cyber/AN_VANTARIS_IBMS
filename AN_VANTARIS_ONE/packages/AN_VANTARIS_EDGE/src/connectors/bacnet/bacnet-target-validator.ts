import type {
  BacnetIpReadOnlyPolicy,
  BacnetNormalizedTarget,
  BacnetTargetRiskEvaluation,
  BacnetTargetValidation,
} from './bacnet-readonly-types.js';

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
  if (parts.join('.') === '255.255.255.255') risks.push('BROADCAST');
  if (parts[3] === 255 && parts[0] >= 1) risks.push('DIRECTED_BROADCAST');
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

export function normalizeBacnetTarget(
  target: string,
  port: number | undefined,
  policy: BacnetIpReadOnlyPolicy,
): BacnetNormalizedTarget | null {
  if (!target || typeof target !== 'string') return null;
  if (/[\x00-\x1f\x7f]/.test(target)) return null;
  if (target.includes('@') || /^[a-z][a-z0-9+.-]*:\/\//i.test(target) || target.includes('/') || target.includes('?')) {
    return null;
  }

  let hostname = target.trim();
  let resolvedPort = port ?? policy.allowedPorts[0] ?? 47808;
  if (hostname.includes(':') && !hostname.startsWith('[')) {
    const lastColon = hostname.lastIndexOf(':');
    const maybePort = Number(hostname.slice(lastColon + 1));
    if (Number.isInteger(maybePort) && maybePort > 0 && maybePort <= 65535) {
      resolvedPort = maybePort;
      hostname = hostname.slice(0, lastColon);
    }
  }
  hostname = normalizeHostname(hostname.replace(/^\[|\]$/g, ''));
  if (!hostname) return null;
  if (hostname === 'bbmd' || hostname.includes('bbmd')) return null;
  if (!(resolvedPort > 0 && resolvedPort <= 65535)) return null;

  return { originalTarget: target, hostname, port: resolvedPort };
}

export function evaluateBacnetTargetRisk(
  normalized: BacnetNormalizedTarget,
  policy: BacnetIpReadOnlyPolicy,
  flags?: { broadcast?: boolean; bbmd?: boolean; foreignDeviceRegistration?: boolean },
): BacnetTargetRiskEvaluation {
  const risks: string[] = [];
  const errors: string[] = [];

  if (!policy.allowedPorts.includes(normalized.port)) {
    risks.push('NON_ALLOWLISTED_PORT');
    errors.push('BACNET_PORT_NOT_ALLOWED');
  }

  if (flags?.broadcast && !policy.broadcastAllowed) {
    risks.push('BROADCAST');
    errors.push('BACNET_BROADCAST_DISABLED');
  }

  if (flags?.bbmd && !policy.bbmdAllowed) {
    risks.push('BBMD');
    errors.push('BACNET_BBMD_DISABLED');
  }

  if (flags?.foreignDeviceRegistration && !policy.foreignDeviceRegistrationAllowed) {
    risks.push('FDR');
    errors.push('BACNET_FDR_DISABLED');
  }

  const denied = new Set(policy.deniedTargets.map((t) => normalizeHostname(t)));
  if (denied.has(normalized.hostname) || normalized.hostname === 'localhost') {
    risks.push('LOCALHOST');
    errors.push('BACNET_TARGET_LOCALHOST_REJECTED');
  }
  if (normalized.hostname === 'metadata.google.internal') {
    risks.push('METADATA');
    errors.push('BACNET_TARGET_METADATA_REJECTED');
  }

  const parsedIp = parseHostnameAsIp(normalized.hostname);
  if (parsedIp) {
    const categories = parsedIp.version === 4 ? classifyIpv4(parsedIp.parts) : classifyIpv6(parsedIp.parts);
    for (const category of categories) {
      risks.push(category);
      errors.push(`BACNET_TARGET_${category}_REJECTED`);
    }
  } else {
    const allowed = policy.allowedTargets.map((t) => normalizeHostname(t));
    if (!allowed.includes(normalized.hostname)) {
      risks.push('NON_ALLOWLISTED');
      errors.push('BACNET_TARGET_NOT_ALLOWLISTED');
    }
  }

  return {
    ok: errors.length === 0,
    risks: [...new Set(risks)],
    target: normalized,
    errors: [...new Set(errors)],
  };
}

export function validateBacnetTarget(
  target: string,
  port: number | undefined,
  policy: BacnetIpReadOnlyPolicy,
  flags?: { broadcast?: boolean; bbmd?: boolean; foreignDeviceRegistration?: boolean },
): BacnetTargetValidation {
  if (target.includes('@') || /^[a-z][a-z0-9+.-]*:\/\//i.test(target)) {
    return { ok: false, errors: ['BACNET_TARGET_MALFORMED'] };
  }
  const normalized = normalizeBacnetTarget(target, port, policy);
  if (!normalized) return { ok: false, errors: ['BACNET_TARGET_MALFORMED'] };
  const risk = evaluateBacnetTargetRisk(normalized, policy, flags);
  return { ok: risk.ok, target: normalized, errors: risk.errors };
}

export function validateBacnetCredentialModel(input: {
  credentialRef?: string;
  username?: string;
  password?: string;
  token?: string;
}): { ok: boolean; credentialRef?: string; errors: string[] } {
  const errors: string[] = [];
  if (input.username || input.password || input.token) errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
  if (input.credentialRef && !/^secret:\/\/edge\/bacnet\/.+/.test(input.credentialRef)) {
    errors.push('PLAINTEXT_CREDENTIAL_PROHIBITED');
  }
  return { ok: errors.length === 0, credentialRef: input.credentialRef, errors };
}
