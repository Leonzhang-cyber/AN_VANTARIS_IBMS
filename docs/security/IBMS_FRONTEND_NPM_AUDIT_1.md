# VANTARIS IBMS Frontend npm Audit 1

## 1. Task Scope

- npm audit review for frontend target
- no raw source changed
- no backend changed
- no contracts changed
- no npm audit fix --force

Target: `AN_VANTARIS_IBMS-frontend/`  
Base commit: `d7b7d23` — test(ibms): verify frontend npm smoke

---

## 2. Audit Summary

| Package | Severity | Direct/Transitive | Runtime/Dev | Fix Available | Action |
|---|---|---|---|---|---|
| `esbuild@0.25.12` | high | Transitive (via `vite`) | Dev / build-time only | Patched in `>=0.28.1`; pulled in by `vite` | **Pending** — no semver-safe fix without major `vite` upgrade |
| `vite@6.4.3` | high | Direct (`devDependencies`) | Dev / build-time only | `vite@8.0.16` (`isSemVerMajor: true`) | **Pending** — defer major upgrade to dedicated task |

### Advisory detail

| Field | `esbuild` | `vite` |
|---|---|---|
| Advisory | [GHSA-gv7w-rqvm-qjhr](https://github.com/advisories/GHSA-gv7w-rqvm-qjhr) | Inherited via `esbuild` |
| Title | Missing binary integrity verification in Deno module enables RCE via `NPM_CONFIG_REGISTRY` | Depends on vulnerable `esbuild` |
| Vulnerable range | `>=0.17.0 <0.28.1` (installed: `0.25.12`) | `4.2.0-beta.0 – 8.0.3` (installed: `6.4.3`) |
| Patched version | `>=0.28.1` | Requires dependency tree with patched `esbuild` |
| CVSS | 8.1 (High) | — |
| npm audit fix major? | Yes — via `vite@8.0.16` | Yes — `8.0.16` is semver-major from `^6.3.0` |

Installed tree at audit time:

```
vite@6.4.3 (direct devDependency)
└── esbuild@0.25.12 (transitive)
```

Total vulnerabilities: **2 high**, 0 moderate/low/critical.

---

## 3. Action Taken

- **`npm audit fix` executed** (without `--force`)
- **Result:** vulnerabilities unchanged; npm reported fix requires `npm audit fix --force` → `vite@8.0.16` (breaking change)
- **`npm audit fix --force` not executed** — would introduce major Vite upgrade outside this task scope
- **`package.json` / `package-lock.json`:** no changes (non-force fix did not alter lockfile)
- **Remaining vulnerabilities:** 2 high (`esbuild`, `vite`)

---

## 4. Build Verification

```bash
npm run build
```

| Check | Result |
|---|---|
| `vue-tsc --noEmit` | PASS |
| `vite build` | PASS (vite v6.4.3, ~11s) |

Build verified after audit review; no dependency changes applied.

---

## 5. Pending Risks

Both findings remain **high severity** but are **build-toolchain / dev-time** issues, not shipped runtime dependencies in the production bundle.

Why `--force` was not used:

1. npm audit fix without `--force` cannot resolve the advisory — patched `esbuild` requires `vite@8.0.16` (semver-major).
2. Major Vite 6 → 8 upgrade may break `@vitejs/plugin-vue`, config, and plugin ecosystem; requires dedicated migration + full build/dev smoke.
3. Advisory attack vector (`NPM_CONFIG_REGISTRY` registry substitution during install) is mitigated in controlled dev/CI environments using the official npm registry and pinned lockfile.

**Recommended follow-up:** dedicated `vite-8-upgrade` task with changelog review, plugin compatibility check, build/dev smoke, and re-audit.
