# UHMI-GA-R2C Report

PASS marker: `UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS`

## Created / Updated

- `UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS.md`
- `UHMI_GA_R2C_CUSTOMER_ENGINEER_ADMIN_OPERATOR_CONTEXT_SPEC.md`
- `UHMI_GA_R2C_REPORT.md`
- `AN_VANTARIS_ONE/registries/uhmi-ga-r2c/uhmi-ga-r2c-role-based-workspace-views.v1.json`
- `scripts/validation/validate-uhmi-ga-r2c-role-based-workspace-views.py`
- `AN_VANTARIS_IBMS-backend/src/uhmi/uhmi_provider.py`
- `AN_VANTARIS_IBMS-backend/src/api/uhmi/uhmi_api.py`
- `AN_VANTARIS_IBMS-frontend/src/services/api/uhmi.ts`
- `AN_VANTARIS_IBMS-frontend/src/modules/uhmi/UhmiWorkspace.vue`

## Summary

R2C is based on UHMI-GA-R2B. R2C adds Customer / Engineer / Admin / Operator role-based workspace views as static role context only.

visualStyle remains `VANTARIS_LIGHT_OPERATIONS_CONSOLE`.

R2C does not perform device control, DB write, runtime activation, EDGE command execution, LINK command execution, install, rollback, authentication change, login change, JWT change, real RBAC mutation, permission write, or package state mutation.

Future control path:

`UHMI -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> LINK -> EDGE -> Device`

## Validation Results

Validation results are recorded after local execution:

- `python3 scripts/validation/validate-uhmi-ga-r2c-role-based-workspace-views.py`: PASS, emitted `UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS`.
- `python3 scripts/validation/validate-uhmi-ga-r2b-workspace-panels-system-context.py`: PASS, emitted `UHMI_GA_R2B_WORKSPACE_PANELS_SYSTEM_CONTEXT_PASS`.
- `python3 scripts/validation/validate-uhmi-ga-r2a-uconsole-menu-ia-ui-api-skeleton.py`: PASS, emitted `UHMI_GA_R2A_FULL_UCONSOLE_MENU_IA_UI_API_SKELETON_PASS`.
- `python3 scripts/validation/validate-uhmi-ga-r1-uconsole-workspace-readonly-foundation.py`: PASS, emitted `UHMI_GA_R1_UCONSOLE_UHMI_WORKSPACE_READONLY_FOUNDATION_FREEZE_PASS`.
- `python3 scripts/validation/validate-one-design-r1-full-product-design-blueprint.py`: PASS, emitted `ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS`.
- `python3 scripts/validation/validate-one-module-ga-wave-r1-consolidated-freeze.py`: PASS, emitted `ONE_MODULE_GA_WAVE_R1_CONSOLIDATED_FREEZE_PASS`.
- `python3 scripts/validation/validate-one-package-route-enforcement.py`: PASS, emitted `ONE_PACKAGE_ROUTE_ENFORCEMENT_PASS`.
- `PYTHONPATH=AN_VANTARIS_ONE python3 scripts/validation/validate-one-boundaries.py`: PASS, emitted `ONE_BOUNDARY_BASELINE_PASS` with existing non-blocking legacy warnings.
- `cd AN_VANTARIS_IBMS-frontend && npm run build`: PASS. Vite/Rolldown reported dependency annotation and chunk-size warnings but exited successfully.

## Safety Statement

No push, no tag, no install, no DB migration, no runtime activation, no device control, no EDGE/LINK command, and no auth/login/JWT/RBAC mutation were executed.

`UHMI_GA_R2C_ROLE_BASED_WORKSPACE_VIEWS_PASS`
