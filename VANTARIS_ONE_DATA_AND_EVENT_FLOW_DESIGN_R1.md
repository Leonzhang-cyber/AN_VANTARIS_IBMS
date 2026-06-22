# VANTARIS ONE Data And Event Flow Design R1

## Primary Flow

Device -> EDGE -> LINK -> CODE -> Modules -> UConsole.

EDGE collects or buffers approved source-system data. LINK handles gateway/API handoff, queue, ack, DLQ, and delivery evidence. CODE validates contracts and enforces execution boundaries. Domain modules consume approved envelopes and publish projections. UConsole renders authorized state and workflow surfaces.

## Event/Fault Flow

Device/source event -> EDGE read-only collector -> local buffer -> LINK canonical handoff -> CODE validation -> UFMS event/fault correlation -> Automated Rules & Policy -> operator review in UConsole -> optional UMMS work intent -> UCDE evidence.

## Evidence/UCDE Flow

Module action or package gate -> evidence envelope -> CODE validation -> UCDE read-only evidence chain -> Reports & Analytics -> UConsole evidence page -> customer/export package.

## Reports Flow

Modules and foundation packages publish approved read models and evidence summaries. Reports & Analytics reads from governed DB/reporting views and produces dashboards, exports, and trend reports. Reports do not bypass policy or route enforcement.

## NEXUS AI Advisory Flow

Approved context -> NEXUS AI model selection/risk scoring/triage -> recommendation record -> CODE policy validation -> UConsole advisory presentation -> human approval/workflow action. NEXUS AI does not execute control.

## Data Separation

- Config: package state, entitlement, policy, route declarations, topology.
- Event: alarms, incidents, heartbeats, work triggers, acknowledgements.
- Raw: source-system payloads retained under approved collector and retention policy.
- Insight: AI recommendations, analytics aggregates, risk scores, trend summaries.
- Evidence: immutable validation, approval, acceptance, and audit artifacts.

## Contracts As Schema Source

Contracts are the schema source for EDGE/LINK envelopes, CODE API delivery, module boundaries, OpenAPI surfaces, and evidence exchange. Modules should consume contract-approved objects rather than ad hoc payloads.

## Logical Architecture

```text
+-----------+    +------+    +------+    +------+    +-------------------+
| Devices / | -> | EDGE | -> | LINK | -> | CODE | -> | Domain Modules    |
| Sources   |    |      |    |      |    |      |    | UFMS UMMS UESG... |
+-----------+    +------+    +------+    +------+    +---------+---------+
                                                            |
                                                            v
                                                    +---------------+
                                                    | UConsole      |
                                                    +---------------+
```

## Data Flow

```text
[source payload]
  -> EDGE collector/read-only buffer
  -> LINK delivery envelope + ack/DLQ
  -> CODE contract validation + policy route
  -> module projection/read model
  -> UConsole or Reports read surface
  -> UCDE evidence where required
```

## Deployment Flow

```text
Package manifest -> precheck -> dry-run plan -> verify -> approval gate
     -> backup confirmation -> activation window -> future runtime pilot
```

## Customer Delivery Flow

```text
Export package -> checksum -> customer handoff -> engineer console
     -> precheck -> install dry-run -> verify -> rollback dry-run
     -> acceptance evidence -> activation remains blocked until approved
```

## Important Rules

- EDGE/LINK do not write direct to UFMS DB.
- UConsole does not bypass CODE layer.
- NEXUS AI does not execute control.

PASS marker: `ONE_DESIGN_R1_FULL_PRODUCT_DESIGN_BLUEPRINT_PASS`
