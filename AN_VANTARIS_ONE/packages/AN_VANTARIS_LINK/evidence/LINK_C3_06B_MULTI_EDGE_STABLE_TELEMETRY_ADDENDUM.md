# LINK-C3-06B — Multi-EDGE and Stable Telemetry Evidence Addendum

Status: PASS
Scope: AN_VANTARIS_LINK only
Date: 2026-06-20

## 1. Purpose

This evidence addendum supplements LINK-C3 validation after two International
GA risks were identified:

1. Multiple EDGE gateways can concurrently enter LINK.
2. Stable unchanged telemetry from the same device / point can unnecessarily
   pressure LINK unless EDGE suppresses it and LINK remains duplicate-aware.

## 2. Related EDGE Follow-up

The following controlled EDGE follow-up was completed before this addendum:

- EDGE-C8-01 Stable Value Suppression and Change Detection Policy
- EDGE-C8-02 Stable Value Suppression Contract
- EDGE-C8-03 Stable Value Suppression Validation Harness
- EDGE-C8-04 Stable Value Suppression Evidence Closure

Current EDGE stable suppression result:

- EDGE_C8_04_STABLE_VALUE_SUPPRESSION_CLOSURE_PASS

EDGE runtime remains not enabled.

## 3. LINK Addendum Items

The following LINK validation harnesses were added:

- LINK-C3-05B Multi-EDGE Concurrent Queue Validation Harness
- LINK-C3-05C Stable Telemetry Duplicate Awareness Harness

Current HEAD before this evidence:

- 9d42e8e test(link): add stable telemetry duplicate awareness

## 4. Validation Commands

Commands executed:

- npm --prefix AN_VANTARIS_LINK run validate:c3-multi-edge
- npm --prefix AN_VANTARIS_LINK run validate:c3-stable-telemetry
- npm --prefix AN_VANTARIS_LINK run typecheck
- bash AN_VANTARIS_LINK/scripts/link-boundary-scan.sh
- git status --short

## 5. Validation Results

Results:

- Multi-EDGE concurrent queue validation: PASS
- Stable telemetry duplicate awareness validation: PASS
- LINK typecheck: PASS
- LINK boundary scan: PASS
- Git status: clean after generated dist-c3 cleanup
- EDGE runtime artifacts: not tracked
- UFMS DB/schema/auth/login/credentials: not modified

Validation markers confirmed:

- LINK_C3_05B_MULTI_EDGE_CONCURRENT_QUEUE_VALIDATION_PASS
- LINK_C3_05C_STABLE_TELEMETRY_DUPLICATE_AWARENESS_PASS

## 6. Multi-EDGE Coverage Confirmed

The multi-EDGE validation confirms:

- multiple gateways can be represented concurrently
- multiple tenants and sites can be represented
- telemetry, event, alarm, and health records can coexist
- alarm records enter CRITICAL priority lane
- telemetry records remain NORMAL priority lane
- gateway counts can be separated
- tenant counts can be separated
- partition assignment remains deterministic
- durable append records validate
- replay candidates can be identified
- duplicate eventId / payloadHash risk can be detected

## 7. Stable Telemetry Coverage Confirmed

The stable telemetry validation confirms:

- LINK can observe EDGE stable suppression metadata through normalizedPayload
- dedupeKey groups stable telemetry samples
- payloadHash groups stable unchanged samples
- suppressedCount can be accumulated for awareness
- stable telemetry remains NORMAL lane
- alarm records remain CRITICAL lane
- stable telemetry does not demote or block alarm priority
- durable queue append records still validate
- partition metadata still validates

## 8. Architecture Decision

EDGE is the first suppression layer.

LINK is the second protection layer.

UFMS remains the final business correlation layer.

Responsibilities:

- EDGE: stable value suppression, deadband, change-only, alarm repeat aggregation
- LINK: partition isolation, queue state, duplicate awareness, priority lanes, durable recovery
- UFMS: business-level correlation, alarm lifecycle, reporting, analytics

## 9. Boundary Confirmation

This addendum does not modify EDGE.

This addendum does not enable production delivery.

This addendum does not enable EDGE runtime.

This addendum does not approve pilot or production use.

This addendum does not permit writeback.

This addendum does not permit direct UFMS DB access.

## 10. Result

LINK_C3_06B_MULTI_EDGE_STABLE_TELEMETRY_ADDENDUM_PASS

LINK-C3 may continue to C3 Aggregate Gate.

Production delivery remains blocked.
Pilot remains not approved.
Runtime enablement remains not approved.
