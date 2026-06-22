# AN_VANTARIS_LINK Offline Bundle

Status: STRUCTURE_ONLY

This offline bundle directory defines the LINK deployment package structure.

It does not enable production delivery.

## Scope

Allowed:

- local package verification
- local healthcheck
- package manifest
- rollback and uninstall planning
- diagnostics reference
- contracts manifest reference

Forbidden:

- production delivery enablement
- endpoint approval
- real UFMS API delivery
- direct UFMS DB access
- writeback
- credential storage
- auth/login modification
- UFMS backend/frontend modification
- VANTARIS ONE / UMMS / UCDE runtime implementation

## Runtime Status

- linkProductionDeliveryAllowed=false
- endpointApproved=false
- directUfmsDbAccessAllowed=false
- writebackAllowed=false
- consumerImplementationIncluded=false
