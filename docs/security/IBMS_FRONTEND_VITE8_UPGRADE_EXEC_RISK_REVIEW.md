# VANTARIS IBMS Frontend Vite 8 Upgrade Execution Risk Review

## 1. Security Outcome

| Item | Status |
|---|---|
| vite/esbuild high vulnerabilities resolved | **Yes** — npm audit reports **0 vulnerabilities** after upgrade |
| Pre-upgrade advisories | 2 high (`esbuild@0.25.12`, `vite@6.4.3`) — GHSA-gv7w-rqvm-qjhr |
| Post-upgrade `esbuild` in tree | **No** — removed; Vite 8 uses Rolldown |
| `npm audit fix --force` used | **No** — controlled `npm install vite@^8.0.16` only |

Remediation achieved without forced semver jumps across unrelated packages.

---

## 2. Supply Chain Boundary

- `node_modules` not committed
- `dist` not committed
- no `.npmrc` credentials committed
- no production API URL committed
- no token/password/secret committed

Lockfile regenerated via explicit devDependency bump; install used default npm registry.

---

## 3. Upgrade Risk

| Risk | Assessment |
|---|---|
| Vite major upgrade (6 → 8) | Executed; build and dev smoke passed |
| Rolldown behavior change | Production build succeeded; `@vueuse/core` pure-annotation warnings observed (non-fatal) |
| Build output warnings | Chunk size > 500 kB (informational); Rolldown INVALID_ANNOTATION on transitive dep |
| Config changes | None required |
| Source changes | None required |
| Manual browser smoke | **Pending** — dev ready only; no UI route verification |

Scoped upgrades respected: TypeScript, vue-tsc, vue-router, @types/node unchanged.

---

## 4. Follow-up

- browser UI smoke (login, system routes, layout shell)
- frontend + backend smoke (`VITE_IBMS_API_BASE_URL` against local API)
- npm audit follow-up if new advisories appear on future installs
- optional chunk-splitting review if bundle size becomes a concern
