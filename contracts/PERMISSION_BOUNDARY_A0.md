# VANTARIS IBMS Permission Boundary A0

## 1. Scope

Draft permission **naming boundary** for VANTARIS IBMS. Defines vocabulary for future RBAC enforcement, admin UI, and contract tests. **Not enforced in runtime** as of A0.

## 2. Permission Naming Rule

Format:

```
<domain>:<action>
```

Rules:

- Domain is lowercase alphanumeric (may use hyphen in future extensions).
- Action is lowercase verb or verb phrase.
- Wildcards (e.g. `iot:*`) reserved for CORE-A1 helper — not in seed yet.

Examples:

- `modeling:read`
- `modeling:predict`
- `modeling:train`
- `iot:command`
- `did:issue`

## 3. Draft Permission Registry

| Permission | Domain | Typical Use |
|---|---|---|
| `modeling:read` | modeling | CSV list, model_info |
| `modeling:predict` | modeling | predict, predict_future |
| `modeling:train` | modeling | train |
| `iot:read` | iot | Device/dictionary GET (future policy) |
| `iot:write` | iot | Register, update, delete device |
| `iot:ingest` | iot | HTTP telemetry ingest |
| `iot:command` | iot | Device command dispatch |
| `device:read` | device | Device detail queries |
| `device:manage` | device | Mappings, reconnect, admin |
| `device:control` | device | Control-plane commands |
| `did:read` | did | Entity/subordinate GET |
| `did:issue` | did | Create entity, issue/reissue VC, generate VP |
| `did:revoke` | did | Revoke VC |
| `did:manage` | did | System init, hierarchy mutations |
| `system:read` | system | Read menus, permissions, configs |
| `system:write` | system | CRUD standard fields/methods, menus |
| `system:admin` | system | Permission table admin |
| `audit:read` | audit | View audit/trace records (future) |

## 4. Pending

- Runtime enforcement (CORE-A1)
- DB seed and permission table alignment
- Admin UI mapping to permission codes
- Contract tests asserting 403 on missing permission
- Mapping JWT `perms` array to registry codes
- **Permission matrix A2:** see [`PERMISSION_MATRIX_A2.md`](PERMISSION_MATRIX_A2.md) for API route → target permission mapping and role drafts
