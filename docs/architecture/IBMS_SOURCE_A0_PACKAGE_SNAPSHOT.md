# VANTARIS IBMS Source A0 Package Snapshot

## 1. Task Scope

- source package inventory only
- no source code changed
- no dependency installed
- no service started
- no migration/seed executed

Snapshot taken at workspace root: `~/Desktop/AN_VANTARIS_IBMS`  
Git reference at scan time: `21c49b6` (`docs(ibms): record permission seed dry-run validation`); security line includes `56234d8 fix(ibms): protect menu API with JWT`.

---

## 2. Source Packages Found

| Package | Path | Exists | Approx Size | Technology Clues | Notes |
|---|---|---|---|---|---|
| ibms_backend | `AN_VANTARIS_IBMS-ibms_backend/` | Yes | 35M | Python, Flask, SQLAlchemy, PyMySQL, JWT, MQTT (paho), Web3/DID, IoT drivers, modeling (sklearn/pkl) | Original backend snapshot; no `.git`; includes `data/`, `src/testMQTT/`, `.idea/` |
| ibms_front | `AN_VANTARIS_IBMS-ibms_front/` | Yes | 200M | Vue 3, Vite 8, TypeScript, Element Plus, Pinia, Vue Router, axios, echarts, three.js, ethers | Full IBMS console UI; package name `ibms-bigdata-fronted`; ~755 `.vue` files under `src/views/` |
| ibms_main | `AN_VANTARIS_IBMS-main/` | Yes | 4K | Markdown only | Placeholder: single `README.md` ("Source Code"); not a runnable frontend |
| current backend (active) | `AN_VANTARIS_IBMS-backend/` | Yes | 1.0M | Same Flask stack family; env-first config; JWT + permission hardening | Tracked in repo; canonical runtime backend for security line |
| contracts | `contracts/` | Yes | small | OpenAPI, permission matrix, security boundary docs | Documentation-only runtime |
| docs | `docs/` | Yes | small | Architecture + security audit trail | Tracked in repo |

**Root archives (not expanded as packages):**

| Archive | Approx Size | Notes |
|---|---|---|
| `AN_VANTARIS_IBMS-ibms_backend.zip` | 22M | Source backup |
| `AN_VANTARIS_IBMS-ibms_front.zip` | 189M | Source backup |
| `AN_VANTARIS_IBMS-main.zip` | 387B | Placeholder backup |

---

## 3. Directory Structure Summary

### 3.1 `AN_VANTARIS_IBMS-ibms_backend`

```
AN_VANTARIS_IBMS-ibms_backend/
├── README.md, README.en.md
├── requirements.txt          (80 lines)
├── .gitignore
├── .idea/                    (JetBrains IDE metadata)
├── data/
│   ├── csv/                  (HVAC_SIM_001.csv)
│   └── models/               (hvac.pkl)
└── src/
    ├── main.py               (Flask entry)
    ├── api/                  (system, menu, did, iot, sse, modeling)
    ├── common/               (config, core, models, utils)
    ├── DID/
    ├── Iot/                  (drivers, services, device_manager)
    ├── blockchain/
    ├── data_modeling/
    ├── system/
    ├── scripts/              (deploy_anchor, migrate_csv_data)
    ├── testMQTT/             (simulator CSV, video.mp4)
    └── tests/
```

### 3.2 `AN_VANTARIS_IBMS-ibms_front`

```
AN_VANTARIS_IBMS-ibms_front/
├── package.json              (Vue 3 + Vite 8)
├── package-lock.json
├── vite.config.ts
├── tsconfig*.json
├── index.html
├── README.md
├── public/
└── src/
    ├── main.ts, App.vue
    ├── api/                  (did_api.js, system_api.js only)
    ├── router/index.ts       (~4600 lines, large nested route tree)
    ├── utils/request.js      (axios + Bearer token)
    ├── stores/, lang/, components/
    ├── images/               (many large PNG/JPG assets — bulk of disk size)
    ├── views/                (40+ top-level modules, 755 .vue files)
    ├── views_analysis_report.txt
    └── missing_files_list.txt
```

**Major view modules:** Home, SystemsDevices, IntegrationHub, DataCenterOperations, Blockchain, Device, Energy, Intelligence, Login, CommandCenter, DeveloperCenter, SecurityCompliance, etc.

### 3.3 `AN_VANTARIS_IBMS-main`

```
AN_VANTARIS_IBMS-main/
└── README.md                 (# AN_VANTARIS_IBMS / Source Code)
```

---

## 4. Git / Build Artifact Notes

| Artifact | ibms_backend | ibms_front | ibms_main |
|---|---|---|---|
| `.git` | No | No | No |
| `node_modules` | No | No | N/A |
| `venv` / `.venv` | No | No | N/A |
| `dist` / `build` | No | No | N/A |
| `__pycache__` | Yes (multiple under `src/`) | No | No |
| `.idea` / `.vscode` | Yes (`.idea/`) | Yes (`.vscode/`) | No |
| zip/backup at repo root | Referenced by zip | Referenced by zip | Referenced by zip |
| Large media/data | csv, pkl, mp4 under backend | Large PNG/JPG under `src/images/` | None |

**Workspace-level:** `Files/` directory present; zip archives at repo root; three source folders are **untracked** (`??`) in git at scan time.

---

## 5. Initial Split Relevance

| Package | Role | Split relevance |
|---|---|---|
| `AN_VANTARIS_IBMS-ibms_backend` | **Original backend package** — pre-security-hardening Flask monolith | Reference source for module inventory; **not** canonical runtime; compare against `AN_VANTARIS_IBMS-backend` |
| `AN_VANTARIS_IBMS-ibms_front` | **Primary frontend / Console UI** — full Vue SPA | Strong candidate for canonical frontend; logical Console modules map to `src/views/*` |
| `AN_VANTARIS_IBMS-main` | **Placeholder / shell label only** | Not a frontend app; do not treat as separate runtime package unless future content added |
| `AN_VANTARIS_IBMS-backend` | **Integrated hardened backend** (current security line) | Canonical backend target for split/migration |
| `contracts/` | API boundary documentation | Cross-cutting split contract layer |
| `docs/` | Architecture and security documentation | Split governance and audit trail |

**Relationship hypothesis (to be confirmed in A1/A2):**

- Backend: same lineage as `AN_VANTARIS_IBMS-backend`; current backend is **newer and security-hardened**.
- Frontend: `ibms_front` is the real UI; `main` is naming placeholder only.
- No evidence that `main` should be merged with `front` physically.

---

## 6. Next Tasks

- **IBMS-SOURCE-A1** — Backend package deep inventory vs current backend
- **IBMS-SOURCE-A2** — Frontend / main package deep inventory
- **IBMS-SPLIT-A0** — Modular split rules and target package map
