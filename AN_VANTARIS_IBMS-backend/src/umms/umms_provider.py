"""UMMS local provider (read-only skeleton)."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


LATEST_UMMS_PACKAGE_UCONSOLE_TAG = "umms-package-uconsole-stakeholder-entry-readiness-local-freeze-20260621"
UMMS_R11_BASELINE_HEAD = "1e39b7dd7a3e1ad4251206a9b82b6573269bd82e"
PACKAGE_ENTRY_REGISTRY = "AN_VANTARIS_ONE/registries/umms-package-uconsole-stakeholder-entry-readiness.v1.json"
LOCAL_FREEZE_REGISTRY = "AN_VANTARIS_ONE/registries/umms-package-uconsole-stakeholder-entry-local-freeze.v1.json"
STAKEHOLDER_REVIEW_REGISTRY = "AN_VANTARIS_ONE/registries/umms-stakeholder-review-package.v1.json"
STAKEHOLDER_REVIEW_PACKAGE = "ONE_UMMS_R10_STAKEHOLDER_REVIEW_PACKAGE.md"
SAFETY_FALSE_DEFAULTS = {
    "productionActivation": False,
    "runtimeActivation": False,
    "dbWrite": False,
    "approvalExecution": False,
    "workflowExecution": False,
    "workOrderRuntimeExecution": False,
    "pmExecution": False,
    "inventoryTransaction": False,
    "vendorContractSlaRuntime": False,
    "evidenceClosureExecution": False,
    "hmiRuntimeExecution": False,
    "deviceConnection": False,
    "connectorExecution": False,
    "edgeRuntimeCall": False,
    "linkRuntimeCall": False,
    "oneAdapterIntroduced": False,
}


def _repo_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AN_VANTARIS_ONE").is_dir() and (parent / "AN_VANTARIS_IBMS-backend").is_dir():
            return parent
    raise RuntimeError("VANTARIS ONE repository root not found")


def _load_registry(relative_path: str) -> Dict[str, Any]:
    path = _repo_root() / relative_path
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{relative_path} must contain a JSON object")
    return data


def _readonly_api_guard() -> Dict[str, Any]:
    return {
        "readOnly": True,
        "runtimeEnabled": False,
        "productionEnabled": False,
        "dbWriteEnabled": False,
        "workflowEnabled": False,
        "approvalEnabled": False,
        "writeActionsEnabled": False,
        "edgeRuntimeCall": False,
        "linkRuntimeCall": False,
        "oneAdapterIntroduced": False,
    }


def _source_descriptor(root_key: str, relative_path: str) -> Dict[str, Any]:
    return {
        "type": "local_projection_registry",
        "path": relative_path,
        "rootKey": root_key,
        "authority": "UMMS_PACKAGE_UCONSOLE_STAKEHOLDER_ENTRY_LOCAL_FREEZE",
    }


def _with_guard(payload: Dict[str, Any]) -> Dict[str, Any]:
    guarded = dict(payload)
    guarded.update(_readonly_api_guard())
    return guarded


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _work_order(
    *,
    work_order_id: str,
    work_order_code: str,
    title: str,
    description: str,
    work_order_type: str,
    work_order_category: str,
    work_order_status: str,
    priority: str,
    lifecycle_stage: str,
    site_id: str,
    site_name: str,
    system_id: str,
    system_name: str,
    asset_id: str,
    asset_name: str,
    requested_by: str,
    assigned_team: str,
    assigned_technician: str,
    planned_start: str,
    planned_end: str,
    source_system: str = "local-umms-provider",
    source_record_id: str = "",
) -> Dict[str, Any]:
    now = _now_iso()
    return {
        "workOrderId": work_order_id,
        "workOrderCode": work_order_code,
        "title": title,
        "description": description,
        "workOrderType": work_order_type,
        "workOrderCategory": work_order_category,
        "workOrderStatus": work_order_status,
        "priority": priority,
        "lifecycleStage": lifecycle_stage,
        "siteId": site_id,
        "siteName": site_name,
        "systemId": system_id,
        "systemName": system_name,
        "assetId": asset_id,
        "assetName": asset_name,
        "requestedBy": requested_by,
        "assignedTeam": assigned_team,
        "assignedTechnician": assigned_technician,
        "plannedStart": planned_start,
        "plannedEnd": planned_end,
        "createdAt": now,
        "updatedAt": now,
        "sourceSystem": source_system,
        "sourceRecordId": source_record_id or work_order_id,
        "provider": "local-umms-provider",
        "runtimeMode": "skeleton",
        "sourceSemantics": "ibms-neutral",
        "mockData": True,
        "readOnly": True,
        "dispatchEnabled": False,
        "mobileIntegrated": False,
        "notificationIntegrated": False,
        "assetRuntimeIntegrated": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "tags": [work_order_type, work_order_category, work_order_status],
        "metadata": {"stage": "umms-r1"},
        "limitations": [
            "Local skeleton work order only.",
            "Dispatch workflow is not integrated.",
            "Mobile integration is not integrated.",
            "Notification delivery is not integrated.",
            "EDGE/LINK integration is not integrated.",
            "DB persistence is not integrated.",
        ],
        "certified": False,
        "iec62443Certified": False,
    }


def _base_work_orders() -> List[Dict[str, Any]]:
    return [
        _work_order(
            work_order_id="wo-preventive-chiller-monthly",
            work_order_code="UMMS-WO-001",
            title="Monthly Chiller Preventive Check",
            description="Monthly preventive maintenance checklist for chiller system.",
            work_order_type="preventive",
            work_order_category="hvac",
            work_order_status="planned",
            priority="medium",
            lifecycle_stage="planning",
            site_id="site-main",
            site_name="Main Site",
            system_id="system-mechanical",
            system_name="Mechanical System",
            asset_id="device-chiller-01",
            asset_name="Chiller 01",
            requested_by="facility-manager",
            assigned_team="hvac-team",
            assigned_technician="tech-placeholder-01",
            planned_start="2026-07-01T08:00:00Z",
            planned_end="2026-07-01T12:00:00Z",
            source_record_id="umms-r1-wo-001",
        ),
        _work_order(
            work_order_id="wo-inspection-electrical-panel",
            work_order_code="UMMS-WO-002",
            title="Electrical Panel Inspection",
            description="Scheduled inspection of main electrical panel.",
            work_order_type="inspection",
            work_order_category="electrical",
            work_order_status="scheduled",
            priority="medium",
            lifecycle_stage="scheduling",
            site_id="site-main",
            site_name="Main Site",
            system_id="system-electrical",
            system_name="Electrical System",
            asset_id="device-panel-01",
            asset_name="Electrical Panel 01",
            requested_by="safety-supervisor",
            assigned_team="electrical-team",
            assigned_technician="tech-placeholder-02",
            planned_start="2026-07-02T09:00:00Z",
            planned_end="2026-07-02T11:00:00Z",
            source_record_id="umms-r1-wo-002",
        ),
        _work_order(
            work_order_id="wo-corrective-pump-vibration",
            work_order_code="UMMS-WO-003",
            title="Pump Vibration Corrective Check",
            description="Corrective maintenance skeleton for reported pump vibration.",
            work_order_type="corrective",
            work_order_category="mechanical",
            work_order_status="open",
            priority="high",
            lifecycle_stage="triage",
            site_id="site-main",
            site_name="Main Site",
            system_id="system-mechanical",
            system_name="Mechanical System",
            asset_id="device-pump-01",
            asset_name="Pump 01",
            requested_by="operations-lead",
            assigned_team="mechanical-team",
            assigned_technician="tech-placeholder-03",
            planned_start="2026-07-03T08:30:00Z",
            planned_end="2026-07-03T14:30:00Z",
            source_system="local-umms-provider",
            source_record_id="umms-r1-wo-003",
        ),
        _work_order(
            work_order_id="wo-safety-check-plant-room",
            work_order_code="UMMS-WO-004",
            title="Plant Room Safety Checklist",
            description="Safety checklist skeleton for plant room.",
            work_order_type="safety",
            work_order_category="facility",
            work_order_status="planned",
            priority="high",
            lifecycle_stage="planning",
            site_id="site-main",
            site_name="Main Site",
            system_id="system-facility",
            system_name="Facility System",
            asset_id="zone-plant-room",
            asset_name="Plant Room",
            requested_by="safety-officer",
            assigned_team="facility-team",
            assigned_technician="tech-placeholder-04",
            planned_start="2026-07-04T09:00:00Z",
            planned_end="2026-07-04T11:00:00Z",
            source_record_id="umms-r1-wo-004",
        ),
        _work_order(
            work_order_id="wo-cleaning-air-filter",
            work_order_code="UMMS-WO-005",
            title="Air Filter Cleaning Routine",
            description="Routine cleaning skeleton for air filter group.",
            work_order_type="routine",
            work_order_category="hvac",
            work_order_status="in-review",
            priority="low",
            lifecycle_stage="review",
            site_id="site-main",
            site_name="Main Site",
            system_id="system-mechanical",
            system_name="Mechanical System",
            asset_id="device-ahu-01",
            asset_name="AHU 01",
            requested_by="facility-manager",
            assigned_team="hvac-team",
            assigned_technician="tech-placeholder-05",
            planned_start="2026-07-05T10:00:00Z",
            planned_end="2026-07-05T12:30:00Z",
            source_record_id="umms-r1-wo-005",
        ),
        _work_order(
            work_order_id="wo-asset-condition-review",
            work_order_code="UMMS-WO-006",
            title="Asset Condition Review",
            description="Condition review skeleton for selected assets.",
            work_order_type="condition-review",
            work_order_category="asset-management",
            work_order_status="draft",
            priority="low",
            lifecycle_stage="drafting",
            site_id="site-main",
            site_name="Main Site",
            system_id="system-asset",
            system_name="Asset Management System",
            asset_id="asset-group-main",
            asset_name="Main Asset Group",
            requested_by="asset-planner",
            assigned_team="asset-team",
            assigned_technician="tech-placeholder-06",
            planned_start="2026-07-06T08:00:00Z",
            planned_end="2026-07-06T10:00:00Z",
            source_record_id="umms-r1-wo-006",
        ),
    ]


def _normalized_work_orders() -> List[Dict[str, Any]]:
    return [deepcopy(item) for item in _base_work_orders()]


def list_work_orders(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    values = filters or {}
    work_order_type = str(values.get("workOrderType", "")).strip()
    work_order_category = str(values.get("workOrderCategory", "")).strip()
    work_order_status = str(values.get("workOrderStatus", "")).strip()
    priority = str(values.get("priority", "")).strip()
    site_id = str(values.get("siteId", "")).strip()
    system_id = str(values.get("systemId", "")).strip()
    asset_id = str(values.get("assetId", "")).strip()

    def _match(row: Dict[str, Any]) -> bool:
        if work_order_type and str(row.get("workOrderType", "")) != work_order_type:
            return False
        if work_order_category and str(row.get("workOrderCategory", "")) != work_order_category:
            return False
        if work_order_status and str(row.get("workOrderStatus", "")) != work_order_status:
            return False
        if priority and str(row.get("priority", "")) != priority:
            return False
        if site_id and str(row.get("siteId", "")) != site_id:
            return False
        if system_id and str(row.get("systemId", "")) != system_id:
            return False
        if asset_id and str(row.get("assetId", "")) != asset_id:
            return False
        return True

    return [row for row in _normalized_work_orders() if _match(row)]


def get_work_order(work_order_id: str) -> Optional[Dict[str, Any]]:
    target = str(work_order_id or "").strip()
    if not target:
        return None
    for row in _normalized_work_orders():
        if str(row.get("workOrderId", "")) == target:
            return row
    return None


def get_maintenance_summary() -> Dict[str, Any]:
    rows = _normalized_work_orders()
    return {
        "totalWorkOrders": len(rows),
        "preventiveCount": len([item for item in rows if str(item.get("workOrderType", "")) == "preventive"]),
        "correctiveCount": len([item for item in rows if str(item.get("workOrderType", "")) == "corrective"]),
        "inspectionCount": len([item for item in rows if str(item.get("workOrderType", "")) == "inspection"]),
        "safetyCount": len([item for item in rows if str(item.get("workOrderType", "")) == "safety"]),
        "routineCount": len([item for item in rows if str(item.get("workOrderType", "")) == "routine"]),
        "draftCount": len([item for item in rows if str(item.get("workOrderStatus", "")) == "draft"]),
        "openCount": len([item for item in rows if str(item.get("workOrderStatus", "")) == "open"]),
        "plannedCount": len([item for item in rows if str(item.get("workOrderStatus", "")) == "planned"]),
        "scheduledCount": len([item for item in rows if str(item.get("workOrderStatus", "")) == "scheduled"]),
        "inReviewCount": len([item for item in rows if str(item.get("workOrderStatus", "")) == "in-review"]),
        "highPriorityCount": len([item for item in rows if str(item.get("priority", "")) == "high"]),
        "mockWorkOrders": len([item for item in rows if bool(item.get("mockData"))]),
        "runtimeLinkedWorkOrders": 0,
        "dispatchedWorkOrders": 0,
        "mobileLinkedWorkOrders": 0,
        "notificationLinkedWorkOrders": 0,
        "certifiedWorkOrders": 0,
        "workOrderTypes": sorted({str(item.get("workOrderType", "")) for item in rows if str(item.get("workOrderType", "")).strip()}),
        "workOrderCategories": sorted(
            {str(item.get("workOrderCategory", "")) for item in rows if str(item.get("workOrderCategory", "")).strip()}
        ),
        "limitations": [
            "No DB work order store.",
            "No real dispatch workflow.",
            "No mobile integration.",
            "No notification delivery.",
            "No EDGE/LINK runtime integration.",
            "No Assets runtime integration.",
        ],
        "certified": False,
        "iec62443Certified": False,
    }


def get_work_order_breakdown() -> Dict[str, Any]:
    rows = _normalized_work_orders()

    def _group(field: str) -> List[Dict[str, Any]]:
        values = sorted({str(row.get(field, "")) for row in rows if str(row.get(field, "")).strip()})
        return [{"key": value, "count": len([row for row in rows if str(row.get(field, "")) == value])} for value in values]

    return {
        "breakdownMode": "local-skeleton-breakdown",
        "byType": _group("workOrderType"),
        "byStatus": _group("workOrderStatus"),
        "byPriority": _group("priority"),
        "byCategory": _group("workOrderCategory"),
        "runtimeLinked": False,
        "certified": False,
        "iec62443Certified": False,
    }


def get_maintenance_associations() -> Dict[str, Any]:
    rows = _normalized_work_orders()
    sites: Dict[str, Dict[str, Any]] = {}
    systems: Dict[str, Dict[str, Any]] = {}
    assets: Dict[str, Dict[str, Any]] = {}

    for row in rows:
        work_order_id = str(row.get("workOrderId", ""))
        site_id = str(row.get("siteId", ""))
        site_name = str(row.get("siteName", ""))
        system_id = str(row.get("systemId", ""))
        system_name = str(row.get("systemName", ""))
        asset_id = str(row.get("assetId", ""))
        asset_name = str(row.get("assetName", ""))

        if site_id:
            site_row = sites.setdefault(
                site_id,
                {"siteId": site_id, "siteName": site_name, "workOrderIds": [], "runtimeLinked": False},
            )
            site_row["workOrderIds"].append(work_order_id)
        if system_id:
            system_row = systems.setdefault(
                system_id,
                {"systemId": system_id, "systemName": system_name, "workOrderIds": [], "runtimeLinked": False},
            )
            system_row["workOrderIds"].append(work_order_id)
        if asset_id:
            asset_row = assets.setdefault(
                asset_id,
                {"assetId": asset_id, "assetName": asset_name, "workOrderIds": [], "runtimeLinked": False},
            )
            asset_row["workOrderIds"].append(work_order_id)

    return {
        "associationMode": "local-skeleton-association",
        "siteAssociations": [
            {**item, "workOrderIds": sorted(set(item["workOrderIds"]))} for item in sorted(sites.values(), key=lambda x: x["siteId"])
        ],
        "systemAssociations": [
            {**item, "workOrderIds": sorted(set(item["workOrderIds"]))}
            for item in sorted(systems.values(), key=lambda x: x["systemId"])
        ],
        "assetAssociations": [
            {**item, "workOrderIds": sorted(set(item["workOrderIds"]))}
            for item in sorted(assets.values(), key=lambda x: x["assetId"])
        ],
        "runtimeLinked": False,
        "assetRuntimeIntegrated": False,
        "notes": "Local skeleton maintenance association; Assets runtime integration is not integrated.",
        "certified": False,
        "iec62443Certified": False,
    }


def get_umms_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "moduleId": "umms",
        "moduleName": "UMMS Maintenance",
        "runtimeMode": "skeleton",
        "provider": "local-umms-provider",
        "sourceSemantics": "ibms-neutral",
        "readOnly": True,
        "controlActionsEnabled": False,
        "dispatchEnabled": False,
        "mobileIntegrated": False,
        "notificationIntegrated": False,
        "assetRuntimeIntegrated": False,
        "edgeRuntimeIntegrated": False,
        "linkRuntimeIntegrated": False,
        "dbPersistenceIntegrated": False,
        "certified": False,
        "iec62443Certified": False,
    }


def get_umms_package_entry_projection() -> Dict[str, Any]:
    registry = _load_registry(PACKAGE_ENTRY_REGISTRY)
    package_entry = deepcopy(registry.get("packageEntry", {}))
    reference = deepcopy(registry.get("stakeholderReviewPackageReference", {}))
    return _with_guard(
        {
            "platform": "VANTARIS ONE",
            "module": "UMMS",
            "projection": "umms_package_entry",
            "packageId": package_entry.get("packageId", "umms"),
            "packageName": package_entry.get("packageName", "Unified Maintenance Management System"),
            "packageDisplayName": package_entry.get("packageDisplayName", "UMMS"),
            "packageStatus": package_entry.get("packageStatus", "stakeholder_review_ready"),
            "entryMode": package_entry.get("entryMode", "read_only_stakeholder_review"),
            "latestTag": LATEST_UMMS_PACKAGE_UCONSOLE_TAG,
            "stakeholderReviewPackage": reference.get("packageDocument", STAKEHOLDER_REVIEW_PACKAGE),
            "source": _source_descriptor("packageEntry", PACKAGE_ENTRY_REGISTRY),
        }
    )


def get_umms_stakeholder_review_projection() -> Dict[str, Any]:
    stakeholder_registry = _load_registry(STAKEHOLDER_REVIEW_REGISTRY)
    local_freeze = _load_registry(LOCAL_FREEZE_REGISTRY)
    package_registry = _load_registry(PACKAGE_ENTRY_REGISTRY)
    return _with_guard(
        {
            "platform": "VANTARIS ONE",
            "module": "UMMS",
            "projection": "umms_stakeholder_review",
            "reviewPackageId": stakeholder_registry.get("reviewPackageId", "umms-stakeholder-review-package.v1"),
            "baselineHead": UMMS_R11_BASELINE_HEAD,
            "publishedTags": sorted(
                set(stakeholder_registry.get("publishedTags", []))
                | {
                    stakeholder_registry.get("latestArchivedTag", ""),
                    local_freeze.get("latestArchivedTag", ""),
                    LATEST_UMMS_PACKAGE_UCONSOLE_TAG,
                }
                - {""}
            ),
            "readinessChain": deepcopy(package_registry.get("ummsReadinessChainReference", [])),
            "knownLimitations": deepcopy(stakeholder_registry.get("knownLimitations", [])),
            "recommendedNextSteps": [
                "UMMS read-only API implementation, future",
                "UMMS read-only frontend implementation, future",
                "UMMS package runtime implementation, future only after explicit approval",
            ],
            "source": _source_descriptor("reviewPackageId", STAKEHOLDER_REVIEW_REGISTRY),
        }
    )


def get_umms_readiness_summary_projection() -> Dict[str, Any]:
    registry = _load_registry(PACKAGE_ENTRY_REGISTRY)
    return _with_guard(
        {
            "platform": "VANTARIS ONE",
            "module": "UMMS",
            "projection": "umms_readiness_summary",
            "readinessStages": deepcopy(registry.get("ummsReadinessChainReference", [])),
            "source": _source_descriptor("ummsReadinessChainReference", PACKAGE_ENTRY_REGISTRY),
        }
    )


def get_umms_customer_core_functions_projection() -> Dict[str, Any]:
    registry = _load_registry(PACKAGE_ENTRY_REGISTRY)
    functions = [
        {
            "function": item.get("function"),
            "coverageStatus": item.get("coverageStatus"),
            "readinessStage": item.get("readinessStage"),
            "runtimeEnabled": False,
            "futureOwner": item.get("futureOwner"),
            "remainingGap": item.get("remainingGap"),
        }
        for item in registry.get("customerCoreFunctionCoverage", [])
    ]
    return _with_guard(
        {
            "platform": "VANTARIS ONE",
            "module": "UMMS",
            "projection": "umms_customer_core_functions",
            "customerCoreFunctions": functions,
            "totalFunctions": len(functions),
            "source": _source_descriptor("customerCoreFunctionCoverage", PACKAGE_ENTRY_REGISTRY),
        }
    )


def get_umms_safety_posture_projection() -> Dict[str, Any]:
    registry = _load_registry(PACKAGE_ENTRY_REGISTRY)
    safety = {"readOnly": True, **SAFETY_FALSE_DEFAULTS, **deepcopy(registry.get("safetyPosture", {}))}
    safety.update(_readonly_api_guard())
    return _with_guard(
        {
            "platform": "VANTARIS ONE",
            "module": "UMMS",
            "projection": "umms_safety_posture",
            "safetyPosture": safety,
            "source": _source_descriptor("safetyPosture", PACKAGE_ENTRY_REGISTRY),
        }
    )
