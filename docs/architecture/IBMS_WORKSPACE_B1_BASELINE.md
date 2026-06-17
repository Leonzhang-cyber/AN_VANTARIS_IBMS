# VANTARIS IBMS Workspace B1 Baseline

**Task:** IBMS-WORKSPACE-B1  
**Date:** 2026-06-16  
**Title:** Create clean local Git baseline commit

---

## 1. Objective

Establish the first clean local Git baseline commit after IBMS-WORKSPACE-B0 initialization. No remote push, no service execution, no business code changes.

---

## 2. Scope Included in Version Control

| Path | Purpose |
|---|---|
| `.gitignore` | Root ignore rules (B0 + B1 updates) |
| `docs/**` | Architecture documentation (A0–A3, B0, B1) |
| `contracts/**` | Cross-module protocol placeholders |
| `AN_VANTARIS_IBMS-backend/` | Backend monolith source tree |
| `AN_VANTARIS_IBMS-main/` | Console placeholder package |

---

## 3. Scope Excluded from Version Control

| Path / Pattern | Reason |
|---|---|
| `AN_VANTARIS_IBMS-backend.zip` | Local archive (~22 MB) |
| `AN_VANTARIS_IBMS-main.zip` | Local archive |
| `Files/` | Reference materials (docx, xlsx, images) |
| `AN_VANTARIS_IBMS-main 2/` | Duplicate / temporary directory |
| `*.pkl`, `*.pickle` | ML model artifacts |
| `*.csv`, `*.xlsx` | Large data files |
| `*.zip`, `*.tar`, `*.tgz`, `*.gz` | Archives |

---

## 4. Large Files Discovered (Not Committed)

| File | Approx. Size | Action |
|---|---|---|
| `AN_VANTARIS_IBMS-backend.zip` | ~22 MB (>20 MB threshold) | Excluded via `*.zip` |
| `AN_VANTARIS_IBMS-backend/data/models/hvac.pkl` | ~8.3 MB | Excluded via `*.pkl` |
| `AN_VANTARIS_IBMS-backend/data/csv/HVAC_SIM_001.csv` | ~7.2 MB | Excluded via `*.csv` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/*.csv` | Various | Excluded via `*.csv` |
| `AN_VANTARIS_IBMS-backend/src/testMQTT/video.mp4` | ~12.8 MB | Excluded via `*.mp4` (unstaged during B1 review) |
| `Files/UFMS-Products.xlsx` | ~11 KB | Excluded via `Files/` + `*.xlsx` |

> Only files matching `.gitignore` patterns are excluded. Source code (`.py`, `.md`, `.html`, `.json` test fixtures, etc.) within backend/main directories is included.

---

## 5. Package Status at Baseline

### Console — AN_VANTARIS_IBMS-main

- **Status:** Placeholder only (`README.md`).
- **Final frontend package:** Pending — not provided yet.
- **Console development:** Deferred (no IBMS-CONSOLE-A0).

### Backend — AN_VANTARIS_IBMS-backend

- **Status:** Available on disk for future read-only inventory.
- **Stack:** Python / Flask monolith.
- **Business code:** Unmodified in B1.

---

## 6. B1 Task Confirmations

| Check | Result |
|---|---|
| Business code modified | ❌ No |
| Dependency installed | ❌ No |
| Migration executed | ❌ No |
| Service started (backend/frontend) | ❌ No |
| Remote push performed | ❌ No |
| Files deleted / moved / renamed | ❌ No |

---

## 7. Commit Details

- **Message:** `chore(ibms): establish modular workspace baseline`
- **Type:** Local baseline only — no push.

---

## 8. Related Documents

- [IBMS_WORKSPACE_B0_STATUS.md](./IBMS_WORKSPACE_B0_STATUS.md)
- [IBMS_MODULAR_BOUNDARY_A0.md](./IBMS_MODULAR_BOUNDARY_A0.md)
- [IBMS_A0_A3_COMPLETION_REPORT.md](./IBMS_A0_A3_COMPLETION_REPORT.md)

---

## 9. Recommended Next Tasks

1. **IBMS-CONTRACTS-A0** — Contracts version policy
2. **IBMS-CONTRACTS-A1** — OpenAPI drafts from backend API routes
3. **IBMS-DATA-A0** — Data layer Repository specification
4. **IBMS-CORE-A0** — Core API and JWT/RBAC boundaries
5. Update **IBMS-INVENTORY-A1** — backend now on disk with git baseline

**Deferred:** IBMS-CONSOLE-A0 (awaiting final frontend package)
