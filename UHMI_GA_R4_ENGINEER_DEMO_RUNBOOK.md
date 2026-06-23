# UHMI-GA-R4 Engineer Demo Runbook

PASS marker: `UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`

## Local Repository Checks

```bash
git status -sb
git branch --show-current
git rev-parse HEAD
git log --oneline -8
git tag --list "uhmi-ga-*"
```

## Validator Commands

```bash
python3 scripts/validation/validate-uhmi-ga-r4-customer-preview-export-package.py
python3 scripts/validation/validate-uhmi-ga-r3-customer-preview-package.py
python3 scripts/validation/validate-uhmi-ga-r2f-final-readonly-workspace-release-index.py
python3 scripts/validation/validate-uhmi-ga-r2e-workspace-api-consolidation-frontend-integration-audit.py
python3 scripts/validation/validate-uhmi-ga-r2d-workspace-visual-polish-light-console-style.py
python3 scripts/validation/validate-uhmi-ga-r2c-role-based-workspace-views.py
python3 scripts/validation/validate-uhmi-ga-r2b-workspace-panels-system-context.py
python3 scripts/validation/validate-uhmi-ga-r2a-uconsole-menu-ia-ui-api-skeleton.py
python3 scripts/validation/validate-uhmi-ga-r1-uconsole-workspace-readonly-foundation.py
python3 scripts/validation/validate-one-design-r1-full-product-design-blueprint.py
python3 scripts/validation/validate-one-module-ga-wave-r1-consolidated-freeze.py
python3 scripts/validation/validate-one-package-route-enforcement.py
PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-boundaries.py
```

## Frontend Build

R4 does not change frontend functionality, so a new frontend build is not required. R4 evidence records that R2E/R2D build evidence remains referenced. Do not run install, do not add dependencies, and do not commit `dist` or `build`.

## Safety Checks Before Demo

- Confirm Customer Preview Export Package is `MANIFEST_EVIDENCE_RUNBOOK_ONLY`.
- Confirm no runnable production package generated.
- Confirm no dist/build committed.
- Confirm no .env/secrets committed.
- Confirm No Direct Device Control.
- Confirm No Runtime Activation.
- Confirm No DB Write.
- Confirm No EDGE Command Execution.
- Confirm No LINK Command Execution.
- Confirm No auth / login / JWT / RBAC mutation.
- Confirm Production Activation is `NOT EXECUTED`.

## After Demo Review

- Re-run R4 validator if any hand-off text changes.
- Confirm `git status --short`.
- Confirm no generated archive, `dist`, `build`, `.env`, `.runtime`, or secrets were added.

## If Terminal Appears Stuck

- Press `Control+C`.
- Press `q` when inside paged output.
- Run `exit` to close a shell.

UHMI is not HMI Server. UHMI is not SCADA replacement.

`UHMI_GA_R4_CUSTOMER_PREVIEW_EXPORT_PACKAGE_PASS`
