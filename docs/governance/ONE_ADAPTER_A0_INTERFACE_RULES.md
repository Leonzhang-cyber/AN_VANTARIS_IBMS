# ONE Adapter A0 Interface Rules

1. ONE Adapter must consume, not redefine, Shared Contracts.
2. ONE Adapter must not implement protocol drivers.
3. ONE Adapter must not own Link ACK/DLQ/retry.
4. ONE Adapter must preserve messageId / traceId / correlationId.
5. ONE Adapter must preserve tenantId / projectId / siteId.
6. ONE Adapter must reject unsupported schemaVersion.
7. ONE Adapter must not import UFMS backend source.
8. ONE Adapter must not copy UFMS DB schema/auth/login/seed/migration.
9. ONE Adapter must expose integration health later through Console.
10. Any runtime implementation requires separate ONE-ADAPTER-A1 approval.
