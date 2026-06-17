# IBMS Repository Baseline Recovery Report

**Task:** IBMS-REPO-BASELINE-1  
**Date:** 2026-06-17  
**Workspace:** `/Users/mac/Desktop/AN_VANTARIS_IBMS`

---

## 1. Problem summary

During **IBMS-DB-SMOKE-1**, the local Git repository was found to be corrupt:

```
fatal: bad object HEAD
```

The previously referenced commit `26a6ff6` (`test(ibms): execute approved dev JWT smoke`) is **not present** in the object database. To unblock smoke work, the repository was **reinitialized** (`git init`), producing a new root commit that tracks **only seven smoke-task files**.

The full IBMS project tree remains on disk but is **largely untracked**. Continuing feature development on this partial baseline risks lost history, incomplete diffs, accidental omission of canonical files, and unsafe pushes.

---

## 2. Current repository state

| Item | Value |
|------|--------|
| **Top-level path** | `/Users/mac/Desktop/AN_VANTARIS_IBMS` |
| **Branch** | `main` |
| **HEAD** | `109aba8` — `test(ibms): prepare local DB smoke profile` |
| **Tracked files** | **7** (see §4) |
| **Remotes** | **None** (`git remote -v` empty) |

### 2.1 Tracked files (complete list)

```
AN_VANTARIS_IBMS-backend/config/local-smoke.env.example
AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py
AN_VANTARIS_IBMS-backend/src/api/system/system_api.py
AN_VANTARIS_IBMS-backend/src/common/utils/local_smoke.py
AN_VANTARIS_IBMS-backend/test/smoke/db_jwt_smoke.py
AN_VANTARIS_IBMS-backend/test/smoke/run_db_jwt_smoke.sh
docs/IBMS_DB_LOCAL_SMOKE_PROFILE.md
```

Inventory captured at: `/tmp/ibms_tracked_files.txt` (not committed).

### 2.2 Untracked top-level tree (max depth 2)

```
.gitignore                          (root ignore rules — present on disk, was untracked before baseline docs commit)
AN_VANTARIS_IBMS-backend/           (canonical backend — mostly untracked except smoke paths above)
AN_VANTARIS_IBMS-frontend/          (canonical frontend — fully untracked)
AN_VANTARIS_IBMS-main/              (archive/reference tree)
AN_VANTARIS_IBMS-main.zip
AN_VANTARIS_IBMS-ibms_backend/      (legacy duplicate backend)
AN_VANTARIS_IBMS-ibms_front/        (legacy duplicate frontend)
contracts/                          (API contracts — untracked)
docs/architecture/                  (existing docs — untracked)
docs/security/                      (existing docs — untracked)
Files/                              (reference documents / diagrams — should stay ignored)
```

Inventory captured at: `/tmp/ibms_tree_maxdepth2.txt` (not committed).

### 2.3 What commit `109aba8` contains

```
109aba8 test(ibms): prepare local DB smoke profile
 AN_VANTARIS_IBMS-backend/config/local-smoke.env.example |  17 +
 AN_VANTARIS_IBMS-backend/src/api/system/menu_api.py      | 795 +++++++++++++++++++++
 AN_VANTARIS_IBMS-backend/src/api/system/system_api.py    | 534 ++++++++++++++
 AN_VANTARIS_IBMS-backend/src/common/utils/local_smoke.py | 109 +++
 AN_VANTARIS_IBMS-backend/test/smoke/db_jwt_smoke.py     | 134 ++++
 AN_VANTARIS_IBMS-backend/test/smoke/run_db_jwt_smoke.sh |  15 +
 docs/IBMS_DB_LOCAL_SMOKE_PROFILE.md                      | 171 +++++
 7 files changed, 1775 insertions(+)
```

This commit is a **smoke patch root**, not a project baseline. It does **not** represent the full IBMS codebase under version control.

---

## 3. Remote status

**No Git remote is configured.**

- `git remote -v` → empty
- No fetch/pull/push was performed in this task
- Prior commit `26a6ff6` cannot be recovered from a configured remote in this workspace

**Action required:** Identify the authoritative remote (Gitee/GitHub/internal mirror) before attempting Option A.

---

## 4. Ignored / forbidden artifacts on disk

Scan date: 2026-06-17. **Nothing was deleted** in this task.

| Artifact | Present? | Location / notes | Recommended handling |
|----------|----------|------------------|----------------------|
| Real `.env` | **No** | Only `.env.example` files in backend/frontend | Keep gitignored; never commit |
| Credentials | Not scanned in depth | — | Manual review before baseline commit |
| `node_modules/` | **Yes** | `AN_VANTARIS_IBMS-frontend/node_modules/` | Gitignore; do not commit |
| `dist/` | **Yes** | `AN_VANTARIS_IBMS-frontend/dist/` | Gitignore; do not commit |
| `build/` | Not observed at depth 2 | — | Gitignore if generated |
| `.venv/` | **Yes** | `AN_VANTARIS_IBMS-backend/.venv/` (broken symlink target) | Gitignore; do not commit |
| `.idea/` | **Yes** | Backend / legacy backend IDE metadata | Gitignore |
| `.DS_Store` | **Yes** | `./`, `docs/` | Gitignore |
| `coverage/` | Not observed | — | Gitignore if generated |
| `*.log` | Not observed at depth 3 | — | Gitignore |
| `package-lock.json` | **Yes** | Frontend + legacy front | **Do not modify** in recovery task; exclude from baseline commit only if policy requires |
| Database dumps | Not observed | — | Never commit |
| `AN_VANTARIS_IBMS-main.zip` | **Yes** | Root archive | Gitignore (local reference) |
| Legacy raw packages | **Yes** | `AN_VANTARIS_IBMS-ibms_backend/`, `-ibms_front/` | Already listed in root `.gitignore` |
| `Files/` reference docs | **Yes** | Office/xlsx/jpeg reference material | Already listed in root `.gitignore` |

Root `.gitignore` (on disk) already excludes `.env`, `node_modules/`, `dist/`, `.venv/`, legacy packages, archives, and `Files/`.

---

## 5. Risk of continuing on incomplete baseline

| Risk | Impact |
|------|--------|
| Partial tracking | Most source files untracked → `git diff` / blame / revert unreliable |
| False “clean” commits | Easy to commit docs-only while source changes stay untracked |
| Lost smoke context | `109aba8` files are full-file adds without parent history |
| No remote anchor | Cannot verify against team canonical branch |
| Duplicate trees | Legacy `ibms_backend` / `ibms_front` vs canonical `AN_VANTARIS_IBMS-*` confusion |
| Accidental secret commit | Baseline rush without ignore rules increases exposure |

**Conclusion:** This repository state is **not safe for further application development** until baseline recovery completes.

---

## 6. Recommended recovery options

### Option A — Preferred (when authoritative remote exists)

1. Locate the canonical remote URL and last known good branch/commit (target: recover history including `26a6ff6` if it existed on remote).
2. Clone into a **new clean folder** (do not reuse corrupt `.git`).
3. Re-apply smoke changes from `109aba8` / `docs/IBMS_DB_SMOKE_1_PATCH_NOTES.md`.
4. Run smoke validation on the clean clone.
5. Retire or archive the partial Desktop repo.

**Use when:** A trusted remote or backup clone exists.

### Option B — Controlled local baseline (no reliable remote)

1. Keep corrupt/partial `.git` for reference only, or re-init in place after backup.
2. Ensure root `.gitignore` is committed (covers secrets, `node_modules`, `dist`, `.venv`, legacy trees).
3. Create a **single baseline commit** adding the full canonical project:
   - `AN_VANTARIS_IBMS-backend/` (excluding `.venv`, `__pycache__`, local data)
   - `AN_VANTARIS_IBMS-frontend/` (excluding `node_modules`, `dist`)
   - `contracts/`, `docs/`
4. Preserve `109aba8` smoke changes (already on disk; may squash into baseline or keep as second commit).
5. Add remote later; **do not push** until reviewed.

**Use when:** No remote exists but full tree on disk is authoritative.

### Option C — Smoke patch extraction only

1. Treat current repo as a **patch carrier** for the seven smoke files + docs.
2. Do **not** develop features here.
3. Copy smoke artifacts to a properly baselined repo (Option A or B).

**Use when:** Temporary holding pattern only.

---

## 7. Recommendation for this workspace

**Primary recommendation: Option B** — because **no remote is configured** and the full project tree is present locally.

**Secondary:** If an authoritative remote is identified later, migrate to **Option A** before any shared push.

**Do not** continue IBMS feature work in this repo until Option B (or A) completes.

---

## 8. Related documents

| Document | Purpose |
|----------|---------|
| `docs/IBMS_DB_SMOKE_1_PATCH_NOTES.md` | Smoke patch file list and change summary |
| `docs/IBMS_DB_LOCAL_SMOKE_PROFILE.md` | Smoke execution profile (commit `109aba8`) |

---

## 9. Task constraints observed

- No application source logic modified in IBMS-REPO-BASELINE-1
- No `npm install`, build, test, migration, fetch, pull, or push
- No secrets, tokens, or real `.env` committed
- `/tmp` inventory files not committed
