# IBMS Frontend A7 Migration Risk Review

## 1. Hardcoded API risk

- Raw `request.js` defaults to production `https://ibms.aegisnx.com/api`
- Many views embed demo API URLs in IntegrationHub/DeveloperCenter
- **Rule:** reject any migrated file retaining absolute API host

## 2. Token handling risk

- Raw Login stores token in localStorage without route guards (pre-A2)
- Target has guards + extractAccessToken — migrated pages must use `persistLoginSession` only

## 3. Route guard risk

- Raw router has ~4600 lines without auth enforcement
- Target routes must set `requiresAuth` / `permissions` meta per page group

## 4. Heavy dependency risk

| Package | Risk | Mitigation |
|---|---|---|
| echarts | Large bundle | Lazy import per chart page |
| three | Very large | Isolate digital-twin routes |
| ethers | Security supply-chain | Pin version; audit |
| @vue-flow | Complex graphs | Migrate IntegrationHub last |
| xlsx | Parse vulnerabilities | Server-side export preferred |

## 5. Asset bloat risk

- `src/images/` drives ~200M raw size
- **Rule:** no bulk copy; CDN or Git LFS with review
- `video.mp4` in raw backend testMQTT must not enter frontend

## 6. Backend permission mismatch risk

- UI pages may call APIs user lacks permission for → 403
- Coordinate with permission seed (DB-B1) before IoT/DID/modeling migration
- Show 403 page; do not silently fail

## 7. Recommended safe migration batch size

| Batch size | Guideline |
|---|---|
| **≤10 `.vue` files** | Preferred per PR/commit |
| **≤15 `.vue` files** | Maximum without architecture review |
| **>15 files** | Split by subfolder or stop and replan |
| **1 dependency addition** | Separate commit with A0-deps review |

## 8. Non-scope

- No files migrated in A7
- No npm install
- No backend changes
