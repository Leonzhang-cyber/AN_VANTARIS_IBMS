# IBMS Source A2 Frontend Risk Review

Scope: read-only analysis of `AN_VANTARIS_IBMS-ibms_front` and `AN_VANTARIS_IBMS-main`.

---

## 1. Token handling risk

| Risk | Location | Severity | Notes |
|---|---|---|---|
| Token in localStorage | `src/utils/request.js`, `Login.vue`, `Layout.vue` | Medium | XSS exposure; acceptable for SPA if CSP hardened — document in split |
| No route auth guard | `src/router/index.ts` `beforeEach` | **High** | User can navigate to protected routes without login check |
| 401 handling | `request.js` removes token + redirect `/login` | Low | Good pattern; ensure all API calls use wrapper |
| Logout cleanup | `Layout.vue` clears token/userInfo | Low | Verify all exit paths |

---

## 2. API base URL risk

| Risk | Location | Severity | Notes |
|---|---|---|---|
| Hardcoded production URL | `src/utils/request.js` — `Online = 'https://ibms.aegisnx.com/api'` active | **High** | Dev URL commented; local/staging builds hit production by default |
| No Vite env pattern | Missing `import.meta.env.VITE_API_BASE` | Medium | Required before split deploy |
| Demo URLs in views | IntegrationHub, RestApi.vue examples | Low | Mock strings — verify not used at runtime |

---

## 3. Hardcoded credentials risk

- No real passwords found in frontend source.
- Demo Bearer placeholders (`YOUR_API_KEY`, `Bearer ***`) in sandbox views — **category: mock UI**.
- Login form posts to backend DID/system login via API — credentials not stored in source.

---

## 4. Menu JWT compatibility risk

| Factor | Status |
|---|---|
| Backend menu routes | JWT required (current backend, 56234d8) |
| Frontend sends Bearer | Yes, via request interceptor |
| Menu fetch before login | May 401 — ensure login flow runs first |
| Permission-aware menu | Not observed in frontend — backend may return 403 after permission seed |

**Risk:** Menu/admin pages may fail until permission seeds applied and frontend handles 403 gracefully.

---

## 5. Build artifact risk

- No `dist/` in snapshot — good.
- No `node_modules/` — good for Git; requires `npm install` at build time only in later phase.
- `package-lock.json` present — lockfile should travel with canonical frontend.

---

## 6. node_modules risk

- Not present in reference tree (~200M is **images**, not dependencies).
- Future install must use lockfile; do not commit `node_modules`.

---

## 7. Large binary / repo bloat risk

- `src/images/` contains many multi-MB PNG/JPG files.
- Split should decide: Git LFS, CDN, or `Storage/Artifacts` — not core Console code.

---

## 8. Recommended safe import order

When phase B frontend migration begins:

1. Declare **`ibms_front`** as canonical; ignore **`main`** for runtime  
2. Externalize **`VITE_API_BASE_URL`** (replace hardcoded Online URL)  
3. Port **`src/utils/request.js`** + error/401 handling unchanged first  
4. Add **router auth guard** (`requiresAuth`, token check)  
5. Port **`src/api/system_api.js`** + **`did_api.js`** — validate against OpenAPI  
6. Add **`iot_api.js`**, **`modeling_api.js`** as backend contracts require  
7. Port **Login / Layout / router** shell  
8. Port **view modules incrementally** by logical domain (Home → System → IoT → DID → Modeling)  
9. **Images/assets** last or via CDN  
10. Run smoke test against staging backend with JWT + permissions  

**Stop conditions:**

- Production API URL still hardcoded in build  
- Menu calls fail without documented auth flow  
- Duplicate frontend package discovered without diff
