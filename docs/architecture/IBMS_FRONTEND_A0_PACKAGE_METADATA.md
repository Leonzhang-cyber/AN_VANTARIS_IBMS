# VANTARIS IBMS Frontend A0 Package Metadata

## 1. Task Scope

- package metadata only
- no raw source copied
- no npm install/build/dev executed
- no business pages migrated

Target package: `AN_VANTARIS_IBMS-frontend/`  
Reference (read-only): `AN_VANTARIS_IBMS-ibms_front/`

---

## 2. Files Created

| File | Purpose |
|---|---|
| `AN_VANTARIS_IBMS-frontend/package.json` | npm manifest — core deps only |
| `AN_VANTARIS_IBMS-frontend/vite.config.ts` | Vite 6 + Vue plugin; port 5173; `@` alias |
| `AN_VANTARIS_IBMS-frontend/tsconfig.json` | Lightweight TS strict config |
| `AN_VANTARIS_IBMS-frontend/env.d.ts` | Vite env type declarations |
| `AN_VANTARIS_IBMS-frontend/index.html` | Shell HTML — title `VANTARIS IBMS`, `#app` root |

**Retained from SPLIT-B3:** `package.manifest.json`, `.env.example`, `README.md`, directory `.gitkeep` files.

**Not created:** `src/main.ts`, any `.vue` files, `package-lock.json`.

---

## 3. Raw Metadata Reference

Raw `ibms-bigdata-fronted` dependency categories (reference only):

| Category | Raw packages |
|---|---|
| Core framework | vue, vue-router, pinia, axios |
| UI | element-plus, @element-plus/icons-vue |
| i18n | vue-i18n |
| Charts / 3D / maps | echarts, three, leaflet |
| Web3 | ethers |
| Flow / org charts | @vue-flow/*, vue-tree-chart, vue3-org-tree |
| Utilities | qrcode, xlsx, vuedraggable, sass-embedded |
| Build | vite 8, vue-tsc, terser, vite-plugin-vue-devtools |

Raw vite config included manual chunk splitting for echarts/element-plus and vue devtools plugin — not migrated in A0 baseline.

---

## 4. Migration Decision

| Dependency / config | Decision |
|---|---|
| vue, vue-router, pinia, axios | **Included** — core stack |
| element-plus, @element-plus/icons-vue | **Included** — primary UI (matches raw) |
| vite, @vitejs/plugin-vue, typescript, vue-tsc | **Included** — build toolchain (vite 6 baseline) |
| @vue/tsconfig, @types/node | **Included** — TS support |
| vue-i18n | **Pending review** — add when i18n module migrates |
| echarts, three, leaflet | **Pending review** — domain-specific; add per module |
| ethers | **Pending review** — DID/blockchain views only |
| @vue-flow/*, vue-tree-chart, vue3-org-tree | **Pending review** — org/flow diagrams |
| qrcode, xlsx, vuedraggable, sass-embedded | **Pending review** — feature-specific |
| vite-plugin-vue-devtools, terser, npm-run-all2 | **Deferred** — dev ergonomics / build tuning |
| Hardcoded API URL in vite | **Rejected** — env-only via `VITE_IBMS_API_BASE_URL` |

Package name changed from `ibms-bigdata-fronted` to **`an_vantaris_ibms-frontend`**.

---

## 5. Next Tasks

- **FRONTEND-A1** — request/auth baseline
- **FRONTEND-A2** — router/auth guard baseline
- **FRONTEND-A3** — app shell baseline (`main.ts`, root App)
