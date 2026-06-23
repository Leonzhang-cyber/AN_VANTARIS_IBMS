"""CODE Policy Gate read-only preview provider.

This provider models future execution boundaries without performing approval,
policy mutation, workflow execution, runtime activation, EDGE/LINK commands,
or device control.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[3]
SCOPE = "CODE_GA_R1"
MODULE_ID = "code-policy"
MODULE_NAME = "CODE Policy Gate"
VISUAL_STYLE = "VANTARIS_LIGHT_OPERATIONS_CONSOLE"
PASS_MARKER = "ONE_CODE_GA_R1_POLICY_GATE_PREVIEW_PASS"
GRAPH_MODE = "local-readonly-code-policy-projection"

READ_ONLY_FLAGS: Dict[str, Any] = {
    "scope": SCOPE,
    "moduleId": MODULE_ID,
    "readOnly": True,
    "runtimeEnabled": False,
    "approvalExecutionEnabled": False,
    "policyMutationEnabled": False,
    "workflowExecutionEnabled": False,
    "commandExecutionEnabled": False,
    "dbWriteEnabled": False,
    "edgeCommandExecution": False,
    "linkCommandExecution": False,
    "deviceControlEnabled": False,
    "productionActivation": False,
    "visualStyle": VISUAL_STYLE,
}

SOURCE_REFERENCE_PATHS = [
    "AN_VANTARIS_ONE/operator_review_policy_guard",
    "AN_VANTARIS_ONE/operator_review_decision",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Code/BOUNDARY.md",
    "AN_VANTARIS_ONE/packages/AN_VANTARIS_Code/README.md",
]

DIRECT_PATHS_BLOCKED = [
    "UHMI -> Device",
    "UMMS -> Device",
    "Asset Context -> Device",
    "UHMI -> EDGE",
    "UHMI -> LINK",
    "UMMS -> EDGE",
    "UMMS -> LINK",
    "Asset Context -> DB write",
    "Reports -> Export execution",
]

REQUIRED_PATH = "UHMI / UMMS / Asset Context -> CODE Policy Gate -> Approval Boundary -> Audit / UCDE Evidence -> LINK -> EDGE -> Device"

GUARDRAILS = [
    "No direct device control",
    "No EDGE/LINK command",
    "No DB write",
    "No approval execution",
    "No runtime activation",
    "No production activation",
    "No bypass CODE",
    "No auth/RBAC mutation",
]

POLICY_GATES = [
    {
        "gateId": "code-gate-uhmi-intent",
        "gateName": "UHMI Control Intent Gate",
        "purpose": "Explain how a future UHMI control intent would be blocked or routed to approval.",
        "sourceModule": "UHMI",
        "protectedActionType": "device-control-intent",
    },
    {
        "gateId": "code-gate-umms-work-order-action",
        "gateName": "UMMS Work Order Action Gate",
        "purpose": "Explain future maintenance action boundaries before any workflow or command path.",
        "sourceModule": "UMMS",
        "protectedActionType": "maintenance-action-intent",
    },
    {
        "gateId": "code-gate-asset-context",
        "gateName": "Asset Context Boundary Gate",
        "purpose": "Prevent Asset Context projection from becoming a DB write or direct device path.",
        "sourceModule": "Asset Context",
        "protectedActionType": "asset-context-intent",
    },
    {
        "gateId": "code-gate-report-export",
        "gateName": "Reports Export Boundary Gate",
        "purpose": "Explain future export governance without generating artifacts.",
        "sourceModule": "Reports & Analytics",
        "protectedActionType": "export-intent",
    },
]

APPROVAL_STAGES = [
    ("request-intent", "preview-only"),
    ("policy-check", "preview-only"),
    ("role-review", "preview-only"),
    ("supervisor-approval", "preview-only"),
    ("code-final-gate", "preview-only"),
    ("ucde-audit-evidence", "future-not-enabled"),
    ("link-dispatch", "future-not-enabled"),
    ("edge-execution", "future-not-enabled"),
    ("device-action", "future-not-enabled"),
]


def common() -> Dict[str, Any]:
    return {
        **READ_ONLY_FLAGS,
        "moduleName": MODULE_NAME,
        "provider": "local-readonly-code-policy-provider",
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


def policy_gates() -> Dict[str, Any]:
    return {
        **common(),
        "items": [
            {
                **item,
                "decisionMode": "preview-only",
                "allowedDecisionStates": ["blocked", "requires-approval", "audit-required", "not-executable-in-r1"],
                "readOnly": True,
                "mutationEnabled": False,
                "runtimeLinked": False,
            }
            for item in POLICY_GATES
        ],
    }


def execution_boundary() -> Dict[str, Any]:
    return {
        **common(),
        "directPathsBlocked": DIRECT_PATHS_BLOCKED,
        "requiredPath": REQUIRED_PATH,
        "r1Status": {
            "previewOnly": True,
            "executable": False,
            "approvalExecutable": False,
            "deviceExecutable": False,
        },
        "executionBoundaryStatus": "preview-only-not-executable",
        "guardrails": GUARDRAILS,
    }


def approval_boundary() -> Dict[str, Any]:
    return {
        **common(),
        "approvalStages": [
            {
                "stageId": stage_id,
                "stageName": stage_id.replace("-", " ").title(),
                "stageState": state,
                "approvalExecutionEnabled": False,
                "workflowExecutionEnabled": False,
                "readOnly": True,
            }
            for stage_id, state in APPROVAL_STAGES
        ],
        "approvalExecutionEnabled": False,
    }


def evidence_linkage() -> Dict[str, Any]:
    return {
        **common(),
        "ucdeConceptualLinkage": True,
        "sourceObjectTypes": ["policyGate", "approvalBoundary", "controlIntent", "blockedDirectPath", "executionBoundary"],
        "evidenceMode": "read-only-preview",
        "evidenceWriteEnabled": False,
        "hashOnlyLocalPreview": True,
        "links": [
            {"source": "CODE Policy Gate", "target": "UCDE Evidence", "relationship": "audit-required", "readOnly": True},
            {"source": "Approval Boundary", "target": "UCDE Evidence", "relationship": "approval-record-preview", "readOnly": True},
            {"source": "Blocked Direct Path", "target": "UCDE Evidence", "relationship": "boundary-evidence-preview", "readOnly": True},
        ],
    }


def control_path() -> Dict[str, Any]:
    nodes = [
        "UHMI",
        "UMMS",
        "Asset Context",
        "CODE Policy Gate",
        "Approval Boundary",
        "UCDE Evidence",
        "LINK",
        "EDGE",
        "Device",
    ]
    edges = [
        {"source": "UHMI", "target": "CODE Policy Gate", "relationship": "read-only-preview"},
        {"source": "UMMS", "target": "CODE Policy Gate", "relationship": "read-only-preview"},
        {"source": "Asset Context", "target": "CODE Policy Gate", "relationship": "read-only-preview"},
        {"source": "CODE Policy Gate", "target": "Approval Boundary", "relationship": "gated-by"},
        {"source": "Approval Boundary", "target": "UCDE Evidence", "relationship": "requires-approval"},
        {"source": "UCDE Evidence", "target": "LINK", "relationship": "evidence-required"},
        {"source": "LINK", "target": "EDGE", "relationship": "future-dispatch"},
        {"source": "EDGE", "target": "Device", "relationship": "future-execution"},
    ]
    return {
        **common(),
        "graphMode": GRAPH_MODE,
        "nodes": [{"nodeId": node.lower().replace(" ", "-"), "label": node, "readOnly": True} for node in nodes],
        "edges": [{**edge, "readOnly": True} for edge in edges],
        "directToDeviceEdgesAbsent": True,
    }


def guardrails() -> Dict[str, Any]:
    return {**common(), "guardrails": GUARDRAILS}


def summary() -> Dict[str, Any]:
    refs = source_references()
    return {
        **common(),
        "policyGateCount": len(POLICY_GATES),
        "controlPathStageCount": len(control_path()["nodes"]),
        "blockedDirectPathCount": len(DIRECT_PATHS_BLOCKED),
        "evidenceLinkCount": len(evidence_linkage()["links"]),
        "approvalBoundaryCount": len(APPROVAL_STAGES),
        "executionBoundaryStatus": "preview-only-not-executable",
        "integrationStatus": "available" if not refs["limitations"] else "degraded",
        "limitations": refs["limitations"],
        "providerStatuses": refs["providerStatuses"],
        "sourceReferences": refs["sourceReferences"],
        "guardrails": GUARDRAILS,
    }


def health() -> Dict[str, Any]:
    data = summary()
    return {
        **common(),
        "status": "ok" if data["integrationStatus"] == "available" else "degraded",
        "providerStatuses": data["providerStatuses"],
        "sourceReferences": data["sourceReferences"],
        "limitations": data["limitations"],
    }

