# VANTARIS IBMS Frontend Vite 8 Upgrade Prep

## 1. Task Scope

- upgrade planning only
- no dependency changed
- no package-lock changed
- no npm install executed
- no npm audit fix --force executed
- no frontend source changed

Target: `AN_VANTARIS_IBMS-frontend/`  
Base commit: `6f8d050` — chore(ibms): review frontend npm audit  
Follow-up from: npm-audit-1 (2 high severity toolchain advisories)

---

## 2. Current Dependency State

### Declared (`package.json`)

| Package | Range |
|---|---|
| `vite` | `^6.3.0` |
| `@vitejs/plugin-vue` | `^6.0.6` |
| `vue` | `^3.5.32` |
| `typescript` | `~5.8.0` |
| `vue-tsc` | `^2.2.0` |

### Installed (lockfile / `node_modules`, read-only)

| Package | Version | Role |
|---|---|---|
| `vite` | **6.4.3** | Direct devDependency |
| `@vitejs/plugin-vue` | **6.0.7** | Direct devDependency |
| `vue` | **3.5.38** | Direct runtime dependency |
| `typescript` | **5.8.3** | Direct devDependency |
| `vue-tsc` | **2.2.12** | Direct devDependency |
| `esbuild` | **0.25.12** | Transitive via `vite` (vulnerable) |

### Current `vite.config.ts` surface

Minimal config — no custom Rollup plugins, no esbuild-specific overrides:

- `@vitejs/plugin-vue` only
- `@` path alias
- dev server port `5173`, `host: true`
- build `outDir: dist`, `assetsDir: assets`

### npm audit high severity summary (unchanged from npm-audit-1)

| Package | Severity | Advisory | Installed | Patched |
|---|---|---|---|---|
| `esbuild` | high | [GHSA-gv7w-rqvm-qjhr](https://github.com/advisories/GHSA-gv7w-rqvm-qjhr) | `0.25.12` | `>=0.28.1` |
| `vite` | high | via vulnerable `esbuild` | `6.4.3` | tree with patched `esbuild` |

**Total:** 2 high. Fix path: `npm audit fix --force` → `vite@8.0.16` (breaking).

### npm outdated summary (read-only)

| Package | Current | Wanted | Latest | Notes |
|---|---|---|---|---|
| `vite` | 6.4.3 | 6.4.3 | **8.0.16** | Primary upgrade target |
| `@vitejs/plugin-vue` | 6.0.7 | 6.0.7 | 6.0.7 | Already at latest in range |
| `typescript` | 5.8.3 | 5.8.3 | 6.0.3 | Out of scope — do not bump with Vite task |
| `vue-tsc` | 2.2.12 | 2.2.12 | 3.3.5 | Optional later; not required for Vite 8 |
| `@types/node` | 24.13.2 | 24.13.2 | 25.9.3 | Out of scope |
| `vue-router` | 4.6.4 | 4.6.4 | 5.1.0 | Out of scope |

---

## 3. Upgrade Target

| Field | Value |
|---|---|
| npm audit suggested fix | `vite@8.0.16` |
| `esbuild` patched requirement | `>=0.28.1` (Vite 8 uses **Rolldown** instead of esbuild for bundling — advisory cleared via toolchain replacement) |
| Major upgrade? | **Yes** — Vite 6 → 8 (semver-major; skips Vite 7) |
| `@vitejs/plugin-vue` sync? | **Likely minimal** — `@vitejs/plugin-vue@6.0.7` peer range already includes `^8.0.0`; bump to latest `^6.0.7` in EXEC for safety |

### Proposed `package.json` changes (VITE8-UPGRADE-EXEC only)

```json
{
  "devDependencies": {
    "vite": "^8.0.16",
    "@vitejs/plugin-vue": "^6.0.7"
  }
}
```

Do **not** change `typescript`, `vue-tsc`, `vue`, or runtime deps in the same commit unless build fails and a minimal pin is required.

---

## 4. Compatibility Risk

### Vite major upgrade risk — **Medium**

Vite 8 replaces esbuild + Rollup with **Rolldown** (Rust bundler). For standard Vue SPA projects this is intended as a drop-in upgrade, but it is still a core bundler change. This project has no custom Rollup plugins and a minimal config, which lowers risk.

### plugin-vue compatibility risk — **Low–Medium**

`@vitejs/plugin-vue@6.0.7` declares peer `vite: ^5 || ^6 || ^7 || ^8`. Early Vite 8 betas had plugin-vue breakage (null-byte path issue); fixed in stable 8.0.x. Stay on `@vitejs/plugin-vue@>=6.0.4`.

### TypeScript / vue-tsc compatibility risk — **Low**

Build script runs `vue-tsc --noEmit` before `vite build`. Type-checking is independent of Vite bundler. Keep `typescript@~5.8.0` and `vue-tsc@^2.2.0` unless EXEC reveals a hard failure.

### Build config compatibility risk — **Low**

Current config uses only standard APIs (`defineConfig`, `plugin-vue`, alias, server, build outDir). No `build.rollupOptions`, no esbuild `target` overrides. If future config needs esbuild/Rollup-specific options, migrate to `build.rolldownOptions` per [Vite 8 migration guide](https://vite.dev/guide/migration).

### Dev server behavior risk — **Low–Medium**

Dev server port/host unchanged. `server.host: true` should remain valid. Smoke-test HMR and route navigation after upgrade; Rolldown dev parity is a stated Vite 8 goal but worth verifying.

### package-lock churn risk — **High (expected)**

Full lockfile regeneration on `npm install` after major `vite` bump. Expect transitive tree changes (Rolldown packages, removal/replacement of esbuild in vite dependency chain). Review diff size; do not hand-edit lockfile.

---

## 5. Proposed Upgrade Steps

**Next task: `VITE8-UPGRADE-EXEC`** — execute in order:

1. Confirm `git status` clean
2. Update `vite` to `^8.0.16` and `@vitejs/plugin-vue` to `^6.0.7` in `package.json` only
3. Run `npm install` (not `npm audit fix --force`)
4. Run `npm run build` — must pass `vue-tsc` and `vite build`
5. Run `npm run dev -- --host 127.0.0.1` — stop after Vite ready + optional route spot-check
6. Run `npm audit` — expect high advisories cleared; document any remaining
7. Document results in `IBMS_FRONTEND_VITE8_UPGRADE_EXEC.md` + security notes
8. Commit only if build/dev pass; revert if stop conditions hit

**Out of scope for EXEC:**

- `typescript@6`, `vue-tsc@3`, `vue-router@5` major bumps
- Source refactors unless required by compile errors
- `npm audit fix --force`

---

## 6. Stop Conditions

Abort upgrade and report (do not commit broken state) if:

- `npm install` dependency conflict or peer dependency failure
- `vite.config.ts` breaking change requires non-trivial config rewrite
- `vue-tsc` / TypeScript build failure not fixable by devDependency pin only
- dev server fails to start or HMR broken without clear minimal config fix
- `npm audit` still reports high severity from **unrelated** packages requiring additional major upgrades
- fix requires broad source rewrite across `src/**`

**Rollback:** `git checkout -- package.json package-lock.json && npm install` from pre-EXEC commit.

---

## 7. Recommendation

**Proceed to `VITE8-UPGRADE-EXEC`.** Project profile (minimal Vite config, standard Vue 3 + Element Plus, no custom Rollup plugins) is favorable. `@vitejs/plugin-vue@6.0.7` already peers Vite 8. Primary residual risk is Rolldown bundler regressions — mitigated by build + dev smoke in EXEC.
