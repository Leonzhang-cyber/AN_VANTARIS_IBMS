# VANTARIS IBMS Frontend A3 App Shell Baseline

## 1. Task Scope

- minimal app shell only
- no raw pages or layout copied
- no npm install/build/dev executed
- no backend connection

---

## 2. Files Created

| File | Purpose |
|---|---|
| `src/main.ts` | Vue app entry — router + bootstrap + mount |
| `src/App.vue` | Minimal shell header + `<router-view>` |
| `src/app/bootstrap.ts` | App bootstrap extension point |
| `src/app/error-handlers.ts` | 401/403 → router navigation |
| `src/app/styles.css` | Minimal CSS reset and shell layout |

**Unchanged:** `request.ts` base URL and interceptors (handlers wired via bootstrap).

---

## 3. App Boot Flow

```
index.html → main.ts
  → createApp(App)
  → app.use(router)
  → bootstrapApp(app, router)
       → bindApiAuthErrorHandlers(router)
  → import styles.css
  → app.mount('#app')
```

---

## 4. Router Integration

- Router registered before mount (A2 baseline)
- `error-handlers` receives `Router` instance for programmatic navigation
- Route meta `title` reflected in App.vue header

---

## 5. 401 / 403 UI Handling

| API status | Handler | UI action |
|---|---|---|
| **401** | `handleUnauthorized` | `logoutLocal()` → `/login?redirect=<path>` |
| **403** | `handleForbidden` | Navigate `/403` |

Handlers registered via `setUnauthorizedHandler` / `setForbiddenHandler` on request client.

---

## 6. No Raw Page Migration

- No copy from `ibms_front` Layout.vue, Login.vue, or 755 view files
- Placeholder routes (A2) remain TS-only until FRONTEND-A5+

---

## 7. Next Tasks

- **FRONTEND-A4** — domain API modules (done in same batch)
- **FRONTEND-A5** — login form + real auth flow
- **FRONTEND-A6** — Element Plus + layout shell
- **FRONTEND-A7** — incremental module view migration
