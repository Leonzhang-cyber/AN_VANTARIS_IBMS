# VANTARIS IBMS Repo Baseline Recovery 1 Risk Review

## 1. Security Boundary

| Control | Status |
| ------- | ------ |
| `.env` committed | **No** — only `.env.example` staged |
| Token/password/secret committed | **No** — test credential JSON gitignored |
| Private key committed | **No** — `did_signature.py` uses env var only |
| `node_modules` / `dist` / `.venv` committed | **No** — gitignored |
| Raw source remains excluded | **Yes** — `ibms_front/`, `ibms_backend/` ignored |
| UFMS content merged | **No** |

---

## 2. Cross-System Boundary

- IBMS and UFMS remain separate
- UFMS references only in boundary/inventory docs
- No UFMS source/API/menu/schema/auth in staged files
- Execution not stopped — no contamination detected

---

## 3. Artifact Controls

- Runtime artifacts ignored
- Archives ignored (`Files/`, `*.zip`, etc.)
- Raw packages ignored
- Generated `vc_credential.json` / `credential_*.json` gitignored
- Build output not committed

---

## 4. Follow-up Controls

- Run `git status` before every task
- Do not continue feature work unless clean
- Do not use `git add .`
- Review untracked before commit
- Stop immediately if UFMS content appears in IBMS scope
