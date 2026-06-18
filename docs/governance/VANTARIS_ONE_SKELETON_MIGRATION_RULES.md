# VANTARIS ONE Skeleton Migration Rules

- Skeleton is not runtime
- No source copy without source audit
- No runtime migration without module boundary
- No DB migration without DB contract
- No API rename without Contracts alignment
- No Edge extraction before EDGE-SOURCE-AUDIT
- No Link implementation before Link contracts
- No IBMS deletion
- No UFMS runtime mixing

## Commit separation rule

The following commits must be separate:

- docs skeleton commit
- source migration commit
- runtime refactor commit
- DB migration commit
- API namespace commit
