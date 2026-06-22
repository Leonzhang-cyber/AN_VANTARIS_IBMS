// AUTO-GENERATED FROM AN_VANTARIS_Contracts. DO NOT EDIT.

export const ZONE_1_EDGE = 'ZONE_1_EDGE' as const;
export const ZONE_2_LINK = 'ZONE_2_LINK' as const;
export const ZONE_3_CORE = 'ZONE_3_CORE' as const;

export const SECURITY_ZONES = {
  ZONE_1_EDGE,
  ZONE_2_LINK,
  ZONE_3_CORE,
} as const;

export class WireZoneViolationError extends Error {
  public constructor(
    public readonly code: string,
    public readonly fromZone: string,
    public readonly toZone: string,
    public readonly eventId?: string,
    message = 'invalid zone transition',
  ) {
    super(message);
  }
}

export function zoneName(zone: string): string {
  return zone;
}

export function assertLinkIngressZoneTransition(
  fromZone: string,
  toZone: string,
  eventId: string | null,
): void {
  if (fromZone !== ZONE_1_EDGE || toZone !== ZONE_2_LINK) {
    throw new WireZoneViolationError('WIRE_ZONE_VIOLATION', fromZone, toZone, eventId ?? undefined);
  }
}
