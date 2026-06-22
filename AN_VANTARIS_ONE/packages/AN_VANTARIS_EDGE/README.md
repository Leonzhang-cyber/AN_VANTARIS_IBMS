# AN_VANTARIS_EDGE

Unified field-side runtime package for VANTARIS ONE and standalone module deployments.

## Package purpose

`AN_VANTARIS_EDGE` provides the edge acquisition and signed handoff runtime boundary for field integration.

## Single unified EDGE runtime rule

- One EDGE runtime package for standalone UFMS and VANTARIS ONE deployments.
- No UFMS-private EDGE fork.
- No VANTARIS ONE-private EDGE fork.
- Contract authority remains `AN_VANTARIS_Contracts`.

## Standalone UFMS and VANTARIS ONE usage

Both deployment modes consume the same EDGE package and same contract authority, with differences expressed through deployment/module/license/routing configuration.

## Current readiness

- International GA framework standard established.
- Runtime hardening in progress.
- Current runtime status: imports resolved and typecheck-ready baseline; typecheck execution pending.

## GA standard docs

- `AN_VANTARIS_EDGE/docs/EDGE_INTERNATIONAL_GA_STANDARD_V1.md`
- `AN_VANTARIS_EDGE/docs/EDGE_GA_ARCHITECTURE_V1.md`
- `AN_VANTARIS_EDGE/docs/EDGE_DEPLOYMENT_PROFILE_STANDARD_V1.md`
- `AN_VANTARIS_EDGE/docs/EDGE_GA_ACCEPTANCE_CHECKLIST_V1.md`
- `AN_VANTARIS_EDGE/docs/EDGE_PACKAGE_AND_DEPLOYMENT_STANDARD_V1.md`
- `AN_VANTARIS_EDGE/docs/EDGE_GA_ENGINEERING_ROADMAP_V1.md`

## Current next phase

`EDGE-GA-A1 — Package Skeleton and Config Standard`

## EDGE-GA-A1 package skeleton status

- Package skeleton and config standard artifacts are created.
- Runtime hardening and typecheck execution remain pending.

## Template and artifact paths

- Config template: `AN_VANTARIS_EDGE/config/templates/edge.config.template.yaml`
- Deployment profiles:
  - `AN_VANTARIS_EDGE/config/templates/deployment-profile.standalone-ufms.yaml`
  - `AN_VANTARIS_EDGE/config/templates/deployment-profile.vantaris-one.yaml`
- Connector profile template: `AN_VANTARIS_EDGE/config/templates/connector-profile.template.yaml`
- Script skeletons:
  - `AN_VANTARIS_EDGE/scripts/install-edge.sh`
  - `AN_VANTARIS_EDGE/scripts/uninstall-edge.sh`
  - `AN_VANTARIS_EDGE/scripts/smoke-edge.sh`
  - `AN_VANTARIS_EDGE/scripts/validate-edge-package.sh`
- Release manifest: `AN_VANTARIS_EDGE/manifests/edge-release-manifest.v1.json`
- Evidence templates:
  - `AN_VANTARIS_EDGE/evidence/templates/EDGE_GA_EVIDENCE_INDEX_TEMPLATE.md`
  - `AN_VANTARIS_EDGE/evidence/templates/EDGE_GA_SECURITY_EVIDENCE_TEMPLATE.md`

## Current next phase

`UFMS-RESTORE-2E — Typecheck Minimal EDGE/LINK Packages`
or
`EDGE-GA-A2 — Typecheck Readiness`
