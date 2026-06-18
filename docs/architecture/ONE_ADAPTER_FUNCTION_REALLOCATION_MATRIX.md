# ONE Adapter Function Reallocation Matrix

| Removed ONE Adapter function | Correct owner | Reason | Required future artifact | Current action | Runtime impact |
| --- | --- | --- | --- | --- | --- |
| consumer boundary | governance/module-manifest rules + UConsole readiness/status model | boundary is a rule, not middleware | boundary governance update and module status model update | reallocated | none in this task |
| contract routing | Contracts for schema/version/namespace + LINK for delivery route/ACK/retry/DLQ/audit | contract meaning and delivery routing are separate | contract candidate policy + LINK routing policy | reallocated | none in this task |
| object mapping | EDGE for source object/tag/point mapping + Contracts for canonical object definition | mapping happens at ingestion; object definition belongs to shared contract | ingestion mapping policy and canonical contract candidate policy | reallocated | none in this task |
| identity preservation | EDGE for source identity + LINK for delivery identity + UCDE for evidence identity + DB for persistent references | identity is preserved across layers, not by a single adapter | cross-layer identity continuity checklist | reallocated | none in this task |
| traceability preservation | LINK for message delivery trace + UCDE for business evidence trace + DB for audit/evidence reference persistence | delivery trace and business evidence trace are different responsibilities | traceability split model and audit persistence checklist | reallocated | none in this task |
| foundation reference map | shared foundation docs/module manifest metadata | reference map is architecture metadata, not runtime | architecture metadata map updates | reallocated | none in this task |
| module consumption policy | governance/module manifest/UConsole | module consumption rules are governance and status metadata | governance consumption policy and status checklist | reallocated | none in this task |
| external system ingress | EDGE Fleet | all external integration enters through EDGE instances | edge-fleet consumption model draft | reallocated | none in this task |

## Conclusion

No standalone ONE Adapter module remains.
