"""UConsole module readiness registry (read-only foundation)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _health_item(status: str, label: str, message: str, score: int) -> Dict[str, Any]:
    return {
        "status": status,
        "label": label,
        "message": message,
        "score": max(0, min(int(score), 100)),
    }


def _security_flags() -> Dict[str, Any]:
    return {
        "realRbacIntegrated": False,
        "dbAuditIntegrated": False,
        "siemIntegrated": False,
        "ucdeRuntimeIntegrated": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
    }


def _module_record(
    *,
    module_id: str,
    module_name: str,
    module_type: str,
    domain: str,
    route: Optional[str],
    runtime_status: str,
    readiness_level: str,
    lifecycle_stage: str,
    frontend_ready: bool,
    backend_ready: bool,
    api_ready: bool,
    audit_readiness: str,
    permission_mode: str,
    data_persistence_mode: str,
    integration_mode: str,
    health_status: str,
    health_score: int,
    health_details: Dict[str, Any],
    limitations: List[str],
    dependencies: List[str],
    next_actions: Optional[List[str]] = None,
    readiness_notes: Optional[List[str]] = None,
    boundary_notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "moduleId": module_id,
        "moduleName": module_name,
        "moduleType": module_type,
        "domain": domain,
        "route": route or "",
        "runtimeStatus": runtime_status,
        "readinessLevel": readiness_level,
        "lifecycleStage": lifecycle_stage,
        "frontendReady": bool(frontend_ready),
        "backendReady": bool(backend_ready),
        "apiReady": bool(api_ready),
        "auditReadiness": audit_readiness,
        "permissionMode": permission_mode,
        "dataPersistenceMode": data_persistence_mode,
        "integrationMode": integration_mode,
        "healthStatus": health_status,
        "healthScore": max(0, min(int(health_score), 100)),
        "healthDetails": health_details,
        "securityFlags": _security_flags(),
        "limitations": limitations,
        "dependencies": dependencies,
        "nextActions": next_actions or [],
        "readinessNotes": readiness_notes or [],
        "boundaryNotes": boundary_notes or [],
        "lastUpdated": _utc_now_iso(),
        "readOnly": True,
        "controlActionsEnabled": False,
        "certified": False,
        "iec62443Certified": False,
    }


def get_module_readiness_registry() -> List[Dict[str, Any]]:
    return [
        _module_record(
            module_id="reports",
            module_name="Reports",
            module_type="platform-module",
            domain="platform-operations",
            route="/reports",
            runtime_status="ready",
            readiness_level="readiness-candidate",
            lifecycle_stage="runnable-readiness",
            frontend_ready=True,
            backend_ready=True,
            api_ready=True,
            audit_readiness="ready",
            permission_mode="placeholder-allow",
            data_persistence_mode="local-jsonl-audit",
            integration_mode="local-skeleton",
            health_status="ready",
            health_score=82,
            health_details={
                "frontend": _health_item("ready", "Frontend", "Reports UI route and workflow are available.", 85),
                "backend": _health_item("ready", "Backend", "Reports API skeleton and service foundation available.", 82),
                "api": _health_item("ready", "API", "Core reports endpoints and manifest flow are available.", 83),
                "audit": _health_item("ready", "Audit", "Local JSONL audit foundation with verification is available.", 82),
                "permission": _health_item("limited", "Permission", "Placeholder permission mode only.", 60),
                "dataPersistence": _health_item(
                    "foundation",
                    "Data Persistence",
                    "Audit persistence uses local JSONL foundation only.",
                    70,
                ),
                "security": _health_item("foundation", "Security", "Security posture is foundation-level only.", 68),
                "integration": _health_item("limited", "Integration", "No external runtime integration enabled.", 65),
            },
            limitations=[
                "No real auth/RBAC integration.",
                "No DB audit table migration.",
                "No formal certified evidence protocol.",
            ],
            dependencies=["uconsole", "platform-menu", "reports-api"],
            next_actions=[
                "Maintain readiness candidate.",
                "Plan DB audit and RBAC integration in later stages.",
            ],
            readiness_notes=["Audit readiness foundation with placeholder permission mode."],
        ),
        _module_record(
            module_id="uconsole",
            module_name="UConsole / Platform Operations Dashboard",
            module_type="platform-module",
            domain="platform-operations",
            route="/console/operations",
            runtime_status="foundation",
            readiness_level="r2-foundation",
            lifecycle_stage="platform-foundation",
            frontend_ready=True,
            backend_ready=True,
            api_ready=True,
            audit_readiness="limited",
            permission_mode="placeholder-allow",
            data_persistence_mode="none",
            integration_mode="local-skeleton",
            health_status="foundation",
            health_score=70,
            health_details={
                "frontend": _health_item("foundation", "Frontend", "Dashboard UI and fallback handling are available.", 74),
                "backend": _health_item("foundation", "Backend", "Read-only console service and registry endpoints available.", 72),
                "api": _health_item("foundation", "API", "Console health, summary, and registry APIs are available.", 72),
                "audit": _health_item("limited", "Audit", "No dedicated console audit persistence in this stage.", 50),
                "permission": _health_item("limited", "Permission", "Placeholder permission mode only.", 60),
                "dataPersistence": _health_item("not-integrated", "Data Persistence", "No persistent store required for R2.", 40),
                "security": _health_item("foundation", "Security", "Read-only posture with no control actions.", 70),
                "integration": _health_item("limited", "Integration", "No cross-module runtime probes in this stage.", 58),
            },
            limitations=[
                "Read-only dashboard only.",
                "No control actions or orchestration.",
                "No runtime integration calls to external foundations.",
            ],
            dependencies=["router", "menu", "console-api"],
            next_actions=[
                "Freeze UConsole foundation.",
                "Use as platform module entry point for read-only operations.",
            ],
            readiness_notes=["Read-only dashboard foundation with local registry-derived score."],
        ),
        _module_record(
            module_id="ucde",
            module_name="UCDE Evidence Center",
            module_type="business-module",
            domain="compliance-evidence",
            route="/ucde/evidence",
            runtime_status="foundation",
            readiness_level="r2-foundation",
            lifecycle_stage="evidence-linkage-foundation",
            frontend_ready=True,
            backend_ready=True,
            api_ready=True,
            audit_readiness="foundation",
            permission_mode="placeholder-allow",
            data_persistence_mode="local-mock-provider",
            integration_mode="local-skeleton",
            health_status="foundation",
            health_score=64,
            health_details={
                "frontend": _health_item("foundation", "Frontend", "UCDE evidence linkage and detail views are available.", 66),
                "backend": _health_item("foundation", "Backend", "UCDE local provider includes linkage and path skeletons.", 64),
                "api": _health_item("foundation", "API", "UCDE health/list/detail/verify/relationships endpoints are available.", 64),
                "audit": _health_item("foundation", "Audit", "Traceability readiness uses hash-only local evidence.", 58),
                "permission": _health_item("limited", "Permission", "Placeholder permission mode only.", 52),
                "dataPersistence": _health_item(
                    "foundation", "Data Persistence", "Local mock provider only; no DB persistence.", 46
                ),
                "security": _health_item("limited", "Security", "No signature or certification integration in this stage.", 46),
                "integration": _health_item("limited", "Integration", "No runtime calls to Reports, EDGE, or LINK.", 42),
            },
            limitations=[
                "No DB evidence store.",
                "No digital signature integration.",
                "No formal certified evidence protocol.",
                "No Reports runtime integration.",
                "No EDGE or LINK runtime integration.",
                "No runtime source validation.",
                "Relationship graph is local skeleton only.",
            ],
            dependencies=["local-ucde-provider", "uconsole", "reports-reference-only"],
            next_actions=[
                "Add persistent evidence store later.",
                "Add runtime Reports audit linkage later.",
                "Add signature verification later.",
            ],
            readiness_notes=[
                "UCDE R2 uses local skeleton references for traceability readiness.",
                "UCDE R1-R2 readiness freeze completed with a no-op runtime gate decision.",
                "Evidence persistence gate is deferred; local-mock-provider remains active in this stage.",
            ],
        ),
        _module_record(
            module_id="uesg",
            module_name="UESG Sustainability",
            module_type="business-module",
            domain="sustainability",
            route="",
            runtime_status="planned",
            readiness_level="planned-runtime",
            lifecycle_stage="planned",
            frontend_ready=False,
            backend_ready=False,
            api_ready=False,
            audit_readiness="planned",
            permission_mode="not-integrated",
            data_persistence_mode="not-integrated",
            integration_mode="not-integrated",
            health_status="planned",
            health_score=28,
            health_details={
                "frontend": _health_item("planned", "Frontend", "UI runtime not integrated.", 28),
                "backend": _health_item("planned", "Backend", "Backend runtime not integrated.", 28),
                "api": _health_item("planned", "API", "API runtime not integrated.", 28),
                "audit": _health_item("planned", "Audit", "Audit readiness pending.", 24),
                "permission": _health_item("planned", "Permission", "Permission integration pending.", 24),
                "dataPersistence": _health_item("planned", "Data Persistence", "Persistence planning only.", 24),
                "security": _health_item("planned", "Security", "Security controls not integrated.", 24),
                "integration": _health_item("not-integrated", "Integration", "No runtime integration enabled.", 20),
            },
            limitations=["Runtime not integrated in current stage."],
            dependencies=["planned-roadmap"],
            next_actions=["Create runtime foundation before enabling module launch."],
        ),
        _module_record(
            module_id="umms",
            module_name="UMMS Maintenance",
            module_type="business-module",
            domain="maintenance",
            route="",
            runtime_status="planned",
            readiness_level="planned-runtime",
            lifecycle_stage="planned",
            frontend_ready=False,
            backend_ready=False,
            api_ready=False,
            audit_readiness="planned",
            permission_mode="not-integrated",
            data_persistence_mode="not-integrated",
            integration_mode="not-integrated",
            health_status="planned",
            health_score=28,
            health_details={
                "frontend": _health_item("planned", "Frontend", "UI runtime not integrated.", 28),
                "backend": _health_item("planned", "Backend", "Backend runtime not integrated.", 28),
                "api": _health_item("planned", "API", "API runtime not integrated.", 28),
                "audit": _health_item("planned", "Audit", "Audit readiness pending.", 24),
                "permission": _health_item("planned", "Permission", "Permission integration pending.", 24),
                "dataPersistence": _health_item("planned", "Data Persistence", "Persistence planning only.", 24),
                "security": _health_item("planned", "Security", "Security controls not integrated.", 24),
                "integration": _health_item("not-integrated", "Integration", "No runtime integration enabled.", 20),
            },
            limitations=["Runtime not integrated in current stage."],
            dependencies=["planned-roadmap"],
            next_actions=["Create runtime foundation before enabling module launch."],
        ),
        _module_record(
            module_id="assets-topology",
            module_name="Assets & Topology",
            module_type="platform-module",
            domain="asset-management",
            route="",
            runtime_status="planned",
            readiness_level="planned-runtime",
            lifecycle_stage="planned",
            frontend_ready=False,
            backend_ready=False,
            api_ready=False,
            audit_readiness="planned",
            permission_mode="not-integrated",
            data_persistence_mode="not-integrated",
            integration_mode="not-integrated",
            health_status="planned",
            health_score=26,
            health_details={
                "frontend": _health_item("planned", "Frontend", "UI runtime not integrated.", 26),
                "backend": _health_item("planned", "Backend", "Backend runtime not integrated.", 26),
                "api": _health_item("planned", "API", "API runtime not integrated.", 26),
                "audit": _health_item("planned", "Audit", "Audit readiness pending.", 22),
                "permission": _health_item("planned", "Permission", "Permission integration pending.", 22),
                "dataPersistence": _health_item("planned", "Data Persistence", "Persistence planning only.", 22),
                "security": _health_item("planned", "Security", "Security controls not integrated.", 22),
                "integration": _health_item("not-integrated", "Integration", "No runtime integration enabled.", 18),
            },
            limitations=["Runtime not integrated in current stage."],
            dependencies=["planned-roadmap"],
            next_actions=["Create runtime foundation before enabling module launch."],
        ),
        _module_record(
            module_id="edge-fleet",
            module_name="EDGE Fleet",
            module_type="foundation-module",
            domain="foundation-reference",
            route="",
            runtime_status="not-integrated",
            readiness_level="external-foundation-reference",
            lifecycle_stage="not-integrated",
            frontend_ready=False,
            backend_ready=False,
            api_ready=False,
            audit_readiness="not-integrated",
            permission_mode="not-integrated",
            data_persistence_mode="not-integrated",
            integration_mode="foundation-reference-only",
            health_status="not-integrated",
            health_score=18,
            health_details={
                "frontend": _health_item("not-integrated", "Frontend", "No frontend runtime integration.", 18),
                "backend": _health_item("not-integrated", "Backend", "No backend runtime integration.", 18),
                "api": _health_item("not-integrated", "API", "No API runtime integration.", 18),
                "audit": _health_item("not-integrated", "Audit", "No audit runtime integration.", 18),
                "permission": _health_item("not-integrated", "Permission", "No permission integration.", 18),
                "dataPersistence": _health_item("not-integrated", "Data Persistence", "No persistence integration.", 18),
                "security": _health_item("limited", "Security", "Reference-only posture in this stage.", 25),
                "integration": _health_item("not-integrated", "Integration", "Runtime integration is disabled.", 18),
            },
            limitations=["Foundation reference only; runtime integration disabled."],
            dependencies=["foundation-contract-reference"],
            next_actions=["Keep boundary separated until integration is explicitly approved."],
            boundary_notes=["Separate shared foundation boundary; no runtime call from UConsole."],
        ),
        _module_record(
            module_id="link-gateway",
            module_name="LINK Gateway",
            module_type="foundation-module",
            domain="foundation-reference",
            route="",
            runtime_status="not-integrated",
            readiness_level="external-foundation-reference",
            lifecycle_stage="not-integrated",
            frontend_ready=False,
            backend_ready=False,
            api_ready=False,
            audit_readiness="not-integrated",
            permission_mode="not-integrated",
            data_persistence_mode="not-integrated",
            integration_mode="foundation-reference-only",
            health_status="not-integrated",
            health_score=18,
            health_details={
                "frontend": _health_item("not-integrated", "Frontend", "No frontend runtime integration.", 18),
                "backend": _health_item("not-integrated", "Backend", "No backend runtime integration.", 18),
                "api": _health_item("not-integrated", "API", "No API runtime integration.", 18),
                "audit": _health_item("not-integrated", "Audit", "No audit runtime integration.", 18),
                "permission": _health_item("not-integrated", "Permission", "No permission integration.", 18),
                "dataPersistence": _health_item("not-integrated", "Data Persistence", "No persistence integration.", 18),
                "security": _health_item("limited", "Security", "Reference-only posture in this stage.", 25),
                "integration": _health_item("not-integrated", "Integration", "Runtime integration is disabled.", 18),
            },
            limitations=["Foundation reference only; runtime integration disabled."],
            dependencies=["foundation-contract-reference"],
            next_actions=["Keep boundary separated until integration is explicitly approved."],
            boundary_notes=["Separate shared foundation boundary; no runtime call from UConsole."],
        ),
        _module_record(
            module_id="nexus-ai",
            module_name="NEXUS-AI",
            module_type="platform-module",
            domain="analytics-ai",
            route="",
            runtime_status="planned",
            readiness_level="planned-runtime",
            lifecycle_stage="planned",
            frontend_ready=False,
            backend_ready=False,
            api_ready=False,
            audit_readiness="planned",
            permission_mode="not-integrated",
            data_persistence_mode="not-integrated",
            integration_mode="not-integrated",
            health_status="planned",
            health_score=25,
            health_details={
                "frontend": _health_item("planned", "Frontend", "UI runtime not integrated.", 25),
                "backend": _health_item("planned", "Backend", "Backend runtime not integrated.", 25),
                "api": _health_item("planned", "API", "API runtime not integrated.", 25),
                "audit": _health_item("planned", "Audit", "Audit readiness pending.", 22),
                "permission": _health_item("planned", "Permission", "Permission integration pending.", 22),
                "dataPersistence": _health_item("planned", "Data Persistence", "Persistence planning only.", 22),
                "security": _health_item("planned", "Security", "Security controls not integrated.", 22),
                "integration": _health_item("not-integrated", "Integration", "No runtime integration enabled.", 18),
            },
            limitations=["Runtime not integrated in current stage."],
            dependencies=["planned-roadmap"],
            next_actions=["Create runtime foundation before enabling module launch."],
        ),
    ]


def list_module_readiness() -> List[Dict[str, Any]]:
    return get_module_readiness_registry()


def get_module_readiness(module_id: str) -> Optional[Dict[str, Any]]:
    if not module_id:
        return None
    target = module_id.strip().lower()
    for module in get_module_readiness_registry():
        if str(module.get("moduleId", "")).lower() == target:
            return module
    return None


def calculate_registry_summary(modules: List[Dict[str, Any]]) -> Dict[str, Any]:
    items = modules or []
    total_modules = len(items)
    ready_modules = [item for item in items if item.get("runtimeStatus") == "ready"]
    foundation_modules = [item for item in items if item.get("runtimeStatus") == "foundation"]
    planned_modules = [item for item in items if item.get("runtimeStatus") == "planned"]
    not_integrated_modules = [item for item in items if item.get("runtimeStatus") == "not-integrated"]
    audit_ready_modules = [item for item in items if str(item.get("auditReadiness")) in {"ready", "foundation", "limited"}]
    health_scores = [int(item.get("healthScore", 0) or 0) for item in items]
    average_health = round(sum(health_scores) / total_modules, 2) if total_modules > 0 else 0.0

    sorted_by_health = sorted(items, key=lambda row: int(row.get("healthScore", 0) or 0))
    lowest = [
        {"moduleId": row.get("moduleId"), "healthScore": row.get("healthScore")}
        for row in sorted_by_health[:3]
    ]
    highest = [
        {"moduleId": row.get("moduleId"), "healthScore": row.get("healthScore")}
        for row in reversed(sorted_by_health[-3:])
    ]

    return {
        "totalModules": total_modules,
        "readyModules": len(ready_modules),
        "foundationModules": len(foundation_modules),
        "plannedModules": len(planned_modules),
        "notIntegratedModules": len(not_integrated_modules),
        "auditReadyModules": len(audit_ready_modules),
        "certifiedModules": 0,
        "iec62443CertifiedModules": 0,
        "averageHealthScore": average_health,
        "lowestHealthModules": lowest,
        "highestHealthModules": highest,
    }


def get_registry_health_details() -> List[Dict[str, Any]]:
    return get_module_readiness_registry()

