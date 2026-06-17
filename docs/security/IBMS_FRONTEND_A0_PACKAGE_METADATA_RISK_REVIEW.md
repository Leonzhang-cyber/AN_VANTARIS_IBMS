# IBMS Frontend A0 Package Metadata Risk Review

## 1. Dependency review risk

- Only core dependencies included in A0 `package.json`; domain-heavy packages (echarts, three, ethers) deferred to **pending review** to avoid unaudited supply-chain surface.
- Version pins follow raw frontend major families but vite pinned to 6.x for conservative baseline — lockfile not generated until approved `npm install` batch.
- **Risk:** missing deps when modules migrate — mitigate via per-module FRONTEND-A3+ dependency additions with review.

## 2. Hardcoded API URL risk

- Raw `request.js` hardcodes `https://ibms.aegisnx.com/api` — **not copied**.
- Vite config has **no** proxy target or API URL.
- API base must come from `VITE_IBMS_API_BASE_URL` (see `.env.example`).

## 3. Env-only API base rule

- Production/staging/local URLs set via `.env` / CI env — never in vite config or source literals.
- Fallback in request client (A1) is relative `/api` only.

## 4. No secret rule

- No JWT secrets, DB passwords, or private keys in frontend package metadata.
- `.env.example` contains placeholders only.

## 5. No node_modules rule

- `node_modules/` not created; not committed.
- `.gitignore` at repo root already excludes `node_modules/` and `dist/`.

## 6. No build artifact rule

- No `dist/`, no `npm run build` executed in A0.
- Build output must remain gitignored when build runs in future batch.

## 7. Non-scope

- No raw frontend source copied
- No npm install / dev / build executed
- No backend changes
