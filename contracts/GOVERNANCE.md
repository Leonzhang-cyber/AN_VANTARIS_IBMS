# VANTARIS ONE Contracts Governance

1. Contract-first principle
   - Cross-module changes start from contract updates and review.

2. No runtime role
   - Contracts are governance/source assets, not runtime modules.

3. No DB connection
   - Contracts define references only and never connect to database runtime.

4. No secret material
   - No credentials, tokens, keys, or private signing material may be stored in contracts.

5. No UFMS runtime import
   - UFMS is only referenced via adapter/boundary contracts, never as runtime/source import.

6. Runtime modules must not invent private cross-module schemas
   - Shared payloads and envelopes must be defined under contracts first.

7. Breaking changes require new version
   - API/event/schema breaking changes require contract version bump and compatibility review.

8. Generated artifacts must trace to source contract
   - Generated outputs must include source contract version and source path references.

9. Public API changes require compatibility review
   - New versions must define wrapper/compatibility strategy before rollout.

10. DB schema changes require AN_VANTARIS_DB migration contract
   - No DB contract change is valid without aligned migration contract planning.

11. Edge/Link changes require envelope/schema review
   - Delivery envelope, ACK, retry, and DLQ schema checks are mandatory.

12. AI/CDE changes require traceability review
   - AI inference and CDE evidence contracts require audit-trace and evidence-chain review.
