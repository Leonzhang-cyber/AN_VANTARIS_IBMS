# VANTARIS IBMS Frontend A5 Login Token Flow

## 1. Task Scope

- minimal login UI + token persistence baseline
- no raw Login.vue copied
- no backend connection tested
- no npm install/build/dev executed

---

## 2. Files Changed

| File | Change |
|---|---|
| `src/views/LoginView.vue` | **Created** — DID challenge login form |
| `src/views/LoginPlaceholder.ts` | **Removed** — replaced by LoginView |
| `src/router/routes.ts` | `/login` → `LoginView.vue` |
| `src/services/auth/session.ts` | Added `extractAccessToken`, `persistLoginSession` |
| `src/services/api/did.ts` | Unchanged (uses `request` client) |

---

## 3. Login Flow

```
User submits did + challenge + signature
  → didApi.login(payload)
  → extractAccessToken(response)
  → persistLoginSession(token, { did })
  → router.push(redirect || /dashboard)
```

Backend contract: `POST /did/login` with `{ did, challenge, signature }` returns `{ code, data: { token } }`.

---

## 4. Token Extraction Compatibility

`extractAccessToken` checks (in order):

1. `response.token`
2. `response.access_token`
3. `response.data.token`
4. `response.data.access_token`

Supports axios body and nested `Result.success` shapes without logging values.

---

## 5. Route Behavior

- `/login` — public; authenticated users redirected to `/dashboard` (A2 guard)
- `?redirect=` query preserved after successful login
- 401 from API triggers A3 handler → clears session → `/login`

---

## 6. Not Changed

- Raw frontend login page
- Backend runtime
- App layout (A6)
- Domain API modules beyond `did.login`

---

## 7. Next Tasks

- **FRONTEND-A6** — Element Plus layout shell
- **FRONTEND-A7** — module migration plan
- **FRONTEND-A8** — challenge fetch helper + VP login mode
