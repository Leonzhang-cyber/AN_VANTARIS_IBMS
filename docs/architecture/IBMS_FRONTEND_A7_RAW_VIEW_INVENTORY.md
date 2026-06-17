# VANTARIS IBMS Frontend A7 Raw View Inventory

## 1. Task Scope

- inventory only
- no raw source copied
- no target source changed
- no npm install/build/dev executed

Source: `AN_VANTARIS_IBMS-ibms_front/` (read-only, gitignored)  
Scan date: relative to commit `a24cff2`

---

## 2. Raw Vue View Summary

| Metric | Value |
|---|---|
| **Total `.vue` under `src/`** | **758** |
| **Top-level view directories** | **39** (+ root `.vue` files) |
| **Largest module (by file count)** | `SystemsDevices` (67) |
| **Largest module (by disk)** | `SystemsDevices` (~2.7M), `IntegrationHub` (~2.2M), `DataCenterOperations` (~2.2M) |
| **Bulk disk outside views** | `src/images/` (~majority of 200M package) |
| **Dedicated API modules in raw** | `system_api.js`, `did_api.js` only |
| **API usage in views** | Mostly UI shells; few wired API calls |

### Top-level directories (`src/views/`)

`AIVideoAnalytics`, `Administration`, `Alarm`, `AlarmsEvents`, `AssetIntelligence`, `Blockchain`, `Carbon`, `CommandCenter`, `DataCenterOperations`, `DataPlatform`, `DecisionEvidence`, `DeveloperCenter`, `Device`, `DigitalTwin`, `DigitalTwinOpenbim`, `Energy`, `EnergySustainability`, `FacilityServices`, `FaultManagement`, `FaultManagementSystem`, `Home`, `IntegrationHub`, `Intelligence`, `Login`, `Maintain`, `Maintenance`, `OperationalAssistance`, `Operations`, `Prediction`, `Property`, `Report`, `ReportsBi`, `SecurityCompliance`, `Settings`, `Sites`, `SitesSpaces`, `Support`, `SystemsDevices`, `TrustIdentity`, `layout`

Root view files: `Dashboard.vue`, `Device.vue`, `DeviceEnergy.vue`, `Home.vue`, etc.

### Major module groups (logical)

| Group | Raw folders | Approx `.vue` count |
|---|---|---|
| **Dashboard / Home** | Home, CommandCenter, Dashboard.vue | ~42 |
| **System / Admin** | Administration, Settings, SecurityCompliance | ~42 |
| **IoT / Devices** | SystemsDevices, Device, IntegrationHub, AlarmsEvents | ~163 |
| **DID / Trust** | Blockchain, TrustIdentity | ~25 |
| **Modeling / AI** | Intelligence, Prediction, AIVideoAnalytics | ~67 |
| **Operations** | Operations, Maintenance, DataCenterOperations, FacilityServices, Energy* | ~150+ |
| **Assets / Digital twin** | DigitalTwin*, AssetIntelligence, Sites* | ~50+ |
| **Login / Layout** | Login, layout | 2 |

### Likely heavy dependency pages

| Dependency | Likely raw folders |
|---|---|
| **echarts** | Home, Operations, Energy, ReportsBi, Intelligence |
| **three.js** | DigitalTwin, DigitalTwinOpenbim |
| **ethers / web3** | Blockchain, TrustIdentity |
| **leaflet** | Sites, SitesSpaces |
| **@vue-flow** | IntegrationHub, DeveloperCenter |
| **xlsx** | DataPlatform, Report |

---

## 3. Candidate Module Groups

| Raw Path Pattern | Candidate Target Module | Priority | Notes |
|---|---|---|---|
| `views/Home/**`, `Dashboard.vue`, `CommandCenter/**` | `dashboard` + `operations` | P1 | Entry UX; migrate after login/layout |
| `views/Administration/**`, `Settings/**`, `SecurityCompliance/**` | `src/modules/system` | P1 | Align with `systemApi`, `menuApi` |
| `views/Login/**`, `layout/**` | target `LoginView` + `AppLayout` | **Done (A5/A6)** | Do not copy raw |
| `views/Blockchain/**`, `TrustIdentity/**` | `src/modules/did` | P2 | ethers-heavy; defer until dep review |
| `views/SystemsDevices/**`, `Device/**`, `IntegrationHub/**` | `src/modules/iot` | P2 | Largest count; mostly UI shells |
| `views/AlarmsEvents/**`, `FaultManagement*/**` | `src/modules/iot` (ops sub) | P3 | Cross-cutting alarms |
| `views/Intelligence/**`, `Prediction/**`, `AIVideoAnalytics/**` | `src/modules/modeling` | P2 | Needs `modelingApi`; chart deps |
| `views/Operations/**`, `Maintenance/**`, `DataCenterOperations/**` | `src/modules/operations` | P3 | Large vertical modules |
| `views/Energy/**`, `EnergySustainability/**`, `Carbon/**` | `src/modules/operations` | P3 | Domain-specific |
| `views/DataPlatform/**`, `ReportsBi/**`, `Report/**` | `src/modules/operations` | P4 | xlsx/echarts |
| `views/DigitalTwin*/**`, `Sites*/**` | `assets review` + `operations` | P4 | three/leaflet + assets |
| `views/DeveloperCenter/**` | `src/modules/system` (sandbox) | P4 | Mock API examples — sanitize URLs |
| `src/images/**` | CDN / LFS / Storage | P5 | ~200M; never bulk copy |

---

## 4. Analysis Artifacts (raw)

- `views_analysis_report.txt` — 587 planned / 748 exist / 43 missing
- `missing_files_list.txt` — gap list for router vs files

Use during FRONTEND-A8+ route migration planning only.
