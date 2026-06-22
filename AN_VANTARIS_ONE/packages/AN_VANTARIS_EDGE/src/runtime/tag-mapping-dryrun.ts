import type { CanonicalMappedPoint, RawTagSample } from './types.js';

export type UnmappedPolicy = 'store_raw' | 'drop' | 'quarantine';

export interface MappingRule {
  readonly siteId: string;
  readonly assetCode: string;
  readonly deviceCode: string;
  readonly pointCode: string;
  readonly rawTag?: string;
  readonly rawName?: string;
  readonly valueType: CanonicalMappedPoint['valueType'];
  readonly unit: string;
  readonly scale?: number;
  readonly offset?: number;
}

function convert(raw: string, valueType: CanonicalMappedPoint['valueType']): number | string | boolean {
  if (valueType == 'float') return Number.parseFloat(raw);
  if (valueType == 'int') return Number.parseInt(raw, 10);
  if (valueType == 'bool') return raw == '1' || /^true$/i.test(raw);
  return raw;
}

export function mapRawSample(
  sample: RawTagSample,
  rules: readonly MappingRule[],
  unmappedPolicy: UnmappedPolicy,
): CanonicalMappedPoint | null {
  const rule = rules.find((item) => item.rawTag == sample.rawTag) ?? rules.find((item) => item.rawName == sample.rawName);
  if (!rule) {
    if (unmappedPolicy == 'drop') return null;
    return {
      siteId: 'unmapped-site',
      assetCode: 'unmapped-asset',
      deviceCode: 'unmapped-device',
      pointCode: 'unmapped-point',
      value: sample.value,
      valueType: 'string',
      unit: 'raw',
      quality: 'uncertain',
      unmappedPolicyApplied: unmappedPolicy,
    };
  }

  const converted = convert(sample.value, rule.valueType);
  const numeric = typeof converted == 'number' ? converted * (rule.scale ?? 1) + (rule.offset ?? 0) : converted;
  return {
    siteId: rule.siteId,
    assetCode: rule.assetCode,
    deviceCode: rule.deviceCode,
    pointCode: rule.pointCode,
    value: numeric,
    valueType: rule.valueType,
    unit: rule.unit,
    quality: 'good',
  };
}

export function defaultDryRunRules(): readonly MappingRule[] {
  return [
    {
      siteId: 'site-001',
      assetCode: 'AHU-01',
      deviceCode: 'DDC-AHU-01',
      pointCode: 'supply_air_temperature',
      rawTag: '40001',
      rawName: 'AHU01.SAT',
      valueType: 'float',
      unit: 'C',
      scale: 1,
      offset: 0,
    },
  ];
}
