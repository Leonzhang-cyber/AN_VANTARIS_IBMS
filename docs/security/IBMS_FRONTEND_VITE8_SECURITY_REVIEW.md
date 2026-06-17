# VANTARIS IBMS Frontend Vite 8 Security Review

## 1. Vulnerability Context

- **High severity** findings originate from the **Vite / esbuild dev toolchain**, not from application runtime dependencies shipped to end users.
- npm-audit-1 confirmed: `esbuild@0.25.12` (transitive) and `vite@6.4.3` (direct devDependency) are affected by [GHSA-gv7w-rqvm-qjhr](https://github.com/advisories/GHSA-gv7w-rqvm-qjhr).
- Advisory title: missing binary integrity verification in Deno module path; potential RCE when npm registry is substituted via `NPM_CONFIG_REGISTRY` during install/build tooling fetch.
- **No production runtime dependency impact** — built static assets (`dist/`) do not bundle esbuild; attack surface is **dev/CI install and build pipeline**.
- Remediation path identified: upgrade to `vite@8.0.16`, which replaces esbuild bundling with Rolldown and clears the advisory chain.

---

## 2. Force Upgrade Rule

| Rule | Rationale |
|---|---|
| `npm audit fix --force` must **not** be used automatically | Forces semver-major jump without review, changelog check, or smoke tests |
| Major upgrade must be **explicit and isolated** | Dedicated `VITE8-UPGRADE-PREP` → `VITE8-UPGRADE-EXEC` sequence |
| Build/dev smoke **required** after upgrade | Rolldown bundler change needs verification before commit |
| No bundled major bumps | Do not simultaneously upgrade TypeScript 6, vue-router 5, or vue-tsc 3 unless EXEC proves necessary |

---

## 3. Registry / Supply Chain Controls

Until Vite 8 is deployed:

- Use **trusted npm registry** (default `https://registry.npmjs.org/`) in dev and CI
- **Avoid arbitrary `NPM_CONFIG_REGISTRY` override** on developer machines and CI runners — this is the primary exploitation path for GHSA-gv7w-rqvm-qjhr
- **Do not commit `.npmrc`** with credentials or custom registry tokens
- **Do not commit `node_modules`** — rely on pinned `package-lock.json`
- **Do not commit `dist`** — build artifacts are generated locally/CI only
- Lockfile from npm-audit-1 remains authoritative until EXEC regenerates it after controlled upgrade

---

## 4. Recommended Execution

| Step | Task | Purpose |
|---|---|---|
| 1 | **VITE8-UPGRADE-PREP** (this task) | Impact assessment, stop conditions, no dependency change |
| 2 | **VITE8-UPGRADE-EXEC** | Controlled `vite@^8.0.16` bump + `npm install` + build/dev smoke |
| 3 | Post-upgrade `npm audit` | Confirm high advisories resolved; document remainder |
| 4 | Optional CI hardening | Enforce registry URL, block `--force` audit fix in automation |

**Success criteria for EXEC:**

- `npm run build` PASS
- `npm run dev` starts and reports ready
- `npm audit` shows 0 high from vite/esbuild chain (or documented exception)
- No secrets, no production API URLs, no `src/**` changes unless unavoidable compile fix

---

## 5. Residual Risk After Upgrade

Even after Vite 8:

- New Rolldown-specific regressions may appear (monitor Vite 8 issue tracker)
- Other transitive advisories may surface — handle per-package, not via `--force`
- Frontend route guards remain **not** a security boundary; backend JWT/permission enforcement stays authoritative
