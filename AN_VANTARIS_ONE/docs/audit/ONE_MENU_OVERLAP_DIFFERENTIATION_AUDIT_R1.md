# ONE Menu Overlap Differentiation Audit R1

## 1. Executive Summary

This audit reviewed the VANTARIS ONE menu and Dashboard L3 rendering support for overlap, ambiguity, stale naming, customer differentiation, and airport-specific projection risk.

VANTARIS ONE remains structured as a cross-industry platform with 12 L1 domains, 109 L2 entries, and 825 L3 entries. The core menu architecture is directionally sound: Dashboard is positioned as a decision layer, Command Center as live handling, Work Management as execution, Assets & Locations as operational object context, Integration & Partner Hub as connector and partner operations, Reports & Documents as evidence output, Governance & Security as control and accountability, and Industry Solutions as industry projection.

The main risks are not structural L1/L2 failures. They are wording boundary risks caused by similar operational nouns appearing across domains: action, evidence, governance, risk, audit, service impact, work order, integration, and airport. These overlaps are mostly acceptable when explained as role-based reuse, but several labels need future tightening so customers do not confuse dashboard summaries with execution consoles, reports with governance control, or airport projection with platform identity.

No code changes were made by this audit.

## 2. Scope and Source Files

Audited source files:

- `AN_VANTARIS_IBMS-frontend/src/services/menu/static-menu.ts`
- `AN_VANTARIS_IBMS-frontend/src/services/menu/l3-content-registry.ts`
- `AN_VANTARIS_IBMS-frontend/src/components/RouteL3ContentPanel.vue`

Read-only reference:

- `AN_VANTARIS_IBMS-frontend/src/views/DashboardPlaceholder.ts`

The audit treated source code as read-only and created documentation only under:

- `AN_VANTARIS_ONE/docs/audit/`

## 3. L1 / L2 / L3 Baseline Counts

| Level | Count | Status |
| --- | ---: | --- |
| L1 domains | 12 | Matches expected baseline |
| L2 entries | 109 | Current menu coverage baseline |
| L3 entries | 825 | Includes Airport ELV / MMS / IBMS coverage additions |

Current L1 baseline:

1. Dashboard
2. Command Center
3. Assets & Locations
4. Work Management
5. Faults & Events
6. Energy & Sustainability
7. Data & Intelligence
8. Reports & Documents
9. Governance & Security
10. Integration & Partner Hub
11. Industry Solutions
12. Administration

## 4. High-risk Ambiguity Findings

| ID | Area | Finding | Risk | Recommendation |
| --- | --- | --- | --- | --- |
| H-001 | Dashboard Workspace Overview | `static-menu.ts` still stores legacy Workspace Overview L3 labels while the registry maps display labels. | Customers may see old labels if any route bypasses the display-label registry. | Keep display-label override as current render path; later align `static-menu.ts` labels once menu baseline freeze allows a rename. |
| H-002 | DashboardPlaceholder stale route | `DashboardPlaceholder.ts` contains old connected workspace names: UMMS Maintenance, Assets & Topology, Evidence Center, Reports Center, UESG Sustainability. | If this placeholder is still routable, it can contradict ONE naming and imply package-level navigation. | Replace or retire DashboardPlaceholder in a later UI cleanup task; do not use it as GA customer-facing Dashboard content. |
| H-003 | Work Management vs Faults & Events | Fault Remediation Control includes Work Order Creation, Closure Notes, Closure Evidence while Work Management owns Work Order Control and Closure Evidence. | Users may treat Faults & Events as the place to execute and close work rather than diagnose and initiate handoff. | Rename fault-side labels toward recommended remediation and handoff intent, then reserve execution closure for Work Management. |

## 5. Medium-risk Overlap Findings

| ID | Area | Finding | Risk | Recommendation |
| --- | --- | --- | --- | --- |
| M-001 | Dashboard vs Command Center | Dashboard Operations Snapshot and Service Risk use actions such as Service Recovery Actions and SLA Mitigation Actions. | Dashboard can look like a full command console if action language is too executable. | Use summary wording such as Recovery Priority Entry or Mitigation Recommendation Entry in Dashboard. |
| M-002 | Dashboard Industry View vs Industry Solutions | Dashboard Industry View includes Industry KPI Actions, Industry Risk Governance, and Industry Evidence Pack. | It can appear to duplicate full Industry Solutions package management. | Clarify Dashboard Industry View as active profile summary and readiness snapshot. |
| M-003 | Reports vs Governance | Report Center and Export & Evidence Center include Report Governance Audit and Export Audit. | Users may confuse evidence export history with policy/audit control ownership. | Keep Reports for produced artifacts; move permission/rule authority wording to Governance. |
| M-004 | Governance vs Vendors | Vendors and Risk & Control Register both contain Vendor Responsibility Matrix and SLA/contract wording. | Contract execution and contract governance ownership may blur. | Vendors should show operational contract scope and contacts; Governance should show control, approval, and accountability. |
| M-005 | Assets vs Integration | Controller & Gateway Health appears under Assets & Locations while Protocol & Gateway Operations appears under Integration. | Gateway health can look like both an asset object and connector operation. | Keep Assets for installed gateway object/location; Integration for protocol runtime and connector state. |
| M-006 | Asset Graph vs Digital Twin vs HMI Map | Mapping, relationship, spatial, and HMI words overlap across Asset Graph, Digital Twin, Floor Plan / HMI Map, and Space Mapping. | Users may not know which view locates equipment versus shows relationships versus visualizes scenarios. | Add future microcopy or L3 wording clarifying physical location, object relationship, and scenario visualization. |
| M-007 | Integration connectors vs Industry Solutions Airport | Industry Connectors lists ELV source systems while Airport lists Airport ELV Systems Integration. | Airport may be interpreted as the only ELV integration domain. | Keep Airport as projection; present ELV source systems as reusable connector coverage. |
| M-008 | Evidence appears everywhere | Evidence Pack / Evidence Timeline / Evidence Export / Evidence Audit appear across most L1 domains. | Customers may ask which evidence entry is authoritative. | Explain evidence as a shared object, with each domain showing a different lifecycle stage. |
| M-009 | Legacy mapped module names | Internal mapped modules include names such as UmmsMaintenance, UesgSustainability, AssetsTopology, EvidenceCenter. | Low direct customer risk today, but leaks through debugging or fallback UI could confuse sales/demo narratives. | Keep internal-only for now; later introduce ONE-facing display names wherever mapped module names are rendered. |

## 6. Acceptable Overlap / Role-based Reuse

The following overlaps are acceptable when presented as different operational stages:

- Evidence: a shared object that appears in operations, work, reports, and audit.
- Risk: a shared decision signal that appears in Dashboard, Command Center, Faults, Governance, and Industry Solutions.
- Work order references: acceptable in Faults & Events as source/linked context; authoritative execution belongs to Work Management.
- Partner/SLA references: acceptable in Integration, Vendors, Reports, and Governance when each domain keeps its responsibility boundary.
- Airport labels: acceptable under `Industry Solutions -> Airport` and as an industry projection, not as a platform-wide identity.

## 7. Legacy Naming and Stale Copy Findings

Search results found these notable terms:

| Text | Location | Classification | Customer-visible risk |
| --- | --- | --- | --- |
| Workspace Risk Signal and related old Workspace Overview L3 labels | `static-menu.ts`, `l3-content-registry.ts` | Menu label / internal mapping | Medium if displayLabel override is bypassed |
| `is a Dashboard workbench section` | `l3-content-registry.ts` fallback subtitle | Template copy | Low; only affects unmapped dashboard sections |
| UMMS Maintenance | `DashboardPlaceholder.ts` | Read-only stale placeholder | High if placeholder route remains customer-visible |
| Assets & Topology | `DashboardPlaceholder.ts` | Read-only stale placeholder | High if placeholder route remains customer-visible |
| Evidence Center | `DashboardPlaceholder.ts`, mapped module references | Stale placeholder / internal mapping | Medium |
| Reports Center | `DashboardPlaceholder.ts` | Read-only stale placeholder | High if placeholder route remains customer-visible |
| UESG Sustainability | `DashboardPlaceholder.ts` | Read-only stale placeholder | High if placeholder route remains customer-visible |
| Placeholder | component name `DashboardPlaceholder` | Source component name | Low if not rendered |

No `Mock`, `Demo`, `MVP`, `Pilot`, or `Coming soon` customer-facing menu labels were found in the audited active menu file.

## 8. Airport ELV / MMS Coverage Differentiation

Airport coverage is now clearly present under `Industry Solutions -> Airport`, with L3 entries for Airport ELV Systems Integration, Airport MMS Operations, Airport Protocol Coverage, Airport Asset & Space Mapping, Airport Service Impact, Airport Evidence Pack, and Airport Handover Readiness.

The platform-level reusable capabilities remain outside the Airport L1/L2 path:

- ELV source systems and protocol health live under `Integration & Partner Hub`.
- Work orders, PM, inventory, vendors, dispatch, closure, and sign-off live under `Work Management`.
- Asset lifecycle, point/tag binding, HMI location, and graph relationships live under `Assets & Locations`.
- Evidence, reports, exports, and handover packages live under `Reports & Documents`.
- SLA governance, audit, permission, responsibility, and control ownership live under `Governance & Security`.

This division supports the product rule: VANTARIS ONE is cross-industry and not airport-only. Airport is an industry projection of shared platform capabilities.

## 9. Customer-facing Differentiation Explanation

Traditional IBMS shows connected systems and alarms.

Traditional MMS manages work orders and preventive maintenance.

Traditional ELV integration diagrams show source systems and protocol connections.

VANTARIS ONE connects systems, assets, faults, work orders, evidence, governance, and customer acceptance into one operational decision and accountability platform.

That means the same operational object may appear in several places:

- Dashboard shows what needs attention first.
- Command Center handles live command, escalation, and decision record.
- Faults & Events detects, correlates, diagnoses, and links the event context.
- Work Management dispatches, executes, closes, and signs off work.
- Reports & Documents produces evidence and customer-facing packages.
- Governance & Security controls permission, approval, audit, SLA, and responsibility.
- Industry Solutions packages the same platform capabilities for airport, data center, building, mall, oil and gas, coking plant, and industrial facility scenarios.

## 10. Recommended Fix Backlog

| Backlog_ID | Priority | Area | Problem | Recommended Fix | Files Expected To Change Later | Risk If Not Fixed |
| --- | --- | --- | --- | --- | --- | --- |
| B-001 | P0 | Dashboard placeholder | Old package names remain in read-only placeholder. | Retire or align DashboardPlaceholder route content with ONE naming. | DashboardPlaceholder or route owner files | Customer sees legacy product/package names. |
| B-002 | P1 | Workspace Overview menu labels | Static L3 labels differ from display labels. | Rename Workspace Overview L3 labels when baseline freeze allows. | `static-menu.ts`, registry mapping cleanup | Bypass paths show old labels. |
| B-003 | P1 | Faults vs Work | Remediation L3 contains work creation and closure language. | Reword Faults side to recommended action and handoff; keep closure in Work Management. | `static-menu.ts`, content registry | Users execute work from fault console. |
| B-004 | P1 | Reports vs Governance | Audit/export/permission words overlap. | Make Reports artifact-oriented and Governance control-oriented. | `static-menu.ts`, content registry | Unclear authority for evidence export and audit. |
| B-005 | P2 | Assets vs Integration | Gateway health appears in both object and connector contexts. | Add customer microcopy or L3 refinements separating installed object from connector operations. | `static-menu.ts`, content registry | Confusion over where to troubleshoot gateways. |
| B-006 | P2 | Visual asset views | Asset Graph, Digital Twin, Floor Plan / HMI Map, and Space Mapping share map/relationship terms. | Add differentiated descriptions in content registry and page cards. | `l3-content-registry.ts`, UI panel | Users cannot choose the right visual entry. |
| B-007 | P2 | Industry projection | Airport ELV and MMS coverage may look like product scope. | Add copy stating Airport is an industry projection of reusable ONE capabilities. | content registry, customer docs | Airportization risk in sales and delivery. |
| B-008 | Backlog | Internal mapped module names | Legacy module names can leak if fallback surfaces them. | Introduce ONE-facing mapped module display names. | menu services, content registry | Lower polish and naming consistency. |

## 11. No-code-change Confirmation

This audit created documentation only. It did not modify frontend source, backend source, routes, APIs, DB schema, deployment files, package files, or runtime configuration.
