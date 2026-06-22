# VANTARIS ONE Full Product Design Blueprint R1

## Executive Summary

VANTARIS ONE is a cross-industry unified operations platform. It is not an airport-only system. Airport, data center, smart building / IBMS, utility, and facility deployments are industry projections that sit on a shared platform foundation.

R1 consolidates the product definition, platform layers, runtime boundaries, editions, deployment modes, and GA decision state from the current branch. The evidence supports a strong foundation package GA and offline customer delivery scaffold, but does not support declaring full customer production activation or full international GA across all modules.

## Product Definition

VANTARIS ONE provides a unified operations model for assets, events, work, evidence, analytics, governance, and integration. Industry-specific products are projections over the common layers, not forks of the platform:

- Airport projection: source-system onboarding, alarm/event intake, HMI/asset locator, operator review, work-order intent, delivery evidence.
- Data Center projection: critical infrastructure topology, power/cooling telemetry, incident correlation, maintenance windows, evidence retention.
- Smart Building / IBMS projection: BMS/ELV integration, comfort/energy operations, contractor workflows, tenant and operator dashboards.
- Utility / Facility projection: field asset health, service dispatch, compliance evidence, offline/edge continuity.

## Layered Architecture

- UConsole presentation layer: operator, engineer, admin, and customer-facing control surface.
- UCode / CODE API execution layer: backend API boundary, integration API, request validation, execution boundary.
- ONE Orchestrator coordination layer: workflow coordination, escalation, package orchestration, and read-only orchestration plans.
- Automated Rules & Policy layer: rule evaluation, thresholds, SLA logic, entitlement guardrails, and policy registry.
- NEXUS AI decision/context layer: advisory triage, recommendation, model selection, and risk scoring.
- Domain modules: UMMS, UFMS, UESG, UCDE, UDOC.
- Foundation packages: EDGE, LINK, DB, Contracts.
- Reports & Analytics: dashboards, exports, trends, and executive/operations reporting.
- Governance & Security: RBAC, audit, approval workflow, policy enforcement, IEC62443 posture, route enforcement.

## Deployment Modes

- All-in-one: UConsole, CODE, domain modules, EDGE/LINK foundation, and DB on a single approved host for constrained environments.
- Single server: application and DB co-located with explicit backup and restore policy.
- App + DB split: application tier separated from PostgreSQL for enterprise operations.
- Multi-edge + central link: multiple EDGE collectors and buffers hand off to a central LINK gateway and CODE layer.
- Offline customer delivery: package delivery, checksum, dry-run installer, verify flow, rollback dry-run plan, acceptance evidence.

## Runtime Boundaries

- UConsole never directly controls device operations; it submits requests through CODE and approved workflows.
- NEXUS AI never executes device control; it remains advisory/control-plane context only.
- EDGE/LINK package artifacts are not activated unless an approved customer activation gate exists.
- DB migrations require explicit approval, backup confirmation, and a deployment window.
- Contracts are the schema source for envelopes, OpenAPI surfaces, and package handoff data.
- Package content remains immutable during this design task.

## Product Editions

- Lite: single-site read-only operations, core UConsole, basic reports, limited integration package visibility.
- Professional: multi-module operations, UFMS/UMMS workflows, dashboards, customer delivery evidence, governance basics.
- Enterprise: multi-edge topology, package entitlement, audit evidence, HA-oriented deployment patterns, advanced reports.
- AI / Advanced Governance: NEXUS AI advisory workflows, model selection, risk scoring, policy analytics, extended approval chains.

## Industry Projections

- Airport: ELV/source-system integration, alarm/event management, HMI locator, operator review, maintenance handoff.
- Data Center: facilities telemetry, incident correlation, asset topology, maintenance and compliance evidence.
- Smart Building / IBMS: BMS/ELV operations, energy optimization, tenant/customer reporting, work management.
- Utility / Facility: distributed assets, offline handoff, service evidence, governance and safety gates.

## Current Readiness Status From R10

- Foundation package GA: PASS
- Offline export package: PASS
- Customer delivery scaffold: PASS
- Full customer production activation: NOT EXECUTED
- Full international GA across all modules: NOT YET

Package counts at R10: EDGE 248, LINK 153, DB 14, Contracts 174.

## Final Conclusion

Platform foundation package GA PASS. Full international GA across all modules NOT YET. Full customer production activation NOT EXECUTED.

PASS marker: `ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS`
