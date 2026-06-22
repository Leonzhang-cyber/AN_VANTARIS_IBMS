# Canonical to DB Mapping Baseline v1

## Purpose

Defines initial mapping concept between VANTARIS ONE canonical contracts and UFMS DB implementation mapping layers.

## Mapping layers

- **Config layer**: gateway/connector/site/config-version metadata and effective configuration state.
- **Event layer**: normalized events/alarms and lifecycle transitions for operational processing.
- **Raw layer**: raw ingestion payload snapshots and transport metadata.
- **Insight layer**: triage outcomes, recommendation traces, and analytical projections.

## Audit and config version fields

- Every persisted integration-critical record should retain contract version context when relevant.
- Audit records should capture `correlationId`, source module, and major processing transitions.
- Config version references should link operational behavior to `configVersionId`.

## Tenant/site partitioning

- Partitioning strategy should include tenant/site boundaries for scalability and isolation.
- Partition metadata must preserve canonical IDs.

## Retention placeholder

- Raw/event/insight retention policies are pending final governance in later task.
- Retention policy must not violate audit/compliance requirements.
