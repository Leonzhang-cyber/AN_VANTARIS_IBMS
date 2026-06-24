# SERVER-PRECHECK-R13F Console GA Runtime Verification Final Review

PASS marker: ONE_SERVER_PRECHECK_R13F_CONSOLE_GA_RUNTIME_VERIFICATION_FINAL_REVIEW_PASS

## Purpose

SERVER-PRECHECK-R13F is the final review and closure layer for SERVER-PRECHECK-R13 Console International GA Menu Runtime Verification.

It determines whether the R13 runtimeVerificationDecision can move from HOLD to GO for downstream R14F reevaluation. R13F records the review model only and does not deploy, connect to servers, execute SSH, run frontend/backend/runtime commands, or mutate implementation.

## Scope

R13F is documentation, registry JSON, evidence JSON, validation JSON, final verification JSON, validator, and local release index documentation only.

It closes the R13 HOLD causes for Sidebar collapse / expand, route/page availability, international brand menu, IBMS upgraded menu, role-based visibility, reviewer model, and approver model.

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
- No production healthcheck execution.
- No production smoke test execution.
- No APP-to-DB live connection test.
- No server mutation.
- No DB mutation.
- No auth mutation.
- No runtime mutation.
- No frontend mutation.
- No backend mutation.
- No route mutation.
- No menu implementation mutation.
- No production config mutation.
- No production credential storage in public files.

## Relationship with MENU-GA-R1/R2

MENU-GA-R1 defines the International Menu Architecture baseline.

MENU-GA-R2 defines route coverage and Sidebar/L3 behavior audit evidence.

R13F references MENU-GA-R1/R2 as the baseline for Dashboard naming, L1/L2 Sidebar behavior, L3 content-area metadata behavior, visible route coverage, duplicate route audit, duplicate menu audit, international brand menu coverage, and IBMS domain menu mapping.

## Relationship with R13 and R14

SERVER-PRECHECK-R13 created the Console International GA Menu Runtime Verification model with runtimeVerificationDecision set to HOLD.

SERVER-PRECHECK-R14 created the APP/DB Deployment Execution Approval Gate with deploymentExecutionApprovalDecision set to HOLD because R13 was required.

R13F closes R13 HOLD items before R14F can reevaluate deployment approval.

If R13F decision remains HOLD or NO-GO, R14F must remain HOLD or NO-GO.

If R13F decision becomes GO, R14F can reevaluate deploymentExecutionApprovalDecision.

## R13 HOLD Closure Model

R13F closes these R13 HOLD causes:

- Sidebar collapse / expand not fully confirmed: closed by final review PASS.
- Route/page availability not fully confirmed: closed by final review PASS.
- International brand menu review incomplete: closed by final review PASS.
- IBMS upgraded menu review incomplete: closed by final review PASS.
- Role-based visibility review incomplete: closed by final review PASS.
- Reviewer / approver not finalized: closed by review-model acceptance and GO approval status.

## Sidebar Collapse / Expand Final Review

Sidebar collapse control is present. Collapse / expand behavior is reviewed. Collapse / expand does not break L1/L2 visibility rules. L3 remains outside Sidebar after collapse / expand.

## Route and Page Availability Final Review

Route coverage references MENU-GA-R2. Duplicate route audit passed. Duplicate menu audit passed. Visible routes have pages or GA-compliant placeholders. No visible route is recorded as leading to a broken page state.

## International Brand Menu Final Review

Coverage or justified placement is reviewed for VANTARIS One, VANTARIS Console, VANTARIS Link, VANTARIS Edge, VANTARIS Code, VANTARIS DB, and VANTARIS Nexus AI.

International GA menu remains business-domain oriented. Brand/product names do not need to be forced into L1 and may appear as L2, package entries, workspace cards, admin package entries, or engineer workspace entries where appropriate.

## IBMS Upgraded Menu Final Review

Coverage or domain mapping is reviewed for Operations, Sites & Spaces, Systems & Devices, Alarms & Events, Fault Management, Maintenance, Energy & Sustainability, Facility Services, Data Center Operations, Decision & Evidence, Command Center, Intelligence, AI Video Analytics, Digital Twin, Reports, Trust & Identity, and Administration.

IBMS upgraded menu is mapped into the International GA domain menu and does not need to appear as a flat L1 list.

## Role-based Visibility Final Review

Customer, Engineer, and Admin roles are reviewed.

Customer does not see restricted deployment content. Customer does not see restricted evidence content. Engineer can see setup / diagnostics / deployment-readiness workspaces only where allowed. Admin can see package / role / tenant / entitlement / governance menus. No role boundary violations are detected.

## Forbidden Language Final Review

GA-visible menu/page text is reviewed for Mock, Demo, Pilot, and Coming soon. No blocker is recorded.

Forbidden terms in internal documentation or policy examples are not treated as GA-visible failures.

## Restricted Evidence Handling Final Review

Production screenshots, customer hostnames, private IPs, usernames, emails, and sensitive runtime evidence are not stored in public packets. Restricted evidence remains reference-only.

## Reviewer and Approver Requirements

R13F requires a reviewer model and an approver model. The final review evidence records reviewer acceptance and approver GO for the documentation-only R13F closure model.

## R14F Dependency Rule

R13F is required before R14F can move deploymentExecutionApprovalDecision to GO.

R13F GO allows R14F to reevaluate deploymentExecutionApprovalDecision. It does not itself authorize deployment, SSH, server access, APP/DB connection, build, runtime action, or server mutation.

## GO / HOLD / NO-GO Final Review Rules

HOLD applies if any final review section remains incomplete, any status remains HOLD, reviewer is missing, approver is missing, or runtimeVerificationFinalDecision is not finalized.

GO applies only if Sidebar collapse / expand final review passed, route/page availability final review passed, international brand menu final review passed, IBMS upgraded menu final review passed, role-based visibility final review passed, forbidden language final review passed, restricted evidence handling final review passed, no mutation occurred in R13F, reviewer accepted, and approver status is GO.

NO-GO applies if Home appears as primary L1, L3 appears in Sidebar, Sidebar L1/L2 behavior is broken, visible menu routes are broken without GA-compliant placeholder, forbidden GA-visible language is detected, unauthorized role visibility is detected, production sensitive evidence leaks into a public packet, frontend/backend/routes/menu implementation was mutated by R13F, reviewer rejected, or approver status is NO-GO.

## Validator Requirements

The validator must check required files, JSON parseability, references to MENU-GA-R1/R2, R13, and R14, R14F dependency fields, false execution/mutation flags, Sidebar collapse / expand final review, route/page availability final review, international brand coverage, IBMS upgraded menu coverage, role-based visibility, forbidden language flags, restricted evidence flags, runtimeVerificationFinalDecision, PASS marker presence, source markers, and absence of executable server or runtime operation steps.

## Boundary Statement

SERVER-PRECHECK-R13F records a final review model only.

It does not execute SSH, create SSH automation, include SSH connection commands, create executable scripts, connect to APP/DB servers, execute server/build/npm/node/frontend/backend/Nginx/PM2 commands, run production healthcheck or smoke tests, test APP-to-DB live connectivity, deploy, install, mutate server, DB, auth, runtime, frontend, backend, routes, menu implementation, production config, or store production credentials in public files.

## PASS Marker

ONE_SERVER_PRECHECK_R13F_CONSOLE_GA_RUNTIME_VERIFICATION_FINAL_REVIEW_PASS
