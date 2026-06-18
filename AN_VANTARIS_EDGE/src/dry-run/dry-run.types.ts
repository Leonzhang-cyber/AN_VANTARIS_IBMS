export interface EdgeDryRunCase {
  caseId: string;
  protocol: string;
  description: string;
}

export interface EdgeDryRunResult {
  caseId: string;
  success: boolean;
  checkedAt: string;
  notes: string[];
}
