# EDGE Source Audit Decision Log

1. Do not create AN_VANTARIS_EDGE runtime in source audit task.
2. Do not copy drivers directly into skeleton.
3. Future EDGE-A0 should create independent EDGE package only after audit.
4. Driver extraction must use adapter/wrapper pattern.
5. Driver output must align to `contracts/schemas/edge-link/edge-normalized-object.schema.json`.
6. Backend DAO/model dependencies must be removed or abstracted before production EDGE.
7. UI/SSE/API coupling must be removed from EDGE runtime.
8. Protocol plugins must not directly write DB.
9. Protocol plugins must not call UFMS runtime directly.
10. Edge delivery path must later use Link envelope contract.
