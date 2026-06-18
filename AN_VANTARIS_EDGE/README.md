# AN_VANTARIS_EDGE

AN_VANTARIS_EDGE is the future VANTARIS ONE Edge Runtime package.

Current status:

- SKELETON_ONLY
- runtimeReady: false
- gaReady: false
- sourceMigration: NOT_STARTED

This package is not production-ready.
No legacy driver source is copied in EDGE-A0.
Legacy driver source remains in `AN_VANTARIS_IBMS-backend/src/Iot/drivers`.
Future extraction must use wrapper/adapter pattern.
Driver output must align with `contracts/schemas/edge-link/edge-normalized-object.schema.json`.
EDGE must not direct-write DB.
EDGE must not call backend DAO/model.
EDGE must not push directly to UI/SSE.
EDGE must not call UFMS runtime directly.
EDGE delivery path will later align to Link envelope contract.
LINK runtime is not created in this task.

Future layers:

- runtime
- connector manager
- protocol plugin runtime
- tag mapping
- data normalization
- local durable buffer
- health
- diagnostics
- security
- dry-run
