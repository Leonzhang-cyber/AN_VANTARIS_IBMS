# NEXUSAI-GA-R2 Current Branch Integration Plan

## Product Statement

NEXUS AI is advisory/decision/context layer. NEXUS AI is advisory/decision/context layer of VANTARIS ONE. NEXUS AI is not autonomous executor. NEXUS AI must not directly control devices. NEXUS AI must not write DB by default. NEXUS AI must not bypass CODE layer.

NEXUS AI provides triage, recommendation, model-selection, risk-scoring, explanation, and evidence-context assistance. Execution authority remains with CODE, ONE Orchestrator policy gates, governed workflows, and human approval.

## Current Status

- Prior branch NEXUS AI R1-R6 exists in project history/context.
- Current branch integration is pending.
- Current branch has module GA Wave R1 audit freeze only.
- Current branch NEXUS AI code integration: NOT EXECUTED.
- Current branch NEXUS AI production activation: NOT EXECUTED.

## Current Branch Evidence

Discovery files were created under `AN_VANTARIS_ONE/registries/nexusai-ga-r2/`.

- Files discovered: `nexusai-current-branch-files.txt`
- References discovered: `nexusai-current-branch-references.txt`
- Branch inventory: `nexusai-branch-inventory.txt`
- Risk scan: `nexusai-risk-scan.txt`

Evidence summary:

- Local branches include `nexus-ai-orchestrator-r1`, `nexus-ai-orchestrator-r2`, `nexus-ai-orchestrator-r3`, `nexus-ai-orchestrator-r4`, and `nexus-ai-orchestrator-r5-r6`.
- Current branch includes contracts such as `code-to-nexusai.v1.yaml`, `nexus-triage-request.v1.schema.json`, and `nexus-triage-response.v1.schema.json`.
- Current branch includes module-wave and product-design references that classify NEXUS AI as not integrated in the current branch.
- Current branch does not prove active NEXUS AI runtime integration, production activation, external AI API wiring, autonomous execution, or DB write behavior.

## Integration Target Architecture

```text
UConsole
  -> CODE API
  -> NEXUS AI advisory endpoint
  -> recommendation output
  -> CODE / ONE Orchestrator policy decision
  -> human approval before any production activation
```

Context dependencies:

- NEXUS AI receives evidence context from UCDE.
- NEXUS AI receives event and fault context from UFMS and UMMS.
- NEXUS AI produces recommendation output only.
- CODE and ONE Orchestrator decide whether any action is allowed.
- Human approval is required before production activation.

## Required NEXUS AI Engines

- Router engine.
- Policy safety engine.
- Risk scoring engine.
- Model selector engine.
- Orchestration engine.
- Evidence/context adapter.
- Audit trail adapter.

## Allowed Outputs

- Triage recommendation.
- Risk score.
- Suggested workflow.
- Explanation/evidence summary.
- Operator/engineer advisory card.

## Forbidden Outputs And Actions

- Direct DB write.
- Device control.
- Automatic rollback.
- Automatic install.
- Bypassing approval.
- Using external API secrets from repo.
- External AI API calls during this planning task.
- Runtime activation during this planning task.

## Required Integration Phases

- Phase 0: branch inventory and diff audit.
- Phase 1: read-only package import plan.
- Phase 2: contract/schema alignment.
- Phase 3: read-only API skeleton.
- Phase 4: UConsole advisory entry.
- Phase 5: UCDE evidence context adapter.
- Phase 6: policy safety gate.
- Phase 7: validation and freeze.

## Required Future Task Sequence

- NEXUSAI-GA-R3 Branch Diff Audit.
- NEXUSAI-GA-R4 Read-only Package Import.
- NEXUSAI-GA-R5 Contract Alignment.
- NEXUSAI-GA-R6 Read-only Advisory API.
- NEXUSAI-GA-R7 UConsole Advisory Entry.
- NEXUSAI-GA-R8 UCDE Evidence Context Adapter.
- NEXUSAI-GA-R9 Safety/Policy Validation Freeze.

## Readiness Decision

- NEXUSAI current branch integration plan: PASS.
- NEXUSAI current branch code integration: NOT EXECUTED.
- NEXUSAI production activation: NOT EXECUTED.

## Safety Statement

No merge executed. No cherry-pick executed. No code copy executed. No install executed. No rollback executed. No DB migration executed. No runtime activation executed. No external AI API calls executed. No production DB connection executed. No secrets created. No push executed. No tag executed.

PASS marker: `NEXUSAI_GA_R2_CURRENT_BRANCH_INTEGRATION_PLAN_PASS`
