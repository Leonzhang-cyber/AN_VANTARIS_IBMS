# UMMS GA R2 Role Based Customer Engineer Admin Operator Views

PASS marker: `UMMS_GA_R2_PRODUCTION_GRADE_MAINTENANCE_WORKSPACE_PASS`

UMMS R2 provides role-based read-only views for production-grade customer demo readiness.

Customer view:
- Maintenance overview
- Customer acceptance
- Evidence summary
- Report snapshot
- No internal diagnostics detail

Engineer view:
- Work orders
- Task board
- Dispatch
- Asset context
- Event context
- Evidence requirements
- Package/server planning context

Admin view:
- Role matrix preview
- Menu visibility preview
- Package readiness preview
- Guardrails
- No real permission mutation

Operator view:
- Live maintenance status
- Active events
- Work order overview
- Shift handover
- Guardrails

R2 does not do auth/login/JWT/RBAC mutation. It does not write permission state or activate production behavior.
