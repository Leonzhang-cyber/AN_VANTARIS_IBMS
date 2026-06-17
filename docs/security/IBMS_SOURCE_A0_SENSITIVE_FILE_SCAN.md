# IBMS Source A0 Sensitive File Scan

## 1. Task Scope

只读扫描，不复制 secret。  
扫描范围：`AN_VANTARIS_IBMS-ibms_backend`, `AN_VANTARIS_IBMS-ibms_front`, `AN_VANTARIS_IBMS-main`  
未执行：依赖安装、服务启动、文件搬迁、`.env` 创建。

---

## 2. Sensitive File Candidates

| Path | Category | Action |
|---|---|---|
| `AN_VANTARIS_IBMS-ibms_backend/src/common/config/default.py` | Hardcoded DB password, JWT secret, MQTT host, DID private key | **Do not commit**; do not copy into runtime package; use env externalization (current backend already refactored) |
| `AN_VANTARIS_IBMS-ibms_backend/.idea/dataSources.xml` | IDE DB connection metadata (may reference hosts/credentials) | Exclude from split; do not commit |
| `AN_VANTARIS_IBMS-ibms_front/src/utils/request.js` | Hardcoded production API base URL (`https://ibms.aegisnx.com/api`) | Externalize via `VITE_*` env at split time; no secret value but deployment risk |
| `AN_VANTARIS_IBMS-ibms_front/src/views/Login/Login.vue` | Token storage in `localStorage` | Review auth flow during split; not a file secret but session handling risk |
| Root `AN_VANTARIS_IBMS-ibms_*.zip` | Full source archives (may contain same secrets as unpacked trees) | Do not commit; keep outside Git or in ignore list |
| No `.env` / `.env.*` found in three packages | — | Good for reference snapshot; enforce `.env.example` only in target packages |

**Not found in three packages:** `.pem`, `.key`, `.p12`, `.pfx`, `.db`, `.sqlite*`, standalone `.env` files.

---

## 3. Large Artifact Candidates

| Path | Type | Action |
|---|---|---|
| `AN_VANTARIS_IBMS-ibms_backend/data/csv/HVAC_SIM_001.csv` | Training/simulation CSV | Do not copy to runtime unless approved; keep in Storage/Artifacts or simulator scope |
| `AN_VANTARIS_IBMS-ibms_backend/data/models/hvac.pkl` | ML model pickle | Do not commit to Git unless approved; runtime load via external artifact store |
| `AN_VANTARIS_IBMS-ibms_backend/src/testMQTT/air_quality_data.csv` | Simulator data | Simulator/Test module only |
| `AN_VANTARIS_IBMS-ibms_backend/src/testMQTT/hvac_2025_prediction_data.csv` | Simulator data | Simulator/Test module only |
| `AN_VANTARIS_IBMS-ibms_backend/src/testMQTT/video.mp4` | Media test artifact | Exclude from production runtime |
| `AN_VANTARIS_IBMS-ibms_front/src/images/*.png` (many >1MB) | UI/marketing images | Large binary bulk (~majority of 200M front size); consider Git LFS or CDN, not core split code |
| `AN_VANTARIS_IBMS-ibms_front.zip` (~189M) | Archive | Do not commit |
| `AN_VANTARIS_IBMS-ibms_backend.zip` (~22M) | Archive | Do not commit |

---

## 4. Secret Pattern Findings

Pattern scan (password, secret, private_key, token, JWT, mysql+pymysql, mqtt, Bearer, etc.) — **paths and categories only; values redacted.**

| Path | Pattern category | Risk |
|---|---|---|
| `ibms_backend/src/common/config/default.py` | DB credentials, JWT secret, MQTT broker host, DID private key | **P0** — real-looking literals in source |
| `ibms_backend/src/common/utils/jwt_util.py` | JWT create/verify helpers | Low (logic); depends on config secret |
| `ibms_backend/src/api/system/system_api.py` | JWT on system routes | Auth surface |
| `ibms_backend/src/api/did/did_api.py` | DID login, VC/VP, JWT on `/did/me` only | Partial protection vs current backend |
| `ibms_backend/src/Iot/*`, `testMQTT/*` | MQTT client usage | Broker creds from config |
| `ibms_front/src/utils/request.js` | Bearer token header, base URL | Token transport + prod URL default |
| `ibms_front/src/api/system_api.js`, `did_api.js` | API client calls | Depends on backend auth contract |
| `ibms_front/src/router/index.ts` | `requiresAuth` meta (login only) | No route guard enforcement observed |
| Various `ibms_front/src/views/**/*.vue` | Example Bearer/API placeholders in demo UI | Documentation/mock data — verify not real keys |
| `ibms_main/README.md` | None | No secrets |

**Note:** `git grep` does not index untracked source folders; scan used direct file inspection and ripgrep on disk.

---

## 5. Handling Rules

- real `.env` must not be committed
- model/data/video artifacts must not enter split runtime packages unless explicitly approved
- credentials must be externalized (follow `AN_VANTARIS_IBMS-backend` A2–A5 security pattern)
- source migration must not copy secrets from `ibms_backend/src/common/config/default.py`
- IDE folders (`.idea/`) and `__pycache__` must not enter canonical packages
- zip backups at repo root remain reference-only; add to ignore policy in split batch if needed
- frontend production API URL must move to build-time env before any staging deploy
