# VANTARIS IBMS Frontend A8 Dynamic Menu Baseline

## 1. Task Scope

- dynamic menu loading baseline
- no raw menu/layout copied
- no backend changes
- no npm install/build/dev executed

---

## 2. Files Changed

| File | Purpose |
|---|---|
| `src/services/menu/types.ts` | `AppMenuItem` type |
| `src/services/menu/static-menu.ts` | `fallbackMenuItems` |
| `src/services/menu/menu-normalizer.ts` | Backend payload → menu tree |
| `src/components/AppLayout.vue` | Load menu on mount, fallback on error |
| `src/services/api/menu.ts` | Unchanged (uses existing `getMenus`) |

---

## 3. Dynamic Menu Flow

```
AppLayout onMounted
  → menuApi.getMenus()  (Bearer via request client)
  → normalizeBackendMenu(response)
  → if items.length > 0 → render backend menu
  → else / error → fallbackMenuItems
```

401/403 handled by A1/A3 interceptors (redirect login / forbidden).

---

## 4. Backend Menu API Compatibility

Normalizer accepts:

| Shape | Extraction |
|---|---|
| `[...]` | direct array |
| `{ data: [...] }` | nested array |
| `{ data: { list/menus/items } }` | common wrappers |
| `{ menus: [...] }` | top-level key |

Field mapping: `label|title|name|menuName`, `path|route|url`, `id|menu_id|code`, `children|subMenus`.

External URLs sanitized to `#` (no off-site navigation from menu path).

---

## 5. Fallback Static Menu

On empty response or any error:

- Dashboard → `/dashboard`
- System → `/system`
- IoT → `/iot`
- DID → `/did`
- Modeling → `/modeling`

UI shows subtle “Using fallback menu” note — no full error body.

---

## 6. JWT Requirement

- `GET /system/menus` requires JWT on backend (MENU-JWT)
- Token attached automatically when user logged in via A5
- Unauthenticated menu fetch → 401 → session cleared → `/login`

---

## 7. Not Changed

- Raw menu tree / Layout.vue
- Backend menu_api
- Route definitions (except menu-driven navigation targets)

---

## 8. Next Tasks

- **FRONTEND-A9** — System module first batch migration (prep done)
- **FRONTEND-A10** — Wire sidebar to `/system/menu/active` or version-aware menu
- **FRONTEND-A11** — Permission-filtered menu items
