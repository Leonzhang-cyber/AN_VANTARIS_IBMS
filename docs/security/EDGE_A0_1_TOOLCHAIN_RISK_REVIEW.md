# EDGE A0.1 Toolchain Risk Review

## 1) node_modules accidentally committed

- description: local dependency directory could be staged by mistake.
- impact: repository bloat and unstable diffs.
- control: `.gitignore` excludes `node_modules`; staging checks confirm not added.
- current status: Controlled.

## 2) root package drift

- description: package operations could modify root `package.json` or root lockfile.
- impact: unintended dependency drift across repository.
- control: install executed only in `AN_VANTARIS_EDGE`; explicit root diff check.
- current status: Controlled.

## 3) devDependency pollution

- description: unnecessary development tooling may be added during unblock.
- impact: maintenance burden and unclear package baseline.
- control: keep only minimal `typescript` devDependency in EDGE package.
- current status: Controlled.

## 4) runtime dependency introduced too early

- description: runtime libraries might be added while fixing typecheck.
- impact: scope breach and hidden runtime coupling before EDGE-A1.
- control: no runtime dependencies added in A0.1.
- current status: Controlled.

## 5) typecheck bypassed

- description: unblock work could skip actual compiler execution.
- impact: false readiness signal for skeleton quality.
- control: run `./node_modules/.bin/tsc -v` and `npm run typecheck` with recorded outputs.
- current status: Controlled.

## 6) legacy driver copied while fixing typecheck

- description: legacy files might be copied into EDGE package during quick fixes.
- impact: architecture contamination and coupling regression.
- control: explicit legacy-file detection check in validation flow.
- current status: Controlled.

## 7) secret leakage through npm files

- description: credentials/tokens could leak into package/toolchain artifacts.
- impact: security exposure.
- control: secret scan over EDGE/docs/script outputs; no secret material allowed.
- current status: Controlled.
