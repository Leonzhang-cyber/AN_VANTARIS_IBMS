# EDGE C1 Closure Audit and Gap Matrix

Date: 2026-06-18  
Workspace: `/Volumes/Work/VANTARIS_UFMS_FULL`  
Project: UFMS  
Audit scope: `AN_VANTARIS_EDGE` only

## 1) Executive conclusion

- EDGE C1 is locally closed for the currently defined C1 scope.
- C1 validation and evidence flow are stable and repeatable on local runtime evidence path.
- EDGE is **not GA-ready yet**; remaining gaps are mostly security hardening, package integrity, real cryptographic/device integrations, and operator interfaces.

## 2) Scope confirmation

- Audited in UFMS workspace and limited to `AN_VANTARIS_EDGE`.
- No LINK runtime implementation changes.
- No changes under UFMS non-EDGE runtime, Code, DB, Console, NexusAI, or Contracts runtime schema/openapi content.

## 3) C1 milestone matrix

| Milestone | Objective | Evidence file / script | Validation status | Closure status | Notes |
|---|---|---|---|---|---|
| C1-01 Runtime Evidence Foundation | EDGE-local evidence flow (registry, normalization, buffer, diagnostics) | `edge-c1-runtime-dry-run.sh`, `edge-c1-runtime-smoke.sh` | PASS | CLOSED | Explicit C1-01 standalone report not found; covered by scripts/evidence and later reports |
| C1-02 Production Install & Hardware-Key Guard Foundation | Production layout, systemd, offline scaffolds, guard baseline | `EDGE_C1_02_PRODUCTION_INSTALL_HARDWARE_KEY_GUARD_REPORT.md`, `edge-c1-production-install-smoke.sh` | PASS | CLOSED | Foundation-only, no real HSM SDK |
| C1-02B Hardware-Key Optional Switch | Optional-by-default hardware-key policy | `EDGE_C1_02B_HARDWARE_KEY_OPTIONAL_SWITCH_REPORT.md`, `edge-c1-runtime-dry-run.sh` | PASS | CLOSED | default required=false; required+production lock retained |
| C1-03 Restart Recovery & Persistence Pressure Evidence | restart recovery, pressure cap, quarantine evidence | `EDGE_C1_03_RESTART_RECOVERY_PERSISTENCE_PRESSURE_REPORT.md`, restart/persistence/quarantine scripts | PASS | CLOSED | Corrupt-line tolerant recovery and pressure cap validated |

## 4) Validation results

- `npm run typecheck:edge` PASS
- `npm run typecheck:link` PASS
- `npm run typecheck:edge-link` PASS
- `bash AN_VANTARIS_EDGE/scripts/validate-edge-package.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/edge-boundary-scan.sh` PASS
- `bash scripts/validate-package-boundaries.sh` PASS (pre-existing warnings)
- `bash scripts/validate-ufms-ibms-isolation.sh` PASS (pre-existing warnings)
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-runtime-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-production-install-smoke.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-restart-recovery-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-persistence-pressure.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-quarantine-dry-run.sh` PASS
- `bash AN_VANTARIS_EDGE/scripts/validation/edge-c1-restart-persistence-smoke.sh` PASS

## 5) Runtime artifact hygiene

- `AN_VANTARIS_EDGE/.runtime` is ignored by git (`.gitignore` rule present).
- No generated runtime artifact under `.runtime` is tracked by git.
- Runtime JSON evidence files are generated artifacts only and remain uncommitted.

## 6) Hardware-key policy closure

- Optional by default: `EDGE_HARDWARE_KEY_REQUIRED=false`.
- Required+production+no verified key -> runtime locked with expected lock reason.
- No fake verified status in validation path.
- Real HSM SDK and challenge-response remain future work.

## 7) Durable buffer closure

- JSONL ledger local-only model in place.
- Restart recovery and replay evidence generated and validated.
- Accepted/failed transitions validated.
- Corrupt line handling and warning collection validated.
- Pressure cap (`maxSafeLimit=1000`) enforced.
- Quarantine evidence generated and verified.
- No LINK dependency and no DB dependency in C1 flow.

## 8) EDGE design alignment matrix

| Item | Status | Notes |
|---|---|---|
| Independent EDGE package | PASS | C1 scripts and runtime are package-local |
| Ubuntu 22.04 offline install foundation | PASS | deploy docs/templates/scripts present |
| systemd non-root service | PASS | `vantaris-edge.service` uses `vantaris-edge` user |
| production directory layout | PASS | layout spec documented |
| edge.env.example with no DB secrets | PASS | forbidden DB keys not present as real env values |
| hardware-key optional guard | PASS | C1-02B policy active |
| locked mode when required | PASS | production required=true lock validated |
| health snapshot | PASS | includes hardware key status and lock reason |
| diagnostics evidence | PASS | includes C1 and C1-03 summaries |
| local durable buffer | PASS | JSONL ledger and state transitions present |
| restart recovery | PASS | dry-run evidence generated |
| quarantine | PASS | invalid sample quarantine evidence generated |
| pressure evidence | PASS | capped pressure dry-run evidence generated |
| no LINK dependency | PASS | boundary assertions and smoke checks pass |
| no DB dependency | PASS | no DB write path in C1 evidence flow |
| no legacy twin/UFMS direct coupling | PASS | isolation scan passes (warnings are historical/global) |

## 9) Remaining gap matrix

| Gap | Current status | Risk | Recommended phase | Blocker for C1 closure |
|---|---|---|---|---|
| Local Health HTTP API / Diagnostic CLI | Missing | Medium | C1-06 | No |
| Offline bundle integrity SHA256SUMS / GPG | Missing | High | C1-05 | No |
| install evidence template execution | Partial | Medium | C1-05 | No |
| Connector Manager | Missing | High | C2-01 | No |
| Protocol Plugin Runtime | Missing | High | C2-01 | No |
| Tag Mapping Engine (full) | Partial (dry-run scope) | Medium | C2 | No |
| Data Normalizer (full runtime) | Partial (dry-run scope) | Medium | C2 | No |
| EDGE to LINK contract dry-run | Missing | Medium | C2 | No |
| Real mTLS | Missing | High | C2 security hardening | No |
| Real HSM challenge-response | Missing | High | C2 security hardening | No |
| AES-256-GCM at-rest payload encryption | Missing | High | C2 security hardening | No |
| Audit event hardening | Partial | Medium | C2 security hardening | No |
| AppArmor profile / host hardening | Partial | Medium | C1-05 / C2 | No |
| Real package rollback test | Missing | Medium | C1-05 | No |

## 10) Recommended next phase

Recommended: `UFMS-EDGE-C1-05 Package Integrity & Offline Bundle Evidence`.

Reason:
- C1 core local evidence path is stable.
- The highest immediate risk gap before broader runtime expansion is artifact integrity and supply-chain/offline install trust (checksums/signing/evidence completeness).
- Closing C1-05 improves deployment confidence without introducing connector/runtime feature breadth yet.

## 11) Final readiness

`UFMS_EDGE_C1_CLOSURE_AUDIT_PASS`
