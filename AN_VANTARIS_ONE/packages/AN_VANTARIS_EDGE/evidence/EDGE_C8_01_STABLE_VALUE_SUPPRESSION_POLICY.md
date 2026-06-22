# EDGE-C8-01 — Stable Value Suppression and Change Detection Policy

Status: POLICY_DEFINED
Scope: AN_VANTARIS_EDGE only
Date: 2026-06-20

## 1. Purpose

This evidence records the EDGE-side policy for reducing repeated unchanged data
before it reaches AN_VANTARIS_LINK.

The goal is to prevent stable device values from flooding LINK queues while
preserving alarm, event, health, evidence, and audit integrity.

This task is a controlled EDGE gap patch identified during LINK-C3 multi-EDGE
concurrency planning.

## 2. Background

LINK-C3 introduced multi-EDGE queue validation and identified that multiple EDGE
gateways can concurrently send data to LINK.

However, queue and backpressure controls alone are not sufficient for
International GA. EDGE must also reduce unnecessary repeated stable telemetry
at the source.

Without EDGE-side suppression, the following risks remain:

- same device / same point / same value repeatedly enters LINK
- telemetry floods can delay alarm and health records
- network recovery can replay large stable-value batches
- LINK partition queues can grow without useful semantic change
- upper-layer UFMS APIs may receive excessive no-change data

## 3. EDGE Responsibility

EDGE is the first suppression layer.

EDGE should detect whether a normalized read-only record represents a meaningful
change before sending it to LINK.

EDGE must not suppress critical lifecycle records.

## 4. Record Type Policy

### 4.1 Telemetry

Telemetry may be suppressed when all of the following are true:

- same tenant / site / gateway / device / point
- same value within deadband
- same quality
- same normalized status
- no heartbeat interval has expired
- no full snapshot is requested
- no reconnect first-sample rule applies

Telemetry should be emitted when:

- value changes beyond deadband
- quality changes
- status changes
- heartbeat / keepalive interval expires
- first sample after EDGE startup
- first sample after device reconnect
- full snapshot is requested
- suppression summary interval expires

### 4.2 Analog Values

Analog values must support deadband policy.

Supported deadband modes:

- absolute deadband
- percentage deadband
- disabled deadband

A new analog value should be emitted when:

- absolute difference is greater than or equal to absolute deadband
- percentage difference is greater than or equal to percentage deadband
- quality changes
- heartbeat interval expires

### 4.3 Digital / Status Values

Digital and status values should use change-only emission.

A record should be emitted when:

- false to true
- true to false
- enum value changes
- quality changes
- heartbeat interval expires
- first sample after startup or reconnect

### 4.4 Alarm and Event Records

Alarm and event records must not be suppressed like telemetry.

Alarm/event policy:

- new active alarm: emit
- cleared alarm: emit
- severity change: emit
- acknowledgement state change: emit
- repeated same active alarm: aggregate repeat count
- long-active alarm: emit summary heartbeat
- event lifecycle transition: emit

Repeated active alarms may be aggregated using repeatCount, firstSeenAt,
lastSeenAt, and aggregationWindowMs.

### 4.5 Health / Evidence / Audit / Config Version

These records must remain conservative.

Suppression must not hide:

- EDGE health transition
- adapter health transition
- connector decision state change
- evidence collection result
- audit record
- config version change
- endpoint approval state change
- credential reference state change

## 5. Required Handoff Metadata

EDGE should prepare the following metadata for future EDGE-LINK integration:

- dedupeKey
- sampleMode
- changeReason
- valueChanged
- qualityChanged
- statusChanged
- suppressedCount
- firstSeenAt
- lastSeenAt
- lastEmittedAt
- deadbandApplied
- deadbandValue
- deadbandMode
- aggregationWindowMs
- heartbeatDue
- fullSnapshot
- reconnectFirstSample

## 6. Sample Modes

Supported sample modes:

- RAW_EVERY_SAMPLE
- CHANGE_ONLY
- DEADBAND
- HEARTBEAT
- AGGREGATED_REPEAT
- FULL_SNAPSHOT

Default production recommendation:

- telemetry: DEADBAND or CHANGE_ONLY
- analog: DEADBAND
- digital/status: CHANGE_ONLY
- alarm/event: AGGREGATED_REPEAT for repeated active state
- health: HEARTBEAT plus transition
- evidence/audit/config: RAW_EVERY_SAMPLE or transition-based by type

## 7. Change Reasons

Supported change reasons:

- FIRST_SAMPLE
- VALUE_CHANGED
- QUALITY_CHANGED
- STATUS_CHANGED
- DEADBAND_EXCEEDED
- HEARTBEAT_DUE
- RECONNECT_FIRST_SAMPLE
- FULL_SNAPSHOT_REQUESTED
- ALARM_NEW_ACTIVE
- ALARM_CLEARED
- ALARM_SEVERITY_CHANGED
- ALARM_ACK_CHANGED
- ALARM_REPEAT_AGGREGATED
- EVIDENCE_STATE_CHANGED
- CONFIG_VERSION_CHANGED
- SUPPRESSED_NO_CHANGE

## 8. LINK Impact

This policy reduces LINK impact by:

- lowering repeated stable telemetry ingress
- preserving alarm and health priority
- reducing partition queue pressure
- improving backpressure behavior
- improving delivery efficiency
- reducing duplicate UFMS API load

LINK must still retain duplicate awareness and idempotency because EDGE
suppression is not a substitute for LINK queue protection.

## 9. Boundary

This task does not enable EDGE runtime.

This task does not approve pilot or production usage.

This task does not allow writeback.

This task does not allow direct UFMS DB access.

This task does not bypass LINK.

This task does not add credentials or secrets.

## 10. Result

EDGE_C8_01_STABLE_VALUE_SUPPRESSION_POLICY_DEFINED

EDGE stable value suppression is now defined as a controlled EDGE follow-up
needed before International GA.

Runtime remains not enabled.
Pilot remains not approved.
Production remains not approved.
Writeback remains prohibited.
