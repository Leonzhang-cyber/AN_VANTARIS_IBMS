# ONE-AIRPORT-A2-05 Read-Only UConsole Integration Health Projection Report

## Status

`READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_COMPLETE`

## Boundary

Generic read-only UConsole projection under `AN_VANTARIS_ONE/uconsole_projection/`.
Aggregates A2-02 review, A2-03 health, and A2-04 evidence contract artifacts. No frontend, API, DB, or runtime activation.

## Result

- Source-system rows: 5
- Dashboard cards: 5 (+ 3 summary cards)
- Total evidence devices: 470
- Pending decisions: 5
- Runtime observed: 0

Readiness: `UCONSOLE_INTEGRATION_HEALTH_READ_ONLY_PROJECTION_COMPLETE_RUNTIME_PENDING`

## Validation

```bash
PYTHONPATH=AN_VANTARIS_ONE python3 -m unittest discover -s AN_VANTARIS_ONE/tests/uconsole_projection -p 'test_*.py'
python3 scripts/validation/validate-one-uconsole-integration-health-projection.py
```

Expected marker: `ONE_AIRPORT_A2_05_READ_ONLY_UCONSOLE_INTEGRATION_HEALTH_PROJECTION_PASS`
