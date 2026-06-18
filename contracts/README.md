# VANTARIS ONE Contracts

`contracts/` is the current Contracts source directory for VANTARIS ONE transition.
`AN_VANTARIS_Contracts` target package will be created later.

Contracts are governance/source-of-truth assets, not runtime modules.
Contracts do not connect to DB.
Contracts do not call Edge/Link/Code/Console/NexusAI.
Runtime modules must align to Contracts.
IBMS is retained as ibms-core business module.
UFMS is only referenced through adapter/boundary contracts, not runtime import.

## A0 Baseline Files

- `contract-manifest.json`
- `VERSION`
- `GOVERNANCE.md`
- `VERSIONING_POLICY.md`
- `OBJECT_IDENTITY_STANDARD.md`
- `API_NAMESPACE_POLICY.md`
- `ERROR_CODES.md`
- `STATUS_CODES.md`
- `PORTS_AND_NETWORK_BOUNDARY.md`
