# VANTARIS IBMS Modular Boundary A0

**Task:** IBMS-SPLIT-A0  
**Date:** 2026-06-16  
**Status:** Initialized

---

## 1. Purpose

本文档初始化 VANTARIS IBMS 在**当前双包物理结构**下的逻辑模块化边界，为后续按 Console / Core / Data / Link / Edge / NexusAI / Storage / Contracts 进行边界内开发提供基线。

---

## 2. Current Physical Structure

当前系统采用 **前端包 + 后端包** 双包结构，不做真实多仓库或多服务拆分。

| Physical Package | Path | Role |
|---|---|---|
| **Console (Frontend)** | `AN_VANTARIS_IBMS-main/` | Web UI 前端包 |
| **Backend (Monolith)** | `AN_VANTARIS_IBMS-backend/` | 后端主程序，暂时承载 Core / Data / Link-like API / Storage / NexusAI Interface / Edge Interface |

### 2.1 Console — `AN_VANTARIS_IBMS-main`

- 物理定位：前端 Console 包。
- 当前状态（2026-06-16 盘点）：目录内仅含 `README.md`，完整前端源码尚未落地到工作区；完整前端包亦存在于 `AN_VANTARIS_IBMS-main.zip`（同样为占位状态）。
- 逻辑职责：Web UI、Dashboard、资产管理、告警、事件/工单、报表、管理后台、集成状态与健康视图。
- **访问约束：Console 只能访问 Backend/Core API（HTTPS + JWT），不得直连 DB / Link / Edge / NexusAI / Storage。**

### 2.2 Backend — `AN_VANTARIS_IBMS-backend`

- 物理定位：后端主程序（Python / Flask 单体）。
- 当前状态（2026-06-16 盘点）：工作区中后端以 **`AN_VANTARIS_IBMS-backend.zip`** 归档形式存在，尚未解压到 `AN_VANTARIS_IBMS-backend/` 目录；zip 内包含完整 `src/` 源码树。
- 逻辑职责（暂时合包承载）：
  - **Core** — 业务 API、认证/RBAC、系统管理
  - **Data** — ORM / 数据库连接 / 数据访问层
  - **Link-like Module** — 外部集成入口、IoT 设备驱动、SSE 推送
  - **Edge Interface** — 设备模拟器、MQTT/HTTP 接入边界
  - **NexusAI Interface** — 数据建模 / ML 预测（HVAC 等）
  - **Storage** — CSV / 模型文件 / 本地数据存储（`data/`）

---

## 3. What We Do NOT Do at This Stage

| Action | Status |
|---|---|
| 真实多仓库拆分 | ❌ 不做 |
| 真实多服务拆分 | ❌ 不做 |
| 移动现有源码 | ❌ 不做 |
| 拆分数据库 | ❌ 不做 |
| 修改认证 / 权限逻辑 | ❌ 不做 |
| 修改 `.env` / 环境配置 | ❌ 不做 |
| 修改 migration / schema / seed | ❌ 不做 |
| 安装依赖 | ❌ 不做 |
| 运行 migration | ❌ 不做 |
| 重构业务模块 | ❌ 不做 |
| 强行拆成 6 个真实运行服务 | ❌ 不做 |

**当前阶段只做：**

- 边界文档（本文档及 A1–A3 系列）
- 目录盘点（IBMS-INVENTORY-A1）
- 逻辑模块归属（IBMS-BOUNDARY-A2）
- 禁止访问矩阵（IBMS-BOUNDARY-A2）
- 部署模式定义（IBMS-DEPLOY-A3）

---

## 4. Logical Module Map (Current → Future)

```
┌─────────────────────────────────────────────────────────────┐
│  AN_VANTARIS_IBMS-main  (Console)                           │
│  Web UI ──HTTPS/JWT──▶ Backend/Core API only               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  AN_VANTARIS_IBMS-backend  (Monolith, logical modules)      │
│  ┌──────────┐ ┌──────┐ ┌──────────┐ ┌─────────────────────┐ │
│  │   Core   │ │ Data │ │Link-like │ │ Edge Interface      │ │
│  │ Business │ │ ORM  │ │ Ingress  │ │ Simulators/Import   │ │
│  │ Auth/RBAC│ │ DAO  │ │ Drivers  │ │ Device Registration │ │
│  └────┬─────┘ └──┬───┘ └────┬─────┘ └──────────┬──────────┘ │
│       │          │          │                   │            │
│  ┌────┴─────┐ ┌──┴───┐ ┌───┴────────┐ ┌───────┴──────────┐  │
│  │ NexusAI  │ │Storage│ │ Blockchain │ │  (Future split)  │  │
│  │Interface │ │Local │ │  (DID/VC)  │ │                  │  │
│  └──────────┘ └──────┘ └────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  contracts/  (Future cross-module protocol center)          │
│  JSON Schema · OpenAPI · Error codes · Status machines      │
│  Documentation-only — NOT part of runtime                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Development Boundary Rules

1. **Console 开发边界**
   - 所有数据请求经 Backend/Core REST API。
   - 禁止在前端持有 DB 连接串、MinIO 长期密钥、Link/Edge 内部端点。

2. **Backend 内部开发边界**
   - 新功能按逻辑模块归属开发，即使物理上仍在同一 `src/` 树内。
   - Core 业务逻辑不得绕过 Data 层直写 DB（除 Data 模块自身运维脚本）。
   - Link-like / Edge 不得直接创建工单或执行业务规则，须经 Core 编排。
   - NexusAI 结果须经 Core 持久化，不得绕过 RBAC。

3. **Contracts 边界**
   - `contracts/` 目录为未来跨模块协议中心。
   - 当前阶段仅文档占位，不参与运行时。

---

## 6. Allowed Modification Scope (A0–A3 Phase)

| Path | Allowed |
|---|---|
| `docs/architecture/**` | ✅ 新增 / 修改 |
| `contracts/**` | ✅ 新增占位文档 |
| `AN_VANTARIS_IBMS-main/src/**` | ❌ 禁止 |
| `AN_VANTARIS_IBMS-backend/src/**` | ❌ 禁止 |
| 所有业务代码 / schema / migration / seed / .env | ❌ 禁止 |

---

## 7. Related Documents

| Document | Task |
|---|---|
| [IBMS_CODE_INVENTORY_A1.md](./IBMS_CODE_INVENTORY_A1.md) | IBMS-INVENTORY-A1 |
| [IBMS_LOGICAL_MODULE_BOUNDARY_A2.md](./IBMS_LOGICAL_MODULE_BOUNDARY_A2.md) | IBMS-BOUNDARY-A2 |
| [IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md](./IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md) | IBMS-BOUNDARY-A2 |
| [IBMS_DEPLOYMENT_MODES_A3.md](./IBMS_DEPLOYMENT_MODES_A3.md) | IBMS-DEPLOY-A3 |
| [IBMS_A0_A3_COMPLETION_REPORT.md](./IBMS_A0_A3_COMPLETION_REPORT.md) | Completion Report |

---

## 8. Inspection Notes (2026-06-16)

- 工作区根目录：`~/Desktop/AN_VANTARIS_IBMS`
- 前端包 `AN_VANTARIS_IBMS-main/` 当前为占位（仅 README）。
- 后端包尚未解压；完整源码在 `AN_VANTARIS_IBMS-backend.zip` 内，基于 **Python / Flask**，未发现 Prisma / Node.js 结构。
- 后续解压后端包后，应重新执行 A1 轻量盘点以更新路径映射表。
