# VANTARIS IBMS Frontend A6 Layout Shell

## 1. Task Scope

- Element Plus layout shell baseline
- no raw Layout.vue copied
- no menu API integration
- no npm install/build/dev executed

---

## 2. Files Changed

| File | Change |
|---|---|
| `src/components/AppLayout.vue` | **Created** — header, aside, menu, main |
| `src/App.vue` | Login/403 bare; other routes use AppLayout |
| `src/main.ts` | Register Element Plus + CSS |
| `src/app/styles.css` | Minimal global reset (removed old app-shell classes) |
| `src/router/routes.ts` | Module stub routes + `layout` meta |

---

## 3. Layout Structure

```
App.vue
├── /login, /403 → <router-view> (no layout)
└── other paths → AppLayout
      ├── el-header (brand + logout)
      ├── el-aside + el-menu
      └── el-main → <router-view>
```

---

## 4. Menu Placeholder Items

| Menu item | Route | Component (temporary) |
|---|---|---|
| Dashboard | `/dashboard` | DashboardPlaceholder |
| System | `/system` | DashboardPlaceholder |
| IoT | `/iot` | DashboardPlaceholder |
| DID | `/did` | DashboardPlaceholder |
| Modeling | `/modeling` | DashboardPlaceholder |

Real views migrate in FRONTEND-A8+ batches.

---

## 5. Logout Local Flow

1. User clicks **Logout** in header
2. `logoutLocal()` clears token + user info
3. `router.push('/login')`
4. No backend logout API call

---

## 6. Not Changed

- Raw layout / menu tree (~4600-line router)
- Backend menu_api integration
- Images / raw CSS

---

## 7. Next Tasks

- **FRONTEND-A8** — fetch menus from `menuApi` with JWT
- **FRONTEND-A9** — System module first page migration
- **FRONTEND-A7** — migration plan (same batch, docs only)
