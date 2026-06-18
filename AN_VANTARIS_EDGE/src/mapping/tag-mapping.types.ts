export type UnmappedPolicy = "store_raw" | "drop" | "quarantine";

export interface TagMappingRule {
  connectorId: string;
  sourceTag: string;
  targetPointCode: string;
  unmappedPolicy: UnmappedPolicy;
}
