# SERVER-PRECHECK-R13 Console International GA Menu Runtime Verification

PASS marker: ONE_SERVER_PRECHECK_R13_CONSOLE_INTERNATIONAL_GA_MENU_RUNTIME_VERIFICATION_PASS

## Purpose

SERVER-PRECHECK-R13 defines the Console International GA menu runtime verification packet required before SERVER-PRECHECK-R14 can be reconsidered for GO.

R13 verifies the menu runtime readiness model for international GA. It does not perform live server access, production deployment, runtime execution, build execution, or frontend/backend/route mutation.

## Scope

R13 is documentation, registry JSON, evidence JSON, validation JSON, validator, final verification note, and release-index documentation only.

It defines verification criteria for Dashboard naming, L1/L2 Sidebar behavior, L3 content-area menu behavior, Sidebar collapse / expand, route/page availability, international brand menu entries, IBMS upgraded menu entries, role-based visibility, forbidden language scan, restricted evidence handling, relationship to MENU-GA-R1/R2, and downstream closure for R14.

## Non-goals

- No SSH execution.
- No SSH automation.
- No SSH connection command.
- No executable shell script.
- No APP server connection.
- No DB server connection.
- No server command execution.
- No deployment.
- No install.
- No runtime installation.
- No build execution.
- No npm execution.
- No Node execution.
- No backend execution.
- No frontend execution.
- No Nginx execution.
- No PM2 execution.
- No healthcheck execution against production.
- No smoke test execution against production.
- No APP-to-DB live connection test.
- No server mutation.
- No DB mutation.
- No auth mutation.
- No runtime mutation.
- No frontend mutation.
- No backend mutation.
- No route mutation.
- No production config mutation.
- No production credential storage in public files.

## Relationship with MENU-GA-R1/R2

MENU-GA-R1 defines the international menu architecture baseline.

MENU-GA-R2 defines route coverage and Sidebar/L3 behavior audit.

R13 records the Console International GA menu runtime verification model that depends on MENU-GA-R1/R2 and completes the missing dependency required by R14.

## Relationship with R1-R14

- R1: Dual-server read-only audit.
- R2: Read-only access window plan.
- R3: Actual read-only observation plan.
- R4: Read-only SSH execution approval packet.
- R5: Actual read-only observation entry gate.
- R6: Manual read-only observation command pack.
- R7: Human approval record and observation window lock.
- R8: Manual observation evidence packet.
- R9: Actual read-only observation evidence record.
- R10: Deployment readiness gate.
- R11: DB server deployment preparation pack.
- R12: APP server deployment preparation pack.
- R13: Console International GA Menu Runtime Verification.
- R14: APP/DB deployment execution approval gate.

## Console International GA Menu Runtime Verification Model

R13 records Dashboard naming, Sidebar L1/L2 behavior, L3 content-area navigation, collapse / expand behavior, route/page availability, international brand menu, IBMS upgraded menu, role visibility, forbidden language, restricted evidence handling, reviewer, approver, and runtime verification decision.

## Dashboard Naming Verification

Dashboard is the primary L1 name. Home must not be used as the primary L1 menu. Dashboard naming follows MENU-GA-R1.

## Sidebar L1/L2 Verification

L1 is displayed in Sidebar. L2 is displayed in Sidebar. L3 is excluded from Sidebar.

## L3 Content-area Navigation Verification

L3 is displayed at the top of the content area, belongs to the same page layout as content, and must not become Sidebar items.

## Sidebar Collapse / Expand Verification

Sidebar collapse / expand behavior is required. This packet records the verification model and does not execute a live production runtime test.

## Route and Page Availability Verification

Visible routes must have a page or GA-compliant placeholder. Route coverage remains referenced to MENU-GA-R2.

## International Brand Menu Verification

R13 defines review fields for VANTARIS One, VANTARIS Console, VANTARIS Link, VANTARIS Edge, VANTARIS Code, VANTARIS DB, and VANTARIS Nexus AI.

Brand/product names do not need to be forced into L1. International GA menu should remain business-domain oriented.

## IBMS Upgraded Menu Verification

R13 defines coverage verification for Operations, Sites & Spaces, Systems & Devices, Alarms & Events, Fault Management, Maintenance, Energy & Sustainability, Facility Services, Data Center Operations, Decision & Evidence, Command Center, Intelligence, AI Video Analytics, Digital Twin, Reports, Trust & Identity, and Administration.

IBMS upgraded menu can be mapped into the international GA domain menu and does not need to appear as a flat L1 list.

## Role-based Visibility Verification

R13 covers Customer, Engineer, and Admin visibility. Customer sees customer-operational menus only. Engineer sees setup / diagnostics / deployment-readiness workspaces where allowed. Admin sees package, role, tenant, entitlement and governance menus. No role should expose unauthorized deployment or restricted evidence content.

## Forbidden Language Verification

R13 defines a GA-visible menu/page text scan for Mock, Demo, Pilot, and Coming soon. Policy mentions in internal documentation must not be treated as GA-visible failures.

## Runtime Evidence and Restricted Evidence Rules

Production screenshots are not stored in public packets by default. Customer hostnames, private IPs, usernames, emails, server names, and sensitive production paths must be redacted. Runtime evidence can be represented by restricted evidence references.

## R14 Dependency Closure Rules

R13 is required by R14. This R13 packet records r13Completed as true for dependency-closure purposes and allows R14 to be reevaluated after R13. It does not change R14's committed HOLD decision.

## GO / HOLD / NO-GO Verification Rules

HOLD applies if Sidebar collapse/expand behavior is not verified, visible route/page availability is incomplete, international brand review is incomplete, IBMS upgraded menu review is incomplete, role visibility review is incomplete, reviewer is missing, or approver is missing.

GO applies only if Dashboard naming, L1/L2 Sidebar, L3 content-area navigation, Sidebar collapse/expand, route/page availability, international brand menu, IBMS upgraded menu, role-based visibility, forbidden language scan, restricted evidence handling, reviewer acceptance, and approver GO are complete.

NO-GO applies if Home appears as primary L1, L3 appears in Sidebar, L1/L2 Sidebar behavior is broken, visible menu routes are broken without GA-compliant placeholder, forbidden GA-visible language is detected, unauthorized role visibility is detected, sensitive production evidence leaks into a public packet, reviewer rejected, or approver status is NO-GO.

## Validator Requirements

The validator must check required files, JSON parseability, MENU-GA-R1/R2 reference, R10/R11/R12/R14 references, R14 dependency closure fields, false execution and mutation flags, Dashboard naming flags, Sidebar/L3 flags, forbidden language flags, restricted evidence flags, runtimeVerificationDecision model, source markers, forbidden executable operation blocks, and the PASS marker.

## Boundary Statement

SERVER-PRECHECK-R13 records a Console International GA menu runtime verification model only.

It does not execute SSH, create SSH automation, include SSH connection commands, create executable scripts, connect to APP/DB servers, execute server/build/npm/node/frontend/backend/Nginx/PM2 commands, run production healthcheck or smoke tests, test APP-to-DB live connectivity, deploy, install, mutate server, DB, auth, runtime, frontend, backend, routes, production config, or store production credentials in public files.

## PASS Marker

ONE_SERVER_PRECHECK_R13_CONSOLE_INTERNATIONAL_GA_MENU_RUNTIME_VERIFICATION_PASS
