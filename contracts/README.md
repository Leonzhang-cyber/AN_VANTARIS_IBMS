# VANTARIS IBMS Contracts

Contracts 是 IBMS 前后端、Core、Data、Link-like、Edge Interface、NexusAI Interface、Storage 之间的协议中心。

---

## Purpose

本目录统一管理跨模块接口定义，确保 Console、Core 及未来拆分模块在演进过程中保持协议一致、版本可追溯、安全边界可审计。

所有跨模块 API、JSON Schema、OpenAPI、错误码、状态机、示例 payload **都应进入 `contracts/`**。

---

## Current Stage

| Property | Value |
|---|---|
| Runtime | **documentation-only** |
| Dependencies | **none** |
| Service process | **none** |
| Database connection | **none** |

Contracts 不参与运行时执行，不被 backend 或 frontend 直接 import。

---

## Architecture Context

- 当前 backend 仍是 **Python/Flask 单体**（`AN_VANTARIS_IBMS-backend`）。
- 开发必须按逻辑模块边界执行：Console / Core / Data / Link-like / Edge Interface / NexusAI Interface / Storage。
- **Console** 未来只能通过 **Core API** 访问业务数据。
- **Link-like / Edge Interface / NexusAI / Storage** 后续必须通过 contracts 对齐接口，不得绕过 Core 直连。

---

## Directory Structure

```
contracts/
├── README.md                 # 本文件 — 总览
├── VERSIONING.md             # 版本策略
├── API_GROUPS.md             # API 分组（基于 B2 盘点）
├── ERROR_CODES.md            # 统一错误码
├── STATUS_CODES.md           # 状态机与状态码
├── SECURITY_BOUNDARY.md      # 安全边界契约
├── PROTECTED_API_BOUNDARY_A1.md  # A1 已保护 API 边界清单
├── PERMISSION_BOUNDARY_A0.md     # A0 权限命名草案 (CORE-A0)
├── PERMISSION_MATRIX_A2.md       # A2 API 权限矩阵草案 (CONTRACTS-A2)
├── schemas/                  # JSON Schema 定义
│   └── README.md
├── openapi/                  # OpenAPI 规范
│   └── README.md
├── examples/                 # 示例 payload
│   └── README.md
├── errors/                   # 错误码 JSON 占位（future）
└── status/                   # 状态机 JSON 占位（future）
```

---

## Related Documents

| Document | Location |
|---|---|
| Contracts A0 completion | `docs/architecture/IBMS_CONTRACTS_A0.md` |
| Protected API boundary A1 | `contracts/PROTECTED_API_BOUNDARY_A1.md` |
| Auth permission boundary CORE-A0 | `docs/architecture/IBMS_CORE_A0_AUTH_PERMISSION_BOUNDARY.md` |
| Permission naming A0 | `contracts/PERMISSION_BOUNDARY_A0.md` |
| Permission matrix A2 | `contracts/PERMISSION_MATRIX_A2.md` |
| Backend inventory B2 | `docs/architecture/IBMS_BACKEND_INVENTORY_B2.md` |
| Logical module boundary | `docs/architecture/IBMS_LOGICAL_MODULE_BOUNDARY_A2.md` |
| Forbidden access matrix | `docs/architecture/IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md` |

### Source inventory & split (SPLIT-A0)

| Document | Location |
|---|---|
| Source package snapshot A0 | `docs/architecture/IBMS_SOURCE_A0_PACKAGE_SNAPSHOT.md` |
| Sensitive file scan A0 | `docs/security/IBMS_SOURCE_A0_SENSITIVE_FILE_SCAN.md` |
| Backend inventory A1 | `docs/architecture/IBMS_SOURCE_A1_BACKEND_INVENTORY.md` |
| Backend risk review A1 | `docs/security/IBMS_SOURCE_A1_BACKEND_RISK_REVIEW.md` |
| Frontend inventory A2 | `docs/architecture/IBMS_SOURCE_A2_FRONTEND_INVENTORY.md` |
| Frontend risk review A2 | `docs/security/IBMS_SOURCE_A2_FRONTEND_RISK_REVIEW.md` |
| Modular split rules | `docs/architecture/IBMS_SPLIT_A0_MODULAR_SPLIT_RULES.md` |
| Target package map | `docs/architecture/IBMS_SPLIT_A0_TARGET_PACKAGE_MAP.md` |
| Forbidden cross access (split) | `docs/architecture/IBMS_SPLIT_A0_FORBIDDEN_CROSS_ACCESS.md` |
| Split execution plan (phase B) | `docs/architecture/IBMS_SPLIT_A0_EXECUTION_PLAN.md` |

---

## Next Steps

1. **IBMS-SPLIT-B1 / B2** — Declare canonical backend and frontend (see `IBMS_SPLIT_A0_EXECUTION_PLAN.md`)
2. **IBMS-CONTRACTS-B1** — Frontend-facing OpenAPI subset for system / menu / IoT / DID / modeling
3. **IBMS-SPLIT-B3** — Target skeleton packages without business logic moves
4. **IBMS-CONTRACTS-A3** — Schema examples and JSON Schema refs (ongoing)
