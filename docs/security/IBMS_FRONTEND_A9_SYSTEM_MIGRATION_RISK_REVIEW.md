# IBMS Frontend A9 System Migration Risk Review

## 1. menu_api JWT compatibility risk

- Dynamic menu (A8) requires token before `getMenus`
- System pages must not fetch menu/permissions before login
- **Mitigation:** route guards + request interceptors already in place

## 2. System permission pending risk

- Backend JWT on system routes; fine-grained `@require_permission` may expand
- PermissionManagement migration must handle 403 gracefully
- Coordinate with DB-B1 permission seed before CRUD testing

## 3. Raw hardcoded API risk

- Raw `request.js` uses production host — selected pages do not import it directly
- IntegrationSettings may contain example URLs — sanitize on migrate

## 4. Dependency risk

| Page | Risk |
|---|---|
| PermissionManagement | Element Plus only — OK |
| RoleManagement (deferred) | Large mock — batch 2 |
| EditionManagement (deferred) | system_api + 1789 lines |

## 5. No build validation risk

- This prep task does not run `npm install` or `vue-tsc`
- First migrated page must be validated in dedicated exec batch with venv/node

## 6. Recommended batch size

| Guideline | Value |
|---|---|
| Pages in first exec batch | **7** (planned), migrate **1 per commit** |
| Max lines per migrated page | ~300 target after simplification |
| Defer over | 500 lines raw without split plan |

## 7. Non-scope

- No `.vue` copied in A9-SYSTEM-PREP
- No target `src/` changes
- No backend changes
