# VANTARIS IBMS Workspace A1 Raw Source Guard

## 1. Task Scope

- Mark original raw source packages as read-only input.
- Do not commit raw source packages directly.
- No source code changed.
- No files deleted.
- No service started.
- No dependency installed.

---

## 2. Raw Source Packages

| Raw Source Package | Purpose | Git Handling |
|---|---|---|
| `AN_VANTARIS_IBMS-ibms_backend` | original backend source for split analysis | ignored |
| `AN_VANTARIS_IBMS-ibms_front` | original frontend source for split analysis | ignored |
| `AN_VANTARIS_IBMS-main` | placeholder/main package; tracked state must be checked before action | keep existing tracked state |

**Tracked in Git (unchanged by this task):** `AN_VANTARIS_IBMS-main/README.md` only.

**Also ignored at workspace root:** `AN_VANTARIS_IBMS-main 2/` (duplicate reference folder).

---

## 3. Rule

- Raw source packages may be read for inventory.
- Raw source packages must not be committed wholesale.
- Only selected, reviewed, sanitized files may be migrated later.
- Secrets, `.env`, `node_modules`, build artifacts, model/data files must not be copied into target runtime packages.

---

## 4. Current Canonical Decision

- **Canonical backend:** `AN_VANTARIS_IBMS-backend`
- **Raw backend reference:** `AN_VANTARIS_IBMS-ibms_backend`
- **Candidate canonical frontend source:** `AN_VANTARIS_IBMS-ibms_front`
- **Main package:** `AN_VANTARIS_IBMS-main` placeholder only

---

## 5. Next Tasks

- IBMS-SPLIT-B1
- IBMS-SPLIT-B2
- IBMS-SPLIT-B3
- CONTRACTS-B1
