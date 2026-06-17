# VANTARIS IBMS Frontend A2 Router Auth Guard

## 1. Task Scope

- router/auth guard baseline only
- no raw router copied (~4600 lines)
- no `.vue` pages migrated
- no npm install/build/dev executed

---

## 2. Files Created

| File | Purpose |
|---|---|
| `src/router/routes.ts` | Minimal route table + meta model |
| `src/router/guards.ts` | `beforeEach` auth/permission guard |
| `src/router/index.ts` | Router factory + guard registration |
| `src/views/LoginPlaceholder.ts` | TS placeholder component |
| `src/views/DashboardPlaceholder.ts` | TS placeholder component |
| `src/views/ForbiddenPlaceholder.ts` | TS placeholder component |
| `src/views/NotFoundPlaceholder.ts` | TS placeholder component |

---

## 3. Route Meta Model

```typescript
interface RouteMeta {
  requiresAuth?: boolean   // default false when omitted
  permissions?: string[]   // future fine-grained checks
  title?: string           // document title suffix
}
```

---

## 4. requiresAuth Behavior

| Condition | Action |
|---|---|
| `requiresAuth: true` + no token | Redirect `/login?redirect=<path>` |
| `/login` + already authenticated | Redirect `/dashboard` |
| Public routes | Proceed |

Uses `isAuthenticated()` from `src/services/auth/session.ts`.

---

## 5. Permissions Future Behavior

- `meta.permissions` array triggers `hasPermission()` check
- Current implementation: **placeholder returns true** (TODO FRONTEND-A3+)
- On failure: redirect `/403`
- Backend `@require_permission` remains authoritative

---

## 6. No Raw Route Copied

- Raw `router/index.ts` had 755+ nested view routes — **not copied**
- Module routes deferred with TODO comments in `routes.ts`

---

## 7. Next Tasks

- **FRONTEND-A3** — app shell (`main.ts`, wire request handlers → router)
- **FRONTEND-A4** — domain API modules
- **FRONTEND-A5** — incremental module route migration
