# VANTARIS IBMS Security System B Prep

**Task:** IBMS-SECURITY-SYSTEM-B-PREP  
**Date:** 2026-06-16  
**Type:** Read-only prep — no runtime changes

---

## 1. Task Scope

- Prep only
- No runtime source changed
- No DB changed
- No seed changed
- No JWT payload changed
- No login changed

---

## 2. Current Route Inventory

### 2.1 system_api.py — JWT on all routes, no permission check

| File | Route | Method | Current JWT | Current Permission | Risk |
|---|---|---|---|---|---|
| system_api | `/system/entity-types` | POST | Yes | None | **High** — entity type mutation |
| system_api | `/system/entity-types/<type_id>` | PUT | Yes | None | **High** |
| system_api | `/system/entity-types/<type_id>` | DELETE | Yes | None | **High** |
| system_api | `/system/entity-types/<type_id>` | GET | Yes | None | Medium — read |
| system_api | `/system/entity-types` | GET | Yes | None | Medium |
| system_api | `/system/entity-types/tree` | GET | Yes | None | Medium |
| system_api | `/system/permissions` | POST | Yes | None | **Critical** — permission table create |
| system_api | `/system/permissions/<perm_id>` | PUT | Yes | None | **Critical** — permission mutate |
| system_api | `/system/permissions/<perm_id>` | DELETE | Yes | None | **Critical** |
| system_api | `/system/permissions/<perm_id>` | GET | Yes | None | Medium |
| system_api | `/system/permissions` | GET | Yes | None | Medium |
| system_api | `/system/create-standard-fields` | POST | Yes | None | **High** |
| system_api | `/system/update-standard-fields/<field_id>` | PUT | Yes | None | **High** |
| system_api | `/system/delete-standard-fields/<field_id>` | DELETE | Yes | None | **High** |
| system_api | `/system/getById-standard-fields/<field_id>` | GET | Yes | None | Low |
| system_api | `/system/list-standard-fields` | GET | Yes | None | Low |
| system_api | `/system/create-standard-methods` | POST | Yes | None | **High** |
| system_api | `/system/update-standard-methods/<method_id>` | PUT | Yes | None | **High** |
| system_api | `/system/delete-standard-methods/<method_id>` | DELETE | Yes | None | **High** |
| system_api | `/system/getById-standard-methods/<method_id>` | GET | Yes | None | Low |
| system_api | `/system/list-standard-methods` | GET | Yes | None | Low |

**Count:** 21 handlers, all `@jwt_required`, zero `@require_permission`.

### 2.2 menu_api.py — no JWT, no permission

| File | Route | Method | Current JWT | Current Permission | Risk |
|---|---|---|---|---|---|
| menu_api | `/system/test` | GET | No | None | Low — health |
| menu_api | `/system/versions` | GET | No | None | Medium — version list |
| menu_api | `/system/versions/default` | GET | No | None | Medium |
| menu_api | `/system/versions` | POST | No | None | **Critical** — create version |
| menu_api | `/system/versions/<version_code>` | PUT | No | None | **Critical** |
| menu_api | `/system/versions/<version_code>` | DELETE | No | None | **Critical** |
| menu_api | `/system/menu/config/<version_code>` | GET | No | None | Medium |
| menu_api | `/system/menu/active` | GET | No | None | Medium — active menu |
| menu_api | `/system/versions/switch/<version_code>` | PUT | No | None | **High** — switch active version |
| menu_api | `/system/menus` | GET | No | None | Medium |
| menu_api | `/system/menus-add` | POST | No | None | **Critical** — menu create |
| menu_api | `/system/menus-update/<menu_id>` | PUT | No | None | **Critical** |
| menu_api | `/system/menus-delete/<menu_id>` | DELETE | No | None | **Critical** |
| menu_api | `/system/menus/batch-sort` | POST | No | None | **High** |
| menu_api | `/system/version-menus/<version_code>` | GET | No | None | Medium |
| menu_api | `/system/version-menus/<version_code>/batch` | POST | No | None | **High** |
| menu_api | `/system/version-menus/<version_code>/incremental` | POST | No | None | **High** |
| menu_api | `/system/version-menus/<version_code>/diff` | POST | No | None | **High** |
| menu_api | `/system/menu/init-data` | GET | No | None | Medium |

**Count:** 19 handlers, **none** `@jwt_required`.

---

## 3. High-Risk Targets

| Category | Routes | Proposed permission |
|---|---|---|
| Permission CRUD | `/system/permissions` POST/PUT/DELETE | `system:admin` |
| Menu create/update/delete | `/system/menus-add`, `menus-update`, `menus-delete` | `system:admin` or `system:write` |
| Version management | `/system/versions` POST/PUT/DELETE, switch | `system:admin` |
| Version-menu batch/diff | `/system/version-menus/*` POST | `system:admin` or `system:write` |
| Entity type admin | `/system/entity-types` POST/PUT/DELETE | `system:admin` |
| System standard field/method writes | `/system/create|update|delete-standard-*` | `system:write` |

---

## 4. Proposed Protection

| Route class | Suggested permission |
|---|---|
| GET list/detail (entity-types, permissions, standard fields/methods, menus, versions) | `system:read` |
| POST/PUT/PATCH standard field/method (system module) | `system:write` |
| Permission table mutation | `system:admin` |
| Menu / version / version-menu mutation | `system:admin` (or `system:write` for non-destructive menu edits) |
| Entity type mutation | `system:admin` |

**Implementation order:** Add `@jwt_required` to all `menu_api` routes first, then `@require_permission` / `@require_any_permission` on both files.

---

## 5. Non-Scope

- No runtime enforcement in this prep task
- No DB seed
- No frontend menu change
- No login change

---

## 6. Recommended Next Tasks

- **IBMS-SECURITY-SYSTEM-B** — JWT + permission on system_api and menu_api
- **IBMS-DB-SEED-PERMS-PREP** — seed `system:read` / `write` / `admin`
- **IBMS-DB-SEED-PERMS** — apply seed and validate login `perms`
- **IBMS-CONTRACTS-A4** — contract tests for system routes 401/403

---

## Related Documents

- `docs/architecture/IBMS_SYSTEM_API_PERMISSION_GAP_REVIEW.md`
- `docs/architecture/IBMS_PERMISSIONS_A0_RUNTIME_INVENTORY.md`
