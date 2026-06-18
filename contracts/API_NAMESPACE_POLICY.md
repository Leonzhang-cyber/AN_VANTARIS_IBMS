# VANTARIS ONE API Namespace Policy

## Future Namespace

- `/api/v1/platform/*`
- `/api/v1/ibms/*`
- `/api/v1/assets/*`
- `/api/v1/integration/*`
- `/api/v1/events/*`
- `/api/v1/mms/*`
- `/api/v1/esg/*`
- `/api/v1/cde/*`
- `/api/v1/ai/*`
- `/api/v1/edge/*`
- `/api/v1/link/*`
- `/api/v1/console/*`
- `/api/v1/trust/*`
- `/api/v1/audit/*`

## Transition Rules

- current legacy APIs remain unchanged
- no runtime API rename in CONTRACTS-A0
- new namespace requires compatibility wrapper
- old API removal requires GA owner approval
- UFMS integration only through adapter namespace/contract
