# VANTARIS ONE UI UConsole Information Architecture R1

## UConsole Role

UConsole is the customer/operator/engineer/admin entry surface for VANTARIS ONE. It is a control surface, not a direct device-control runtime. UConsole does not bypass the CODE layer.

## Top-Level Navigation Proposal

- Home
- Command Center
- Work Management
- Assets & Topology
- Faults & Events / UFMS
- Maintenance / UMMS
- Energy & Sustainability / UESG
- Decision & Evidence / UCDE
- Documents / UDOC
- Reports & Analytics
- NEXUS AI
- Integration / EDGE / LINK
- Governance & Security
- Administration
- Customer Delivery / Installer

## L1/L2/L3 Rule

- Sidebar only shows L1 and L2 navigation.
- L3 tasks live inside the page as tabs, panels, tables, drawers, or workflow steps.
- Deep operational actions must remain visible through breadcrumbs, page headers, and audit context rather than sidebar sprawl.

## Engineer-Only Installer UI

The installer UI is visible only to entitled engineers/admins. It exposes precheck, dry-run install, verify, rollback dry-run, package integrity, DB plan, topology, and acceptance evidence. It does not execute production activation without approval gates.

## Customer-Facing Delivery UI

The customer delivery UI shows package readiness, acceptance checklist, deployment topology, evidence package, pending approvals, and activation blocked state. Customer users can review and sign where authorized, but cannot bypass engineering/security gates.

## Package State Model

- Locked: package exists but is not entitled or visible.
- Entitled: customer contract allows package access.
- Installed: package is present in the approved environment.
- Enabled: package is configured for use under policy.
- Visible: package appears in UConsole navigation for the role.
- Not activated: runtime or production execution remains blocked.

## Module Readiness Badge

- GA-ready: evidence supports declared GA scope.
- Freeze: capability is frozen/read-only but needs full GA acceptance.
- Scaffold: structure exists but production execution is not complete.
- Incomplete: missing module evidence or final capability work.
- Not activated: installed or delivered artifacts are blocked from runtime activation.

## Production Label Rule

No mock/demo/pilot labels are allowed in production UI. Non-production states must be represented as readiness, entitlement, activation, or evidence status instead.

PASS marker: `ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS`
