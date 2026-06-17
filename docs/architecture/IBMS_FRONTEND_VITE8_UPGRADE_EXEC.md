# VANTARIS IBMS Frontend Vite 8 Upgrade Execution

## 1. Task Scope

- upgrade Vite 6 to Vite 8
- frontend target only
- no raw source changed
- no backend changed
- no contracts changed
- no npm audit fix --force

Target: `AN_VANTARIS_IBMS-frontend/`  
Base commit: `b0b1f4b` — docs(ibms): prepare Vite 8 upgrade

---

## 2. Dependency Changes

| Package | Before | After | Reason |
|---|---|---|---|
| `vite` | 6.4.3 | **8.0.16** | Remediate npm audit high (esbuild chain) |
| `@vitejs/plugin-vue` | 6.0.7 | **6.0.7** | Peer compatibility with Vite 8 (range bumped to `^6.0.7` in manifest) |
| `esbuild` | 0.25.12 (transitive) | **removed from tree** | Vite 8 uses Rolldown; vulnerable esbuild no longer installed |
| `typescript` | 5.8.3 | 5.8.3 | Unchanged (per task rule) |
| `vue-tsc` | 2.2.12 | 2.2.12 | Unchanged |
| `vue-router` | 4.6.4 | 4.6.4 | Unchanged |
| `@types/node` | 24.13.2 | 24.13.2 | Unchanged |

Environment: Node v20.20.2, npm 10.8.2

---

## 3. Commands Executed

```bash
cd AN_VANTARIS_IBMS-frontend

# Pre-upgrade baseline
npm list vite @vitejs/plugin-vue vue typescript vue-tsc esbuild --depth=0
npm audit

# Controlled upgrade (no --force)
npm install vite@^8.0.16 @vitejs/plugin-vue@^6.0.7 --save-dev

# Post-install verification
npm list vite @vitejs/plugin-vue esbuild --depth=1
npm audit
npm run build
npm run dev -- --host 127.0.0.1   # stopped after ready
npm audit
```

---

## 4. Verification Results

| Check | Result | Notes |
|---|---|---|
| npm install | **PASS** | 6 added, 5 removed, 1 changed; 119 packages audited |
| npm run build | **PASS** | `vue-tsc --noEmit` + `vite build` in ~10.5s / ~1.35s bundling |
| npm run dev | **PASS** | Vite v8.0.16 ready in 703 ms @ `http://127.0.0.1:5174/` (5173 in use) |
| npm audit | **PASS** | **0 vulnerabilities** (was 2 high before upgrade) |

### Build warnings (non-blocking)

- Rolldown `[INVALID_ANNOTATION]` on `@vueuse/core` `/* #__PURE__ */` comments — upstream dependency; no action in this task
- Chunk size > 500 kB — pre-existing; Rolldown suggests `build.rolldownOptions.output.codeSplitting`

---

## 5. Fixes Applied

**None** — no `vite.config.ts` or `src/**` changes required. Minimal config (`plugin-vue`, alias, server port, build outDir) compatible with Vite 8 / Rolldown as-is.

---

## 6. Remaining Risks

- **Rolldown regression risk** — bundler changed from Rollup/esbuild to Rolldown; build passed but full browser regression not run
- **Browser manual smoke pending** — dev server started; no route/HMR manual verification in this task
- **Backend integration smoke pending** — API calls not tested against local backend
- **@vueuse/core annotation warnings** — monitor upstream; may affect DCE in edge cases

---

## 7. Audit Remediation Outcome

| Metric | Before | After |
|---|---|---|
| High severity | 2 | **0** |
| Total vulnerabilities | 2 | **0** |
| `npm audit fix --force` used | No | No |

Advisories cleared: GHSA-gv7w-rqvm-qjhr (`esbuild` / `vite` chain).
