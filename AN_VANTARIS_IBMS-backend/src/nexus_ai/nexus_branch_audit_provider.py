"""NexusAI read-only branch diff audit provider.

This provider does not invoke AI runtime, model APIs, git commands, shell
commands, remediation, workflow execution, persistence, EDGE/LINK commands, or
device control. It presents a static local branch audit projection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]
SCOPE = "NEXUSAI_GA_R3"
MODULE_ID = "nexus-ai-branch-audit"
MODULE_NAME = "NexusAI Branch Audit"
VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
PASS_MARKER = "ONE_NEXUSAI_GA_R3_BRANCH_DIFF_AUDIT_PASS"

BRANCH = "sync/ufms-foundation-packages-20260622-104646"
BASELINE_REMOTE_HEAD = "0ddf2a4c06fb5d50201b9b3936b85f4457c9c6c4"
ASSET_CONTEXT_COMMIT = "70fef5f1e2b27df0d5ce2fbdbf21cc4920b0e84d"
CODE_POLICY_COMMIT = "d2e1b6b72adb454338f0c1db6f39752ff19976c6"
LATEST_REMOTE_TAG = "reports-ga-r13-customer-demo-report-pack-export-center-freeze-20260622"
LOCAL_TAGS = [
    "asset-context-ga-r1-unified-linkage-local-freeze-20260623",
    "code-ga-r1-policy-gate-preview-local-freeze-20260623",
]

READ_ONLY_FLAGS: Dict[str, Any] = {
    "scope": SCOPE,
    "moduleId": MODULE_ID,
    "readOnly": True,
    "aiRuntimeEnabled": False,
    "modelApiCallEnabled": False,
    "autoFixEnabled": False,
    "codeMutationEnabled": False,
    "workflowExecutionEnabled": False,
    "dbWriteEnabled": False,
    "edgeCommandExecution": False,
    "linkCommandExecution": False,
    "deviceControlEnabled": False,
    "productionActivation": False,
    "visualStyle": VISUAL_STYLE,
}

SOURCE_REFERENCE_PATHS = [
    "AN_VANTARIS_ONE/ASSET_CONTEXT_GA_R1.md",
    "AN_VANTARIS_ONE/CODE_GA_R1.md",
    "AN_VANTARIS_ONE/registries/asset-context-ga-r1",
    "AN_VANTARIS_ONE/registries/code-ga-r1",
    "AN_VANTARIS_ONE/registries/nexusai-ga-r2",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_NexusAI/BOUNDARY.md",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Contracts/openapi/code-to-nexusai.v1.yaml",
]

GUARDRAILS = [
    "No AI runtime",
    "No model API call",
    "No auto-fix",
    "No code mutation",
    "No DB write",
    "No deployment",
    "No EDGE/LINK command",
    "No device control",
    "No production activation",
]


def common() -> Dict[str, Any]:
    return {
        **READ_ONLY_FLAGS,
        "moduleName": MODULE_NAME,
        "provider": "local-readonly-nexusai-branch-audit-provider",
        "passMarker": PASS_MARKER,
    }


def source_references() -> Dict[str, Any]:
    limitations: List[str] = []
    statuses: Dict[str, Any] = {}
    refs: List[Dict[str, Any]] = []
    for item in SOURCE_REFERENCE_PATHS:
        path = ROOT / item
        try:
            exists = path.exists()
            content_length = len(path.read_text(encoding="utf-8")) if path.is_file() else 0
            status = "available" if exists else "unavailable"
            if not exists:
                limitations.append(f"Reference source unavailable: {item}")
            statuses[item] = {"integrationStatus": status, "readOnly": True}
            refs.append({"path": item, "exists": exists, "contentLength": content_length, "readOnly": True})
        except Exception as exc:  # pragma: no cover - defensive read-only reference guard
            message = f"Reference source unavailable: {item} ({exc.__class__.__name__})"
            limitations.append(message)
            statuses[item] = {"integrationStatus": "unavailable", "readOnly": True, "reason": message}
            refs.append({"path": item, "exists": False, "contentLength": 0, "readOnly": True})
    return {"sourceReferences": refs, "providerStatuses": statuses, "limitations": limitations}


def commits() -> Dict[str, Any]:
    return {
        **common(),
        "branch": BRANCH,
        "items": [
            {
                "commitHash": BASELINE_REMOTE_HEAD,
                "shortHash": "0ddf2a4",
                "title": "Reports GA-R13 remote freeze",
                "localTag": LATEST_REMOTE_TAG,
                "changeType": "remote-freeze-baseline",
                "modulesTouched": ["Reports & Analytics"],
                "customerDemoImpact": "Customer demo report pack and export center visible.",
                "riskBoundary": "No real export, no PDF/Excel/ZIP generation, no production activation.",
                "validationMarker": "REPORTS_GA_R13_CUSTOMER_DEMO_REPORT_PACK_EXPORT_CENTER_PASS",
                "buildStatus": "PASS with existing frontend warnings",
                "remoteStatus": "remote-freeze",
            },
            {
                "commitHash": ASSET_CONTEXT_COMMIT,
                "shortHash": "70fef5f",
                "title": "Asset Context GA-R1 local freeze",
                "localTag": LOCAL_TAGS[0],
                "changeType": "local-readonly-linkage",
                "modulesTouched": ["Asset Context", "Assets & Topology", "UMMS", "UHMI", "UCDE", "Reports"],
                "customerDemoImpact": "Asset/System/Event/Work Order/Evidence linkage now visible.",
                "riskBoundary": "Local-only, no DB write, no runtime activation, no device control.",
                "validationMarker": "ONE_ASSET_CONTEXT_GA_R1_UNIFIED_LINKAGE_PASS",
                "buildStatus": "PASS with existing frontend warnings",
                "remoteStatus": "local-only",
            },
            {
                "commitHash": CODE_POLICY_COMMIT,
                "shortHash": "d2e1b6b",
                "title": "CODE GA-R1 local freeze",
                "localTag": LOCAL_TAGS[1],
                "changeType": "local-readonly-boundary-preview",
                "modulesTouched": ["CODE Policy Gate", "UHMI", "UMMS", "Asset Context", "UCDE"],
                "customerDemoImpact": "CODE execution boundary and approval preview visible.",
                "riskBoundary": "Local-only, no approval execution, no workflow execution, no EDGE/LINK command.",
                "validationMarker": "ONE_CODE_GA_R1_POLICY_GATE_PREVIEW_PASS",
                "buildStatus": "PASS with existing frontend warnings",
                "remoteStatus": "local-only",
            },
        ],
    }


def modules() -> Dict[str, Any]:
    items = [
        ("reports", "Reports", "Customer demo reports available", "Linked to Asset Context and CODE audit outputs", "Report references visible", "Export guardrails unchanged"),
        ("asset-context", "Asset Context", "Not present in Reports baseline", "Unified linkage visible", "UCDE and Reports references available", "Read-only aggregation only"),
        ("code-policy", "CODE Policy Gate", "Not present in Reports baseline", "Execution boundary visible", "UCDE evidence preview references available", "No approval or command execution"),
        ("umms", "UMMS", "Maintenance workspace available", "Linked into Asset Context and CODE control intent story", "Work order linkage visible", "No work order write"),
        ("uhmi", "UHMI", "Read-only workspace available", "Linked into Asset Context and CODE control path story", "Panel/event/evidence linkage visible", "No direct device path"),
        ("ucde", "UCDE", "Evidence center available", "Linked as audit/evidence target", "Evidence concepts visible", "No evidence write"),
        ("customer-delivery", "Customer Delivery", "Handoff readiness available", "Demo story improved by branch audit narrative", "Handoff references visible", "No deployment/install"),
        ("foundation-diagnostics", "Foundation Diagnostics", "Engineer diagnostics available", "Readiness boundary reflected in risks", "Diagnostics references visible", "No server precheck yet"),
    ]
    return {
        **common(),
        "items": [
            {
                "moduleId": module_id,
                "moduleName": module_name,
                "readinessBefore": before,
                "readinessAfter": after,
                "linkageAdded": linkage,
                "evidenceLinkage": evidence,
                "reportLinkage": "Reports/UCDE linkage available in read-only preview",
                "guardrails": guardrail,
                "productionGaStatus": "NOT_YET",
            }
            for module_id, module_name, before, after, linkage, evidence, guardrail in items
        ],
    }


def risks() -> Dict[str, Any]:
    risk_rows = [
        ("risk-local-only", "local commits not pushed", "medium", ["Asset Context", "CODE Policy Gate"], "Optional push/tag after final review", "Local-only branch freeze", "Remote is not aligned"),
        ("risk-production-ga", "production GA not yet", "high", ["All"], "Run server precheck and UAT before GA", "Read-only preview only", "Production GA remains NOT_YET"),
        ("risk-real-export", "no real export", "medium", ["Reports"], "Keep export execution disabled until governed export path is approved", "Reports export boundary", "No customer artifact generation"),
        ("risk-db-evidence-write", "no DB persistence/evidence write", "medium", ["Asset Context", "UCDE"], "Keep local projections read-only", "No persistence mutation", "No durable runtime evidence"),
        ("risk-runtime", "no runtime activation", "high", ["UHMI", "UMMS", "CODE Policy Gate"], "Activate only after policy/runtime gates", "Runtime disabled", "No real operations execution"),
        ("risk-edge-link", "no EDGE/LINK command", "high", ["CODE Policy Gate", "UHMI"], "Maintain command boundary", "EDGE/LINK command boundary", "No device path execution"),
        ("risk-ai-runtime", "no AI runtime", "medium", ["NexusAI"], "Keep R3 branch audit static", "No model API call", "No automated AI analysis runtime"),
        ("risk-server-precheck", "no server precheck yet", "medium", ["Foundation Diagnostics", "Customer Delivery"], "Run SERVER-PRECHECK-R1 after NexusAI R3", "Server planning only", "Deployment readiness unverified"),
        ("risk-uat", "no UAT yet", "medium", ["All"], "Perform customer/engineer UAT review", "Customer preview not UAT-certified", "Customer acceptance pending"),
    ]
    return {
        **common(),
        "items": [
            {
                "riskId": risk_id,
                "title": title,
                "severity": severity,
                "status": "open-readonly-risk",
                "affectedModules": affected,
                "mitigation": mitigation,
                "boundary": boundary,
                "productionImpact": impact,
            }
            for risk_id, title, severity, affected, mitigation, boundary, impact in risk_rows
        ],
    }


def evidence_linkage() -> Dict[str, Any]:
    return {
        **common(),
        "auditMode": "read-only-branch-diff-preview",
        "ucdeEvidenceReferences": [
            "ONE_ASSET_CONTEXT_GA_R1_UNIFIED_LINKAGE_PASS",
            "ONE_CODE_GA_R1_POLICY_GATE_PREVIEW_PASS",
            "REPORTS_GA_R13_CUSTOMER_DEMO_REPORT_PACK_EXPORT_CENTER_PASS",
        ],
        "reportsReferences": [
            "REPORTS_GA_R13_CUSTOMER_DEMO_REPORT_PACK.md",
            "Reports GA-R13 customer demo report pack",
        ],
        "registryReferences": [
            "AN_VANTARIS_ONE/registries/asset-context-ga-r1/",
            "AN_VANTARIS_ONE/registries/code-ga-r1/",
            "AN_VANTARIS_ONE/registries/nexusai-ga-r2/",
        ],
        "validationMarkers": [
            "ONE_ASSET_CONTEXT_GA_R1_UNIFIED_LINKAGE_PASS",
            "ONE_CODE_GA_R1_POLICY_GATE_PREVIEW_PASS",
            PASS_MARKER,
        ],
        "localFreezeTags": LOCAL_TAGS,
        "evidenceWriteEnabled": False,
    }


def customer_demo_impact() -> Dict[str, Any]:
    return {
        **common(),
        "positiveImpact": [
            "Asset/System/Event/Work Order/Evidence linkage now visible",
            "CODE execution boundary visible",
            "Customer demo story improved",
        ],
        "remainingGaps": [
            "NEXUS AI runtime not active",
            "Server precheck not done",
            "Real DB and deployment not done",
            "Production GA not reached",
        ],
        "recommendation": [
            "SERVER-PRECHECK-R1 after NexusAI R3",
            "optional push/tag after final review",
        ],
    }


def guardrails() -> Dict[str, Any]:
    return {**common(), "guardrails": GUARDRAILS}


def summary() -> Dict[str, Any]:
    refs = source_references()
    commit_items = commits()["items"]
    module_items = modules()["items"]
    risk_items = risks()["items"]
    return {
        **common(),
        "branch": BRANCH,
        "baselineRemoteHead": BASELINE_REMOTE_HEAD,
        "currentLocalHead": CODE_POLICY_COMMIT,
        "localCommitCountSinceRemote": 2,
        "auditedCommits": len(commit_items),
        "auditedModules": len(module_items),
        "riskCount": len(risk_items),
        "customerDemoReadinessImpact": "improved-readonly-preview-story",
        "productionGaStatus": "NOT_YET",
        "remoteAligned": False,
        "pushExecuted": False,
        "deploymentExecuted": False,
        "aiRuntimeEnabled": False,
        "integrationStatus": "available" if not refs["limitations"] else "degraded",
        "limitations": refs["limitations"],
        "sourceReferences": refs["sourceReferences"],
        "providerStatuses": refs["providerStatuses"],
    }


def health() -> Dict[str, Any]:
    data = summary()
    return {
        **common(),
        "status": "ok" if data["integrationStatus"] == "available" else "degraded",
        "sourceReferences": data["sourceReferences"],
        "providerStatuses": data["providerStatuses"],
        "aiRuntimeStatus": "disabled",
        "limitations": data["limitations"],
    }

