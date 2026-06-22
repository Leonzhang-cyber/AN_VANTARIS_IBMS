# Deployment Profile Security Baseline v1

## standalone UFMS profile

- security boundary: UFMS module boundary on shared VANTARIS ONE contract model
- required machine identity: required
- network assumptions: segmented OT/IT boundary with controlled ingress
- logging/audit requirement: auditability contract categories required
- secrets/config handling: external secret injection, no repo secrets
- allowed conduits: Device->EDGE, EDGE->LINK, LINK->Code/API, Code/API->DB, Console->Code/API
- forbidden conduits: EDGE->DB direct, LINK->DB direct, Console->DB direct
- minimum validation evidence: contract validation, boundary scans, profile review

## VANTARIS ONE profile

- security boundary: multi-module platform boundary using shared Contracts authority
- required machine identity: required
- network assumptions: segmented module/service network with controlled cross-zone conduits
- logging/audit requirement: cross-module audit correlation required
- secrets/config handling: profile-scoped secret management and config policy
- allowed conduits: Device->EDGE, EDGE->LINK, LINK->Code/API, Code/API->DB, Code/API->NexusAI, Console->Code/API
- forbidden conduits: EDGE/LINK direct DB write, module-private bypass conduits
- minimum validation evidence: contracts + boundary scans + profile security review

## hardware appliance profile

- security boundary: appliance-hosted edge runtime boundary
- required machine identity: hardware-bound or equivalent protected identity required
- network assumptions: controlled appliance network ingress/egress
- logging/audit requirement: local and exportable audit/event logs
- secrets/config handling: protected local key/config storage
- allowed conduits: Device->EDGE, EDGE->LINK
- forbidden conduits: direct external admin bypass to runtime data plane
- minimum validation evidence: hardening checklist + smoke evidence

## software-only industrial PC profile

- security boundary: host OS + runtime service boundary
- required machine identity: required
- network assumptions: host firewall and segmented routing policy
- logging/audit requirement: service logs + audit export support
- secrets/config handling: OS-protected config and key files
- allowed conduits: standard profile conduits per deployment mode
- forbidden conduits: unrestricted inbound admin channel to data plane
- minimum validation evidence: host hardening and runtime validation checklist

## offline/air-gapped profile

- security boundary: isolated deployment with controlled update channel
- required machine identity: required
- network assumptions: no internet dependency for runtime operation
- logging/audit requirement: local audit retention and controlled export process
- secrets/config handling: offline secret/bootstrap process and custody record
- allowed conduits: local approved conduits only
- forbidden conduits: unapproved external network egress
- minimum validation evidence: offline package validation + buffer/restart smoke evidence

## multi-EDGE single-LINK profile

- security boundary: multiple EDGE zones converging on one LINK integration boundary
- required machine identity: required per EDGE instance and LINK endpoint
- network assumptions: segmented conduits with per-edge identity enforcement
- logging/audit requirement: per-edge traceability and centralized correlation
- secrets/config handling: per-edge scoped config/identity material
- allowed conduits: Device->EDGE(xN), EDGE(xN)->LINK, LINK->Code/API
- forbidden conduits: EDGE-to-EDGE lateral trust bypass, EDGE/LINK direct DB write
- minimum validation evidence: identity validation, routing validation, boundary scan evidence
