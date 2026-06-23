"""Local mock provider for Reports runtime skeleton."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_mock_rows(report_id: str, filters: Dict[str, Any], aggregation_level: str, limit: int) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for idx in range(limit):
        rows.append(
            {
                "recordId": f"{report_id}-row-{idx + 1}",
                "sourceType": "reference",
                "sourceReferenceId": f"ref-{idx + 1:04d}",
                "sourceModuleId": filters.get("moduleId", "source-reference"),
                "status": filters.get("status", "open"),
                "severity": filters.get("severity", "medium"),
                "category": filters.get("category", "general"),
                "timestamp": _utc_now_iso(),
                "evidenceReferenceId": filters.get("evidenceReferenceId", f"ev-{idx + 1:04d}"),
                "summary": f"Mock summary for {report_id} #{idx + 1}",
                "count": idx + 1,
                "trendValue": round((idx + 1) * 1.25, 2),
                "aggregationLevel": aggregation_level,
            }
        )

    columns = [
        "recordId",
        "sourceType",
        "sourceReferenceId",
        "sourceModuleId",
        "status",
        "severity",
        "category",
        "timestamp",
        "evidenceReferenceId",
        "summary",
        "count",
        "trendValue",
        "aggregationLevel",
    ]

    summary = {
        "rowCount": len(rows),
        "aggregationLevel": aggregation_level,
        "timeRange": filters.get("timeRange", "unspecified"),
    }

    return {"columns": columns, "rows": rows, "summary": summary}


REPORTS_GA_R13_SCOPE = "REPORTS_GA_R13"
REPORTS_GA_R13_MODE = "read_only"
REPORTS_GA_R13_READINESS = "CUSTOMER_DEMO_REPORT_PACK"
REPORTS_GA_R13_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
REPORTS_GA_R13_APP_TARGET = "192.168.60.21"
REPORTS_GA_R13_DB_TARGET = "192.168.60.22"
REPORTS_GA_R13_EXPORT_PATH = "Reports -> CODE -> Policy Gate -> Approval -> Audit / UCDE -> Export Artifact"


def reports_ga_r13_common() -> Dict[str, Any]:
    return {
        "scope": REPORTS_GA_R13_SCOPE,
        "mode": REPORTS_GA_R13_MODE,
        "readinessLevel": REPORTS_GA_R13_READINESS,
        "visualStyle": REPORTS_GA_R13_STYLE,
        "customerDemoReportPack": True,
        "exportCenterPreview": True,
        "exportExecuted": False,
        "reportGenerated": False,
        "pdfGenerated": False,
        "excelGenerated": False,
        "zipGenerated": False,
        "dbWrite": False,
        "evidenceWrite": False,
        "runtimeActivation": False,
        "edgeCommandExecution": False,
        "linkCommandExecution": False,
        "productionActivation": False,
        "appNonDbTarget": REPORTS_GA_R13_APP_TARGET,
        "dbOnlyTarget": REPORTS_GA_R13_DB_TARGET,
        "deploymentExecuted": False,
        "sshExecuted": False,
        "futureExportPath": REPORTS_GA_R13_EXPORT_PATH,
    }


def _report_item(
    report_id: str,
    report_name: str,
    report_category: str,
    source_module: str,
    linked_workspace: str,
) -> Dict[str, Any]:
    return {
        "reportId": report_id,
        "reportName": report_name,
        "reportCategory": report_category,
        "sourceModule": source_module,
        "linkedWorkspace": linked_workspace,
        "customerVisible": True,
        "engineerVisible": True,
        "adminVisible": True,
        "exportFormats": ["PDF Preview", "Excel Preview", "CSV Preview", "Evidence Bundle Preview"],
        "evidenceLinked": True,
        "readinessStatus": "CUSTOMER_DEMO_READY",
        "exportState": "NOT_EXECUTED",
        "readOnly": True,
    }


REPORTS_GA_R13_LIBRARY = [
    _report_item("r13-umms-maintenance", "UMMS Maintenance Report", "Maintenance", "UMMS", "UMMS Production-grade Maintenance Workspace"),
    _report_item("r13-work-order-summary", "Work Order Summary Report", "Maintenance", "UMMS", "Work Management"),
    _report_item("r13-engineer-dispatch", "Engineer Dispatch Report", "Maintenance", "UMMS", "Engineer Dispatch"),
    _report_item("r13-uhmi-system-status", "UHMI System Status Report", "System Status", "UHMI", "UConsole / UHMI Workspace"),
    _report_item("r13-uhmi-workspace-evidence", "UHMI Workspace Evidence Report", "Evidence", "UHMI", "UHMI Evidence & Reports"),
    _report_item("r13-ucde-evidence-trace", "UCDE Evidence Trace Report", "Evidence", "UCDE", "UCDE Evidence Center"),
    _report_item("r13-ucde-release-evidence", "UCDE Release Evidence Report", "Evidence", "UCDE", "UCDE Release Evidence"),
    _report_item("r13-customer-delivery-handoff", "Customer Delivery Handoff Report", "Delivery", "Customer Delivery", "Customer Delivery"),
    _report_item("r13-customer-acceptance", "Customer Acceptance Report", "Delivery", "Customer Delivery", "Customer Acceptance"),
    _report_item("r13-foundation-diagnostics", "Foundation Diagnostics Readiness Report", "Foundation", "Foundation Diagnostics", "Engineer Diagnostics Workspace"),
    _report_item("r13-package-readiness", "Package Readiness Report", "Foundation", "Foundation Diagnostics", "Package Readiness"),
    _report_item("r13-audit-compliance", "Audit / Compliance Summary Report", "Governance", "Governance & Security", "Audit / Compliance"),
]


def reports_ga_r13_export_center() -> Dict[str, Any]:
    return {
        **reports_ga_r13_common(),
        "exportCenter": {
            "supportedFormats": ["PDF Preview", "Excel Preview", "CSV Preview", "Evidence Bundle Preview"],
            "exportQueuePreview": [
                {"queueId": "EXP-R13-001", "reportName": "UMMS Maintenance Report", "format": "PDF Preview", "executionState": "NOT_EXECUTED", "readOnly": True},
                {"queueId": "EXP-R13-002", "reportName": "UCDE Evidence Trace Report", "format": "Evidence Bundle Preview", "executionState": "NOT_EXECUTED", "readOnly": True},
            ],
            "exportPolicy": "Requires future CODE policy gate, approval, and audit / UCDE record before real export.",
            "approvalRequired": True,
            "auditRequired": True,
            "exportExecuted": False,
            "generatedArtifact": False,
            "readOnly": True,
        },
    }


def reports_ga_r13_workspace() -> Dict[str, Any]:
    return {
        **reports_ga_r13_common(),
        "reportSummaryCards": [
            {"label": "Report Library", "value": len(REPORTS_GA_R13_LIBRARY), "status": "Ready"},
            {"label": "Ready Reports", "value": 12, "status": "Customer Demo"},
            {"label": "Evidence-linked Reports", "value": 12, "status": "Linked"},
            {"label": "Customer Handoff Reports", "value": 2, "status": "Ready"},
            {"label": "Export Formats", "value": 4, "status": "Preview"},
            {"label": "Export Guardrails", "value": 10, "status": "Active"},
            {"label": "Audit Coverage", "value": "UCDE", "status": "Referenced"},
            {"label": "Demo Readiness", "value": "Ready", "status": "Read-only"},
        ],
        "reportLibrary": REPORTS_GA_R13_LIBRARY,
        "exportCenter": reports_ga_r13_export_center()["exportCenter"],
        "moduleLinkage": ["UHMI", "UCDE", "UMMS", "Customer Delivery", "Foundation Diagnostics", "UConsole", "Reports & Analytics", "Governance & Security"],
        "customerReportPack": ["Customer Overview Report", "Maintenance Summary Report", "Evidence Summary Report", "Delivery Handoff Report", "Foundation Readiness Report", "Acceptance Checklist Report"],
        "engineerReportPack": ["Installation Readiness Report", "Package Readiness Report", "Foundation Diagnostics Report", "Server Planning Report", "Validation Result Report", "Risk / Guardrail Report"],
        "adminReportPack": ["Role / Menu Visibility Report", "Package State Preview Report", "Audit Boundary Report", "Compliance Mapping Report", "Production Activation Gap Report"],
        "guardrails": ["No Real Export Execution", "No PDF Generation", "No Excel Generation", "No ZIP Generation", "No DB Write", "No Evidence Write", "No Runtime Activation", "No EDGE Command Execution", "No LINK Command Execution", "No Production Activation"],
    }


def reports_ga_r13_section(name: str) -> Dict[str, Any]:
    workspace = reports_ga_r13_workspace()
    mapping = {
        "customer-demo-pack": workspace,
        "export-center": reports_ga_r13_export_center(),
        "report-library": {"reportLibrary": REPORTS_GA_R13_LIBRARY},
        "umms-maintenance": {"reports": [row for row in REPORTS_GA_R13_LIBRARY if row["sourceModule"] == "UMMS"]},
        "uhmi-system-status": {"reports": [row for row in REPORTS_GA_R13_LIBRARY if row["sourceModule"] == "UHMI"]},
        "ucde-evidence": {"reports": [row for row in REPORTS_GA_R13_LIBRARY if row["sourceModule"] == "UCDE"]},
        "customer-delivery-handoff": {"reports": [row for row in REPORTS_GA_R13_LIBRARY if row["sourceModule"] == "Customer Delivery"]},
        "foundation-diagnostics": {"reports": [row for row in REPORTS_GA_R13_LIBRARY if row["sourceModule"] == "Foundation Diagnostics"]},
        "package-readiness": {"reports": [row for row in REPORTS_GA_R13_LIBRARY if "Package Readiness" in row["reportName"]]},
        "audit-compliance": {"reports": [row for row in REPORTS_GA_R13_LIBRARY if row["sourceModule"] == "Governance & Security"]},
        "export-queue-preview": {"exportQueuePreview": workspace["exportCenter"]["exportQueuePreview"]},
        "guardrails": {"guardrails": workspace["guardrails"]},
    }
    return {**reports_ga_r13_common(), **mapping.get(name, workspace)}
