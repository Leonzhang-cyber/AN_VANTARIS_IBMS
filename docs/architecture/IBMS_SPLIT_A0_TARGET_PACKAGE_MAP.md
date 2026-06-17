# VANTARIS IBMS Split A0 Target Package Map

Mapping from discovered sources to target runtime/reference roles.  
**No files moved in this task.**

---

## Target package table

| Source Package | Candidate Target | Role | Decision | Notes |
|---|---|---|---|---|
| `AN_VANTARIS_IBMS-ibms_backend/` | Reference archive | Original backend snapshot | **reference-only** | Pre-security; hardcoded secrets; do not run as canonical |
| `AN_VANTARIS_IBMS-ibms_front/` | `AN_VANTARIS_IBMS-frontend/` (future) | Console Vue SPA | **canonical frontend source** | 755 views; wire API client + auth guard in B2/B4 |
| `AN_VANTARIS_IBMS-main/` | Workspace README / meta | Placeholder label | **not a runtime package** | Single README; no src |
| `AN_VANTARIS_IBMS-backend/` | `AN_VANTARIS_IBMS-backend/` | Core API monolith | **canonical backend** | Security line through MENU-JWT, permissions A6–A10 |
| `contracts/` | `contracts/` | API & permission contracts | **keep and extend** | Documentation-only; sync with each API change |
| `docs/` | `docs/` | Architecture & security docs | **keep and extend** | Split governance, inventories, risk reviews |
| Root `*.zip` | External backup / ignore | Delivery archives | **do not commit** | ibms_front.zip ~189M |
| `Files/` | TBD / reference | Legacy files bucket | **inventory before use** | Not part of A0 scope |
| `AN_VANTARIS_IBMS-backend/scripts/` | Same backend package | Ops/seed scripts | **canonical** | Dry-run default; staging apply later |
| `ibms_backend/data/`, `testMQTT/` | Storage/Artifacts or Simulator | Non-runtime data | **exclude from prod** | csv, pkl, mp4 |
| `ibms_front/src/images/` | Frontend assets / CDN | UI binaries | **optional LFS/CDN** | Bulk of 200M front size |

---

## Physical layout (target end-state)

```
AN_VANTARIS_IBMS/                    # monorepo root
├── AN_VANTARIS_IBMS-backend/        # canonical Core API
├── AN_VANTARIS_IBMS-frontend/       # canonical Console (from ibms_front, B3+)
├── contracts/                       # API boundary
├── docs/                            # governance
├── README.md                        # from main placeholder concept
└── reference/                       # optional future: ibms_* snapshots + zips (gitignored)
```

---

## Canonical decisions (A0)

| Layer | Canonical source |
|---|---|
| Backend runtime | `AN_VANTARIS_IBMS-backend` |
| Frontend runtime | `AN_VANTARIS_IBMS-ibms_front` → rename/move in B3 |
| API contracts | `contracts/` |
| Original backend diff reference | `AN_VANTARIS_IBMS-ibms_backend` |
| Main/shell app | **None** — workspace root only |

---

## Module → target mapping (logical)

| Logical module | Primary target package |
|---|---|
| Core/Auth/System | backend |
| Console/UI Shell | frontend |
| Data/DB | backend (internal) |
| IoT/Edge Interface | backend + frontend views |
| DID/Trust | backend + frontend views |
| Modeling/NexusAI | backend + frontend views |
| Contracts/API | contracts + both runtimes |
| Simulator/Test | backend testMQTT + excluded from prod |
| Storage/Artifacts | external / gitignore / LFS |
