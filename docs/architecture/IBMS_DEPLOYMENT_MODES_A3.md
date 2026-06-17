# VANTARIS IBMS Deployment Modes A3

**Task:** IBMS-DEPLOY-A3  
**Date:** 2026-06-16  
**Status:** Defined (documentation only — no installation packages generated)

---

## 1. Purpose

本文档定义 VANTARIS IBMS 从当前**前端包 + 后端包双包结构**演进到多种部署拓扑的模式。当前阶段仅做模式定义，不生成安装包、不拆分服务。

---

## 2. Current Development Mode

**适用场景：** 本地开发、架构边界初始化、模块归属梳理。

| Component | Deployment |
|---|---|
| Frontend | `AN_VANTARIS_IBMS-main` — local dev server (when implemented) |
| Backend | `AN_VANTARIS_IBMS-backend` — Flask dev server |
| Database | Local DB or shared dev DB |
| Service split | **None** — logical boundaries only |
| Redis | Optional (local) |
| MinIO | Optional (local) |
| AI / NexusAI | Optional (local model files in `data/models/`) |

**Characteristics:**

- Single developer machine or small team shared environment.
- All logical modules run within one Python process.
- No container orchestration required.
- Contracts directory is documentation-only.

---

## 3. PoC / Demo Mode

**适用场景：** 客户演示、功能验证、PoC 交付。

### One Server

```
┌─────────────────────────────────────────────┐
│                  Server 1                    │
│  ┌──────────┐  ┌─────────────────────────┐  │
│  │ Console  │  │ Backend (Monolith)       │  │
│  │ (static  │  │  Core + Link + Edge +    │  │
│  │  or dev) │  │  NexusAI + Storage API   │  │
│  └──────────┘  └─────────────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │PostgreSQL│  │Redis     │  │MinIO      │  │
│  │(optional)│  │(optional)│  │(optional) │  │
│  └──────────┘  └──────────┘  └───────────┘  │
│  AI model files (optional, local)            │
└─────────────────────────────────────────────┘
```

| Component | Required | Notes |
|---|---|---|
| Console | Yes | Nginx static or embedded dev server |
| Backend / Core | Yes | Single Flask process |
| DB | Yes | PostgreSQL (or SQLite for minimal demo) |
| Redis | Optional | Session cache, SSE pub/sub |
| MinIO | Optional | Object storage for attachments/reports |
| AI | Optional | Local ML model (`data/models/`) |

**Resource baseline:** 4 vCPU, 8 GB RAM, 100 GB disk.

---

## 4. Two-Server Minimum Production Mode

**适用场景：** 商业化初期部署 — **建议优先支持的模式**。

> 这是当前商业化初期建议优先支持的部署模式。应用层与数据层分离，满足基本安全隔离与独立扩容需求，同时保持运维复杂度可控。

### Server A — App Server

| Component | Role |
|---|---|
| Console | Nginx-served static frontend |
| Backend / Core | Business API, auth/RBAC |
| Link-like API | IoT ingress, SSE, webhook receivers |
| Storage API | File upload/download via signed URL |
| NexusAI Interface | ML inference service (co-located or sidecar) |

### Server B — Data Server

| Component | Role |
|---|---|
| PostgreSQL | Primary business database |
| TimescaleDB | Optional — time-series extension for IoT telemetry |
| Redis | Cache, session, pub/sub |
| MinIO | Object storage (attachments, reports, evidence) |
| Backup jobs | Scheduled pg_dump, MinIO replication |

```
┌──────────────────────────┐       ┌──────────────────────────┐
│      Server A (App)       │       │     Server B (Data)       │
│  Console (Nginx)          │       │  PostgreSQL               │
│  Backend/Core             │◀─────▶│  TimescaleDB (optional)   │
│  Link-like API            │  TLS  │  Redis                    │
│  Storage API              │       │  MinIO                    │
│  NexusAI Interface        │       │  Backup jobs              │
└──────────────────────────┘       └──────────────────────────┘
```

**Network rules:**

- Server B **not** directly accessible from public internet.
- Server A connects to Server B via private network (VPC/VLAN).
- Console clients connect to Server A only (HTTPS :443).

**Resource baseline:**

| Server | vCPU | RAM | Disk |
|---|---|---|---|
| A (App) | 4–8 | 16 GB | 50 GB |
| B (Data) | 4–8 | 32 GB | 500 GB+ (data dependent) |

---

## 5. Three-Server Standard Production Mode

**适用场景：** 中等规模生产，集成流量与业务负载需要独立扩展。

### Server A — Console + Core

| Component | Role |
|---|---|
| Console | Static frontend |
| Core | Business API, auth/RBAC, rule engine, audit |

### Server B — Link / Integration / Queue Worker

| Component | Role |
|---|---|
| Link ingress | IoT/webhook/CMMS/SIEM intake |
| Queue worker | Async message processing, retry, dead-letter |
| Notification adapter | Email, Teams, webhook outbound |
| SSE / WebSocket gateway | Real-time push |

### Server C — Data + Redis + MinIO + Backup

| Component | Role |
|---|---|
| PostgreSQL | Business database |
| TimescaleDB | Time-series (optional) |
| Redis | Cache, queue backend |
| MinIO | Object storage |
| Backup / restore | Automated backup, retention |

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Server A        │   │  Server B        │   │  Server C        │
│  Console + Core  │◀─▶│  Link / Queue    │◀─▶│  Data + Storage  │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │                                              ▲
         └──────────────────────────────────────────────┘
                    (Core → Data direct for sync queries)
```

---

## 6. Enterprise Multi-Server Mode

**适用场景：** 大型企业、多站点、高可用、OT/IT 严格隔离。

| Server ID | Role | Components |
|---|---|---|
| **S01** Edge Server | Edge zone | Edge Interface agents, protocol adapters, local buffering |
| **S02** Link Server | Integration zone | Link ingress, queue, notification adapters, webhook |
| **S03** Core Server | Application zone | Business API, auth/RBAC, rule engine, audit, AI orchestration |
| **S04** NexusAI Server | AI zone | ML inference, model serving, GPU (optional) |
| **S05** Data Server | Data zone | PostgreSQL, TimescaleDB, Redis, backup |
| **S06** Storage / Console Server | Client + object zone | MinIO cluster, Console static, CDN origin |

```
                    ┌─────────┐
                    │   S06   │ Console + MinIO
                    └────┬────┘
                         │ HTTPS
                    ┌────▼────┐
                    │   S03   │ Core
                    └──┬──┬───┘
              ┌────────┘  └────────┐
         ┌────▼────┐          ┌────▼────┐
         │   S02   │          │   S04   │
         │  Link   │          │ NexusAI │
         └────┬────┘          └────┬────┘
              │                    │
         ┌────▼────┐          ┌────▼────┐
         │   S01   │          │   S05   │
         │  Edge   │          │  Data   │
         └─────────┘          └─────────┘
```

**Network segmentation:**

- S01 (Edge) in OT/DMZ zone — outbound only to S02.
- S02 (Link) in DMZ — receives external integrations.
- S03–S06 in internal application/data zones.
- No direct Console → S01/S02/S04/S05/S06 except Console → S03 (via S06 proxy).

---

## 7. HA Mode (High Availability)

**适用场景：** 生产级 SLA ≥ 99.9%，可叠加于两服务器/三服务器/企业模式。

| Component | HA Strategy |
|---|---|
| Core | Multiple replicas + Load Balancer (active/active or active/passive) |
| Link | Multiple replicas + queue HA (Redis Sentinel / dedicated message broker) |
| PostgreSQL | Streaming replication or Patroni cluster |
| Redis | Sentinel or Cluster mode |
| MinIO | Distributed mode (≥ 4 nodes, erasure coding) |
| Console | Static file replication + CDN / dual Nginx |
| Edge | Multi-site edge nodes with local buffer + store-and-forward |
| Backup | Automated backup + regular restore drill (monthly minimum) |

```
                    ┌─────────┐
                    │   LB    │
                    └────┬────┘
              ┌──────────┼──────────┐
         ┌────▼────┐ ┌───▼─────┐ ┌──▼──────┐
         │ Core-1  │ │ Core-2  │ │ Core-3  │
         └────┬────┘ └───┬─────┘ └──┬──────┘
              └──────────┼──────────┘
                    ┌────▼────┐
                    │ PG Primary│──replication──▶ PG Standby(s)
                    └─────────┘
```

**Failover targets:**

| Component | RTO | RPO |
|---|---|---|
| Core | ≤ 30s | 0 (stateless) |
| Link queue | ≤ 60s | ≤ 5 min (queued messages) |
| PostgreSQL | ≤ 60s | ≤ 0 (sync replication) |
| MinIO | ≤ 60s | 0 (distributed) |
| Edge (per site) | Local buffer ≥ 24h | Store-and-forward |

---

## 8. Installation Package Direction

当前阶段**仅定义**安装包命名与内容方向，**不生成**实际安装包。

| Package Name | Contents | Target Mode |
|---|---|---|
| `ibms-all-in-one` | Console + Backend + DB + Redis + MinIO + AI | PoC / Demo |
| `ibms-frontend-console` | Console static build + Nginx config | All modes |
| `ibms-backend-core` | Core business API + auth/RBAC | All modes |
| `ibms-data` | PostgreSQL + TimescaleDB + migration + backup tools | Data Server |
| `ibms-link` | Link ingress + queue worker + notification adapters | Link Server |
| `ibms-edge` | Edge Interface agent + protocol adapters + simulators | Edge Server |
| `ibms-storage` | MinIO + storage API + signed URL service | Storage Server |
| `ibms-nexusai` | NexusAI inference service + model management | NexusAI Server |

**Packaging principles (future):**

- Each package ships with its own `docker-compose` fragment and merge instructions.
- `ibms-all-in-one` compose merges all fragments for PoC.
- Enterprise mode uses selective package deployment per server role.
- All packages reference `contracts/` for API compatibility version pinning.

---

## 9. Mode Selection Guide

| Criteria | Recommended Mode |
|---|---|
| Local development | Current Development Mode |
| Customer demo / PoC | PoC / Demo (One Server) |
| First commercial deployment | **Two-Server Minimum Production** |
| High integration volume | Three-Server Standard |
| Multi-site enterprise + OT isolation | Enterprise Multi-Server |
| SLA ≥ 99.9% | Any production mode + HA overlay |

---

## 10. Current State vs Target

| Aspect | Current (2026-06-16) | Target (Future) |
|---|---|---|
| Physical packages | 2 (main + backend zip) | 2–8 depending on mode |
| Service processes | 1 (Flask monolith) | 1–6 |
| Database | SQLAlchemy (embedded config) | PostgreSQL + TimescaleDB |
| Object storage | Local `data/` directory | MinIO |
| AI | Local pkl model | NexusAI service |
| Contracts | Documentation placeholder | Versioned protocol registry |

---

## 11. Related Documents

- [IBMS_MODULAR_BOUNDARY_A0.md](./IBMS_MODULAR_BOUNDARY_A0.md)
- [IBMS_LOGICAL_MODULE_BOUNDARY_A2.md](./IBMS_LOGICAL_MODULE_BOUNDARY_A2.md)
- [IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md](./IBMS_FORBIDDEN_ACCESS_MATRIX_A2.md)
