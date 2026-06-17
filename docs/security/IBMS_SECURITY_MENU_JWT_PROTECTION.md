# VANTARIS IBMS Security Menu JWT Protection

**Task ID:** IBMS-SECURITY-MENU-JWT  
**Date:** 2026-06-16

---

## 1. Task Scope

- Protect `menu_api.py` routes with JWT only
- No permission enforcement in this task
- No SQL logic changed
- No response envelope changed
- No DB schema changed
- No frontend changed
- No login / JWT payload changed

---

## 2. Files Changed

| File | Change |
|---|---|
| `AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py` | Added `@jwt_required` to all 19 routes; import `jwt_required` |
| `docs/security/IBMS_SECURITY_MENU_JWT_PROTECTION.md` | This document |

---

## 3. Protected Routes

| Route | Method | Handler | Protection |
|---|---|---|---|
| `/api/system/test` | GET | `test` | `@jwt_required` |
| `/api/system/versions` | GET | `list_versions` | `@jwt_required` |
| `/api/system/versions/default` | GET | `get_default_version` | `@jwt_required` |
| `/api/system/versions` | POST | `create_version` | `@jwt_required` |
| `/api/system/versions/<version_code>` | PUT | `update_version` | `@jwt_required` |
| `/api/system/versions/<version_code>` | DELETE | `delete_version` | `@jwt_required` |
| `/api/system/menu/config/<version_code>` | GET | `get_menu_config` | `@jwt_required` |
| `/api/system/menu/active` | GET | `get_active_version_menu_config` | `@jwt_required` |
| `/api/system/versions/switch/<version_code>` | PUT | `switch_active_version` | `@jwt_required` |
| `/api/system/menus` | GET | `get_menu_tree` | `@jwt_required` |
| `/api/system/menus-add` | POST | `create_menu` | `@jwt_required` |
| `/api/system/menus-update/<menu_id>` | PUT | `update_menu` | `@jwt_required` |
| `/api/system/menus-delete/<menu_id>` | DELETE | `delete_menu` | `@jwt_required` |
| `/api/system/menus/batch-sort` | POST | `batch_update_menu_sort` | `@jwt_required` |
| `/api/system/version-menus/<version_code>` | GET | `get_version_menus` | `@jwt_required` |
| `/api/system/version-menus/<version_code>/batch` | POST | `batch_update_version_menus` | `@jwt_required` |
| `/api/system/version-menus/<version_code>/incremental` | POST | `incremental_update_version_menus` | `@jwt_required` |
| `/api/system/version-menus/<version_code>/diff` | POST | `diff_update_version_menus` | `@jwt_required` |
| `/api/system/menu/init-data` | GET | `get_initialization_data` | `@jwt_required` |

**Total:** 19 routes protected.

---

## 4. Not Changed

- `system_api.py` not changed
- Menu SQL logic not changed
- Permission enforcement not added (`require_permission` not used)
- Frontend not changed

---

## 5. Pending

- `system:read` / `system:write` / `system:admin` permission enforcement (IBMS-SECURITY-SYSTEM-B)
- DB seed execution and user `permission_codes` alignment
- Frontend token compatibility check (menu calls must send `Authorization: Bearer`)
- Contract / OpenAPI update for system menu routes

---

## Related Documents

- `docs/security/IBMS_SECURITY_SYSTEM_B_PREP.md`
- `docs/architecture/IBMS_SYSTEM_API_PERMISSION_GAP_REVIEW.md`
