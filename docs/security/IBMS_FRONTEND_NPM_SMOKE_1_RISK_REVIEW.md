# VANTARIS IBMS Frontend npm Smoke 1 Risk Review

## 1. Security Boundary

- no real `.env` created
- no production API URL used
- no token/password/secret committed
- node_modules not committed
- dist not committed

API base URL remains env-driven via `VITE_IBMS_API_BASE_URL` (`.env.example` only: `http://localhost:5001/api`). No live credentials were written during install, build, or dev smoke.

---

## 2. Dependency Risk

- `package-lock.json` created from `npm install` (116 packages)
- dependencies pending security audit — npm reported 2 high severity vulnerabilities; no `npm audit fix` in this task
- lockfile pins transitive versions for reproducible installs

---

## 3. Runtime Risk

- frontend route guard is not backend security
- backend JWT/permission remains source of truth
- placeholders must remain clearly labeled (audit logs, notification settings, integration settings)

Dev server bound to `127.0.0.1:5173` only; no external exposure configured for this smoke.

---

## 4. Follow-up

- npm audit review as separate task
- frontend smoke with backend as separate task
- contract tests as separate task
